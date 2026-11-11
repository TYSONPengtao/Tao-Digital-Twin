import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex
O=Path(__file__).parent;M=json.loads((O/'Mutation.json').read_bytes());S=json.loads(Path(r'E:/jz/JIA/Rebuild_V11_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_bytes());materials=dict(S['materials']);materials.update(M['materials']);elements=M['add']+[e for e in S['elements'] if e['name'].startswith('SITE_KITCHEN_') and e['name'] not in M['remove']]
rows=[]
for e in elements:
 for i,p in enumerate(e['parts']):
  v,fs,_,_=ex.solid_data(p['geometry']);tris=[]
  for f in fs:
   if len(f)<=4:tris.append(list(f))
   else:tris.extend([[f[j] for j in t] for t in ex.triangulate(v[f])])
  rows.append(dict(name=e['name']+'__'+str(i),node=e['name'],vertices=v.tolist(),faces=tris,material=p['material']))
(O/'Preview_Data.json').write_text(json.dumps(dict(materials=materials,parts=rows)),encoding='utf8');print('preview parts',len(rows))
