#!/usr/bin/env bash
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
# Batched deploys: count changes since the last production deploy, track builds used this month, and deploy only
# when the full tier has passed on the exact commit being shipped.
#
#   bash scripts/deploy_batch.sh status            changes pending, batch threshold, builds used and left
#   bash scripts/deploy_batch.sh deploy            deploy if the batch is full and tests passed on HEAD
#   bash scripts/deploy_batch.sh deploy --force    deploy before the batch is full (the test gate still applies)
#   bash scripts/deploy_batch.sh mark              record HEAD as deployed without deploying (first setup)
#
# Settings (environment variables):
#   BATCH_SIZE=10        commits per batch
#   BUILD_LIMIT=500      builds per month on your plan (Cloudflare Pages free: 500)
#   RESERVE=20           builds kept back for hotfixes; normal deploys stop at BUILD_LIMIT - RESERVE
#   DEPLOY_BRANCH=main
#   DEPLOY_CMD="git push origin main"   e.g. "npx wrangler pages deploy dist" or "netlify deploy --prod --dir dist"
#   REPORT=tests/eval/report.json       written by scripts/run_suite.py
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
    put "last_deployed=$HEAD" "builds_used=$((USED + 1))"
    echo "Deployed ${HEAD:0:10}. Check the build status on your host, then the live site." ;;
  *) echo "usage: deploy_batch.sh status|deploy [--force]|mark"; exit 2 ;;
esac
