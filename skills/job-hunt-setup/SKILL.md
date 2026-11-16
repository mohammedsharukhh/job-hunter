---
name: job-hunt-setup
description: Sets up the user's job-hunt workspace — master resume profile, job preferences and application tracker. Use when the user says "set up job hunter", "start my job search", "here is my resume", "update my profile/preferences", or when any other job-hunter skill finds no workspace yet.
---

# Job Hunt Setup

Create (or update) the user's job-hunt workspace. Every other job-hunter skill reads from it.

## Workspace layout

Use a folder named `job-hunt/` in the current working directory (or the folder the user names):

```
job-hunt/
├── profile.md          # master resume: EVERYTHING true about the user (source of truth)
├── preferences.yaml    # target roles, locations, salary, limits, sending rules
├── tracker.csv         # one row per job (managed by scripts/tracker.py)
└── applications/       # one subfolder per job: jd.md, resume.docx/.pdf, cover-letter.md, emails
```

## Steps

1. **Check for an existing workspace.** If `job-hunt/profile.md` exists, read it and ask only what changed.
2. **Collect the resume.** Ask the user to attach their current resume (PDF/DOCX) or paste it. Extract everything. If they also have LinkedIn/portfolio/GitHub links, ask for them.
3. **Build `profile.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/profile.example.md`. This is a *master* file — include every role, project, metric, skill, certification, even ones that won't fit on one page. Tailored resumes are cut from it; nothing may be added to a tailored resume that isn't here.
4. **Fill gaps with questions, not guesses.** For each role, ask for measurable results (numbers, scale, users, % improvements) if missing. Mark unknowns `TODO` rather than inventing them.
5. **Build `preferences.yaml`** from `${CLAUDE_PLUGIN_ROOT}/templates/preferences.example.yaml`. Ask (AskUserQuestion when available, max 4 at a time): target titles, locations / remote, experience level, notice period, visa/work-authorization notes the user wants stated, salary expectation (optional), companies to avoid, daily outreach limit.
6. **Create the tracker:** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py init --dir job-hunt`
7. Confirm in two or three lines what was set up and suggest `/job-hunter:find-jobs` as the next step.

## Rules

- Never store passwords, OTPs, government ID numbers or bank details in the workspace.
- `profile.md` is the only source of truth for facts about the user. If the user tells you a new fact later, add it here first.
