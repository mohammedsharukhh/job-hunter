#!/usr/bin/env python3
"""SessionStart hook: runs automatically whenever a Claude session starts.
Finds the job-hunt workspace and tells Claude what to do — no command needed from the user.

Workspace: $JOB_HUNT_DIR, else ~/job-hunt, else ./job-hunt.
Output: JSON with hookSpecificOutput.additionalContext (added to Claude's context).
"""
import csv, datetime as dt, json, os, sys


def workspace():
    for d in (os.environ.get("JOB_HUNT_DIR"), os.path.expanduser("~/job-hunt"), os.path.join(os.getcwd(), "job-hunt")):
        if d and os.path.isfile(os.path.join(d, "profile.md")):
            return d
    return None


def pref(d, key, default):
    p = os.path.join(d, "preferences.yaml")
    if not os.path.exists(p): return default
    for line in open(p, encoding="utf-8"):
        s = line.split("#", 1)[0].strip()
        if s.startswith(key + ":"):
            v = s.split(":", 1)[1].strip().strip('"\'')
            return {"true": True, "false": False}.get(v.lower(), v) if v else default
    return default


def emit(text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
    sys.exit(0)


def main():
    d = workspace()
    if not d:
        emit("job-hunter plugin is installed but not set up yet. If the user talks about jobs, resumes or "
             "applying, offer one line: 'Want me to set up job hunter? Attach your resume.' Don't bring it up otherwise.")
    if pref(d, "auto_start", True) is False:
        emit(f"job-hunter workspace: {d} (auto-start is off; use job-hunter skills only when asked).")

    rows = []
    tp = os.path.join(d, "tracker.csv")
    if os.path.exists(tp):
        rows = list(csv.DictReader(open(tp, newline="", encoding="utf-8")))
    today = dt.date.today()
    lr = os.path.join(d, ".last_run")
    last = open(lr).read().strip() if os.path.exists(lr) else ""
    ran_today = last == today.isoformat()

    awaiting = [r for r in rows if r.get("status") in ("found", "tailored")]
    action = [r for r in rows if r.get("status") in ("assessment", "interview", "offer")]
    due = []
    for r in rows:
        try:
            if r.get("status") in ("applied", "emailed") and r.get("date_applied") and \
               (today - dt.date.fromisoformat(r["date_applied"])).days >= 7 and int(r.get("follow_ups") or 0) < 1:
                due.append(r)
        except ValueError:
            pass

    status = (f"job-hunter workspace: {d}. Today {today.isoformat()}; last full run: {last or 'never'}. "
              f"{len(awaiting)} jobs awaiting approval, {len(action)} need action "
              f"({', '.join(r['company'] + ' ' + r['status'] for r in action[:4])}), {len(due)} follow-ups due.")
    if not ran_today and today.weekday() < 7:
        todo = ("AUTO-START: today's job hunt hasn't run yet. At the start of your first reply in this session, "
                "briefly tell the user you're starting today's job hunt, then run the job-hunter `job-hunt` skill "
                f"(workspace {d}) — unless the user's first message is clearly about something unrelated and urgent, "
                "in which case answer that first and offer the run in one line. The approval step still applies "
                "according to preferences (outreach.mode).")
    else:
        todo = ("Today's run is done. If anything needs action, mention it in one line at the start of your first "
                "reply (e.g. 'Reminder: Acme interview Thursday — prep is ready'), then help with what the user asked.")
    emit(status + " " + todo)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never block a session
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                 "additionalContext": f"job-hunter status unavailable ({e})."}}))
