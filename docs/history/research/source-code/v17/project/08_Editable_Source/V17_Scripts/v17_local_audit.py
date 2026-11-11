import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np,export_v5 as ex
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from PIL import Image,ImageDraw
B=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v17'
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'))
region=box(12,-11,20,-2)
im=Image.new('RGB',(1600,1400),'white');dr=ImageDraw.Draw(im)
def px(q):return (int((q[0]-11)*150+30),int(1300-(q[1]+11)*130))
for x in range(11,22):dr.line([px([x,-11]),px([x,-2])],fill='#dddddd');dr.text(px([x,-10.8]),str(x),fill='black')
for y in range(-11,-1):dr.line([px([11,y]),px([21,y])],fill='#dddddd');dr.text(px([11,y]),str(y),fill='black')
rows=[]
for r in sorted(I,key=lambda r:0 if 'GRADED_INTERIOR' in r['name'] else 1):
 n=r['name']
 if not any(k in n for k in ['KITCHEN_GREY','INNER_STORAGE_MASONRY','OUTER_STORAGE_VISIBLE','PERIMETER_JOINED_RETAINING','PERIMETER_V15','V16_GRADED']):continue
 d=np.load(B/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=no[:,2]>1e-9
 color='#d3c791' if 'GRADED' in n else '#5161b6' if 'MASONRY' in n else '#4e7778' if 'KITCHEN' in n else '#996d51' if n.endswith('_0') else '#eaa6a6' if 'WHITE' in n else '#766851'
 for tri in t[up]:
  if Polygon(tri[:,:2]).intersects(region):dr.polygon([px(q) for q in tri],fill=color)
 if n.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_0'):
  for j,p in enumerate(E[n]['parts']):
   try:v0,fs,_,_=ex.solid_data(p['geometry'])
   except Exception:continue
   poly=Polygon(v0[:,:2]).convex_hull
   if not poly.intersects(region):continue
   lo=v0.min(0);hi=v0.max(0)
   if n.endswith('_0') or (len(E[n]['parts'])<120):
    row={'name':n,'part':j,'material':p.get('material'),'bounds':[lo.tolist(),hi.tolist()],'geometry':p['geometry']};rows.append(row)
   if n.endswith('_0'):
    c=poly.representative_point();dr.text(px([c.x,c.y]),str(j),fill='white')
im.save(D/'Local_Wall_Plan_Before.png');(D/'Local_Parts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:print(r['name'],r['part'],r['material'],np.round(r['bounds'],3).tolist())
for n,e in E.items():
 if 'PERIMETER' in n and ('WHITE' in n or 'V15' in n):print('WHITE NODE',n,len(e.get('parts',[])))
for nn in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 a=np.array(json.loads((W/'v16'/f'{nn}_centerline.json').read_text(encoding='utf8')))
 print('CENTERLINE',nn,[(j,p.round(3).tolist()) for j,p in enumerate(a) if p[0]>12 and p[1]<-2])
