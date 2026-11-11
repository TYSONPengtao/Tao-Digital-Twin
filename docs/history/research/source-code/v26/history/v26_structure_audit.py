from pathlib import Path
import sys,json,re
W=Path(__file__).parent;D=W/'v26';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from v24_16_common import solid,cube,union
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
solids={};rows=[]
for n,r in I.items():
 if not n.startswith(('KZ_','BEAM_','SLAB_JOINED','FACADE_CONTINUOUS','PARTITIONS_JOINED','STAIR_F','STAIR_LANDING','ROOF_MAIN')):continue
 a=np.load(D/r['file'])
 try:
  m=solid(a['v'],a['f'],n);solids[n]=m
  parts=m.decompose();row={'name':n,'status':str(m.status()),'volume_m3':m.volume(),'components':len(parts),'bounds':r['bounds']}
  if n.startswith(('STAIR_','PARTITIONS','FACADE')):
   row['component_bounds']=[list(p.bounding_box()) for p in parts];row['component_volumes']=[p.volume() for p in parts]
  rows.append(row)
 except Exception as ex:rows.append({'name':n,'error':str(ex)})
print('SOLIDS',len(solids),'ERRORS',[r for r in rows if 'error'in r],flush=True)

def vol(a,b):return max(0.,(a^b).volume())
def plan(m,z):
 ps=[Polygon(p) for p in m.slice(z).to_polygons() if len(p)>2]
 return unary_union(ps).buffer(0)

checks=[]
for fl,z in [(1,-.45),(2,3.450024414),(3,7.05)]:
 for n in [n for n in solids if n.startswith('BEAM_') and f'_F{fl}_'in n]:
  m=solids[n];lo,hi=np.array(I[n]['bounds']);axis=0 if n.startswith('BEAM_X') else 1
  hits=[]
  for end,coord in [('A',lo[axis]),('B',hi[axis])]:
   p=(lo+hi)/2;p[axis]=coord
   cols=[k for k in solids if k.startswith('KZ_') and f'_F{fl}_'in k]
   near=[]
   for k in cols:
    qlo,qhi=np.array(I[k]['bounds']);gap=np.maximum(0,np.maximum(qlo-p,p-qhi));dist=np.linalg.norm(gap)
    if dist<.5:near.append((float(dist),k))
   near.sort();hits.append({'end':end,'position':p.tolist(),'near_columns':near[:2]})
  checks.append({'beam':n,'ends':hits,'above_slab_gap_m':I.get(f'SLAB_JOINED_F{fl+1}_Geometry',{}).get('bounds',[[0,0,hi[2]]])[0][2]-hi[2]})
for fl in [1,2]:
 for k in [1,2]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';m=solids[n];others=[f'SLAB_JOINED_F{fl}_Geometry',f'SLAB_JOINED_F{fl+1}_Geometry',f'STAIR_LANDING_F{fl}_Geometry',f'PARTITIONS_JOINED_F{fl}_Geometry',f'FACADE_CONTINUOUS_F{fl}_Geometry']
  checks.append({'stair':n,'bounds':I[n]['bounds'],'support_intersections_m3':{b:vol(m,solids[b]) for b in others}})
for fl in [1,2,3]:
 for kind in ['FACADE_CONTINUOUS','PARTITIONS_JOINED']:
  n=f'{kind}_F{fl}_Geometry';m=solids[n]
  checks.append({'walls':n,'components':len(m.decompose()),'vertical_connections':[{'to':b,'intersection_m3':vol(m,solids[b])} for b in solids if (b.startswith('KZ_') and f'_F{fl}_' in b) or b==f'SLAB_JOINED_F{fl}_Geometry']})
report={'base':str(D/'Base.json'),'solids':rows,'checks':checks,'not_structural_capacity_calculation':True}
(D/'Structure_Before.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for r in checks:
 if 'stair'in r:print(json.dumps(r),flush=True)
for fl in [1,2,3]:
 for z in [{1:.8,2:4.5,3:8.1}[fl],{1:3.2,2:6.8,3:10.1}[fl]]:
  for kind in ['PARTITIONS_JOINED','FACADE_CONTINUOUS']:
   n=f'{kind}_F{fl}_Geometry';p=plan(solids[n],z).intersection(box(3.3,6.8,9.6,10.25));(D/f'Plan_{kind}_F{fl}_{z}.json').write_text(json.dumps(p.__geo_interface__),encoding='utf8')
print('AUDIT_DONE',len(checks),flush=True)
