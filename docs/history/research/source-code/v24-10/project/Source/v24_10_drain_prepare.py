import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
import export_v5 as ex
D=W/'v24_10';S=json.loads(Path('E:/jz/JIA/Rebuild_V23/08_Editable_Source/Architecture_Scene_V23.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S
out=[]
for base in['SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE','SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE']:
 e=E[base];parts=[]
 for p in e['parts']:
  v,fs=ex.world_part(p,e);ff=[]
  for face in fs:
   if len(face)==3:ff.append(face)
   else:
    for t in ex.triangulate(v[face]):ff.append([face[k]for k in t])
  vv,iv=np.unique(np.round(v,9),axis=0,return_inverse=True);ff=iv[np.array(ff)];m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(vv),np.array(ff,dtype=np.uint64,order='C')))
  print('SOURCE',base,p['material'],p['geometry']['type'],m.status(),m.volume(),flush=True)
  assert m.status()==mf.Error.NoError
  cutter=mf.Manifold.cube([23.4-12.5,19.4-8.65,6.35]).translate([12.5,-19.4,-7]);m=m-cutter;assert m.status()==mf.Error.NoError and m.volume()>0
  me=m.to_mesh64();parts.append({'material':p['material'],'v':np.asarray(me.vert_properties[:,:3]).tolist(),'f':np.asarray(me.tri_verts).tolist()})
 out.append({'name':base+'_Geometry','parts':parts})
(D/'Closed_Legacy_Drain_Replacement.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8');print('PREPARED_CLOSED_DRAINS',len(out),flush=True)
