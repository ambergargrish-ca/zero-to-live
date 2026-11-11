# Bug log

32 bugs found during the build, all fixed. Each one records the root cause and what now stops it coming back.

## Summary

| Severity | Count |
|---|---|
| High | 5 |
| Medium | 16 |
| Low | 11 |

| Type | Count |
|---|---|
| Security | 14 |
| Functional | 6 |
| UI | 5 |
| Operational | 2 |
| Performance | 2 |
| Test | 1 |
| Accessibility | 1 |
| Process | 1 |

| Found by | Count |
|---|---|
| Security audit | 7 |
| Pen test | 5 |
| Lighthouse | 3 |
| UAT on phone | 2 |
| Live smoke test | 2 |
| Product owner on phone | 1 |
| Test run | 1 |
| Header check | 1 |
| Responsive audit | 1 |
| Product owner review | 1 |
| Feature test | 1 |
| UAT | 1 |
| UAT on iPhone | 1 |
| Product owner sign-up test | 1 |
| Product owner | 1 |
| Audit | 1 |
| Setup review | 1 |
| Usage review | 1 |

**Pattern worth noting:** most security findings came from scheduled tests (pen test, audits), most UI bugs from real-phone UAT. Automated suites catch regressions; humans on real devices catch what nobody thought to test.

## All bugs

| ID | Bug | Severity | Type | Story | Found by | Fixed |
|---|---|---|---|---|---|---|
| B01 | Invisible overlays blocked taps; swipe and anchor links misbehaved on phones | High | Functional | S002 | UAT on phone | Nov 6 |
| B07 | Sign up failed when the confirmation email couldn't be sent | High | Functional | S021 | Live smoke test | Nov 6 |
| B09 | Sign in showed 'Database not connected' after first deploy | High | Operational | S016 | Live smoke test | Nov 6 |
| B12 | Portal pages lost their security headers | High | Security | S016 | Header check | Nov 9 |
| B15 | Job applications admin route replaced the instructor applications route | High | Functional | S038 | Feature test | Nov 10 |
| B02 | JSON-LD could be broken out of by content containing '</' | Medium | Security | S013 | Pen test | Nov 6 |
| B03 | Inline scripts forced a weak Content Security Policy | Medium | Security | S049 | Pen test | Nov 6 |
| B04 | Build config files were publicly downloadable | Medium | Security | S049 | Pen test | Nov 6 |
| B08 | Returning visitors kept stale CSS and JS after releases | Medium | Functional | S019 | Product owner on phone | Nov 6 to 7 |
| B10 | Notification panel overflowed phone screens | Medium | UI | S029 | UAT on phone | Nov 7 |
| B13 | Tablet navigation wrapped to two lines; portal tabs and hero card overflowed; small tap targets | Medium | UI | S047 | Responsive audit | Nov 9 to 10 |
| B14 | Help chatbot quoted wrong start dates and schedules | Medium | Functional | S039 | Product owner review | Nov 9 |
| B17 | Career profile dates overflowed on iPhone; school years missed | Medium | UI | S037 | UAT on iPhone | Nov 10 |
| B18 | Short password showed 'Password is required' instead of 'too short' | Medium | Functional | S022 | Product owner sign-up test | Nov 10 |
| B19 | Turning on two-step sign in didn't end sessions opened with only a password | Medium | Security | S023 | Security audit | Nov 11 |
| B20 | One account could hold every seat with unpaid checkouts | Medium | Security | S031 | Security audit | Nov 11 |
| B26 | Home page blocked the main thread for over 1 second | Medium | Performance | S051 | Lighthouse | Nov 11 |
| B27 | Sign in page jumped on phones | Medium | Performance | S051 | Lighthouse | Nov 11 |
| B28 | Accessibility score 96: duplicate image labels and crowded footer links | Medium | Accessibility | S051 | Lighthouse | Nov 11 |
| B29 | Blank flash and outlined box on every page change | Medium | UI | S009 | Product owner (screen recording) | Nov 11 |
| B32 | An unscoped audit fanned out to 13 agents and exhausted the usage limit | Medium | Process | S048 | Usage review | Nov 11 |
| B05 | Form inputs had no length limits | Low | Security | S004 | Pen test | Nov 6 |
| B06 | Checkout links were not forced to HTTPS | Low | Security | S031 | Pen test | Nov 6 |
| B11 | Carousel arrow tests failed because the Help button covered it | Low | Test | S046 | Test run | Nov 7 |
| B16 | Portal briefly drew outdated navigation | Low | UI | S026 | UAT | Nov 10 |
| B21 | Staff without two-step sign in could see applicants and tickets | Low | Security | S024 | Security audit | Nov 11 |
| B22 | An instructor could delete another course's video by ID | Low | Security | S028 | Security audit | Nov 11 |
| B23 | Managers could see money amounts on Insights and in the course editor | Low | Security | S024 | Security audit | Nov 11 |
| B24 | A late payment event could re-activate a refunded seat | Low | Security | S034 | Security audit | Nov 11 |
| B25 | Sign up revealed whether an email already had an account | Low | Security | S021 | Security audit | Nov 11 |
| B30 | Build dependency had known vulnerabilities | Low | Security | S050 | Audit | Nov 11 |
| B31 | Hosting setup started on the wrong product (Workers instead of Pages) | Low | Operational | S016 | Setup review | Nov 6 |

