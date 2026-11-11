from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,union,cube
BASE=W/'v26_8_windows';D=BASE/'Prepared';FD=W/'v26_7/Final';prep=json.loads((BASE/'Prepared_Geometry.json').read_text('utf8'));J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);before=solid(a['v'],a['f']);house=before;checks=[]
def check(name,ok,**data):checks.append({'check':name,'pass':bool(ok),**data});print(name,bool(ok),data if not ok else'',flush=True)
def src(row):
 a=np.load(D/row['file']);return solid(a['v'],a['f'])
cuts=[]
for q in prep['house_recipe']:
 c=src(q['cut']);a=src(q['add']);cuts.append(c);house=(house-c)+a
for q in prep['glazing_clearance_recipe']:
 c=src(q['cut']);cuts.append(c);house-=c
check('Window recipe produces one closed positive main house',house.status()==mf.Error.NoError and len(house.decompose())==1,components=len(house.decompose()),volume_m3=house.volume())
delta=(before-house)+(house-before);outside=(delta-union(cuts)).volume()
check('Window changes remain within five front bay scopes',outside<1e-7,outside_difference_m3=outside)
heights=[]
for q in prep['house_recipe']:
 x=2. if q['side']=='L'else 11.;expected=q['target_sill_world_z_m'];hits=house.ray_cast([x,1.17,expected+1],[x,1.17,expected-.5]);h=next((h for h in hits if h.normal[2]>.99),None);heights.append({'floor':q['floor'],'side':q['side'],'expected_world_z_m':expected,'actual_top_m':h.position[2]if h else None,'pass':h is not None and abs(h.position[2]-expected)<.0001})
check('All five bay sill tops match user height/reference',all(h['pass']for h in heights),samples=heights)
glazing=[];preserved=[]
for r in prep['objects']:
 aa=np.load(D/r['file']);orig=np.load(FD/J[r['name']]['file']);preserved.append({'name':r['name'],'pass':np.array_equal(orig['v'][:,:2],aa['v'][:,:2])and np.array_equal(orig['f'],aa['f'])and np.array_equal(orig['mi'],aa['mi'])and np.array_equal(orig['uv'],aa['uv'])and J[r['name']]['materials']==r['materials']})
 glass_ids=[i for i,n in enumerate(r['materials'])if'Glass'in n]
 ff=aa['f'][np.isin(aa['mi'],glass_ids)]
 if not len(ff):continue
 g=solid(aa['v'],ff,r['name']);over=(g^house).volume();glazing.append({'name':r['name'],'glass_volume_m3':g.volume(),'opaque_intersection_m3':over,'pass':over<2e-8})
check('All adjusted window arrays retain XY topology UV and material ownership',all(q['pass']for q in preserved),objects=len(preserved),failures=[q for q in preserved if not q['pass']])
check('Retained lower glazing is clear of the resized opaque sill',all(q['pass']for q in glazing),components=len(glazing),failures=[q for q in glazing if not q['pass']])
check('All fifteen synthetic bay guard objects retired as user confirmed',len(prep['remove'])==15 and all(n.startswith('CONSTRUCTION_LOW_SILL_GUARD_BAY_WINDOW_F')for n in prep['remove']))
check('True stone balcony rail is outside every local mutation',not any('PHOTO_OPEN_STONE_RAIL'in r['name']for r in prep['objects'])and not any('PHOTO_OPEN_STONE_RAIL'in n for n in prep['remove']))
house=house.simplify(1e-6)
me=house.to_mesh64();v=np.array(me.vert_properties[:,:3]);f=np.array(me.tri_verts);t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5
check('Recipe does not create zero-area triangles',bool(np.all(area>1e-18)),zero_triangle_count=int(np.count_nonzero(area<=1e-18)),minimum_area_m2=float(area.min()))
np.savez_compressed(BASE/'QA_Candidate_House.npz',v=v,f=f)
result={'source_sha256':prep['source_sha256'],'scope':'Prepared cut/add geometry only; parent must re-run against native saved merged build','checks':checks,'all_pass':all(c['pass']for c in checks)}
(BASE/'Prepared_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('WINDOW_QA',sum(q['pass']for q in checks),len(checks),flush=True)
