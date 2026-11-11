import sys,json,ast,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));n='TERRACE_SIDE_CERAMIC_PANEL_GRID';source=next(e for e in S['elements'] if e['name']==n);e=next(e for e in Q['replace'] if e['name']==n)
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'solid','exec'))
cu=manifold({'type':'box','origin':[3.6,6.15,7.48],'size':[.45,.90,2.13]});ps=[]
for p in source['parts']:
 v,_,_,_=ex.solid_data(p['geometry']);lo=v.min(0);hi=v.max(0)
 if np.all(hi>[3.6,6.15,7.48]) and np.all(lo<[4.05,7.05,9.61]):
  m=manifold(p['geometry']);r=m-cu
  if abs(m.volume()-r.volume())>1e-9:
   if not r.is_empty():ps.append({'geometry':fromman(r),'material':p['material']})
  else:ps.append(p)
 else:ps.append(p)
ps.append({'geometry':{'type':'box','origin':[3.792,7.05,7.50],'size':[.008,.148,2.10]},'material':source['parts'][0]['material']});e['parts']=ps;(W/'v14/Building_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('FINISH OPENING RESTORED AND CUT 6.15..7.05',flush=True)
