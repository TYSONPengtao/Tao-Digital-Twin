"""Replace invented terrain in the hole with surveyed photo geometry.
Only newly added patch data is rewritten; original five source meshes are read only.
"""
import sys,json,math,ast,collections
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,mapbox_earcut,shapely
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from nearest_photo_projection import PhotoProjector,closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid')
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'))
a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a)
T=np.eye(4);T[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]];T[:3,3]=C['origin']
hp=json.loads((O/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'))
H=Polygon(hp['local']['outer'],hp['local']['holes'])
tree=ast.parse((W/'build_v6_patch.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','polygon_tris','clip_half','clipped']],type_ignores=[]),'<clip helpers>','exec'))
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
terrain_names={'SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD','SITE_CURVED_PUBLIC_ROAD','SITE_EAST_GARDEN','SITE_CONTEXT_TERRAIN','SITE_SW_GATE_APPROACH','SITE_SW_GATE_THRESHOLD'}
# Snapshot once, so this repair can be rerun without consuming its own output.
snapshot=O/'02_Data/Patch_Index_Before_Ground_Repair.json'
if not snapshot.exists():snapshot.write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
else:I=json.loads(snapshot.read_text(encoding='utf-8'))
P=PhotoProjector.from_objs(sorted(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj')),np.linalg.inv(T))
t=P.triangles;n=P.normals
band=H.difference(H.buffer(-.22))
low_ground=(t[:,:,2].max(axis=1)<1.4)&(np.abs(n[:,2])>.35)
low_retaining=(t[:,:,2].max(axis=1)<.6)
bb=H.bounds;mn=t[:,:,:2].min(axis=1);mx=t[:,:,:2].max(axis=1)
inbb=(mx[:,0]>=bb[0])&(mn[:,0]<=bb[2])&(mx[:,1]>=bb[1])&(mn[:,1]<=bb[3])
candidates=np.flatnonzero(inbb)
xyareas=np.abs(np.cross(t[candidates,1,:2]-t[candidates,0,:2],t[candidates,2,:2]-t[candidates,0,:2]))/2
positive=candidates[xyareas>1e-12]
geoms=shapely.polygons(t[positive,:,:2]);hit=shapely.intersects(geoms,H)
pos=positive[hit];geoms=geoms[hit]
edge=shapely.intersects(geoms,band)
select=np.flatnonzero((low_ground[pos]|low_retaining[pos])|edge)
ground_tri=[];ground_uv=[];ground_m=[];border_tri=[];border_uv=[];border_m=[]
for j in select:
 i=int(pos[j]);isground=bool(low_ground[i] or low_retaining[i]);mask=H if isground else band
 for tt in clipped(t[i],mask):
  if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-10:continue
  _,bw,_=closest_on_triangles(tt,np.repeat(t[i][None,:,:],3,axis=0))
  lists=(ground_tri,ground_uv,ground_m) if isground else (border_tri,border_uv,border_m)
  lists[0].append(tt);lists[1].append(bw@P.uv[i]);lists[2].append('PATCH_PHOTO_'+str(P.material_ids[i]))
 print('',end='') if j%20000 else None
print('Measured donor triangles',len(ground_tri),'border',len(border_tri),flush=True)
ground_cov=shapely.union_all(shapely.polygons(np.array(ground_tri)[:,:,:2]))
# The original donor replaces uncertain terrain; modeled fallback is restricted
# to scan-occluded areas, and never supplies the visible outer boundary band.
fallback_mask=H.difference(ground_cov.union(band))
newindex=[r for r in I if r['name'] not in terrain_names]
def save(name,e,tri,uv,mat,role):
 if not len(tri):return
 fn='GroundRepair_'+name+'.npz';ms=list(dict.fromkeys(mat));mid=np.array([ms.index(m) for m in mat],np.int32)
 v=np.array(tri).reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3)
 np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=f,uv=np.array(uv).reshape(-1,2),material_ids=mid)
 newindex.append(dict(index=len(newindex),file=fn,name=name,element=e,materials=ms,triangles=len(tri),vertices=len(v),role=role,photo_triangles=sum(m.startswith('PATCH_PHOTO_') for m in mat)))
