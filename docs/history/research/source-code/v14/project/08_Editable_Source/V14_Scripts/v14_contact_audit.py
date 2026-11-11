import sys,json,ast,collections,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));E.update({e['name']:e for e in Q['replace']+Q['add']})
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'solid','exec'))
records=[];rows=[]
def bounds(p):
 v,_,_,_=ex.solid_data(p['geometry']);return np.array([v.min(0),v.max(0)])
def nodeparts(n):return [(n,i,p) for i,p in enumerate(E[n]['parts'])]
names=['SITE_V14_INNER_STORAGE_FLOOR','SITE_V14_INNER_STORAGE_MASONRY','SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME','SITE_V14_INNER_STORAGE_ROOF_WOOD_SHEATHING','SITE_V14_INNER_STORAGE_GABLE_ROOF','SITE_V14_OUTER_STORAGE_FLOOR','SITE_V14_OUTER_STORAGE_STEEL_BEARING_FRAME','SITE_V14_OUTER_STORAGE_METAL_ROOF','SITE_V14_OUTER_STORAGE_VISIBLE_STONE_PLINTH']
targets=[r for n in names for r in nodeparts(n)]
# Nearby retained real main-kitchen roof members and masonry are support neighbors.
for n,e in E.items():
 if n.startswith('SITE_KITCHEN_') and any(q in n for q in ['TIMBER','RAFTER','PURLIN','RIDGE_UNDER','BRICK_BACK']):
  for i,p in enumerate(e['parts']):
   b=bounds(p)
   if np.all(b[1]>[11.2,-12.2,2.5]) and np.all(b[0]<[13.8,-9.2,4.4]):targets.append((n,i,p))
bs=np.array([bounds(p) for n,i,p in targets]);ms=[manifold(p['geometry']) for n,i,p in targets];adj=[set() for r in targets];contacts=[]
for i in range(len(targets)):
 for j in range(i):
  if np.all(bs[i,1]+.003>=bs[j,0]) and np.all(bs[j,1]+.003>=bs[i,0]):
   gap=ms[i].min_gap(ms[j],.004)
   if gap<=.0001:adj[i].add(j);adj[j].add(i);contacts.append([i,j,float(gap)])
 roots={i for i,(n,j,p) in enumerate(targets) if n in ['SITE_V14_INNER_STORAGE_FLOOR','SITE_V14_OUTER_STORAGE_FLOOR'] or n.startswith('SITE_KITCHEN_')};seen=set(roots);queue=list(roots)
while queue:
 i=queue.pop()
 for j in adj[i]-seen:seen.add(j);queue.append(j)
floating=[{'node':targets[i][0],'part':targets[i][1],'bounds':bs[i].tolist(),'neighbors':len(adj[i])} for i in range(len(targets)) if i not in seen]
# Cover tiles must touch their roof backing at a foot; curved central air space is intentional.
tile_roofs=[manifold(p['geometry']) for p in E['SITE_V14_INNER_STORAGE_GABLE_ROOF']['parts']];tile_gaps=[]
for i,p in enumerate(E['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES']['parts']):
 m=manifold(p['geometry']);gap=min(m.min_gap(r,.02) for r in tile_roofs)
 if gap>.0001:tile_gaps.append({'part':i,'gap_m':float(gap)})
qa={'status':'PASS' if not floating and not tile_gaps else 'NEEDS_CORRECTION','method':'Closed mesh geometric contact graph at 0.1 mm tolerance; floor or retained kitchen member is graph root. Checks visible geometry contacts only, not load capacity. Changed native vertices are verified separately against these modeled parts.','members':len(targets),'support_contacts':len(contacts),'unconnected_members':floating,'curved_tile_support_failures':tile_gaps,'tile_count':len(E['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES']['parts']),'force_capacity_calculated':False}
(W/'v14/Contact_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(qa,ensure_ascii=False),flush=True)
