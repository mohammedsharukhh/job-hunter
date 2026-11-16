---
name: share-stats
description: Prepares an anonymous, opt-in summary of the user's job-search results (counts and reply rates only) that they can choose to submit to the job-hunter project's public results page. Use when the user says "share my stats", "contribute my results", "publish my response rate", or after a job search ends (offer accepted).
---

# Share My Results (anonymous, opt-in)

Real response rates are how other job seekers decide whether this works. Sharing is always the user's choice — never submit anything on their behalf without an explicit yes.

1. Ask the role family (ios, android, data, procurement, mechanical, … see `--role-family` choices) and region if not in preferences.
2. Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/share_stats.py --dir job-hunt --role-family <family> --save`
3. Show the JSON to the user and say plainly what's in it (counts, rates, generic source types, template names, region, month, a random ID) and what is NOT (no names, companies, job titles, emails, URLs, salaries).
4. If they agree, offer two ways to submit:
   - Open the project's "📊 Share my results" issue form (`https://github.com/<owner>/job-hunter/issues/new?template=share-stats.yml`) and paste the JSON, or
   - With the user's OK and the GitHub CLI signed in: save the JSON wrapped in a ```json block to a file and run
     `gh issue create --repo <owner>/job-hunter --label stats --title stats --body-file <file>`.
5. Re-sharing later reuses the same random ID, so their entry is updated rather than duplicated.
