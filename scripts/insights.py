#!/usr/bin/env python3
"""Learn from results: which sources, resume variants, email templates, fit-score bands
and skip reasons correlate with replies. Writes job-hunt/insights.json and prints a summary.

Usage: insights.py --dir job-hunt [--min-n 3]
"""
import argparse, collections, csv, json, os, sys

POSITIVE = {"assessment", "interview", "offer", "accepted", "replied"}


def rate(group):
    sent = [r for r in group if r["date_applied"]]
    pos = [r for r in sent if r["status"] in POSITIVE or (r["date_reply"] and r["status"] != "rejected")]
    any_reply = [r for r in sent if r["date_reply"]]
    return {"sent": len(sent), "positive": len(pos), "any_reply": len(any_reply),
            "positive_rate": round(len(pos) / len(sent), 3) if sent else None}


def band(score):
    try:
        s = int(score)
    except (TypeError, ValueError):
        return "unscored"
    return "90+" if s >= 90 else "80-89" if s >= 80 else "70-79" if s >= 70 else "<70"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.environ.get("JOB_HUNT_DIR") or (os.path.expanduser("~/job-hunt") if os.path.isdir(os.path.expanduser("~/job-hunt")) else "job-hunt"))
    ap.add_argument("--min-n", type=int, default=3, help="min sends before a group counts as evidence")
    a = ap.parse_args()
    p = os.path.join(a.dir, "tracker.csv")
    if not os.path.exists(p):
        sys.exit(f"No tracker at {p}")
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    for r in rows:
        for k in ("date_applied", "date_reply", "resume_variant", "email_template", "skip_reason", "source", "score"):
            r.setdefault(k, "")

    out = {"overall": rate(rows), "by": {}}
    for key, fn in {"source": lambda r: r["source"] or "unknown",
                    "resume_variant": lambda r: r["resume_variant"] or "default",
                    "email_template": lambda r: r["email_template"] or "none",
                    "fit_band": lambda r: band(r["score"])}.items():
        groups = collections.defaultdict(list)
        for r in rows:
            groups[fn(r)].append(r)
        out["by"][key] = {g: rate(v) for g, v in groups.items()}

    skips = collections.Counter(r["skip_reason"].strip().lower() for r in rows if r["skip_reason"].strip())
    out["top_skip_reasons"] = skips.most_common(10)

    recs = []
    for key, groups in out["by"].items():
        ev = {g: v for g, v in groups.items() if v["sent"] >= a.min_n and v["positive_rate"] is not None}
        if len(ev) >= 2:
            best = max(ev, key=lambda g: ev[g]["positive_rate"])
            worst = min(ev, key=lambda g: ev[g]["positive_rate"])
            if ev[best]["positive_rate"] > ev[worst]["positive_rate"]:
                recs.append(f"{key}: '{best}' works best ({ev[best]['positive_rate']:.0%} positive of {ev[best]['sent']}) "
                            f"vs '{worst}' ({ev[worst]['positive_rate']:.0%} of {ev[worst]['sent']}).")
    if out["overall"]["sent"] < a.min_n * 2:
        recs.append(f"Only {out['overall']['sent']} sent so far — treat patterns as early signals.")
    out["recommendations"] = recs

    json.dump(out, open(os.path.join(a.dir, "insights.json"), "w"), indent=2)
    print(json.dumps({"overall": out["overall"], "recommendations": recs,
                      "top_skip_reasons": out["top_skip_reasons"]}, indent=2))


if __name__ == "__main__":
    main()
