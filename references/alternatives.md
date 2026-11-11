# Alternatives to Cloudflare

The workflow, rules and scripts are host-neutral. Only the platform glue changes.

| Need | Cloudflare | Netlify | Vercel | AWS | Self-hosted |
|---|---|---|---|---|---|
| Static hosting | Pages | Netlify sites | Vercel | S3 + CloudFront | Nginx/Caddy |
| Server code | Pages Functions | Netlify Functions | Vercel Functions | Lambda | Node/Python app |
| SQL database | D1 (SQLite) | Netlify DB / external Postgres | Vercel Postgres partners (Neon) | RDS / Aurora | Postgres / SQLite |
| Object storage | R2 | Netlify Blobs | Vercel Blob | S3 | MinIO / disk |
| Headers | `_headers` | `_headers` or `netlify.toml` | `vercel.json` | CloudFront response policy | server config |
| Redirects | `_redirects` | `_redirects` | `vercel.json` | CloudFront Functions | server config |
| Secrets | Pages secrets | Environment variables (secret) | Environment variables | Secrets Manager / SSM | env file outside repo |
| Build budget | Builds per month | Build minutes / credits | Build minutes | Pay per use | Your CI |

## What changes per host

- **`scripts/serve_local.sh`:** swap `wrangler pages dev` for `netlify dev`, `vercel dev`, `sam local`, or your app server. Keep the health-check wait.
- **`scripts/make_routes.py`:** Cloudflare only. Other hosts serve static files without invoking functions by default.
- **`scripts/deploy_batch.sh`:** set `DEPLOY_CMD` (for example `netlify deploy --prod --dir dist`) or keep the git-push trigger. Set `BUILD_LIMIT` to your plan's monthly allowance, or to a cost cap you choose.
- **`scripts/compliance_check.py`:** point `headers_files` in `checks.json` at `netlify.toml`, `vercel.json` or your server config.

## Keep headers in one place

If you host on two platforms during a migration, generate both header files from one source (for example `netlify.toml` to `_headers`) so they cannot drift.

## Postgres instead of SQLite

Everything in `security.md` holds. Use parameterised queries in your driver (`$1`, `%s`), a connection pooler for serverless functions, and migrations (`node-pg-migrate`, Alembic, Prisma) instead of create-on-start.
