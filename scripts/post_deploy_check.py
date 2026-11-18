#!/usr/bin/env python3
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
"""Post-deploy health check: confirm the new build is live and healthy, and roll back if it is not.

Pre-deploy gates catch most problems. This closes the loop for the ones that only show up in production
(a missing binding or secret, a header rule that replaced another, a route that works locally only).

  python3 scripts/post_deploy_check.py                     check the live site once
  python3 scripts/post_deploy_check.py --wait              first wait until the new build is live, then check
  python3 scripts/post_deploy_check.py --wait --rollback   and roll back automatically if a check fails

Config: the "post_deploy" block in checks.json (see templates/checks.json):
  base_url      the live site, e.g. https://example.com (or set BASE_URL)
  version_url   a path the build writes with the commit it was built from (e.g. /version.txt). --wait polls it
                until it shows the commit being deployed, so you never check the old build by mistake
  wait_seconds  how long --wait keeps polling (default 600)
  max_ms        slowest acceptable response per page (default 3000)
  headers       response headers every page must carry, e.g. Content-Security-Policy
  pages         [{"path": "/", "status": 200, "contains": "<h1"}, {"path": "/api/health", "contains": "ok"}]
                add "headers": false to a page (an API route, a redirect) to skip the header check
  retries       extra tries for a failing page before it counts as failed (default 2, 10 seconds apart)

Rollback runs `bash scripts/deploy_batch.sh rollback` (see that script for Cloudflare and other hosts).
Exit code 0 when every check passes. Results are added to the cost and catch log (scripts/telemetry.py)."""
import argparse, json, os, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
try:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(HERE)); import telemetry
except Exception:
    telemetry = None


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "zero-to-live-post-deploy-check", "Cache-Control": "no-cache"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(400_000).decode("utf-8", "replace")
            return r.status, dict(r.headers), body, (time.time() - t) * 1000
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read(50_000).decode("utf-8", "replace"), (time.time() - t) * 1000
    except Exception as e:
        return 0, {}, str(e), (time.time() - t) * 1000


def head_commit():
    sha = os.environ.get("EXPECT_COMMIT") or subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return sha


def wait_for_build(base, cfg):
    limit = int(cfg.get("wait_seconds", 600))
    vurl = cfg.get("version_url")
    want = head_commit()
    if not vurl:
        print("WARN  no version_url set, so the check cannot tell the new build from the old one. Waiting 60 s instead.")
        time.sleep(min(60, limit))
        return True
    print(f"Waiting up to {limit} s for {base}{vurl} to show {want[:10]}")
    end = time.time() + limit
    while time.time() < end:
        status, _, body, _ = fetch(base + vurl)
        if status == 200 and want[:7] in body:
            print(f"New build is live ({want[:10]}).")
            return True
        time.sleep(15)
    print(f"FAIL  the new build did not go live within {limit} s (still not showing {want[:10]})")
    return False


def check_page(base, page, cfg):
    path = page.get("path", "/")
    want_status = int(page.get("status", 200))
    max_ms = int(page.get("max_ms", cfg.get("max_ms", 3000)))
    need_headers = cfg.get("headers", []) if page.get("headers", True) else []
    problems = []
    status, headers, body, ms = fetch(base + path)
    lower = {k.lower(): v for k, v in headers.items()}
    if status != want_status:
        problems.append(f"status {status or 'no response'} (expected {want_status})" + ("" if status else f": {body[:120]}"))
    if page.get("contains") and page["contains"] not in body:
        problems.append(f"page does not contain {page['contains']!r}")
    for h in need_headers:
        if h.lower() not in lower:
            problems.append(f"missing header {h}")
    if ms > max_ms:
        problems.append(f"slow: {ms:.0f} ms (limit {max_ms})")
    return problems, ms


def main():
    ap = argparse.ArgumentParser(description="Check the live site after a deploy")
    ap.add_argument("--wait", action="store_true", help="wait for the new build before checking")
    ap.add_argument("--rollback", action="store_true", help="roll back automatically if a check fails")
    ap.add_argument("--config", default="checks.json")
    a = ap.parse_args()

    cfgp = Path(a.config)
    cfg = json.loads(cfgp.read_text()).get("post_deploy", {}) if cfgp.exists() else {}
    base = (os.environ.get("BASE_URL") or cfg.get("base_url") or "").rstrip("/")
    if not base:
        print("No base_url. Add a post_deploy block to checks.json (see templates/checks.json) or set BASE_URL.")
        return 2
    pages = cfg.get("pages") or [{"path": "/"}]
    retries = int(cfg.get("retries", 2))
    started = time.time()

    live = wait_for_build(base, cfg) if a.wait else True
    failed, passed = [], 0
    if live:
        print(f"POST-DEPLOY CHECK  {base}")
        for page in pages:
            for attempt in range(retries + 1):
                problems, ms = check_page(base, page, cfg)
                if not problems or attempt == retries:
                    break
                time.sleep(10)
            if problems:
                failed.append(page.get("path", "/"))
                print(f"  FAIL  {page.get('path', '/')}: " + "; ".join(problems))
            else:
                passed += 1
                print(f"  PASS  {page.get('path', '/')} ({ms:.0f} ms)")
    else:
        failed.append("new build not live")

    ok = not failed
    if telemetry:
        telemetry.log("post_deploy", ok=ok, passed=passed, failed=len(failed), seconds=round(time.time() - started, 1))
    print(f"\n{passed} passed, {len(failed)} failed. " + ("LIVE SITE HEALTHY" if ok else "LIVE SITE UNHEALTHY"))
    if not ok and a.rollback:
        print("\nRolling back.")
        rc = subprocess.run(["bash", str(HERE / "deploy_batch.sh"), "rollback"]).returncode
        print("Rollback " + ("done. Run this check again to confirm the old build is healthy." if rc == 0 else "FAILED: roll back from the host dashboard now."))
    elif not ok:
        print("Roll back with: bash scripts/deploy_batch.sh rollback")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
