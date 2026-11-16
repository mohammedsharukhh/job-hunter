# Quality evals

Two layers keep resume quality from drifting as contributors change the skills:

1. **Deterministic checkers (run in CI on every PR)**
   - `scripts/fact_check.py` — every number, skill, employer, title and credential must trace to `profile.md`.
   - `scripts/ats_check.py` — the rendered PDF must read back cleanly (name, contact, sections, order, bullets, keywords).
   - `evals/run_golden.py` — honest reference resumes in `golden/*/good.md` must PASS; `golden/*/fabricated.md` (invented metrics, skills, employers, certifications) must FAIL. If a checker change breaks either direction, CI fails.

2. **LLM evals (run before releasing skill changes)** — `evals.json` lists prompts for each case in `cases/`. Run them in Claude with the plugin installed, save outputs to `evals/outputs/`, then:
   ```bash
   for c in ios-mid procurement-analyst data-analyst; do python3 evals/check_case.py evals/cases/$c evals/outputs/$c.md; done
   ```
   Include the results in your PR description.

## Adding a case
Create `cases/<name>/` with `profile.md`, `jd.md` and `expected.json`:
- `supported_keywords`: JD keywords the profile genuinely supports (the resume should cover ≥ `min_coverage`).
- `unsupported_keywords`: JD keywords the profile lacks — appearing in the resume = fabrication.
Add `golden/<name>/good.md` and at least one `golden/<name>/fabricated*.md`.