## Root cause and prevention

### B01 Invisible overlays blocked taps; swipe and anchor links misbehaved on phones

- **Severity / type:** High / Functional  (epic E01, story S002)
- **Found by:** UAT on phone, Nov 6
- **Root cause:** Hidden layers stayed in the hit area after their animation ended
- **Fix:** Removed hidden layers from the hit area; fixed swipe and anchor handling
- **Prevention:** Site suite clicks real elements at phone sizes

### B02 JSON-LD could be broken out of by content containing '</'

- **Severity / type:** Medium / Security  (epic E03, story S013)
- **Found by:** Pen test, Nov 6
- **Root cause:** Structured data written into the page without escaping
- **Fix:** Escape '<' in all embedded JSON
- **Prevention:** Compliance check fails on unescaped JSON-LD

### B03 Inline scripts forced a weak Content Security Policy

- **Severity / type:** Medium / Security  (epic E12, story S049)
- **Found by:** Pen test, Nov 6
- **Root cause:** Small scripts embedded directly in pages
- **Fix:** Moved every script to files; CSP now script-src 'self'
- **Prevention:** Compliance check fails on inline scripts or handlers

### B04 Build config files were publicly downloadable

- **Severity / type:** Medium / Security  (epic E12, story S049)
- **Found by:** Pen test, Nov 6
- **Root cause:** Build copied the whole repo to the web root
- **Fix:** Build publishes an allow-list only; config paths blocked
- **Prevention:** Test asserts dist/ has no config, server or test files

### B05 Form inputs had no length limits

- **Severity / type:** Low / Security  (epic E01, story S004)
- **Found by:** Pen test, Nov 6
- **Root cause:** Fields accepted unbounded text
- **Fix:** maxlength on every field and server-side caps
- **Prevention:** Pen test suite posts oversized inputs

### B06 Checkout links were not forced to HTTPS

- **Severity / type:** Low / Security  (epic E07, story S031)
- **Found by:** Pen test, Nov 6
- **Root cause:** Links rendered from config without a scheme check
- **Fix:** Only https: links render
- **Prevention:** Unit check on link rendering

### B07 Sign up failed when the confirmation email couldn't be sent

- **Severity / type:** High / Functional  (epic E05, story S021)
- **Found by:** Live smoke test, Nov 6
- **Root cause:** Email failure aborted account creation
- **Fix:** Account created; email retried and resend offered
- **Prevention:** Test with email service disabled

### B08 Returning visitors kept stale CSS and JS after releases

- **Severity / type:** Medium / Functional  (epic E04, story S019)
- **Found by:** Product owner on phone, Nov 6 to 7
- **Root cause:** Shared assets cached without a version in the URL
- **Fix:** Fingerprinted asset URLs; portal files revalidated
- **Prevention:** Build fails if an asset reference is unversioned

