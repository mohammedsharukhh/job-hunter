# job-hunter 🎯 — an open-source job-search copilot for Claude

A Claude plugin (works in Claude Code and the Claude desktop app) that turns your job hunt into one daily review:

| Skill | What it does |
|---|---|
| `job-hunt-setup` | Builds your **master profile** from your resume, your preferences, and an application tracker |
| `find-jobs` | Searches job-board connectors (e.g. Indeed), LinkedIn/Naukri/Bayt via your browser, and company **career portals**; scores each job's fit |
| `tailor-resume` | Writes an **ATS-friendly resume tailored to each job description**, with a keyword-coverage report — using only true facts from your profile — and exports DOCX/PDF |
| `apply-to-job` | Fills the application on the career portal with your tailored resume, **stops for your approval** before Submit |
| `hr-outreach` | Finds the **official** recruiting contact (from the posting or company careers page) and drafts a personalised email with the resume attached; sends only what you approve, with a daily cap |
| `check-updates` | Reads your inbox for confirmations, tests, interview invites, rejections and offers; updates the tracker and drafts replies |
| `job-hunt` | Runs the whole loop: updates → find → tailor → prepare → **one approval round** → submit/send |

## Install

**Claude Code**
```bash
/plugin marketplace add <your-github-username>/job-hunter
/plugin install job-hunter@job-hunter-marketplace
```

**Claude desktop app** — download the `.plugin` file from Releases (or zip this repo) and add it under Customize → Plugins.

Then say: **"set up job hunter"** and attach your resume.

### Optional connections (recommended)
- **Email** (Gmail / Outlook connector) — drafts, sending, reply tracking
- **Calendar** — interview scheduling
- **Job board** (e.g. Indeed connector) — structured job search
- **Browser** (Claude in Chrome) — career portals and job-board applications, using your own signed-in session

Dependencies for the scripts: Python 3.9+, `pip install python-docx`; LibreOffice for PDF export (optional).

## Daily use
```
run my job hunt — iOS roles in Bangalore and Doha, top 5
tailor my resume for this JD: <paste>
check my job emails
```
Schedule it: *"run my job hunt every weekday at 9am"* — scheduled runs prepare everything and wait for your approval.

## Your data
Everything lives in a local `job-hunt/` folder (profile, preferences, tracker.csv, one folder per application). It's in `.gitignore` — never commit it.

## Guardrails (by design, please keep them in forks)
- **No fabrication** — tailored resumes only reword/reorder facts in your master profile; gaps are reported, not invented.
- **Human approval** before every submission and every email.
- **No spam** — official contacts only, no guessed/scraped personal emails, daily send cap, one follow-up max, honours "not interested".
- **No credentials** — Claude never types passwords/OTPs, solves captchas, or handles ID/bank details.
- **Respects site terms** — human-paced browsing, stops at bot checks. Some sites forbid automation; you are responsible for using it within their terms.
- **Scam flags** — fees to apply, ID/bank requests before an offer, etc.

## Contributing
PRs welcome: new job-board guides, regional templates (Gulf, India, EU, US), better ATS rules, more resume layouts. See `CONTRIBUTING.md`.

## License
MIT
