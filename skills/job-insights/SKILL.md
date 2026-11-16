---
name: job-insights
description: Analyses the user's application history to learn what works — which job sources, resume layouts, email templates and fit-score ranges get replies — and updates preferences so future runs favour what works. Use when the user says "what's working", "why am I not getting replies", "analyse my applications", "improve my response rate", or weekly via /job-hunter:job-hunt.
---

# Job Insights (learn from results)

1. Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/insights.py --dir job-hunt`
   It writes `job-hunt/insights.json`: reply rates by source, resume variant, email template and fit-score band, plus top skip reasons.
2. Interpret honestly. With fewer than ~10 sent applications, call patterns "early signals". Never overstate small samples.
3. Diagnose low response rates with the common causes:
   - Applying below fit threshold → raise `min_fit_score`.
   - A source with many sends and no replies → deprioritise it in `sources`.
   - One resume template/email template clearly outperforming → make it the default.
   - Applying late → prioritise postings < 7 days old.
   - Keyword coverage low on tailored resumes → run **skill-gap-coach**.
4. Show recommendations as a short list and ask before changing `preferences.yaml`. When approved, edit the file and add a dated line to `job-hunt/learning-log.md` saying what changed and why.
5. **Fit-score learning:** read `skip_reason` values (jobs the user rejected). If a reason repeats ≥ 3 times (e.g. "too senior", "needs relocation", "requires Flutter"), propose adding it to `exclude_keywords`, `seniority` or `avoid_companies`.

A/B testing: when two resume templates or email templates are in use, alternate them across similar jobs (record via `--resume-variant` / `--email-template` on tracker updates) so insights have something to compare.
