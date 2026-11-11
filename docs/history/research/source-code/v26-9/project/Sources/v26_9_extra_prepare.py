"""Local structural corrections; do not change protected screenwall geometry."""
from v26_2_common import *
import v26_2_common as C
from v26_8_native_cleanup import repair_native
from shutil import copy2
D=W/'v26_9';C.D=D;FD=W/'v26_8/Final'
J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
E={r['name']:r for r in json.loads((D/'Extra_Source_Index.json').read_text('utf8'))}
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));base_rows={r['name']:r for r in prep['objects']};rows={};proof={};animations=[]
WHITE='M_Wall_Interior';BRICK='M_V24_18_Continuous_Blue_Brick';BLACK='M_Metal_Black';GLASS='M_Glass_Clear'
def source(n,prepared=False):
 r=base_rows[n] if prepared else J.get(n,E.get(n));dd=D if prepared or n in E else FD
 return r,np.load(dd/(('Window_Base_' if prepared and n=='V26_3_House_Connected_Walls_And_Stairs' else '')+r['file']))
def native(n,prepared=False):
 r,a=source(n,prepared);uv=a['uv'].copy();bad=~np.isfinite(uv).all((1,2));uv[bad]=uv_project(a['v'],a['f'])[bad]
 return tracked(a['v'],a['f'],r['materials'],a['mi'],uv,n)
def put(n,m,why,**kw):
 r,m=export(n,m.simplify(.00002),why,**kw);a=np.load(D/r['file']);v,f,mi,uv=a['v'],a['f'],a['mi'],a['uv']
 if n=='V26_3_House_Connected_Walls_And_Stairs':v,f,mi,uv,repair=repair_native(v,f,mi,uv)
 else:
  # Retain distinct manifold vertices at inherited construction contacts;
  # globally welding coincident points would join unrelated touching skins.
  tt=v[f];area=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2
  edges=np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,ct=np.unique(edges,axis=0,return_counts=True)
  assert area.min()>0 and np.all(ct==2),(n,float(area.min()),int((ct!=2).sum()))
  repair={'minimum_triangle_area_m2':float(area.min()),'indexed_manifold_edges':True,'inherited_touching_shell_vertices_not_globally_welded':True}
 np.savez_compressed(D/r['file'],v=v,f=f,mi=mi,uv=uv);r['triangles']=len(f);r['bounds']=[v.min(0).tolist(),v.max(0).tolist()];r['native_cleanup']=repair;rows[n]=r;return m
def raw(n,v,a,r,why,**kw):
 fn=n+'.npz';np.savez_compressed(D/fn,v=v,f=a['f'],mi=a['mi'],uv=a['uv']);rows[n]={'name':n,'file':fn,'materials':r['materials'],'triangles':len(a['f']),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'reason':why,**kw}
def beam(a,b,w,h):
 a=np.asarray(a,float);b=np.asarray(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0.,0.,1.]);v/=np.linalg.norm(v);no=np.cross(u,v)
 return mf.Manifold.cube([w,h,float(np.linalg.norm(b-a))],True).transform(np.c_[v,no,u,(a+b)/2])

# A real 400mm source pier is visible in the actual room photo. Retain it;
# remove only the extra 12.2mm finish halo/step at rear room junctions.
HN='V26_3_House_Connected_Walls_And_Stairs';house=native(HN,True);changes=[];trims=[]
cores=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
for c in cores:
 if not c['name'].startswith('KZ_'):continue
 lo,hi=np.asarray(c['bounds_m']);center=(lo+hi)/2
 if abs(center[1]-7.3)>.02:continue
 # Leave the perpendicular wall bands continuous into the core. Trim only
 # the exposed outer corner finish, outside those connecting wall bands.
 for axis in [0,1]:
  other=1-axis
  for side in [-1,1]:
   p0=lo.copy();p1=hi.copy();p0[:2]-=.0123;p1[:2]+=.0123
   if side<0:p0[axis]=lo[axis]-.0123;p1[axis]=lo[axis]-.00002
   else:p0[axis]=hi[axis]+.00002;p1[axis]=hi[axis]+.0123
   for part in [-1,1]:
    aa=p0.copy();bb=p1.copy()
    if part<0:bb[other]=center[other]-.122
    else:aa[other]=center[other]+.122
    trims.append(cube(aa,bb))
 changes.append({'core':c['name'],'bounds_m':c['bounds_m'],'maximum_finish_reduction_m':.01228,'perpendicular_wall_bands_preserved_m':.244})
