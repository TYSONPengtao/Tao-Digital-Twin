from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).parent;F=W/'v26_6/Final'
I={r['name']:r for r in json.loads((F/'Geometry_Index.json').read_text('utf8'))}
names=[n for n in I if 'Secondary_Screenwall' in n or n.startswith('V24_21_Exterior_')]
im=Image.new('RGB',(1400,1600),'white');draw=ImageDraw.Draw(im)
stats=[]
for n in names:
 a=np.load(F/I[n]['file']);t=a['v'][a['f']];sel=(t[:,:,0].max(1)>10.55)&(t[:,:,0].min(1)<13.7)&(t[:,:,1].max(1)>-17.6)&(t[:,:,1].min(1)<-16.05)
 tt=t[sel]
 if not len(tt):continue
 j=0 if 'Secondary_Screenwall' in n else 1 if 'White_Frieze' in n else 2 if 'Stepped_Frames' in n else 3
 palette=['#74a9cf','#f7a582','#fdd49e','#a6bddb','#c7e9c0','#fecc5c','#9ecae1','#bcbddc','#b2e2e2','#cccccc']
 for tr in tt:
  pts=[(60+int((p[0]-10.5)/3.3*1260),j*400+370-int((p[2]+1.5)/4.6*340))for p in tr]
  draw.polygon(pts,fill=palette[names.index(n)%10],outline='#444444')
 stats.append({'name':n,'bounds':I[n]['bounds'],'triangles':len(t),'local_triangles':len(tt),'local_bounds':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()]})
for j,title in enumerate(['PROTECTED original 11 objects','Generic white backing','Generic stepped frames','Generic cornices']):
 draw.text((30,j*400+10),title,fill='black')
 for z in [-1,0,1,2,3]:
  y=j*400+370-int((z+1.5)/4.6*340);draw.text((5,y),str(z),fill='black');draw.line((40,y,1340,y),fill='#dddddd')
 for x in [11,12,13]:draw.text((60+int((x-10.5)/3.3*1260),j*400+380),str(x),fill='black')
im.save(D/'Secondary_Local_XZ.png')
(D/'Site_Local_Inventory.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
print(json.dumps(stats,indent=2))
