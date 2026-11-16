import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def md_to_docx(md_path: str, docx_path: str):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    doc = Document()

    # Configure Margins: 1 inch (2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base Normal Style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 41, 59) # Slate 800

    i = 0
    in_code_block = False
    in_table = False
    table_lines = []

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        # Filter markdown table rows
        rows = [r.strip() for r in tbl_lines if r.strip().startswith("|") and not re.match(r"^\|(\s*[-:]+[-|\s:]*)\|?$", r.strip())]
        if not rows:
            return
        
        parsed_rows = []
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            parsed_rows.append(cells)
            
        num_cols = max(len(r) for r in parsed_rows)
        tbl = doc.add_table(rows=len(parsed_rows), cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        for r_idx, row_data in enumerate(parsed_rows):
            for c_idx, cell_value in enumerate(row_data):
                if c_idx < num_cols:
                    cell = tbl.cell(r_idx, c_idx)
                    cell.text = cell_value
                    # Format header
                    if r_idx == 0:
                        shading_elm = parse_xml(r'<w:shd {} w:fill="F1F5F9"/>'.format(nsdecls('w')))
                        cell._tc.get_or_add_tcPr().append(shading_elm)
                        for p in cell.paragraphs:
                            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            for run in p.runs:
                                run.bold = True
                                run.font.size = Pt(9.5)
                                run.font.color.rgb = RGBColor(15, 23, 42)
                    else:
                        for p in cell.paragraphs:
                            for run in p.runs:
                                run.font.size = Pt(9.5)
        doc.add_paragraph() # Spacing

    while i < len(lines):
        line = lines[i].rstrip("\r\n")

        # Code blocks
        if line.startswith("```"):
            if in_table:
                flush_table(table_lines)
                table_lines = []
                in_table = False
            in_code_block = not in_code_block
            i += 1
            continue

        if in_code_block:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(line)
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(51, 65, 85)
            i += 1
            continue

        # Markdown tables
        if line.strip().startswith("|"):
            in_table = True
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            flush_table(table_lines)
            table_lines = []
            in_table = False

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Headers
        if line.startswith("# "):
            h = doc.add_heading(line[2:].strip(), level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(8)
            for r in h.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(18)
                r.font.bold = True
                r.font.color.rgb = RGBColor(15, 23, 42)
        elif line.startswith("## "):
            h = doc.add_heading(line[3:].strip(), level=2)
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(6)
            for r in h.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(14)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 41, 59)
        elif line.startswith("### "):
            h = doc.add_heading(line[4:].strip(), level=3)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(4)
            for r in h.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(71, 85, 105)
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            text = line[2:].strip()
            # Clean basic bold
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.bold = True
                else:
                    p.add_run(part)
        elif re.match(r"^\d+\.\s", line):
            m = re.match(r"^(\d+\.\s)(.*)", line)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(3)
            text = m.group(2).strip()
            parts = re.split(r'(\*\*.*?\*\*)', text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.bold = True
                else:
                    p.add_run(part)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.bold = True
                else:
                    p.add_run(part)

        i += 1

    if in_table:
        flush_table(table_lines)

    doc.save(docx_path)
    print(f"Word document saved successfully: {docx_path}")

if __name__ == "__main__":
    md_file = os.path.abspath("docs/ARTICULO_CIENTIFICO_INV02_ACTUALIZADO.md")
    docx_file = os.path.abspath("docs/ARTICULO_CIENTIFICO_INV02_ACTUALIZADO.docx")
    md_to_docx(md_file, docx_file)
