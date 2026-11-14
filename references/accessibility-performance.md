# Accessibility and performance

## Targets (Lighthouse, mobile, local production build)

| Category | Target | Gate |
|---|---|---|
| Accessibility | 100 | Blocks deploy |
| Performance | 90+ (marketing pages), 85+ (heavy home page) | Blocks deploy below 80 |
| Best Practices | 95+ | Warn |
| SEO | 90+ on indexable pages | Warn; `noindex` pages are exempt by design |

Core Web Vitals on a mid-range phone: LCP under 2.5 s, CLS under 0.1, INP under 200 ms, Total Blocking Time under 300 ms.

Run `scripts/lighthouse.sh` against the local build. Lab scores vary by a few points between runs; judge on two runs, not one.

### Known false negatives

Record these in your performance notes so nobody chases them:
- Best Practices drops when a sandbox blocks outside fonts or images (console errors that do not happen in production).
- SEO flags unknown `robots.txt` directives (for example Cloudflare's `Content-Signal`). Keep them if intended.
- SEO is low on `noindex` pages on purpose.

## Accessibility checklist

- [ ] `lang` on `<html>`, one `<h1>` per page, headings in order
- [ ] Skip link to main content, visible on focus
- [ ] Every interactive element reachable and usable by keyboard, with a visible focus style
- [ ] Colour contrast 4.5:1 for text, 3:1 for large text and UI parts, in light and dark themes
- [ ] Every form field has a `<label>`; errors are announced (`aria-live` or `aria-describedby`)
- [ ] Every image has alt text; decorative images use `alt=""`; no duplicate labels on adjacent links
- [ ] Tap targets at least 24 by 24 CSS px (44 preferred), with spacing between neighbours
- [ ] No content only conveyed by colour
- [ ] Motion respects `prefers-reduced-motion`; count-ups and staged reveals are skipped, and the final value is already in the HTML
- [ ] Anything that moves, scrolls or cycles on its own for more than 5 seconds (rotating taglines, carousels, tickers) stops by itself or has a pause control (WCAG 2.2.2). The simplest fix is one round, then rest on the default state. Also pause it on hover, keyboard focus and hidden tabs
- [ ] Animated text that replaces an image keeps the accessible name on the link and hides the moving part with `aria-hidden="true"`
- [ ] A count of new messages is in the button's accessible name, not only in a visual badge, and sound is never the only signal
- [ ] Shared components (cookie banner, chat) are contrast checked on every surface that loads them, since the app's own button styles can override the public site's
- [ ] Custom controls (quiz options, tabs, toggle buttons, a dialog's close button, checklist boxes) each get a `:focus-visible` style; toggles set `aria-pressed` or `aria-selected`, and text revealed by a click lands in an `aria-live` region
- [ ] Dialogs trap focus and return it on close
- [ ] Skip link and other off-screen helpers hidden until focused (a skip link that shows on every page load looks like a bug)

Automate with axe-core in the site suite; Lighthouse alone misses issues.

## Performance checklist

| Item | How |
|---|---|
| Static files skip server code | `_routes.json` excludes assets (Cloudflare) |
| Long cache for assets | `Cache-Control: public, max-age=604800` on `/assets/*`, fingerprinted URLs |
| Short edge cache for public reads | 60 to 120 s TTL on public catalogue API responses; never on per-user responses |
| Minified CSS and JS | esbuild in the build |
| Code split | Load dashboard areas on demand |
| Deferred scripts | Chat, consent, analytics and search scripts load with `defer` |
| Images | WebP/AVIF, `srcset`, width and height set, lazy below the fold |
| Fonts | `font-display: swap`, preconnect, two weights at most |
| No layout shift | Reserve space for images, embeds and late content; measure once, not per item |
| Image to live text | When animated text replaces a logo image, keep the image until `document.fonts.load()` resolves and `document.fonts.check()` passes, and reserve the widest state's width, so no fallback font flashes and nothing shifts |
| Measured overlays | A canvas or overlay sized from a container that grows after load watches that container with `ResizeObserver`, not only window resize |
| Skeletons | Show a placeholder for lists that load after the page |
| Pagination | Every list paginated; admin lists capped |
| Debounce | Search inputs wait 250 to 300 ms after typing |
| Indexes | Every query column indexed |

## Common fixes that moved scores

- **Blocking time over 1 s on a home page** came from measuring many elements in a loop on load. Measure once in a single pass and defer the rest.
- **Layout shift on a sign-in page** came from a form that changed height after a script loaded. Reserve its final height in CSS.
- **Accessibility 96** came from duplicate image labels and crowded footer links. De-duplicate labels and add spacing.
