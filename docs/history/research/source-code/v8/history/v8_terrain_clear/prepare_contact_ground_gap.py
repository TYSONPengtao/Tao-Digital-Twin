"""Prepare minimal ground-only repair candidates for final V8 projection gaps. Does not edit V8."""
import sys,json,ast,math
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,shapely,mapbox_earcut
from shapely.geometry import Polygon,LineString,shape
from shapely.ops import unary_union
from scipy.spatial import cKDTree
from nearest_photo_projection import closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');D=W/'v8_terrain_clear/contact_gap';D.mkdir(exist_ok=True);source=Path(sys.argv[1]) if len(sys.argv)>1 else W/'v8_coverage_residual.json';meta=json.loads(source.read_text(encoding='utf-8'))
def decode(q):
 if isinstance(q,list):return unary_union([decode(x) for x in q])
 if 'outer' in q:return Polygon(q['outer'],q.get('holes',[]))
 if q.get('type') in ['Polygon','MultiPolygon','GeometryCollection']:return shape(q)
 for k in ['polygons','residual_polygons','residual','geometry','geojson','residual_geojson','residual_geometry']: 
  if k in q and isinstance(q[k],(dict,list)):return decode(q[k])
 raise ValueError('Unknown residual geometry keys '+str(q.keys()))
G=decode(meta).buffer(0);assert G.area<1.,('unexpected nonlocal repair area',G.area);assert G.area>1e-9;tree=ast.parse((W/'build_v6_patch.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','polygon_tris','clip_half','clipped']],type_ignores=[]),'<clip helpers>','exec'))
oldI=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));r=next(x for x in oldI if x['name']=='PHOTO_BOUNDARY_GROUND_RECOVERY');pre=np.load(O/'02_Data/V8_Clearance_PHOTO_BOUNDARY_GROUND_RECOVERY.npz');gt=pre['vertices'][pre['faces']];gu=pre['uv'][pre['faces']];mid=pre['material_ids'];gc=gt.mean(1);n=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-20);lo=np.array(G.bounds[:2])-.5;hi=np.array(G.bounds[2:])+.5;near=(gt[:,:,:2].max(1)>=lo).all(1)&(gt[:,:,:2].min(1)<=hi).all(1);earth=near&(abs(n[:,2])>.7)&(gt[:,:,2].max(1)<.08)&(gt[:,:,2].max(1)-gt[:,:,2].min(1)<.20);support=gt[earth].reshape(-1,3);assert len(support)>5;support=np.unique(support,axis=0);photo_support=support.copy();tree=cKDTree(photo_support[:,:2])
coord=json.loads((O/'02_Data/Coordinate.json').read_text());rot=np.array(coord['local_to_survey'])[:3,:3];org=np.array(coord['origin']);bd=np.load(O/'02_Data/Base_3.npz');bv=(bd['vertices']-org)@rot;bt=bv[bd['faces'][:,:3]];bn=np.cross(bt[:,1]-bt[:,0],bt[:,2]-bt[:,0]);bn/=np.maximum(np.linalg.norm(bn,axis=1)[:,None],1e-20);bb=G.bounds;base_near=(bt[:,:,:2].max(1)>=np.array(bb[:2])-1.2).all(1)&(bt[:,:,:2].min(1)<=np.array(bb[2:])+1.2).all(1);base_ground=base_near&(abs(bn[:,2])>.7)&(bt[:,:,2].max(1)<.5)&(np.ptp(bt[:,:,2],axis=1)<.22);base_tri=bt[base_ground];base_xy=base_tri.copy();base_xy[:,:,2]=0;base_tree=cKDTree(base_tri[:,:,:2].mean(1));support=np.unique(np.vstack([photo_support,base_tri.reshape(-1,3)]),axis=0)
def measured_base_ground(xy):
 xy=np.asarray(xy);k=min(32,len(base_tri));_,ii=base_tree.query(xy,k=k);ii=np.asarray(ii).reshape(len(xy),k);qq=np.repeat(np.c_[xy,np.zeros(len(xy))],k,axis=0);_,bary,dist=closest_on_triangles(qq,base_xy[ii].reshape(-1,3,3));dist=dist.reshape(-1,k);bary=bary.reshape(-1,k,3);pick=np.argmin(dist,axis=1);ids=np.arange(len(xy));z=(bary[ids,pick]*base_tri[ii[ids,pick],:,2]).sum(1);return z,dist[ids,pick]
def height(xy):
 xy=np.asarray(xy);ds,ix=tree.query(xy,k=min(10,len(photo_support)));w=1/np.maximum(ds,.03)**2;z=(w*photo_support[ix,2]).sum(1)/w.sum(1);east=xy[:,0]>10
 if east.any():
  zz,dd=measured_base_ground(xy[east]);assert dd.max()<1.2,('measured base ground too distant',dd.max());z[east]=zz
 return z
tri=[];uv=[];mat=[];fromids=[]
for j in np.flatnonzero(earth):
 for tt in clipped(gt[j],G):
  if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-9:continue
  _,bw,_=closest_on_triangles(tt,np.repeat(gt[j][None,:,:],3,axis=0));tri.append(tt);uv.append(bw@gu[j]);mat.append(r['materials'][int(mid[j])]);fromids.append(int(j))
