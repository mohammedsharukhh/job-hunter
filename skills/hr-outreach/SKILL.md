---
name: hr-outreach
description: Finds the official, publicly listed recruiting contact for each job (careers email in the posting or on the company site, or the recruiter/hiring manager on LinkedIn) and sends a personalised application email with that job's tailored resume — one email at a time, after the user approves the day's list. Use when the user says "email the HR", "send my resume to <company>", "reach out to recruiters", "follow up on my application", or when a job's apply method is email.
---

# HR / Recruiter Outreach

## Finding the right contact (in this order)
1. An email address written in the job posting itself.
2. The company's official careers / jobs / contact page on its own domain (careers@, jobs@, hr@, recruitment@…).
3. A recruiter or hiring manager who posted the job on LinkedIn → draft a LinkedIn message (see **referral-finder** for the style) rather than guessing an email.

**Do not** guess or pattern-generate personal addresses (firstname.lastname@…), pull contacts from third-party lead/scraping databases, or email anyone who isn't connected to a real opening. Record the contact and the URL where it was found in `job-hunt/applications/<job>/contact.md`.

## Drafting
Use `references/email-templates.md`. Every email:
- Subject: `Application: <Exact Job Title> — <Full Name>` (plus the job/reference ID if the posting gives one).
- ≤ 150 words: the exact role, 2 concrete matching achievements from `profile.md`, one genuine detail about the company, notice period.
- Attaches that job's tailored `resume.pdf` (never a generic one).
- Signature: name, phone, LinkedIn.
- Tag which template was used (for job-insights): `--email-template t1` etc.

## Sending modes (`preferences.yaml → outreach.mode`)
**`approve_list` (default)** — the user approves the day's list once, then Claude sends them one by one:
1. Prepare all drafts (in the email connector as drafts, e.g. Gmail create-draft).
2. Show one compact table: #, company, role, recipient, where the address was found, subject, first line. The user can open any draft, edit, or untick items.
3. After the user approves the list, send **one email at a time** in the approved order, waiting `outreach.send_gap_minutes` (default 3) between sends. After each send, update the tracker immediately:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py update --dir job-hunt --id <id> --status emailed --contact "<email>" --email-template <t>`
4. Stop when `outreach.daily_email_limit` is reached (check `tracker.py sent-today`), on any bounce/error, or if the user says stop. Report what was sent.

**`review_each`** — show and confirm each email individually before sending it.

If no email connector is connected, search the connector registry and suggest one; otherwise give the text to copy.

Never send anything the user hasn't seen in the approved list, and never add new recipients after approval without asking again.

## Follow-ups
- One polite follow-up after `follow_up_after_days` with no reply, as a reply in the same thread (`tracker.py due` lists them). Follow-ups go through the same approve-list step. Max `max_follow_ups`.
- If anyone replies "not interested", "unsubscribe", "please don't contact", mark the job `closed` and never email that address again.
- Watch for bounces: mark the contact invalid in `contact.md` and don't retry it.
