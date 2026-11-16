# How job-hunter is built

job-hunter is a standard Claude plugin: **skills** (Markdown instructions Claude follows), **Python helper scripts** (deterministic work: tracking, rendering, testing), and one **hook** (auto-start).

```
job-hunter/
├── .claude-plugin/
│   ├── plugin.json          # plugin manifest (name, version)
│   └── marketplace.json     # lets people install from this repo
├── hooks/hooks.json         # SessionStart → scripts/session_start.py (auto-start)
├── skills/<name>/SKILL.md   # 18 skills (see docs/SKILLS.md)
├── scripts/
│   ├── tracker.py           # application tracker (CSV): add/update/list/due/mark-run
│   ├── watch_jobs.py        # hourly watchlist via public ATS job APIs
│   ├── render_resume.py     # resume.md → DOCX/PDF (classic | modern | compact)
│   ├── ats_check.py         # ATS self-test: reads the PDF back like hiring software
│   ├── fact_check.py        # blocks facts not in profile.md (+ known_terms.txt)
│   ├── insights.py          # what gets replies (source, template, fit band)
│   ├── dashboard.py         # self-contained HTML dashboard
│   ├── share_stats.py       # anonymous opt-in stats
│   ├── aggregate_stats.py   # maintainers: builds docs/RESULTS.md
│   └── session_start.py     # auto-start hook
├── templates/               # profile, preferences, region packs (india, gulf, eu_uk, us)
├── examples/                # sample resume + example profiles for 4 professions
├── evals/                   # quality test cases + golden resumes
├── tests/                   # unit tests
└── docs/                    # guides, website (GitHub Pages), demo video
```

## The user's workspace (`~/job-hunt/`)
```
profile.md         master resume — the only source of truth for facts
preferences.yaml   roles, locations, limits, sending mode, automation times
watchlist.txt      companies for the hourly watchlist (e.g. greenhouse:airbnb)
tracker.csv        one row per job
applications/<company-role>/   jd.md, resume.md, PDF/DOCX, cover letter, contact, prep notes
dashboard.html, insights.json, learning-log.md
```

## Daily flow
`session_start.py` (or a scheduled task) → **job-hunt** skill → check-updates → job-watchlist + find-jobs → tailor-resume (ATS ≥ 85 + fact check) → apply-to-job / hr-outreach drafts → **one approval table** → send one by one → dashboard → `tracker.py mark-run`.

## Design rules (keep them in forks)
1. Facts come only from `profile.md`.
2. Nothing is submitted or sent outside the list the user approved; one at a time; daily caps.
3. Official contacts only; no scraping of personal data; human-paced browsing.
4. Deterministic checks in scripts, judgement in skills.
