#!/usr/bin/env bash
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
# Batched deploys: count changes since the last production deploy, track builds used this month, and deploy only
# when the full tier has passed on the exact commit being shipped.
#
#   bash scripts/deploy_batch.sh status            changes pending, batch threshold, builds used and left
#   bash scripts/deploy_batch.sh deploy            deploy if the batch is full and tests passed on HEAD
#   bash scripts/deploy_batch.sh deploy --force    deploy before the batch is full (the test gate still applies)
#   bash scripts/deploy_batch.sh mark              record HEAD as deployed without deploying (first setup)
#   bash scripts/deploy_batch.sh rollback          put the previous production deployment back (one command)
#
# Settings (environment variables):
#   BATCH_SIZE=10        commits per batch
#   BUILD_LIMIT=500      builds per month on your plan (Cloudflare Pages free: 500)
#   RESERVE=20           builds kept back for hotfixes; normal deploys stop at BUILD_LIMIT - RESERVE
#   DEPLOY_BRANCH=main
#   DEPLOY_CMD="git push origin main"   e.g. "npx wrangler pages deploy dist" or "netlify deploy --prod --dir dist"
#   REPORT=tests/eval/report.json       written by scripts/run_suite.py
#   POST_DEPLOY=1        after deploying, run scripts/post_deploy_check.py --wait --rollback
#
# Rollback, in order of preference:
#   ROLLBACK_CMD="..."   your host's own rollback command, e.g. "vercel rollback --yes"
#   Cloudflare Pages:    set CF_API_TOKEN (a token with Cloudflare Pages: Edit), CF_ACCOUNT_ID and CF_PAGES_PROJECT.
#                        The script finds the production deployment before the one now live and rolls back to it
#                        through the Cloudflare API. No build is used and it takes seconds. ROLLBACK_TO=<deployment id>
#                        picks a specific deployment instead.
#   Otherwise it prints the manual steps.
#
# State is kept in .deploy/state.json (add .deploy/ to .gitignore). Builds you trigger outside this script are not
# counted; check the host dashboard and correct with: BUILDS_USED=<n> bash scripts/deploy_batch.sh status
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
BATCH_SIZE="${BATCH_SIZE:-10}"; BUILD_LIMIT="${BUILD_LIMIT:-500}"; RESERVE="${RESERVE:-20}"
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"; DEPLOY_CMD="${DEPLOY_CMD:-git push origin $DEPLOY_BRANCH}"
REPORT="${REPORT:-tests/eval/report.json}"; STATE=.deploy/state.json
MONTH=$(date +%Y-%m)
mkdir -p .deploy
[ -f "$STATE" ] || echo '{}' > "$STATE"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tlog() { python3 "$HERE/telemetry.py" log "$@" >/dev/null 2>&1 || true; }

rollback() {
  if [ -n "${ROLLBACK_CMD:-}" ]; then
    echo "Running ROLLBACK_CMD"; eval "$ROLLBACK_CMD"
  elif [ -n "${CF_API_TOKEN:-}" ] && [ -n "${CF_ACCOUNT_ID:-}" ] && [ -n "${CF_PAGES_PROJECT:-}" ]; then
    python3 - <<'PY'
import json, os, sys, urllib.request
base = os.environ.get("CF_API_BASE", "https://api.cloudflare.com/client/v4").rstrip("/")
proj = f"{base}/accounts/{os.environ['CF_ACCOUNT_ID']}/pages/projects/{os.environ['CF_PAGES_PROJECT']}"
def call(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if not data.get("success"):
        sys.exit(f"Cloudflare API error: {data.get('errors')}")
    return data["result"]
target = os.environ.get("ROLLBACK_TO")
if not target:
    live = (call(proj).get("canonical_deployment") or {})
    deps = call(f"{proj}/deployments?env=production&per_page=25")
    ok = [d for d in deps if (d.get("latest_stage") or {}).get("status") == "success" and d["id"] != live.get("id")
          and d.get("created_on", "") < live.get("created_on", "9999")]
    ok.sort(key=lambda d: d.get("created_on", ""), reverse=True)
    if not ok:
        sys.exit("No earlier successful production deployment to roll back to.")
    target = ok[0]["id"]
    commit = ((ok[0].get("deployment_trigger") or {}).get("metadata") or {}).get("commit_hash", "")[:10]
    print(f"Live now: {live.get('id', '?')}. Rolling back to {target} (commit {commit or 'unknown'}, built {ok[0].get('created_on', '?')}).")
res = call(f"{proj}/deployments/{target}/rollback", "POST")
print(f"Rolled back. Production now serves deployment {res.get('id', target)}.")
PY
  else
    cat <<'TXT'
No automatic rollback configured. Do one of these now:
  - Host dashboard: open the deployments list, pick the last good production deployment, choose "Rollback"
    (Cloudflare Pages: Workers & Pages > project > Deployments > ... > Rollback to this deployment). No build used.
  - Or revert the bad commits on the production branch and push (uses one build, and goes through any release gate).
To make this one command next time, set ROLLBACK_CMD, or CF_API_TOKEN, CF_ACCOUNT_ID and CF_PAGES_PROJECT.
TXT
    return 1
  fi
}

get() { python3 -c "import json,sys; print(json.load(open('$STATE')).get('$1', '$2'))"; }
put() { python3 - "$STATE" "$@" <<'PY'
import json, sys
p = sys.argv[1]; s = json.load(open(p))
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1); s[k] = int(v) if v.isdigit() else v
json.dump(s, open(p, "w"), indent=1)
PY
}

