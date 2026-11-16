---
name: skill-gap-coach
description: Finds the skills the user is repeatedly missing across the jobs they target and builds a short learning plan with portfolio projects to close each gap. Use when the user says "what skills am I missing", "skill gap", "how do I become a stronger candidate", "learning plan", or weekly as part of job-insights.
---

# Skill-Gap Coach

## Steps
1. Read every `job-hunt/applications/*/jd.md` (and gap lists in tailored-resume reports if saved). If fewer than 5 JDs exist, run **find-jobs** in discovery mode first or ask the user to paste a few target JDs.
2. Extract must-have and nice-to-have skills from each JD. Normalise synonyms (e.g. "Swift UI" → SwiftUI, "CI CD" → CI/CD).
3. Compare with `profile.md`. For each skill compute: % of JDs requiring it, whether the user has it (yes / partial / no).
4. Rank gaps by `frequency × importance` (must-have counts double). Show the top 5–8 in a table.
5. For each top gap, propose:
   - **Learn**: 1–2 high-quality free resources (official docs, Apple WWDC sessions, reputable courses) — look them up, don't guess URLs.
   - **Prove**: a small portfolio project or feature the user can ship in 1–2 weeks that demonstrates it (e.g. "add Swift Concurrency + unit tests to <existing project>").
   - **Resume line**: what they'll be able to truthfully add once done.
6. Offer a week-by-week plan (default 4–6 weeks, fitting the hours/week the user gives) and, if a task tool or calendar is connected, offer to add it.
7. Save the plan to `job-hunt/skill-plan.md`. When the user later reports finishing something, add the new fact to `profile.md` (that's the only way it may appear on a resume).
