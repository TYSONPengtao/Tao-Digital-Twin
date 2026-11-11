"""Standalone V8 west farmyard clearance preparation. Reads V7 only. Writes isolated results."""
import sys,json,ast,math,hashlib,collections
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,shapely,mapbox_earcut
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from scipy.spatial import cKDTree,ConvexHull
from nearest_photo_projection import closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');out=W/'v8_terrain_clear';data=out/'data';data.mkdir(exist_ok=True)
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));B=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'));C=json.loads((O/'02_Data/Coordinate.json').read_text());rotation=np.array(C['local_to_survey'])[:3,:3];origin=np.array(C['origin']);hp=json.loads((O/'02_Data/Hole_Polygon.json').read_text());H=Polygon(hp['local']['outer'],hp['local']['holes'])
cal=json.loads((out/'Redline_Calibration.json').read_text());raw=Polygon(cal['raw_local_polygon']);remove=[r['name'] for r in I if r['name'].startswith(('SITE_SHED_1_','SITE_SHED_2_','SITE_SHED_3_','SITE_WEST_PERGOLA_'))]+['SITE_FARMYARD_TIMBER_FENCE','SITE_SW_METAL_ENTRY_GATE']
rawparts=[raw]
for r in I:
 if r['name'] in remove and r['name'].endswith(('ROOF','POSTS')):
  d=np.load(O/'02_Data'/r['file']);v=d['vertices'];p=Polygon(v[ConvexHull(v[:,:2]).vertices,:2]).buffer(.045);rawparts.append(p)
# Boundary stone enclosure stays; clearance does not carve its base/coping.
wallparts=[]
for r in I:
 if r['name'].startswith('SITE_PERIMETER_JOINED_RETAINING_WALL'):
  d=np.load(O/'02_Data'/r['file']);t=d['vertices'][d['faces']];ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));ps=shapely.polygons(t[ar>1e-11,:,:2]);wallparts.append(shapely.union_all(ps))
protect=unary_union(wallparts).buffer(.045)
clear=unary_union(rawparts).difference(protect).buffer(0)
maskmeta={'task':'Only terrain in west farmyard, full intersecting shed/pergola units removed','raw_redline_local':cal['raw_local_polygon'],'clearance':{'outer':list(clear.exterior.coords),'holes':[list(r.coords) for r in clear.interiors]} if clear.geom_type=='Polygon' else [{'outer':list(p.exterior.coords),'holes':[list(r.coords) for r in p.interiors]} for p in clear.geoms], 'area_m2':clear.area,'raw_redline_area_m2':raw.area,'bounds_local':clear.bounds,'removed_scene_and_patch_names':remove,'preserved_boundary_elements':'SITE_PERIMETER_JOINED_RETAINING_WALL* (45mm guard)','calibration_rms_pixels':cal['fit_rms_pixels'],'scope_note':'Editing polygon includes entire shed/pergola footprints crossing the coarse red brush. No source file is overwritten. Kitchen/gatehouse/screenwall/main architecture untouched.'}
(out/'Terrain_Clearance_Polygon.json').write_text(json.dumps(maskmeta,ensure_ascii=False,indent=2),encoding='utf-8')
# Isolate pure XY clipping helpers from old pipeline.
tree=ast.parse((W/'build_v6_patch.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','polygon_tris','clip_half','clipped']],type_ignores=[]),'<clip helpers>','exec'))
# Ground support from actual original measured UV surfaces. Up-facing/low/locally smooth ground only.
grow=next(r for r in I if r['name']=='PHOTO_BOUNDARY_GROUND_RECOVERY');gd=np.load(O/'02_Data'/grow['file']);gt=gd['vertices'][gd['faces']];gu=gd['uv'][gd['faces']];gm=gd['material_ids'];gc=gt.mean(1);gn=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);gn/=np.linalg.norm(gn,axis=1)[:,None];zone=clear.buffer(2.0)
near=shapely.contains_xy(zone,gc[:,0],gc[:,1]);groundlike=near&(abs(gn[:,2])>.70)&(gt[:,:,2].max(1)-gt[:,:,2].min(1)<.22)&(gc[:,2]<.3)
cp=gc[groundlike];cells=np.floor(cp[:,:2]*2).astype(int);samples=[]
for key in set(map(tuple,cells)):
 idx=np.flatnonzero((cells==key).all(1));q=cp[idx];lo=np.percentile(q[:,2],15);sel=np.argmin(abs(q[:,2]-lo));samples.append(q[sel])
