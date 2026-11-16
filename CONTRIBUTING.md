# Contributing

1. Fork, create a branch, make your change.
2. Skills live in `skills/<name>/SKILL.md` (YAML frontmatter `name` + `description` with trigger phrases). Keep each under ~3,000 words; move detail into `references/`.
3. Keep the guardrails in `skills/job-hunt/SKILL.md` intact — PRs that remove approval gates, enable bulk emailing, or allow invented resume content won't be merged.
4. Run the tests: `python3 -m unittest discover -s tests -v && python3 evals/run_golden.py` (needs `pip install python-docx pypdf`, poppler-utils). If you change `tailor-resume` or `quick-tailor`, run the LLM evals in `evals/evals.json` and paste the `check_case.py` results in your PR.
5. Open a PR describing what you changed and how you tested it.
