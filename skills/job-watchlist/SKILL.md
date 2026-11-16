---
name: job-watchlist
description: Watches a list of target companies' career boards (Greenhouse, Lever, Ashby, Workable, SmartRecruiters) through their public job APIs and alerts the user within the hour when a matching role is posted, so they can apply among the first candidates. Use when the user says "watch these companies", "alert me when <company> posts iOS jobs", "set up a watchlist", "check my watchlist", or "apply early".
---

# Company Watchlist (be among the first applicants)

Early applicants get far more recruiter attention. These ATS vendors publish public, read-only job APIs — no browser, no login, no scraping of personal data.

## 1. Build the watchlist
For each company the user names (or top companies from past high-fit jobs):
1. Find which ATS hosts its careers page and the board slug. Open the careers page or search, e.g. `"<Company>" (site:boards.greenhouse.io OR site:jobs.lever.co OR site:jobs.ashbyhq.com OR site:apply.workable.com OR site:jobs.smartrecruiters.com)`. The slug is the path segment after the domain.
2. Add a line to `job-hunt/watchlist.txt`: `greenhouse:<slug>   <Company Name>`.
3. Companies on Workday, Taleo, SuccessFactors, iCIMS or their own site can't be watched this way — add them to `preferences.yaml → career_pages` for **find-jobs** instead and tell the user.

## 2. Check for new postings
Build filters from `preferences.yaml` (target_titles → short keywords such as `iOS,Swift,Mobile`; locations plus `Remote` if remote is OK; exclude words from seniority, e.g. `Senior,Staff,Principal,Lead` for junior/mid):
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/watch_jobs.py --dir job-hunt \
  --titles "iOS,Swift,Mobile" --locations "Bangalore,Bengaluru,India,Doha,Qatar,Remote" \
  --exclude "Senior,Staff,Principal" --max-age-hours 72 --add
```
- New matches are saved to `applications/<company>-<title>/jd.md` and added to the tracker with source `watchlist:<ats>`.
- The first run only reports postings from the last `--max-age-hours`; everything older is marked as seen.
- **If the script can't reach the network** (sandboxed environment), fetch each URL listed at the top of `scripts/watch_jobs.py` with WebFetch instead, apply the same filters, and add matches with `tracker.py add`.

## 3. Act fast on each new match
For every new match: score fit (as in **find-jobs**), then immediately run **tailor-resume** and prepare the application (**apply-to-job** or **hr-outreach**). Tell the user right away with the posting age ("posted 3h ago") and ask for approval — speed is the point.

## 4. Run it every hour
Offer to create a scheduled task, hourly during the user's waking hours (e.g. 08:00–22:00 in their timezone), with this prompt:
"Run the job-hunter job-watchlist skill on my job-hunt folder. For new matches, tailor resumes and prepare applications, then notify me. Do not submit or send anything until I approve."
Polling hourly with a 1-second gap between companies is polite; don't poll more often than every 30 minutes.
