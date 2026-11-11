import sys,json,collections,math,hashlib,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v4_audit_junction')]
import numpy as np,export_v3 as ex
from apply_junction_v4 import apply
S=copy.deepcopy(ex.SCENE);changes=apply(S);ex.SCENE=S
bad=[];neg=[];dup=[];fp={};count=0
for e in S['elements']:
 for j,p in enumerate(ex.expand_parts(e)):
  if p['geometry']['type']=='terrain':continue
  v,f=ex.world_part(p,e)
  if v is None:continue
  edges=collections.Counter();vol=0
  for face in f:
   for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1
   for k in range(1,len(face)-1):vol+=np.dot(v[face[0]],np.cross(v[face[k]],v[face[k+1]]))/6
  name=e['name']+'__'+str(j+1);count+=1
  if any(c!=2 for c in edges.values()):bad.append(name)
  if vol<=0:neg.append([name,vol])
  digest=hashlib.sha256(np.round(np.array(sorted(map(tuple,v))),7).tobytes()).hexdigest()
  if digest in fp:dup.append([fp[digest],name])
  fp[digest]=name
r={'count':count,'bad':bad,'nonpositive':neg,'duplicates':dup,'changes':changes}
(W/'v4_audit_junction/Apply_Module_QA.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
(W/'v4_audit_junction/Scene_Repair_Test.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k!='changes'},indent=2))
assert not bad and not neg and not dup