adaptive_stats={'refined_triangles':0,'depth_limit_cells':0,'edge_size_limit_cells':0}
def refined_ground_triangles(xy,depth=0):
 xy=np.asarray(xy);z=height(xy);tt=np.c_[xy,z];mids=(xy+np.roll(xy,-1,axis=0))/2;zm=height(mids);err=abs(zm-(z+np.roll(z,-1))/2);center=xy.mean(0);ce=abs(float(height(center[None,:])[0])-z.mean());length=np.linalg.norm(np.roll(xy,-1,axis=0)-xy,axis=1)
 if max(err.max(),ce)<.01 or depth>=16 or length.max()<.0015:
  if depth>=16 and max(err.max(),ce)>=.01:adaptive_stats['depth_limit_cells']+=1
  if length.max()<.0015 and max(err.max(),ce)>=.01:adaptive_stats['edge_size_limit_cells']+=1
  n=np.cross(tt[1]-tt[0],tt[2]-tt[0])
  if np.linalg.norm(n)<1e-9:return []
  if n[2]<0:tt=tt[[0,2,1]]
  return [tt]
 adaptive_stats['refined_triangles']+=1;i=int(err.argmax()) if err.max()>=ce else int(length.argmax());j=(i+1)%3;k=(i+2)%3;mid=mids[i]
 return refined_ground_triangles(np.array([xy[i],mid,xy[k]]),depth+1)+refined_ground_triangles(np.array([mid,xy[j],xy[k]]),depth+1)
measured_cov=shapely.union_all(shapely.polygons(np.array(tri)[:,:,:2])) if tri else Polygon();missing=G.difference(measured_cov);fill=[];filluv=[];step=.075;b=missing.bounds
if missing.area>1e-10:
 for x in np.arange(math.floor(b[0]/step)*step,b[2]+step,step):
  for y in np.arange(math.floor(b[1]/step)*step,b[3]+step,step):
   cell=Polygon([(x,y),(x+step,y),(x+step,y+step),(x,y+step)]).intersection(missing)
   for pp in polys(cell):
    if pp.area<1e-10:continue
    for xy in polygon_tris(pp):
     for tt in refined_ground_triangles(xy):
      fill.append(tt);filluv.append(tt[:,:2])
rows=[]
def save(name,tri,uv,mat,role,confidence):
 if not tri:return
 v=np.array(tri).reshape(-1,3);f=np.arange(len(v),dtype=np.int32).reshape(-1,3);ms=list(dict.fromkeys(mat));mi=np.array([ms.index(m) for m in mat],np.int32);fn=name+'.npz';np.savez_compressed(D/fn,vertices=v,faces=f,uv=np.array(uv).reshape(-1,2),material_ids=mi)
 rows.append({'index':0,'file':fn,'name':name,'element':{'name':name,'layer':'60_SITE','family':'SITE_MODEL','source':'Measured low ground clipped to actual final V8 projection residual' if confidence=='HIGH' else 'Local neighboring measured ground support interpolated only over actual final projection residual','confidence':confidence,'role':role},'materials':ms,'triangles':len(f),'vertices':len(v),'role':role,'photo_triangles':len(f) if confidence=='HIGH' else 0})
save('V8_CONTACT_GAP_MEASURED_GROUND',tri,uv,mat,'FINAL_LOCAL_CONTACT_GROUND_ONLY_ORIGINAL_SOURCE_UV','HIGH');save('V8_CONTACT_GAP_INTERPOLATED_GROUND',fill,filluv,['M_V8_West_Earth']*len(fill),'FINAL_LOCAL_CONTACT_GROUND_ONLY_SCAN_OCCLUDED_INTERPOLATION','MEDIUM');np.savez_compressed(D/'Ground_Support_And_Donor_Indices.npz',support=support,donor_triangle_indices=np.array(fromids,int),base3_support_triangles=base_tri)
combined=np.concatenate([np.array(a).reshape(-1,3,3) for a in [tri,fill] if len(a)]);cov=shapely.union_all(shapely.polygons(combined[:,:,:2]));res=G.difference(cov).area;over=cov.difference(G).area;assert res<1e-6;assert over<1e-9;assert combined[:,:,2].max()<.08
qa={'status':'PASS_CANDIDATE_ONLY','input_residual_file':str(source),'input_residual_area_m2':G.area,'measured_ground_area_m2':measured_cov.area,'interpolated_ground_area_m2':missing.area,'measured_triangles':len(tri),'interpolated_triangles':len(fill),'ground_support_points':len(support),'measured_base3_ground_support_triangles':len(base_tri),'adaptive_refinement':adaptive_stats,'nominal_ground_grid_m':step,'interpolation_method':'East gaps follow nearest exact measured Base3 ground surface (height from nearest XY projection, no photo assigned beyond source support); tiny courtyard ground gaps use neighboring original measured ground','ground_support_extent_local':[support.min(0).tolist(),support.max(0).tolist()],'output_ground_elevation_range_local_m':[float(combined[:,:,2].min()),float(combined[:,:,2].max())],'output_residual_m2':res,'output_outside_gap_m2':over,'source_uv_only_measured_faces':True,'source_file_and_existing_base_modified':False,'limits':'Only exact source measured ground faces preserve their original photo UV. Occluded interpolation uses provisional soil material. Native/export validation remains parent task.'}
(D/'Candidate_Patch_Index_Rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');(D/'Contact_Gap_Ground_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(qa,ensure_ascii=False,indent=2))
