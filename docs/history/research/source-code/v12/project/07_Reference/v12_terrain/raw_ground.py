import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).parent
pts=[];fs=[]
for p in O.glob('source_*.npz'):
 d=np.load(p);v=d['local'];f=d['faces'];t=v[f[:,:3]];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mag=np.linalg.norm(n,axis=1);nz=abs(n[:,2])/(mag+1e-30);ok=(nz>.65)&(np.ptp(t[:,:,2],axis=1)<.7);pts.extend(t[ok].mean(1))
p=np.array(pts);cells=np.floor(p[:,:2]).astype(int);samples=[]
for c in np.unique(cells,axis=0):
 q=p[(cells==c).all(1)];z=np.percentile(q[:,2],10);samples.append([c[0]+.5,c[1]+.5,z,len(q)])
s=np.array(samples);np.savez_compressed(O/'Ground_Samples_Raw.npz',samples=s)
print('sample extent',s.min(0),s.max(0))
I=Image.new('RGB',(1260,1150),(255,255,255));D=ImageDraw.Draw(I);mn=np.array([-48,-48]);scale=10
for x,y,z,n in s:
 col=(int(max(0,min(255,(z+9)/30*255))),int(max(0,min(255,230-abs(z)*10))),int(max(0,min(255,255-(z+9)/30*255))))
 px,py=(np.array([x,y])-mn)*scale;py=1120-py;D.rectangle([px-5,py-5,px+5,py+5],fill=col)
for x in range(-40,70,10):
 px=(x-mn[0])*scale;D.line([(px,0),(px,1120)],fill=(150,150,150));D.text((px+2,1125),str(x),fill='black')
for y in range(-40,60,10):
 py=1120-(y-mn[1])*scale;D.line([(0,py),(1200,py)],fill=(150,150,150));D.text((1202,py),str(y),fill='black')
D.text((10,10),'Raw lower tenth-percentile ground support: green low Z, yellow high Z',fill='black');I.save(O/'Ground_Raw_Heights.png')
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
rows=[]
for e in S['elements']:
 if e['layer']=='60_SITE' and any(w in e['name'] for w in ['GROUND','TERRAIN','PAVING','ROAD','STEP','RAMP','APPROACH','THRESHOLD','EARTH']): rows.append(e)
(O/'V11_Ground_Elements.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('V11 ground names',[(e['name'],len(e.get('parts',[])),e.get('source')) for e in rows])
