from pathlib import Path
import json,numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';T=np.array(json.loads((D/'Coordinate_Seed.json').read_text())['seed_source_to_local'])
def data(rows,trans=None):
 vv=[];ff=[];offset=0
 for r in rows:
  a=np.load(D/r['file']);v=a['v'];f=a['f']
  if not len(v):continue
  if trans is not None:v=v@trans[:3,:3].T+trans[:3,3]
  vv.append(v);ff.append(f+offset);offset+=len(v)
 return np.concatenate(vv),np.concatenate(ff)
rows=json.loads((D/'Geometry_Index.json').read_text());cv,cf=data([r for r in rows if 'ORIGINAL_EXTERIOR_'in r['name']]);rv,rf=data(json.loads((D/'Decoded_L21_Index.json').read_text()),T)
bc=BVHTree.FromPolygons(cv.tolist(),cf.tolist(),all_triangles=True);br=BVHTree.FromPolygons(rv.tolist(),rf.tolist(),all_triangles=True);matches=json.loads((D/'SIFT_Matches.json').read_text());pairs=[]
for i,(x,y) in enumerate(zip(matches['source_xy'],matches['target_xy'])):
 a=br.ray_cast(Vector((*x,200)),Vector((0,0,-1)),400);b=bc.ray_cast(Vector((*y,200)),Vector((0,0,-1)),400)
 if a[0] is not None and b[0] is not None and abs(a[1].z)>.4 and abs(b[1].z)>.4:pairs.append({'match':i,'source':list(a[0]),'target':list(b[0]),'source_normal':list(a[1]),'target_normal':list(b[1])})
(D/'Landmarks_3D.json').write_text(json.dumps(pairs,indent=2));np.savez_compressed(D/'Registration_Clouds.npz',rv=rv,rf=rf,cv=cv,cf=cf);print('LANDMARKS',len(pairs),'triangles',len(cf),len(rf),flush=True)
