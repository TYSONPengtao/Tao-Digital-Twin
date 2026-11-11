"""Give the native Rhino top surfaces the same continuous, top-only normal field.
Vertex coordinates, face indices, texture coordinates and object IDs remain exact.
"""
import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V12');p=O/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(p));records=[];checks=[]
for ob in F.Objects:
 n=ob.Attributes.Name
 if not n.startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD')):continue
 g=ob.Geometry;v=np.array([[q.X,q.Y,q.Z] for q in g.Vertices.ToPoint3dArray()]);faces=np.array([tuple(f)[:3] for f in g.Faces]);cross=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]]);length=np.linalg.norm(cross,axis=1);top=cross[:,2]/np.maximum(length,1e-30)>.35
 assert len(g.Normals)==len(v) and g.IsValid and g.IsClosed
 old_uv=np.array([[q.X,q.Y] for q in g.TextureCoordinates]);records.append((ob,g,v,faces,cross,top,old_uv,'EARTH' if n.startswith('SITE_V12_REBUILT_EARTH') else 'ROAD'))
for category in ['EARTH','ROAD']:
 items=[a for a in records if a[-1]==category];xyz=np.concatenate([a[2] for a in items]);_,inv=np.unique(np.round(xyz,4),axis=0,return_inverse=True);sums=np.zeros((int(inv.max())+1,3));offset=0;parts=[]
 for ob,g,v,faces,cross,top,uv,_ in items:
  ids=inv[offset:offset+len(v)];offset+=len(v)
  for c in range(3):np.add.at(sums,ids[faces[top,c]],cross[top])
  parts.append((ob,g,v,faces,ids,top,uv))
 sums/=np.maximum(np.linalg.norm(sums,axis=1)[:,None],1e-30)
 for ob,g,v,faces,ids,top,uv in parts:
  used=np.unique(faces[top]);assert np.all(np.isfinite(sums[ids[used]]))
  for i in used:g.Normals[int(i)]=rh.Vector3f(*map(float,sums[ids[i]]))
  v2=np.array([[q.X,q.Y,q.Z] for q in g.Vertices.ToPoint3dArray()]);uv2=np.array([[q.X,q.Y] for q in g.TextureCoordinates]);f2=np.array([tuple(f)[:3] for f in g.Faces]);assert np.array_equal(v,v2) and np.array_equal(faces,f2) and np.array_equal(uv,uv2) and g.IsValid and g.IsClosed
  checks.append(dict(name=ob.Attributes.Name,vertices_and_faces_exact=True,uv_exact=True,valid_closed=True,top_normals_changed=len(used)))
assert len(checks)>40;F.Strings['V12_Terrain_Normals']='Continuous area-weighted top-only normal field across adjacent panels of each ground category; geometry and UV exact.';assert F.Write(str(p),8)
h=hashlib.sha256()
with p.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
(O/'06_Report/Native_Ground_Shading_QA.json').write_text(json.dumps(dict(status='PASS',native_model_sha256=h.hexdigest(),geometry_and_uv_unchanged=True,panels=checks),ensure_ascii=False,indent=2),encoding='utf8');print('Native top-only shading PASS',len(checks),'panels; geometry and UV exact',flush=True)
