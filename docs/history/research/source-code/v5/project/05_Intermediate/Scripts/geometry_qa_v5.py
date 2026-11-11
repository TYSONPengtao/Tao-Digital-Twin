import sys,json,collections,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import export_v5 as ex
O=ex.OUT;S=ex.SCENE;bad=[];negative=[];duplicates=[];fingerprints={};counts=collections.Counter();solidcount=0
for e in S['elements']:
 for j,part in enumerate(ex.expand_parts(e)):
  g=part['geometry'];v,f=ex.world_part(part,e)
  if v is None or g['type']=='terrain':continue
  edges=collections.Counter();volume=0
  for face in f:
   for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted([a,b]))]+=1
   for k in range(1,len(face)-1):volume+=np.dot(v[face[0]],np.cross(v[face[k]],v[face[k+1]]))/6
  name=e['name']+f'__{j+1}';solidcount+=1;counts[g['type']]+=1
  if any(n!=2 for n in edges.values()):bad.append(name)
  if volume<=0:negative.append((name,volume))
  digest=hashlib.sha256(np.round(np.array(sorted(map(tuple,v))),7).tobytes()).hexdigest()
  if digest in fingerprints:duplicates.append((fingerprints[digest],name))
  fingerprints[digest]=name
report={'expanded_closed_parts':solidcount,'types':dict(counts),'nonmanifold_parts':bad,'nonpositive_signed_volume':negative,'exact_duplicate_solids':duplicates,'ground_regions':[{'name':e['name'],'area_m2':e.get('area_m2')} for e in S['elements'] if e.get('surface_only')],'scope_area_m2':S['site']['area_m2'],'note':'Topology and orientation checks do not certify dimensional accuracy. Adjacent grouped CAD solids may share contact faces.'}
print('GEOMETRY QA',solidcount,'closed parts',len(bad),'nonmanifold',len(negative),'wrong orientations',len(duplicates),'duplicates');(O/'09_Report/Geometry_QA_V5.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not bad and not negative and not duplicates
