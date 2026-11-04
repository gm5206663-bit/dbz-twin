from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup
import requests,time,json,hashlib
root=Path('/home/user/Twin_Rebuild_Research_2026-11-01/sources')
headers={'User-Agent':'Mozilla/5.0 (individual literary research)'}
def get(n):
    u=f'https://lineup.toei-anim.co.jp/ja/tv/dragonz/episode/{n}/'
    for attempt in range(3):
        try:
            r=requests.get(u,headers=headers,timeout=25)
            r.raise_for_status()
            s=BeautifulSoup(r.content,'html.parser')
            e=s.select_one('.episode_current.entry')
            if e is None: raise ValueError('cannot identify episode_current')
            h=e.select_one('h1.story_caption_title')
            t=e.select_one('.text_details_inner')
            img=e.select_one('.story_text img')
            if not h or not t: raise ValueError('title or official synopsis missing')
            summary=' '.join(t.get_text(' ',strip=True).split())
            return {'episode':n,'url':u,'official_title_ja':' '.join(h.get_text(' ',strip=True).split()), 'official_synopsis_ja':summary,'still_url':img.get('src') if img else None,'source_level':'official promotional synopsis; NOT full footage; summary is not complete scene list', 'automatic_fetch':'success'}
        except Exception as ex:
            if attempt==2: return {'episode':n,'url':u,'automatic_fetch':'failed','error':str(ex)}
            time.sleep(1.5)
        finally:
            time.sleep(.20)
with ThreadPoolExecutor(max_workers=2) as p:
    data=sorted((f.result() for f in as_completed([p.submit(get,n) for n in range(1,36)])),key=lambda x:x['episode'])
out=root/'toei_saiyan_ep_001_035_official_synopses.json'
out.write_text(json.dumps({'scope':'official synopsis pages only; not video or full scene verification','retrieved_local_date':'2026-11-01','episodes':data},ensure_ascii=False,indent=2)+'\n')
print('Official pages fetched:',sum(x['automatic_fetch']=='success' for x in data),'/',len(data))
print('File:',out)
for n in (1,2,3,8,9):
    d=data[n-1]
    if d.get('still_url'):
        try:
            im=requests.get(d['still_url'],headers=headers,timeout=20);im.raise_for_status()
            (root/f'toei_dbz_ep_{n:03}_official_still.jpg').write_bytes(im.content)
            print('still downloaded',n,len(im.content))
        except Exception as ex: print('still failed',n,str(ex))
