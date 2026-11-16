---
name: referral-finder
description: Finds people in the user's own network (LinkedIn connections, alumni, ex-colleagues) who work at a target company and drafts short, personal referral requests for the user to send. Use when the user says "find a referral", "who do I know at <company>", "ask for a referral", or for high-fit jobs during /job-hunter:job-hunt.
---

# Referral Finder

Referrals convert far better than cold applications. Work only from the user's own network and public profiles.

## Steps
1. For each target company (high fit score first), in the user's signed-in browser:
   - LinkedIn: search `<Company>` people filtered by **1st-degree connections**, then **2nd-degree**, then **school** (the user's colleges from `profile.md`), then **past companies**.
   - Note name, role, team, connection degree, any shared context (same college, ex-colleague, same city, mutual connection).
2. Rank candidates: 1st-degree in the same team/function > alumni > 2nd-degree with strong mutual > recruiter at that company.
3. Save to `job-hunt/applications/<job>/referrals.md` (max 3 people per job; public professional info only).
4. Draft one message per person (≤ 80 words for LinkedIn, ≤ 300 characters if it's a connection-request note):
   - Shared context first, the exact role + job link/ID, one line on fit with a number, a clear easy ask ("would you be open to referring me, or pointing me to the right person?"), offer to send the tailored resume.
   - For 2nd-degree: ask the mutual connection for an intro instead of cold-messaging.
5. Present drafts. The user sends LinkedIn messages themselves (or Claude clicks Send in their browser after explicit approval for each message). Never mass-message.
6. Tracker note: `tracker.py update --id <id> --note "referral asked: <name>"`. Suggest one gentle follow-up after 5–7 days, then stop.
