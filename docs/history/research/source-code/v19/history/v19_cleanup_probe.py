import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
t=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented']],type_ignores=[]),'<helpers>','exec'))
Q=json.loads((W/'v19/Mutation.json').read_text(encoding='utf8'))
for e in Q['replace']+Q['add']:
 for j,p in enumerate(e['parts']):
  g=p['geometry'];v=np.asarray(g['vertices']);f=np.asarray(g['faces']);a=mf.Manifold(mf.Mesh64(v,f.astype(np.uint64)));rows=[]
  for tol in [1e-7,1e-6,1e-5]:
   b=mf.Manifold.batch_boolean([k for k in a.decompose() if k.volume()>1e-10],mf.OpType.Add).set_tolerance(tol).simplify(tol)
   m=b.to_mesh64();vv=np.asarray(m.vert_properties)[:,:3];ff=np.asarray(m.tri_verts);tt=vv[ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)
   try:oriented({'type':'polyhedron','vertices':vv.tolist(),'faces':ff.tolist()});ok=True
   except ValueError:ok=False
   rows.append({'tol':tol,'kept_components':len(b.decompose()),'triangles':len(ff),'min_area':float(ar.min()),'small_facets':int((ar<1e-12).sum()),'oriented_pass':ok})
   if ok:break
  print(e['name'],j,json.dumps(rows),flush=True)
