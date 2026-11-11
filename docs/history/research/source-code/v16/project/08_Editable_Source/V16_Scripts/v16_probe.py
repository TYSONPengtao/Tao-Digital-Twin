import sys,json
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from PIL import Image,ImageDraw
B=Path(r'E:/jz/JIA/Rebuild_V15');D=W/'v16';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'))
I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'))
E={e['name']:e for e in S['elements']}
rows=[];im=Image.new('RGB',(1400,1100),'white');draw=ImageDraw.Draw(im);earthpolys=[];earthz=[];overlays=[]
def xy(p):return ((p[0]+31)*24+28,1050-(p[1]+25)*24)
for x in range(-30,25,5):draw.line([xy([x,-25]),xy([x,19])],fill='#dddddd');draw.text(xy([x,-24]),str(x),fill='black')
for y in range(-25,20,5):draw.line([xy([-31,y]),xy([25,y])],fill='#dddddd');draw.text(xy([-30,y]),str(y),fill='black')
for r in I:
 n=r['name']
 if not any(k in n for k in ['REBUILT_EARTH','REBUILT_ROAD','REBUILT_COURT','RETAINING_WALL','SCREENWALL','ENTRY_PAVEMENT','CONTINUOUS_PAVEMENT','OUTER_GATE_SCORED','STORAGE_VISIBLE_STONE','GATE_POST','ENDPOINT_CONNECTOR']):continue
 d=np.load(B/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];t=v[f];norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=norm[:,2]>1e-8
 g=unary_union([Polygon(q[:,:2]) for q in t[up]]).buffer(0)
 row={'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'top_area':g.area,'top_z_quantiles':np.quantile(t[up,:,2],[0,.1,.5,.9,1]).tolist() if up.any() else [],'material':r['materials'],'part_types':[p['geometry']['type'] for p in E[n].get('parts',[])]}
 if len(E[n].get('parts',[]))<5 and 'RETAINING_WALL' in n:row['parts']=E[n].get('parts')
 rows.append(row)
 if 'REBUILT_EARTH' in n:
  earthpolys.extend(t[up,:,:2]);earthz.extend(t[up,:,2].mean(1))
 elif any(k in n for k in ['RETAINING_WALL','SCREENWALL','STORAGE_VISIBLE_STONE','GATE_POST']):overlays.append((t[up,:,:2],'#555555'))
 else:overlays.append((t[up,:,:2],'#bdcad2'))
for q,z in zip(earthpolys,earthz):
 h=max(0,min(1,(float(z)+4)/5));draw.polygon([xy(p) for p in q],fill=(int(190*h+40),int(190*h+40),int(80*h+45)))
for tris,color in overlays:
 for q in tris:draw.polygon([xy(p) for p in q],fill=color)
draw.text((30,10),'LOCAL XY: yellow light = high, dark = low; grey = walls; blue = paved',fill='black');im.save(D/'Before_Height_Map.png')
(D/'Probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for row in rows:
 if any(k in row['name'] for k in ['REBUILT_EARTH','RETAINING_WALL_0','RETAINING_WALL_1','OUTER_GATE_SCORED','CONTINUOUS_PAVEMENT','STORAGE_VISIBLE_STONE']):print(json.dumps({k:v for k,v in row.items() if k!='parts'},ensure_ascii=False))
print('PARTS_SUMMARY')
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_V14_OUTER_STORAGE_VISIBLE_STONE_PLINTH']:
 print(n,json.dumps(E[n],ensure_ascii=False)[:12000])
