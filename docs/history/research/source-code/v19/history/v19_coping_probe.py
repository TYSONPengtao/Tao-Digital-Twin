import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
t=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<helpers>','exec'))
Q=json.loads((W/'v19/Mutation.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']+Q['add']}
from collections import Counter
def raw(g):
 v=np.array(g['vertices'],np.float64);f=np.array(g['faces'],np.uint64);a=mf.Manifold(mf.Mesh64(v,f))
 print('RAW',len(v),len(f),a.status(),dict(Counter(Counter(tuple(sorted((int(x),int(y)))) for t in f for x,y in zip(t,np.roll(t,-1))).values())),flush=True)
 if a.status()!=mf.Error.NoError:
  _,ix,rev=np.unique(np.round(v,10),axis=0,return_index=True,return_inverse=True);a=mf.Manifold(mf.Mesh64(v[ix],rev[f].astype(np.uint64)));print('WELDED',a.status(),flush=True)
 assert a.status()==mf.Error.NoError
 return a
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 body=mf.Manifold.batch_boolean([raw(p['geometry']) for p in E[n]['parts']],mf.OpType.Add);cap=raw(E[n+'_TILE_COPING']['parts'][0]['geometry']);parts=cap.decompose();rows=[]
 for j,a in enumerate(parts):
  v=np.asarray(a.to_mesh64().vert_properties)[:,:3];vol=(a^body).volume()
  if len(v):rows.append({'component':j,'volume':a.volume(),'min':v.min(0).round(6).tolist(),'max':v.max(0).round(6).tolist(),'vertices':len(v),'wall_overlap_m3':vol})
  else:rows.append({'component':j,'volume':a.volume(),'vertices':0,'wall_overlap_m3':vol})
 rows.sort(key=lambda r:r['volume'],reverse=True);print(n,'body',len(body.decompose()),'cap',len(parts),'combined',len((body+cap).decompose()),flush=True);print(json.dumps(rows,indent=2),flush=True)
