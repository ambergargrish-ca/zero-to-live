#!/usr/bin/env python3
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
"""Full tier: run every suite once, each against a fresh local server and database, and write one report.

Suites come from checks.json under "full":
  "full": [
    { "name": "Build", "run": "bash scripts/build.sh" },
    { "name": "Compliance", "run": "python3 scripts/compliance_check.py" },
    { "name": "Accounts", "run": "python3 tests/auth_e2e.py", "server": true, "timeout": 900 }
  ]
A suite with "server": true gets a fresh server from "server_cmd" first. If a suite named "Build" fails, the run stops.

Counting: a suite's output lines that start with PASS or FAIL are counted (also "N of M passed" or "N/M passed").
Exit code 0 only when every suite exits 0.

Writes tests/eval/report.md (for people) and tests/eval/report.json (commit, time, result; read by deploy_batch.sh).

  python3 scripts/run_suite.py             every suite
  python3 scripts/run_suite.py --only Accounts,Compliance"""
import datetime, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "tests" / "eval"


def sh(cmd, timeout):
    t = time.time()
    try:
        p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr, time.time() - t
    except subprocess.TimeoutExpired as e:
        part = lambda b: (b.decode(errors="replace") if isinstance(b, bytes) else b) or ""
        return 124, part(e.stdout) + part(e.stderr) + f"\nStopped after {timeout}s.", time.time() - t


def score(out):
    passed = len(re.findall(r"^\s*PASS\b", out, re.M))
    failed = len(re.findall(r"^\s*FAIL\b", out, re.M))
    if passed or failed:
        return passed, passed + failed
    m = re.findall(r"(\d+)\s*(?:of|/)\s*(\d+) passed", out)
    if m:
        return int(m[-1][0]), int(m[-1][1])
    m = re.findall(r"(\d+) ok, \d+ warnings, (\d+) failures", out)
    if m:
        return int(m[-1][0]), int(m[-1][0]) + int(m[-1][1])
    return 0, 0


def details(out, code):
    lines = out.rstrip().splitlines()
    tb = [i for i, l in enumerate(lines) if l.startswith("Traceback (most recent call last)")]
    if tb:
        return ["The suite crashed:"] + lines[tb[-1]:][-30:]
    bad = [l.strip() for l in lines if re.match(r"\s*(FAIL|WARN)\b", l)][:40]
    if code and not any(l.startswith("FAIL") for l in bad):
        bad += [f"Exited with code {code}. Last lines:"] + lines[-20:]
    return bad


def main():
    cfgp = ROOT / "checks.json"
    if not cfgp.exists():
        print("No checks.json in the project root. Copy templates/checks.json and edit it."); return 2
    cfg = json.loads(cfgp.read_text())
    suites = cfg.get("full", [])
    if "--only" in sys.argv:
        keep = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        suites = [s for s in suites if s["name"] in keep]
    OUT.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", ".", ":!tests/eval", ":!.deploy"], capture_output=True, text=True, cwd=ROOT).stdout.strip())
    started = datetime.datetime.now()
    rows = []
    for s in suites:
        if s.get("server"):
            code, out, _ = sh(cfg.get("server_cmd", "false"), 300)
            if code:
                rows.append({"name": s["name"], "ok": False, "passed": 0, "total": 0, "secs": 0, "details": ["The local server did not start"] + out.splitlines()[-10:]})
                print(f"FAIL  {s['name']}: server did not start"); continue
        code, out, secs = sh(s["run"], s.get("timeout", 1800))
        p, t = score(out)
        row = {"name": s["name"], "ok": code == 0, "passed": p, "total": t, "secs": round(secs), "details": details(out, code)}
        rows.append(row)
        print(f"{'PASS' if code == 0 else 'FAIL'}  {s['name']}: {p}/{t} in {secs:.0f}s")
        if code:
            for l in row["details"][-6:]: print("      " + l)
            if s["name"].lower() == "build":
                break
    if cfg.get("server_stop_cmd"):
        sh(cfg["server_stop_cmd"], 60)

    ok = bool(rows) and all(r["ok"] for r in rows) and len(rows) == len(suites)
    passed, total = sum(r["passed"] for r in rows), sum(r["total"] for r in rows)
    md = ["# Evaluation report", "",
          f"{started:%Y-%m-%d %H:%M}, commit `{commit[:10] or 'none'}`{' (uncommitted changes)' if dirty else ''}. "
          f"**{'All suites passed' if ok else 'Some suites failed'}**: {passed} of {total} checks passed.", "",
          "| Suite | Result | Checks | Time |", "|---|---|---|---|"]
    md += [f"| {r['name']} | {'Pass' if r['ok'] else 'Fail'} | {r['passed']}/{r['total']} | {r['secs']}s |" for r in rows]
    for r in rows:
        if r["details"]:
            md += ["", f"## {r['name']}", "", "```", *r["details"], "```"]
    (OUT / "report.md").write_text("\n".join(md) + "\n")
    (OUT / "report.json").write_text(json.dumps({"commit": commit, "dirty": dirty, "time": started.isoformat(timespec="seconds"),
                                                 "all_ok": ok, "passed": passed, "total": total, "suites": rows}, indent=1) + "\n")
    print(f"\nReport: tests/eval/report.md. {passed} of {total} checks passed. {'ALL PASSED' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
