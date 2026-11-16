#!/usr/bin/env python3
"""ATS self-test: read a resume file back the way applicant-tracking systems do (plain
text extraction, no layout) and verify the important fields survive.

Usage:
  ats_check.py RESUME.pdf|.docx [--source resume.md] [--keywords "SwiftUI,Combine,CI/CD"]
               [--keywords-file kw.txt] [--max-pages 1] [--min-score 80] [--json]

Checks: text is extractable · name, email, phone found · standard section headings ·
every job title / company / date range from resume.md present and in order · bullets not
scrambled (multi-column / text-box problems) · skills present · JD keywords present ·
odd glyphs (icons, ligatures) · page count · file name & size.
Exit code 1 when the score is below --min-score (useful in CI).
"""
import argparse, json, os, re, shutil, subprocess, sys

SECTIONS = {
    "summary": ["summary", "profile", "professional summary", "about"],
    "skills": ["skills", "technical skills", "core skills", "key skills"],
    "experience": ["experience", "work experience", "professional experience", "employment history"],
    "education": ["education", "academic background"],
}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
DATE = re.compile(r"((jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{4}|\b(19|20)\d{2}\b|present|current)", re.I)
BAD_GLYPHS = re.compile("[\ufffd\ue000-\uf8ff\ufb00-\ufb06\u2600-\u27bf\u2b00-\u2bff\U0001f000-\U0001faff]")
CRITICAL = {"text extractable", "email", "name at top", "reading order"}


def norm(s):
    s = (s or "").replace("–", "-").replace("—", "-").replace("−", "-").replace(" ", " ")
    s = re.sub(r"\*\*|__|`", "", s)
    s = re.sub(r"[•▪●◦·|]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def extract(path):
    ext = os.path.splitext(path)[1].lower()
    pages = None
    if ext == ".pdf":
        text = ""
        if shutil.which("pdftotext"):  # raw reading order, like most ATS parsers
            text = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, text=True).stdout
        if not text.strip():
            try:
                from pypdf import PdfReader
                text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            except ImportError:
                sys.exit("Install poppler-utils (pdftotext) or `pip install pypdf`")
        try:
            from pypdf import PdfReader
            pages = len(PdfReader(path).pages)
        except Exception:
            if shutil.which("pdfinfo"):
                m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout)
                pages = int(m.group(1)) if m else None
        return text, pages
    if ext == ".docx":
        from docx import Document
        d = Document(path)
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:  # ATS often drop or scramble tables — report them
            parts.append("[[TABLE]]")
        for s in d.sections:
            for p in s.header.paragraphs + s.footer.paragraphs:
                if p.text.strip(): parts.append("[[HEADER/FOOTER]] " + p.text)
        return "\n".join(parts), None
    if ext in (".txt", ".md"):
        return open(path, encoding="utf-8").read(), None
    sys.exit(f"Unsupported file type: {ext}")


