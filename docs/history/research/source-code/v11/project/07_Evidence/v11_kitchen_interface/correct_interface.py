"""Registered-source local kitchen / eastern retaining-wall junction correction.

Only retaining links60..66 are changed. Every other retaining part remains exact.
The western kitchen/gate underlap and the original roof stay unchanged.
"""
import sys,json,math,copy,hashlib,ast
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,mapbox_earcut,manifold3d as mf
from scipy.spatial import cKDTree
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import set_precision
import export_v5 as ex
O=Path(__file__).parent;SP=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json');source_bytes=SP.read_bytes();S=json.loads(source_bytes);E={e['name']:e for e in S['elements']};B=copy.deepcopy(E)
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));func=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']];exec(compile(ast.Module(func,type_ignores=[]),'<geometry_helpers>','exec'))
collapsed_boolean_slivers=[]
def fromman(a):
 mm=a.simplify(1e-6).to_mesh64();v=np.asarray(mm.vert_properties)[:,:3];fs=np.asarray(mm.tri_verts,dtype=np.int64);parents=np.arange(len(v))
 if len(v)==0 or len(fs)==0:return None
 def find(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for x,y in zip(mm.merge_from_vert,mm.merge_to_vert):parents[find(int(x))]=find(int(y))
 for x,y in cKDTree(v).query_pairs(1e-5):parents[find(int(x))]=find(int(y))
 remap=np.array([find(i) for i in range(len(v))],dtype=np.int64);fs=remap[fs];keep=(fs[:,0]!=fs[:,1])&(fs[:,1]!=fs[:,2])&(fs[:,0]!=fs[:,2]);fs=fs[keep]
 if len(fs)==0:
  collapsed_boolean_slivers.append(dict(raw_volume_m3=a.volume(),raw_vertices=len(v),weld_tolerance_m=1e-5));return None
 used,inv=np.unique(fs,return_inverse=True);vv=v[used];ff=inv.reshape(-1,3)
 vol=abs(float(np.sum(np.einsum('ij,ij->i',vv[ff[:,0]],np.cross(vv[ff[:,1]],vv[ff[:,2]])))/6))
 if vol<1e-12:
  collapsed_boolean_slivers.append(dict(raw_volume_m3=a.volume(),cleaned_volume_m3=vol,raw_vertices=len(v),weld_tolerance_m=1e-5));return None
 return dict(type='polyhedron',vertices=vv.tolist(),faces=ff.tolist())
REFS=['D:/Desktop/DJI_0511.DNG','D:/Desktop/DJI_0513.DNG','D:/Desktop/屏幕截图 2026-10-09 120147.jpg','E:/jz/JIA/Productions/Production_OBJ (2)/Data'];R=[];A=[];checks=[]
def check(name,ok,**kw):
 checks.append(dict(name=name,passed=bool(ok),**kw))
 if not ok:raise AssertionError((name,kw))
def part(g,m):return dict(geometry=g,material=m) if g is not None else None
def put(name,pp,cls,**kw):
 pp=[p for p in pp if p is not None]
 e=copy.deepcopy(E.get(name,dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')));e.update(parts=pp,source='; '.join(REFS),status='V11_REGISTERED_MESH_AND_DNG_CORRECTED_LOCAL_INTERFACE; DIMENSIONS_FIT',classification=cls,**kw);(R if name in B else A).append(e);E[name]=e;return e
def prism(poly,top,bottom):
 poly=orient(set_precision(poly,1e-6).simplify(1e-7,preserve_topology=True),1);rings=[list(poly.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in poly.interiors];q=np.array([v for r in rings for v in r]);k=len(q);ts=mapbox_earcut.triangulate_float64(q,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3)
 v=[[*xy,top(*xy)] for xy in q]+[[*xy,bottom(*xy)] for xy in q];fs=[list(t) for t in ts]+[list(t[::-1]+k) for t in ts];off=0
 for ring in rings:
  n=len(ring);fs.extend([[off+i,off+(i+1)%n,off+(i+1)%n+k,off+i+k] for i in range(n)]);off+=n
 return oriented(dict(type='polyhedron',vertices=v,faces=fs))
def united(pp):return mf.Manifold.batch_boolean([manifold(p['geometry']) for p in pp],mf.OpType.Add)
def parts_for_poly(poly,top,bottom,material,breaks=[]):
 polys=[poly]
 for axis,value in breaks:
  nextp=[]
  for p in polys:
   for mask in ([box(-100,-100,value,100),box(value,-100,100,100)] if axis==0 else [box(-100,-100,100,value),box(-100,value,100,100)]):
    g=p.intersection(mask)
    nextp.extend([q for q in getattr(g,'geoms',[g]) if q.area>1e-10])
  polys=nextp
 return [part(prism(p,top,bottom),material) for p in polys]
# Robust line fitted to the original photographed gray brick face, not to the
# edited hole model. The source comes from scan_section.py, original OBJ2.
d=np.load(O/'Registered_Kitchen_Wall_Section_LOCAL.npz');t=d['vertices'][d['faces']];ct=t.mean(1);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);weight=np.linalg.norm(normal,axis=1)/2;normal/=np.maximum(2*weight[:,None],1e-12)
use=(np.abs(normal[:,0])>.65)&(np.abs(normal[:,2])<.35)&(ct[:,2]>.0)&(ct[:,2]<2.60)&(ct[:,1]>-8.75)&(ct[:,1]<-3.0)&(ct[:,0]<14.4)
q=ct[use];wt=weight[use];design=np.c_[q[:,1],np.ones(len(q))];fit=np.linalg.lstsq(design*np.sqrt(wt[:,None]),q[:,0]*np.sqrt(wt),rcond=None)[0]
for _ in range(6):
 resid=q[:,0]-design@fit;keep=abs(resid)<.075;fit=np.linalg.lstsq(design[keep]*np.sqrt(wt[keep,None]),q[keep,0]*np.sqrt(wt[keep]),rcond=None)[0]
slope,intercept=map(float,fit)
check('registered_gray_wall_face_fit_supported',len(q)>100 and sum(keep)>100 and .06<slope<.16,triangles=len(q),retained=int(keep.sum()),slope=slope,intercept=intercept,p95_abs_residual_m=float(np.percentile(abs(resid[keep]),95)))
def face_x(y):return intercept+slope*y
def east_top(x,y):return 3.365916710451-.440835*(x-13.35)+.003125757*(y+11.65)
oldnorth=np.array(B['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts'][1]['geometry']['vertices']);nn=oldnorth[(abs(oldnorth[:,1]+2.6)<1e-8)&(oldnorth[:,2]>0)];nx=nn[:,0];nz=nn[:,2]
def roof_bottom(x,y):
 if x>11.515:return east_top(x,y)
 return float(np.interp(x,nx,nz))+.003125757*(y+2.6)
# The north return begins at the existing wood-front point. Its new perpendicular
# face meets the registered east back wall at exactly90degrees.
corner_x=(intercept-2.6*slope+slope*slope*7.7)/(1+slope*slope)
corner_y=-2.6-slope*(corner_x-7.7)
corner=np.array([corner_x,corner_y]);back_u=np.array([slope,1.]);back_u/=np.linalg.norm(back_u);north_u=np.array([1.,-slope]);north_u/=np.linalg.norm(north_u)
check('L_return_is_exact_right_angle',abs(float(back_u@north_u))<1e-12,corner_local_m=corner.tolist())
# Preserve backwall south junction; a200mm face transition starts outside the
# source-supported seven links. No one-metre solid fill is fabricated.
back_outer=[[13.35,-11.65],[13.35,-8.475],[face_x(-8.275),-8.275],corner.tolist()]
inside_n=np.array([-1.,slope]);inside_n/=np.linalg.norm(inside_n)
north_inside=np.array([-slope,-1.]);north_inside/=np.linalg.norm(north_inside)
miter=(inside_n+north_inside);miter=miter/np.dot(miter,inside_n)*.22
innercorner=corner+miter
back_plan=Polygon(back_outer+[innercorner.tolist(),(np.array(back_outer[2])+inside_n*.22).tolist(),[13.13,-8.475],[13.13,-11.65]])
north_plan=Polygon([[7.7,-2.6],corner.tolist(),innercorner.tolist(),[7.7,-2.82]])
L=unary_union([back_plan,north_plan]);check('north_back_L_footprint_continuous',L.geom_type=='Polygon' and L.is_valid)
Lparts=parts_for_poly(L,lambda x,y:roof_bottom(x,y),lambda x,y:-.4,'M_Grey_Brick',[(0,11.515),(1,-8.475),(1,-8.275)])
lk=put('SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES',[copy.deepcopy(B['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts'][0])]+Lparts,'REGISTERED_BARE_GRAY_BRICK_L_BACK_AND_NORTH_GABLE',north_east_corner_angle_degrees=90.,north_east_corner_local_m=corner.tolist(),registered_back_face_x_by_y=[slope,intercept],south_gable_exactly_preserved=True,old_inferred_parallel_gap_removed=True,exterior_foundation_strength_not_specified=True)
# East roof strip follows the unchanged eastern roof plane. It extends only the
# local eave and does not alter the west gate/kitchen roof overlap.
oldroof=united(B['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts'])
extension_plan=Polygon([[13.20,-8.60],[face_x(-8.60)+.35,-8.60],[face_x(-2.42)+.35,-2.42],[13.20,-2.42]])
extension=prism(extension_plan,lambda x,y:east_top(x,y)+.085,lambda x,y:east_top(x,y)-.018)
extension_only=manifold(extension)-oldroof
check('east_eave_addition_is_closed_and_does_not_duplicate_old_roof',not extension_only.is_empty() and (extension_only^oldroof).volume()<1e-10)
put('SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP',[part(fromman(extension_only),'M_Roof')],'LOCAL_EXTENSION_OF_UNCHANGED_KITCHEN_EAST_ROOF_PLANE',registered_wall_face_fit=True,original_roof_and_west_gate_underlap_preserved=True,eave_projection_reference_m=.35,roof_rise_shape_preserved=True)
# Seven original links60..66 are locally reconciled with the new kitchen back
# wall. The retained stone base ends match link59/67 exactly; short endpoint
# transitions express a real local junction rather than a full-height thick fill.
wallname='SITE_PERIMETER_JOINED_RETAINING_WALL_0';oldparts=B[wallname]['parts'];affected=list(range(60,67));pnts=[];basez=[];oldcenter=[]
for j in range(60,68):
 p=oldparts[2*j]['geometry']['vertices'] if j<67 else oldparts[2*66]['geometry']['vertices'];ids=(0,3) if j<67 else (1,2);a=np.mean(np.array(p)[list(ids)],axis=0);oldcenter.append(a[:2].tolist());basez.append(float(a[2]))
 # Stone outward face is80mm beyond gray brick; its320mm body supports the220mm brick wall.
 pnts.append(a[:2].tolist() if j in [60,67] else [face_x(float(a[1]))-.08,float(a[1])])
pnts=np.array(pnts);uv=np.diff(pnts,axis=0);uv/=np.linalg.norm(uv,axis=1)[:,None];norm=np.c_[-uv[:,1],uv[:,0]];offs=[]
for j in range(len(pnts)):
 if j==0:
  vv=np.array(oldparts[120]['geometry']['vertices']);off=(vv[3,:2]-vv[0,:2])/2
 elif j==len(pnts)-1:
  vv=np.array(oldparts[132]['geometry']['vertices']);off=(vv[2,:2]-vv[1,:2])/2
 else:
  off=(norm[j-1]+norm[j])/2;off=off/np.dot(off,norm[j])*.16
 offs.append(off)
newpieces={};lowplans=[];occupied_stone_plan=Polygon()
for ii,j in enumerate(affected):
 a=pnts[ii];b=pnts[ii+1];offa=offs[ii];offb=offs[ii+1];plan=Polygon([a-offa,b-offb,b+offb,a+offa]);L0=float(np.linalg.norm(b-a));unit=(b-a)/L0
 def bottom(x,y,ii=ii,a=a,unit=unit,L0=L0):
  s=float((np.array([x,y])-a)@unit)/L0;return basez[ii]+(basez[ii+1]-basez[ii])*s
 support=back_plan.intersection(box(-100,min(a[1],b[1]),100,max(a[1],b[1])))
 stoneplan=unary_union([plan,support]) if support.area>1e-10 else plan
 disjoint_stone=stoneplan.difference(occupied_stone_plan);occupied_stone_plan=unary_union([occupied_stone_plan,stoneplan])
 stones=[part(prism(pp,lambda x,y:-.4,bottom),'M_Stone_Rubble') for pp in getattr(disjoint_stone,'geoms',[disjoint_stone]) if pp.area>1e-10]
 # On the high kitchen back-wall span the existing extra wall body is removed.
 # Only the low return north of the corrected corner remains, now gray brick.
 lowplan=plan.intersection(box(-100,corner_y,100,100));lowplans.append(lowplan)
 upper=[]
 if lowplan.area>1e-10:
  oldv=np.array(oldparts[2*j+1]['geometry']['vertices']);top0=float(max(oldv[:4,2]));top1=float(max(oldv[4:,2]))
  # Top1 is the original low wall crest; no crown height increase.
  low=manifold(prism(lowplan,lambda x,y,z=top1:z,lambda x,y:-.4))-united(Lparts)
  if not low.is_empty() and low.volume()>1e-12:upper=[v for v in [part(fromman(low),'M_Grey_Brick')] if v is not None]
 newpieces[j]=stones+upper
rebuilt=[];mapping=[]
for j in range(len(oldparts)//2):
 if j in newpieces:rebuilt.extend(newpieces[j]);mapping.append(dict(link_index=j,new_part_count=len(newpieces[j]),old_parts=[2*j,2*j+1]))
 else:rebuilt.extend(copy.deepcopy(oldparts[2*j:2*j+2]))
put(wallname,rebuilt,'LOCAL_KITCHEN_REGISTERED_STONE_BASE_AND_GRAY_BRICK_RETURN',changed_link_indices=affected,all_other_original_link_parts_exact=True,local_low_wall_ends_at_kitchen_corner_y=corner_y,old_white_body_omitted_under_kitchen_high_wall=True,source_face_line=[slope,intercept],stone_visible_base_top_z_reference_m=-.4)
# Crop former floating white ornaments and floral crowns from the high-kitchen
# segment, and reposition the ordinary lower coping on the corrected low return.
scope_plans=[]
for j in affected:
 vv=np.array(oldparts[2*j]['geometry']['vertices'])[:4,:2];aa=(vv[0]+vv[3])/2;bb=(vv[1]+vv[2])/2;oa=(vv[3]-vv[0])/2/.16*.30;ob=(vv[2]-vv[1])/2/.16*.30
 scope_plans.append(Polygon([aa-oa,bb-ob,bb+ob,aa+oa]))
scope=unary_union(scope_plans);high_scope=scope.intersection(box(-100,-100,100,corner_y));mask_solid=manifold(prism(high_scope,lambda x,y:10,lambda x,y:-10));fullmask=manifold(prism(scope,lambda x,y:10,lambda x,y:-10))
def shifted(q):
 y=q[1];oldxs=np.interp(-y,-np.array(oldcenter)[:,1],np.array(oldcenter)[:,0]);newxs=np.interp(-y,-pnts[:,1],pnts[:,0]);return [q[0]+newxs-oldxs,q[1],q[2]]
for name in [wallname+'_TILE_COPING',wallname+'_PROVISIONAL_FLOWER_CROWN',wallname+'_PLASTER_STEPPED_RELIEF']:
 pp=[];kept_exact=0;cropped=0
 for p in B[name]['parts']:
  g=p['geometry'];v=np.array(g['vertices']);bbox=box(v[:,0].min(),v[:,1].min(),v[:,0].max(),v[:,1].max())
  if not bbox.intersects(scope):pp.append(copy.deepcopy(p));kept_exact+=1;continue
  a=manifold(g)
  if (a^fullmask).volume()<=1e-11:pp.append(copy.deepcopy(p));kept_exact+=1;continue
  # No floral or plaster decoration is applied to this DNG bare-brick segment.
  if name.endswith('_TILE_COPING'):
   outside=a-fullmask;inside=(a^fullmask)-mask_solid
   if not outside.is_empty() and outside.volume()>1e-12:pp.append(part(fromman(outside),p['material']))
   if not inside.is_empty() and inside.volume()>1e-12:
    gg=fromman(inside)
    if gg is not None:
     gg['vertices']=[shifted(q) for q in gg['vertices']];pp.append(part(oriented(gg),p['material']))
  else:
   outside=a-fullmask
   if not outside.is_empty() and outside.volume()>1e-12:pp.append(part(fromman(outside),p['material']))
  cropped+=1
 put(name,pp,'LOCAL_COPING_JUNCTION_CLEANUP_AT_KITCHEN_GRAY_BRICK_WALL',non_kitchen_parts_exactly_preserved=kept_exact,local_changed_original_parts=cropped,bare_gray_DNG_segment_flower_and_white_relief_omitted=True)
# Add exposed gray-brick skins along the new back line and perpendicular return.
# Closed individual visible units; texture transfer is deliberately not sampled
# from nearby vegetation. The original source photograph meshes are preserved.
bricks=[];mortars=[]
faces=[('back',np.array(back_outer[2]),corner,inside_n),('north',np.array([7.7,-2.6]),corner,north_inside)]
for label,a,b,nin in faces:
 L0=float(np.linalg.norm(b-a));u=(b-a)/L0;out=-nin
 faceplan=Polygon([a,b,b+out*.003,a+out*.003]);mortars.extend(parts_for_poly(faceplan,lambda x,y:roof_bottom(x,y)-.014,lambda x,y:-.4,'M_V11_Kitchen_Brick_Joints',[(0,11.515)]))
 for row in range(73):
  z0=-.4+row*.065+.004;off=.12 if row%2 else 0
  for ss in np.arange(-off,L0,.24):
   s0=max(0.,float(ss+.004));s1=min(L0,float(ss+.236))
   if s1-s0<.025:continue
   aa=a+u*s0;bb=a+u*s1;poly=Polygon([aa+out*.003,bb+out*.003,bb+out*.015,aa+out*.015]);zt=min(roof_bottom(*aa),roof_bottom(*bb))-.020
   if zt<=z0+.008:continue
   bricks.append(part(prism(poly,lambda x,y,z=min(z0+.055,zt):z,lambda x,y,z=z0:z),'M_Grey_Brick'))
put('SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS',bricks,'REGISTERED_L_FACES_INDIVIDUAL_BARE_GRAY_BRICKS',reference_brick_unit_m=[.232,.012,.055],unit_dimensions_unmeasured=True)
put('SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING',mortars,'GRAY_MORTAR_SKIN_FOR_L_BACK_AND_NORTH_WALL',finish_dimensions_reference=True)
changes=[dict(id='V11_REGISTERED_KITCHEN_LOCAL_L_JOIN',description='以原完整OBJ2实景灰砖外壁拟合厨房东背墙，北山墙与其为90度。外周墙0仅60～66链段石挡基和低灰砖回接保留，厨房高墙段重复白墙/花脊/装饰剔除；原59/67端面及其它110链段完全保留。新增东檐窄条顺原坡盖校正外壁，西门楼厨房高低檐不改。',source=REFS,full_height_1m_fill_omitted=True,original_wall0_non_kitchen_links_exact=True,fit_residual_not_field_survey=True,buried_foundation_not_specified=True)]
mutation=dict(replace=R,add=A,remove=[],definitions={},materials={'M_V11_Kitchen_Brick_Joints':dict(color=[157,160,155],roughness=.96)},changes=changes,source_scene_sha256=hashlib.sha256(source_bytes).hexdigest(),old_node_sha256={e['name']:hashlib.sha256(json.dumps(B[e['name']],sort_keys=True,separators=(',',':')).encode()).hexdigest() for e in R},registered_fit=dict(slope_x_per_y=slope,intercept=intercept,corner_local_m=corner.tolist(),point_count=len(q),kept=int(keep.sum()),p95_abs_residual_m=float(np.percentile(abs(resid[keep]),95))),changed_retaining_links=affected,nonchanged_wall0_parts_exact=True,old_wall0_replacement_map=mapping,kitchen_south_gable_original_part_exact=True,original_kitchen_roof_part_exact=True)
for e in R+A:
 for i,p in enumerate(e['parts']):
  try:aa=manifold(p['geometry'])
  except Exception as exc:
   (O/'Invalid_Geometry_Debug.json').write_text(json.dumps(dict(name=e['name'],part=i,geometry=p['geometry']),indent=2),encoding='utf8')
   print('INVALID',e['name'],i,str(exc),flush=True);raise
  check(e['name']+f'_{i}_closed',aa.status()==mf.Error.NoError and aa.volume()>1e-12)
check('117_minus7_retaining_links_exact',all(newpieces.get(j) is not None or B[wallname]['parts'][2*j:2*j+2]==E[wallname]['parts'][sum(len(newpieces[k]) if k in newpieces else 2 for k in range(j)):sum(len(newpieces[k]) if k in newpieces else 2 for k in range(j))+2] for j in range(len(oldparts)//2)))
check('source_scene_not_modified',SP.read_bytes()==source_bytes)
(O/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()),encoding='utf8')
qa=dict(status='PASS',checks=checks,checks_count=len(checks),parts=sum(len(e['parts']) for e in R+A),replace=len(R),add=len(A),fit=mutation['registered_fit'],changed_links=affected,brick_units=len(bricks),not_field_survey=True,boolean_weld_tolerance_m=1e-5,collapsed_boolean_slivers=collapsed_boolean_slivers)
(O/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()),encoding='utf8')
print(json.dumps({k:v for k,v in qa.items() if k!='checks'},ensure_ascii=False))
