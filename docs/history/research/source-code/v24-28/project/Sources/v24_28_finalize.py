"""Remove the construction seam inside the new perpendicular white wall."""
from pathlib import Path
import json,sys
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import v24_16_common as g
import numpy as np
p=W/'v24_28/Prepared_Geometry.json';a=json.loads(p.read_text('utf8'));rows=a['objects']
fill=next((r for r in rows if r['name']=='V24_28_Perpendicular_White_Wall_Fill'),None)
face=next(r for r in rows if r['name']=='V24_28_Continuous_White_Courtyard_Wall_Face')
parts=g.solid(face['v'],face['f']).decompose()
if fill:parts+=g.solid(fill['v'],fill['f']).decompose()
if fill or len(parts)>1:
 core=max(parts,key=lambda p:p.volume());q=core.to_mesh64();v=np.array(q.vert_properties[:,:3]);f=np.array(q.tri_verts)
 for axis,values in [(0,[14.115]),(1,[-2.855,10.25]),(2,[-.55,2.44720006])]:
  for value in values:v[abs(v[:,axis]-value)<1e-6,axis]=value
 core=g.solid(v,f);coat=g.cube([14.10,-2.855,-.55],[14.116,10.25,2.44720006]);m=g.union([core,coat]);q=m.to_mesh64()
 assert len(m.decompose())==1,('White wall still disconnected',len(m.decompose()))
 g.solid(np.array(q.vert_properties[:,:3],np.float32).astype(float),q.tri_verts)
 face.update(v=q.vert_properties[:,:3].tolist(),f=q.tri_verts.tolist(),volume_m3=m.volume(),bodies=1)
 a['objects']=[r for r in rows if r is not fill]
a['proof']['facing_white_wall']['new_white_wall_is_one_closed_solid']=True
a['proof']['facing_white_wall']['internal_construction_face_removed']=True
p.write_text(json.dumps(a,ensure_ascii=False,separators=(',',':')),encoding='utf8');print('FINALIZED_ONE_WHITE_WALL',face['bodies'],face['volume_m3'],flush=True)
