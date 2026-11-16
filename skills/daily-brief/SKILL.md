---
name: daily-brief
description: Sends a short morning job-search summary — new matches waiting for approval, interviews and test deadlines, replies received, follow-ups due — and can schedule itself every weekday. Use when the user says "job brief", "morning summary", "what's on for my job hunt today", or "send me a daily update".
---

# Daily Job Brief

## Build the brief
1. Run **check-updates** (inbox) quietly.
2. Gather: `tracker.py list --status found` (new matches awaiting approval), `tracker.py due` (follow-ups), jobs in `assessment`/`interview`/`offer`, and calendar events titled with interview/company names if a calendar is connected.
3. Write ≤ 8 lines, most urgent first:
   ```
   🔴 Today: Interview — Acme iOS Developer, 3:00 PM (prep ready)
   🟡 Test due Thu: Beta Corp HackerRank
   📬 2 replies: Gamma (rejected), Delta (asked for portfolio — draft ready)
   🆕 5 new matches ready to approve (best: Epsilon, fit 91)
   ↩️ 3 follow-ups due
   📈 This week: 9 applied · 22% response rate
   ```
4. End with one suggested action ("Approve today's 5 applications?").

## Delivery
- Interactive: reply in chat.
- Scheduled: send via push notification / the session's message tool; if the user asked for email, draft-to-self via the email connector.

## Scheduling
When the user asks for it daily, create a scheduled task (weekdays, the time they choose, in their timezone) whose prompt is: "Run the job-hunter daily-brief skill on my job-hunt folder; prepare but do not send or submit anything." Confirm the time and how to pause it.
