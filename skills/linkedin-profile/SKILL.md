---
name: linkedin-profile
description: Writes a recruiter-optimised LinkedIn headline, About section, experience bullets, skills list and "Open to work" settings from the user's master profile and target roles. Use when the user says "improve my LinkedIn", "write my LinkedIn about", "LinkedIn headline", or "make recruiters find me".
---

# LinkedIn Profile Optimiser

1. Read `profile.md`, `preferences.yaml` (target titles, locations) and, if available, insights from recent JDs (most frequent keywords).
2. Produce:
   - **Headline** (≤ 220 chars): target title + 3–4 top keywords + proof point. Give 3 options.
   - **About** (180–300 words, first person, first 2 lines must hook — they show before "see more"): who you are, what you build, 2–3 quantified wins, tech keywords naturally, what you're looking for, contact line.
   - **Experience**: 3–5 bullets per role, same facts as the master profile, slightly more conversational than the resume.
   - **Skills**: top 50 ordered by target-JD frequency; pin the top 3.
   - **Featured**: suggest App Store links, GitHub repos, demo videos.
   - **Open to work**: titles, locations, start date, recruiter-only visibility suggestion.
   - **Custom URL** suggestion.
3. Same no-invention rule as resumes.
4. Save to `job-hunt/linkedin.md`. If the user wants, apply edits in their signed-in browser section by section, showing each change and saving only after they approve it.
