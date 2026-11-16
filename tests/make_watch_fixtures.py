"""Generate realistic ATS API fixtures with timestamps relative to now (used by tests)."""
import datetime as dt, json, os, sys
d = sys.argv[1]; os.makedirs(d, exist_ok=True)
now = dt.datetime.now(dt.timezone.utc)
iso = lambda h: (now - dt.timedelta(hours=h)).isoformat()
ms = lambda h: int((now - dt.timedelta(hours=h)).timestamp() * 1000)
fx = {
 "greenhouse_acme": {"jobs": [
   {"id": 101, "title": "iOS Engineer", "location": {"name": "Bengaluru, India"}, "absolute_url": "https://boards.greenhouse.io/acme/jobs/101", "first_published": iso(3), "updated_at": iso(3), "company_name": "Acme", "content": "&lt;p&gt;Build our app in &lt;b&gt;SwiftUI&lt;/b&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;3+ years Swift&lt;/li&gt;&lt;/ul&gt;"},
   {"id": 102, "title": "Senior iOS Engineer", "location": {"name": "Bengaluru, India"}, "absolute_url": "https://boards.greenhouse.io/acme/jobs/102", "first_published": iso(5), "company_name": "Acme", "content": ""},
   {"id": 103, "title": "Backend Engineer", "location": {"name": "Bengaluru, India"}, "absolute_url": "https://x/103", "first_published": iso(2), "company_name": "Acme", "content": ""},
   {"id": 104, "title": "iOS Developer", "location": {"name": "Bengaluru"}, "absolute_url": "https://x/104", "first_published": iso(24*20), "company_name": "Acme", "content": ""}]},
 "lever_beta": [
   {"id": "b1", "text": "Mobile Developer (iOS)", "categories": {"location": "Doha, Qatar"}, "hostedUrl": "https://jobs.lever.co/beta/b1", "applyUrl": "https://jobs.lever.co/beta/b1/apply", "createdAt": ms(10), "descriptionPlain": "Swift, UIKit, Combine"},
   {"id": "b2", "text": "iOS Developer", "categories": {"location": "London"}, "hostedUrl": "https://jobs.lever.co/beta/b2", "createdAt": ms(1), "descriptionPlain": ""}],
 "ashby_gamma": {"jobs": [
   {"id": "g1", "title": "iOS Engineer", "location": "Anywhere", "isRemote": True, "isListed": True, "publishedAt": iso(30), "jobUrl": "https://jobs.ashbyhq.com/gamma/g1", "applyUrl": "https://jobs.ashbyhq.com/gamma/g1/application", "descriptionPlain": "Remote iOS role, SwiftUI"},
   {"id": "g2", "title": "iOS Engineer (unlisted)", "location": "Anywhere", "isRemote": True, "isListed": False, "publishedAt": iso(1), "jobUrl": "x"}]},
 "workable_delta": {"name": "Delta", "jobs": [
   {"shortcode": "D1", "title": "Swift Developer", "city": "Bangalore", "country": "India", "url": "https://apply.workable.com/delta/j/D1", "published_on": now.date().isoformat(), "description": "<p>Swift</p>"}]},
 "smartrecruiters_Eps": {"content": [
   {"id": "e1", "name": "iOS Developer", "location": {"city": "Doha", "country": "qa", "remote": False}, "releasedDate": iso(6), "company": {"name": "Epsilon"}}]},
}
for k, v in fx.items():
    json.dump(v, open(os.path.join(d, k + ".json"), "w"))
open(os.path.join(d, "watchlist.txt"), "w").write("""# test watchlist
greenhouse:acme      Acme
lever:beta           Beta
ashby:gamma          Gamma
workable:delta       Delta
smartrecruiters:Eps  Epsilon
lever:missing        Missing Co
""")
print("fixtures in", d)
