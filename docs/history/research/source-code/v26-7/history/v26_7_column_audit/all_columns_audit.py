from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')];import numpy as np,manifold3d as mf
D=W/'v26_7_column_audit';FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';A=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));R={r['name']:r for r in A['objects']}
def load(p):
 a=np.load(p);v,ix=np.unique(a['v'],axis=0,return_inverse=True);return mf.Manifold(mf.Mesh64(v.astype(float),ix[a['f']].astype(np.uint64)))
old=load(FD/J[HN]['file']);new=load(D/R[HN]['file'])
def inside(m,p):
 x,y,z=p;hs=m.ray_cast([x-40,y,z],[x+40,y,z]);return sum(h.position[0]<x for h in hs)%2==1
rows=[]
cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
for r in cp:
 n=r['name']
 if not n.startswith('KZ_'):continue
 lo,hi=np.array(r['bounds_m']);cx,cy=(lo+hi)[:2]/2;z=lo[2]+.6;sample=[]
 for sx in[-1,1]:
  for sy in[-1,1]:
   x,y=cx+sx*.16,cy+sy*.16
   if x<.12 or x>12.88 or y<2.22 or y>9.68:continue
   p=[float(x),float(y),float(z)];o=inside(old,p);v=inside(new,p);sample.append({'point_m':p,'source_occupied':o,'candidate_occupied':v})
 rows.append({'name':n,'source_column_xy_m':[[float(lo[0]),float(lo[1])],[float(hi[0]),float(hi[1])]],'probe_z_m':float(z),'interior_quadrant_probes':sample,'remaining_unsupported_quadrants':sum(q['candidate_occupied']for q in sample)})
(D/'All_Columns_First_Candidate_Audit.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for r in rows:
 if r['remaining_unsupported_quadrants']:print(r['name'],r['remaining_unsupported_quadrants'])
print('ALL',len(rows),'REMAINING_COLUMNS',sum(bool(r['remaining_unsupported_quadrants'])for r in rows))
