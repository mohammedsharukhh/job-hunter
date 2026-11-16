#!/usr/bin/env python3
"""Maintainers: aggregate community stat submissions into docs/RESULTS.md and the
README results table.

Sources (any combination):
  --from-gh OWNER/REPO   read open+closed issues labelled 'stats' via the gh CLI
  --from-dir DIR         read *.json files (one submission each)
Writes docs/RESULTS.md and replaces the block between
<!-- RESULTS:START --> and <!-- RESULTS:END --> in README.md.
"""
import argparse, collections, glob, json, os, re, statistics, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "job-hunter-stats/1"
JSON_BLOCK = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)


def valid(d):
    if not isinstance(d, dict) or d.get("schema") != SCHEMA: return False
    for k in ("submission_id", "applications_sent", "role_family", "region"):
        if k not in d: return False
    if not isinstance(d["applications_sent"], (int, float)) or d["applications_sent"] < 1 or d["applications_sent"] > 5000:
        return False
    for k in ("any_reply_rate", "positive_reply_rate", "interview_rate"):
        v = d.get(k)
        if v is not None and not (0 <= v <= 1): return False
    return True


def from_gh(repo):
    out = subprocess.run(["gh", "issue", "list", "--repo", repo, "--label", "stats", "--state", "all",
                          "--limit", "1000", "--json", "body,createdAt"], capture_output=True, text=True, check=True).stdout
    subs = []
    for issue in sorted(json.loads(out), key=lambda i: i["createdAt"]):
        for m in JSON_BLOCK.finditer(issue["body"] or ""):
            try: subs.append(json.loads(m.group(1)))
            except json.JSONDecodeError: pass
    return subs


def pct(x): return "—" if x is None else f"{x:.0%}"


def med(vals):
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-gh")
    ap.add_argument("--from-dir")
    ap.add_argument("--min-group", type=int, default=3, help="hide groups with fewer submitters (privacy)")
    a = ap.parse_args()
    subs = []
    if a.from_gh: subs += from_gh(a.from_gh)
    if a.from_dir: subs += [json.load(open(f)) for f in sorted(glob.glob(os.path.join(a.from_dir, "*.json")))]
    latest = {}
    for s in subs:
        if valid(s): latest[s["submission_id"]] = s  # later submission replaces earlier
    S = list(latest.values())
    n = len(S)
    total_sent = int(sum(s["applications_sent"] for s in S))

    def table(keyfn, title):
        g = collections.defaultdict(list)
        for s in S: g[keyfn(s)].append(s)
        rows = [(k, v) for k, v in g.items() if len(v) >= a.min_group]
        if not rows: return f"_{title}: not enough submissions yet (need ≥{a.min_group} per group)._\n"
        lines = [f"| {title} | Job seekers | Applications | Median reply rate | Median interview rate |", "|---|---|---|---|---|"]
        for k, v in sorted(rows, key=lambda kv: -len(kv[1])):
            lines.append(f"| {k} | {len(v)} | {int(sum(x['applications_sent'] for x in v))} | "
                         f"{pct(med([x.get('any_reply_rate') for x in v]))} | {pct(med([x.get('interview_rate') for x in v]))} |")
        return "\n".join(lines) + "\n"

    src = collections.defaultdict(lambda: [0, 0.0])
    tpl = collections.defaultdict(lambda: [0, 0.0])
    for s in S:
        for k, v in (s.get("by_source") or {}).items():
            if v.get("any_reply_rate") is not None:
                src[k][0] += v["sent"]; src[k][1] += v["sent"] * v["any_reply_rate"]
        for k, v in (s.get("by_resume_template") or {}).items():
            if v.get("any_reply_rate") is not None:
                tpl[k][0] += v["sent"]; tpl[k][1] += v["sent"] * v["any_reply_rate"]
    def weighted(d, title):
        rows = [(k, v) for k, v in d.items() if v[0] >= 20]
        if not rows: return f"_{title}: not enough data yet._\n"
        lines = [f"| {title} | Applications | Reply rate |", "|---|---|---|"]
        for k, v in sorted(rows, key=lambda kv: -kv[1][1] / kv[1][0]):
            lines.append(f"| {k} | {v[0]} | {v[1] / v[0]:.0%} |")
        return "\n".join(lines) + "\n"

    headline = (f"**{n} job seekers · {total_sent} applications** · median reply rate "
                f"**{pct(med([s.get('any_reply_rate') for s in S]))}** · median interview rate "
                f"**{pct(med([s.get('interview_rate') for s in S]))}** · offers reported: **{sum(s.get('offers', 0) for s in S)}**"
                if n else "_No submissions yet — be the first: see “Share your results” below._")
    body = f"""{headline}

{table(lambda s: s['role_family'], 'Role')}
{table(lambda s: s['region'], 'Region')}
{weighted(src, 'Source')}
{weighted(tpl, 'Resume template')}
<sub>Self-reported, anonymous, opt-in. Groups with fewer than {a.min_group} people are hidden. Not a guarantee of results.</sub>
"""
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "RESULTS.md"), "w").write("# Community results\n\n" + body)
    rp = os.path.join(ROOT, "README.md")
    readme = open(rp).read()
    new = re.sub(r"<!-- RESULTS:START -->.*?<!-- RESULTS:END -->", f"<!-- RESULTS:START -->\n{body}<!-- RESULTS:END -->", readme, flags=re.S)
    open(rp, "w").write(new)
    print(f"{n} valid submissions aggregated → docs/RESULTS.md, README.md")


if __name__ == "__main__":
    main()
