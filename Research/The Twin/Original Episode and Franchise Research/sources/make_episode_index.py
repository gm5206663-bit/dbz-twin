#!/usr/bin/env python3
"""Create a navigational source index only. No project writes, no story changes.
English title glosses are machine translations, not official/localized titles.
"""
from pathlib import Path
import json,re,requests,concurrent.futures,time
from collections import Counter
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table,TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation

ROOT=Path('/home/user/Twin_Rebuild_Research_2026-11-01')
with open(ROOT/'sources/toei_saiyan_ep_001_035_official_synopses.json',encoding='utf8') as f: first=json.load(f)['episodes']
with open(ROOT/'sources/toei_franchise_official_synopses.jsonl',encoding='utf8') as f: other=[json.loads(s) for s in f]
rows=[]
for r in first:
 rows.append(dict(series='Dragon Ball Z', ep=r['episode'], title=r['official_title_ja'], url=r['url'], status='Official synopsis read in this audit', second=''))
for r in other:
 s,e,st=r['series'],r['episode'],r['status']; title=r.get('title_ja',''); url=r['url']; second=''
 if st.startswith('official synopsis'): status=('Official combined 109–110 synopsis inspected; no footage' if s=='Dragon Ball Super (2015)' and e==109 else 'Official synopsis indexed; not individually reviewed this pass')
 elif s=='Dragon Ball Z' and e in (189,209):
  title={189:'第 189 話 白昼の悪夢!!恐怖はより完璧に',209:'第 209 話 危うしサイヤマン! 激写に御用心!?'}[e]
  status='Official title/still only; synopsis absent; secondary guide linked'
  second=f'https://www.kanzenshuu.com/episode/dbz/eps-{e:03d}/'
 elif s=='Dragon Ball Super (2015)' and e==110:
  title='第 110 話 孫悟空覚醒！目覚めし者の新たなる極意！！'
  url='https://lineup.toei-anim.co.jp/ja/tv/dragon_super/episode/109/'
  status='Toei 109 page combines 109 and 110; title from secondary 110 guide'
  second='https://www.kanzenshuu.com/wiki/Dragon_Ball_Super_Episode_110'
 else: status='No parsed synopsis; inspect the linked source'
 rows.append(dict(series=s,ep=e,title=title,url=url,status=status,second=second))

daima=['インボウ','グロリオ','ダイマ','オシャベリ','パンジ','イナヅマ','クビワ','タマガミ','トウゾク','ウナバラ','デンセツ','ソコヂカラ','サプライズ','タブー','サードアイ','デゲス','ゴマー','メザメ','ウラギリ','ゼンカイ']
gloss=['Conspiracy','Glorio','Daima','Chatty','Panzy','Lightning','Collar','Tamagami','Thieves','Ocean','Legend','Inner strength','Surprise','Taboo','Third eye','Degesu','Gomah','Awakening','Betrayal','All out']
for i,t in enumerate(daima,1):
 rows.append(dict(series='Dragon Ball DAIMA',ep=i,title=f'第 {i} 話 {t}',url=f'https://www.videx.jp/detail/anime/v_a_toeianimation/atoa0483_{i:04d}/index.htm',status='Distributor short listing reviewed; no footage',second='',manual_gloss=gloss[i-1]))
order={'Dragon Ball':0,'Dragon Ball Z':1,'Dragon Ball GT':2,'Dragon Ball Super (2015)':3,'Dragon Ball DAIMA':4}
rows.sort(key=lambda r:(order[r['series']],r['ep']))
assert Counter(r['series'] for r in rows)=={'Dragon Ball':153,'Dragon Ball Z':291,'Dragon Ball GT':64,'Dragon Ball Super (2015)':131,'Dragon Ball DAIMA':20}
assert len({(r['series'],r['ep']) for r in rows})==659

