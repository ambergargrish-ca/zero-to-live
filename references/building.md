# Building

## Repository layout

```
build.py            generates every HTML page from data + one layout function
data/               content as JSON (courses, products, FAQs); edited without touching code
assets/             css, js, images (served as-is, fingerprinted)
server/             API code (never published)
functions/          platform entry points that call server/ (Cloudflare: functions/api/[[path]].js)
tests/              suites, fixtures, reports (never published)
scripts/            build and deploy helpers
docs/               plan, runbook, security notes
```

The build copies only public files into `dist/`. Server code, tests, data sources and config never ship. Use an allow-list (or a skip-list you review) in the build script, and add a test that `dist/` contains no `.py`, `.toml`, `.env`, `server/` or `tests/`.

## One layout function

Every page goes through one function, for example `page(title, description, body, canonical)`, that renders:

- `<html lang>`, viewport meta, title, description, canonical URL, Open Graph tags
- skip link, header and navigation with `aria-current="page"`
- footer with privacy policy link, terms, cookie settings button
- deferred scripts only

A page that bypasses the layout is a compliance bug: it loses the privacy link and cookie settings. The compliance check warns on it.

## Front-end rules

- **No inline scripts or handlers** (`<script>...</script>`, `onclick=`). Put code in files so the CSP can use `script-src 'self'`. JSON-LD (`type="application/ld+json"`) is the one allowed inline block, and its content must be escaped (replace `<` with `<`) so data cannot close the tag.
- **Design tokens** for colour, spacing, radius and type in CSS custom properties. No one-off values.
- **Mobile first.** Build at 360px wide, then widen. No horizontal scroll at 320px.
- **Images:** width and height attributes, `loading="lazy"` below the fold, WebP or AVIF, `srcset` for sizes. Every image has alt text (empty `alt=""` for decorative ones).
- **Forms:** labels on every field, `maxlength` on every text input, a one-line privacy notice next to the submit button, a bot check (Turnstile, hCaptcha) on public forms.
- **Fallbacks:** if a font, image CDN or API fails, the page still reads and works. Test it by blocking them.
- **Fingerprint** CSS and JS (`app.js?v=3f2a9c1b`) at build time, and cache `/assets/*` for a week or more. After changing a shared asset, rebuild every page that loads it: a page still carrying the old hash keeps serving the old file, so the change never reaches browsers. `scripts/compliance_check.py` fails when a page's hash does not match the file.
- **Signed-in state on static pages.** To show an account menu instead of "Sign in" without slowing every visit, have the app set a harmless hint in browser storage at sign in (and clear it at sign out). Public pages only call the session endpoint when the hint is there, and show nothing until the server confirms the session. The hint is never trusted for access.

## SEO and AI-crawler basics

Ship these with the first deploy:

| File or tag | Purpose |
|---|---|
| `<title>`, meta description | Unique per page, under 60 and 155 characters |
| `<link rel="canonical">` | One URL per page; use clean URLs (`/courses`, not `/courses.html`) |
| `robots.txt` | Allow crawlers, list the sitemap; decide explicitly which AI crawlers you allow |
| `sitemap.xml` | Every indexable page with `lastmod`, and never a page marked `noindex` (search consoles flag the contradiction). Filter the sitemap by each page's robots tag at build time rather than keeping a separate list |
| `llms.txt` | Plain-text summary of the site and links to key pages for AI agents |
| JSON-LD | `Organization`, `Person`, `Product`/`Course`, `FAQPage`, `BreadcrumbList` as they apply |
| `noindex` | On sign-in, dashboards, preview deploy URLs and any `/md/` agent copies |

Write content that can be cited: a clear first sentence per section that answers the heading, real numbers, named authors.

## Server code rules

- One router; each route declares `auth: none | user | staff | admin` and a validator for every input (type, length, allowed values).
- Schema in code, created or migrated on start, with indexes for every lookup column.
- Paginate every list; cap admin lists.
- An audit log row for every privileged action (role change, refund, deletion, export).
- Edge-cache public reads for a short TTL; never cache anything per user.
- Hide a screen in the menu **and** tighten its API route to the same role. A hidden link with an open route is not access control.

## Outside integrations

- **Syndicated copies point home.** When a post is copied to another platform, set that platform's canonical or original URL field to your page, and make relative links absolute, so search engines credit your site.
- **GraphQL errors arrive with HTTP 200.** Parse the body and treat a non-empty `errors` array as a failure; also catch HTML error pages that are not JSON.
- **Renew OAuth tokens before they expire.** Store refresh tokens encrypted and renew a few days before expiry instead of waiting for a failed call.
- **Map provider errors to plain messages.** A missing permission or an unapproved API product is not the same as the user cancelling; tell the admin which one happened and what to do.
- **Record share results per item.** Save each platform's result or error on the item so a failed share can be retried without re-sharing the ones that worked.
- **Content files import once, revisions on purpose.** If content files seed database records that people then edit, import each file once, and let a raised `revision` number in the file replace an item that is not live yet. Live items are never changed from a file.

## Build script checklist

- [ ] Fails the build on any error (`set -euo pipefail`)
- [ ] Copies only public files to `dist/`
- [ ] Minifies CSS and JS
- [ ] Fingerprints assets
- [ ] Writes `_headers`, `_redirects`, `_routes.json` (see `stack-cloudflare.md`)
- [ ] Prints a file count so a sudden jump or drop is visible
