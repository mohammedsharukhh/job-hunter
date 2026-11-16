---
name: hr-outreach
description: Finds the official, publicly listed recruiting contact for a job (careers email in the posting or on the company site, or the hiring manager on LinkedIn) and drafts a short personalised application or referral email with the tailored resume attached, sending only after the user approves. Use when the user says "email the HR", "send my resume to <company>", "reach out to recruiters", "follow up on my application", or when a job's apply method is email.
---

# HR / Recruiter Outreach

## Finding the right contact (in this order)
1. An email address written in the job posting itself.
2. The company's official careers / jobs / "work with us" page (e.g. careers@, jobs@, hr@ shown on their own domain).
3. A recruiter or hiring manager who posted the job on LinkedIn — draft a LinkedIn message for the user to send instead of guessing their email.

**Do not** guess or pattern-generate personal email addresses (firstname.lastname@…), scrape personal contact data from third-party lead databases, or bulk-email lists. Unsolicited bulk mail gets the user's address flagged as spam and can break anti-spam law. One relevant, personalised message beats fifty generic ones.

Record the contact and where it was found in `job-hunt/applications/<job>/contact.md`.

## Drafting
Use `references/email-templates.md`. Every email must:
- Have a specific subject: `Application: <Exact Job Title> — <Full Name>` (or the reference/job ID the posting asks for).
- Be ≤ 150 words, mention the exact role, 2 concrete matching achievements from `profile.md`, and one genuine detail about the company.
- Attach the tailored `resume.pdf` for that job (never a generic one).
- End with name, phone, LinkedIn.

## Sending (approval required)
1. Create the email as a **draft** in the user's connected email (e.g. the Gmail connector's create-draft tool). If no email connector is connected, search the connector registry and suggest one; otherwise give the text to copy.
2. Show the user all drafts for the batch: recipient, subject, body, attachment.
3. Send only the ones the user explicitly approves. Respect `outreach.daily_email_limit` — count today's sends in the tracker and stop at the cap.
4. Update tracker: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py update --dir job-hunt --id <id> --status emailed --contact "<email>"`

## Follow-ups
- One polite follow-up after `follow_up_after_days` with no reply, as a reply in the same thread. Max `max_follow_ups`. Never more.
- If anyone replies "not interested", "unsubscribe" or similar, mark the job `closed` and never email that contact again.