# Public source title texts, batched with stable per-batch IDs; no proprietary user data sent.
def xlate(batch):
 text='\n'.join(f'{i:03d} | '+re.sub(r'^第\s*\d+\s*話\s*','',r['title']).replace('\n',' ') for i,r in enumerate(batch,1))
 for attempt in range(3):
  try:
   resp=requests.get('https://translate.googleapis.com/translate_a/single',params={'client':'gtx','sl':'ja','tl':'en','dt':'t','q':text},timeout=40)
   resp.raise_for_status(); out=''.join(seg[0] or '' for seg in resp.json()[0]);
   vals={}
   for line in out.splitlines():
    m=re.match(r'^\s*(\d{1,3})\s*[|｜:]\s*(.*)$',line)
    if m: vals[int(m.group(1))]=m.group(2).strip()
   if len(vals)!=len(batch) or any(i not in vals for i in range(1,len(batch)+1)):
    raise ValueError('Batch marker mismatch; refusing misalignment')
   return [vals[i] for i in range(1,len(batch)+1)]
  except Exception as e:
   if attempt==2: return ['[Translation unavailable; use Japanese title/source]']*len(batch)
   time.sleep(1.0*(attempt+1))

translate_rows=[r for r in rows if 'manual_gloss' not in r]
batches=[translate_rows[i:i+20] for i in range(0,len(translate_rows),20)]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for b,translated in zip(batches,ex.map(xlate,batches)):
  for r,t in zip(b,translated):r['english']=t
for r in rows:
 if 'manual_gloss' in r:r['english']=r['manual_gloss']
# Correct especially misleading machine translations in the immediate review range.
manual_z={
 1: "Mini Goku is a pampered boy! I'm Gohan",
 6: "A battle in the afterlife! Even King Yemma is surprised",
 9: "Sorry, Mr. Robot: tears vanish in the desert",
 10: "Don't cry, Gohan! His first battle",
 13: "Don't touch it! King Yemma's secret fruit",
 16: "Run, Gohan! Chi-Chi awaits at beloved Mount Paozu",
 23: "Yamcha dies! The terrifying Saibaman",
 24: "Farewell, Tien! Chiaotzu's desperate strategy",
 25: "Tien cries out! The final Tri-Beam",
 26: "Three hours to wait! Nimbus in a rush",
 28: "The Saiyans' fury! Kami and Piccolo both die",
 31: "Hang in there, Goku! One final, all-or-nothing move",
}
for r in rows:
 if r['series']=='Dragon Ball Z' and r['ep'] in manual_z:r['english']=manual_z[r['ep']]
missing=sum(r['english'].startswith('[Translation unavailable') for r in rows)
print('Title gloss translations unavailable:',missing)

