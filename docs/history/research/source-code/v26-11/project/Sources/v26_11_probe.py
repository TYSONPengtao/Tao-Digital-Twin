from v26_2_common import *
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
D=W/'v26_11';D.mkdir(exist_ok=True);FD=W/'v26_10/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';r=J[HN];a=np.load(FD/r['file']);v,f=a['v'],a['f'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*area[:,None],1e-30);m=solid(v,f);mats=r['materials'];rows=[]
core=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];(D/'Source_Core.json').write_text(json.dumps(core,indent=2),'utf8')
for fl,z in [(1,-.44999998807907104),(2,3.450024366378784),(3,7.050000190734863)]:
 for y in [2.1,7.3,9.8]:
  ids=np.flatnonzero((no[:,2]>.999)&(t[:,:,2].max(1)<z+.005)&(t[:,:,2].min(1)>z-.005)&(t[:,:,1].mean(1)>y-.5)&(t[:,:,1].mean(1)<y+.5))
  for i in ids:
   mat=mats[int(a['mi'][i])]
   if mat=='M_Floor':continue
   rows.append({'floor':fl,'wall_y':y,'triangle':int(i),'material':mat,'area_m2':float(area[i]),'bounds':[t[i].min(0).tolist(),t[i].max(0).tolist()]})
print('FLOOR_NONFLOOR',len(rows),flush=True)
for q in rows:
 if q['area_m2']>.0005:print(json.dumps(q),flush=True)
sections=[]
for fl,z0 in [(1,-.44999998807907104),(2,3.450024366378784),(3,7.050000190734863)]:
 for y in[2.1,7.3]:
  for z in [z0+.7,z0+2.7,z0+3.02,z0+3.14,z0+3.4,z0+3.74]:
   loops=m.slice(z).to_polygons();sections.append({'floor':fl,'z':z,'wall_y':y,'lines':[p.tolist()for p in loops]})
(D/'Floor_Material_Faces.json').write_text(json.dumps(rows,indent=2),'utf8');(D/'Section_Probe.json').write_text(json.dumps(sections),'utf8')
for n in J:
 if any(s in n for s in['ROMAN','COLUMN','BALCONY_EDGE','ENTRY','PORCH','LOWERED']):print('OBJECT',n,J[n]['bounds'],flush=True)
print('CORES',[(q['name'],q['bounds_m'])for q in core if ('KZ_'in q['name']or'BEAM_'in q['name'])],flush=True)
