#!/usr/bin/env python3
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path('/home/user/Twin_Rebuild_Research_2026-11-01')
doc=Document(); sec=doc.sections[0]
sec.top_margin=Inches(.68);sec.bottom_margin=Inches(.68);sec.left_margin=Inches(.72);sec.right_margin=Inches(.72)
sec.header_distance=Inches(.29);sec.footer_distance=Inches(.30)
style=doc.styles['Normal'];style.font.name='Calibri';style.font.size=Pt(10.5);style.font.color.rgb=RGBColor.from_string('28384D')
style.paragraph_format.space_after=Pt(6);style.paragraph_format.line_spacing=1.12
for name,size,col in [('Title',28,'142943'),('Subtitle',12,'5B6F83'),('Heading 1',18,'16365D'),('Heading 2',13,'1F527A'),('Heading 3',11,'28705F')]:
 st=doc.styles[name];st.font.name='Calibri';st.font.size=Pt(size);st.font.bold=name!='Subtitle';st.font.color.rgb=RGBColor.from_string(col)
 st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(5)

head=sec.header.paragraphs[0];head.text='THE TWINS  /  RESEARCH & REBUILD PLAN';head.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for r in head.runs:r.font.name='Calibri';r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('6E8294')
foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=foot.add_run('Review copy  •  1 November 2026     |     ');r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('6E8294')
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)

def shade(cell,fill):
 tcPr=cell._tc.get_or_add_tcPr();shd=tcPr.find(qn('w:shd'))
 if shd is None:shd=OxmlElement('w:shd');tcPr.append(shd)
 shd.set(qn('w:fill'),fill)
def set_cell_margins(cell,top=80,start=90,bottom=80,end=90):
 tc=cell._tc.get_or_add_tcPr();mar=tc.first_child_found_in('w:tcMar')
 if mar is None:mar=OxmlElement('w:tcMar');tc.append(mar)
 for tag,val in [('top',top),('start',start),('bottom',bottom),('end',end)]:
  e=mar.find(qn('w:'+tag))
  if e is None:e=OxmlElement('w:'+tag);mar.append(e)
  e.set(qn('w:w'),str(val));e.set(qn('w:type'),'dxa')
def link(paragraph,text,url):
 part=paragraph.part;rid=part.relate_to(url,'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink',is_external=True)
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid); run=OxmlElement('w:r');pr=OxmlElement('w:rPr')
 color=OxmlElement('w:color');color.set(qn('w:val'),'17618D');pr.append(color);u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u);run.append(pr)
 t=OxmlElement('w:t');t.text=text;run.append(t);h.append(run);paragraph._p.append(h)
pattern=re.compile(r'(\*\*.*?\*\*|`[^`]+`|\[[^\]]+\]\(https?://[^)]+\)|(?<!\*)\*[^*\n]+\*(?!\*))')
def inline(p,s):
 pos=0
 for m in pattern.finditer(s):
  if m.start()>pos:p.add_run(s[pos:m.start()])
  val=m.group()
  if val.startswith('**'):
   rr=p.add_run(val[2:-2]);rr.bold=True
  elif val.startswith('`'):
   rr=p.add_run(val[1:-1]);rr.font.name='Consolas';rr.font.size=Pt(9)
  elif val.startswith('['):
   mm=re.match(r'\[([^\]]+)\]\(([^)]+)\)',val);link(p,mm.group(1),mm.group(2))
  else:rr=p.add_run(val[1:-1]);rr.italic=True
  pos=m.end()
 if pos<len(s):p.add_run(s[pos:])
