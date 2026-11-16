---
name: find-jobs
description: Searches job boards and company career portals for openings that match the user's profile and preferences, scores each for fit, and adds the good ones to the tracker. Use when the user says "find jobs", "search for iOS jobs in Bangalore", "check career portals", "any new openings?", or as step one of /job-hunter:job-hunt.
---

# Find Jobs

## Inputs
- `job-hunt/profile.md` and `job-hunt/preferences.yaml` (run **job-hunt-setup** first if missing).
- Optional arguments: a role, a location, a company, or a career-page URL.

## Where to search (in this order)
1. **Job-board connector** (e.g. the Indeed connector) if one is connected — use its search and job-details tools.
2. **Company career pages** listed in `preferences.yaml` → `career_pages`, and any the user names. Open them in the browser (Claude in Chrome / built-in browser) or with WebFetch when the page is public and renders without JS.
3. **Job boards via browser** (LinkedIn Jobs, Naukri, Bayt, GulfTalent, Wellfound, etc.) per `sources`. Use the user's own signed-in browser session; never ask for or type passwords.
4. **WebSearch** queries like `"iOS Developer" careers Bangalore site:greenhouse.io OR site:lever.co OR site:myworkdayjobs.com` to find ATS-hosted postings.

Respect each site's terms: read pages at a human pace, do not bypass captchas or logins, and stop if a site blocks automated access.

## For each posting found
1. Skip if already in the tracker (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py list --dir job-hunt`), company is in `avoid_companies`, or it contains `exclude_keywords`.
2. Save the full JD text to `job-hunt/applications/<company>-<title-slug>/jd.md` with the source URL, posting date and apply URL/method at the top.
3. **Score fit 0–100**: required skills matched (50), experience level match (20), location/remote match (15), nice-to-haves matched (15). Note the top 3 gaps.
4. If score ≥ `min_fit_score`, add it:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py add --dir job-hunt --company "<c>" --title "<t>" --url "<u>" --location "<l>" --score <n> --source "<s>"`

## Output
A short table: company, title, location, fit score, top gap, apply method (portal / email / easy-apply). Then ask which ones to tailor and apply to (default: all above threshold, best first).

Never apply or contact anyone in this skill — it only discovers and records.
