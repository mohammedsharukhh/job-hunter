---
name: tailor-resume
description: Builds an ATS-friendly resume (and optional cover letter) tailored to one specific job description, using only facts from the user's master profile, and reports keyword coverage. Use when the user says "tailor my resume", "make a resume for this JD", "customize resume for <company>", pastes a job description, or as a step of /job-hunter:job-hunt.
---

# Tailor Resume to a Job Description

## Inputs
- JD: a pasted description, a URL, or `job-hunt/applications/<job>/jd.md`.
- `job-hunt/profile.md` (master facts) and `job-hunt/preferences.yaml`.

## The golden rule
**Never invent.** Every claim, number, tool, title and date in the tailored resume must exist in `profile.md`. You may reword, reorder, merge, emphasise and cut. If the JD asks for something the user lacks, list it under "Gaps" for the user — do not add it. If a stronger number is plausible but unknown, ask the user.

## Steps
1. **Parse the JD** into: job title, must-have skills, nice-to-have skills, responsibilities, seniority, domain words, soft skills. Extract the 15–25 most important keywords/phrases exactly as the JD writes them (e.g. "SwiftUI", "CI/CD", "RESTful APIs").
2. **Map evidence.** For each keyword, find matching evidence in `profile.md`. Build a table: keyword → evidence line → covered / partial / missing.
3. **Write the resume** following `references/ats-rules.md`:
   - Headline mirroring the JD title (only if truthful).
   - 3–4 line summary using the top must-haves the user truly has.
   - Skills section ordered by JD priority, using the JD's spelling.
   - Experience bullets re-ordered so the most relevant come first; rewrite each as *action verb + what + tech + measurable result*, weaving in JD keywords naturally.
   - Projects chosen for relevance to this JD.
   - Fit on `resume.max_pages` (default 1 page for < 5 yrs experience).
4. **Save** as `job-hunt/applications/<job>/resume.md` using the exact Markdown structure in `references/ats-rules.md`, then render:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_resume.py job-hunt/applications/<job>/resume.md --pdf`
   (produces `resume.docx`, and `resume.pdf` when LibreOffice is available).
5. **Cover letter (if the application asks or the user wants one):** 3 short paragraphs — why this company (one specific, verifiable detail from their site/JD), the 2–3 strongest matching achievements, a clear close. Save to `cover-letter.md`. Same no-invention rule.
6. **Report** to the user: keyword coverage % (covered ÷ total), the table of missing keywords (gaps), and anything you need confirmed. Update tracker status to `tailored`:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py update --dir job-hunt --id <id> --status tailored`

## Quality check before finishing
- Open the rendered DOCX/PDF text (e.g. `pandoc resume.docx -t plain`) and confirm it reads cleanly, top to bottom, with no broken sections.
- Re-scan every bullet against `profile.md` — delete anything you cannot trace.
