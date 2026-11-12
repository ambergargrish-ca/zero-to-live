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

## Previews

Push feature branches to get preview URLs without touching production. Preview builds count toward the same monthly build limit on Cloudflare, so batch those too. Keep preview URLs `noindex`.

## Before every production deploy

- [ ] Full tier passed on this exact commit
- [ ] Privacy warnings reviewed and accepted
- [ ] Builds left this month stated
- [ ] Rollback path known (below)
- [ ] No dev flags in production environment variables

## After every production deploy

- [ ] Build finished green (check the commit status on the Git host or the host dashboard)
- [ ] Open the home page, a key journey and the sign-in page on the live domain
- [ ] Check response headers on the live domain (`curl -sI https://example.com/ | grep -i content-security`)
- [ ] Watch error logs for 15 minutes

## Rollback

| Situation | Action |
|---|---|
| Build failed | Nothing to undo: the host keeps serving the last good build. Read the build log, fix, push. |
| Live site broken by a change | Revert the commit on the production branch and push (one build), or use the host's "rollback to this deployment" button (no build). |
| Bad data migration | Restore the database from its latest export or point-in-time restore, then revert the code. |
| Leaked secret | Rotate it in the provider and the secret store first, then clean history. |

Prefer the host's instant rollback for emergencies: it does not use a build and takes seconds.

## Scheduled jobs on the minute

GitHub Actions `schedule` runs often start several minutes late, and cron is in UTC. For something that must happen at an exact local time (publishing a post at 9:00):

- Schedule the job 20 minutes early and have it sleep until the target time, computed in the local time zone (`TZ=America/New_York date -d "today 09:00:05" +%s`).
- Add two cron lines, one for standard time and one for daylight time. The run that is not near the target that day exits straight away.
- Skip the wait on manual runs (`workflow_dispatch`) so you can test it.
- Give the workflow `permissions: {}` and a `timeout-minutes` when it only calls your own endpoint.
- Keep a slower fallback (an hourly job) that picks up anything the exact-time run missed.

## Hand-over runbook

Write a short `docs/RUNBOOK.md` for anyone else who may need to ship a fix: how a change reaches production, where each service is managed, how to roll back, and what never to do (delete the database, set dev flags in production, share keys over chat).