samples=np.array(samples);tree=cKDTree(samples[:,:2]);ids=tree.query_ball_point(samples[:,:2],1.4);accept=[]
for j,nn in enumerate(ids):
 low=np.percentile(samples[nn,2],25);accept.append(samples[j,2]<=low+.16)
samples=samples[np.array(accept)];tree=cKDTree(samples[:,:2]);print('support ground samples',len(samples),'z range',samples[:,2].min(),samples[:,2].max(),flush=True)
def height(xy):
 dist,idx=tree.query(np.asarray(xy),k=min(12,len(samples)));weight=1/np.maximum(dist,.075)**2;z=(weight*samples[idx,2]).sum(1)/weight.sum(1);return z
# Conservative absolute test removes car/stack tops present in the V6 low surface cache.
zz=height(gt[:,:,:2].reshape(-1,2)).reshape(-1,3);ok=groundlike&(gt[:,:,2]-zz<.13).all(1)&(gt[:,:,2]-zz>-.35).all(1)
direct=[];directuv=[];directm=[]
for j in np.flatnonzero(ok):
 for tt in clipped(gt[j],clear):
  if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-11:continue
  _,bw,_=closest_on_triangles(tt,np.repeat(gt[j][None,:,:],3,axis=0));direct.append(tt);directuv.append(bw@gu[j]);directm.append(grow['materials'][int(gm[j])])
direct=np.array(direct);covered=shapely.union_all(shapely.polygons(direct[:,:,:2]));gaps=clear.difference(covered).buffer(0);print('direct measured ground',len(direct),'coverage',covered.area,'gaps',gaps.area,flush=True)
fill=[];filluv=[];step=.4;b=clear.bounds
for x in np.arange(math.floor(b[0]/step)*step,b[2]+step,step):
 for y in np.arange(math.floor(b[1]/step)*step,b[3]+step,step):
  cell=Polygon([(x,y),(x+step,y),(x+step,y+step),(x,y+step)]).intersection(gaps)
  for p in polys(cell):
   if p.area<1e-10:continue
   for xy in polygon_tris(p):
    tt=np.column_stack([xy,height(xy)]);n=np.cross(tt[1]-tt[0],tt[2]-tt[0]);
    if np.linalg.norm(n)<=1e-10:continue
    if n[2]<0:tt=tt[[0,2,1]]
    fill.append(tt);filluv.append(tt[:,:2])
newrows=[]
def save_ground(name,tri,uv,mat,role):
 v=np.array(tri).reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3);materials=list(dict.fromkeys(mat));mid=np.array([materials.index(m) for m in mat],np.int32);fn=name+'.npz';np.savez_compressed(data/fn,vertices=v,faces=f,uv=np.array(uv).reshape(-1,2),material_ids=mid)
 e={'name':name,'layer':'60_SITE','family':'SITE_MODEL','confidence':'HIGH' if 'MEASURED' in name else 'MEDIUM','source':'V7 original measured low ground UV triangles' if 'MEASURED' in name else 'Locally screened measured earth-ground support samples; inverse-distance interpolation over scan occlusion','role':role}
 r={'index':0,'file':fn,'name':name,'element':e,'materials':materials,'triangles':len(tri),'vertices':len(v),'role':role,'photo_triangles':len(tri) if 'MEASURED' in name else 0};newrows.append(r)
