# zero-to-live

A Claude skill for taking a website or web app from idea to production: plan, build, test in tiers, secure, and deploy in batches. Stack-neutral, with Cloudflare Pages, D1 and R2 as the preferred path.

## What it covers

- **Planning:** a one-page plan, static vs dynamic per page, phased delivery
- **Building:** static-first pages, one shared layout, strict CSP-friendly front end, SEO and AI-crawler files
- **Testing tiers:** quick checks mapped to the files you changed, and a full suite once per deploy batch
- **Accessibility and performance:** Lighthouse targets as release gates, checklists, common fixes
- **Security:** a checklist covering API design, object-level authorization, sessions, MFA, headers, uploads, rate limits, secrets and privacy by design
- **Batched deploys:** a build budget, a test gate on the exact commit, and a rollback plan

## Layout

```
zero-to-live/
├── SKILL.md                         workflow and key rules (loaded first)
├── references/                      detailed guides (loaded when needed)
│   ├── planning.md
│   ├── building.md
│   ├── stack-cloudflare.md
│   ├── alternatives.md
│   ├── testing.md
│   ├── accessibility-performance.md
│   ├── security.md
│   └── deploys.md
├── scripts/                         reusable, project-agnostic tools
│   ├── quick_check.py               run only the checks affected by your diff
│   ├── compliance_check.py          secrets, CSP, headers, SQL safety, privacy drift
│   ├── run_suite.py                 full tier with one report
│   ├── serve_local.sh               local Pages server with D1 and R2
│   ├── lighthouse.sh                Lighthouse with pass/fail thresholds
│   ├── make_routes.py               Cloudflare _routes.json for static files
│   └── deploy_batch.sh              batch counter, build budget, test gate
├── templates/
│   ├── checks.json                  test map and suite config
│   ├── _headers                     security headers starting point
│   └── gitignore
└── project/                         project management view of the case study
    ├── README.md                    timeline, hierarchy, how to import
    ├── BACKLOG.md                   14 epics, 54 stories, 144 sub-tasks
    ├── BUGS.md                      32 bugs with root cause and prevention
    └── backlog.csv                  Jira-importable backlog
```

## Install

**Claude Code:** clone into your skills folder.

```bash
git clone https://github.com/ambergargrish-ca/zero-to-live ~/.claude/skills/zero-to-live
```

**Claude apps:** download the repo as a zip and upload it as a custom skill.

## Use in a project

```bash
cp ~/.claude/skills/zero-to-live/templates/checks.json .
cp ~/.claude/skills/zero-to-live/templates/gitignore .gitignore
mkdir -p scripts && cp ~/.claude/skills/zero-to-live/scripts/* scripts/

python3 scripts/quick_check.py --dry-run      # what this change would run
python3 scripts/compliance_check.py           # security and privacy check
python3 scripts/run_suite.py                  # full tier before a deploy batch
bash scripts/deploy_batch.sh status           # pending changes and builds left this month
```

Then ask Claude to "take this site live" or "add sign in to this site" and the skill guides the work.

Requirements: Python 3.10+, Git, Node 18+ for wrangler and Lighthouse. Playwright is recommended for browser suites.

## Case study: Get In Tech

This workflow was built and proven on [Get In Tech](https://getintech.ca), a live AI training and tech careers platform, taken from a static launch site to a full platform with accounts, dashboards, a learning portal, payments and a job board on Cloudflare Pages, D1 and R2.

Along the way it shaped:
- a test map that cut routine checks from a 25-minute full run to the few suites a change can affect
- a compliance check that blocks secrets, inline scripts and unsafe SQL, and flags every privacy-relevant change for review
- Lighthouse Accessibility 100 across key pages, with mobile Performance in the 85 to 100 range
- a security review whose fixed findings became the object-level authorization, session and capacity-abuse items in the checklist
- batched deploys that keep a growing platform well inside the free plan's monthly build limit

For the product view of the build (epics, features, user stories, sub-tasks and every bug with its root cause), see [project/](project/README.md). The CSV imports straight into Jira.

Built by [Amber Gargrish](https://gargrish.com).

## Citing

If this skill, its scripts or its checklists help your project, please credit it. GitHub's **Cite this repository** button (right sidebar) gives APA and BibTeX from [CITATION.cff](CITATION.cff).

**APA**

> Gargrish, A. (2026). *zero-to-live: an end-to-end web development skill for Claude* (Version 1.0.0) [Computer software]. https://github.com/ambergargrish-ca/zero-to-live

**BibTeX**

```bibtex
@software{gargrish_zero_to_live_2026,
  author  = {Gargrish, Amber},
  title   = {zero-to-live: an end-to-end web development skill for Claude},
  year    = {2026},
  version = {1.0.0},
  url     = {https://github.com/ambergargrish-ca/zero-to-live},
  license = {MIT}
}
```

**In a project README or credits page**

```markdown
Built with [zero-to-live](https://github.com/ambergargrish-ca/zero-to-live) by [Amber Gargrish](https://gargrish.com).
```

## License

MIT. See [LICENSE](LICENSE). If you copy or adapt the scripts or guides, keep the copyright notice in LICENSE with them.