historical=set(json.load(open('/home/user/dbz-twin/canon/episodes.json',encoding='utf8'))['full_spoken_caption_reads'])
wb=Workbook(); ws=wb.active; ws.title='START HERE'
NAVY='162A47'; BLUE='264F78'; GOLD='F6B847'; LIGHT='EAF1F8'; SOFT='FFF3D4'; WHITE='FFFFFF'; GRAY='44546A'; GREEN='E6F4EA'; RED='FBE5E3'
ws.sheet_view.showGridLines=False
ws.merge_cells('A1:F1'); ws['A1']='DRAGON BALL TWIN PROJECT | RESEARCH INDEX';ws['A1'].font=Font(name='Calibri',size=18,bold=True,color=WHITE);ws['A1'].fill=PatternFill('solid',fgColor=NAVY);ws['A1'].alignment=Alignment(vertical='center');ws.row_dimensions[1].height=32
info=[
 ('Purpose','Navigation and source-status tracking, not a story draft or approval.'),
 ('Coverage','659 episode entries: original Dragon Ball 153, Z 291, GT 64, Super (2015–2018) 131, and DAIMA 20. 21 film entries are on the Films tab.'),
 ('What was read','This audit read Toei’s short Z 1–35 synopses, reread the local Japanese SRTs for Z 9–10, and read the DAIMA distributor listings. It did not watch full episodes or films.'),
 ('What was indexed','636 individual Toei synopsis pages were extracted automatically across the first four series. Most were NOT individually read in this audit. DAIMA listings are separate.'),
 ('Source exceptions','Z 189/209: official title and still only, no synopsis visible. Super 110: Toei 109 page is a combined 109–110 listing; separate title is from a secondary guide.'),
 ('English titles','English title hints are mainly machine translations, with a few immediate Z and DAIMA entries hand-glossed. None is an official or fully verified localization; names and meanings can be wrong.'),
 ('Captions','The historical project records a full spoken-caption read for particular Z episodes. Their SRT provenance and cut remain unverified. A caption is not footage.'),
 ('Decisions','Every movie decision remains PENDING. Editing this workbook does not change the story. Ask the user before adopting any decision in the project.'),
 ('Order','The ordering here is a source catalogue, not a proposed in-universe chronology or a decision that GT, DAIMA, films and Super all fit unchanged.'),
 ('Next step','Read 01_REBUILD_PROPOSAL.md and the detailed comparison and provenance files. The living project and backups are unchanged.'),
]
for n,(a,b) in enumerate(info,3):
 ws.cell(n,1,a);ws.cell(n,1).font=Font(bold=True,color=BLUE,size=11)
 ws.merge_cells(start_row=n,start_column=2,end_row=n,end_column=6); c=ws.cell(n,2,b);c.alignment=Alignment(wrap_text=True,vertical='top');c.font=Font(color=GRAY,size=11);ws.row_dimensions[n].height=34 if len(b)>100 else 27
 if n%2==1:
  for col in range(1,7):ws.cell(n,col).fill=PatternFill('solid',fgColor=LIGHT)
ws.column_dimensions['A'].width=24
for col in 'BCDEF':ws.column_dimensions[col].width=21
ws.freeze_panes='B3';ws.print_options.horizontalCentered=True

ws=wb.create_sheet('Episodes');ws.sheet_view.showGridLines=False
headers=['Series','Episode','Japanese title (source)','English title hint (unverified)','Source / synopsis status','Caption history','Primary page','Secondary exception']
ws.append(headers)
for c in ws[1]:c.fill=PatternFill('solid',fgColor=NAVY);c.font=Font(bold=True,color=WHITE);c.alignment=Alignment(wrap_text=True,vertical='center')
ws.row_dimensions[1].height=30
for r in rows:
 s,e=r['series'],r['ep']
 if s=='Dragon Ball Z':
  if e in (9,10): cap='Local SRT reread in this audit; not video'
  elif e in historical:cap='Prior project reports full spoken-caption read; not video'
  else:cap='Local caption file indexed; not full-read according to project'
 else:cap='No caption review asserted for this series in this audit'
 vals=[s,e,r['title'],r['english'],r['status'],cap,r['url'],r['second'] or '']
 ws.append(vals); row=ws.max_row
 for c in ws[row]:c.alignment=Alignment(vertical='top',wrap_text=True);c.font=Font(name='Calibri',size=10,color=GRAY)
 for j in (7,8):
  c=ws.cell(row,j)
  if c.value:c.hyperlink=c.value;c.font=Font(name='Calibri',size=10,color='0563C1',underline='single')
 if 'absent' in r['status'] or 'combines' in r['status']:
  for c in ws[row]:c.fill=PatternFill('solid',fgColor=SOFT)
 elif s=='Dragon Ball Z' and e<=35:
  for c in ws[row]:c.fill=PatternFill('solid',fgColor=GREEN)
ws.freeze_panes='C2';ws.auto_filter.ref=f'A1:H{ws.max_row}';ws.sheet_properties.pageSetUpPr.fitToPage=True
for i,w in enumerate([24,10,39,43,49,46,39,40],1):ws.column_dimensions[get_column_letter(i)].width=w
ws.sheet_view.zoomScale=85

