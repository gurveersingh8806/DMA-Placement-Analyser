from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

out=Path('outputs/college_placement_insights_report.docx')
doc=Document()
sec=doc.sections[0]
sec.top_margin=Inches(0.62); sec.bottom_margin=Inches(0.62); sec.left_margin=Inches(0.72); sec.right_margin=Inches(0.72)

# Global typography
styles=doc.styles
for sty_name in ['Normal','Title','Heading 1','Heading 2']:
    sty=styles[sty_name]
    sty.font.name='Arial'
    sty._element.rPr.rFonts.set(qn('w:ascii'),'Arial')
    sty._element.rPr.rFonts.set(qn('w:hAnsi'),'Arial')
styles['Normal'].font.size=Pt(10.2)
styles['Normal'].font.color.rgb=RGBColor(40,48,56)
styles['Normal'].paragraph_format.space_after=Pt(5)
styles['Normal'].paragraph_format.line_spacing=1.04
styles['Title'].font.size=Pt(20)
styles['Title'].font.bold=True
styles['Title'].font.color.rgb=RGBColor(27,57,82)
styles['Title'].paragraph_format.space_after=Pt(3)
styles['Heading 1'].font.size=Pt(13)
styles['Heading 1'].font.bold=True
styles['Heading 1'].font.color.rgb=RGBColor(27,82,94)
styles['Heading 1'].paragraph_format.space_before=Pt(8)
styles['Heading 1'].paragraph_format.space_after=Pt(3)
styles['Heading 2'].font.size=Pt(11)
styles['Heading 2'].font.bold=True
styles['Heading 2'].font.color.rgb=RGBColor(27,82,94)
styles['Heading 2'].paragraph_format.space_before=Pt(6)
styles['Heading 2'].paragraph_format.space_after=Pt(2)

# Helper: compact, editable shaded tables
def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr()
    shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def set_cell(cell, text, bold=False, color=(40,48,56), size=9.2):
    cell.text=''
    p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(0); p.paragraph_format.space_before=Pt(0)
    r=p.add_run(str(text)); r.bold=bold; r.font.name='Arial'; r.font.size=Pt(size); r.font.color.rgb=RGBColor(*color)
    r._element.rPr.rFonts.set(qn('w:ascii'),'Arial'); r._element.rPr.rFonts.set(qn('w:hAnsi'),'Arial')
    cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER

def set_repeat_table(table):
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    table.autofit=True

def add_bullet(text):
    p=doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent=Inches(0.22); p.paragraph_format.first_line_indent=Inches(-0.13)
    p.paragraph_format.space_after=Pt(2); p.paragraph_format.line_spacing=1.0
    p.add_run(text)
    return p

# Page one
t=doc.add_paragraph(style='Title'); t.alignment=WD_ALIGN_PARAGRAPH.CENTER
t.add_run('College Placement Insights')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(6)
r=p.add_run('Gurveer Singh (Roll No. 24103054)  |  Harpreet Singh (Roll No. 24103056)\nGroup 5A G2')
r.bold=True; r.font.name='Arial'; r.font.size=Pt(9.7); r.font.color.rgb=RGBColor(75,84,92)

p=doc.add_paragraph()
p.add_run('Project summary. ').bold=True
p.add_run('We surveyed 70 students about placement preparation, technical-skill confidence, internship experience, placement confidence, and expected salary. The clearest pattern is that students who reported preparing more regularly also tended to report higher confidence. This describes the survey respondents; it does not show that preparation caused placement success.')

doc.add_heading('Aim and survey method', level=1)
doc.add_paragraph('The project asks what students expect from placements and how their self-reported readiness relates to their confidence about getting a suitable placement. We collected responses through an online form. The analysis uses the original 70 responses only; the extra generated rows in the separate demo file are not included in these findings.')
doc.add_paragraph('The form asked students to rate technical-skill confidence, placement-preparation regularity, and placement confidence on a 1-to-5 scale. It also asked about year of study, broad branch, CGPA range, internship or substantial project experience, and expected salary range.')

