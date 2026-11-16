# FAQ & troubleshooting

## The basics

**Is it free?**
Yes. job-hunter is open source (MIT). You need your own Claude subscription.

**Will it apply to jobs without asking me?**
No. It prepares everything and shows you one table a day. Only what you approve gets submitted or emailed — one at a time, within your daily limit.

**Do I have to type a command every day?**
No. After "set up job hunter" it runs by itself: a daily run, an hourly watchlist and a morning brief. When you open Claude it also starts today's run if it hasn't happened yet. Say "pause job hunter" to stop.

**Will it make things up to get past filters?**
Never. Every resume is fact-checked against your own profile. Skills you don't have are listed as gaps with ideas to learn them — not added to your resume.

**Where is my data?**
In a `job-hunt` folder in your home directory on your own computer. Nothing is uploaded or shared unless you choose "share my stats" (anonymous counts only).

**Can it get my LinkedIn account banned?**
LinkedIn doesn't allow automation of its site. job-hunter reads LinkedIn at a human pace in your own browser and leaves the final click to you. For speed it uses the public job feeds companies publish (the watchlist) instead.

**Which countries does it support?**
Any. It has ready-made settings for India, the Gulf, EU/UK and the US (job sites, resume style, salary sources).

**Which jobs does it work for?**
Any profession. Examples are included for iOS developers, procurement, mechanical engineers and data analysts.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "set up job hunter" does nothing | Check the plugin is installed and enabled (Customize → Plugins in the app, or `/plugin` in Claude Code). Start a new chat. |
| It doesn't start automatically | Make sure setup finished (there's a `job-hunt` folder in your home folder). If you moved it, set the `JOB_HUNT_DIR` environment variable. Check `automation.auto_start: true` in `preferences.yaml`. |
| No emails are sent | Connect Gmail/Outlook under Settings → Connectors. Without it, Claude gives you drafts to copy. |
| Can't fill in a career portal | Install Claude in Chrome and sign in to the portal yourself first. Claude never types passwords or solves captchas. |
| Resume PDF not created | Install LibreOffice (free) for PDF export; the Word file is always created. |
| `python3` / `python-docx` errors | Install Python 3.9+, then run `pip install python-docx pypdf`. |
| Watchlist finds nothing | Check the company slug in `job-hunt/watchlist.txt` (e.g. `greenhouse:airbnb`) and that your title/location keywords aren't too narrow. |
| Too many / too few jobs | Change `min_fit_score` and `daily_new_jobs` in `job-hunt/preferences.yaml`, or just tell Claude "only show me jobs above 85". |
| Want to stop everything | Say "pause job hunter". |

Still stuck? [Open an issue](https://github.com/<owner>/job-hunter/issues/new/choose) — include what you said and what happened (remove personal details).
