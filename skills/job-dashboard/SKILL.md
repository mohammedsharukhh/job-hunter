---
name: job-dashboard
description: Builds a visual dashboard of the user's job search — funnel, response rate, interviews, offers, applications by source, items needing action and follow-ups due — as a self-contained web page. Use when the user says "show my dashboard", "job search stats", "how is my job hunt going", or at the end of /job-hunter:job-hunt.
---

# Job Dashboard

1. Generate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py --dir job-hunt` → `job-hunt/dashboard.html` (works offline, light/dark mode, filterable table).
2. Deliver it the best way the environment allows:
   - If an artifact/publishing tool is available, publish the page (or use a dashboard artifact type with the tracker rows as data) so the user gets a link that stays updated on each run — republish the same artifact rather than creating new ones.
   - Otherwise send/open the HTML file.
3. Reply with one or two lines: the headline numbers (applied, response rate, interviews) and the single most important action (e.g. "2 follow-ups due, 1 assessment closes Friday").