halo=union(trims);halo_removed=(house^halo).volume();house-=finish(halo,WHITE,'Remove only exposed surplus finish; leave real cores and wall bonds continuous')
header=cube([.20002,7.0,9.9499],[3.69998,7.6,10.220000267028809])
hall_header=cube([4.10002,7.0,9.15],[8.89998,7.6,10.220000267028809]);header=header+hall_header
removed=(house^header).volume();house-=finish(header,'M_V26_3_Neutral_White_Interior_Ceiling','Remove residual terrace header and user-marked F3 corridor drop up to the retained ceiling plane')
house=put(HN,house,'Retain source structural piers and photo-supported door returns; remove extra finish halos and the residual F3 terrace ceiling header')
proof['room_returns']={'cause':'200-240mm masonry joins retained400mm native KZ piers, plus an unintended12.2mm finish halo. Actual144236 photo confirms a door-side wall return. Only the halo is reduced; real cores remain.','adjustments':changes,'real_pier_core_retained':True,'finish_removed_m3':halo_removed}
proof['f3_ceiling']={'cause':'Earlier terrace opening stopped at9.951m; the adjacent corridor also retained a visible crossbeam drop. User requested a flat F3 ceiling here.','cut_regions_m':[[[.20002,7.0,9.9499],[3.69998,7.6,10.220000267028809]],[[4.10002,7.0,9.15],[8.89998,7.6,10.220000267028809]]],'removed_m3':removed,'flat_ceiling_kept':True,'explicit_user_requested_visible_beam_drop_removal':True}

# Continue the existing front edge into all four sides without separate
# projecting corner pads. Source Roman-column capitals stay unchanged.
n='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry';edge=native(n);lo=np.array(J[n]['bounds'][0]);hi=np.array(J[n]['bounds'][1]);z0,z1=lo[2],hi[2];x0,x1=lo[0],hi[0];back=2.22;w=.24
bands=union([cube([x0,hi[1]-.01,z0],[x0+w,back,z1]),cube([x1-w,hi[1]-.01,z0],[x1,back,z1]),cube([x0,back-w,z0],[x1,back,z1])])
put(n,edge+finish(bands,'M_Wall_Exterior','Continuous rectangular balcony edge returns'),'Retain source front edge and Roman columns; complete three missing rectangle edges without individual corner pads')
proof['balcony_edge']={'outer_xy_m':[[float(x0),float(lo[1])],[float(x1),back]],'edge_z_m':[float(z0),float(z1)],'added_band_width_m':w,'roman_column_meshes_unchanged':True}

# Restore the north gable from the known V24.28 280mm inward translation.
# Translate the thin wall rather than accumulating a second thick layer.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';masonry=native(n);zone=cube([8.341,-3.281,-.6],[14.301,-2.40,5.8])
# The old low veranda closure has a different profile from the retained
# curved coping. Build the thin wall to the actual underside of that cap.
cap=native('V24_17_Kitchen_North_Gable_Coping');cr,ca=source('V24_17_Kitchen_North_Gable_Coping');xs=np.unique(np.r_[8.341,9.43,14.10,np.clip(ca['v'][:,0],8.341,14.10)])
tops=[]
for xx in xs:
 hh=cap.ray_cast([float(np.clip(xx,8.34101,14.09999)),-3.035,1.9],[float(np.clip(xx,8.34101,14.09999)),-3.035,5.8]);assert hh,('Missing cap section',xx)
 tops.append(float(min(q.position[2]for q in hh))+.008)
