# Deploys

## Batch, don't drip

On Git-connected hosts every push to the production branch is a build. Free plans cap builds per month (Cloudflare Pages: 500), and every deploy is a moment the site can break. So:

1. Work on a branch (or commit locally without pushing).
2. Run the quick tier after each change.
3. When the batch is ready (a set threshold of changes, or the end of a working session), run the full tier once.
4. Merge and push once. One batch, one build.

`scripts/deploy_batch.sh` enforces this:

```
scripts/deploy_batch.sh status     # changes since last deploy, threshold, builds used and left this month
scripts/deploy_batch.sh deploy     # refuses unless tests/eval/report.md passed on the current commit
scripts/deploy_batch.sh deploy --force   # override the threshold (never the test gate)
```

State lives in `.deploy/state.json` (git-ignored): last deployed commit, builds used this month, month key. Configure with environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `BATCH_SIZE` | 10 | Changes (commits) per batch before an automatic deploy is suggested |
| `BUILD_LIMIT` | 500 | Builds allowed per month on your plan |
| `DEPLOY_BRANCH` | `main` | Branch that triggers production builds |
| `DEPLOY_CMD` | `git push origin main` | Command that deploys (swap for a CLI deploy on other hosts) |

Always say how many builds are left before deploying, and stop when you are within a reserve (default 20) of the limit, keeping those for hotfixes.

## Environments and previews

Push feature branches to get preview URLs without touching production. Preview builds count toward the same monthly build limit on Cloudflare, so batch those too.

Once real users and real money are involved, add a standing dev environment:

- A `dev` branch that builds a dev site (for example `dev.example.com`) with its own database, its own file bucket and test payment keys only. It never shares a binding or a secret with production.
- An `ENVIRONMENT=development` variable that the app exposes in its config, so every screen of the dev site shows a banner saying it is a development site with test data. Nobody mistakes it for the real site or enters real details there.
- Every non-production build is hidden from search engines in the build step itself, not by memory. On Cloudflare Pages, `CF_PAGES_BRANCH` names the branch being built:

```bash
if [ -n "${CF_PAGES_BRANCH:-}" ] && [ "$CF_PAGES_BRANCH" != "$PRODUCTION_BRANCH" ]; then
  printf '\n/*\n  X-Robots-Tag: noindex, nofollow\n' >> dist/_headers
  printf 'User-agent: *\nDisallow: /\n' > dist/robots.txt
  rm -f dist/sitemap.xml dist/llms.txt
fi
```

## Change management: a release gate

A small team can meet the change management part of SOC 2 (and stop "quick fixes" going straight to production) with three GitHub Actions workflows and one rule: nobody pushes to the production branch by hand.

1. **Quick checks on every pull request** into `dev` and `main`: build, compliance check, unit checks, server code parses. A red X means do not merge. Use a fixed job name (`Quick checks`) so the gate can look it up.
2. **A release gate** (`templates/github/release-gate.yml`). The host builds production from a separate branch (for example `live`). On every push to `main` the gate checks each change since the last release and moves `live` forward only when every change:
   - arrived through a pull request into `main` from `dev`, so it ran on the dev site first,
   - was approved by someone other than the person who opened it, and
   - passed the Quick checks on its head commit.
   If anything fails, nothing is published and the gate opens an issue saying which change failed and why.
3. **A detective control** (`templates/github/guard-production.yml`). The gate moves `live` with the workflow's own token, and pushes made with that token never start other workflows. So any push event on `live` means a person pushed directly, and the workflow opens an issue for review straight away.

Plan for the exceptions in writing, so the gate is never switched off in a hurry:

- **Emergency changes.** A pull request labelled `emergency` may skip the dev and approval steps. It is released, and an issue is opened so a second person reviews it within a set time (for example 2 business days).
- **Commits that reached main without a pull request.** A manual run of the gate with the commit SHAs and a written reason (at least a sentence) accepts them, and the reason is recorded in an issue.
- **Only one approver available.** When the second reviewer is not set up yet, use a time-boxed exception: an end date in the workflow, after which a second approval is required again without anyone remembering to switch it back. The other checks still apply, and every release made without a second approval is listed in an issue for later review. Record who decided it and why in the change management policy.

