from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,union,cube
BASE=W/'v26_8_windows';D=BASE/'Prepared';FD=W/'v26_7/Final';prep=json.loads((BASE/'Prepared_Geometry.json').read_text('utf8'));J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);before=solid(a['v'],a['f']);house=before;checks=[]
def check(name,ok,**data):checks.append({'check':name,'pass':bool(ok),**data});print(name,bool(ok),data if not ok else'',flush=True)
def src(row):
 a=np.load(D/row['file']);return solid(a['v'],a['f'])
ND=W/'v26_8/Final';NJ={r['name']:r for r in json.loads((ND/'Geometry_Index.json').read_text('utf8'))};actual=np.load(ND/NJ[HN]['file']);house=solid(actual['v'],actual['f'])
check('Saved resized house is one positive closed solid',house.status()==mf.Error.NoError and len(house.decompose())==1)
check('All15 proposal iron guards are absent from actual visible native model',len(prep['remove'])==15 and not any(n in NJ for n in prep['remove']))
heights=[]
for q in prep['house_recipe']:
 x=2. if q['side']=='L'else 11.;expected=q['target_sill_world_z_m'];hits=house.ray_cast([x,1.17,expected+1],[x,1.17,expected-.5]);h=next((h for h in hits if h.normal[2]>.99),None);heights.append({'floor':q['floor'],'side':q['side'],'expected_world_z_m':expected,'actual_top_m':h.position[2]if h else None,'pass':h is not None and abs(h.position[2]-expected)<.0001})
check('All five bay sill tops match user height/reference',all(h['pass']for h in heights),samples=heights)
glazing=[];preserved=[]
for r in prep['objects']:
 aa=np.load(ND/NJ[r['name']]['file']);expected=np.load(D/r['file']);check('Saved window matches prepared '+r['name'],aa['v'].shape==expected['v'].shape and np.max(abs(aa['v']-expected['v']))<3e-6 and np.array_equal(aa['f'],expected['f']));orig=np.load(FD/J[r['name']]['file']);preserved.append({'name':r['name'],'pass':np.allclose(orig['v'][:,:2],aa['v'][:,:2],atol=3e-6,rtol=0)and np.array_equal(orig['f'],aa['f'])and np.array_equal(orig['mi'],aa['mi'])and np.array_equal(orig['uv'],aa['uv'])and J[r['name']]['materials']==r['materials']})
 glass_ids=[i for i,n in enumerate(r['materials'])if'Glass'in n]
 ff=aa['f'][np.isin(aa['mi'],glass_ids)]
 if not len(ff):continue
 g=solid(aa['v'],ff,r['name']);over=(g^house).volume();glazing.append({'name':r['name'],'glass_volume_m3':g.volume(),'opaque_intersection_m3':over,'pass':over<2e-8})
check('All adjusted window arrays retain XY topology UV and material ownership',all(q['pass']for q in preserved),objects=len(preserved),failures=[q for q in preserved if not q['pass']])
check('Retained lower glazing is clear of the resized opaque sill',all(q['pass']for q in glazing),components=len(glazing),failures=[q for q in glazing if not q['pass']])
check('All fifteen synthetic bay guard objects retired as user confirmed',len(prep['remove'])==15 and all(n.startswith('CONSTRUCTION_LOW_SILL_GUARD_BAY_WINDOW_F')for n in prep['remove']))
check('True stone balcony rail is outside every local mutation',not any('PHOTO_OPEN_STONE_RAIL'in r['name']for r in prep['objects'])and not any('PHOTO_OPEN_STONE_RAIL'in n for n in prep['remove']))
# Validate the actual saved triangulation without simplifying it.
me=house.to_mesh64();v=np.array(me.vert_properties[:,:3]);f=np.array(me.tri_verts);t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5
check('Recipe does not create zero-area triangles',bool(np.all(area>1e-18)),zero_triangle_count=int(np.count_nonzero(area<=1e-18)),minimum_area_m2=float(area.min()))
rail='BALCONY_F2_PHOTO_OPEN_STONE_RAIL_Geometry';oldrail=np.load(FD/J[rail]['file']);newrail=np.load(ND/NJ[rail]['file']);check('Original F2 stone rail remains exact',all(np.array_equal(oldrail[k],newrail[k])for k in ['v','f','mi','uv']))
P=Path('E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend');fail=[c for c in checks if not c['pass']];result={'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'source_sha256':prep['source_sha256'],'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'height_samples':heights,'glazing_samples':glazing,'scope':'Actual final saved native readback, five front room bay groups; user confirmed no iron guards on all three floors.'}
(Path('E:/jz/JIA/Rebuild_V26_8/Reports')/'V26_8_Window_Sill_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print('SAVED_WINDOW_QA',len(checks),'FAIL',len(fail),flush=True)
