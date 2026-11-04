from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup
import requests,time,json,threading
root=Path('/home/user/Twin_Rebuild_Research_2026-11-01/sources')
output=root/'toei_franchise_official_synopses.jsonl'
configs=[('Dragon Ball','dragon',1,153),('Dragon Ball Z','dragonz',36,291),('Dragon Ball GT','dragongt',1,64),('Dragon Ball Super (2015)','dragon_super',1,131)]
alljobs=[(series,slug,n) for series,slug,lo,hi in configs for n in range(lo,hi+1)]
seen=set()
if output.exists():
 for line in output.read_text().splitlines():
  try:
   d=json.loads(line); seen.add((d['series'],d['episode']))
  except Exception: pass
jobs=[j for j in alljobs if (j[0],j[2]) not in seen]
headers={'User-Agent':'Mozilla/5.0 (individual literary research; 2 concurrent requests)'}
def get(job):
 series,slug,n=job; u=f'https://lineup.toei-anim.co.jp/ja/tv/{slug}/episode/{n}/'
 time.sleep(.30)
 try:
  r=requests.get(u,headers=headers,timeout=25)
  if r.status_code!=200: return {'series':series,'episode':n,'url':u,'status':f'HTTP {r.status_code}'}
  s=BeautifulSoup(r.content,'html.parser'); e=s.select_one('.episode_current.entry')
  if not e: return {'series':series,'episode':n,'url':u,'status':'episode container missing'}
  h=e.select_one('h1.story_caption_title'); t=e.select_one('.text_details_inner')
  if not h or not t: return {'series':series,'episode':n,'url':u,'status':'title/summary selector missing'}
  return {'series':series,'episode':n,'url':u,'title_ja':' '.join(h.get_text(' ',strip=True).split()),'synopsis_ja':' '.join(t.get_text(' ',strip=True).split()),'status':'official synopsis only; full scene footage not reviewed'}
 except Exception as ex: return {'series':series,'episode':n,'url':u,'status':'fetch failure: '+str(ex)}
print('Starting',len(jobs),'page fetches with two workers; previously cached:',len(seen),flush=True)
with output.open('a') as f,ThreadPoolExecutor(max_workers=2) as pool:
 for i,fu in enumerate(as_completed([pool.submit(get,j) for j in jobs]),1):
  result=fu.result();f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush()
  if i%25==0 or i==len(jobs): print('processed',i,'/',len(jobs),'last status:',result['status'],flush=True)
print('FINISHED',flush=True)
