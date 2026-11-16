#!/usr/bin/env python3
"""Build a self-contained HTML dashboard from job-hunt/tracker.csv.

Usage: dashboard.py --dir job-hunt [--out job-hunt/dashboard.html] [--followup-days 7]
"""
import argparse, collections, csv, datetime as dt, html, os, sys

FUNNEL = [("Found", None), ("Applied / emailed", {"applied", "emailed", "assessment", "interview", "replied", "offer", "accepted", "rejected"}),
          ("Any reply", "reply"), ("Interview+", {"interview", "offer", "accepted"}), ("Offer", {"offer", "accepted"})]
COLORS = {"found": "#9AA5B1", "skipped": "#CBD2D9", "tailored": "#7B93DB", "applied": "#3E6FD8", "emailed": "#2B59C3",
          "assessment": "#E3A008", "interview": "#0E9F6E", "replied": "#31C48D", "offer": "#057A55",
          "accepted": "#03543F", "rejected": "#E02424", "closed": "#6B7280"}


def esc(x): return html.escape(str(x or ""))


def bar_rows(items, maxv, color="#3E6FD8"):
    out = []
    for label, v, extra in items:
        w = 0 if not maxv else max(2, int(100 * v / maxv)) if v else 0
        out.append(f'<div class="br"><span class="bl">{esc(label)}</span><span class="bt"><span class="bf" '
                   f'style="width:{w}%;background:{color}"></span></span><span class="bv">{v}{esc(extra)}</span></div>')
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="job-hunt")
    ap.add_argument("--out")
    ap.add_argument("--followup-days", type=int, default=7)
    a = ap.parse_args()
    p = os.path.join(a.dir, "tracker.csv")
    if not os.path.exists(p):
        sys.exit(f"No tracker at {p}")
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    for r in rows:
        for k in ("date_applied", "date_reply", "follow_ups", "source"):
            r.setdefault(k, "")
    today = dt.date.today()

    sent = [r for r in rows if r["date_applied"]]
    replied = [r for r in sent if r["date_reply"]]
    interviews = [r for r in rows if r["status"] in ("interview", "offer", "accepted")]
    offers = [r for r in rows if r["status"] in ("offer", "accepted")]
    rr = f"{len(replied) / len(sent):.0%}" if sent else "—"

    funnel = []
    for label, sel in FUNNEL:
        if sel is None: n = len([r for r in rows if r["status"] != "skipped"])
        elif sel == "reply": n = len(replied)
        else: n = len([r for r in rows if r["status"] in sel])
        funnel.append((label, n, ""))

    by_source = collections.defaultdict(lambda: [0, 0])
    for r in sent:
        by_source[r["source"] or "unknown"][0] += 1
        by_source[r["source"] or "unknown"][1] += 1 if r["date_reply"] else 0
    src_items = sorted(((s, v[0], f"  · {v[1]} replied") for s, v in by_source.items()), key=lambda x: -x[1])

    cutoff = today - dt.timedelta(days=a.followup_days)
    due = [r for r in rows if r["status"] in ("applied", "emailed") and r["date_applied"]
           and dt.date.fromisoformat(r["date_applied"]) <= cutoff and int(r["follow_ups"] or 0) < 1]
    action = [r for r in rows if r["status"] in ("assessment", "interview", "offer")]

    def table(rs, cols):
        if not rs: return '<p class="muted">Nothing here.</p>'
        head = "".join(f"<th>{c}</th>" for c, _ in cols)
        body = "".join("<tr>" + "".join(f"<td>{f(r)}</td>" for _, f in cols) + "</tr>" for r in rs)
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

    pill = lambda r: f'<span class="pill" style="background:{COLORS.get(r["status"], "#999")}">{esc(r["status"])}</span>'
    link = lambda r: f'<a href="{esc(r["url"])}" target="_blank">{esc(r["title"])}</a>' if r.get("url") else esc(r["title"])
    all_rows = sorted(rows, key=lambda r: r.get("date_updated", ""), reverse=True)

    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Job Hunt Dashboard</title><style>
