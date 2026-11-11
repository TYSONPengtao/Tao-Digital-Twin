import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np
from nearest_photo_projection import PhotoProjector
C=json.loads(Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/02_Data/Coordinate.json').read_text(encoding='utf8'));M=np.linalg.inv(np.array(C['local_to_survey']))
P=PhotoProjector.from_objs(list(Path(r'E:/jz/JIA/Productions/Production_OBJ (2)/Data').rglob('*.obj')),coordinate_transform=M)
t=P.triangles;cent=t.mean(1);keep=(cent[:,0]>6)&(cent[:,0]<23)&(cent[:,1]>-19)&(cent[:,1]<-1)&(cent[:,2]>1.8)&(cent[:,2]<6)
np.savez_compressed(W/'v14/data/Registered_Actual_Roof.npz',vertices=t[keep].reshape(-1,3),faces=np.arange(keep.sum()*3).reshape(-1,3),uv=P.uv[keep].reshape(-1,2),material_ids=P.material_ids[keep])
(W/'v14/Roof_Source_Materials.json').write_text(json.dumps(P.materials,indent=2),encoding='utf8')
from PIL import Image,ImageDraw
tt=t[keep];cc=cent[keep];im=Image.new('RGB',(1200,1280),'white');dr=ImageDraw.Draw(im);scale=64
def xy(q):return (int((q[0]-6)*scale+50),int((-1-q[1])*scale+50))
for i in np.argsort(cc[:,2]):
 h=np.clip((cc[i,2]-2.4)/2.2,0,1);color=tuple(int(c*255) for c in __import__('colorsys').hsv_to_rgb((1-h)*.7,.8,.85));dr.polygon([xy(q) for q in tt[i]],fill=color)
for x in range(6,24):dr.line([xy([x,-19]),xy([x,-1])],fill='#999999',width=1);dr.text(xy([x,-.8]),str(x),fill='black')
for y in range(-19,0):dr.line([xy([6,y]),xy([23,y])],fill='#999999',width=1);dr.text((5,xy([6,y])[1]),str(y),fill='black')
im.save(W/'v14/Actual_Roof_Height_Top.png')
# Dense topmost observed roof height at a coarse grid, excluding nearly vertical wall triangles.
n=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-20);q=cc[abs(n[:,2])>.50]
for x in np.arange(7,22,.5):
 row=[]
 for y in np.arange(-17,-8,.5):
  z=q[(abs(q[:,0]-x)<.20)&(abs(q[:,1]-y)<.20),2];row.append(None if len(z)==0 else round(float(np.median(z)),2))
 print('X',x,row)
print('DONE',keep.sum(),flush=True)
