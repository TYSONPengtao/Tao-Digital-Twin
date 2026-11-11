import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from PIL import Image,ImageDraw
B=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v17';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));rows=[];im=Image.new('RGB',(1400,1300),'white');dr=ImageDraw.Draw(im)
def px(q):return ((q[0]-10)*100+50,1200-(q[1]+20)*100)
for x in range(10,24):dr.line([px([x,-20]),px([x,-8])],fill='#dddddd');dr.text(px([x,-19.8]),str(x),fill='black')
for y in range(-20,-7):dr.line([px([10,y]),px([23,y])],fill='#dddddd');dr.text(px([10,y]),str(y),fill='black')
for r in I:
 n=r['name']
 if not any(k in n for k in ['KITCHEN','STORAGE','SCREENWALL','RETAINING_WALL','V16_GRADED','V16_CONTINUOUS','V16_SEALED','SITE_TREE']):continue
 d=np.load(B/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];lo=v.min(0);hi=v.max(0);rows.append({'name':n,'bounds':[lo.tolist(),hi.tolist()],'materials':r['materials']})
 if any(k in n for k in ['GREY_BRICK_BACK','INNER_STORAGE_MASONRY','OUTER_STORAGE_VISIBLE_STONE','RETAINING_WALL_0','RETAINING_WALL_1','UNDER_ROOF_BASE','V16_GRADED','SITE_TREE']):
  t=v[f];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9
  if 'V16_GRADED' in n:color='#b8a871'
  elif 'RETAINING' in n:color='#3e4145'
  elif 'TREE' in n:color='#5f8943'
  elif 'STORAGE' in n:color='#44658f'
  else:color='#947654'
  for tri in t[up]:dr.polygon([px(q) for q in tri],fill=color)
 for p in E[n].get('parts',[]):
  if n in ['SITE_V14_INNER_STORAGE_MASONRY','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_V14_OUTER_STORAGE_VISIBLE_STONE_PLINTH']:
   g=p['geometry'];print('DETAIL',n,json.dumps(g,ensure_ascii=False)[:800])
im.save(D/'Junction_Plan_Before.png');(D/'Bounds.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
 if any(k in r['name'] for k in ['INNER_STORAGE_MASONRY','KITCHEN_GREY_BRICK','REGISTERED','SCREENWALL_UNDER','RAISED_BODY','OUTER_STORAGE_VISIBLE','OUTER_STORAGE_FLOOR','INNER_STORAGE_FLOOR','STONE_FLOOR','V16_GRADED','SITE_TREE']):print(json.dumps(r))
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_V14_INNER_STORAGE_MASONRY','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']:
 print('META',n,json.dumps({k:v for k,v in E[n].items() if k!='parts'},ensure_ascii=False))
