#!/usr/bin/env python3
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
"""Quick tier: run only the checks the current change can affect.

Reads checks.json in the project root (see templates/checks.json):
  "always": commands that run on every change (keep these fast)
  "map":    [{ "paths": [glob, ...], "run": [command, ...], "server": true|false }]
  "server_cmd": command that starts the local server with a fresh database (used when "server" is true)

Changed files = commits since the last deploy (from .deploy/state.json, written by deploy_batch.sh) plus
uncommitted and untracked files. Override the base with --base REF.

  python3 scripts/quick_check.py              run affected checks
  python3 scripts/quick_check.py --dry-run    show what would run
  python3 scripts/quick_check.py --base main  compare against a branch or commit
Exit code is non-zero if any command fails."""
import fnmatch, json, subprocess, sys
from pathlib import Path


def git(*args):
    p = subprocess.run(["git", *args], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def changed_files(base):
    files = set()
    if base:
        files |= set(git("diff", "--name-only", f"{base}...HEAD").splitlines())
    files |= set(git("diff", "--name-only", "HEAD").splitlines())          # staged and unstaged
    files |= set(git("ls-files", "--others", "--exclude-standard").splitlines())  # untracked
    return sorted(f for f in files if f)


def matches(path, patterns):
    return any(fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p.replace("/**", "")) for p in patterns)


def main():
    root = Path(git("rev-parse", "--show-toplevel") or ".")
    cfg_path = root / "checks.json"
    if not cfg_path.exists():
        print("No checks.json in the project root. Copy templates/checks.json and edit it."); return 2
    cfg = json.loads(cfg_path.read_text())
    dry = "--dry-run" in sys.argv
    base = None
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]
    else:
        state = root / ".deploy" / "state.json"
        if state.exists():
            base = json.loads(state.read_text()).get("last_deployed")

    files = changed_files(base)
    if not files:
        print("No changes found. Nothing to check."); return 0

    plan, need_server, unmapped = list(cfg.get("always", [])), False, []
    for f in files:
        hit = False
        for rule in cfg.get("map", []):
            if matches(f, rule["paths"]):
                hit = True
                need_server |= bool(rule.get("server"))
                plan += [c for c in rule["run"] if c not in plan]
        if not hit:
            unmapped.append(f)

    print(f"{len(files)} changed file(s) since {base or 'HEAD'}:")
    for f in files: print(f"  {f}")
    if unmapped:
        print("Not covered by any mapping (only the 'always' checks apply):")
        for f in unmapped: print(f"  {f}")
    print("\nPlan:")
    if need_server: print(f"  [server] {cfg.get('server_cmd', '(no server_cmd set)')}")
    for c in plan: print(f"  {c}")
    if dry: return 0

    if need_server:
        if not cfg.get("server_cmd") or subprocess.run(cfg["server_cmd"], shell=True, cwd=root).returncode:
            print("FAIL  local server did not start"); return 1
    failed = []
    for c in plan:
        print(f"\n$ {c}")
        if subprocess.run(c, shell=True, cwd=root).returncode:
            failed.append(c)
    print("\nQUICK CHECK: " + ("all passed" if not failed else f"{len(failed)} failed"))
    for c in failed: print(f"  FAIL  {c}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
