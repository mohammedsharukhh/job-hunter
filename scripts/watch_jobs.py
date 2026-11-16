#!/usr/bin/env python3
"""Company watchlist: poll public ATS job-board APIs (no browser, no login) and report
NEW postings that match your titles/locations — so you can apply in the first hours.

Supported (all public, read-only endpoints published by the ATS vendors):
  greenhouse:<board>        https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true
  lever:<company>           https://api.lever.co/v0/postings/<company>?mode=json
  ashby:<board>             https://api.ashbyhq.com/posting-api/job-board/<board>
  workable:<account>        https://apply.workable.com/api/v1/widget/accounts/<account>
  smartrecruiters:<company> https://api.smartrecruiters.com/v1/companies/<company>/postings

Watchlist file (job-hunt/watchlist.txt), one per line:
  greenhouse:airbnb   Airbnb
  lever:spotify       Spotify        # comments allowed
Find the slug in the company's careers URL (boards.greenhouse.io/<slug>, jobs.lever.co/<slug>,
jobs.ashbyhq.com/<slug>, apply.workable.com/<slug>, jobs.smartrecruiters.com/<slug>).

Usage:
  watch_jobs.py --dir job-hunt --titles "iOS,Swift,Mobile" --locations "Bangalore,Bengaluru,India,Doha,Qatar,Remote"
                [--exclude "Senior,Staff,Principal"] [--max-age-hours 72] [--add] [--json] [--fixtures DIR]
  --add       add new matches to tracker.csv and save each JD to applications/<company>-<title>/jd.md
  --fixtures  read <ats>_<slug>.json files from DIR instead of the network (tests/offline)
First run marks everything as seen except postings newer than --max-age-hours.
"""
import argparse, datetime as dt, html, json, os, re, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "job-hunter-watchlist/0.3 (+https://github.com/; personal job search, polite polling)"
URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{s}/jobs?content=true",
    "lever": "https://api.lever.co/v0/postings/{s}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{s}",
    "workable": "https://apply.workable.com/api/v1/widget/accounts/{s}",
    "smartrecruiters": "https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=100",
}


def strip_html(x):
    x = html.unescape(x or "")
    x = re.sub(r"<(br|/p|/li|/h\d)[^>]*>", "\n", x, flags=re.I)
    x = re.sub(r"<li[^>]*>", "- ", x, flags=re.I)
    x = re.sub(r"<[^>]+>", "", x)
    return re.sub(r"\n{3,}", "\n\n", x).strip()


def parse_time(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):  # epoch ms (Lever)
        return dt.datetime.fromtimestamp(v / 1000, dt.timezone.utc)
    try:
        t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        try:
            return dt.datetime.strptime(str(v)[:10], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
        except ValueError:
            return None


def normalise(ats, slug, data, company):
    out = []
    if ats == "greenhouse":
        for j in data.get("jobs", []):
            out.append(dict(id=j.get("id"), title=j.get("title"), location=(j.get("location") or {}).get("name", ""),
                            url=j.get("absolute_url"), posted=j.get("first_published") or j.get("updated_at"),
                            company=j.get("company_name") or company, description=strip_html(j.get("content"))))
    elif ats == "lever":
        for j in data if isinstance(data, list) else []:
            c = j.get("categories") or {}
            loc = c.get("location") or ", ".join(c.get("allLocations") or [])
            if j.get("workplaceType") == "remote": loc = (loc + " (Remote)").strip()
            out.append(dict(id=j.get("id"), title=j.get("text"), location=loc, url=j.get("hostedUrl"),
                            apply_url=j.get("applyUrl"), posted=j.get("createdAt"), company=company,
                            description=j.get("descriptionPlain") or strip_html(j.get("description"))))
    elif ats == "ashby":
        for j in data.get("jobs", []):
            if j.get("isListed") is False: continue
            locs = [j.get("location") or ""] + [s.get("location", "") for s in (j.get("secondaryLocations") or []) if isinstance(s, dict)]
            loc = ", ".join(l for l in locs if l) + (" (Remote)" if j.get("isRemote") else "")
            out.append(dict(id=j.get("id"), title=j.get("title"), location=loc, url=j.get("jobUrl"),
                            apply_url=j.get("applyUrl"), posted=j.get("publishedAt"), company=company,
                            description=j.get("descriptionPlain") or strip_html(j.get("descriptionHtml"))))
    elif ats == "workable":
        for j in data.get("jobs", []):
            loc = ", ".join(x for x in [j.get("city"), j.get("state"), j.get("country")] if x)
            if j.get("telecommuting"): loc += " (Remote)"
            out.append(dict(id=j.get("shortcode") or j.get("url"), title=j.get("title"), location=loc,
                            url=j.get("url") or j.get("shortlink"), posted=j.get("published_on") or j.get("created_at"),
                            company=data.get("name") or company, description=strip_html(j.get("description"))))
    elif ats == "smartrecruiters":
        for j in data.get("content", []):
            l = j.get("location") or {}
            loc = ", ".join(x for x in [l.get("city"), l.get("region"), l.get("country")] if x) + (" (Remote)" if l.get("remote") else "")
            out.append(dict(id=j.get("id"), title=j.get("name"), location=loc,
                            url=f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}", posted=j.get("releasedDate"),
                            company=(j.get("company") or {}).get("name") or company, description=""))
    for o in out:
        o["ats"], o["slug"], o["key"] = ats, slug, f"{ats}:{slug}:{o['id']}"
    return out