### B09 Sign in showed 'Database not connected' after first deploy

- **Severity / type:** High / Operational  (epic E04, story S016)
- **Found by:** Live smoke test, Nov 6
- **Root cause:** Database and storage bindings added after the build that was live
- **Fix:** Set bindings, then redeployed; runbook entry added
- **Prevention:** Runbook check after any settings change

### B10 Notification panel overflowed phone screens

- **Severity / type:** Medium / UI  (epic E06, story S029)
- **Found by:** UAT on phone, Nov 7
- **Root cause:** Panel sized for desktop
- **Fix:** Full-width panel under the header on phones
- **Prevention:** Responsive suite

### B11 Carousel arrow tests failed because the Help button covered it

- **Severity / type:** Low / Test  (epic E11, story S046)
- **Found by:** Test run, Nov 7
- **Root cause:** Floating Help button overlapped the control at some sizes
- **Fix:** Test clicks the control directly; layout spacing checked
- **Prevention:** Responsive suite overlap check

### B12 Portal pages lost their security headers

- **Severity / type:** High / Security  (epic E04, story S016)
- **Found by:** Header check, Nov 9
- **Root cause:** A second /app/* header rule replaced the first instead of adding to it
- **Fix:** One /app/* rule carrying every header
- **Prevention:** Compliance check verifies required headers

### B13 Tablet navigation wrapped to two lines; portal tabs and hero card overflowed; small tap targets

- **Severity / type:** Medium / UI  (epic E11, story S047)
- **Found by:** Responsive audit, Nov 9 to 10
- **Root cause:** Fixed widths and missing wrap rules
- **Fix:** Redesigned phone menu; nav on one line; tabs wrap; 44 px targets
- **Prevention:** 16-size responsive suite

### B14 Help chatbot quoted wrong start dates and schedules

- **Severity / type:** Medium / Functional  (epic E09, story S039)
- **Found by:** Product owner review, Nov 9
- **Root cause:** Bot read an outdated course field
- **Fix:** Bot reads the live schedule, sorted by start date
- **Prevention:** Chatbot answers checked against catalogue in tests

### B15 Job applications admin route replaced the instructor applications route

- **Severity / type:** High / Functional  (epic E08, story S038)
- **Found by:** Feature test, Nov 10
- **Root cause:** Two routes registered on the same path; the later one won
- **Fix:** Distinct paths
- **Prevention:** Compliance check fails on duplicate routes

### B16 Portal briefly drew outdated navigation

- **Severity / type:** Low / UI  (epic E06, story S026)
- **Found by:** UAT, Nov 10
- **Root cause:** Earlier render not cancelled when a newer one started
- **Fix:** Only the latest navigation renders
- **Prevention:** Smoke screen checks

### B17 Career profile dates overflowed on iPhone; school years missed

- **Severity / type:** Medium / UI  (epic E08, story S037)
- **Found by:** UAT on iPhone, Nov 10
- **Root cause:** Date inputs had intrinsic width; parser skipped years
- **Fix:** Full-width fields, dates side by side; year fallback
- **Prevention:** Responsive suite on iPhone sizes

### B18 Short password showed 'Password is required' instead of 'too short'

- **Severity / type:** Medium / Functional  (epic E05, story S022)
- **Found by:** Product owner sign-up test, Nov 10
- **Root cause:** Validation returned the wrong message key
- **Fix:** Correct message; live checklist added
- **Prevention:** Sign-up test covers each rule

### B19 Turning on two-step sign in didn't end sessions opened with only a password

- **Severity / type:** Medium / Security  (epic E05, story S023)
- **Found by:** Security audit, Nov 11
- **Root cause:** Session store not cleared on MFA enrolment
- **Fix:** Enabling MFA ends every other session
- **Prevention:** Regression test

### B20 One account could hold every seat with unpaid checkouts

- **Severity / type:** Medium / Security  (epic E07, story S031)
- **Found by:** Security audit, Nov 11
- **Root cause:** Pending holds counted per checkout, not per person
- **Fix:** One open checkout per buyer; one hold per person
- **Prevention:** Regression test

### B21 Staff without two-step sign in could see applicants and tickets

- **Severity / type:** Low / Security  (epic E05, story S024)
- **Found by:** Security audit, Nov 11
- **Root cause:** MFA requirement checked on some routes only
- **Fix:** Without MFA, staff act as learners on every route
- **Prevention:** Role-by-route test matrix

### B22 An instructor could delete another course's video by ID

- **Severity / type:** Low / Security  (epic E06, story S028)
- **Found by:** Security audit, Nov 11
- **Root cause:** Delete checked role, not ownership
- **Fix:** Videos belong to their course; shared videos kept until unused
- **Prevention:** Object-ownership tests

### B23 Managers could see money amounts on Insights and in the course editor

- **Severity / type:** Low / Security  (epic E05, story S024)
- **Found by:** Security audit, Nov 11
- **Root cause:** Field filtering missing on two screens
- **Fix:** Amounts hidden for managers everywhere
- **Prevention:** Platform tests for manager view

### B24 A late payment event could re-activate a refunded seat

- **Severity / type:** Low / Security  (epic E07, story S034)
- **Found by:** Security audit, Nov 11
- **Root cause:** Events applied in arrival order
- **Fix:** Refund remembered; order states only move forward
- **Prevention:** Out-of-order webhook test

### B25 Sign up revealed whether an email already had an account

- **Severity / type:** Low / Security  (epic E05, story S021)
- **Found by:** Security audit, Nov 11
- **Root cause:** Different response for existing emails
- **Fix:** Same response for every email; owner notified by email
- **Prevention:** Regression test

### B26 Home page blocked the main thread for over 1 second

- **Severity / type:** Medium / Performance  (epic E13, story S051)
- **Found by:** Lighthouse, Nov 11
- **Root cause:** Many elements measured one by one on load
- **Fix:** Single measurement pass (1,010 ms to under 500 ms)
- **Prevention:** Lighthouse gate on key pages

### B27 Sign in page jumped on phones

- **Severity / type:** Medium / Performance  (epic E13, story S051)
- **Found by:** Lighthouse, Nov 11
- **Root cause:** Form changed height after a script loaded
- **Fix:** Final height reserved in CSS (shift 0.235 to 0)
- **Prevention:** Lighthouse gate

### B28 Accessibility score 96: duplicate image labels and crowded footer links

- **Severity / type:** Medium / Accessibility  (epic E13, story S051)
- **Found by:** Lighthouse, Nov 11
- **Root cause:** Logos repeated their label; links too close
- **Fix:** Unique labels; spacing (score 100)
- **Prevention:** Accessibility 100 gate

### B29 Blank flash and outlined box on every page change

- **Severity / type:** Medium / UI  (epic E02, story S009)
- **Found by:** Product owner (screen recording), Nov 11
- **Root cause:** Loading screen shown on every navigation
- **Fix:** Brand screen on first page only; cross fade; early load on hover
- **Prevention:** UAT script

### B30 Build dependency had known vulnerabilities

- **Severity / type:** Low / Security  (epic E12, story S050)
- **Found by:** Audit, Nov 11
- **Root cause:** Old build tool version, no lockfile
- **Fix:** Upgraded with a lockfile (0 known issues)
- **Prevention:** Dependency audit in the full tier

### B31 Hosting setup started on the wrong product (Workers instead of Pages)

- **Severity / type:** Low / Operational  (epic E04, story S016)
- **Found by:** Setup review, Nov 6
- **Root cause:** Repo built for Pages; dashboard flow defaulted elsewhere
- **Fix:** Switched to the Pages flow with build command and output dir
- **Prevention:** Platform guide states the exact settings

### B32 An unscoped audit fanned out to 13 agents and exhausted the usage limit

- **Severity / type:** Medium / Process  (epic E11, story S048)
- **Found by:** Usage review, Nov 11
- **Root cause:** No scope or agent cap; full suites after small edits
- **Fix:** Capped, scoped audits; quick tier for small changes
- **Prevention:** Testing tiers in the skill