e={'name':'PHOTO_BOUNDARY_GROUND_RECOVERY','layer':'60_SITE','family':'SITE_MODEL','confidence':'HIGH','source':'Original JIA surveyed OBJ triangles and barycentric original photo UV, clipped exclusively to missing region'}
save(e['name'],e,ground_tri,ground_uv,ground_m,'ORIGINAL_PHOTO_GROUND_RECOVERY')
e=dict(e,name='PHOTO_BOUNDARY_SURFACE_RECOVERY',source='Original JIA photo surfaces in 0.22m hole-side edge strip; original base is unchanged')
save(e['name'],e,border_tri,border_uv,border_m,'ORIGINAL_PHOTO_EDGE_SURFACE_RECOVERY')
fallback_count=0
for row in I:
 if row['name'] not in terrain_names:continue
 d=np.load(O/'02_Data'/row['file']);tr=d['vertices'][d['faces']];tu=d['uv'][d['faces']];mi=d['material_ids'];ft=[];fu=[];fm=[]
 for j,t0 in enumerate(tr):
  for tt in clipped(t0,fallback_mask):
   if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-10:continue
   _,bw,_=closest_on_triangles(tt,np.repeat(t0[None,:,:],3,axis=0));ft.append(tt);fu.append(bw@tu[j]);fm.append(row['materials'][int(mi[j])])
 save(row['name'],row['element'],ft,fu,fm,'MODELED_GROUND_FALLBACK_ONLY_IN_SCAN_OCCLUDED_INTERIOR')
 fallback_count+=len(ft)
 print('ground fallback',row['name'],len(ft),flush=True)
coverage=[]
for i,row in enumerate(newindex):
 row['index']=i;d=np.load(O/'02_Data'/row['file']);tr=d['vertices'][d['faces']];areas=np.abs(np.cross(tr[:,1,:2]-tr[:,0,:2],tr[:,2,:2]-tr[:,0,:2]))/2
 coverage.append(shapely.union_all(shapely.polygons(tr[areas>1e-10,:,:2])))
covered=unary_union(coverage);residual=H.difference(covered)
# Photo triangles supply any remaining gaps directly, including occluded ground
# beneath the clean building. No cross-boundary extrapolation or guessed UV.
if residual.area>1e-6:
 rt=[];ru=[];rm=[]
 for i in pos:
  if not Polygon(t[i,:,:2]).intersects(residual):continue
  for tt in clipped(t[i],residual):
   if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-10:continue
   _,bw,_=closest_on_triangles(tt,np.repeat(t[i][None,:,:],3,axis=0));rt.append(tt);ru.append(bw@P.uv[i]);rm.append('PATCH_PHOTO_'+str(P.material_ids[i]))
 if rt:
  e=dict(e,name='PHOTO_BOUNDARY_RESIDUAL_RECOVERY')
  save(e['name'],e,rt,ru,rm,'ORIGINAL_PHOTO_EDGE_RESIDUAL_RECOVERY')
  covered=covered.union(shapely.union_all(shapely.polygons(np.array(rt)[:,:,:2])))
residual=H.difference(covered);outside=covered.difference(H)
assert outside.area<1e-7
assert residual.area<1e-5,(residual.area,'unfilled projection')
(O/'02_Data/Patch_Index.json').write_text(json.dumps(newindex,ensure_ascii=False,indent=2),encoding='utf-8')
q=json.loads((O/'06_Report/Patch_Clip_And_Photo_QA.json').read_text(encoding='utf-8'))
q['counts'].update(patch_nodes=len(newindex),patch_triangles=sum(r['triangles'] for r in newindex),photo_projected_triangles=sum(r.get('photo_triangles',0) for r in newindex),residual_after_photo_edge_m2=residual.area,patch_outside_primary_void_m2=outside.area)
q['ground_repair']={'source':'Original JIA measured mesh/UV, no source mesh editing','direct_measured_ground_triangles':len(ground_tri),'edge_surface_triangles':len(border_tri),'modeled_interior_fallback_triangles':fallback_count,'edge_strip_width_m':.22,'replacement_terrain_nodes':sorted(terrain_names),'low_ground_max_vertex_z_local_m':1.4,'note':'Ground/edge photos use original triangle UV directly; other model photos use distance/normal projection gates'}
(O/'06_Report/Patch_Clip_And_Photo_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print('REPAIRED',q['counts'],q['ground_repair'],flush=True)