def fetch(ats, slug, fixtures):
    if fixtures:
        p = os.path.join(fixtures, f"{ats}_{slug}.json")
        return json.load(open(p, encoding="utf-8"))
    req = urllib.request.Request(URLS[ats].format(s=slug), headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def words(csv_str):
    return [w.strip().lower() for w in (csv_str or "").split(",") if w.strip()]


def matches(job, titles, locations, exclude):
    t, l = (job["title"] or "").lower(), (job["location"] or "").lower()
    if titles and not any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in titles): return False
    if exclude and any(re.search(r"\b" + re.escape(w) + r"\b", t) for w in exclude): return False
    if locations and not any(w in l for w in locations): return False
    return True


def slugify(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.environ.get("JOB_HUNT_DIR") or (os.path.expanduser("~/job-hunt") if os.path.isdir(os.path.expanduser("~/job-hunt")) else "job-hunt"))
    ap.add_argument("--watchlist")
    ap.add_argument("--titles", default="")
    ap.add_argument("--locations", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--max-age-hours", type=float, default=72)
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fixtures")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between companies (be polite)")
    a = ap.parse_args()

    wl = a.watchlist or os.path.join(a.dir, "watchlist.txt")
    if not os.path.exists(wl):
        sys.exit(f"No watchlist at {wl}. Create it with lines like 'greenhouse:airbnb  Airbnb'.")
    entries = []
    for line in open(wl, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if not line: continue
        spec, _, name = line.partition(" ")
        ats, _, slug = spec.partition(":")
        if ats not in URLS or not slug:
            print(f"skip bad line: {line}", file=sys.stderr); continue
        entries.append((ats, slug, name.strip() or slug))

    state_p = os.path.join(a.dir, ".watch_state.json")
    state = json.load(open(state_p)) if os.path.exists(state_p) else {"seen": {}, "last_run": None}
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=a.max_age_hours)
    titles, locs, excl = words(a.titles), words(a.locations), words(a.exclude)

    new, errors, checked = [], [], 0
    for i, (ats, slug, name) in enumerate(entries):
        if i and not a.fixtures: time.sleep(a.delay)
        try:
            jobs = normalise(ats, slug, fetch(ats, slug, a.fixtures), name)
            checked += 1
        except Exception as e:  # keep going on one bad company
            errors.append(f"{ats}:{slug}: {type(e).__name__}: {e}"); continue
        for j in jobs:
            if j["key"] in state["seen"]: continue
            state["seen"][j["key"]] = now.isoformat()
            posted = parse_time(j["posted"])
            if posted and posted < cutoff: continue  # old posting we just haven't seen before
            if not matches(j, titles, locs, excl): continue
            j["posted_iso"] = posted.isoformat() if posted else ""
            j["age_hours"] = round((now - posted).total_seconds() / 3600, 1) if posted else None
            new.append(j)

    new.sort(key=lambda j: j["age_hours"] if j["age_hours"] is not None else 1e9)
    if a.add:
        for j in new:
            folder = os.path.join(a.dir, "applications", f"{slugify(j['company'])}-{slugify(j['title'])}")
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, "jd.md"), "w", encoding="utf-8") as f:
                f.write(f"# {j['title']} — {j['company']}\n\n- Source: {j['ats']} watchlist\n- URL: {j['url']}\n"
                        f"- Apply: {j.get('apply_url') or j['url']} (portal)\n- Location: {j['location']}\n"
                        f"- Posted: {j['posted_iso']}\n\n## Description\n\n{j['description'] or '(open the URL for the full description)'}\n")
            r = subprocess.run([sys.executable, os.path.join(HERE, "tracker.py"), "add", "--dir", a.dir,
                                "--company", j["company"], "--title", j["title"], "--url", j["url"] or "",
                                "--location", j["location"], "--source", f"watchlist:{j['ats']}",
                                "--posted", (j["posted_iso"] or "")[:10]], capture_output=True, text=True)
            j["tracker"] = r.stdout.strip()

    state["last_run"] = now.isoformat()
    json.dump(state, open(state_p, "w"), indent=1)

    if a.json:
        print(json.dumps({"checked": checked, "errors": errors, "new": [{k: v for k, v in j.items() if k != "description"} for j in new]}, indent=2))
    else:
        print(f"Checked {checked}/{len(entries)} companies · {len(new)} new matching postings")
        for j in new:
            age = f"{j['age_hours']}h ago" if j["age_hours"] is not None else "date unknown"
            print(f"  NEW  {j['company']} — {j['title']} ({j['location']}) · {age}\n       {j['url']}")
        for e in errors:
            print("  ERROR", e)


if __name__ == "__main__":
    main()
