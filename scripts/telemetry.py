#!/usr/bin/env python3
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
"""Cost and catch log: what each check run, deploy and rollback cost, and what it caught.

Every run of quick_check.py, run_suite.py and post_deploy_check.py, and every deploy and rollback made with
deploy_batch.sh, appends one line to .deploy/telemetry.jsonl. The file stays on your machine (.deploy/ is in
.gitignore) and nothing is sent anywhere.

Each line records: time, event (quick, full, post_deploy, deploy, rollback, agent), commit, whether it passed,
checks passed and failed, files changed, seconds, and optionally AI tokens and cost.

  python3 scripts/telemetry.py report               summary of the last 30 days
  python3 scripts/telemetry.py report --days 7
  python3 scripts/telemetry.py log --event agent --tokens 180000 --cost 1.25 --note "batch 12 session"

AI tokens and cost (optional). Scripts cannot see what an AI agent spent, so add it one of two ways:
  - set ZTL_TOKENS and ZTL_COST_USD in the environment before a run, and that run records them, or
  - log an "agent" event after a working session, with the totals from your tool (Claude Code shows a
    session's cost with /cost, and exports claude_code.token.usage and claude_code.cost.usage when its
    OpenTelemetry telemetry is turned on).

Turn logging off with ZTL_TELEMETRY=0."""
import argparse, datetime, json, os, subprocess, sys
from pathlib import Path

EVENTS = ["quick", "full", "post_deploy", "deploy", "rollback", "agent"]


def _root():
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
        return Path(out) if out else Path.cwd()
    except Exception:
        return Path.cwd()


def _path():
    return _root() / ".deploy" / "telemetry.jsonl"


def _num(v, cast):
    try:
        return cast(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def log(event, **fields):
    """Append one record. Never raises: logging must not break the check that called it."""
    if os.environ.get("ZTL_TELEMETRY", "1") == "0":
        return
    try:
        commit = subprocess.run(["git", "rev-parse", "--short=10", "HEAD"], capture_output=True, text=True).stdout.strip()
        rec = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "event": event, "commit": commit or None}
        rec.update({k: v for k, v in fields.items() if v is not None})
        rec.setdefault("tokens", _num(os.environ.get("ZTL_TOKENS"), int))
        rec.setdefault("cost_usd", _num(os.environ.get("ZTL_COST_USD"), float))
        rec = {k: v for k, v in rec.items() if v is not None}
        p = _path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def _load(days):
    p = _path()
    if not p.exists():
        return []
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    out = []
    for line in p.read_text().splitlines():
        try:
            r = json.loads(line)
            if datetime.datetime.fromisoformat(r["time"]) >= since:
                out.append(r)
        except Exception:
            continue
    return out


def _fmt_money(v):
    return f"${v:,.2f}" if v else "-"


def report(days):
    recs = _load(days)
    if not recs:
        print(f"No records in the last {days} days ({_path()}). Run a check first.")
        return 0
    by = {e: [r for r in recs if r["event"] == e] for e in EVENTS}
    print(f"COST AND CATCH LOG, last {days} days ({len(recs)} records)\n")
    print(f"{'Tier':<13}{'Runs':>6}{'Minutes':>10}{'Caught':>8}{'Min per catch':>15}{'Tokens':>12}{'Cost':>10}")
    for e, label in [("quick", "Quick tier"), ("full", "Full tier"), ("post_deploy", "Post-deploy")]:
        rs = by[e]
        if not rs:
            continue
        mins = sum(r.get("seconds", 0) for r in rs) / 60
        caught = sum(1 for r in rs if r.get("ok") is False)
        toks = sum(r.get("tokens", 0) for r in rs)
        cost = sum(r.get("cost_usd", 0) for r in rs)
        per = f"{mins / caught:.1f}" if caught else "-"
        print(f"{label:<13}{len(rs):>6}{mins:>10.1f}{caught:>8}{per:>15}{(f'{toks:,}' if toks else '-'):>12}{_fmt_money(cost):>10}")

    deploys = len(by["deploy"])
    rollbacks = sum(1 for r in by["rollback"] if r.get("ok") is not False)
    escapes = sum(1 for r in by["post_deploy"] if r.get("ok") is False)
    print(f"\nDeploys {deploys}, rollbacks {rollbacks}, post-deploy failures {escapes}")
    if deploys:
        print(f"Change failure rate: {escapes / deploys:.0%} of deploys failed the post-deploy check")

    q, f = by["quick"], by["full"]
    if q and f:
        avg_full = sum(r.get("seconds", 0) for r in f) / len(f) / 60
        q_min = sum(r.get("seconds", 0) for r in q) / 60
        avoided = len(q) * avg_full - q_min
        if avoided >= 1:
            print(f"Quick tier saved about {avoided:.0f} minutes versus running the full tier on all {len(q)} changes "
                  f"(full tier averages {avg_full:.1f} min)")

    total_cost = sum(r.get("cost_usd", 0) for r in recs)
    total_caught = sum(1 for r in recs if r["event"] in ("quick", "full") and r.get("ok") is False)
    if total_cost:
        print(f"\nAI cost recorded: {_fmt_money(total_cost)}")
        if deploys:
            print(f"  per deploy: {_fmt_money(total_cost / deploys)}")
        if total_caught:
            print(f"  per problem caught before deploy: {_fmt_money(total_cost / total_caught)}")
    else:
        print("\nNo AI cost recorded yet. See the top of this script for how to add tokens and cost.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Cost and catch log for checks, deploys and rollbacks")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("report"); r.add_argument("--days", type=int, default=30)
    l = sub.add_parser("log")
    l.add_argument("--event", required=True, choices=EVENTS)
    l.add_argument("--ok", choices=["0", "1"])
    l.add_argument("--seconds", type=float)
    l.add_argument("--tokens", type=int)
    l.add_argument("--cost", type=float)
    l.add_argument("--note")
    a = ap.parse_args()
    if a.cmd == "log":
        log(a.event, ok=None if a.ok is None else a.ok == "1", seconds=a.seconds, tokens=a.tokens, cost_usd=a.cost, note=a.note)
        return 0
    return report(a.days if a.cmd == "report" else 30)


if __name__ == "__main__":
    sys.exit(main())