films=[
('Dragon Ball','Curse of the Blood Rubies',1986,'Early adventure reimagining'),('Dragon Ball',"Sleeping Princess in Devil’s Castle",1987,'Early Goku/Krillin history'),('Dragon Ball','Mystical Adventure',1988,'Alternate tournament and relationships'),('Dragon Ball','The Path to Power',1996,'Early adventure/Red Ribbon reimagining'),
('Dragon Ball Z','Dead Zone',1989,'Gohan/Piccolo/Krillin prior-meeting conflict; later Garlic Jr. arc'),('Dragon Ball Z',"The World’s Strongest",1990,'Cast, techniques and Piccolo’s status'),('Dragon Ball Z','The Tree of Might',1990,'Turles and cast placement'),('Dragon Ball Z','Lord Slug',1991,'Transformation depiction and cast'),('Dragon Ball Z',"Cooler’s Revenge",1991,'Frieza/Goku/Cooler history'),('Dragon Ball Z','The Return of Cooler',1992,'First Cooler encounter and Namek’s state'),('Dragon Ball Z','Super Android 13!',1992,'Android chronology and cast'),('Dragon Ball Z','Broly – The Legendary Super Saiyan',1993,'Earlier Broly is a distinct portrayal'),('Dragon Ball Z','Bojack Unbound',1993,'Cell-era aftermath and who is alive'),('Dragon Ball Z','Broly – Second Coming',1994,'Prior Broly encounter and later children'),('Dragon Ball Z','Bio-Broly',1994,'Earlier Broly storyline and cast'),('Dragon Ball Z','Fusion Reborn',1995,'Otherworld, death and fusion status'),('Dragon Ball Z','Wrath of the Dragon',1995,'Tapion, family ages and sword account'),
('Modern Z / Super','Battle of Gods',2013,'Overlaps Super TV and Super: Beerus'),('Modern Z / Super',"Resurrection ‘F’",2015,'Overlaps Super TV and Super: Beerus'),('Modern Z / Super','Dragon Ball Super: Broly',2018,'Distinct Broly history from the 1990s films'),('Modern Z / Super','Dragon Ball Super: SUPER HERO',2022,'Film versus manga adaptation, family and Red Ribbon state')]
ws=wb.create_sheet('Films');ws.sheet_view.showGridLines=False
ws.append(['Group','Film','Release year','Question to investigate','Continuity decision','Coverage'])
for c in ws[1]:c.fill=PatternFill('solid',fgColor=NAVY);c.font=Font(bold=True,color=WHITE);c.alignment=Alignment(wrap_text=True)
for group,title,year,issue in films:
 ws.append([group,title,year,issue,'PENDING','Not watched in this audit'])
 for c in ws[ws.max_row]:c.alignment=Alignment(vertical='top',wrap_text=True);c.font=Font(size=10,color=GRAY)
 ws.cell(ws.max_row,5).fill=PatternFill('solid',fgColor=SOFT)
dv=DataValidation(type='list',formula1='"PENDING,IN,OUT,SIDE"');dv.promptTitle='Planning only';dv.prompt='Any project decision requires user approval.';dv.showInputMessage=True;ws.add_data_validation(dv);dv.add('E2:E22')
for i,w in enumerate([21,43,15,65,23,30],1):ws.column_dimensions[get_column_letter(i)].width=w
ws.freeze_panes='B2';ws.auto_filter.ref='A1:F22';ws.row_dimensions[1].height=28
out=ROOT/'06_EPISODE_AND_FILM_INDEX.xlsx';wb.save(out)
check=load_workbook(out,read_only=False,data_only=False)
assert check['Episodes'].max_row==660 and check['Films'].max_row==22
print('Wrote',out,'episode rows',len(rows),'films',len(films),'sheets',check.sheetnames)