save_ground('V8_WEST_CLEARED_MEASURED_GROUND',direct,directuv,directm,'ORIGINAL_MEASURED_EARTH_TERRAIN_RETAINED_AFTER_BUILDING_REMOVAL')
save_ground('V8_WEST_CLEARED_INTERPOLATED_GROUND',fill,filluv,['M_V8_West_Earth']*len(fill),'GROUND_INTERPOLATION_ONLY_OVER_SCAN_OCCLUDED_DEMOLISHED_BUILDING_FOOTPRINTS')
np.savez_compressed(data/'V8_Measured_Ground_Support.npz',points=samples)
# Remove all old cached ground/photo fragments inside edit zone. All outside triangles/UV retained exactly.
replacement_rows=[];replaced_names=[];patchstats=[]
terrainrows={'PHOTO_BOUNDARY_GROUND_RECOVERY','PHOTO_BOUNDARY_SURFACE_RECOVERY','PHOTO_BOUNDARY_RESIDUAL_RECOVERY','PHOTO_BOUNDARY_RECOVERY','PHOTO_RIM_TRANSITION','SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD','SITE_CURVED_PUBLIC_ROAD','SITE_CONTEXT_TERRAIN','SITE_SW_GATE_APPROACH','SITE_SW_GATE_THRESHOLD'}
for r in I:
 if r['name'] not in terrainrows:continue
 d=np.load(O/'02_Data'/r['file']);t=d['vertices'][d['faces']];uv=d['uv'][d['faces']];mi=d['material_ids'];mins=t[:,:,:2].min(1);maxs=t[:,:,:2].max(1);b=clear.bounds;cand=np.flatnonzero((maxs[:,0]>=b[0])&(mins[:,0]<=b[2])&(maxs[:,1]>=b[1])&(mins[:,1]<=b[3]));hits=shapely.intersects(shapely.polygons(t[cand,:,:2]),clear);touch=cand[hits]
 if not len(touch):continue
 outside=clear.buffer(100).difference(clear);touchset=set(touch);tr=[];tu=[];tm=[];changed=0
 for j,tt in enumerate(t):
  if j not in touchset:tr.append(tt);tu.append(uv[j]);tm.append(int(mi[j]));continue
  for q in clipped(tt,outside):
   if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))<1e-11:continue
   _,bw,_=closest_on_triangles(q,np.repeat(tt[None,:,:],3,axis=0));tr.append(q);tu.append(bw@uv[j]);tm.append(int(mi[j]))
  changed+=1
 if tr:
  fn='V8_Clearance_'+r['name']+'.npz';v=np.array(tr).reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3);np.savez_compressed(data/fn,vertices=v,faces=f,uv=np.array(tu).reshape(-1,2),material_ids=np.array(tm,np.int32));nr=dict(r,file=fn,triangles=len(tr),vertices=len(v),clearance_revision='V8 west-yard terrain-only edit zone');replacement_rows.append(nr)
 else:remove.append(r['name'])
 replaced_names.append(r['name']);patchstats.append({'name':r['name'],'source_triangles':len(t),'touched_triangles':len(touch),'retained_output_triangles':len(tr)})
 print('cleared patch',r['name'],len(touch),len(tr),flush=True)
