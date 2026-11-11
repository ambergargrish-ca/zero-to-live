# Testing

Two tiers. The quick tier runs on every change and takes seconds to a few minutes. The full tier runs once per deploy batch and can take as long as it needs.

## Why tiers

Running every suite after a one-line copy change wastes time and, when an AI agent is doing the work, burns a lot of tokens on output nobody reads. Running nothing ships regressions. The answer is to run what the change can break, then everything before it goes live.

## Quick tier: every change

`scripts/quick_check.py` reads the diff (`git diff --name-only` against the last deployed commit, or `HEAD` plus uncommitted changes) and runs only the commands whose patterns match. Configure the mapping in `checks.json`:

```json
{
  "always": ["python3 scripts/compliance_check.py"],
  "map": [
    { "paths": ["data/**", "build.py", "assets/**"], "run": ["python3 build.py", "python3 tests/site.py --pages changed"] },
    { "paths": ["server/auth*.js"], "run": ["python3 tests/auth_e2e.py"], "server": true },
    { "paths": ["server/payments*.js"], "run": ["python3 tests/payments_e2e.py"], "server": true }
  ]
}
```

Rules:
- `always` covers the compliance and security check. It is fast; never skip it.
- A path that matches nothing runs only `always`. If that happens for a code file, add a mapping.
- `"server": true` starts the local server with a fresh database first.
- Smoke-test layout at three sizes (390, 768, 1440) only when CSS or layout changed.

## Full tier: before each deploy batch

`scripts/run_suite.py` runs every suite in `checks.json` under `"full"`, each against a fresh local database, and writes `tests/eval/report.md` with pass counts, times and the first failures. Exit code 0 only when everything passes. `deploy_batch.sh` reads that report's timestamp and commit and refuses to deploy if it is older than the last change.

A good full tier for a site with accounts and payments:

| Suite | Covers |
|---|---|
| Compliance | Secrets, CSP, headers, SQL safety, privacy drift |
| Site | Every public page at phone, tablet and desktop: links, titles, meta, alt text, no console errors, no horizontal scroll, forms intercepted |
| Accessibility | axe-core on every page; Lighthouse Accessibility 100 |
| Auth | Sign up, confirm, sign in, reset, MFA, session invalidation |
| Roles | Every route called as every role; each must allow or refuse correctly |
| Payments | Checkout with test keys, webhook signature check, duplicate and out-of-order webhooks, refunds |
| Uploads | Allowed types pass; renamed scripts and HTML are refused; size caps |
| Screens | 16 sizes from 320 to 2560 px, every element measured |
| Lighthouse | Key pages on mobile against targets |

## Writing suites that stay useful

- **Playwright** (Python or Node) for browser journeys. Block outside fonts and images in one run to prove fallbacks work.
- **Intercept form posts** so tests never send real emails or submissions.
- **One `check(suite, id, name, ok, detail)` helper** that prints `PASS`/`FAIL` lines in a fixed format, so the runner can count them.
- **Fresh database per suite.** Shared state between suites hides bugs and creates flaky ones.
- **Test the refusal, not just the success.** For every privileged action, assert that the wrong role, a signed-out user and another user's object all get 401, 403 or 404.
- **Test bindings for local only.** Flags such as `LIMITS_OFF_FOR_TESTS` must be read only when `DEV_MODE` is set. Add a test that they are ignored without it.

## UAT

Before a launch or a major feature, walk the real journeys on a phone against a preview deploy: find a page, fill a form, sign up, pay with a test card, receive the email, sign out. Write them down as numbered steps so anyone can repeat them.
