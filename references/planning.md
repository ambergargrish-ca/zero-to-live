# Planning

A one-page plan before code saves days later. Keep it in the repo (`docs/PLAN.md`) and update it when scope changes.

## 1. The one-page plan

| Section | Answer in a sentence or a short list |
|---|---|
| Audience | Who visits, on what device, what they came to do |
| Pages | Each page and its single job ("Courses: pick a course and reserve a seat") |
| Data | Every piece of personal information stored, why, and for how long |
| Outside services | Every company that receives data (email, payments, forms, analytics) and in which country |
| Roles | Who can do what (visitor, member, staff, admin) |
| Done means | Lighthouse targets, supported browsers, screen sizes, legal pages reviewed |
| Out of scope | What you are deliberately not building yet |

The "Data" and "Outside services" rows become your privacy policy. Writing them first stops surprise data collection.

## 2. Static or dynamic, per page

Default every page to static. Move a route to server code only when it needs one of:

- a database read or write
- a secret (API key, signing key)
- per-user content behind sign in

Marketing pages, course listings that change weekly and legal pages stay static and are rebuilt on deploy. This keeps hosting free or close to it and removes most of the attack surface.

## 3. Phase the build

1. **Launch site:** static pages, forms through a form service, SEO basics, legal pages. Live in days.
2. **Accounts:** sign in, roles, a database, audit log.
3. **Money:** checkout, webhooks, refunds. Only after accounts are tested.
4. **Everything else:** dashboards, uploads, integrations.

Each phase ships on its own and passes the full tier before the next starts.

## 4. Decisions to make up front

- **Hosting and build budget.** How many deploys the plan allows a month; this drives batching (see `deploys.md`).
- **Domain and DNS owner.** Who holds the registrar login. Move DNS to the host only when the new build is verified.
- **Who approves what.** Who signs off privacy changes, paid services, and production deploys.
- **Cost ceiling.** Stay on free tiers until there is revenue; list what would trigger an upgrade.

## 5. Plan the tests with the features

For each feature, write its acceptance checks in the plan ("a visitor without consent loads no analytics script"). These become test cases in `testing.md` and stop "done" from being a feeling.
