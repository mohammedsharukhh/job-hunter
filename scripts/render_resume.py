#!/usr/bin/env python3
"""Render a resume.md (structure in skills/tailor-resume/references/ats-rules.md)
into an ATS-friendly single-column resume.docx, and optionally resume.pdf.

Usage: render_resume.py path/to/resume.md [--pdf] [--out NAME]
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


def add_runs(p, text, size=10.5, bold=False):
    # supports **bold** segments
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not part:
            continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1)
        r.font.size = Pt(size)
        r.font.name = FONT


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


def render(md_path, out_base):
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(0.6)
        s.left_margin = s.right_margin = Inches(0.7)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    lines = open(md_path, encoding="utf-8").read().splitlines()
    after_name = False
    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("# "):
            p = doc.add_paragraph(); spacing(p, 0, 0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, line[2:].strip(), size=18, bold=True)
            after_name = True
            continue
        if after_name and not line.startswith("#"):
            p = doc.add_paragraph(); spacing(p, 0, 6)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, line.strip().replace(" · ", "  |  "), size=10)
            after_name = False
            continue
        after_name = False
        if line.startswith("## "):
            p = doc.add_paragraph(); spacing(p, 8, 3)
            r = p.add_run(line[3:].strip().upper())
            r.bold = True; r.font.size = Pt(11.5); r.font.name = FONT
            r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
            bottom_border(p)
        elif line.startswith("### "):
            text = line[4:].strip()
            left, _, right = text.rpartition("|") if "|" in text else (text, "", "")
            p = doc.add_paragraph(); spacing(p, 4, 1)
            add_runs(p, left.strip(), size=10.5, bold=True)
            if right:
                p.paragraph_format.tab_stops.add_tab_stop(Inches(7.1), alignment=2)
                r = p.add_run("\t" + right.strip()); r.font.size = Pt(10); r.font.name = FONT; r.italic = True
        elif re.match(r"^\s*[-*] ", line):
            p = doc.add_paragraph(style="List Bullet"); spacing(p, 0, 1)
            add_runs(p, re.sub(r"^\s*[-*] ", "", line))
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
    ap.add_argument("--out", help="output base name without extension (default: next to the .md)")
    a = ap.parse_args()
    base = a.out or os.path.splitext(a.md)[0]
    d = render(a.md, base)
    print("Wrote", d)
    if a.pdf:
        p = to_pdf(d)
        if p:
            print("Wrote", p)