doc.add_heading('Survey results', level=1)
doc.add_paragraph('The average technical-skill confidence was 3.03 out of 5. Average preparation regularity was 2.91, while average placement confidence was 3.37. These averages are near the middle of the scale, with placement confidence somewhat higher than reported preparation.')

# Small scores table
tab=doc.add_table(rows=1, cols=3); tab.style='Table Grid'; set_repeat_table(tab)
for c,txt in zip(tab.rows[0].cells,['Rating','Average','Scale']): set_cell(c,txt,True,(255,255,255),9); shade(c,'1B5260')
for vals in [('Technical-skill confidence','3.03','1–5'),('Preparation regularity','2.91','1–5'),('Placement confidence','3.37','1–5')]:
    cells=tab.add_row().cells
    for c,txt in zip(cells,vals): set_cell(c,txt,size=9)

doc.add_paragraph()
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(3)
p.add_run('Who answered. ').bold=True
p.add_run('There were 34 third-year students, 28 final-year students, and 8 second-year students. Internship or substantial project experience was reported by 34 respondents; 36 reported no such experience.')
p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(3)
p.add_run('Salary expectations. ').bold=True
p.add_run('The most common answer was “12+” (23 students, 32.9%). Nineteen students (27.1%) selected “5–8 LPA,” 14 (20.0%) selected “8–12 LPA,” 8 (11.4%) selected “3–5 LPA,” and 6 (8.6%) were unsure or preferred not to say. These are expectations, not salaries received.')

# Page two
doc.add_page_break()
doc.add_heading('Data-mining pattern', level=1)
doc.add_paragraph('We grouped preparation ratings 4–5 as high and confidence ratings 4–5 as high. Among the 21 students in the high-preparation group, 19 also reported high placement confidence (90.5%). Among the 49 students who rated preparation 1–3, 16 reported high confidence (32.7%).')

# Comparison table
tab2=doc.add_table(rows=1, cols=4); tab2.style='Table Grid'; set_repeat_table(tab2)
for c,txt in zip(tab2.rows[0].cells,['Preparation group','Respondents','High confidence','Share']): set_cell(c,txt,True,(255,255,255),9); shade(c,'1B5260')
for vals in [('High (4–5)','21','19','90.5%'),('Low or medium (1–3)','49','16','32.7%')]:
    cells=tab2.add_row().cells
    for c,txt in zip(cells,vals): set_cell(c,txt,size=9)

doc.add_paragraph('This is a recurring association in the responses. In association-rule terms, the pattern “high preparation → high confidence” appeared in 19 of 70 responses (support 27.1%). Among high-preparation respondents, 90.5% reported high confidence (rule confidence). The lift was 1.81, meaning high confidence appeared more often in this group than in the full survey. The result is not evidence of cause and effect.')

doc.add_heading('R Shiny app and prediction', level=1)
doc.add_paragraph('We built an R Shiny app to load the Google Forms CSV, show averages and salary ranges, find recurring answer combinations, and estimate the chance that a similar profile would report high placement confidence. The logistic-regression model uses preparation rating, technical-skill confidence, and internship experience. The app also compares model accuracy with a simple baseline when the response count is large enough.')
doc.add_paragraph('The prediction target is a confidence rating of 4 or 5. The survey does not record actual job offers or placements, so this model cannot predict whether a student will actually be hired. Predictions should be treated as exploratory, especially with a small convenience sample.')

doc.add_heading('Conclusion and limits', level=1)
doc.add_paragraph('In this survey, higher preparation ratings appeared alongside higher placement-confidence ratings. The group can present this as a pattern among its 70 respondents and use the app to explore the answers. The survey was self-reported and included more third- and final-year students than second-year students. It did not measure actual placement outcomes or ask which support students wanted most. Therefore, the results should not be described as official placement statistics or as proof that preparation causes placement success.')

# Compact footer
for section in doc.sections:
    footer=section.footer.paragraphs[0]
    footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_before=Pt(0); footer.paragraph_format.space_after=Pt(0)
    rr=footer.add_run('Data Mining Mini Project  |  Group 5A G2')
    rr.font.name='Arial'; rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(110,118,124)

doc.save(out)
print(out.resolve())
