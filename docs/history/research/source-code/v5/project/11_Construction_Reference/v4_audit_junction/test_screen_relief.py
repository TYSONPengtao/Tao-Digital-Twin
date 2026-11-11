import sys,json,collections,hashlib,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v4_audit_junction')]
import numpy as np
from fix_screen_relief_backing import fix_screen_relief_backing
from check_final_v4 import SceneGeometry,run
source=Path('E:/jz/JIA/Rebuild_V4/05_Intermediate/Architecture_Scene.json')
S=json.loads(source.read_text());changes=fix_screen_relief_backing(S);G=SceneGeometry(S)
bad=[];negative=[];duplicates=[];fingerprints={};n=0
for e in S['elements']:
 if not e['name'].startswith('SITE_SCREENWALL_STEPPED_PANEL_'):continue
 for j,p in enumerate(G.parts(e)):
  v,f=G.world_part(p,e);edge=collections.Counter();volume=0
  for face in f:
   for a,b in zip(face,face[1:]+face[:1]):edge[tuple(sorted([a,b]))]+=1
   for k in range(1,len(face)-1):volume+=np.dot(v[face[0]],np.cross(v[face[k]],v[face[k+1]]))/6
  name=e['name']+'__'+str(j+1);n+=1
  if any(x!=2 for x in edge.values()):bad.append(name)
  if volume<=0:negative.append([name,volume])
  h=hashlib.sha256(np.round(np.array(sorted(map(tuple,v))),7).tobytes()).hexdigest()
  if h in fingerprints:duplicates.append([fingerprints[h],name])
  fingerprints[h]=name
out=W/'v4_audit_junction/Screen_Relief_Repair_Test_Scene.json';out.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
qa={'changes':changes,'parts_checked':n,'nonmanifold':bad,'nonpositive_volume':negative,'duplicates':duplicates}
(W/'v4_audit_junction/Screen_Relief_Repair_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False,indent=2));assert not bad and not negative and not duplicates
r=run(out,W/'v4_audit_junction/Screen_Relief_Final_Interface_Check.json');assert r['passed']
