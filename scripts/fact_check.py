#!/usr/bin/env python3
"""Fact check: every number, skill, employer, job title and credential in a tailored
resume.md must be traceable to the master profile.md. Catches invented content.

Usage: fact_check.py resume.md --profile profile.md [--json]
Exit 1 if anything unsupported is found.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TERMS_FILE = os.path.join(HERE, "known_terms.txt")
CREDENTIALS = re.compile(r"\b(PMP|CIPS|CPSM|CSCP|MBA|M\.?Tech|M\.?Sc|Ph\.?D|Master'?s|AWS Certified[\w\s-]*|Six Sigma \w+ Belt|CFA|ACCA|CPA|Scrum Master|PRINCE2|ITIL)\b", re.I)
NUM = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)*)(\s?%|\s?x\b|\s?k\b|\+|\s?m\b|\s?lakh|\s?cr)?", re.I)


def norm(s):
    s = (s or "").replace("–", "-").replace("—", "-").replace(" ", " ")
    s = re.sub(r"\*\*|__|`", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def numbers(text):
    out = set()
    for m in NUM.finditer(text):
        n = m.group(1).replace(",", "")
        out.add(n)
    return out


def stem(w):
    if len(w) > 5 and (w.endswith("sis") or w.endswith("ses")):  # analysis / analyses
        return w[:-2]
    for suf in ("ies", "es", "s", "ing", "ed"):
        if len(w) > 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def supported(phrase, P):
    """Exact phrase in profile, or every meaningful word of it (stemmed) appears in the profile."""
    n = norm(phrase)
    if n in P: return True
    words = [stem(w) for w in re.findall(r"[a-z0-9+#./]+", n) if len(w) > 2 and w not in ("and", "the", "for", "with")]
    pw = {stem(w) for w in re.findall(r"[a-z0-9+#./]+", P)}
    return bool(words) and all(w in pw for w in words)


def load_terms():
    if not os.path.exists(TERMS_FILE): return []
    return [t.strip() for t in open(TERMS_FILE, encoding="utf-8") if t.strip() and not t.startswith("#")]


def term_in(term, text):
    return re.search(r"(?<![a-z0-9])" + re.escape(term.lower()) + r"(?![a-z0-9])", text) is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("resume")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    R_raw, P_raw = open(a.resume, encoding="utf-8").read(), open(a.profile, encoding="utf-8").read()
    R, P = norm(R_raw), norm(P_raw)
    issues = []

    # 1. numbers (metrics, years, counts). Contact line excluded from check except it must match too.
    p_nums = numbers(P_raw)
    body_lines, after_name = [], False
    for line in R_raw.splitlines():  # skip the contact line (2nd line) — not a claim
        if line.startswith("# "): after_name = True; continue
        if after_name and line.strip() and not line.startswith("#"): after_name = False; continue
        body_lines.append(line)
    for line in body_lines:
        for n in numbers(line):
            if n not in p_nums and not (len(n) >= 7 and n in re.sub(r"\D", "", P_raw)):  # phone fragments
                issues.append({"type": "number", "value": n, "line": line.strip()[:140]})

    # 2. headings: employers, titles, schools, projects
    for line in R_raw.splitlines():
        if line.startswith("### "):
            head = line[4:]
            left = head.split("|")[0]
            for part in re.split(r"\s+[—–-]\s+|,|\(", left):
                part = part.strip(" )")
                if len(part) > 2 and not supported(part, P):
                    issues.append({"type": "heading", "value": part, "line": line.strip()[:140]})

    # 3. skills section items
    sec = None
    for line in R_raw.splitlines():
        if line.startswith("## "): sec = line[3:].lower(); continue
        if sec and "skill" in sec and line.strip() and not line.startswith("#"):
            body = re.sub(r"^\s*[-*]?\s*\*\*[^*]+:\*\*", "", line)
            for item in re.split(r"[,;·]", body):
                item = re.sub(r"\(.*?\)", "", item).strip(" .")
                if item and not supported(item, P):
                    issues.append({"type": "skill", "value": item, "line": line.strip()[:140]})

    # 4. known technology / tool terms anywhere in the resume
    # case-sensitive in the resume (proper nouns: "Combine" the framework, not "combine" the verb)
    for t in load_terms():
        found = re.search(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", R_raw)
        if found and not term_in(t, P):
            issues.append({"type": "term", "value": t, "line": ""})

    # 5. credentials / degrees
    for m in set(x.group(0) for x in CREDENTIALS.finditer(R_raw)):
        if norm(m) not in P:
            issues.append({"type": "credential", "value": m, "line": ""})

    # de-duplicate
    seen, uniq = set(), []
    for i in issues:
        k = (i["type"], i["value"].lower())
        if k not in seen: seen.add(k); uniq.append(i)

    if a.json:
        print(json.dumps({"ok": not uniq, "unsupported": uniq}, indent=2, ensure_ascii=False))
    else:
        if not uniq:
            print("Fact check: OK — everything traces to the profile")
        else:
            print(f"Fact check: {len(uniq)} unsupported item(s) — remove, or confirm with the user and add to profile.md")
            for i in uniq:
                print(f"  ✗ {i['type']:<10} {i['value']}" + (f"   ← {i['line']}" if i["line"] else ""))
    sys.exit(0 if not uniq else 1)


if __name__ == "__main__":
    main()