def parse_md(path):
    """Expected facts from the resume.md source (structure in tailor-resume/references/ats-rules.md)."""
    info = {"name": "", "contact": "", "entries": [], "bullets": [], "skills": [], "sections": []}
    section = None
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line: continue
        if line.startswith("# "):
            info["name"] = line[2:].strip(); continue
        if info["name"] and not info["contact"] and not line.startswith("#"):
            info["contact"] = line; continue
        if line.startswith("## "):
            section = line[3:].strip().lower(); info["sections"].append(section); continue
        if line.startswith("### "):
            head = line[4:].strip()
            left, _, right = head.rpartition("|") if "|" in head else (head, "", "")
            parts = [p.strip() for p in re.split(r"\s+[—–-]\s+|,", left) if p.strip()]
            info["entries"].append({"raw": head, "parts": parts, "dates": right.strip(), "section": section}); continue
        if re.match(r"^[-*] ", line):
            info["bullets"].append(line[2:].strip()); continue
        if section and "skill" in section:
            body = re.sub(r"^\*\*[^*]+:\*\*", "", line)
            info["skills"] += [s.strip(" .") for s in re.split(r"[,;·]", body) if s.strip(" .")]
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resume")
    ap.add_argument("--source")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--keywords-file")
    ap.add_argument("--max-pages", type=int, default=2)
    ap.add_argument("--min-score", type=int, default=80)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    text, pages = extract(a.resume)
    T = norm(text)
    lines = [norm(l) for l in text.splitlines() if l.strip()]
    checks = []  # (name, weight, passed(0..1), detail)

    def add(name, weight, ratio, detail=""):
        checks.append({"check": name, "weight": weight, "score": round(max(0.0, min(1.0, ratio)), 3), "detail": detail})

    add("text extractable", 15, 1.0 if len(T) > 300 else 0.0,
        f"{len(T)} characters extracted" + ("" if len(T) > 300 else " — looks image-based or empty; ATS will see nothing"))

    emails, phones = EMAIL.findall(text), PHONE.findall(text)
    src = parse_md(a.source) if a.source else None
    if src:
        nm = norm(src["name"])
        add("name at top", 8, 1.0 if any(nm == l or nm in l for l in lines[:3]) else 0.5 if nm in T else 0.0,
            f"expected '{src['name']}' in the first lines")
        exp_email = EMAIL.findall(src["contact"])
        add("email", 6, 1.0 if (emails and (not exp_email or exp_email[0].lower() in [e.lower() for e in emails])) else 0.0,
            ", ".join(emails) or "no email found")
    else:
        add("email", 6, 1.0 if emails else 0.0, ", ".join(emails) or "no email found")
    add("phone", 4, 1.0 if phones else 0.0, phones[0].strip() if phones else "no phone number found")

    found = {k: any(l.strip(" :") in v for l in lines) for k, v in SECTIONS.items()}
    add("standard section headings", 10, sum(found.values()) / len(found),
        "missing: " + ", ".join(k for k, v in found.items() if not v) if not all(found.values()) else "all found")

    if src and src["entries"]:
        hits, order_pos, in_order, missing = 0, -1, True, []
        for e in src["entries"]:
            ok = all(norm(p) in T for p in e["parts"])
            dates_ok = all(norm(d) in T for d in DATE.findall(e["dates"]) for d in [d[0]]) if e["dates"] else True
            if ok and dates_ok:
                hits += 1
                pos = T.find(norm(e["parts"][0]))
                if pos < order_pos: in_order = False
                order_pos = max(order_pos, pos)
            else:
                missing.append(e["raw"])
        add("titles, companies & dates", 20, hits / len(src["entries"]),
            ("missing/garbled: " + "; ".join(missing[:4])) if missing else f"{hits} entries intact")
    if src and src["sections"]:
        # where each expected section heading appears in the extracted text
        pos = []
        for sec in src["sections"]:
            idx = next((i for i, l in enumerate(lines) if l.strip(" :") == norm(sec)), None)
            if idx is not None: pos.append(idx)
        ordered = pos == sorted(pos) and (not src["entries"] or in_order)
        add("reading order", 12, 1.0 if ordered else 0.0,
            "sections and entries read top-to-bottom" if ordered else
            "sections/entries come out in a different order — typical of two-column, sidebar or text-box layouts")

    if src and src["bullets"]:
        intact = [b for b in src["bullets"] if norm(b)[:60] in T]
        add("bullets not scrambled", 12, len(intact) / len(src["bullets"]),
            f"{len(intact)}/{len(src['bullets'])} bullets read back cleanly")

    if src and src["skills"]:
        have = [s for s in src["skills"] if norm(s) in T]
        add("skills readable", 8, len(have) / len(src["skills"]),
            "missing: " + ", ".join(s for s in src["skills"] if s not in have)[:200] if len(have) < len(src["skills"]) else "all skills found")

    kws = [k.strip() for k in a.keywords.split(",") if k.strip()]
    if a.keywords_file:
        kws += [k.strip() for k in open(a.keywords_file, encoding="utf-8") if k.strip() and not k.startswith("#")]
    if kws:
        have = [k for k in kws if re.search(r"(?<![a-z0-9])" + re.escape(norm(k)) + r"(?![a-z0-9])", T)]
        miss = [k for k in kws if k not in have]
        add("JD keywords present", 12, len(have) / len(kws),
            f"{len(have)}/{len(kws)} present" + (f"; missing: {', '.join(miss)}" if miss else ""))

    bad = BAD_GLYPHS.findall(text)
    tables = text.count("[[TABLE]]"); hf = text.count("[[HEADER/FOOTER]]")
    add("no icons / odd glyphs / tables", 5, 0.0 if (len(bad) > 3 or tables) else 0.5 if (bad or hf) else 1.0,
        f"{len(bad)} odd glyphs, {tables} tables, {hf} header/footer lines")

    if pages is not None:
        add("page count", 3, 1.0 if pages <= a.max_pages else 0.0, f"{pages} page(s), limit {a.max_pages}")
    fn = os.path.basename(a.resume)
    size_mb = os.path.getsize(a.resume) / 1e6
    add("file name & size", 2, (1.0 if re.match(r"^[A-Za-z]+[_-][A-Za-z]+.*[Rr]esume|CV", fn) else 0.5) * (1.0 if size_mb < 2 else 0.0),
        f"{fn}, {size_mb:.2f} MB" + ("" if re.match(r"^[A-Za-z]+[_-][A-Za-z]+.*[Rr]esume|CV", fn) else " — prefer First_Last_Role_Resume.pdf"))

    total_w = sum(c["weight"] for c in checks)
    score = round(100 * sum(c["weight"] * c["score"] for c in checks) / total_w)
    critical_fail = [c["check"] for c in checks if c["check"] in CRITICAL and c["score"] < 0.5]
    if critical_fail:
        score = min(score, 60)  # an ATS that can't read name/email/order will mis-file you
    result = {"file": a.resume, "score": score, "pass": score >= a.min_score, "critical_failures": critical_fail, "pages": pages, "checks": checks,
              "extracted_preview": text[:600]}
    if a.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"ATS self-test: {score}/100 {'PASS' if result['pass'] else 'FAIL'}  ({fn})"
              + (f"  — critical: {', '.join(critical_fail)}" if critical_fail else ""))
        for c in checks:
            mark = "✓" if c["score"] >= 0.999 else "~" if c["score"] >= 0.5 else "✗"
            print(f"  {mark} {c['check']:<32} {c['detail']}")
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
