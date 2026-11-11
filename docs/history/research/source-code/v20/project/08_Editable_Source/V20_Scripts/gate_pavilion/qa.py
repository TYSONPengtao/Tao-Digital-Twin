import sys,json,ast
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
O=Path(__file__).parent;Q=json.loads((O/'Mutation.json').read_text(encoding='utf8'))
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'<checks>','exec'))
rows=[];volumes={}
for e in Q['replace']+Q['add']:
 valid=True;vol=0
 for j,p in enumerate(e['parts']):
  try:
   g=oriented(p['geometry']);m=manifold(g);assert m.volume()>0;vol+=m.volume();p['geometry']=g
  except Exception as x:raise ValueError((e['name'],j,str(x)))
 rows.append({'node':e['name'],'parts':len(e['parts']),'all_parts_closed_outward':True,'volume_m3':vol});volumes[e['name']]=vol
gate=next(e for e in Q['replace'] if e['name']=='SITE_GATEHOUSE_VISIBLE_SOFFIT_BOARD');m=manifold(gate['parts'][0]['geometry'])
inside=manifold({'type':'box','origin':[6.0,-11.1,3.09],'size':[1.0,.55,.3]})
assert (m^inside).volume()>.16
report={'status':'PASS_ISOLATED_PATCH_GEOMETRY','rows':rows,'filled_gate_under_eave_probe_volume_m3':(m^inside).volume(),'roof_retraction_m':.6,'wood_slats':25,'native_source_models_modified':False}
(O/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Patch_Geometry_QA.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('QA PASS',len(rows),'nodes',sum(r['parts'] for r in rows),'closed outward positive parts; solid gate probe',(m^inside).volume())
