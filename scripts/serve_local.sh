#!/usr/bin/env bash
# Part of zero-to-live (https://github.com/ambergargrish-ca/zero-to-live). Copyright (c) 2026 Amber Gargrish. MIT License.
# Start a local Cloudflare Pages server (wrangler pages dev) with a local D1 database and R2 bucket, then wait
# until it answers. Reuses a running server unless "fresh" is given.
#
#   bash scripts/serve_local.sh          start, or reuse a healthy running server
#   bash scripts/serve_local.sh fresh    stop it, wipe the local database and storage, start clean
#   bash scripts/serve_local.sh stop     stop it
#
# Settings (environment variables):
#   PORT=8788            local port
#   DIST=dist            build output directory
#   HEALTH=/api/health   path that returns 2xx when the app is ready (use / for a static site)
#   D1=DB  R2=FILES      binding names (set to empty to skip)
#   BINDINGS="DEV_MODE=1 ADMIN_EMAILS=admin@example.com"   extra plain bindings for local runs only
#   LOG=.wrangler/dev.log
#
# Never put real secrets in BINDINGS. Development-only flags must be honoured by your code only when DEV_MODE is set.
set -uo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PORT="${PORT:-8788}"; DIST="${DIST:-dist}"; HEALTH="${HEALTH:-/api/health}"
D1="${D1-DB}"; R2="${R2-FILES}"; BINDINGS="${BINDINGS:-DEV_MODE=1}"; LOG="${LOG:-.wrangler/dev.log}"
URL="http://localhost:${PORT}${HEALTH}"

stop() { pkill -f "wrangler pages dev" 2>/dev/null; sleep 2; }

case "${1:-}" in
  stop) stop; echo "stopped"; exit 0 ;;
  fresh) stop; rm -rf .wrangler/state ;;
  *) curl -fs -m 2 "$URL" >/dev/null && { echo "already running on :$PORT"; exit 0; } ;;
esac

ARGS=(pages dev "$DIST" --port "$PORT")
[ -n "$D1" ] && ARGS+=(--d1 "$D1")
[ -n "$R2" ] && ARGS+=(--r2 "$R2")
for b in $BINDINGS; do ARGS+=(--binding "$b"); done

mkdir -p "$(dirname "$LOG")"
nohup npx wrangler "${ARGS[@]}" >"$LOG" 2>&1 &
for _ in $(seq 1 60); do
  curl -fs -m 2 "$URL" >/dev/null && { echo "ready on :$PORT"; exit 0; }
  sleep 1
done
echo "server did not start; last log lines:"; tail -20 "$LOG"; exit 1
