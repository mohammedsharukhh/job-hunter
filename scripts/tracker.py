#!/usr/bin/env python3
"""CSV application tracker for job-hunter.

Commands:
  init    --dir job-hunt
  add     --dir job-hunt --company X --title Y [--url --location --score --source --posted]
  update  --dir job-hunt --id ID [--status --note --contact --resume-variant --email-template --reason]
  list    --dir job-hunt [--status S] [--json]
  stats   --dir job-hunt
  due     --dir job-hunt [--days 7]         # follow-ups due
  sent-today --dir job-hunt                  # emails/applications sent today (for daily caps)
  mark-run   --dir job-hunt                  # record today's full run (auto-start hook reads it)
"""
import argparse, csv, datetime as dt, difflib, json, os, re, sys

FIELDS = ["id", "company", "title", "location", "url", "source", "score", "status",
          "contact", "resume_variant", "email_template", "posted_date", "date_added",
          "date_applied", "date_reply", "date_updated", "follow_ups", "skip_reason", "notes"]
STATUSES = ["found", "skipped", "tailored", "applied", "emailed", "assessment", "interview",
            "replied", "offer", "accepted", "rejected", "closed"]
REPLY_STATUSES = {"assessment", "interview", "replied", "offer", "accepted", "rejected"}


def path(d): return os.path.join(d, "tracker.csv")
def today(): return dt.date.today().isoformat()


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\b(pvt|private|ltd|limited|inc|llc|technologies|technology|solutions|w\.?l\.?l)\b", " ", s)
    s = re.sub(r"\b(sr|senior)\b", "senior", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def load(d):
    p = path(d)
    if not os.path.exists(p):
        sys.exit(f"No tracker at {p}. Run: tracker.py init --dir {d}")
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:  # migrate older trackers
        for k in FIELDS:
            r.setdefault(k, "")
        for k in list(r):
            if k not in FIELDS:
                r.pop(k)
    return rows


def save(d, rows):
    with open(path(d), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)


def find_dup(rows, company, title, url):
    for r in rows:
        if url and r["url"] and r["url"].split("?")[0] == url.split("?")[0]:
            return r
        if norm(r["company"]) == norm(company) and \
           difflib.SequenceMatcher(None, norm(r["title"]), norm(title)).ratio() >= 0.85:
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "add", "update", "list", "stats", "due", "sent-today", "mark-run"])
    ap.add_argument("--dir", default=os.environ.get("JOB_HUNT_DIR") or (os.path.expanduser("~/job-hunt") if os.path.isdir(os.path.expanduser("~/job-hunt")) else "job-hunt"))
    for a in ["company", "title", "url", "location", "source", "status", "note", "contact", "id",
              "posted", "resume-variant", "email-template", "reason"]:
        ap.add_argument(f"--{a}")
    ap.add_argument("--score", type=int)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "init":
        os.makedirs(os.path.join(a.dir, "applications"), exist_ok=True)
        if not os.path.exists(path(a.dir)):
            save(a.dir, [])
        else:
            save(a.dir, load(a.dir))  # migrate columns
        print(f"Tracker ready: {path(a.dir)}")
        return

    if a.cmd == "mark-run":  # record that today's full job-hunt run finished (read by the SessionStart hook)
        open(os.path.join(a.dir, ".last_run"), "w").write(today())
        print("Marked today's run as done"); return

    rows = load(a.dir)

    if a.cmd == "add":
        if not (a.company and a.title):
            sys.exit("--company and --title are required")
        dup = find_dup(rows, a.company, a.title, a.url)
        if dup:
            print(f"DUPLICATE of id {dup['id']} ({dup['company']} — {dup['title']}, status {dup['status']})")
            return
        new_id = str(max([int(r["id"]) for r in rows] or [0]) + 1)
        row = {k: "" for k in FIELDS}
        row.update({"id": new_id, "company": a.company, "title": a.title, "location": a.location or "",
                    "url": a.url or "", "source": a.source or "", "score": "" if a.score is None else a.score,
                    "status": "found", "posted_date": a.posted or "", "date_added": today(),
                    "date_updated": today(), "follow_ups": "0"})
        rows.append(row); save(a.dir, rows)
        print(f"Added id {new_id}: {a.company} — {a.title}")

    elif a.cmd == "update":
        if a.status and a.status not in STATUSES:
            sys.exit(f"status must be one of {STATUSES}")
        r = next((r for r in rows if r["id"] == a.id), None)
        if not r:
            sys.exit(f"No job with id {a.id}")
        if a.status:
            if a.status in ("applied", "emailed") and not r["date_applied"]:
                r["date_applied"] = today()
            if a.status in REPLY_STATUSES and not r["date_reply"]:
                r["date_reply"] = today()
            r["status"] = a.status
        if a.note and "follow-up" in a.note.lower():
            r["follow_ups"] = str(int(r["follow_ups"] or 0) + 1)
        if a.contact: r["contact"] = a.contact
        if a.resume_variant: r["resume_variant"] = a.resume_variant
        if a.email_template: r["email_template"] = a.email_template
        if a.reason: r["skip_reason"] = a.reason
        if a.note: r["notes"] = (r["notes"] + " | " if r["notes"] else "") + f"{today()}: {a.note}"
        r["date_updated"] = today()
        save(a.dir, rows)
        print(f"Updated id {a.id}: {r['status']}")

    elif a.cmd == "list":
        sel = [r for r in rows if not a.status or r["status"] == a.status]
        if a.json:
            print(json.dumps(sel, indent=2, ensure_ascii=False)); return
        for r in sel:
            print(f"{r['id']:>3}  {r['status']:<10} {str(r['score']):>3}  {r['company']} — {r['title']} ({r['location']})")
        if not sel: print("(no jobs)")

    elif a.cmd == "stats":
        counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}
        sent = [r for r in rows if r["date_applied"]]
        replied = [r for r in sent if r["date_reply"]]
        print(json.dumps({"total": len(rows), "by_status": counts, "sent": len(sent),
                          "reply_rate": round(len(replied) / len(sent), 3) if sent else None}, indent=2))

    elif a.cmd == "due":
        cutoff = dt.date.today() - dt.timedelta(days=a.days)
        due = [r for r in rows if r["status"] in ("applied", "emailed") and r["date_applied"]
               and dt.date.fromisoformat(r["date_applied"]) <= cutoff and int(r["follow_ups"] or 0) < 1]
        print(json.dumps(due, indent=2, ensure_ascii=False) if a.json else
              "\n".join(f"{r['id']:>3}  {r['company']} — {r['title']} (sent {r['date_applied']})" for r in due) or "(none due)")

    elif a.cmd == "sent-today":
        n = sum(1 for r in rows if r["date_applied"] == today())
        print(n)


if __name__ == "__main__":
    main()
