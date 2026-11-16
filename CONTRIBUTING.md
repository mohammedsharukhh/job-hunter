# Contributing

1. Fork, create a branch, make your change.
2. Skills live in `skills/<name>/SKILL.md` (YAML frontmatter `name` + `description` with trigger phrases). Keep each under ~3,000 words; move detail into `references/`.
3. Keep the guardrails in `skills/job-hunt/SKILL.md` intact — PRs that remove approval gates, enable bulk emailing, or allow invented resume content won't be merged.
4. Test scripts: `python3 scripts/tracker.py init --dir /tmp/jh && python3 scripts/dashboard.py --dir /tmp/jh && python3 scripts/render_resume.py examples/sample-resume.md --pdf --template modern`
5. Open a PR describing what you changed and how you tested it.