# Derivative base edit; source file stays untouched. Whole outside faces and source attributes retain exact values.
basestats=[];basereplacements=[]
for br in B:
 d=np.load(O/'02_Data'/f'Base_{br["index"]}.npz');v=d['vertices'];vl=(v-origin)@rotation;f=d['faces'];t=vl[f[:,:3]];bb=clear.bounds;mins=t[:,:,:2].min(1);maxs=t[:,:,:2].max(1);cand=np.flatnonzero((maxs[:,0]>=bb[0])&(mins[:,0]<=bb[2])&(maxs[:,1]>=bb[1])&(mins[:,1]<=bb[3]));hit=shapely.intersects(shapely.polygons(t[cand,:,:2]),clear);touch=set(map(int,cand[hit]));
 if not touch:basestats.append({'index':br['index'],'changed':False,'touched_faces':0});continue
 nv=v.tolist();nu=d['uv'].tolist();nn=d['normals'].tolist();nf=[];clipcount=0;outside=clear.buffer(100).difference(clear)
 for j,face in enumerate(f):
  if j not in touch:nf.append(face.tolist());continue
  sub=[face[:3]] if face[2]==face[3] else [face[:3],face[[0,2,3]]]
  for ids0 in sub:
   tt=vl[ids0]
   for q in clipped(tt,outside):
    if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))<1e-11:continue
    _,bw,_=closest_on_triangles(q,np.repeat(tt[None,:,:],3,axis=0));newuv=bw@d['uv'][ids0];newnormal=bw@d['normals'][ids0];newnormal/=np.maximum(np.linalg.norm(newnormal,axis=1)[:,None],1e-16);ids1=[]
    for k in range(3):ids1.append(len(nv));nv.append((q[k]@rotation.T+origin).tolist());nu.append(newuv[k].tolist());nn.append(newnormal[k].tolist())
    nf.append(ids1+[ids1[2]]);clipcount+=1
 fn=f'Base_{br["index"]}.npz';np.savez_compressed(data/fn,vertices=np.array(nv),faces=np.array(nf,np.int32),uv=np.array(nu),normals=np.array(nn));nbr=dict(br,vertices=len(nv),faces=len(nf),uv_count=len(nu),v8_source_edit='West redline clearance only; original arrays preserved as prefix; clipped crossing faces retain barycentric source UV/normals');basereplacements.append(nbr);basestats.append({'index':br['index'],'changed':True,'touched_faces':len(touch),'output_clipped_triangles':clipcount,'source_faces':len(f),'output_faces':len(nf),'original_vertex_uv_normal_prefix_exact':True});print('base clip',br['index'],len(touch),len(nf),flush=True)
# Geometric projection QA independent of native export.
allground=np.concatenate([direct,np.array(fill)]);cov=shapely.union_all(shapely.polygons(allground[:,:,:2]));res=clear.difference(cov).area;outsidearea=cov.difference(clear).area
qa={'status':'PASS','clearance_area_m2':clear.area,'screenshot_reprojection_rms_pixels':cal['fit_rms_pixels'],'removed_modeled_components':remove,'measured_ground_triangles':len(direct),'interpolated_ground_triangles':len(fill),'measured_ground_support_points':len(samples),'measured_ground_uv_original_barycentric':True,'original_source_files_modified':False,'ground_projection_residual_m2':res,'ground_outside_clearance_m2':outsidearea,'max_ground_elevation_local_m':float(allground[:,:,2].max()),'min_ground_elevation_local_m':float(allground[:,:,2].min()),'interpolation_grid_m':step,'support_filter':'Up-facing |normal.z|>.70; centroid z<.3m; face z spread<.22m; lower 15th percentile 0.5m cells; exclude elevated cell envelope; source faces within +.13/-0.35m of local earth envelope','patch_replacements':patchstats,'base_edits':basestats,'limits':'Screenshot polygon and terrain in formerly occluded shed floors are estimated, not a field-controlled demolition or surveying drawing. No roof geometry is lowered into the terrain.'}
assert res<1e-6,(res,'ground hole');assert outsidearea<1e-7,(outsidearea,'ground outside');assert allground[:,:,2].max()<.5
(out/'Terrain_Clearance_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');(out/'Merge_Manifest.json').write_text(json.dumps({'delete_names':remove,'replacement_patch_rows':replacement_rows,'new_patch_rows':newrows,'replacement_base_rows':basereplacements,'material_additions':{'M_V8_West_Earth':{'color':[147,122,88],'roughness':.95,'role':'Unmeasured earth surface under removed shelters; no invented photographic roof projection'}}},ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE QA',qa['measured_ground_triangles'],qa['interpolated_ground_triangles'],clear.area,res,outsidearea,flush=True)
