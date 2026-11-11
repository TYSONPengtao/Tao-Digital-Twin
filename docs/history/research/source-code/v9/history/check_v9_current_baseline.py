import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh,numpy as np
root=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');cur=root/'04_Rhino/Reality_Hybrid_V8.3dm';pkg=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V8/04_Rhino/Reality_Hybrid_V8.3dm'
A=rh.File3dm.Read(str(pkg));B=rh.File3dm.Read(str(cur));aa={str(o.Attributes.Id):o for o in A.Objects};bb={str(o.Attributes.Id):o for o in B.Objects};changed=[]
for id,a in aa.items():
 if id not in bb:continue
 b=bb[id]
 if isinstance(a.Geometry,rh.Mesh) and isinstance(b.Geometry,rh.Mesh):
  same=list(a.Geometry.Faces)==list(b.Geometry.Faces) and len(a.Geometry.Vertices)==len(b.Geometry.Vertices)
  if same:
   for p,ks in [('Vertices','XYZ'),('Normals','XYZ'),('TextureCoordinates','XY')]:
    va=np.array([[getattr(v,k) for k in ks] for v in getattr(a.Geometry,p)]);vb=np.array([[getattr(v,k) for k in ks] for v in getattr(b.Geometry,p)]);same &= np.array_equal(va,vb)
 elif isinstance(a.Geometry,rh.InstanceReference) and isinstance(b.Geometry,rh.InstanceReference):
  av=np.array([[getattr(a.Geometry.Xform,f'M{i}{j}') for j in range(4)] for i in range(4)]);bv=np.array([[getattr(b.Geometry.Xform,f'M{i}{j}') for j in range(4)] for i in range(4)])
  same=a.Geometry.ParentIdefId==b.Geometry.ParentIdefId and np.max(abs(av-bv))<1e-10
 else:same=a.Geometry.Encode()==b.Geometry.Encode()
 if not same:changed.append({'id':id,'name':a.Attributes.Name,'geometry':type(a.Geometry).__name__})
result={'current_sha256':hashlib.sha256(cur.read_bytes()).hexdigest(),'delivered_sha256':hashlib.sha256(pkg.read_bytes()).hexdigest(),'added_ids':list(set(bb)-set(aa)),'removed_objects':[{'id':id,'name':aa[id].Attributes.Name} for id in set(aa)-set(bb)],'changed_geometry':changed,'objects_delivered_current':[len(aa),len(bb)],'current_valid':all(o.Geometry.IsValid for o in B.Objects),'views_counts':[len(A.Views),len(B.Views)],'named_views_counts':[len(A.NamedViews),len(B.NamedViews)]}
(W/'v9_current_baseline_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
