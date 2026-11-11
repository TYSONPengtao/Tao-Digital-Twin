import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work')
sys.path[:0]=[str(W/'np1'),str(W/'libs'),str(W/'geomlibs'),str(W)]
import numpy as np
import export_v3 as ex
from PIL import Image
out=W/'v4_audit_safety'
S=ex.SCENE
items=[]
for e in S['elements']:
 if e['layer'] not in ['40_STAIR','41_RAILING','30_DOOR','31_WINDOW']: continue
 vv=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e)
  if v is not None:vv.extend(v.tolist())
 if vv:
  a=np.array(vv)
  items.append({'name':e['name'],'layer':e['layer'],'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist(),'origin':e.get('origin'),'angle':e.get('angle'),'source':e.get('source'),'definition':e.get('definition'),'rise_list':e.get('rises')})
(out/'Bounds_V3.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
for i in items:
 if i['name'].startswith(('STAIR_F','STAIR_LAND','STAIR_HAND','TERRACE_','BALCONY_STONE','DOOR')):
  print(i)
img=Image.open(r'E:\jz\JIA\Rebuild_V3\02_PDF_Reference\D10.png')
img.crop((420,215,795,1025)).resize((750,1620)).save(out/'D10_Stair_Plan_Crop.png')
