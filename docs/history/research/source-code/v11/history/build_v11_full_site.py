import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S
I=[]
for e in S['elements']:
 if e['layer']!='60_SITE' and not e['name'].startswith('DOOR_OUTER_GATE'):continue
 tri=[];mats=[]
 for part in ex.expand_parts(e):
  v,f=ex.world_part(part,e)
  if v is None:continue
  for face in f:
   for ix in (ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]):
    t=v[[face[j] for j in ix]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-12:tri.append(t);mats.append(part['material'])
 if not tri:continue
 t=np.array(tri);v=t.reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);drop=np.argmax(abs(n),axis=1);uv=np.zeros((len(t),3,2))
 for j in range(3):
  idx=np.where(drop==j)[0];uv[idx]=t[idx][:,:,[k for k in range(3) if k!=j]]
 ms=list(dict.fromkeys(mats));mid=np.array([ms.index(m) for m in mats],np.int32);fn='FULL_V11_'+e['name']+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=f,uv=uv.reshape(-1,2),material_ids=mid);I.append({'name':e['name'],'file':fn,'materials':ms,'triangles':len(t)})
 print('full',e['name'],len(t),flush=True)
(O/'02_Data/Full_Wall_Index_V11.json').write_text(json.dumps(I,indent=2),encoding='utf-8');print('Full V11 site review',len(I),'nodes',sum(r['triangles'] for r in I),'triangles',flush=True)