Add a pull request template that asks what changed, how it was tested on the dev site, whether privacy or security is affected, and the rollback step.

## Before every production deploy

- [ ] Full tier passed on this exact commit
- [ ] Privacy warnings reviewed and accepted
- [ ] Builds left this month stated
- [ ] Rollback path known (below)
- [ ] No dev flags in production environment variables
- [ ] The change reached production through the release gate, not a direct push

## After every production deploy: health check and rollback

Pre-deploy gates catch most problems, but some only exist in production: a binding or secret set on the wrong environment, a header rule that replaced another, a route that only worked locally. Close the loop automatically:

```bash
python3 scripts/post_deploy_check.py --wait --rollback
# or let the deploy run it: POST_DEPLOY=1 bash scripts/deploy_batch.sh deploy
```

1. **Wait for the new build, not the old one.** Have the build write the commit it was built from to a small public file (`echo "$CF_PAGES_COMMIT_SHA" > dist/version.txt`, or `git rev-parse HEAD`). `--wait` polls it until it shows the commit you deployed, so a check never passes against the previous build while the new one is still building.
2. **Check what users need.** For each page in the `post_deploy` block of `checks.json`: the expected status, a piece of text that proves the page rendered (`<h1`, `"ok":true`), the required security headers, and a response time limit. Include the home page, sign in, one key journey and a health route that touches the database.
3. **Retry before failing.** A page gets a couple of retries, 10 seconds apart, so a cold start doesn't trigger a rollback.
4. **Roll back on failure.** `--rollback` runs `bash scripts/deploy_batch.sh rollback` (below). Run the check again afterwards to confirm the old build is healthy, then fix forward on the dev site.

Still worth doing by hand: watch error logs for 15 minutes, and walk one journey on a real phone after any change to sign in or payments.

## Rollback

| Situation | Action |
|---|---|
| Build failed | Nothing to undo: the host keeps serving the last good build. Read the build log, fix, push. |
| Live site broken by a change | Revert the commit on the production branch and push (one build), or use the host's "rollback to this deployment" button (no build). |
| Bad data migration | Restore the database from its latest export or point-in-time restore, then revert the code. |
| Leaked secret | Rotate it in the provider and the secret store first, then clean history. |

Prefer the host's instant rollback for emergencies: it does not use a build and takes seconds.

**One command:** `bash scripts/deploy_batch.sh rollback`.
- **Cloudflare Pages:** set `CF_API_TOKEN` (an API token with the *Cloudflare Pages: Edit* permission, stored in your secret store or CI secrets, never in the repo), `CF_ACCOUNT_ID` and `CF_PAGES_PROJECT`. The script reads which deployment is live, picks the newest successful production deployment before it, and calls the Pages rollback API (`POST /accounts/{account_id}/pages/projects/{project}/deployments/{id}/rollback`). `ROLLBACK_TO=<deployment id>` picks a specific one.
- **Other hosts:** set `ROLLBACK_CMD` to the host's own rollback, for example `vercel rollback --yes`.
- **Nothing set:** it prints the dashboard steps.

A rollback restores code, not data. If the bad release ran a database migration, check that the old code still works with the new schema (additive migrations make this safe), or restore the database too.

## Scheduled jobs on the minute

GitHub Actions `schedule` runs often start several minutes late, and cron is in UTC. For something that must happen at an exact local time (publishing a post at 9:00):

- Schedule the job 20 minutes early and have it sleep until the target time, computed in the local time zone (`TZ=America/New_York date -d "today 09:00:05" +%s`).
- Add two cron lines, one for standard time and one for daylight time. The run that is not near the target that day exits straight away.
- Skip the wait on manual runs (`workflow_dispatch`) so you can test it.
- Give the workflow `permissions: {}` and a `timeout-minutes` when it only calls your own endpoint.
- Keep a slower fallback (an hourly job) that picks up anything the exact-time run missed.
- Have the endpoint return what each step of the job did (items published, the next one due, and the error message rather than a bare `error: true`), and print that response in the workflow log, so a run that did nothing can be traced without opening the database.

## Hand-over runbook

Write a short `docs/RUNBOOK.md` for anyone else who may need to ship a fix: how a change reaches production, where each service is managed, how to roll back, and what never to do (delete the database, set dev flags in production, share keys over chat).
