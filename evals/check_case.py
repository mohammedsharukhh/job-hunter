#!/usr/bin/env python3
"""Score one tailored resume against an eval case.

Usage: check_case.py CASE_DIR CANDIDATE_resume.md [--json]
CASE_DIR has profile.md, jd.md, expected.json:
  supported_keywords    JD keywords the profile truly supports → resume should cover ≥ min_coverage
  unsupported_keywords  JD keywords the profile lacks → must NOT appear (would be fabrication)
  max_pages, min_ats    rendering + ATS self-test thresholds
Pass = fact check clean AND no unsupported keywords AND coverage ≥ min AND ATS ≥ min_ats.
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = lambda n: os.path.join(ROOT, "scripts", n)


def has(term, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])", text.lower()) is not None


def check(case, cand):
    exp = json.load(open(os.path.join(case, "expected.json")))
    text = open(cand, encoding="utf-8").read()
    res = {"case": os.path.basename(case.rstrip("/")), "candidate": cand}

    fc = subprocess.run([sys.executable, S("fact_check.py"), cand, "--profile", os.path.join(case, "profile.md"), "--json"],
                        capture_output=True, text=True)
    res["fact_check"] = json.loads(fc.stdout)["unsupported"]

    res["fabricated_keywords"] = [k for k in exp["unsupported_keywords"] if has(k, text)]
    covered = [k for k in exp["supported_keywords"] if has(k, text)]
    res["coverage"] = round(len(covered) / len(exp["supported_keywords"]), 3)
    res["missing_supported"] = [k for k in exp["supported_keywords"] if k not in covered]

    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "Candidate_Test_Resume")
        subprocess.run([sys.executable, S("render_resume.py"), cand, "--pdf", "--out", base], capture_output=True, check=True)
        f = base + ".pdf" if os.path.exists(base + ".pdf") else base + ".docx"
        kw = ",".join(exp["supported_keywords"])
        at = subprocess.run([sys.executable, S("ats_check.py"), f, "--source", cand, "--keywords", kw,
                             "--max-pages", str(exp.get("max_pages", 2)), "--json"], capture_output=True, text=True)
        a = json.loads(at.stdout)
        res["ats_score"], res["ats_critical"] = a["score"], a["critical_failures"]

    reasons = []
    if res["fact_check"]: reasons.append(f"{len(res['fact_check'])} unsupported facts")
    if res["fabricated_keywords"]: reasons.append("claims missing skills: " + ", ".join(res["fabricated_keywords"]))
    if res["coverage"] < exp["min_coverage"]: reasons.append(f"coverage {res['coverage']:.0%} < {exp['min_coverage']:.0%}")
    if res["ats_score"] < exp.get("min_ats", 85) or res["ats_critical"]: reasons.append(f"ATS {res['ats_score']}")
    res["pass"], res["reasons"] = not reasons, reasons
    return res


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    r = check(sys.argv[1], sys.argv[2])
    if "--json" in sys.argv: print(json.dumps(r, indent=2))
    else:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['case']}  coverage {r['coverage']:.0%}  ATS {r['ats_score']}  "
              + ("" if r["pass"] else "— " + "; ".join(r["reasons"])))
        for i in r["fact_check"]: print(f"    ✗ {i['type']}: {i['value']}")
    sys.exit(0 if r["pass"] else 1)