:root{{--bg:#F7F8FA;--card:#fff;--ink:#1F2933;--muted:#7B8794;--line:#E4E7EB}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111418;--card:#1B1F24;--ink:#E4E7EB;--muted:#9AA5B1;--line:#2D333B}}}}
body{{margin:0;font:14px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}}
.wrap{{max-width:1100px;margin:auto;padding:24px}} h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:15px;margin:0 0 12px}}
.muted{{color:var(--muted)}} .grid{{display:grid;gap:16px}} .k{{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}}
.two{{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}}
.kv{{font-size:28px;font-weight:700}} .kl{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.br{{display:grid;grid-template-columns:130px 1fr 110px;align-items:center;gap:8px;margin:6px 0}}
.bl{{color:var(--muted)}} .bt{{background:var(--line);border-radius:6px;height:14px;overflow:hidden}} .bf{{display:block;height:100%;border-radius:6px}}
.bv{{font-variant-numeric:tabular-nums}} table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;color:var(--muted);font-weight:600}} .pill{{color:#fff;border-radius:999px;padding:2px 8px;font-size:12px}}
a{{color:#3E6FD8;text-decoration:none}} input{{box-sizing:border-box;width:100%;padding:8px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);margin-bottom:8px}}
</style></head><body><div class="wrap">
<h1>Job Hunt Dashboard</h1><p class="muted">Updated {today.isoformat()} · {len(rows)} jobs tracked</p>
<div class="grid k">
<div class="card"><div class="kl">Applied / emailed</div><div class="kv">{len(sent)}</div></div>
<div class="card"><div class="kl">Response rate</div><div class="kv">{rr}</div></div>
<div class="card"><div class="kl">Interviews</div><div class="kv">{len(interviews)}</div></div>
<div class="card"><div class="kl">Offers</div><div class="kv">{len(offers)}</div></div>
<div class="card"><div class="kl">Follow-ups due</div><div class="kv">{len(due)}</div></div>
</div><br>
<div class="grid two">
<div class="card"><h2>Funnel</h2>{bar_rows(funnel, max([n for _, n, _ in funnel] or [0]))}</div>
<div class="card"><h2>Applications by source</h2>{bar_rows(src_items, max([n for _, n, _ in src_items] or [0]), "#0E9F6E") if src_items else '<p class="muted">No applications yet.</p>'}</div>
</div><br>
<div class="grid two">
<div class="card"><h2>Needs action</h2>{table(action, [("Company", lambda r: esc(r["company"])), ("Role", link), ("Status", pill), ("Notes", lambda r: esc((r.get("notes") or "").split(" | ")[-1]))])}</div>
<div class="card"><h2>Follow-ups due</h2>{table(due, [("Company", lambda r: esc(r["company"])), ("Role", link), ("Sent", lambda r: esc(r["date_applied"]))])}</div>
</div><br>
<div class="card"><h2>All jobs</h2><input id="q" placeholder="Filter by company, role, status…" oninput="f()">
{table(all_rows, [("#", lambda r: esc(r["id"])), ("Company", lambda r: esc(r["company"])), ("Role", link), ("Location", lambda r: esc(r["location"])), ("Fit", lambda r: esc(r["score"])), ("Status", pill), ("Updated", lambda r: esc(r.get("date_updated")))])}
</div></div>
<script>function f(){{var q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('.card:last-child tbody tr').forEach(function(t){{t.style.display=t.textContent.toLowerCase().indexOf(q)>-1?'':'none'}})}}</script>
</body></html>"""
    out = a.out or os.path.join(a.dir, "dashboard.html")
    open(out, "w", encoding="utf-8").write(doc)
    print("Wrote", out)


if __name__ == "__main__":
    main()
