# ATS-friendly resume rules

## Layout
- Single column. No tables, text boxes, images, icons, headers/footers for key info, or skill bars.
- Standard section names: Summary, Skills, Experience, Projects, Education, Certifications.
- Standard fonts (Calibri/Arial), 10.5–11 pt body; dates as `Mon YYYY – Mon YYYY`.
- **Plain black text only** — no coloured headings, names, links or lines.
- Contact line at the top in plain text (email, phone, city, LinkedIn, GitHub).
- File name: `Firstname_Lastname_<Role>_Resume.pdf`.

## Writing
- Mirror the JD's exact phrasing for skills ("SwiftUI" not "Swift UI").
- Spell out acronyms once when JD does: "Continuous Integration (CI/CD)".
- Bullets: strong verb + what + how/tech + result. 1–2 lines each, 3–6 bullets per role.
- Quantify: users, downloads, ratings, latency, crash-free %, time saved, revenue, team size.
- No first person, no "responsible for", no buzzword stuffing, no white-text keyword hacks.
- Keyword target: ≥ 70% of must-haves covered *truthfully*.

## Markdown structure expected by render_resume.py
```
# Full Name
email · phone · City, Country · linkedin.com/in/x · github.com/x

## Summary
Two to four lines.

## Skills
**Languages:** Swift, Objective-C
**Frameworks:** SwiftUI, UIKit, Combine

## Experience
### iOS Developer — Company, City | Jan 2025 – Present
- Bullet
- Bullet

## Projects
### Project Name | link
- Bullet

## Education
### B.Tech Mechanical Engineering — University | 2021 – 2024
```
`#` = name, `##` = section, `###` = entry heading, `-` = bullet, `**x:**` = bold label.
