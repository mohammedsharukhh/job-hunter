"""Unit tests for job-hunter scripts. Run: python3 -m unittest discover -s tests -v"""
import csv, json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = lambda n: os.path.join(ROOT, "scripts", n)
PY = sys.executable


def run(*args, check=True):
    r = subprocess.run([PY, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise AssertionError(f"{args} failed:\n{r.stdout}\n{r.stderr}")
    return r


class Tracker(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); run(S("tracker.py"), "init", "--dir", self.d)

    def test_add_dedupe_update(self):
        run(S("tracker.py"), "add", "--dir", self.d, "--company", "Acme", "--title", "iOS Developer", "--score", "80")
        out = run(S("tracker.py"), "add", "--dir", self.d, "--company", "Acme Pvt Ltd", "--title", "iOS developer").stdout
        self.assertIn("DUPLICATE", out)
        run(S("tracker.py"), "update", "--dir", self.d, "--id", "1", "--status", "applied")
        rows = list(csv.DictReader(open(os.path.join(self.d, "tracker.csv"))))
        self.assertEqual(len(rows), 1); self.assertEqual(rows[0]["status"], "applied"); self.assertTrue(rows[0]["date_applied"])

    def test_bad_status_rejected(self):
        run(S("tracker.py"), "add", "--dir", self.d, "--company", "A", "--title", "B")
        self.assertNotEqual(run(S("tracker.py"), "update", "--dir", self.d, "--id", "1", "--status", "hired", check=False).returncode, 0)


class Watchlist(unittest.TestCase):
    def test_filters_and_state(self):
        d = tempfile.mkdtemp(); fx = os.path.join(d, "fx")
        run(os.path.join(ROOT, "tests", "make_watch_fixtures.py"), fx)
        run(S("tracker.py"), "init", "--dir", d)
        os.replace(os.path.join(fx, "watchlist.txt"), os.path.join(d, "watchlist.txt"))
        args = [S("watch_jobs.py"), "--dir", d, "--fixtures", fx, "--titles", "iOS,Swift,Mobile",
                "--locations", "Bangalore,Bengaluru,India,Doha,Qatar,Remote", "--exclude", "Senior", "--json"]
        r = json.loads(run(*args, "--add").stdout)
        titles = sorted(f"{j['company']}|{j['title']}" for j in r["new"])
        self.assertEqual(titles, ["Acme|iOS Engineer", "Beta|Mobile Developer (iOS)", "Delta|Swift Developer",
                                  "Epsilon|iOS Developer", "Gamma|iOS Engineer"])
        self.assertEqual(len(r["errors"]), 1)  # missing company doesn't stop the run
        self.assertEqual(json.loads(run(*args).stdout)["new"], [])  # second run: nothing new
        self.assertEqual(len(list(csv.DictReader(open(os.path.join(d, "tracker.csv"))))), 5)


class ResumeAndATS(unittest.TestCase):
    def test_all_templates_pass_ats(self):
        md = os.path.join(ROOT, "examples", "sample-resume.md")
        for t in ("classic", "modern", "compact"):
            with tempfile.TemporaryDirectory() as td:
                base = os.path.join(td, f"Alex_Sample_iOS_Resume")
                run(S("render_resume.py"), md, "--pdf", "--template", t, "--out", base)
                f = base + (".pdf" if os.path.exists(base + ".pdf") else ".docx")
                r = json.loads(run(S("ats_check.py"), f, "--source", md, "--max-pages", "1", "--json", check=False).stdout)
                self.assertGreaterEqual(r["score"], 85, f"{t}: {r}")
                self.assertEqual(r["critical_failures"], [])


class FactCheck(unittest.TestCase):
    def test_catches_fabrication(self):
        case = os.path.join(ROOT, "evals", "cases", "ios-mid")
        bad = os.path.join(ROOT, "evals", "golden", "ios-mid", "fabricated.md")
        good = os.path.join(ROOT, "evals", "golden", "ios-mid", "good.md")
        self.assertEqual(run(S("fact_check.py"), good, "--profile", os.path.join(case, "profile.md"), check=False).returncode, 0)
        r = json.loads(run(S("fact_check.py"), bad, "--profile", os.path.join(case, "profile.md"), "--json", check=False).stdout)
        vals = {i["value"] for i in r["unsupported"]}
        for v in ("45", "Google", "XCTest", "Kotlin"):
            self.assertIn(v, vals)


class Golden(unittest.TestCase):
    def test_golden_regression(self):
        run(os.path.join(ROOT, "evals", "run_golden.py"))


class StatsAndDashboard(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); run(S("tracker.py"), "init", "--dir", self.d)
        for i, c in enumerate(["A", "B", "C"]):
            run(S("tracker.py"), "add", "--dir", self.d, "--company", c, "--title", f"Role {i}", "--source", "LinkedIn")
            run(S("tracker.py"), "update", "--dir", self.d, "--id", str(i + 1), "--status", "applied")
        run(S("tracker.py"), "update", "--dir", self.d, "--id", "1", "--status", "interview")

    def test_share_stats_is_anonymous(self):
        out = run(S("share_stats.py"), "--dir", self.d, "--role-family", "ios", "--region", "india").stdout
        d = json.loads(out)
        self.assertEqual(d["schema"], "job-hunter-stats/1")
        for secret in ("Role 0", '"A"', "LinkedIn"):  # titles, company names, raw source names must not leak
            self.assertNotIn(secret, out)
        self.assertIn("linkedin", d["by_source"])

    def test_dashboard_and_insights(self):
        run(S("dashboard.py"), "--dir", self.d)
        self.assertTrue(os.path.getsize(os.path.join(self.d, "dashboard.html")) > 2000)
        run(S("insights.py"), "--dir", self.d)


if __name__ == "__main__":
    unittest.main()