def render_table(lines):
 data=[[x.strip() for x in line.strip().strip('|').split('|')] for line in lines]
 if len(data)>1 and all(re.fullmatch(r':?-{2,}:?',x) for x in data[1]):del data[1]
 n=max(map(len,data));tbl=doc.add_table(rows=0,cols=n);tbl.alignment=WD_TABLE_ALIGNMENT.CENTER;tbl.style='Table Grid';tbl.autofit=True
 for ri,vals in enumerate(data):
  cells=tbl.add_row().cells
  trPr=tbl.rows[-1]._tr.get_or_add_trPr();cannot=OxmlElement('w:cantSplit');trPr.append(cannot)
  if ri==0:
   repeat=OxmlElement('w:tblHeader');repeat.set(qn('w:val'),'true');trPr.append(repeat)
  for i,c in enumerate(cells):
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP;set_cell_margins(c)
   p=c.paragraphs[0];p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.05
   if i<len(vals):inline(p,vals[i])
   if ri==0:
    shade(c,'1B395A')
    for run in p.runs:run.font.bold=True;run.font.color.rgb=RGBColor(255,255,255);run.font.size=Pt(9)
   else:
    if ri%2==0:shade(c,'EEF3F8')
    for run in p.runs:run.font.size=Pt(9)
 doc.add_paragraph().paragraph_format.space_after=Pt(2)

def convert(path):
 lines=path.read_text(encoding='utf8').splitlines();i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line.startswith('|'):
   batch=[]
   while i<len(lines) and lines[i].strip().startswith('|'):batch.append(lines[i]);i+=1
   render_table(batch);continue
  m=re.match(r'^(#{1,3})\s+(.*)$',line)
  if m:
   lvl=len(m.group(1));p=doc.add_paragraph(style=f'Heading {lvl}');inline(p,m.group(2));i+=1;continue
  if line.startswith('- '):
   p=doc.add_paragraph(style='List Bullet');p.paragraph_format.space_after=Pt(3);inline(p,line[2:]);i+=1;continue
  m=re.match(r'^\d+\.\s+(.*)',line)
  if m:
   p=doc.add_paragraph(style='List Number');p.paragraph_format.space_after=Pt(5);inline(p,m.group(1));i+=1;continue
  p=doc.add_paragraph();inline(p,line);i+=1

p=doc.add_paragraph();p.paragraph_format.space_before=Pt(38)
r=p.add_run('DRAGON BALL  /  THE TWINS');r.font.name='Calibri';r.font.size=Pt(10);r.bold=True;r.font.color.rgb=RGBColor.from_string('28705F')
p=doc.add_paragraph(style='Title');p.add_run('Research &\nRebuild Plan')
p=doc.add_paragraph(style='Subtitle');p.add_run('A source-first review of the existing story and a proposal for getting it back on track')
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(18)
r=p.add_run('FOR YOUR REVIEW  •  1 NOVEMBER 2026');r.bold=True;r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('1F527A')
tbl=doc.add_table(rows=2,cols=1);tbl.style='Table Grid';tbl.alignment=WD_TABLE_ALIGNMENT.LEFT
for idx,(text,bg) in enumerate([('CHAPTER TEN IS REJECTED. Its authored additions are not accepted continuity.','FCEBE8'),('NO STORY FILES CHANGED. A separate draft requires your approval.','E9F4ED')]):
 c=tbl.cell(idx,0);shade(c,bg);set_cell_margins(c,120,130,120,130);p=c.paragraphs[0];p.paragraph_format.space_after=Pt(0);rr=p.add_run(text);rr.bold=True;rr.font.size=Pt(10);rr.font.color.rgb=RGBColor.from_string('70382D' if idx==0 else '225744')
p=doc.add_paragraph();p.paragraph_format.space_before=Pt(12)
p.add_run('Inside: ').bold=True;p.add_run('the proposed approach, rules to preserve, review gates, and a chapter-by-chapter audit. The companion source comparison and film map are separate files.')
doc.add_page_break();convert(root/'01_REBUILD_PROPOSAL.md');doc.add_page_break();convert(root/'02_CHAPTER_BY_CHAPTER_AUDIT.md')
out=root/'00_REBUILD_PLAN_AND_AUDIT.docx';doc.save(out)
reopen=Document(out);print('Wrote',out,'paragraphs',len(reopen.paragraphs),'tables',len(reopen.tables))
assert len(reopen.paragraphs)>80 and len(reopen.tables)>=3
