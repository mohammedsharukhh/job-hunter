#!/usr/bin/env python3
"""CI regression test: every evals/golden/<case>/good*.md must PASS and every
fabricated*.md must FAIL. Proves the checkers catch invented content and that
honest, well-tailored resumes score well. Run: python3 evals/run_golden.py"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_case import check

here = os.path.dirname(os.path.abspath(__file__))
ok = True
for g in sorted(glob.glob(os.path.join(here, "golden", "*", "*.md"))):
    case = os.path.join(here, "cases", os.path.basename(os.path.dirname(g)))
    r = check(case, g)
    expect_pass = os.path.basename(g).startswith("good")
    good = r["pass"] == expect_pass
    ok &= good
    tag = "ok " if good else "BAD"
    print(f"[{tag}] {r['case']}/{os.path.basename(g):<16} expected {'PASS' if expect_pass else 'FAIL'}, got "
          f"{'PASS' if r['pass'] else 'FAIL'} (coverage {r['coverage']:.0%}, ATS {r['ats_score']}"
          + (f", caught: {'; '.join(r['reasons'])}" if r["reasons"] else "") + ")")
print("ALL GOOD" if ok else "REGRESSION")
sys.exit(0 if ok else 1)