prof=[(float(xs[0]),-.55),(float(xs[-1]),-.55)]+[(float(x),float(z))for x,z in zip(xs[::-1],tops[::-1])]
north_full=section(prof,.18).transform([[1,0,0,0],[0,0,-1,-2.575],[0,1,0,0]])
part=finish(north_full^cube([9.43,-2.756,-.6],[14.1001,-2.574,5.8]),BRICK,'180mm complete north wall follows actual retained coping underside')
closure_new=finish(north_full^cube([8.3409,-2.756,-.6],[9.43,-2.574,5.8]),BRICK,'Complete low veranda closure to curved cap rather than exposing timber above it')
new=(masonry-zone)+part
bond=section([(13.915,-2.575),(14.115,-2.575),(14.25,-3.36),(14.05,-3.36)],2.99720006).translate([0,0,-.55]);new+=finish(bond,BRICK,'200mm bonded return connecting restored north gable to existing east wall')
row,new=export('Temp_Kitchen_Wall',new,'Restored outer gable line');rr=np.load(D/row['file']);v=rr['v'];f=rr['f'];mi=rr['mi'].copy();uv=rr['uv'].copy();t=v[f];cc=t.mean(1);nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-20)
white=np.array([('White'in row['materials'][i] or 'Interior'in row['materials'][i] or 'Limewash'in row['materials'][i])for i in mi]);outside=white&(cc[:,0]>12.25)&(cc[:,0]<13.70)&(cc[:,1]<-11.6401)&(cc[:,1]>-12.1)&((nn[:,0]<-.25)|(nn[:,1]<-.25))
for mat in [BRICK,WHITE]:
 if mat not in row['materials']:row['materials'].append(mat)
mi[outside]=row['materials'].index(BRICK);uv[outside]=uv_project(v,f)[outside]
inner_north=(cc[:,0]>9.429)&(cc[:,0]<14.101)&(abs(cc[:,1]+2.755)<.001)&(nn[:,1]<-.8);mi[inner_north]=row['materials'].index(WHITE)
# Match the interior of the new L bond, keeping the external face brick.
inside_bond=(cc[:,0]>13.914)&(cc[:,0]<14.116)&(cc[:,1]>-3.151)&(cc[:,1]<-2.574)&(nn[:,0]<-.5);mi[inside_bond]=row['materials'].index(WHITE)
new=tracked(v,f,row['materials'],mi,uv,'Kitchen restored gable and exterior brick corner')
put(n,new,'Undo280mm north-gable setback; retain180mm gable; bond east return; use blue brick on the external kitchen/storage corner only')
proof['kitchen_wall']={'known_prior_error_source':'v24_28_prepare.py: part.translate([0,-.28,0])','north_gable_outward_restore_m':.28,'replaced_old_wall_instead_of_overlay':True,'timber_meshes_unchanged':True,'new_bond_thickness_m':.20,'gable_thickness_m':.18,'complete_wall_top_from_actual_native_coping':True,'coping_section_stations':len(xs),'external_white_corner_faces_reassigned':int(outside.sum())}
rr,closure_new=export('Temp_Complete_Veranda_Closure',closure_new);aa=np.load(D/rr['file']);tt=aa['v'][aa['f']];nnn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);mmi=aa['mi'].copy();mmi[nnn[:,1]<-1e-8]=rr['materials'].index(WHITE);closure_new=tracked(aa['v'],aa['f'],rr['materials'],mmi,aa['uv'],'Blue brick outside and white plaster inside completed closure')
put('V24_24_Kitchen_North_Veranda_White_Closure',closure_new,'Restore outer wall line and close the entire space below the source curved coping; brick outside, white inside')
for n in ['V24_03_Kitchen_Rear_Stone_Plinth','V24_17_Kitchen_North_Gable_Coping','V24_22_North_Verge','V24_22_North_Verge_Bead']+[f'V24_19_Kitchen_North_Faceted_Head_Frame_{i}'for i in [1,2,3]]:
 r,a=source(n);v=a['v'].copy();v[:,1]+=.28;raw(n,v,a,r,'Restore attached north gable trim to pre-setback outer line, preserving shapes and UVs')
n='V24_16_Storage_Entrance_White_Wall_Return';r,a=source(n);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);mi=a['mi'].copy();r=dict(r,materials=list(r['materials'])+[BRICK]);mask=(no[:,0]<-1e-8)|(no[:,1]<-1e-8);mi[mask]=len(r['materials'])-1;uv=a['uv'].copy();uv[mask]=uv_project(a['v'],a['f'])[mask];raw(n,a['v'],{'f':a['f'],'mi':mi,'uv':uv},r,'Blue-brick external return faces; retain the white inside jamb face')

