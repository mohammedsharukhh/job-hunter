#!/usr/bin/env python3
"""Tiny CSV application tracker for job-hunter.

Usage:
  tracker.py init   --dir job-hunt
  tracker.py add    --dir job-hunt --company X --title Y [--url U --location L --score N --source S]
  tracker.py update --dir job-hunt --id ID [--status S --note N --contact C]
  tracker.py list   --dir job-hunt [--status S] [--json]
  tracker.py stats  --dir job-hunt
"""
import argparse, csv, datetime as dt, json, os, sys

FIELDS = ["id", "company", "title", "location", "url", "source", "score",
          "status", "contact", "date_added", "date_updated", "notes"]
STATUSES = ["found", "tailored", "applied", "emailed", "assessment", "interview",
            "replied", "offer", "rejected", "closed"]


def path(d):
    return os.path.join(d, "tracker.csv")


def load(d):
    p = path(d)
    if not os.path.exists(p):
        sys.exit(f"No tracker at {p}. Run: tracker.py init --dir {d}")
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(d, rows):
    with open(path(d), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def today():
    return dt.date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "add", "update", "list", "stats"])
    ap.add_argument("--dir", default="job-hunt")
    for a in ["company", "title", "url", "location", "source", "status", "note", "contact", "id"]:
        ap.add_argument(f"--{a}")
    ap.add_argument("--score", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "init":
        os.makedirs(os.path.join(a.dir, "applications"), exist_ok=True)
        if not os.path.exists(path(a.dir)):
            save(a.dir, [])
        print(f"Tracker ready: {path(a.dir)}")
        return

    rows = load(a.dir)

    if a.cmd == "add":
        if not (a.company and a.title):
            sys.exit("--company and --title are required")
        for r in rows:
            if (r["url"] and a.url and r["url"] == a.url) or \
               (r["company"].lower() == a.company.lower() and r["title"].lower() == a.title.lower()):
                print(f"Already tracked as id {r['id']}")
                return
        new_id = str(max([int(r["id"]) for r in rows] or [0]) + 1)
        rows.append({"id": new_id, "company": a.company, "title": a.title,
                     "location": a.location or "", "url": a.url or "", "source": a.source or "",
                     "score": a.score if a.score is not None else "", "status": "found",
                     "contact": "", "date_added": today(), "date_updated": today(), "notes": ""})
        save(a.dir, rows)
        print(f"Added id {new_id}: {a.company} — {a.title}")

    elif a.cmd == "update":
        if a.status and a.status not in STATUSES:
            sys.exit(f"status must be one of {STATUSES}")
        for r in rows:
            if r["id"] == a.id:
                if a.status: r["status"] = a.status
                if a.contact: r["contact"] = a.contact
                if a.note:
                    r["notes"] = (r["notes"] + " | " if r["notes"] else "") + f"{today()}: {a.note}"
                r["date_updated"] = today()
                save(a.dir, rows)
                print(f"Updated id {a.id}: {r['status']}")
                return
        sys.exit(f"No job with id {a.id}")

    elif a.cmd == "list":
        sel = [r for r in rows if not a.status or r["status"] == a.status]
        if a.json:
            print(json.dumps(sel, indent=2, ensure_ascii=False))
        else:
            for r in sel:
                print(f"{r['id']:>3}  {r['status']:<10} {r['score']:>3}  {r['company']} — {r['title']} ({r['location']})")
            if not sel:
                print("(no jobs)")

    elif a.cmd == "stats":
        counts = {s: 0 for s in STATUSES}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        sent_today = sum(1 for r in rows if r["status"] in ("applied", "emailed") and r["date_updated"] == today())
        print(json.dumps({"total": len(rows), "by_status": counts, "applied_or_emailed_today": sent_today}, indent=2))


if __name__ == "__main__":
    main()
