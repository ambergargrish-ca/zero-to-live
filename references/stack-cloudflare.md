# Cloudflare stack: Pages, Functions, D1, R2

The preferred path: static files and server code in one Pages project, a SQLite database (D1) and object storage (R2), all on the free tier to start.

## Free plan limits that shape the design

Check the current numbers at https://developers.cloudflare.com/pages/platform/limits before relying on them.

| Limit | Value (Nov 2026) | Design consequence |
|---|---|---|
| Builds per month | 500 | Batch deploys (see `deploys.md`) |
| Concurrent builds | 1 per account | Two pushes queue; don't push twice for one change |
| Files per site | 20,000 | Don't ship test screenshots or source maps you don't need |
| File size | 25 MiB per asset | Large video or files go to R2 or a video service, not `dist/` |
| `_headers` | 100 rules, 2,000 characters per header | Keep CSP compact; generate the file |
| `_routes.json` | 100 rules (include + exclude) | Exclude asset folders with wildcards, not file by file |

Function requests count against the Workers request quota, so keep static files off Functions with `_routes.json`.

## Project layout

```
functions/api/[[path]].js     catch-all: export onRequest = ctx => handle(ctx) from server/
server/                       router, auth, schema, handlers (bundled into the Function, not served)
dist/                         build output (Build output directory)
dist/_headers                 security headers
dist/_redirects               redirects
dist/_routes.json             which paths run Functions
```

Pages settings: Build command `bash scripts/build.sh` (or your build), Build output directory `dist`, production branch `main`.

## Bindings

Set in the Pages project under Settings, Bindings (separately for Production and Preview):

| Binding | Type | Used as |
|---|---|---|
| `DB` | D1 database | `env.DB.prepare("SELECT ... WHERE id = ?").bind(id).first()` |
| `FILES` | R2 bucket | `env.FILES.put(key, body, { httpMetadata })`, `env.FILES.get(key)` |
| `SITE_URL` | Variable | Absolute URLs in emails and redirects |
| `ADMIN_EMAILS` | Variable | Bootstrap admins (only after their email is confirmed) |
| API keys | **Secret** (encrypted) | Never a plain variable, never in the repo |

Locally, `wrangler pages dev dist --d1 DB --r2 FILES --binding DEV_MODE=1` gives a throwaway database and bucket under `.wrangler/state`. `scripts/serve_local.sh` wraps this.

## D1

- Create tables with `CREATE TABLE IF NOT EXISTS` on first request, or with `wrangler d1 migrations`. Pick one and keep it.
- Always bind values (`?`). Never build SQL with template strings from request data.
- Add an index for every column used in `WHERE`, `JOIN` or `ORDER BY`.
- Use `env.DB.batch([...])` for multi-statement writes that must succeed together.
- For "reserve a limited resource" flows (seats, stock), count and insert in one guarded statement and cap how many pending holds one account can have, so one user cannot exhaust capacity with unpaid holds.
- Export regularly: `wrangler d1 export <db> --remote --output backup.sql`. D1 also offers point-in-time restore (Time Travel); know how to use it before you need it.

## R2

- Keep the bucket private. Serve files through a Function that checks permission, then streams `env.FILES.get(key)`.
- Check the file type by its first bytes (magic numbers), not the name or the `Content-Type` header, and cap size before writing.
- Use lifecycle rules to delete temporary files (recordings, exports) automatically.
- R2 requires a payment method on the account even on the free tier.

## `_headers`

Generate it from one source of truth in the build so headers never drift. See `templates/_headers` for a starting point: strict CSP without `unsafe-eval` or inline scripts, HSTS, `nosniff`, strict referrer policy, permissions policy, `frame-ancestors 'none'`. Add `X-Robots-Tag: noindex` for `https://:project.pages.dev/*` so preview URLs stay out of search.

## `_routes.json`

Without it, every request (images, CSS) invokes your Function. `scripts/make_routes.py` writes:

```json
{ "version": 1, "include": ["/*"], "exclude": ["/assets/*", "/favicon.ico", "/robots.txt", "/sitemap.xml"] }
```

## Secrets and environments

- Production and Preview have separate variables and secrets. Previews must never hold live payment keys.
- Development flags (`DEV_MODE`, test-only bypasses) must be honoured only when `DEV_MODE` is set, and `DEV_MODE` must never be set in Production. Add a startup assertion that refuses to run with a dev flag on a production hostname.

## Rate limiting

- In code: a small per-IP counter in memory per isolate (cheap, approximate) for all API routes, plus stricter limits on sign in, password reset and code entry.
- At the edge: one free-plan rate limiting rule on `/api/*`, excluding payment webhooks.

## Custom domain

Add the domain in the Pages project, Custom domains. If DNS is elsewhere, move nameservers to Cloudflare first. Keep the old host running until the new domain serves the verified build, then remove it.
