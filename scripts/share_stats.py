#!/usr/bin/env python3
"""Build an ANONYMOUS, opt-in summary of your job-search results to share with the
job-hunter project. Nothing is sent by this script — it only writes/prints JSON for you
to review and submit yourself (GitHub issue form) if you want.

Contains only: counts and rates, generic source types, resume template names, region,
role family, month, plugin version, and a random ID (so re-submitting updates your entry).
Never contains: names, emails, phone, companies, job titles, URLs, notes, dates of
individual applications, salaries.

Usage: share_stats.py --dir job-hunt --role-family ios [--region india] [--save]
"""
import argparse, collections, csv, datetime as dt, json, os, re, sys, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
POSITIVE = {"assessment", "interview", "offer", "accepted", "replied"}
SOURCE_MAP = [("watchlist", "watchlist"), ("linkedin", "linkedin"), ("naukri", "naukri"), ("indeed", "indeed"),
              ("bayt", "gulf_board"), ("gulftalent", "gulf_board"), ("naukrigulf", "gulf_board"),
              ("career", "career_page"), ("greenhouse", "ats_board"), ("lever", "ats_board"), ("ashby", "ats_board"),
              ("workday", "ats_board"), ("referral", "referral"), ("email", "email")]
ROLE_FAMILIES = ["ios", "android", "mobile", "frontend", "backend", "fullstack", "data", "ml", "devops", "qa",
                 "design", "product", "procurement", "supply_chain", "mechanical", "civil", "electrical",
                 "finance", "sales", "marketing", "hr", "operations", "healthcare", "other"]
REGIONS = ["india", "gulf", "eu_uk", "us", "other"]


def generic_source(s):
    s = (s or "").lower()
    for k, v in SOURCE_MAP:
        if k in s: return v
    return "other"


def plugin_version():
    try:
        return json.load(open(os.path.join(HERE, "..", ".claude-plugin", "plugin.json")))["version"]
    except Exception:
        return "unknown"


def rate(n, d): return round(n / d, 3) if d else None


def bucket(n):
    """Coarsen small counts so tiny searches can't be fingerprinted."""
    if n < 5: return n
    return int(round(n / 5.0) * 5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="job-hunt")
    ap.add_argument("--role-family", required=True, choices=ROLE_FAMILIES)
    ap.add_argument("--region", choices=REGIONS)
    ap.add_argument("--save", action="store_true", help="write job-hunt/stats-share.json")
    a = ap.parse_args()

    p = os.path.join(a.dir, "tracker.csv")
    if not os.path.exists(p): sys.exit(f"No tracker at {p}")
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    for r in rows:
        for k in ("date_applied", "date_reply", "resume_variant", "source", "date_added"): r.setdefault(k, "")

    region = a.region
    if not region:
        pref = os.path.join(a.dir, "preferences.yaml")
        m = re.search(r"^regions:\s*\[([^\]]*)\]", open(pref).read(), re.M) if os.path.exists(pref) else None
        regs = [x.strip() for x in m.group(1).split(",")] if m else []
        region = regs[0] if len(regs) == 1 and regs[0] in REGIONS else ("multi" if len(regs) > 1 else "other")

    id_p = os.path.join(a.dir, ".stats_id")
    sid = open(id_p).read().strip() if os.path.exists(id_p) else str(uuid.uuid4())
    open(id_p, "w").write(sid)

    sent = [r for r in rows if r["date_applied"]]
    pos = [r for r in sent if r["status"] in POSITIVE or (r["date_reply"] and r["status"] != "rejected")]
    anyr = [r for r in sent if r["date_reply"]]
    interviews = [r for r in rows if r["status"] in ("interview", "offer", "accepted")]
    offers = [r for r in rows if r["status"] in ("offer", "accepted")]
    dates = sorted(r["date_added"] for r in rows if r["date_added"])
    weeks = max(1, (dt.date.fromisoformat(dates[-1]) - dt.date.fromisoformat(dates[0])).days // 7 + 1) if dates else 0

    def group(keyfn):
        g = collections.defaultdict(list)
        for r in sent: g[keyfn(r)].append(r)
        return {k: {"sent": bucket(len(v)), "any_reply_rate": rate(sum(1 for r in v if r["date_reply"]), len(v))}
                for k, v in g.items()}

    out = {
        "schema": "job-hunter-stats/1",
        "submission_id": sid,
        "month": dt.date.today().strftime("%Y-%m"),
        "plugin_version": plugin_version(),
        "role_family": a.role_family,
        "region": region,
        "weeks_active": weeks,
        "jobs_found": bucket(len(rows)),
        "applications_sent": bucket(len(sent)),
        "any_reply_rate": rate(len(anyr), len(sent)),
        "positive_reply_rate": rate(len(pos), len(sent)),
        "interview_rate": rate(len(interviews), len(sent)),
        "offers": len(offers),
        "by_source": group(lambda r: generic_source(r["source"])),
        "by_resume_template": group(lambda r: (r["resume_variant"] or "default") if r["resume_variant"] in ("", "classic", "modern", "compact") else "other"),
    }
    js = json.dumps(out, indent=2)
    if a.save:
        open(os.path.join(a.dir, "stats-share.json"), "w").write(js)
    print(js)


if __name__ == "__main__":
    main()
