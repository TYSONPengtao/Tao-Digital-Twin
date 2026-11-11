"""Correct source wall intersections, level the F3 rail, and detail gate piers."""
from v26_2_common import *
import v26_2_common as C
from v26_8_native_cleanup import repair_native
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from PIL import Image
from v24_relief_blender import _panel_mesh_arrays,_atlas_layout
D=W/'v26_10';D.mkdir(exist_ok=True);C.D=D;FD=W/'v26_9/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};rows=[];proof={};rigid=[]
def native(n):
 r=J[n];a=np.load(FD/r['file']);return tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
def put(n,m,why,**kw):
 # The fused house contains existing narrow window returns. Do not globally
 # simplify those remote edges when correcting a local WC intersection.
 if n!='V26_3_House_Connected_Walls_And_Stairs':m=m.simplify(.000015)
 r,m=export(n,m,why,**kw);a=np.load(D/r['file'])
 if n=='V26_3_House_Connected_Walls_And_Stairs':
  v,f,mi,uv,qa=repair_native(a['v'],a['f'],a['mi'],a['uv']);np.savez_compressed(D/r['file'],v=v,f=f,mi=mi,uv=uv);r['native_cleanup']=qa;r['triangles']=len(f)
 rows.append(r);return m
def extrude_poly(p,z0,z1):
 contours=[]
 for q in (p.geoms if hasattr(p,'geoms')else[p]):
  if q.is_empty or q.area<1e-12:continue
  q=orient(q,1);contours.append(np.array(q.exterior.coords)[:-1]);contours.extend(np.array(r.coords)[:-1]for r in q.interiors)
 return mf.CrossSection(contours,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
HN='V26_3_House_Connected_Walls_And_Stairs';house=native(HN);original=house;changes=[];scope=[]
floors=[-.44999998807907104,3.450024366378784,7.050000190734863];ceil=[3.32,6.92,10.220000267]
def interval(axis,start,end,center):
 hh=original.ray_cast(start,end)
 for a,b in zip(hh,hh[1:]):
  if a.normal[axis]<-.8 and b.normal[axis]>.8 and a.position[axis]<center<b.position[axis]:return[float(np.float32(round(a.position[axis],4))),float(np.float32(round(b.position[axis],4)))]
 return None
nodes=[(fl,x)for fl in range(3)for x in [3.9,9.1]]+[(0,2.2),(1,2.2),(1,10.8),(2,10.8),(0,13.)]
for fl,cx in nodes:
 z=floors[fl]+1.25;cy=7.3;roi=box(cx-.36,7.03,cx+.36,7.57)
 vs=interval(0,[cx-.6,7.06,z],[cx+.6,7.06,z],cx);vn=interval(0,[cx-.6,7.58,z],[cx+.6,7.58,z],cx)
 hl=interval(1,[cx-.6,6.85,z],[cx-.6,7.75,z],cy);hr=interval(1,[cx+.6,6.85,z],[cx+.6,7.75,z],cy)
 # A WC return starts at its front wall; there is no south wall branch.
 if abs(cx-2.2)<.01 or abs(cx-10.8)<.01:vs=None
 # F1 west WC wall: match the hall-facing plane to its bedroom continuation
 # while retaining the existing WC interior face and the door aperture.
 if fl==0 and cx==9.1:vn=[vs[0],vn[1]]
 bands=[];bounds=[q for q in[vs,vn]if q];assert bounds,(fl,cx)
 if vs:bands.append(box(vs[0],7.02,vs[1],cy))
 if vn:bands.append(box(vn[0],cy,vn[1],7.58))
 if hl:bands.append(box(cx-.37,hl[0],max(q[1]for q in bounds),hl[1]))
 if hr:bands.append(box(min(q[0]for q in bounds),hr[0],cx+.37,hr[1]))
 desired=unary_union(bands);excess=roi.difference(desired)
 if cx==13.:excess=excess.intersection(box(cx-.36,7.03,vs[0],7.57)) # interior only
 cutter=extrude_poly(excess,floors[fl]+.00005,ceil[fl]);removed=(house^cutter).volume();house-=finish(cutter,'M_Wall_Interior','Wall ends matched to neighbouring finished planes, not assumed400mm column bounds');scope.append(cutter)
 changes.append({'floor':fl+1,'center_x':cx,'south_wall_x':vs,'north_wall_x':vn,'left_crosswall_y':hl,'right_crosswall_y':hr,'removed_m3':removed,'roi_xy':list(roi.exterior.coords),'desired_outline':desired.__geo_interface__})
ext=finish(cube([8.979999542236328,7.39995,floors[0]],[9.00002,9.56,ceil[0]]),'M_Wall_Interior','Continue the WC outer face without a20mm step')
door=J['DOOR_KITCHEN_F1__FRAME_Geometry']['bounds'];ext-=finish(cube([8.97,door[0][1]-.0001,floors[0]-.001],[9.01,door[1][1]+.0001,door[1][2]+.0001]),'M_Wall_Interior','Retain the complete WC doorway')
house+=ext;scope.append(ext)
house=put(HN,house,'Remove8–14cm inherited intersection blocks; join neighbouring wall planes continuously in rooms and WCs without filling door openings')
mask=union(scope);proof['walls']={'corrections':changes,'source_assumption_corrected':'V26.9 retained assumed source-column projections. Source bounding boxes are not surveyed structural evidence. New intersections follow neighbouring wall faces and the existing wall plan.','outside_scope_removed_m3':((original-house)-mask).volume(),'outside_scope_added_m3':((house-original)-mask).volume(),'components':len(house.decompose()),'floor_slab_and_stair_datums_retained':True}

STONE='M_V21_GATE_REF_02';TRIM='M_V21_GATE_REF_03';RELIEF='M_V21_GATE_REF_04';piers=[];frame_layout=[]
def beveled_rect(x0,x1,y0,y1,b):return[(x0+b,y0),(x1-b,y0),(x1,y0+b),(x1,y1-b),(x1-b,y1),(x0+b,y1),(x0,y1-b),(x0,y0+b)]
def ring(cx,cy,u,no,w,z0,z1,border=.014):
 m=cube([-w/2,-.018,z0],[w/2,.013,z1])-cube([-w/2+border,-.02,z0+border],[w/2-border,.02,z1-border])
 return m.transform([[u[0],no[0],0,cx],[u[1],no[1],0,cy],[0,0,1,0]])
for i,(x0,x1)in enumerate([(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)],1):
 core=section(beveled_rect(x0,x1,-11.87,-11.294,.012),3.51).translate([0,0,-.40]);parts=[core]
 # Feet expand toward the outside and the court, with the inner doorway
 # edge retained for the original working hinges and leaf clearance.
 lo,hi=(4.80,x1)if i==1 else(x0,8.40)
 parts += [cube([lo,-12.08,-.51],[hi,-11.25,-.405]),cube([lo+.035 if i==1 else lo,-12.025,-.41],[hi if i==1 else hi-.035,-11.26,-.326])]
 waist=cube([x0-.022,-11.895,.608],[x1+.022,-11.28,.738])
 # The retained door's hinge-side timber starts at Y=-11.574 when shut.
 # Recess only the inner waist return to keep that full swept edge clear.
 if i==1:waist-=cube([x1-.0001,-11.615,.60],[x1+.03,-11.27,.75])
 else:waist-=cube([x0-.03,-11.615,.60],[x0+.0001,-11.27,.75])
 parts.append(waist)
 for face,px,py,u,no,w in [('front',(x0+x1)/2,-11.87,[1,0],[0,-1],.326),('left',x0,-11.67,[0,-1],[-1,0],.15),('right',x1,-11.67,[0,1],[1,0],.15)]:
  for z0,z1 in[(-.305,.575),(.778,2.312),(2.395,3.025)]:parts.append(ring(px,py,u,no,w,z0,z1));frame_layout.append({'pier':i,'face':face,'z_m':[z0,z1],'width_m':w})
 piers.append(finish(union(parts),STONE,'Rectangular deep pier, vertical stone fields, waist course and flared bearing foot'))
 # Relocate the original narrow45deg stone pictures rigidly to the two
 # rectangular side faces. The original front pictures remain untouched.
 ex={r['name']:r for r in json.loads((W/'v26_9/Extra_Source_Index.json').read_text('utf8'))}
 for face,angle,tx in [('left_bevel',-np.pi/4,x0-.002),('right_bevel',np.pi/4,x1+.002)]:
  for band in[1,2]:
   n=f'V24_Gate_Reference_Relief_P{i}_{face}_{band}';a=np.load(W/'v26_9'/ex[n]['file']);cc=(a['v'][:,:2].min(0)+a['v'][:,:2].max(0))/2;c,s=np.cos(angle),np.sin(angle);R=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
   t=np.r_[tx,-11.67,0.]-R@np.r_[cc,0.];M=np.eye(4);M[:3,:3]=R;M[:3,3]=t;rigid.append({'name':n,'matrix_world_left_multiply':M.tolist(),'reason':'Rigidly reposition original narrow stone picture on rectangular side face; no stretch or pixel change'})
put('V26_10_Inner_Gate_Rectangular_Stone_Piers',union(piers),'Two deep rectangular piers with three vertical relief fields per face, retained waist carvings, and outward flared bases',new=True)
platform=native('SITE_V21_GATE_REFERENCE_LAYER_01_Geometry')+finish(cube([4.80,-12.15,-.70],[8.40,-11.18,-.50]),'M_V21_GATE_REF_01','One continuous entrance tread bonded to both pier feet')
put('SITE_V21_GATE_REFERENCE_LAYER_01_Geometry',platform,'One100mm front step; continuous entrance platform connects both flared pier foundations')

# Reuse the actual existing stone-relief atlas for the short upper panels.
# The sampling is baked into closed3D geometry, with no extra subdivision.
atlas=Path('E:/jz/JIA/Rebuild_V24/Textures/Gate_Carving_HeightAtlas.png');gray=np.flipud(np.asarray(Image.open(atlas).convert('RGB'),float).mean(2)/255.);layout=_atlas_layout(atlas);new_reliefs=[]
for i,(x0,x1)in enumerate([(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)],1):
 for face,a,b,key,nx in [('front',[(x0+x1)/2-.1409,-11.87],[(x0+x1)/2+.1409,-11.87],'flowers',64),('left',[x0,-11.6275],[x0,-11.7125],'vine',32),('right',[x1,-11.7125],[x1,-11.6275],'vine',32)]:
  rect=layout[key].copy();v0,v1=rect[1],rect[3];rect[1]=v0+(v1-v0)*.15;rect[3]=v0+(v1-v0)*.85
  v,polys,uv,stats=_panel_mesh_arrays(gray,rect,a,b,2.42,3.0,nx,112,.012);v=np.array(v);f=np.array([[q[0],q[k],q[k+1]]for q in polys for k in range(1,len(q)-1)],np.int32);uv=np.array(uv)[f]
  n=f'V26_10_Gate_Upper_Relief_P{i}_{face}';r,m=export(n,tracked(v,f,[RELIEF],np.zeros(len(f),int),uv,n),'Upper floral/leaf relief from the existing packed source atlas; closed baked mesh',new=True,smooth_stone=True);rows.append(r);new_reliefs.append({'name':n,'source_cell':key,'uv_rect':rect,'base_mesh_statistics':stats})
proof['gate']={'rectangular_core_m':{'width':.52380946,'depth':.576,'corner_bevel':.012},'front_step_top_m':-.5,'court_m':-.6,'front_step_rise_m':.1,'platform_bounds_m':[[4.8,-12.15,-.7],[8.4,-11.18,-.5]],'waist_z_m':[.608,.738],'frame_layout':frame_layout,'upper_reliefs':new_reliefs,'original_front_and_header_stone_pictures_unchanged':True,'original_side_pictures_rigidly_relocated':True,'source_atlas':str(atlas),'dimensions_are_photo_and_model_fit_not_surveyed':True}
archived=['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','V24_05_Gate_Upper_Pier_Bearing_1','V24_05_Gate_Upper_Pier_Bearing_2']
(D/'Prepared_Geometry.json').write_text(json.dumps({'objects':rows,'proof':proof,'remove':archived,'rigid_transforms':rigid},ensure_ascii=False,indent=2),'utf8');print('V26_10_PREPARED',len(rows),len(changes),'RIGID',len(rigid),flush=True)
