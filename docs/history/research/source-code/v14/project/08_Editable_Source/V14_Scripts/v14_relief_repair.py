import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex,manifold3d as mf
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S
for file,names in [('v14_assemble.py',['mesh']),('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'helpers','exec'))
Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));e=next(e for e in Q['replace'] if e['name']=='SITE_PERIMETER_JOINED_RETAINING_WALL_0_PLASTER_STEPPED_RELIEF');ps=[];rep=[]
for i,p in enumerate(e['parts']):
 try:mesh(p['geometry']);ps.append(p)
 except AssertionError:
  g0=p['geometry'];g=dict(g0);g['type']='mesh'
  # Keep the original closed CSG triangulation: generic polyhedron conversion
  # discarded five near-collinear boundary facets and opened the two relief pieces.
  mesh(g);ps.append({'geometry':g,'material':p['material']});rep.append({'original_part':i,'repair':'Preserved raw valid closed CSG mesh boundary triangles; no vertex or face moved'});continue
  m=mf.Manifold(mf.Mesh64(np.array(g0['vertices'],np.float64),np.array(g0['faces'],np.uint64)));assert m.status()==mf.Error.NoError
  print('REPAIR',i,'volume',m.volume(),'components',len(m.decompose()),flush=True);fixed=None
  for tol in [1e-6,1e-5,1e-4]:
   g=fromman(m.simplify(tol))
   try:mesh(g);fixed=[{'geometry':g,'material':p['material']}];rep.append({'original_part':i,'max_simplification_m':tol,'volume_difference_m3':abs(m.volume()-manifold(g).volume())});break
   except AssertionError:pass
  if fixed is None:
   gs=[fromman(mm.simplify(1e-5)) for mm in m.decompose()]
   for g in gs:mesh(g)
   fixed=[{'geometry':g,'material':p['material']} for g in gs];rep.append({'original_part':i,'split_closed_components':len(gs)})
  ps.extend(fixed)
e['parts']=ps;Q['relief_mesh_repair']=rep;(W/'v14/Building_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('REPAIRED',rep,flush=True)
