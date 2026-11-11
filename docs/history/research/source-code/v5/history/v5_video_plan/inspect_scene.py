import sys,json,math,csv
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from shapely.geometry import MultiPoint
import v2_geometry
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
O=Path(__file__).resolve().parent
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',17)
rows=[]
for e in S['elements']:
 if e['name'].startswith('DOOR_'):
  d=S['definitions'][e['definition']];r={'name':e['name'],'origin':e['origin'],'angle':e.get('angle',0),'parameters':d['parameters']};rows.append(r); print(json.dumps(r),flush=True)
(O/'V4_Doors.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
def xy(q):return [100+q[0]*85,1050-q[1]*85]
for floor,z in enumerate([0,3.9,7.5],1):
 im=Image.new('RGB',(1300,1160),'white');draw=ImageDraw.Draw(im)
 for x in [0,3.9,9.1,13]:
  a,b=xy((x,-.5)),xy((x,10.2));draw.line([a,b],fill='#ccc',width=1);draw.text((a[0],a[1]+15),str(x),font=font,fill='gray')
 for y in [0,2.1,7.3,9.8]:
  a,b=xy((-.4,y)),xy((13.5,y));draw.line([a,b],fill='#ccc',width=1);draw.text((25,a[1]),str(y),font=font,fill='gray')
 for e in S['elements']:
  if e['layer'] not in ['10_WALL_EXT','11_WALL_INT','20_COLUMN']:continue
  pts=e['parts'] if 'definition' not in e else S['definitions'][e['definition']]['parts']
  for p in pts:
   g=p['geometry']
   if g['type']=='box':
    q=np.array(g['origin']);d=np.array(g['size']);v=np.array([q+d*[a,b,c] for a in [0,1] for b in [0,1] for c in [0,1]])
   elif g['type']=='cylinder':
    q=np.array(g['origin']);v=np.array([q+[g['radius']*math.cos(a),g['radius']*math.sin(a),h] for a in np.linspace(0,2*math.pi,24) for h in [0,g['height']]])
   else:v,faces,_,_=v2_geometry.data(g);v=np.asarray(v,float)
   a=e.get('angle',0);v[:,:2]=v[:,:2]@np.array([[math.cos(a),math.sin(a)],[-math.sin(a),math.cos(a)]]);v+=np.array(e.get('origin',[0,0,0]))
   if v[:,2].min()>z+1.5+1e-4 or v[:,2].max()<z+1.5-1e-4:continue
   poly=MultiPoint(v[:,:2]).convex_hull
   if poly.geom_type=='Polygon':draw.polygon([xy(q) for q in poly.exterior.coords],fill='#333' if e['layer']=='20_COLUMN' else '#bbb',outline='#444')
 for r in rows:
  if abs(r['origin'][2]-z)>.01:continue
  x,y,_=r['origin'];w=r['parameters']['Width'];a=r['angle'];q=[x+w*math.cos(a),y+w*math.sin(a)];draw.line([xy((x,y)),xy(q)],fill='#bf4820',width=7)
  # Single labels normalized in separate table to avoid dense overlaps.
  draw.text((xy((x,y))[0]+10,xy((x,y))[1]-15),r['name'].replace('DOOR_',''),font=font,fill='#a52b16')
 draw.text((100,20),f'V4 F{floor} plan at {z+1.5}m; drawing dimensions, not verified as-built',font=font,fill='black')
 im.save(O/f'V4_F{floor}_Plan.png')