# Continue only the cut stone guard terminal into the protected wall face.
# Existing carved panels/openings are unchanged; no extra stone post.
n='SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry';guard=native(n);bay=json.loads((W/'v24_10/Prepared_Geometry.json').read_text('utf8'))['guard_bays'][0];aa=np.array(bay['a']);bb=np.array(bay['b']);u=(bb-aa)/np.linalg.norm(bb-aa);no=np.array(bay['normal']);wall_x=13.130000114440918
start=aa+u*((wall_x-.002-aa[0])/u[0]);end=aa+u*.09;parts=[]
for z,w,h in [(-.345,.105,.155),(-.03,.077,.52),(.337,.078,.294),(.51,.105,.145)]:parts.append(beam([*start,z],[*end,z],w,h))
for s in [-1,1]:
 for z in [-.253,.194]:parts.append(beam([*(start+no*s*.043),z],[*(end+no*s*.043),z],.018,.020))
extension=finish(union(parts),'M_V18_Storage_Stone_Guard','Continue existing terminal profiles without rescaling source carved panels')
put(n,guard+extension,'Extend original cut stone rail and panel profiles to the actual secondary wall plane; retain screenwall and existing panels')
proof['stone_guard']={'terminal_start_xy_m':start.tolist(),'source_end_overlap_xy_m':end.tolist(),'actual_secondary_wall_x_m':wall_x,'extension_length_m':float(np.linalg.norm(end-start)),'screenwall_meshes_unchanged':True,'original_carved_panels_and_openings_unscaled':True,'no_new_terminal_post':True}

# Raise lintel and timber head400mm; remove the obsolete plain neck while
# keeping every original stone-relief vertex and UV unchanged in shape.
delta=.40
for n in ['SITE_V21_GATE_REFERENCE_LAYER_05_Geometry','SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM_Geometry']+[f'V24_Gate_Reference_Relief_Header_{i}'for i in [1,2,3]]:
 r,a=source(n);v=a['v'].copy();v[:,2]+=delta;raw(n,v,a,r,'Raise whole lintel/head without stretching original relief, shape, or UV')
for n in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','V24_07_Gate_Moulded_Timber_Jambs','GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry','SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 r,a=source(n);v=a['v'].copy();v[:,2]+=delta*np.clip((v[:,2]-.75)/(2.0732998848-.75),0,1);raw(n,v,a,r,'Raise gate opening and plain jamb/head borders; original stone picture relief meshes stay separate and untouched')
# The existing bearing bodies shorten to a15mm concealed bearing under
# the unchanged soffit. None of the carved pillar panels is transformed.
n='V24_05_Gate_Plain_Neck_Above_Carved_Lintel';r,a=source(n);v=a['v'].copy();v[:,2]=np.interp(v[:,2],[v[:,2].min(),v[:,2].max()],[3.095,3.117000102996826]);raw(n,v,a,r,'Compress the obsolete429mm plain neck to a22mm concealed upper bearing')
for n in ['V24_05_Gate_Upper_Pier_Bearing_1','V24_05_Gate_Upper_Pier_Bearing_2']:
 r,a=source(n);v=a['v'].copy();v[:,2]=np.interp(v[:,2],[v[:,2].min(),v[:,2].max()],[3.021999979,3.117000103]);raw(n,v,a,r,'Fit upper plain pier bearing to raised lintel and retained soffit')
proof['inner_gate']={'head_raise_m':delta,'old_plain_neck_height_m':.4290001392,'new_plain_neck_height_m':.022000103,'roof_soffit_unchanged':True,'original_side_stone_picture_meshes_unchanged':True,'header_reliefs_rigid_translation_only':True,'stone_threshold_unchanged':True,'photo':'D:/Desktop/屏幕截图 2026-10-24 150401.jpg','dimension_status':'Photo/native proportion fit, not field measured'}

