#!/usr/bin/env python3
"""Render a resume.md (structure in skills/tailor-resume/references/ats-rules.md)
into an ATS-friendly single-column resume.docx, and optionally resume.pdf.

Usage: render_resume.py path/to/resume.md [--pdf] [--out NAME] [--template classic|modern|compact]

Templates (all single-column, ATS-safe):
  classic  centred name, navy section rules (default)
  modern   left-aligned name, accent colour, tighter headings
  compact  smaller type and margins to fit dense one-page resumes
Requires: python-docx  (pip install python-docx). PDF needs LibreOffice (soffice).
"""
import argparse, os, re, shutil, subprocess, sys

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, Inches, RGBColor
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    sys.exit("python-docx missing: pip install python-docx")

FONT = "Calibri"
TEMPLATES = {
    "classic": dict(font="Calibri", body=10.5, name=18, head=11.5, margin=0.6, side=0.7,
                    align="center", accent=(0x1F, 0x3A, 0x5F), upper=True, rule=True),
    "modern":  dict(font="Arial", body=10, name=20, head=11, margin=0.55, side=0.65,
                    align="left", accent=(0x0E, 0x7C, 0x86), upper=False, rule=True),
    "compact": dict(font="Calibri", body=9.5, name=15, head=10.5, margin=0.45, side=0.55,
                    align="center", accent=(0x33, 0x33, 0x33), upper=True, rule=True),
}
T = TEMPLATES["classic"]


def add_runs(p, text, size=None, bold=False):
    size = size or T["body"]
    # supports **bold** segments
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not part:
            continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1)
        r.font.size = Pt(size)
        r.font.name = T["font"]


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in {"w:val": "single", "w:sz": "6", "w:space": "1", "w:color": "444444"}.items():
        b.set(qn(k), v)
    bdr.append(b)
    pPr.append(bdr)


def spacing(p, before=0, after=2):
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)


def render(md_path, out_base, template="classic"):
    global T
    T = TEMPLATES[template]
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(T["margin"])
        s.left_margin = s.right_margin = Inches(T["side"])
    st = doc.styles["Normal"]
    st.font.name = T["font"]
    st.font.size = Pt(T["body"])
    st.element.rPr.rFonts.set(qn("w:eastAsia"), T["font"])
    center = WD_ALIGN_PARAGRAPH.CENTER if T["align"] == "center" else WD_ALIGN_PARAGRAPH.LEFT

    lines = open(md_path, encoding="utf-8").read().splitlines()
    after_name = False
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(); spacing(p, 0, 0)
            p.alignment = center
            add_runs(p, line[2:].strip(), size=T["name"], bold=True)
            after_name = True
            continue
        if after_name and not line.startswith("#"):
            p = doc.add_paragraph(); spacing(p, 0, 6)
            p.alignment = center
            add_runs(p, line.strip().replace(" · ", "  |  "), size=T["body"] - 0.5)
            after_name = False
            continue
        after_name = False
        if line.startswith("## "):
            p = doc.add_paragraph(); spacing(p, 8, 3)
            title = line[3:].strip()
            r = p.add_run(title.upper() if T["upper"] else title)
            r.bold = True; r.font.size = Pt(T["head"]); r.font.name = T["font"]
            r.font.color.rgb = RGBColor(*T["accent"])
            if T["rule"]:
                bottom_border(p)
        elif line.startswith("### "):
            text = line[4:].strip()
            left, _, right = text.rpartition("|") if "|" in text else (text, "", "")
            p = doc.add_paragraph(); spacing(p, 4, 1)
            add_runs(p, left.strip(), bold=True)
            if right:
                p.paragraph_format.tab_stops.add_tab_stop(Inches(8.5 - 2 * T["side"]), alignment=2)
                r = p.add_run("\t" + right.strip()); r.font.size = Pt(T["body"] - 0.5); r.font.name = T["font"]; r.italic = True
        elif re.match(r"^\s*[-*] ", line):
            # plain "•" + hanging indent: ATS-safe (Word's list bullets use a Symbol-font glyph)
            p = doc.add_paragraph(); spacing(p, 0, 1)
            p.paragraph_format.left_indent = Inches(0.22)
            p.paragraph_format.first_line_indent = Inches(-0.16)
            add_runs(p, "\u2022 " + re.sub(r"^\s*[-*] ", "", line))
        else:
            p = doc.add_paragraph(); spacing(p, 0, 2)
            add_runs(p, line.strip())

    docx_path = out_base + ".docx"
    doc.save(docx_path)
    return docx_path


def to_pdf(docx_path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        print("LibreOffice not found — skipped PDF (export resume.docx to PDF from Word/Google Docs).")
        return None
    outdir = os.path.dirname(os.path.abspath(docx_path))
    subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.splitext(docx_path)[0] + ".pdf"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--template", default="classic", choices=list(TEMPLATES))
    ap.add_argument("--out", help="output base name without extension (default: next to the .md)")
    a = ap.parse_args()
    base = a.out or os.path.splitext(a.md)[0]
    d = render(a.md, base, a.template)
    print("Wrote", d)
    if a.pdf:
        p = to_pdf(d)
        if p:
            print("Wrote", p)
