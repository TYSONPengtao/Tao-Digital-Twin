"""Slope-fitted open gate bottom rails; isolated replacement patch only."""
import json,sys,ast,math,copy
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'helpers','exec'))
proof={};tree=ast.parse((W/'v19_design.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fromman'],type_ignores=[]),'fromman','exec'))
O=Path('E:/jz/JIA/Rebuild_V20');I=json.loads((O/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
DQ=json.loads((W/'v20/Door_Mutation.json').read_text(encoding='utf8'));DE={e['name']:e for e in DQ['replace']+DQ['add']};DM=json.loads((W/'v20/Door_Manifest.json').read_text(encoding='utf8'))
ground_names=[n for n in ii if n.startswith('SITE_V12_REBUILT_ROAD') or n in ['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP','SITE_V16_GRADED_INTERIOR_SOIL']]
ground=[]
for n in ground_names:
 d=np.load(O/'02_Data'/ii[n]['file']);v=d['vertices'];t=v[d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ground.append((n,t[no[:,2]>1e-9]))
axis=np.array([.877,.479]);axis/=np.linalg.norm(axis);normal=np.array([-axis[1],axis[0]])
patch={'replace':[],'add':[],'remove':[],'materials':{},'scope':'Only inward-open outer metal gate lower geometry; hinge positions and animations stay fixed; no site ground changes'};qa={'status':'PASS_SLOPE_GATE_BOTTOM_QA','pairs':[],'nodes':[]}
for rootnum,nums in [(1,[1,2]),(4,[4,3])]:
 rootn=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{rootnum}';pivot=np.array(DE[rootn]['pivot_world_m']);vs=np.vstack([p['geometry']['vertices'] for j in nums for p in DE[f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{j}']['parts']]);xy=vs[:,:2]-pivot[:2];st=xy@axis;rt=xy@normal
 # Fit a plane above every actual grade triangle under the full open pair.
 smin,smax=float(st.min()-.002),float(st.max()+.002);rmin,rmax=float(rt.min()-.002),float(rt.max()+.002);band=box(smin,rmin,smax,rmax)
 pts=[];contributors=set()
 for n,tt in ground:
  for tri in tt:
   sr=np.c_[(tri[:,:2]-pivot[:2])@axis,(tri[:,:2]-pivot[:2])@normal]
   if sr[:,0].max()<smin or sr[:,0].min()>smax or sr[:,1].max()<rmin or sr[:,1].min()>rmax:continue
   poly=Polygon(sr).intersection(band)
   if poly.is_empty or poly.area<1e-12:continue
   mat=np.c_[sr,np.ones(3)];zz=np.linalg.solve(mat,tri[:,2]);contributors.add(n)
   polys=[poly] if poly.geom_type=='Polygon' else [p for p in poly.geoms if p.geom_type=='Polygon']
   for p in polys:
    for s,r in list(p.exterior.coords)[:-1]:pts.append([s,r,zz[0]*s+zz[1]*r+zz[2]])
 assert len(pts)>10,(rootnum,len(pts));points=np.array(pts);A=np.c_[points[:,:2],np.ones(len(points))];fit=np.linalg.lstsq(A,points[:,2],rcond=None)[0];err=points[:,2]-A@fit;fit[2]+=float(err.max())+.020
 # Cover all geometry below this plane; its vertical extrusion is a safe
 # finite halfspace, well below the current ground and door bottom.
 def z(s,r):return float(fit[0]*s+fit[1]*r+fit[2])
 def xyat(s,r):return pivot[:2]+axis*s+normal*r
 corners=[(smin-.25,rmin-.25),(smax+.25,rmin-.25),(smax+.25,rmax+.25),(smin-.25,rmax+.25)]
 cutg={'type':'prism','profile':[[*xyat(s,r),z(s,r)] for s,r in corners],'vector':[0,0,-8]};cut=manifold(cutg)
 minclear=float((A@fit-points[:,2]).min());assert minclear>=.019999
 gt=np.concatenate([t for n,t in ground]);gsr=np.stack([ (gt[:,:,:2]-pivot[:2])@axis,(gt[:,:,:2]-pivot[:2])@normal],axis=-1)
 gg=(gsr[:,:,0].max(1)>=smin)&(gsr[:,:,0].min(1)<=smax)&(gsr[:,:,1].max(1)>=rmin)&(gsr[:,:,1].min(1)<=rmax);gt=gt[gg];gsr=gsr[gg]
 aa=gsr[:,0];uu=gsr[:,1]-aa;vv=gsr[:,2]-aa;dd=uu[:,0]*vv[:,1]-uu[:,1]*vv[:,0];visible_clear=[]
 for s,r,zz in points:
  ww=np.array([s,r])-aa;bb=(ww[:,0]*vv[:,1]-ww[:,1]*vv[:,0])/dd;cc=(uu[:,0]*ww[:,1]-uu[:,1]*ww[:,0])/dd;inside=(bb>=-1e-6)&(cc>=-1e-6)&(bb+cc<=1+1e-6)
  if inside.any():visible_clear.append(z(s,r)-float(np.max(gt[inside,0,2]+bb[inside]*(gt[inside,1,2]-gt[inside,0,2])+cc[inside]*(gt[inside,2,2]-gt[inside,0,2]))))
 qa['pairs'].append({'root':rootn,'preserved_root_hinge':pivot.tolist(),'plane_in_pair_coordinates':fit.tolist(),'pair_axis_local_xy':axis.tolist(),'plane_origin_xy':pivot[:2].tolist(),'grade_sources':sorted(contributors),'grade_facet_vertex_samples':len(pts),'minimum_floor_clearance_m':minclear,'maximum_floor_clearance_m':float((A@fit-points[:,2]).max()),'visible_upper_ground_clearance_range_m':[min(visible_clear),max(visible_clear)]})
 for j in nums:
  n=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{j}';e=copy.deepcopy(DE[n]);parts=[];modified=[];before=[]
  for k,p in enumerate(e['parts']):
   m=manifold(p['geometry']);before.append(m)
   # The original main bottom rail is replaced wholly, rather than leaving a
   # floating fragment when a higher grade cuts through it.
   if k==2:modified.append({'part':k,'operation':'old bottom rail removed and rebuilt'});continue
   mm=m-cut
   if m.volume()-mm.volume()>1e-10:
    modified.append({'part':k,'removed_volume_m3':m.volume()-mm.volume()})
    if not mm.is_empty():parts.append({'geometry':fromman(mm),'material':p['material']})
   else:parts.append(p)
  railvs=np.array(e['parts'][2]['geometry']['vertices']);rcenter=float(np.mean((railvs[:,:2]-pivot[:2])@normal));rs=(railvs[:,:2]-pivot[:2])@axis;a0,a1=float(rs.min()),float(rs.max());width=.055
  rp=[(a0,rcenter-width/2),(a1,rcenter-width/2),(a1,rcenter+width/2),(a0,rcenter+width/2)]
  rg={'type':'prism','profile':[[*xyat(s,r),z(s,r)] for s,r in rp],'vector':[0,0,.055]}
  parts.append({'geometry':oriented(rg),'material':e['parts'][2]['material']});e['parts']=parts
  e['v20_slope_clear_bottom']={'hinge_height_unchanged':True,'open_pose_grade_fitted_lower_cut':True,'new_lower_rail_height_m':.055,'minimum_reference_ground_clearance_m':.020,'pair_plane_sr':fit.tolist(),'pair_plane_origin_xy':pivot[:2].tolist(),'pair_axis_xy':axis.tolist(),'pair_normal_xy':normal.tolist(),'reference':'Actual retained V20 modeled road/ramp/soil upper envelope; clearance is walkthrough geometry fit, not a field-measured gate alteration'}
  e['current_pose']='OPEN_INWARD';e['relative_open_angle_degrees']=0 if j!=rootnum else e['open_angle_degrees']
  patch['replace'].append(e)
  dm=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in parts],mf.OpType.Add);assert dm.status()==mf.Error.NoError
  collision=[]
  for gn in contributors:
   dd=np.load(O/'02_Data'/ii[gn]['file']);vv=dd['vertices'];ff=dd['faces'];uvv,ix=np.unique(np.round(vv,9),axis=0,return_inverse=True);gm=mf.Manifold(mf.Mesh(vert_properties=uvv.astype(np.float32),tri_verts=ix[ff].astype(np.uint32)));assert gm.status()==mf.Error.NoError,(gn,gm.status());vvv=(dm^gm).volume()
   assert vvv<1e-7,(n,gn,vvv);collision.append({'ground':gn,'volume_m3':vvv})
  qa['nodes'].append({'name':n,'hinge_local_unchanged':e['pivot_world_m'],'parent_door_id':e.get('parent_door_id'),'changed_lower_parts':modified,'rebuilt_bottom_rail':True,'positive_closed_parts':len(parts),'volume_before_m3':mf.Manifold.batch_boolean(before,mf.OpType.Add).volume(),'volume_after_m3':dm.volume(),'ground_collision_checks':collision})
(D/'Outer_Gate_Bottom_Mutation.json').write_text(json.dumps(patch,ensure_ascii=False,indent=2),encoding='utf8');(D/'Outer_Gate_Bottom_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)