# Rear windows: fixed upper lights and actual paired lower sliding sashes,
# independent tracks, overlapping meeting stiles and recessed pull handles.
for n,r in J.items():
 if not n.startswith('WINDOW_BACK_F'):continue
 a=np.load(FD/r['file']);lo=a['v'].min(0);hi=a['v'].max(0);x0,y0,z0=lo;x1,y1,z1=hi;gy=a['v'][a['f'][a['mi']==r['materials'].index(GLASS)]];zs=np.unique(np.round(gy[:,:,2],6));trans=(zs[1]+zs[2])/2
 count=4 if x1-x0>2.5 else 2;bar=.04;half=(x1-x0-2*bar)/count;mid=(y0+y1)/2
 outer=union([cube([x0,y0,z0],[x1,y1,z0+.04]),cube([x0,y0,z1-.04],[x1,y1,z1]),cube([x0,y0,z0],[x0+.04,y1,z1]),cube([x1-.04,y0,z0],[x1,y1,z1]),cube([x0+.04,y0,trans-.025],[x1-.04,y1,trans+.025])]);upper=[]
 for i in range(count):
  xa=x0+.04+i*half;xb=xa+half
  if i:outer+=cube([xa-.015,y0,trans+.025],[xa+.015,y1,z1-.04])
  upper.append(cube([xa+.016,mid-.003,trans+.026],[xb-.016,mid+.003,z1-.041]))
 # Two narrow extruded rails run inside the retained90mm reveal.
 for yy in [mid-.025,mid+.025]:
  for za,zb in [(z0+.04,z0+.052),(trans-.039,trans-.025)]:outer+=cube([x0+.04,yy-.004,za],[x1-.04,yy+.004,zb])
 fixed=finish(outer,BLACK,'Original outline and fixed upper transom with twin guide rails')+finish(union(upper),GLASS,'Fixed rear upper lights')
 put(n,fixed,'Rear window fixed frame and upper lights; lower paired sashes travel on separate parallel tracks')
 for i in range(count):
  xa=x0+.04+i*half-.009;xb=x0+.04+(i+1)*half+.009;xa=max(xa,x0+.041);xb=min(xb,x1-.041);yy=mid+(-.025 if i%2==0 else .025);za=z0+.054;zb=trans-.040;depth=.027;profile=.032
  frame=union([cube([xa,yy-depth/2,za],[xb,yy+depth/2,za+profile]),cube([xa,yy-depth/2,zb-profile],[xb,yy+depth/2,zb]),cube([xa,yy-depth/2,za],[xa+profile,yy+depth/2,zb]),cube([xb-profile,yy-depth/2,za],[xb,yy+depth/2,zb])])
  hx=xb-.017 if i%2==0 else xa+.017;hz=(za+zb)/2;handle=cube([hx-.009,yy-.023,hz-.07],[hx+.009,yy-.013,hz+.07]);frame+=handle
  pane=cube([xa+profile+.0004,yy-.003,za+profile+.0004],[xb-profile-.0004,yy+.003,zb-profile-.0004])
  name=n.replace('_Geometry','')+'_Sliding_Sash_'+str(i+1);sash=finish(frame,BLACK,'Rear sliding sash with meeting stile and recessed pull')+finish(pane,GLASS,'Sliding pane clear of black sash')
  put(name,sash,'Rear sliding sash,50mm track separation; horizontal sliding only',new=True)
  travel=float(half-.055)if i%2==0 else 0.;other=-float(half-.055)if i%2 else 0.
  animations.append({'object':name,'parent':n.replace('_Geometry',''),'axis':0,'closed_frame':1,'open_frame':40,'open_translation_m':travel,'alternate_open_translation_m':other,'track_center_y_m':float(yy),'closed_bounds':[[float(xa),float(za)],[float(xb),float(zb)]]})
proof['rear_sliding_windows']={'windows':9,'sliding_sashes':len(animations),'fixed_upper_transoms_preserved':True,'track_separation_m':.05,'frame_outline_and_wall_openings_unchanged':True,'lower_sash_horizontal_only':True,'controls':'Timeline1=closed,40=left sash open,60=closed,80=right sash open,100=closed; leave roam withEsc to inspect the window animation'}

prep['objects']=[rows.pop(n,r)for n,r in base_rows.items()]+list(rows.values());prep['proof']['additional_repairs']=proof;prep['new_sliding_animations']=animations
(D/'Prepared_All_Geometry.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8')
print('V26_9_EXTRA_READY',len(prep['objects']),'SLIDING',len(animations),flush=True)