[ "$(get month '')" = "$MONTH" ] || put "month=$MONTH" "builds_used=0"
[ -n "${BUILDS_USED:-}" ] && put "builds_used=$BUILDS_USED"
LAST=$(get last_deployed '')
USED=$(get builds_used 0)
LEFT=$((BUILD_LIMIT - USED))
HEAD=$(git rev-parse HEAD)
if [ -n "$LAST" ] && git cat-file -e "$LAST" 2>/dev/null; then PENDING=$(git rev-list --count "$LAST..HEAD"); else PENDING=$(git rev-list --count HEAD); fi

status() {
  echo "Last deployed:   ${LAST:-(never)}"
  echo "Pending commits: $PENDING of $BATCH_SIZE per batch"
  echo "Builds in $MONTH: $USED used, $LEFT left of $BUILD_LIMIT (reserve $RESERVE for hotfixes)"
  if [ -f "$REPORT" ]; then
    python3 - "$REPORT" "$HEAD" <<'PY'
import json, sys
r = json.load(open(sys.argv[1])); same = r["commit"] == sys.argv[2] and not r.get("dirty")
print(f"Full tier:       {'passed' if r['all_ok'] else 'FAILED'} on {r['commit'][:10]} at {r['time']}" + ("" if same else "  (not the current commit: run it again)"))
PY
  else
    echo "Full tier:       not run yet (python3 scripts/run_suite.py)"
  fi
}

gate() {
  [ -z "$(git status --porcelain -- . ':!tests/eval' ':!.deploy')" ] || { echo "Refusing: uncommitted changes. Commit them into the batch first."; exit 1; }
  [ -f "$REPORT" ] || { echo "Refusing: no full-tier report. Run: python3 scripts/run_suite.py"; exit 1; }
  python3 - "$REPORT" "$HEAD" <<'PY' || { echo "Refusing: the full tier has not passed on this commit. Run: python3 scripts/run_suite.py"; exit 1; }
import json, sys
r = json.load(open(sys.argv[1]))
sys.exit(0 if r["all_ok"] and r["commit"] == sys.argv[2] and not r.get("dirty") else 1)
PY
}

case "${1:-status}" in
  status) status ;;
  mark) put "last_deployed=$HEAD"; echo "Recorded ${HEAD:0:10} as deployed." ;;
  deploy)
    status; echo
    [ "$PENDING" -gt 0 ] || { echo "Nothing to deploy."; exit 0; }
    if [ "$PENDING" -lt "$BATCH_SIZE" ] && [ "${2:-}" != "--force" ]; then
      echo "Batch not full ($PENDING of $BATCH_SIZE). Keep collecting changes, or use --force."; exit 0
    fi
    if [ "$LEFT" -le "$RESERVE" ] && [ "${2:-}" != "--force" ]; then
      echo "Only $LEFT builds left this month; the last $RESERVE are kept for hotfixes. Use --force for a hotfix."; exit 1
    fi
    gate
    echo "Deploying $PENDING commit(s) as one build. Builds left after this: $((LEFT - 1))."
    eval "$DEPLOY_CMD"
    put "previous_deployed=$LAST" "last_deployed=$HEAD" "builds_used=$((USED + 1))"
    tlog --event deploy --ok 1 --note "$PENDING commit(s)"
    echo "Deployed ${HEAD:0:10}."
    if [ "${POST_DEPLOY:-0}" = "1" ]; then
      python3 "$HERE/post_deploy_check.py" --wait --rollback
    else
      echo "Next: python3 scripts/post_deploy_check.py --wait --rollback"
    fi ;;
  rollback)
    if rollback; then
      put "rolled_back_from=$LAST"
      tlog --event rollback --ok 1 --note "from ${LAST:0:10}"
    else
      tlog --event rollback --ok 0 --note "manual steps needed"; exit 1
    fi ;;
  *) echo "usage: deploy_batch.sh status|deploy [--force]|mark|rollback"; exit 2 ;;
esac
