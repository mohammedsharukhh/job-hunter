---
name: apply-to-job
description: Prepares and submits a job application on a company career portal or job board (LinkedIn Easy Apply, Workday, Greenhouse, Lever, Naukri, etc.) using the tailored resume, filling the form from the user's profile and pausing for the user's approval before the final submit. Use when the user says "apply to this job", "apply for me", "submit my application to <company>", or as a step of /job-hunter:job-hunt.
---

# Apply to a Job

## Preconditions
- A tailored resume exists in `job-hunt/applications/<job>/` (run **tailor-resume** first if not).
- A browser tool is available (Claude in Chrome or the built-in browser). Load its skill first if one is listed.

## Steps
1. Read `jd.md` for the apply URL/method. If the method is *email-only*, hand off to **hr-outreach** with "application" mode instead.
2. Open the apply page in the user's browser, in a new tab.
3. **Sign-in:** if the portal needs an account, ask the user to sign in or create it themselves. Never type passwords, OTPs or solve captchas.
4. **Fill the form** from `profile.md` / `preferences.yaml`:
   - Upload `resume.pdf` (or `.docx` if PDF is rejected) and the cover letter when asked.
   - Standard fields: name, contact, links, experience, education, notice period, location.
   - **Screening questions:** answer only from known facts. For anything not in the profile (salary, relocation, years with a specific tool, sponsorship, legal/diversity questions), STOP and ask the user — never guess. Leave voluntary demographic questions as "prefer not to say" unless the user has said otherwise.
5. **Review gate (mandatory):** before clicking the final Submit/Apply button, show the user a summary — company, role, resume file used, every screening answer — and ask for explicit confirmation ("yes, submit"). Only then submit.
6. Capture confirmation (screenshot or confirmation text/ID) into `job-hunt/applications/<job>/submission.md`.
7. Update the tracker: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py update --dir job-hunt --id <id> --status applied --note "<portal, confirmation id>"`

## Batch mode
When applying to several jobs, fill each up to the review gate, then present all summaries together for one round of approvals. Submit only the approved ones.

## Stop and ask when
- The site shows a captcha, bot warning, or "unusual activity".
- The form asks for payment, ID documents, or bank details (legit employers don't charge to apply — flag it as a possible scam).
- Two attempts fail on the same step.
