import sys,json,hashlib,time
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'libs'))
import rhino3dm as r
O=W/'v24_03_dimension_audit';O.mkdir(exist_ok=True)
def load(path,name):
 f=r.File3dm.Read(str(path)); mats={};cache={}
 for i,m in enumerate(f.Materials):
  tex=m.GetBitmapTexture()
  if tex and Path(tex.FileName).exists():
   if tex.FileName not in cache:
    with Image.open(tex.FileName) as im:
     im.thumbnail((2048,2048));cache[tex.FileName]=np.array(im.convert('RGB'))
   mats[i]=cache[tex.FileName]
 ps=[];cs=[]
 for ob in f.Objects:
  g=ob.Geometry
  if not isinstance(g,r.Mesh):continue
  p=np.array([(v.X,v.Y,v.Z) for v in g.Vertices],dtype=np.float32)
  t=mats.get(ob.Attributes.MaterialIndex)
  if t is None:c=np.tile([170,170,170],(len(p),1)).astype(np.uint8)
  else:
   uv=np.array([(v.X,v.Y) for v in g.TextureCoordinates])
   xx=np.clip(np.round(uv[:,0]*(t.shape[1]-1)).astype(int),0,t.shape[1]-1)
   yy=np.clip(np.round((1-uv[:,1])*(t.shape[0]-1)).astype(int),0,t.shape[0]-1)
   c=t[yy,xx]
  ps.append(p);cs.append(c)
 p=np.concatenate(ps);c=np.concatenate(cs)
 np.savez_compressed(O/(name+'_points.npz'),p=p,c=c)
 return p,c
def project(p,c,name,axes,scale=None,center=None):
 a=np.array(axes,dtype=float);q=p@a.T
 if center is not None:q[:,:2]-=np.array(center)
 mn=q[:,:2].min(0);mx=q[:,:2].max(0)
 size=1600;sc=(size-50)/max(mx-mn) if scale is None else scale
 xy=(q[:,:2]-(mn+mx)/2)*sc+size/2; xy[:,1]=size-xy[:,1]
 xy=np.round(xy).astype(int)
 order=np.argsort(q[:,2]);xy=xy[order];co=c[order]
 ok=(xy[:,0]>=2)&(xy[:,0]<size-2)&(xy[:,1]>=2)&(xy[:,1]<size-2);xy=xy[ok];co=co[ok]
 im=np.full((size,size,3),240,dtype=np.uint8)
 # Far to near overwrite; 3x3 splats preserve exposed near points.
 for dx,dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1)]:im[xy[:,1]+dy,xy[:,0]+dx]=co
 image=Image.fromarray(im);dr=ImageDraw.Draw(image);dr.text((20,20),name,fill=(0,0,0))
 # Coordinate ticks referenced to native XY for top.
 if name.endswith('top'):
  for axis in [0,1]:
   for v in np.arange(np.ceil(mn[axis]/10)*10,mx[axis],10):
    s=(v-(mn[axis]+mx[axis])/2)*sc+size/2
    if axis==0:dr.text((s,size-20),str(int(v)),fill=(255,0,0))
    else:dr.text((5,size-s),str(int(v)),fill=(255,0,0))
 image.save(O/(name+'.png'))
 return {'bbox':p.min(0).tolist()+p.max(0).tolist(),'vertices':len(p),'pixels_per_m':sc}
summary={}
for path,name in [(Path('E:/jz/实景三维场景模型2.3dm'),'reference2'),(Path('E:/jz/纯场地版本.3dm'),'current_site')]:
 print('LOAD',name,flush=True);p,c=load(path,name)
 summary[name]=project(p,c,name+'_top',[[1,0,0],[0,1,0],[0,0,1]])
 project(p,c,name+'_oblique',[[.707,-.707,0],[.354,.354,.866],[-.612,-.612,.5]])
 print(summary[name],flush=True)
(O/'projection_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
