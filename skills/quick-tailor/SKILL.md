---
name: quick-tailor
description: Zero-setup resume tailoring — the user pastes or attaches a resume and a job description and gets back an ATS-friendly resume tailored to that job, a keyword match score, honest gaps, and an optional cover letter, with no profile, tracker or connectors needed. Use when the user says "tailor my resume to this job", "make my resume match this JD", "ATS-optimise my resume", "resume for this job posting", or shares a resume and a job description together.
---

# Quick Tailor (no setup)

Works on its own — no workspace, no connectors. If the full job-hunter plugin is set up (`job-hunt/profile.md` exists), prefer **tailor-resume** instead.

## 1. Get the two inputs
- **Resume:** attached file (PDF/DOCX) or pasted text. Read it completely.
- **Job description:** pasted text or a URL (fetch it). If either is missing, ask for it — one short question.

## 2. Analyse the JD
Extract 15–25 keywords/phrases exactly as written (tools, frameworks, methods, domain words, certifications), split into **must-have** and **nice-to-have**, plus the job title and seniority.

## 3. Map evidence — the golden rule
For each keyword, find proof in the resume: covered / partial / missing. **Never invent** experience, tools, numbers, employers, titles, dates or certifications. You may reword, reorder, merge, emphasise and cut. If the JD wants something the resume doesn't show, it's a gap — ask the user if they actually have it; only add it if they confirm.

## 4. Write the tailored resume
- Single column, standard headings (Summary, Skills, Experience, Projects, Education, Certifications), no tables, icons, photos, text boxes or skill bars.
- Headline mirroring the JD title only if truthful; 3–4 line summary built from the strongest true matches.
- Skills ordered by JD priority, using the JD's exact spelling ("SwiftUI", "Power BI").
- Bullets: action verb + what + tool + measurable result; most relevant first; JD keywords woven in naturally, no stuffing.
- One page under ~5 years of experience, otherwise two max. Dates as `Mon YYYY – Mon YYYY`.

## 5. Deliver
- Give the resume as a downloadable document. If the job-hunter plugin scripts are available, write the Markdown structure from `tailor-resume/references/ats-rules.md` and run `render_resume.py` then `ats_check.py` and `fact_check.py`; otherwise create a DOCX/PDF with the available document tools using the rules above. File name: `First_Last_<Role>_Resume`.
- Then a short report:
  - **Match score:** covered must-haves ÷ total must-haves (and overall), before → after.
  - **Changes made:** 3–5 bullets.
  - **Honest gaps:** missing keywords and a one-line idea for closing each (a course, a small project).
  - **Questions:** any facts you need confirmed to strengthen bullets (numbers, scale).
- Offer a 3-paragraph cover letter (same no-invention rule) and, if they're job hunting seriously, mention the full job-hunter plugin (job search, applications, tracking).

## Self-check before sending
Re-read every line of the new resume against the original: anything you can't point to in the original (or in what the user told you) must go.
