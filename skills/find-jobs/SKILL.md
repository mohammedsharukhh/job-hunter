---
name: find-jobs
description: Searches job boards and company career portals for openings that match the user's profile and preferences, filters out duplicates and stale "ghost" listings, scores each for fit (learning from jobs the user rejected), and adds the good ones to the tracker. Use when the user says "find jobs", "search for iOS jobs in Bangalore", "check career portals", "any new openings?", or as a step of /job-hunter:job-hunt.
---

# Find Jobs

## Inputs
- `job-hunt/profile.md`, `job-hunt/preferences.yaml` (run **job-hunt-setup** first if missing).
- `job-hunt/insights.json` and `learning-log.md` if present (learned preferences).
- Optional arguments: role, location, company, or a career-page URL.

## Where to search (in this order)
1. **Job-board connector** (e.g. Indeed) if connected — use its search and job-details tools.
2. **Company career pages** in `preferences.yaml → career_pages` and any the user names (browser, or WebFetch for public static pages).
3. **Job boards via the user's signed-in browser** per `sources` and the region pack (`templates/regions/<region>.yaml` lists the main boards per country).
4. **WebSearch** for ATS-hosted postings, e.g. `"iOS Developer" Bangalore (site:greenhouse.io OR site:lever.co OR site:myworkdayjobs.com OR site:smartrecruiters.com)`.

Read at a human pace, don't bypass captchas/logins, stop if a site blocks automation.

## Filter
For each posting:
1. **Duplicates** — `tracker.py add` reports `DUPLICATE` for the same URL or same company + near-identical title (also catches the same job reposted on several boards). Keep the version with the direct company/ATS apply link.
2. **Ghost / stale jobs** — skip or flag when: posted > 30 days ago (`max_posting_age_days`), "reposted" repeatedly, applicant count very high with no recent activity, no company name ("confidential client") with vague JD, the company careers page no longer lists it, or the apply link is dead.
3. **Scam signals** — fees, Telegram/WhatsApp-only contact, free-mail "HR" for a large company, unrealistic pay → skip and mention.
4. **Preferences** — `avoid_companies`, `exclude_keywords`, seniority, location/remote.

## Score fit 0–100
Required skills matched (50), experience-level match (20), location/remote (15), nice-to-haves (15). Then apply **learned adjustments**: −15 if the posting matches a skip reason the user has given ≥ 2 times (see `tracker.py list --status skipped --json` → `skip_reason`), +5 for sources that insights show get replies. Note the top 3 gaps.

## Save
If score ≥ `min_fit_score`:
- Save JD to `job-hunt/applications/<company>-<title-slug>/jd.md` with source URL, posting date, apply URL/method (portal / email / easy-apply), and any listed contact email.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py add --dir job-hunt --company "<c>" --title "<t>" --url "<u>" --location "<l>" --score <n> --source "<s>" --posted <YYYY-MM-DD>`

## Output
Table: company, title, location, posted, fit, top gap, apply method. Ask which to pursue (default: all above threshold, best first). When the user rejects one, ask for a 2–5 word reason and record it:
`tracker.py update --dir job-hunt --id <id> --status skipped --reason "<reason>"` — this is how scoring learns.

Never apply or contact anyone in this skill.
