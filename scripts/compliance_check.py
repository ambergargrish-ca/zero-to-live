#!/usr/bin/env python3
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
"""Compliance and security check. Run on every change (quick tier) and before every deploy (full tier).

FAILS on things that must never ship:
  - secret keys in the repository (common key formats and private key blocks)
  - inline scripts or inline event handlers in public HTML (they break a strict Content Security Policy)
  - JSON-LD blocks that contain a raw "</" (unescaped data can close the script tag)
  - SQL built by interpolating request data into a query string
  - missing security headers, or a CSP that allows unsafe-eval
  - a public page without a link to the privacy policy

WARNS when a change affects privacy, so a person reviews the privacy policy before deploying:
  - new database tables or columns
  - new outside hosts the code talks to
  - new cookies or browser storage keys
  - forms that collect contact details without a privacy notice nearby

Configure in checks.json under "compliance" (all keys optional; see templates/checks.json).

  python3 scripts/compliance_check.py            check and report (exit 1 on failures)
  python3 scripts/compliance_check.py --accept   record the current state as reviewed"""
import json, re, sys
from pathlib import Path

ROOT = Path.cwd()
DEFAULTS = {
    "public_html": ["*.html", "**/*.html"],
    "skip_dirs": ["node_modules", ".git", ".wrangler", "dist", "tests", ".deploy"],
    "headers_files": ["_headers", "dist/_headers"],
    "required_headers": ["Content-Security-Policy", "Strict-Transport-Security", "X-Content-Type-Options",
                         "Referrer-Policy", "Permissions-Policy", "frame-ancestors"],
    "code_dirs": ["server", "functions", "assets", "src", "app"],
    "schema_files": [],
    "host_allowlist": ["schema.org", "w3.org", "example.com", "example.org"],
    "privacy_marker": "privacy",
    "pages_without_privacy_link": ["404.html"],
    "baseline": "tests/eval/compliance_baseline.json",
}
SECRET = re.compile(r"(sk_live_[0-9a-zA-Z]{10,}|rk_live_[0-9a-zA-Z]{10,}|sk-ant-[0-9a-zA-Z_-]{20,}|sk-[A-Za-z0-9]{40,}"
                    r"|whsec_[0-9a-zA-Z]{20,}|AKIA[0-9A-Z]{16}|ghp_[0-9A-Za-z]{30,}|xox[baprs]-[0-9A-Za-z-]{10,}"
                    r"|AIza[0-9A-Za-z_-]{35}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
TEXT = {".js", ".mjs", ".ts", ".py", ".json", ".html", ".toml", ".md", ".txt", ".sh", ".yml", ".yaml", ".env", ".vars"}
# Query text built from request data: JS template literals and Python f-strings passed to a query function
SQL_JS = re.compile(r"\b(prepare|query|exec|execute|raw)\(\s*`[^`]*\$\{\s*(req|request|body|params|query|q|url|input|data|ctx)\b")
SQL_PY = re.compile(r"\b(execute|executemany|query|raw)\(\s*f[\"'][^\"']*\{\s*(request|req|body|params|form|args|data)\b")

fails, warns, oks = [], [], []


def load_cfg():
    cfg = dict(DEFAULTS)
    p = ROOT / "checks.json"
    if p.exists():
        cfg.update(json.loads(p.read_text()).get("compliance", {}))
    return cfg


def files(cfg, exts=None):
    for p in ROOT.rglob("*"):
        if not p.is_file() or any(d in p.relative_to(ROOT).parts for d in cfg["skip_dirs"]):
            continue
        if exts is None or p.suffix in exts or p.name.startswith(".env"):
            yield p


def read(p):
    return p.read_text(encoding="utf-8", errors="ignore")


def public_pages(cfg):
    seen = set()
    for pat in cfg["public_html"]:
        for p in ROOT.glob(pat):
            if p.is_file() and not any(d in p.relative_to(ROOT).parts for d in cfg["skip_dirs"]) and p not in seen:
                seen.add(p); yield p


def code_text(cfg):
    out = []
    for d in cfg["code_dirs"]:
        base = ROOT / d
        if base.is_dir():
            out += [read(p) for p in base.rglob("*") if p.is_file() and p.suffix in {".js", ".mjs", ".ts", ".py"} and "node_modules" not in p.parts]
    return "\n".join(out)


def hard_checks(cfg):
    n = 0
    for p in files(cfg, TEXT):
        n += 1
        if SECRET.search(read(p)):
            fails.append(f"Possible secret key in {p.relative_to(ROOT)}. Keys belong in the platform secret store only.")
    oks.append(f"Scanned {n} text files for secret keys")

    pages = list(public_pages(cfg))
    for p in pages:
        h, rel = read(p), p.relative_to(ROOT)
        if re.search(r"<script(?![^>]*\bsrc=)(?![^>]*application/ld\+json)[^>]*>", h, re.I):
            fails.append(f"Inline script in {rel} breaks the content security policy")
        if re.search(r"\son(click|load|error|submit|change|input|mouseover|focus|blur)\s*=", h, re.I):
            fails.append(f"Inline event handler in {rel} breaks the content security policy")
        for block in re.findall(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", h, re.S | re.I):
            if "</" in block or "<!--" in block:
                fails.append(f"JSON-LD in {rel} contains '</' or '<!--'. Escape '<' as \\u003c.")
        if p.name not in cfg["pages_without_privacy_link"] and cfg["privacy_marker"] not in h.lower():
            fails.append(f"{rel} has no link to the privacy policy. Use the shared layout.")
        for m in re.finditer(r"<form\b.*?</form>", h, re.S | re.I):
            form, before = m.group(0), h[max(0, m.start() - 600):m.start()]
            if re.search(r'type="email"|name="email"|name="phone"|type="tel"', form) and cfg["privacy_marker"] not in (form + before).lower():
                warns.append(f"A form in {rel} collects contact details without a privacy notice next to it")
    oks.append(f"Checked {len(pages)} public pages for inline scripts, JSON-LD escaping and privacy links")

    sql_hits = 0
    for d in cfg["code_dirs"]:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.suffix not in {".js", ".mjs", ".ts", ".py"} or "node_modules" in p.parts:
                continue
            for i, line in enumerate(read(p).split("\n"), 1):
                if SQL_JS.search(line) or SQL_PY.search(line):
                    sql_hits += 1
                    fails.append(f"{p.relative_to(ROOT)}:{i} builds SQL from request data. Use bound parameters.")
    if not sql_hits:
        oks.append("No SQL built from request data")

    hdr = "\n".join(l for f in cfg["headers_files"] if (ROOT / f).exists()
                    for l in read(ROOT / f).split("\n") if not l.lstrip().startswith("#"))
    if not hdr:
        warns.append(f"No headers file found ({', '.join(cfg['headers_files'])}). Set headers_files in checks.json.")
    else:
        for h in cfg["required_headers"]:
            (oks if h in hdr else fails).append(f"Security header {h} {'is set' if h in hdr else 'is missing'}")
        if "'unsafe-eval'" in hdr:
            fails.append("The content security policy allows 'unsafe-eval'")

    gi = ROOT / ".gitignore"
    needed = [".env", ".dev.vars", "*.pem", "*.key"]
    missing = [x for x in needed if not gi.exists() or x not in read(gi)]
    (warns if missing else oks).append(".gitignore " + (f"is missing {', '.join(missing)}" if missing else "keeps local secrets out of Git"))


def snapshot(cfg):
    schema = "\n".join(read(ROOT / f) for f in cfg["schema_files"] if (ROOT / f).exists())
    tables = sorted(set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?[`\"]?(\w+)", schema, re.I)))
    columns = set(f"{t}.{c}" for t, c in re.findall(r"ALTER TABLE [`\"]?(\w+)[`\"]? ADD COLUMN [`\"]?(\w+)", schema, re.I))
    for t, body in re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?[`\"]?(\w+)[`\"]?\s*\((.*?)\)\s*(?:;|`|$)", schema, re.S | re.I):
        for line in body.split("\n"):
            m = re.match(r"\s*[`\"]?([a-z_][a-z0-9_]*)[`\"]?\s+(INTEGER|TEXT|REAL|BLOB|NUMERIC|VARCHAR|BOOLEAN|TIMESTAMP)", line, re.I)
            if m:
                columns.add(f"{t}.{m.group(1)}")
    code = code_text(cfg) + "\n".join(read(p) for p in public_pages(cfg))
    allow = tuple(cfg["host_allowlist"])
    hosts = sorted(set(h.lower() for h in re.findall(r"https://([a-z0-9.-]+\.[a-z]{2,})", code, re.I)
                       if not h.lower().endswith(allow)))
    cookies = sorted(set(re.findall(r"(?:document\.cookie\s*=\s*[`\"']?|Set-Cookie[\"']?\s*[:,]\s*[`\"']?)([A-Za-z_][\w-]*)=", code)))
    storage = sorted(set(re.findall(r"(?:localStorage|sessionStorage)\.(?:getItem|setItem)\(\s*[\"'`]([\w.:-]+)", code)))
    return {"tables": tables, "columns": sorted(columns), "hosts": hosts, "cookies": cookies, "storage": storage}


def main():
    cfg = load_cfg()
    hard_checks(cfg)
    now = snapshot(cfg)
    base_path = ROOT / cfg["baseline"]
    if "--accept" in sys.argv:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        base_path.write_text(json.dumps(now, indent=1) + "\n")
        print(f"Accepted the current state as reviewed ({base_path.relative_to(ROOT)}).")
        return 0
    if not base_path.exists():
        warns.append("No reviewed privacy baseline yet. Review the privacy policy, then run with --accept.")
    else:
        base = json.loads(base_path.read_text())
        labels = [("tables", "New database table"), ("columns", "New database column"), ("hosts", "New outside service"),
                  ("cookies", "New cookie"), ("storage", "New browser storage key")]
        for key, label in labels:
            for item in sorted(set(now[key]) - set(base.get(key, []))):
                warns.append(f"{label}: {item}. Check the privacy policy covers it, then run --accept.")

    print("COMPLIANCE AND SECURITY CHECK")
    for o in oks: print("  OK    " + o)
    for w in warns: print("  WARN  " + w)
    for f in fails: print("  FAIL  " + f)
    print(f"\n{len(oks)} ok, {len(warns)} warnings, {len(fails)} failures")
    if warns:
        print("Warnings need a person to review privacy compliance before deploying.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
