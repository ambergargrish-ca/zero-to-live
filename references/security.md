# Security and privacy checklist

Work through the relevant sections for every change to auth, roles, data access, uploads, payments or anything that sends data to another company. `scripts/compliance_check.py` automates the mechanical parts; the rest needs a person.

## Separation of front end and back end

- [ ] The browser calls only your API; it never holds database credentials.
- [ ] Every route declares who may call it and is checked on the server for every request.
- [ ] Every input is validated: type, length, allowed values, URL scheme (`https:` only for links you will render).
- [ ] Every SQL value is a bound parameter. Table and column names never come from a request.
- [ ] There is no route that runs arbitrary SQL or changes schema.
- [ ] State-changing requests require JSON and a matching `Origin` header (CSRF).
- [ ] Server code, schema, config and tests are not in the published output.

## Authorization beyond role checks

Role checks on obvious admin routes are the easy part. Check one level down as well:

- [ ] **Object ownership.** A user with the right role can only act on their own objects. Knowing another object's ID (a video, a file, an order) must not let them read, edit or delete it.
- [ ] **Sensitive fields inside allowed pages.** A role allowed to open a dashboard may still not be allowed to see every number on it. Filter fields on the server by role, not in the UI.
- [ ] **Step-up requirements apply to every route.** If a role must have MFA, every route for that role refuses until MFA is set up, including read-only ones.
- [ ] **Security changes end old sessions.** Turning on MFA, changing a password or resetting it signs out every other session for that account.
- [ ] **Capacity abuse.** Limited resources (seats, stock, slots) cannot be held indefinitely by unpaid or abandoned checkouts; cap holds per account and expire them.
- [ ] **Payment state machines.** Webhooks are verified by signature, handled idempotently, and order states only move forward along defined transitions, whatever order events arrive in.

## Sessions and passwords

- [ ] Session cookie uses the `__Host-` prefix, `HttpOnly`, `Secure`, `SameSite=Lax` (or `Strict`), and a bounded lifetime.
- [ ] Session tokens are stored hashed on the server.
- [ ] Passwords are hashed with a slow salted function (PBKDF2 with a high iteration count, scrypt or Argon2).
- [ ] Sign in, sign up, reset and code entry are rate limited and protected by a bot check.
- [ ] Reset links are single use and short lived; they lead to the MFA step, not past it.
- [ ] MFA codes are single use; recovery codes are stored hashed; repeated failures lock the step for a period; changes to MFA email the account owner.
- [ ] MFA secrets are encrypted at rest with a key held in the secret store.

## Headers

- [ ] `Content-Security-Policy` with no `unsafe-eval`, no inline scripts, explicit sources, `frame-ancestors 'none'`, `base-uri 'self'`, `object-src 'none'`, `form-action` restricted.
- [ ] `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` turning off camera, microphone, geolocation and payment unless needed.
- [ ] `noindex` on preview deploys and signed-in areas.

## Output encoding

- [ ] JSON embedded in HTML (JSON-LD, bootstrapped data) escapes `<` so content cannot close the script tag.
- [ ] User content is inserted with `textContent` or escaped templates, never `innerHTML` with raw strings.
- [ ] Links to payment or third-party flows are checked as `https:` before rendering.

## Uploads

- [ ] Type checked by first bytes (magic numbers), not name or header.
- [ ] Size capped before storage; large uploads checked on the first chunk.
- [ ] Stored privately; served only after a permission check.
- [ ] HTML, SVG and scripts refused unless you serve them from a separate sandboxed origin.

## Rate limits and abuse

- [ ] Per-IP limits on all API routes in code, with stricter limits on auth and public chat or contact endpoints.
- [ ] An edge rate limit rule (free on most hosts), excluding payment webhooks.
- [ ] Public free-text endpoints (contact, chat, reports) capped in length and frequency.

## Secrets and dependencies

- [ ] `.env*`, `.dev.vars*`, `*.pem`, `*.key` in `.gitignore` from the first commit.
- [ ] Secrets only in the platform secret store; preview environments use test keys only.
- [ ] A committed secret is rotated immediately; deleting the file does not remove it from history.
- [ ] `npm audit` (or equivalent) is clean; dependencies pinned by a lock file; reviewed quarterly.
- [ ] Development bypass flags are honoured only with `DEV_MODE`, and production refuses to start with it set.

## Logging

- [ ] Every privileged action (role change, refund, export, deletion, MFA reset) writes an audit log row with who, what and when.
- [ ] Errors and request outcomes are recorded so attacks and failures are visible.
- [ ] Logs do not contain passwords, tokens or full card data.

## Privacy by design

- [ ] Analytics and marketing scripts and cookies load only after consent; the consent choice can be changed from every page.
- [ ] Sign-up consent to Terms and Privacy Policy is explicit; marketing email consent is separate and unticked.
- [ ] Every consent is logged with the policy version it was given for.
- [ ] Users can export their data and delete their account; deletion removes personal data and files, keeping only what law requires (anonymised).
- [ ] Retention periods are written down and actually enforced by a scheduled job.
- [ ] Every new table, column, outside service, cookie or storage key is reviewed against the privacy policy before deploy. `compliance_check.py` warns on each one; `--accept` records the review.
- [ ] Policy text changes bump a version, and users are notified.
- [ ] A named privacy contact, a breach log, and a lawyer review before launch.

## Running an audit

- Scope it. A capped audit of the riskiest areas (auth, payments, uploads, access control) finds most real issues for a fraction of the cost of a full sweep.
- For each finding, record: severity, the invariant it breaks, a reproduction, the fix, and a regression test.
- Fix, add the test to the full tier, and re-run the affected suites before closing.
- Keep audit reports out of public repositories until every finding is fixed.
