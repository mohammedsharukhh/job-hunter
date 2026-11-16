---
name: job-hunt-setup
description: Sets up the user's job-hunt workspace — master resume profile, job preferences, region pack and application tracker. Use when the user says "set up job hunter", "start my job search", "here is my resume", "update my profile/preferences", or when any other job-hunter skill finds no workspace yet.
---

# Job Hunt Setup

Create (or update) the user's job-hunt workspace. Every other job-hunter skill reads from it.

## Workspace layout

Use a folder named `job-hunt/` in the current working directory (or the folder the user names):

```
job-hunt/
├── profile.md          # master resume: EVERYTHING true about the user (source of truth)
├── preferences.yaml    # target roles, locations, limits, sending mode, resume template
├── tracker.csv         # one row per job (managed by scripts/tracker.py)
├── insights.json       # written by job-insights
├── learning-log.md     # what preferences changed and why
├── dashboard.html      # written by job-dashboard
└── applications/       # one folder per job: jd.md, resume, cover letter, contact, prep notes
```

## Steps
1. **Check for an existing workspace.** If `job-hunt/profile.md` exists, read it and ask only what changed. Run `tracker.py init` anyway — it migrates older trackers to the current columns.
2. **Collect the resume.** Ask the user to attach their current resume (PDF/DOCX) or paste it. Extract everything. Ask for LinkedIn/portfolio/GitHub/App Store links.
3. **Pick region pack(s).** Ask where they're applying: India, Gulf, EU/UK, US (several allowed). Merge the matching `${CLAUDE_PLUGIN_ROOT}/templates/regions/<region>.yaml` into preferences (job boards, resume conventions, salary sources). If they want a starting point, show the closest example in `${CLAUDE_PLUGIN_ROOT}/examples/profiles/` (ios-developer, procurement, mechanical-engineer, data-analyst).
4. **Build `profile.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/profile.example.md`. Master file — include every role, project, metric, skill, certification. Tailored resumes are cut from it; nothing may appear on a tailored resume that isn't here.
5. **Fill gaps with questions, not guesses.** Ask for measurable results (numbers, users, ratings, % improvements). Mark unknowns `TODO`.
6. **Build `preferences.yaml`** from `${CLAUDE_PLUGIN_ROOT}/templates/preferences.example.yaml`. Ask (AskUserQuestion when available, max 4 at a time): target titles, locations / remote, level, notice period, work-authorization notes to state, salary expectation (optional), companies to avoid, daily email limit, email sending mode (approve the day's list once, or review each email), resume template (classic / modern / compact).
7. **Create the tracker:** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py init --dir job-hunt`
8. Offer **job-watchlist** for their top target companies (be among the first applicants), **linkedin-profile** to align LinkedIn with the new profile, and **daily-brief** scheduling.
9. Confirm in two or three lines what was set up and suggest `/job-hunter:job-hunt` as the next step.

## Rules
- Never store passwords, OTPs, government ID numbers or bank details in the workspace.
- `profile.md` is the only source of truth for facts about the user. New facts go here first.
