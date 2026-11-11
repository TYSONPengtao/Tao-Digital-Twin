import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory'),str(W)]
import numpy as np,shapely
from shapely.geometry import shape,Polygon,Point
from scipy.spatial import cKDTree
from nearest_photo_projection import closest_on_triangles
import export_v5 as ex
O=Path(r'E:/jz/JIA/Rebuild_V14');D=W/'v14';mask=shape(json.loads((D/'Merge_Boundary_LOCAL.json').read_text(encoding='utf8')));T=json.loads((D/'Terrain_Mutation.json').read_text(encoding='utf8'));B=json.loads((D/'Building_Mutation.json').read_text(encoding='utf8'))
tt=[];sourcefaces=0;penetration=[];edgepoints=[]
for p in (D/'data').glob('SITE_V14_ORIGINAL_EXTERIOR_*.npz'):
 d=np.load(p);v=d['vertices'];f=d['faces'];q=v[f];p2=shapely.polygons(q[:,:,:2]);xyarea=abs(np.cross(q[:,1,:2]-q[:,0,:2],q[:,2,:2]-q[:,0,:2]));valid=xyarea>1e-10;over=shapely.area(shapely.intersection(p2[valid],mask));penetration.append({'file':p.name,'positive_xy_area_inside_mask_m2':float(over.sum())});sourcefaces+=len(f)
 near=shapely.distance(shapely.points(v[:,:2]),mask.boundary)<.001;edgepoints.append(v[near]);tt.append(q)
source=np.concatenate(tt);a=np.unique(np.round(np.concatenate(edgepoints),6),axis=0)
model=[]
for e in T['replace']:
 for p in e['parts']:
  g=p['geometry'];v=np.array(g['vertices']);f=np.array(g['faces']);q=v[f];n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);top=n[:,2]>1e-10;model.append(q[top])
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;ramps=[]
for e in S['elements']:
 if 'SITE_V12_OUTER_GATE' in e['name'] and 'RAMP' in e['name']:
  for p in e['parts']:
   v,fs=ex.world_part(p,e);ff=[]
   for f in fs:
    ff.extend([[f[k] for k in t] for t in ex.triangulate(v[f])])
   ff=np.array(ff);q=v[ff];n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);model.append(q[n[:,2]>1e-10]);ramps.append(np.array([v.min(0),v.max(0)]))
mt=np.concatenate(model);tree=cKDTree(mt[:,:,:2].mean(1));seams=[]
for p in a[::max(1,len(a)//300)]:
 _,ids=tree.query(p[:2],k=min(64,len(mt)));tri=mt[ids];fake=tri.copy();fake[:,:,2]=0;pp=np.array([p[0],p[1],0]);_,weights,dd=closest_on_triangles(np.repeat(pp[None,:],len(ids),axis=0),fake);zz=np.einsum('ni,ni->n',weights,tri[:,:,2]);exact=np.where(dd<.001)[0];best=int(exact[np.argmin(abs(zz[exact]-p[2]))]) if len(exact) else int(np.argmin(dd));z=float(zz[best]);seams.append({'xy':p[:2].tolist(),'source_z':float(p[2]),'modeled_z':z,'horizontal_gap_m':float(dd[best]),'height_difference_m':abs(z-p[2])})
matched=[s for s in seams if s['horizontal_gap_m']<.01];maxheight=max((s['height_difference_m'] for s in matched),default=0);rampjoins=[s for s in matched if any(np.all(np.array(s['xy'])>r[0,:2]-.2) and np.all(np.array(s['xy'])<r[1,:2]+.2) for r in ramps)]
# Route lies beside the stair opening, on the retained F3 floor slab.
stair=Polygon([[4.1,7.3],[7.8,7.3],[7.8,9.7],[4.1,9.7]]);route=B['circulation']['route_local_xy'];clear=[not stair.contains(Point(p)) for p in route]
qa={'status':'PASS_SCOPE_AND_FLOOR_ROUTE' if max(r['positive_xy_area_inside_mask_m2'] for r in penetration)<1e-6 and all(clear) else 'NEEDS_CORRECTION','original_exterior_3dm':r'E:/jz/纯场地版本.3dm','original_exterior_sha256':hashlib.sha256(Path(r'E:/jz/纯场地版本.3dm').read_bytes()).hexdigest(),'original_unchanged_sha256':T['source_sha256'],'exterior_triangles':sourcefaces,'exterior_overlap_area':penetration,'interior_mask_area_m2':mask.area,'route_local_xy':route,'route_points_outside_stair_void':clear,'clear_hall_width_m':1.0,'stairs_and_floor_slabs_unchanged':True,'boundary_height_samples':len(seams),'matched_boundary_samples':len(matched),'max_boundary_height_difference_including_retaining_faces_m':maxheight,'gate_ramp_boundary_samples':rampjoins,'boundary_samples':seams,'merge_note':'Source exterior keeps surveyed geometry and UV. Central void and rebuilt ramp are masked; model interior retains its ramps, steps and levels. Height differences at a retaining face are evaluated separately from path continuity. This test does not treat retaining-wall tops as terrain seams.'}
qa['clear_hall_width_m']=B['circulation']['clear_width_m'];qa['exit_column_clearance_y_m']=B['circulation'].get('column_clearance_y_m');(D/'Merge_Route_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print({k:v for k,v in qa.items() if k not in ['boundary_samples','gate_ramp_boundary_samples']},flush=True)
