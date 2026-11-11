import sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import mutation as m
S=m.apply(copy.deepcopy(m.S));m.ex.SCENE=S
select=[e for e in S['elements'] if e['name'].startswith(('SITE_KITCHEN','SITE_INNER_GATEHOUSE','SITE_INNER_STONE_GATE','SITE_GATEHOUSE_CARVED','SITE_SOUTH_SCREENWALL','SITE_SCREENWALL_'))]
out=[]
for e in select:
 mats={}
 for p in m.ex.expand_parts(e):
  v,fs=m.ex.world_part(p,e)
  if v is None:continue
  name=p['material'];row=mats.setdefault(name,dict(vertices=[],faces=[],material=name));offset=len(row['vertices']);row['vertices']+=v.tolist()
  for f in fs:
   for t in m.ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]:row['faces'].append([offset+f[i] for i in t])
 out.append(dict(name=e['name'],meshes=list(mats.values())))
(Path(__file__).parent/'Preview_Geometry.json').write_text(json.dumps(dict(elements=out,materials=S['materials'])),encoding='utf-8')
print('Preview data',len(out))
