import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,manifold3d as mf
O=Path(r'E:/jz/JIA/Rebuild_V19');B=Path(r'E:/jz/JIA/Rebuild_V18');C=json.loads((O/'02_Data/Coordinate.json').read_text());ang=math.radians(C['rotation_deg']);R=np.array([[math.cos(ang),-math.sin(ang),0],[math.sin(ang),math.cos(ang),0],[0,0,1]]);origin=np.array(C['origin']);F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm'));BF=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm'))
def raw(ob):
 mm=ob.Geometry;v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;f=[]
 for q in mm.Faces:
  f.append(q[:3])
  if q[3]!=q[2]:f.append([q[0],q[2],q[3]])
 v,ix=np.unique(np.round(v,10),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(v,ix[np.array(f)].astype(np.uint64)));assert a.status()==mf.Error.NoError
 if a.volume()<0:print('NEGATIVE OLD OBJECT',ob.Attributes.Name,a.volume(),flush=True)
 return a
def node(mm,n):return [o for o in mm.Objects if o.Attributes.Name==n or o.Attributes.Name.startswith(n+'__')]
def report(a):
 rows=[]
 for c in a.decompose():
  if abs(c.volume())<1e-8:continue
  v=np.asarray(c.to_mesh64().vert_properties)[:,:3];rows.append({'volume':c.volume(),'min':v.min(0).tolist(),'max':v.max(0).tolist(),'vertices':len(v)})
 return rows
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 before=mf.Manifold.batch_boolean([raw(o) for o in node(BF,n)],mf.OpType.Add);after=mf.Manifold.batch_boolean([raw(o) for o in node(F,n)],mf.OpType.Add)
 print(n,'before',before.volume(),'after',after.volume(),'lost',json.dumps(report(before-after)),'added',json.dumps(report(after-before)),flush=True)
