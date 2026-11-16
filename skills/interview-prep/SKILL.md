---
name: interview-prep
description: Prepares the user for a specific interview — company research brief, likely questions from the job description (behavioural, technical, DSA, role-specific), STAR answers built from the user's real experience, and a live mock interview with scored feedback. Use when the user says "prep me for my interview", "mock interview", "I have an interview with <company>", "practice DSA/Swift questions", or when check-updates finds an interview invite.
---

# Interview Prep

## Inputs
- The job folder `job-hunt/applications/<job>/` (jd.md, tailored resume.md) — or a pasted JD/company name.
- `job-hunt/profile.md` for the user's real stories.
- Interview details if known: round (HR / technical / system design / managerial), format, duration, interviewer names.

## 1. Company brief (save to `interview-prep.md` in the job folder)
Research with WebSearch/WebFetch (recent, verifiable facts only; cite links):
- What they do, products/apps, customers, size, funding/revenue if public, recent news (last 6 months).
- Tech stack signals (job posts, engineering blog, App Store apps → ratings, recent reviews and complaints the user could speak to).
- Interview process reports (Glassdoor/AmbitionBox/LeetCode discuss) — summarise patterns, don't copy text.
- 3 smart questions the user can ask the interviewer.

## 2. Question bank
Build 20–30 likely questions, grouped:
- **HR / behavioural** (tell me about yourself, why us, conflict, failure, notice period, salary).
- **Role-technical** from the JD's must-haves. For iOS roles use `references/ios-question-bank.md`; for other roles derive from the JD.
- **DSA / problem solving** (if the role or company typically tests it): 5 problems matched to level, each with the pattern (two pointers, sliding window, BFS…), hint, and optimal complexity.
- **Resume deep-dive**: 1–2 probing questions per project/bullet on the tailored resume — interviewers ask about what's written.

## 3. Answers from real experience
For behavioural/resume questions draft STAR answers (Situation, Task, Action, Result) using only facts from `profile.md`. Mark any missing detail as a question to the user. Keep "Tell me about yourself" to ~60–90 seconds.

## 4. Mock interview (interactive)
Offer a mock round. Ask one question at a time, wait for the user's answer, then give:
- Score 1–5 on structure, specificity (numbers), relevance, and communication.
- One concrete fix and a tightened model answer using their facts.
For coding questions: let the user think aloud / write code; review correctness, complexity, edge cases, and Swift style (or the relevant language). Don't reveal the full solution until they ask or have tried.

End with: top 3 strengths, top 3 things to practise, and a 1-page cheat sheet (key stories, numbers, questions to ask) appended to `interview-prep.md`.

## After the interview
Draft the thank-you email (hr-outreach template 5) and update the tracker note with the round and how it went.
