# Backlog

14 epics, 24 features, 60 user stories, 159 sub-tasks and 35 bugs. All items are **Done**.
Bugs are listed under the story where they were found and in full in [BUGS.md](BUGS.md).

## Epics

| Epic | Goal | Features | Stories | Bugs | Delivered |
|---|---|---|---|---|---|
| [E01 Launch site](#e01-launch-site) | Ship a fast, credible public site so visitors can find courses and register interest. | 2 | 5 | 2 | Nov 5 to 6 |
| [E02 Brand and design system](#e02-brand-and-design-system) | A consistent, accessible visual identity across site, portal and email. | 2 | 5 | 1 | Nov 6 to 10 |
| [E03 SEO and AI-engine readiness](#e03-seo-and-ai-engine-readiness) | Be found and cited by search engines and AI assistants. | 2 | 5 | 2 | Nov 6 to 12 |
| [E04 Hosting, CI and deploys](#e04-hosting-ci-and-deploys) | Free, reliable hosting with controlled, countable releases. | 2 | 5 | 4 | Nov 6 to 11 |
| [E05 Accounts and access](#e05-accounts-and-access) | Safe sign in with the right access for every role. | 2 | 7 | 7 | Nov 6 to 11 |
| [E06 Learning platform](#e06-learning-platform) | Everything a learner and instructor need to run a live course. | 2 | 5 | 3 | Nov 6 to 10 |
| [E07 Commerce](#e07-commerce) | Take payment safely and fairly, in the buyer's currency. | 2 | 4 | 3 | Nov 6 to 11 |
| [E08 Careers marketplace](#e08-careers-marketplace) | Connect learners and employers with real Canadian AI and tech jobs. | 2 | 4 | 2 | Nov 7 to 10 |
| [E09 Support and engagement](#e09-support-and-engagement) | Help visitors fast and keep them coming back. | 2 | 7 | 2 | Nov 7 to 11 |
| [E10 Privacy and compliance](#e10-privacy-and-compliance) | Collect only what we need, keep it only as long as stated, and prove it. | 2 | 4 | 0 | Nov 10 to 11 |
| [E11 Quality engineering](#e11-quality-engineering) | Know the product works before anyone else finds out it doesn't. | 1 | 3 | 3 | Nov 6 to 11 |
| [E12 Security](#e12-security) | Find and fix weaknesses before attackers do. | 1 | 2 | 3 | Nov 6 to 11 |
| [E13 Performance](#e13-performance) | Fast on a mid-range phone, cheap to serve. | 1 | 1 | 3 | Nov 10 to 11 |
| [E14 Productisation: zero-to-live](#e14-productisation-zero-to-live) | Turn the build's methods into a reusable, citable open-source Claude skill. | 1 | 3 | 0 | Nov 11 |

## E01 Launch site

**Goal:** Ship a fast, credible public site so visitors can find courses and register interest.  
**Delivered:** Nov 5 to 6

### F01.1 Marketing pages

#### S001  ·  Done  ·  Nov 5

As a visitor, I want clear pages for courses, coaching, team training and instructors so that I can find the right offer quickly.

**Acceptance criteria**

- [x] Every offer has its own page with one primary action
- [x] Navigation marks the current page
- [x] Works from 320 px wide

**Sub-tasks**

- [x] S001-T1 Write page content as data (JSON) instead of hard-coded HTML
- [x] S001-T2 Build every page from one layout function
- [x] S001-T3 Add About, FAQ, Privacy, Terms and Credits pages

#### S002  ·  Done  ·  Nov 6

As a visitor, I want a course catalogue with filters so that I can compare cohorts at a glance.

**Acceptance criteria**

- [x] Filters by topic and format
- [x] Each card shows outcomes, schedule and a reserve action

**Sub-tasks**

- [x] S002-T1 Course data file with schedule fields
- [x] S002-T2 Carousel and slider with keyboard and swipe support
- [x] S002-T3 Static catalogue pre-rendered for crawlers

**Bugs found**

- B01 (High, Functional): Invisible overlays blocked taps; swipe and anchor links misbehaved on phones

#### S003  ·  Done  ·  Nov 6

As a visitor, I want a back-to-top control on long pages so that I don't have to scroll back manually.

**Acceptance criteria**

- [x] Appears after scrolling, reachable by keyboard
- [x] Respects reduced motion

**Sub-tasks**

- [x] S003-T1 Add control to shared layout
- [x] S003-T2 Cover it in the site suite

### F01.2 Lead capture

#### S004  ·  Done  ·  Nov 6

As a visitor, I want to request a seat, coaching or a team quote through a form so that someone follows up with me.

**Acceptance criteria**

- [x] Four forms: seat, coaching, team enquiry, instructor application
- [x] Bot check on every public form
- [x] Per-form email subject so requests are easy to triage

**Sub-tasks**

- [x] S004-T1 Wire forms to a hosted form service
- [x] S004-T2 Add bot check
- [x] S004-T3 Intercept form posts in tests so no real emails send

**Bugs found**

- B05 (Low, Security): Form inputs had no length limits

#### S005  ·  Done  ·  Nov 6

As a university partner, I want an enquiry page so that I can start a partnership conversation.

**Acceptance criteria**

- [x] Dedicated page with a short enquiry form

**Sub-tasks**

- [x] S005-T1 Partnership page and form
- [x] S005-T2 Add to sitemap

## E02 Brand and design system

**Goal:** A consistent, accessible visual identity across site, portal and email.  
**Delivered:** Nov 6 to 10

### F02.1 Design tokens and identity

#### S006  ·  Done  ·  Nov 6

As a visitor, I want a consistent look across every page so that the brand feels trustworthy.

**Acceptance criteria**

- [x] Typography, spacing and radius come from tokens
- [x] Logo has enough contrast on dark surfaces

**Sub-tasks**

- [x] S006-T1 Define type, spacing and radius tokens
- [x] S006-T2 Swap icon set
- [x] S006-T3 Restore original wordmark after contrast review
- [x] S006-T4 Favicons and share image

#### S007  ·  Done  ·  Nov 7

As a signed-in user, I want the portal in the same dark theme as the site so that it feels like one product.

**Acceptance criteria**

- [x] Student, instructor and admin screens use the site palette

**Sub-tasks**

- [x] S007-T1 Port tokens into the portal
- [x] S007-T2 Check contrast in both themes

#### S008  ·  Done  ·  Nov 10

As a recipient, I want branded emails with buttons instead of raw links so that emails look legitimate and are easy to act on.

**Acceptance criteria**

- [x] Logo and tagline in every email
- [x] Action buttons, not pasted URLs

**Sub-tasks**

- [x] S008-T1 Shared email template
- [x] S008-T2 Button component with allow-listed link labels

### F02.2 Motion and media

#### S009  ·  Done  ·  Nov 6 to 11

As a first-time visitor, I want a short branded loading moment and smooth page changes so that navigation feels polished.

**Acceptance criteria**

- [x] Brand screen only on the first page of a visit
- [x] Cross fade between pages, no blank flash

**Sub-tasks**

- [x] S009-T1 Loading screen
- [x] S009-T2 Prefetch on hover
- [x] S009-T3 Replace full blank with cross fade

**Bugs found**

- B29 (Medium, UI): Blank flash and outlined box on every page change

#### S010  ·  Done  ·  Nov 6

As a visitor, I want relevant photography with credits so that pages feel real, not generic.

**Acceptance criteria**

- [x] Every image credited
- [x] Illustration fallback if an image fails

**Sub-tasks**

- [x] S010-T1 Source photos
- [x] S010-T2 Credits page
- [x] S010-T3 Fallback art

## E03 SEO and AI-engine readiness

**Goal:** Be found and cited by search engines and AI assistants.  
**Delivered:** Nov 6 to 12

### F03.1 Crawlability and structured data

#### S011  ·  Done  ·  Nov 6

As a search engine, I want clean URLs, a sitemap and per-page metadata so that every page indexes correctly.

**Acceptance criteria**

- [x] Unique title, description and canonical on every page
- [x] sitemap.xml with every indexable page
- [x] Clean URLs without .html

**Sub-tasks**

- [x] S011-T1 Per-page metadata in the layout
- [x] S011-T2 Generate sitemap at build
- [x] S011-T3 Redirect .html to clean URLs

**Bugs found**

- B33 (Medium, SEO): Sitemap listed a page marked noindex

#### S012  ·  Done  ·  Nov 6

As an AI assistant, I want llms.txt, Markdown copies and explicit crawler rules so that I can read and cite the site accurately.

**Acceptance criteria**

- [x] robots.txt states which AI crawlers are allowed
- [x] llms.txt summarises the site
- [x] Markdown copies are noindex

**Sub-tasks**

- [x] S012-T1 llms.txt
- [x] S012-T2 Markdown for agents with Link headers
- [x] S012-T3 Content signals in robots.txt

#### S013  ·  Done  ·  Nov 6

As a search engine, I want structured data so that courses, people and FAQs show rich results.

**Acceptance criteria**

- [x] Organization, Person, Course, FAQ JSON-LD
- [x] JSON-LD content escaped

**Sub-tasks**

- [x] S013-T1 Schema generator in the build
- [x] S013-T2 Validator check in the suite

**Bugs found**

- B02 (Medium, Security): JSON-LD could be broken out of by content containing '</'

### F03.2 Migration hygiene

#### S014  ·  Done  ·  Nov 10

As a visitor following an old link, I want old addresses to redirect so that I never land on a 404.

**Acceptance criteria**

- [x] Every old address that search engines still know redirects with 301

**Sub-tasks**

- [x] S014-T1 Collect old URLs
- [x] S014-T2 Redirect rules
- [x] S014-T3 Test every redirect

#### S015  ·  Done  ·  Nov 6

As a Canadian visitor, I want the site marked for my locale so that search shows the right version.

**Acceptance criteria**

- [x] hreflang en-CA on every page

**Sub-tasks**

- [x] S015-T1 Add hreflang to the layout

## E04 Hosting, CI and deploys

**Goal:** Free, reliable hosting with controlled, countable releases.  
**Delivered:** Nov 6 to 11

### F04.1 Platform migration

#### S016  ·  Done  ·  Nov 6

As the product owner, I want the site and API on one free platform so that hosting costs nothing and nothing sleeps.

**Acceptance criteria**

- [x] Static pages on Pages, API on Functions, data in D1, files in R2
- [x] Old host kept until the new domain serves the verified build

**Sub-tasks**

- [x] S016-T1 Decide stack with options and trade-offs
- [x] S016-T2 Pages project, bindings and secrets
- [x] S016-T3 Build script writing dist/
- [x] S016-T4 DNS move

**Bugs found**

- B09 (High, Operational): Sign in showed 'Database not connected' after first deploy
- B12 (High, Security): Portal pages lost their security headers
- B31 (Low, Operational): Hosting setup started on the wrong product (Workers instead of Pages)

#### S017  ·  Done  ·  Nov 10

As an operator, I want a runbook so that someone else can ship a fix or roll back without me.

**Acceptance criteria**

- [x] How a change reaches production
- [x] Rollback in one step
- [x] What never to do

**Sub-tasks**

- [x] S017-T1 Write docs/RUNBOOK.md
- [x] S017-T2 Write docs/PLATFORM.md

### F04.2 Release control

#### S018  ·  Done  ·  Nov 6 to 11

As the product owner, I want deploys batched and counted so that we stay inside the monthly build limit.

**Acceptance criteria**

- [x] One deploy per batch of changes
- [x] Builds left this month stated before each deploy

**Sub-tasks**

- [x] S018-T1 Batch counter
- [x] S018-T2 Deploy only after the full tier passes
- [x] S018-T3 Track builds used per month

#### S019  ·  Done  ·  Nov 6 to 7

As a visitor, I want the latest code on my device so that I never run a stale app.

**Acceptance criteria**

- [x] Fingerprinted asset URLs
- [x] Portal files revalidated on every visit

**Sub-tasks**

- [x] S019-T1 Version shared assets in the build
- [x] S019-T2 Cache headers per path

**Bugs found**

- B08 (Medium, Functional): Returning visitors kept stale CSS and JS after releases

#### S020  ·  Done  ·  Nov 11

As a job seeker, I want job listings refreshed hourly so that I see current openings without waiting for a visit.

**Acceptance criteria**

- [x] Scheduled refresh runs hourly
- [x] Failures don't affect the live site

**Sub-tasks**

- [x] S020-T1 Scheduled CI job
- [x] S020-T2 Retention sweep on the same schedule

## E05 Accounts and access

**Goal:** Safe sign in with the right access for every role.  
**Delivered:** Nov 6 to 11

### F05.1 Sign up and sign in

#### S021  ·  Done  ·  Nov 6

As a learner, I want to create an account and confirm my email so that I can enrol and track progress.

**Acceptance criteria**

- [x] Email confirmation link
- [x] Bot check on sign up, sign in and reset
- [x] Sign up still works if the email service is down

**Sub-tasks**

- [x] S021-T1 Account tables and sessions
- [x] S021-T2 Confirmation and reset emails
- [x] S021-T3 Graceful fallback when email fails

**Bugs found**

- B07 (High, Functional): Sign up failed when the confirmation email couldn't be sent
- B25 (Low, Security): Sign up revealed whether an email already had an account

#### S022  ·  Done  ·  Nov 10

As a learner, I want clear password rules with a live checklist so that I know why a password is rejected.

**Acceptance criteria**

- [x] Show and hide password
- [x] Re-enter box on sign up
- [x] Live checklist; server enforces the same rules

**Sub-tasks**

- [x] S022-T1 Password policy on server
- [x] S022-T2 Checklist component
- [x] S022-T3 Correct error text for short passwords

**Bugs found**

- B18 (Medium, Functional): Short password showed 'Password is required' instead of 'too short'

#### S023  ·  Done  ·  Nov 10 to 11

As a staff member, I want two-step sign in with an authenticator app so that my account is protected.

**Acceptance criteria**

- [x] Authenticator enrolment and recovery codes
- [x] Turning it on ends other sessions

**Sub-tasks**

- [x] S023-T1 TOTP enrolment
- [x] S023-T2 Hashed recovery codes
- [x] S023-T3 Session invalidation

**Bugs found**

- B19 (Medium, Security): Turning on two-step sign in didn't end sessions opened with only a password

#### S055  ·  Done  ·  Nov 11

As a signed in learner browsing the public site, I want an account menu instead of "Sign in" so that I can jump to my screens without signing in again.

**Acceptance criteria**

- [x] Menu lists only the screens this person's role can use, plus Sign out
- [x] Visitors who are not signed in make no extra request
- [x] Nothing shows until the server confirms the session
- [x] Phone menu gets the same links

**Sub-tasks**

- [x] S055-T1 Sign in hint set by the app at sign in and cleared at sign out
- [x] S055-T2 Account menu with role-based links, hover and keyboard support
- [x] S055-T3 Same links in the phone menu

**Bugs found**

- B34 (Medium, Functional): Account menu did not reach browsers after release

### F05.2 Roles and permissions

#### S024  ·  Done  ·  Nov 6 to 11

As an admin, I want roles for learners, instructors, managers, agents and admins so that each sees only what they need.

**Acceptance criteria**

- [x] Role-aware sign in
- [x] Managers can do everything except money
- [x] Admin approval for manual course assignment

**Sub-tasks**

- [x] S024-T1 Role model
- [x] S024-T2 Route-level guards
- [x] S024-T3 Field-level filtering of money for managers

**Bugs found**

- B21 (Low, Security): Staff without two-step sign in could see applicants and tickets
- B23 (Low, Security): Managers could see money amounts on Insights and in the course editor

#### S025  ·  Done  ·  Nov 10

As an employee, I want one employee sign in so that my screens follow the role tied to my email.

**Acceptance criteria**

- [x] Single entry point for all staff
- [x] Screens set by role at onboarding

**Sub-tasks**

- [x] S025-T1 Employee sign in page
- [x] S025-T2 Role mapping

#### S056  ·  Done  ·  Nov 11

As an admin, I want the curriculum builder inside Admin and limited to admins and managers so that the top bar stays short and only staff can change course outlines.

**Acceptance criteria**

- [x] Curricula is a tab in Admin, not a top bar item
- [x] The API route returns curricula to admins and managers only
- [x] Old links redirect to the Admin tab

**Sub-tasks**

- [x] S056-T1 Curricula tab in Admin
- [x] S056-T2 API route limited to staff roles

## E06 Learning platform

**Goal:** Everything a learner and instructor need to run a live course.  
**Delivered:** Nov 6 to 10

### F06.1 Learner experience

#### S026  ·  Done  ·  Nov 6

As a learner, I want a dashboard and course player so that I can join classes, watch replays and track progress.

**Acceptance criteria**

- [x] Join button 15 minutes before class
- [x] Replays available for a fixed window
- [x] Progress saved per lesson

**Sub-tasks**

- [x] S026-T1 Dashboard
- [x] S026-T2 Course player
- [x] S026-T3 Replay access window

**Bugs found**

- B16 (Low, UI): Portal briefly drew outdated navigation

#### S027  ·  Done  ·  Nov 7

As a learner, I want a verifiable certificate I can add to LinkedIn so that employers can trust my credential.

**Acceptance criteria**

- [x] Completion based on attendance
- [x] Public verification page by code
- [x] Add-to-LinkedIn link

**Sub-tasks**

- [x] S027-T1 Certificate generator
- [x] S027-T2 Verification page
- [x] S027-T3 Attendance rule

### F06.2 Instructor and admin tools

#### S028  ·  Done  ·  Nov 6 to 10

As an instructor, I want a course studio so that I can build curricula, post class links and upload recordings.

**Acceptance criteria**

- [x] Curriculum builder
- [x] Class link per session
- [x] Recording upload

**Sub-tasks**

- [x] S028-T1 Studio screens
- [x] S028-T2 Curriculum builder
- [x] S028-T3 Recordings to private object storage

**Bugs found**

- B22 (Low, Security): An instructor could delete another course's video by ID

#### S029  ·  Done  ·  Nov 7

As an admin, I want bulk course editing, notifications and notices so that running the catalogue is quick.

**Acceptance criteria**

- [x] Bulk edit and delete
- [x] Badge counts and platform notices

**Sub-tasks**

- [x] S029-T1 Bulk actions
- [x] S029-T2 Notification model and panel

**Bugs found**

- B10 (Medium, UI): Notification panel overflowed phone screens

#### S030  ·  Done  ·  Nov 10

As the product owner, I want recordings stored in free object storage so that video costs nothing.

**Acceptance criteria**

- [x] Recordings and lesson videos in R2
- [x] Auto-deleted after the replay window

**Sub-tasks**

- [x] S030-T1 Upload and playback via the API
- [x] S030-T2 Lifecycle deletion

## E07 Commerce

**Goal:** Take payment safely and fairly, in the buyer's currency.  
**Delivered:** Nov 6 to 11

### F07.1 Checkout

#### S031  ·  Done  ·  Nov 6 to 7

As a learner, I want to pay at checkout and get my seat immediately so that enrolment is instant.

**Acceptance criteria**

- [x] Hosted checkout; no card data touches our servers
- [x] Webhook verified by signature
- [x] Seat activates only after payment

**Sub-tasks**

- [x] S031-T1 Checkout session
- [x] S031-T2 Webhook handler with idempotency
- [x] S031-T3 Admin-only test course

**Bugs found**

- B06 (Low, Security): Checkout links were not forced to HTTPS
- B20 (Medium, Security): One account could hold every seat with unpaid checkouts

#### S032  ·  Done  ·  Nov 7

As an international buyer, I want prices in my currency and tax worked out for my location so that the total is clear.

**Acceptance criteria**

- [x] Local currency display
- [x] Tax by buyer location
- [x] Tax number on receipts

**Sub-tasks**

- [x] S032-T1 Currency conversion
- [x] S032-T2 Location-based tax
- [x] S032-T3 Receipt fields

#### S033  ·  Done  ·  Nov 7

As a learner, I want to enter a promo code on our own checkout page so that discounts are easy to apply.

**Acceptance criteria**

- [x] Promo box on the page
- [x] Invalid codes explained

**Sub-tasks**

- [x] S033-T1 Promo validation

### F07.2 Refunds

#### S034  ·  Done  ·  Nov 7 to 11

As an admin, I want one-step refunds with clear confirmation so that access and money stay in sync.

**Acceptance criteria**

- [x] Refund removes access in the same step
- [x] Provider's reason shown when a refund fails
- [x] A late payment event can't undo a refund

**Sub-tasks**

- [x] S034-T1 Refund action
- [x] S034-T2 Error surfacing
- [x] S034-T3 Forward-only order states

**Bugs found**

- B24 (Low, Security): A late payment event could re-activate a refunded seat

## E08 Careers marketplace

**Goal:** Connect learners and employers with real Canadian AI and tech jobs.  
**Delivered:** Nov 7 to 10

### F08.1 Job board

#### S035  ·  Done  ·  Nov 9

As a job seeker, I want a Canada-focused AI and tech job board with verified employers so that I only see real roles.

**Acceptance criteria**

- [x] Verified employers
- [x] Imports from careers pages
- [x] Search and filters

**Sub-tasks**

- [x] S035-T1 Job model and imports
- [x] S035-T2 Verification flow
- [x] S035-T3 Search

#### S036  ·  Done  ·  Nov 9

As a job seeker, I want courses and jobs linked so that I can see which course leads to which role.

**Acceptance criteria**

- [x] Course matches on job pages
- [x] Jobs links on course pages

**Sub-tasks**

- [x] S036-T1 Matching rules
- [x] S036-T2 Cross links

### F08.2 Applications and hiring

#### S037  ·  Done  ·  Nov 10

As a job seeker, I want a career profile filled from my resume so that applying is fast.

**Acceptance criteria**

- [x] Resume first with auto-fill
- [x] Cropped photo
- [x] Preferences with up to 5 locations

**Sub-tasks**

- [x] S037-T1 Resume parsing
- [x] S037-T2 Photo crop
- [x] S037-T3 Preferences

**Bugs found**

- B17 (Medium, UI): Career profile dates overflowed on iPhone; school years missed

#### S038  ·  Done  ·  Nov 10

As an employer, I want Easy Apply and an applicant tracker so that I can manage candidates on the platform.

**Acceptance criteria**

- [x] One-click apply
- [x] Applicant stages
- [x] Photos hidden until the person applies

**Sub-tasks**

- [x] S038-T1 Easy Apply
- [x] S038-T2 ATS views
- [x] S038-T3 Photo privacy rule

**Bugs found**

- B15 (High, Functional): Job applications admin route replaced the instructor applications route

## E09 Support and engagement

**Goal:** Help visitors fast and keep them coming back.  
**Delivered:** Nov 7 to 11

### F09.1 Help and support

#### S039  ·  Done  ·  Nov 7 to 10

As a visitor, I want a help chatbot that knows courses, jobs and pages so that I get answers without waiting.

**Acceptance criteria**

- [x] Answers from current catalogue and schedules
- [x] Hands off to a live queue
- [x] Closes after inactivity

**Sub-tasks**

- [x] S039-T1 Chatbot with site knowledge
- [x] S039-T2 Live chat queue and tickets
- [x] S039-T3 Staff alerts

**Bugs found**

- B14 (Medium, Functional): Help chatbot quoted wrong start dates and schedules

#### S040  ·  Done  ·  Nov 9

As a visitor, I want site search so that I can find a course, job or page directly.

**Acceptance criteria**

- [x] Search across courses, jobs and pages

**Sub-tasks**

- [x] S040-T1 Search index
- [x] S040-T2 Search UI with debounce

### F09.2 Content

#### S041  ·  Done  ·  Nov 11

As the product owner, I want a blog with an approval step and auto-sharing so that content builds reach without extra work.

**Acceptance criteria**

- [x] Drafts twice a week
- [x] Approve in admin before publishing
- [x] Shares to social and developer platforms with canonical link

**Sub-tasks**

- [x] S041-T1 Blog pages
- [x] S041-T2 Approval workflow
- [x] S041-T3 Share integrations

#### S057  ·  Done  ·  Nov 11

As an admin, I want blog drafts waiting for approval to show on the notification bell and the Admin badges so that no draft misses its publish date.

**Acceptance criteria**

- [x] Bell lists the number of drafts waiting with a link to the Blog tab
- [x] Admin menu and Blog tab show a badge
- [x] New draft files are imported before counting

**Sub-tasks**

- [x] S057-T1 Count drafts waiting
- [x] S057-T2 Bell item and badges

#### S058  ·  Done  ·  Nov 11

As the product owner, I want each live post copied to a second developer platform and shared on the company page so that it reaches more readers while search engines still credit our site.

**Acceptance criteria**

- [x] Copies set our page as the original URL and use absolute links
- [x] Company page posting uses its own connection
- [x] Each platform's result or error shows on the post and can be retried
- [x] Connections renew before they expire

**Sub-tasks**

- [x] S058-T1 Copy to Hashnode with the original URL set
- [x] S058-T2 Company page sharing with its own connection
- [x] S058-T3 Token renewal before expiry
- [x] S058-T4 Per-platform result and error saved on each post

**Bugs found**

- B35 (Low, Functional): Company page connection said 'cancelled' when page posting was not approved yet

#### S059  ·  Done  ·  Nov 11

As the product owner, I want approved posts to go live at 9:00 local time on the minute so that the share lands when readers are online.

**Acceptance criteria**

- [x] Publishes within a minute of the target time despite late scheduler starts
- [x] Works in both standard and daylight time
- [x] Other times are still picked up by the hourly job

**Sub-tasks**

- [x] S059-T1 Early-start workflow that waits for the local target time
- [x] S059-T2 Two schedules for standard and daylight time

#### S060  ·  Done  ·  Nov 11

As an editor, I want to push a rewritten draft file over a post that is not live yet so that a revised draft replaces the old one without losing its approval or publish time.

**Acceptance criteria**

- [x] A raised revision number in the file replaces the text once
- [x] Status and publish time are kept
- [x] Live posts are never changed from a file

**Sub-tasks**

- [x] S060-T1 Revision field in content files
- [x] S060-T2 Replace text once per revision, keep status

## E10 Privacy and compliance

**Goal:** Collect only what we need, keep it only as long as stated, and prove it.  
**Delivered:** Nov 10 to 11

### F10.1 Consent and policies

#### S042  ·  Done  ·  Nov 10

As a visitor, I want to choose cookies and change my mind from any page so that tracking only happens with consent.

**Acceptance criteria**

- [x] Analytics loads only after opt-in
- [x] Cookie settings in every footer
- [x] Consent logged with policy version

**Sub-tasks**

- [x] S042-T1 Consent banner and settings
- [x] S042-T2 Consent log
- [x] S042-T3 Footer control

#### S043  ·  Done  ·  Nov 10

As an account holder, I want to be told when policies change so that I'm never surprised.

**Acceptance criteria**

- [x] Monthly summary on the last working day
- [x] Significant changes emailed immediately
- [x] Public policy updates page

**Sub-tasks**

- [x] S043-T1 Policy versioning
- [x] S043-T2 Scheduled summary email
- [x] S043-T3 Updates page

### F10.2 Data rights and retention

#### S044  ·  Done  ·  Nov 11

As an account holder, I want to export my data and close my account so that I control my information.

**Acceptance criteria**

- [x] Export includes tickets and notifications
- [x] Closing an account erases personal data

**Sub-tasks**

- [x] S044-T1 Export endpoint
- [x] S044-T2 Erasure flow

#### S045  ·  Done  ·  Nov 11

As the privacy owner, I want retention enforced automatically so that the policy schedule is real.

**Acceptance criteria**

- [x] Daily retention sweep
- [x] Dormant accounts warned 30 days before erasure after 2 years

**Sub-tasks**

- [x] S045-T1 Retention job
- [x] S045-T2 Dormancy warning email

## E11 Quality engineering

**Goal:** Know the product works before anyone else finds out it doesn't.  
**Delivered:** Nov 6 to 11

### F11.1 Test suites

#### S046  ·  Done  ·  Nov 6 to 10

As the product owner, I want an evaluation kit with one report so that release readiness is a fact, not a feeling.

**Acceptance criteria**

- [x] 10 suites, fresh database each
- [x] One report with pass counts and first failures

**Sub-tasks**

- [x] S046-T1 SIT and UAT suite
- [x] S046-T2 Platform and features suites
- [x] S046-T3 Evaluation runner

**Bugs found**

- B11 (Low, Test): Carousel arrow tests failed because the Help button covered it

#### S047  ·  Done  ·  Nov 9 to 10

As a designer, I want every screen checked at 16 sizes so that nothing overflows on any device.

**Acceptance criteria**

- [x] 320 to 2560 px
- [x] Every element measured; tap targets at least 44 px

**Sub-tasks**

- [x] S047-T1 Responsive suite
- [x] S047-T2 Smoke mode for quick checks

**Bugs found**

- B13 (Medium, UI): Tablet navigation wrapped to two lines; portal tabs and hero card overflowed; small tap targets

#### S048  ·  Done  ·  Nov 10 to 11

As the product owner, I want quick checks for small changes so that testing effort matches risk.

**Acceptance criteria**

- [x] Changed files map to affected suites
- [x] Full tier once per deploy batch

**Sub-tasks**

- [x] S048-T1 Diff-to-suite map
- [x] S048-T2 Local test server script

**Bugs found**

- B32 (Medium, Process): An unscoped audit fanned out to 13 agents and exhausted the usage limit

## E12 Security

**Goal:** Find and fix weaknesses before attackers do.  
**Delivered:** Nov 6 to 11

### F12.1 Hardening

#### S049  ·  Done  ·  Nov 6

As the product owner, I want a penetration test of the public site so that launch risks are closed.

**Acceptance criteria**

- [x] Strict CSP without inline scripts
- [x] No config files served
- [x] Input limits everywhere

**Sub-tasks**

- [x] S049-T1 Pen test suite
- [x] S049-T2 Header policy
- [x] S049-T3 security.txt

**Bugs found**

- B03 (Medium, Security): Inline scripts forced a weak Content Security Policy
- B04 (Medium, Security): Build config files were publicly downloadable

#### S050  ·  Done  ·  Nov 11

As the product owner, I want scoped security audits of the platform so that every confirmed finding is fixed and tested.

**Acceptance criteria**

- [x] No critical or high findings
- [x] Each fix has a regression test

**Sub-tasks**

- [x] S050-T1 Audit runs 1 and 2
- [x] S050-T2 Rate limits and upload checks
- [x] S050-T3 Dependency upgrade with lockfile

**Bugs found**

- B30 (Low, Security): Build dependency had known vulnerabilities

## E13 Performance

**Goal:** Fast on a mid-range phone, cheap to serve.  
**Delivered:** Nov 10 to 11

### F13.1 Speed

#### S051  ·  Done  ·  Nov 10 to 11

As a learner on a phone, I want pages and the portal to load quickly so that I don't give up.

**Acceptance criteria**

- [x] Lighthouse Accessibility 100 on key pages
- [x] Home blocking time under 500 ms
- [x] No layout shift on sign in

**Sub-tasks**

- [x] S051-T1 Static routing so assets skip server code
- [x] S051-T2 Edge cache for public reads
- [x] S051-T3 Portal split into modules
- [x] S051-T4 Skeleton screens
- [x] S051-T5 Smaller icons

**Bugs found**

- B26 (Medium, Performance): Home page blocked the main thread for over 1 second
- B27 (Medium, Performance): Sign in page jumped on phones
- B28 (Medium, Accessibility): Accessibility score 96: duplicate image labels and crowded footer links

## E14 Productisation: zero-to-live

**Goal:** Turn the build's methods into a reusable, citable open-source Claude skill.  
**Delivered:** Nov 11

### F14.1 Skill and repository

#### S052  ·  Done  ·  Nov 11

As a developer, I want the workflow, guides and scripts as an installable Claude skill so that I can reuse them on my own project.

**Acceptance criteria**

- [x] Short SKILL.md, guides in references/, tools in scripts/
- [x] Every script proven on a sample project
- [x] Nothing project-specific or sensitive

**Sub-tasks**

- [x] S052-T1 Extract and generalise
- [x] S052-T2 Scrub sensitive content
- [x] S052-T3 Test scripts
- [x] S052-T4 Human review before publishing

#### S053  ·  Done  ·  Nov 11

As a researcher or developer, I want a citation file so that I can credit the work correctly.

**Acceptance criteria**

- [x] GitHub shows Cite this repository
- [x] APA and BibTeX in the README

**Sub-tasks**

- [x] S053-T1 CITATION.cff
- [x] S053-T2 Copyright header in each script

#### S054  ·  Done  ·  Nov 11

As a product leader, I want the project management view in the repo so that I can see how the product was planned and delivered.

**Acceptance criteria**

- [x] Epics, features, stories, sub-tasks and bugs
- [x] Jira-importable CSV

**Sub-tasks**

- [x] S054-T1 Reconstruct backlog from history
- [x] S054-T2 Publish under project/
