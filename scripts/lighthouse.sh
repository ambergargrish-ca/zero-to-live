#!/usr/bin/env bash
# Run Lighthouse (mobile) on key pages of a local or preview build and check the scores against targets.
#
#   bash scripts/lighthouse.sh                         pages from PAGES, against BASE
#   bash scripts/lighthouse.sh / /pricing /signup      these pages
#
# Settings (environment variables):
#   BASE=http://localhost:8788
#   PAGES="/"                     space separated paths, used when no arguments are given
#   MIN_A11Y=100  MIN_PERF=90  MIN_BP=95  MIN_SEO=90
#   GATE="a11y perf"              categories that fail the run; the others only warn
#   NOINDEX="/app/login"          paths exempt from the SEO target (kept out of search on purpose)
#   OUT=tests/eval/lighthouse     where JSON reports go
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BASE="${BASE:-http://localhost:8788}"; OUT="${OUT:-tests/eval/lighthouse}"
MIN_A11Y="${MIN_A11Y:-100}"; MIN_PERF="${MIN_PERF:-90}"; MIN_BP="${MIN_BP:-95}"; MIN_SEO="${MIN_SEO:-90}"
GATE="${GATE:-a11y perf}"; NOINDEX="${NOINDEX:-}"
PAGES_LIST=("$@"); [ ${#PAGES_LIST[@]} -eq 0 ] && read -r -a PAGES_LIST <<<"${PAGES:-/}"
mkdir -p "$OUT"
status=0
printf "%-28s %6s %6s %6s %6s\n" "Page" "Perf" "A11y" "BP" "SEO"
for p in "${PAGES_LIST[@]}"; do
  name=$(echo "$p" | sed 's#[^a-zA-Z0-9]#_#g'); [ "$name" = "_" ] && name="home"
  npx --yes lighthouse "${BASE}${p}" --quiet --output=json --output-path="$OUT/$name.json" \
    --only-categories=performance,accessibility,best-practices,seo \
    --chrome-flags="--headless=new --no-sandbox" >/dev/null 2>&1 || { echo "FAIL  $p: lighthouse did not run"; status=1; continue; }
  line=$(python3 - "$OUT/$name.json" "$p" <<PY
import json, sys
r = json.load(open(sys.argv[1]))["categories"]
s = {k: round((r[k]["score"] or 0) * 100) for k in ["performance", "accessibility", "best-practices", "seo"]}
page, noindex = sys.argv[2], "$NOINDEX".split()
mins = {"performance": ("perf", $MIN_PERF), "accessibility": ("a11y", $MIN_A11Y), "best-practices": ("bp", $MIN_BP), "seo": ("seo", $MIN_SEO)}
gate, bad, warn = "$GATE".split(), [], []
for k, (short, m) in mins.items():
    if short == "seo" and page in noindex: continue
    if s[k] < m: (bad if short in gate else warn).append(f"{short} {s[k]}<{m}")
print(f"{page[:28]:<28} {s['performance']:>6} {s['accessibility']:>6} {s['best-practices']:>6} {s['seo']:>6}|{';'.join(bad)}|{';'.join(warn)}")
PY
)
  IFS='|' read -r row bad warn <<<"$line"
  echo "$row"
  [ -n "$warn" ] && echo "  WARN  $p: $warn"
  [ -n "$bad" ] && { echo "  FAIL  $p: $bad"; status=1; }
  [ -z "$bad" ] && echo "  PASS  $p"
done
exit $status
