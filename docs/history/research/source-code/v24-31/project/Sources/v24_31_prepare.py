"""Scoped native geometry repairs; give each visible ground patch one owner."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_31';sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point,box,shape
from shapely.ops import unary_union,triangulate,nearest_points
from v24_16_common import solid,cube,union,section,rod
INDEX={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};OUT={'raw_objects':[],'remove':[],'proof':{}}
PLAN={r['name']:shape(r['outline']) for r in json.loads((D/'Plan_Outlines.json').read_text('utf8'))}
def src(n):return np.load(D/INDEX[n]['file'])
def load(n):
 a=src(n);return solid(a['v'],a['f'],n)
def polys(g):return [g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon' and p.area>1e-10]
def prism(g,z0,z1):
 ms=[]
 for p in polys(g):
  if p.area<1e-10:continue
  m=section(list(p.exterior.coords)[:-1],z1-z0).translate([0,0,z0])
  for h in p.interiors:m-=section(list(h.coords)[:-1],z1-z0+.02).translate([0,0,z0-.01])
  if m.volume()>1e-10:ms.append(m)
 return union(ms)
def mesh(m):
 a=m.to_mesh64();return np.asarray(a.vert_properties[:,:3]).copy(),np.asarray(a.tri_verts).copy()
def put(n,m,materials,mi=None,uv=None,info=None):
 v,f=m if isinstance(m,tuple) else mesh(m);v=np.asarray(v);f=np.asarray(f);fn='NEW_'+n+'.npz'
 if mi is None:mi=np.zeros(len(f),int)
 if uv is None:uv=v[f][:,:,:2].copy()
 np.savez_compressed(D/fn,v=v,f=f,mi=np.asarray(mi),uv=uv)
 row={'name':n,'file':fn,'materials':materials,'vertices':len(v),'triangles':len(f)}
 if info:row.update(info)
 OUT['raw_objects'].append(row);print('PREPARED',n,len(v),len(f),flush=True)
def foot(n):
 if n in PLAN:return PLAN[n]
 a=src(n);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return unary_union([Polygon(p[:,:2]) for p in t[abs(no[:,2])>1e-10]]).buffer(0)
def height_data(n):
 a=src(n);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return t[no[:,2]>1e-9]
def height(t,x,y):
 p=t[:,:,:2];A=p[:,1]-p[:,0];B=p[:,2]-p[:,0];Q=np.array([x,y])-p[:,0];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];safe=np.where(abs(det)>1e-10,det,1);u=(Q[:,0]*B[:,1]-Q[:,1]*B[:,0])/safe;w=(A[:,0]*Q[:,1]-A[:,1]*Q[:,0])/safe;ok=(abs(det)>1e-10)&(u>=-2e-5)&(w>=-2e-5)&(u+w<=1.00002)
 if not ok.any():return None
 return float((t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]))[ok].max())
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)

# Cut the level pad back to the inner edge of the curb. Previously both
# cap stones and pad occupied exactly z=-0.60 over the same 2.4 square metres.
pad=foot('V24_30_Outer_Yard_White_Building_Pad');caps=foot('V24_30_Individual_Roadside_Curb_Stones');base=foot('V24_30_Graded_Approach_Curb_Retaining_Base');curb_band=unary_union([base,caps]).buffer(.002,join_style=2).buffer(-.001,join_style=2)
padnew=pad.difference(curb_band).buffer(0)
put('V24_30_Outer_Yard_White_Building_Pad',prism(padnew,-4.8,-.6),INDEX['V24_30_Outer_Yard_White_Building_Pad']['materials'])
put('V24_30_Graded_Approach_Curb_Retaining_Base',union([load('V24_30_Graded_Approach_Curb_Retaining_Base'),prism(curb_band,-.67,-.6025)])-load('V24_30_Individual_Roadside_Curb_Stones'),['M_V22_Courtyard_Stone_3'])
OUT['proof']['pad_curb']={'before_coplanar_overlap_m2':pad.intersection(caps).area,'after_coplanar_overlap_m2':padnew.intersection(caps).area,'joint_backing_z_m':-.6025,'pad_top_m':-.6,'pad_area_m2':padnew.area,'pad_outline':padnew.__geo_interface__,'curb_band':curb_band.__geo_interface__}
# Joint beds must not retain a second almost coincident top under each stone.
# Recess them by the actual full stone depth; keep the exposed joint recess.
OUT['proof']['paver_beds']=[]
for label in ['Low_Main_Court','High_North_Lane_And_Rear']:
 n='V24_30_'+label+'_Joint_Base';stone='V24_30_'+label+'_Running_Bond_Stone';m=load(n)-load(stone);put(n,m,INDEX[n]['materials']);OUT['proof']['paver_beds'].append({'name':n,'visible_joint_recess_m':.0015,'hidden_bed_face_depth_below_stone_top_m':.03,'duplicate_near_top_faces_removed':True})

# Recover the whole storage/gate approach footprint, including the floor
# lost when superseded court meshes were retired. Keep the outer wall trace.
allplans=unary_union([g for n,g in PLAN.items() if not n.startswith('OLD_')]+[g for n,g in PLAN.items() if n.startswith('OLD_')]).buffer(.002).buffer(-.002)
site=Polygon(max(polys(allplans),key=lambda p:p.area).exterior)
approach=site.intersection(box(-14.88,-20.,13.55,-7.0))
roadnames=['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry','SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP_Geometry','V24_30_Outer_Gate_Swing_Clearance_Graded_Apron']
exclude=unary_union([padnew,curb_band,foot('V24_30_Low_Main_Court_Joint_Base'),foot('SITE_KITCHEN_STONE_FLOOR_Geometry'),foot('SITE_V14_INNER_STORAGE_FLOOR_Geometry'),foot('SITE_V14_OUTER_STORAGE_FLOOR_Geometry'),foot('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry')])
roadshape=unary_union([foot(n) for n in roadnames]+[approach,foot('V24_23_Storage_Flush_Alley_Floor')]).difference(exclude).buffer(0)
ht={n:height_data(n) for n in roadnames};hc={}
def roadz(x,y):
 key=(round(x,7),round(y,7))
 if key in hc:return hc[key]
 vals=[]
 for n in roadnames:
  z=height(ht[n],x,y)
  if z is not None:vals.append(z-(.002 if 'Apron' in n else 0))
 if vals:z=max(vals)
 else:
  near=[]
  for n in roadnames:
   p=nearest_points(foot(n),Point(x,y))[0];h=height(ht[n],p.x,p.y)
   if h is not None:near.append((Point(x,y).distance(p),h-(.002 if 'Apron' in n else 0)))
  z=min(near,key=lambda q:q[0])[1] if near else -.60+.20*smooth((x-8.0)/4.90)
 # The new filled approach meets the retained storage threshold at -0.40.
 if x>7.89:z=-.60+.20*smooth((x-8.0)/4.90)
 hc[key]=z;return z
cells=[]
xl,yl,xh,yh=roadshape.bounds
for x in np.arange(math.floor(xl),xh,.65):
 for y in np.arange(math.floor(yl),yh,.65):
  g=roadshape.intersection(box(x,y,x+.65,y+.65))
  if g.is_empty or g.area<1e-9:continue
  v,f=mesh(prism(g,-4.8,0.))
  for i,(xx,yy,zz) in enumerate(v):
   if zz>-.01:v[i,2]=roadz(xx,yy)
  cells.append(solid(v,f,'road cell'))
road=union(cells)
put('V24_31_Continuous_Gray_Road_And_Storage_Approach',road,['M_V12_Road_Concrete'])
OUT['remove']+=roadnames+['SITE_V15_ENTRY_PAVEMENT_SUPPORTED_SUBGRADE_Geometry','V24_25_Storage_Entrance_Continuous_Light_Gray_Finish','V24_23_Storage_Flush_Alley_Floor']
OUT['proof']['continuous_road']={'outline':roadshape.__geo_interface__,'area_m2':roadshape.area,'storage_threshold_z_m':-.40,'inner_landing_z_m':-.60,'single_visible_surface':True,'removed_layers':list(OUT['remove']),'closed_solid_volume_m3':road.volume(),'material':'M_V12_Road_Concrete'}

# Extend the existing gallery base itself; avoid adding a face over its fascia.
n='SITE_KITCHEN_STONE_FLOOR_Geometry';a=src(n);v=a['v'].copy();oldbottom=float(v[:,2].min());v[abs(v[:,2]-oldbottom)<1e-5,2]=-.83
put(n,(v,a['f']),INDEX[n]['materials'],a['mi'],a['uv']);OUT['proof']['gallery_base']={'old_bottom_m':oldbottom,'new_bottom_m':-.83,'top_retained_m':float(v[:,2].max()),'gap_to_court_closed':True}

# Remove old earth only under actual, closed replacement ground. Barycentric
# interpolation retains the material and UVs of the untouched exterior terrain.
trim=unary_union([roadshape.buffer(.004),curb_band,padnew]);n='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';a=src(n);v=a['v'];f=a['f'];mi=a['mi'];uv=a['uv'];vv=v.tolist();ff=[];mm=[];uu=[];cache={tuple(np.round(q,8)):i for i,q in enumerate(v)};lo=np.array(trim.bounds[:2]);hi=np.array(trim.bounds[2:]);kept=0
for face,mat,tex in zip(f,mi,uv):
 t=v[face];xy=t[:,:2]
 if ((xy.max(0)<lo)|(xy.min(0)>hi)).any():ff.append(face);mm.append(mat);uu.append(tex);kept+=1;continue
 A=xy[1]-xy[0];B=xy[2]-xy[0];det=A[0]*B[1]-A[1]*B[0]
 if abs(det)<1e-12:
  if not all(trim.covers(Point(q))for q in xy):ff.append(face);mm.append(mat);uu.append(tex);kept+=1
  continue
 p=Polygon(xy)
 if not trim.intersects(p):ff.append(face);mm.append(mat);uu.append(tex);kept+=1;continue
 diff=p.difference(trim)
 if diff.is_empty:continue
 for part in polys(diff):
  for tr in triangulate(part):
   if tr.area<1e-12 or not part.covers(tr.representative_point()):continue
   q=np.array(tr.exterior.coords)[:3];Q=q-xy[0];u=(Q[:,0]*B[1]-Q[:,1]*B[0])/det;w=(A[0]*Q[:,1]-A[1]*Q[:,0])/det;p3=t[0]+u[:,None]*(t[1]-t[0])+w[:,None]*(t[2]-t[0]);tx=tex[0]+u[:,None]*(tex[1]-tex[0])+w[:,None]*(tex[2]-tex[0])
   if det<0:p3=p3[::-1];tx=tx[::-1]
   ids=[]
   for q in p3:
    k=tuple(np.round(q,8))
    if k not in cache:cache[k]=len(vv);vv.append(q.tolist())
    ids.append(cache[k])
   if len(set(ids))==3:ff.append(ids);mm.append(mat);uu.append(tx)
put(n,(np.array(vv),np.array(ff)),INDEX[n]['materials'],np.array(mm),np.array(uu));OUT['proof']['soil_trim']={'untouched_triangles':kept,'footprint':trim.__geo_interface__,'earth_below_road_removed':True}

# Under-window opaque walls use the existing wall's exact footprint. Replace
# only these low regions in both core and finish, then make them one full-depth
# solid down through the slab edge. Existing window frames and actions stay.
cladname='HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry';clad=load(cladname);coreproof=[]
for fl,floor,sides in [(1,-.45,['L','R']),(2,3.450024414,['L','R']),(3,7.05,['R'])]:
 core=load(f'FACADE_CONTINUOUS_F{fl}_Geometry');repl=[]
 # The previous low-opening infill was 424mm thick, while the original
 # bathroom side wall is 200mm. Trim that raised patch to the original faces.
 for wcside in (['LEFT','RIGHT'] if fl in [1,2] else ['RIGHT']):
  x=0. if wcside=='LEFT' else 13.
  core-=union([cube([x-.25,7.94998,floor+.85],[x-.1000005,9.15002,floor+2.65]),cube([x+.1000005,7.94998,floor+.85],[x+.25,9.15002,floor+2.65])])
 ceil={1:3.3200194836,2:6.9199953079,3:10.220044136}[fl];beamlo=ceil-.27001953
 # Existing walls stop below separate BIM beams. Continue their exact plan
 # through the beam zone, with the same finish and no projecting belt.
 def top_plan(m):
  ps=[Polygon(p)for p in m.slice(beamlo-.01).to_polygons()if len(p)>2];return unary_union(ps).intersection(box(3.6,7.1,9.35,10.02)).buffer(0)
 cp=top_plan(core);core=union([core,prism(cp,beamlo-.012,ceil),cube([4.0,9.7,floor],[7.7,9.9,ceil])])
 pn=f'PARTITIONS_JOINED_F{fl}_Geometry';part=load(pn);pp=top_plan(part);part=union([part,prism(pp,beamlo-.012,ceil),cube([3.8,7.2,floor],[4.0,9.9,ceil]),cube([4.0,7.2,floor],[4.1,7.4,ceil])])
 if fl==1:
  infill='HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS_Geometry';part=union([part,load(infill)]);OUT['remove'].append(infill)
 stairvoid=cube([4.0,7.4,floor-.001],[7.7,9.7,ceil+.001]);part-=stairvoid;core-=stairvoid
 put(pn,part,INDEX[pn]['materials'])
 for side in sides:
  x0=0 if side=='L' else 9.1;sill=floor+.60;zone=box(x0-.24,.78,x0+4.14,2.215)
  cs=core.slice(floor+.30);ps=[Polygon(p)for p in cs.to_polygons()if len(p)>2];fp=unary_union(ps).intersection(zone).buffer(0)
  assert fp.area>.2,(fl,side,fp.area)
  cut=prism(zone,floor-.205,sill-.002)
  core-=cut;clad-=cut
  wall=prism(fp,floor-.20,sill-.002);repl.append(wall)
  coreproof.append({'floor':fl,'side':side,'floor_z_m':floor,'sill_z_m':sill,'bottom_z_m':floor-.20,'footprint':fp.__geo_interface__,'closed_volume_m3':wall.volume()})
 put(f'FACADE_CONTINUOUS_F{fl}_Geometry',core,INDEX[f'FACADE_CONTINUOUS_F{fl}_Geometry']['materials'])
 put(f'V24_31_F{fl}_Complete_Bay_Underwindow_Walls',mf.Manifold.compose(repl),['M_Stone'])
put(cladname,clad,INDEX[cladname]['materials']);OUT['proof']['bay_underwalls']=coreproof

# Obsolete complete reveal assemblies are not part of the five high windows.
# Their surviving side faces are the unwanted fins below the bathroom glass.
wc=[]
for fl,sides in [(1,['LEFT','RIGHT']),(2,['LEFT','RIGHT']),(3,['RIGHT'])]:
 for side in sides:
  n=f'CONSTRUCTION_SILL_WINDOW_{side}_C1212_F{fl}_Geometry';OUT['remove'].append(n);wc.append(n)
OUT['proof']['bathroom']={'obsolete_surrounds_removed':wc,'five_frosted_high_windows_retained':True,'old_infill_thickness_m':.424,'corrected_wall_thickness_m':.200001,'raised_low_opening_infill_trimmed_to_existing_wall_faces':True}

# Retire the separate stair-wall beam proxies after continuing the actual
# walls to the ceiling. Trim column projections on the same plain left wall.
beamproof=[]
for fl in [1,2,3]:
 for n in [f'BEAM_X_F{fl}_9.8_3.9_Geometry',f'BEAM_Y_F{fl}_3.9_7.3_Geometry',f'BEAM_Y_F{fl}_9.1_7.3_Geometry']:
  OUT['remove'].append(n);beamproof.append({'name':n,'separate_beam_proxy_removed':True,'wall_continued_to_ceiling':True})
 for j in [2,3]:
  n=f'KZ_2_{j}_F{fl}_Geometry'
  if n in INDEX:
   m=load(n);before=m.volume();m-=cube([3.8,7.099,-1],[4.21,10.001,15]);put(n,m,INDEX[n]['materials']);beamproof.append({'name':n,'projection_removed_m3':before-m.volume(),'left_finished_wall_x_m':4.0})
OUT['proof']['stair_wall']=beamproof
# The old fascia also followed the internal stair opening, creating the
# projecting belt circled in the screenshot. Keep its exterior components.
for fl in [2,3]:
 n=f'FLOOR_FASCIA_CONTINUOUS_F{fl}_Geometry';m=load(n);before=m.volume();m-=cube([3.95,7.15,-1],[7.94,9.78,15]);put(n,m,INDEX[n]['materials']);OUT['proof']['stair_wall'].append({'name':n,'removed_internal_edge_fascia_m3':before-m.volume(),'exterior_fascia_retained':True})
 n=f'SLAB_JOINED_F{fl}_Geometry';m=load(n);before=m.volume();m-=cube([4.0,7.29999,-1],[4.10001,9.70001,15]);put(n,m,INDEX[n]['materials']);OUT['proof']['stair_wall'].append({'name':n,'slab_edge_projection_removed_m3':before-m.volume(),'opening_left_edge_flush_x_m':4.0,'floor_height_retained':True})

# Delete the additional red finish; retain the grey structural third-floor slab.
OUT['remove'].append('HOUSE_V20_F3_RIGHT_BEDROOM_RED_BROWN_WOOD_FLOOR_Geometry')

# Turned wood stair components follow the retained flight edges and landings.
wood='M_V24_31_Polished_Dark_Red_Stair_Wood';balusters=[];newels=[];handles=[];railmeta=[]
def lathe(x,y,z,profile,sides=24):
 vv=[]
 for h,r in profile:
  for k in range(sides):
   t=2*math.pi*k/sides;vv.append([x+r*math.cos(t),y+r*math.sin(t),z+h])
 ff=[]
 for j in range(len(profile)-1):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides;c=(j+1)*sides+(k+1)%sides;d=(j+1)*sides+k;ff.extend([[a,b,c],[a,c,d]])
 vv.extend([[x,y,z+profile[0][0]],[x,y,z+profile[-1][0]]]);bot=len(vv)-2;top=bot+1
 for k in range(sides):ff.append([bot,(k+1)%sides,k]);ff.append([top,(len(profile)-1)*sides+k,(len(profile)-1)*sides+(k+1)%sides])
 return solid(vv,ff,'lathe')
def baluster(x,y,z,top):
 h=top-z;assert h>.5
 prof=[(.17,.024),(.195,.033),(.22,.034),(.245,.024),(.28,.022),(.34,.029),(.39,.031),(.44,.026),(.49,.019),(.57,.020),(.62,.028),(.65,.034),(.68,.034),(.71,.024),(.76,.023)]
 pp=[(q*h/.94,r) for q,r in prof];baseh=.18*h/.94;toph=.75*h/.94
 return union([cube([x-.0275,y-.0275,z],[x+.0275,y+.0275,z+baseh]),lathe(x,y,z,pp,20),cube([x-.0275,y-.0275,z+toph],[x+.0275,y+.0275,top-.008])])
def newel(x,y,z):
 prof=[(.105,.075),(.145,.075),(.18,.058),(.24,.048),(.30,.057),(.34,.068),(.38,.066),(.425,.052),(.68,.050),(.72,.065),(.75,.071),(.79,.059),(.86,.052),(.93,.052),(.96,.075),(1.01,.075),(1.035,.040)]
 return union([cube([x-.075,y-.075,z-.008],[x+.075,y+.075,z+.12]),lathe(x,y,z,prof),mf.Manifold.sphere(.074,24).translate([x,y,z+1.10])])
def handpath(points):
 # One swept tube with shared rings, avoiding lumpy cylinder/ball unions.
 points=np.asarray(points,float);vv=[];ff=[];sides=32
 for i,p in enumerate(points):
  tangent=points[min(i+1,len(points)-1)]-points[max(i-1,0)];tangent/=np.linalg.norm(tangent);ex=np.cross(tangent,[0.,0.,1.]);ex/=np.linalg.norm(ex);ey=np.cross(tangent,ex)
  for k in range(sides):
   t=2*math.pi*k/sides;vv.append(p+.039*(ex*math.cos(t)+ey*math.sin(t)))
 for j in range(len(points)-1):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides;c=(j+1)*sides+(k+1)%sides;d=(j+1)*sides+k;ff.extend([[a,b,c],[a,c,d]])
 vv.extend([points[0],points[-1]]);a=len(vv)-2;b=a+1
 for k in range(sides):ff.append([a,(k+1)%sides,k]);ff.append([b,(len(points)-1)*sides+k,(len(points)-1)*sides+(k+1)%sides])
 return solid(vv,ff,'swept handrail')
for fl,basez,land,upper in [(1,-.45,1.499951124,3.450024414),(2,3.450024414,5.249951363,7.05)]:
 for k,ya,xb,xe,zb,ze in [(1,8.585,7.8,5.2,basez,land),(2,8.515,5.2,7.8,land,upper)]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';t=height_data(n);tops=np.unique(np.round(t[:,0,2],5));count=0
  # Twelve evenly spaced turned spindles, each seated on its actual tread.
  for xx in np.linspace(5.32,7.68,12):
   yy=9.0 if k==1 else 8.0;z=height(t,float(xx),yy)
   if z is None:continue
   u=(xx-xb)/(xe-xb);top=zb+(ze-zb)*u+.94
   balusters.append(baluster(float(xx),ya,z-.008,top));count+=1
  pts=[]
  for u in np.linspace(0,1,25):
   x=xb+(xe-xb)*u;z=zb+(ze-zb)*u+.94
   # Slight sweep to the lower/newel end as seen in the real handrail.
   if k==1:z+=.035*(1-smooth(u/.15))
   if k==2:z+=.035*smooth((u-.85)/.15)
   pts.append([x,ya,z])
  handles.append(handpath(pts));railmeta.append({'floor':fl,'flight':k,'spindles':count,'line_endpoints':[pts[0],pts[-1]]})
 newels.append(newel(5.13,8.55,land));newels.append(newel(5.13,7.465,land))
 handles.append(handpath([[4.10,7.465,land+.94],[5.13,7.465,land+.94]]))
 for xx in np.arange(4.25,5.04,.145):balusters.append(baluster(float(xx),7.465,land-.008,land+.94))
for z in [-.45,3.450024414,7.05]:newels.append(newel(7.8,8.55,z))
# Third floor well edge protection retains its previous span and clear route.
handles.append(handpath([[4.10,7.3325,7.05+.94],[7.8,7.3325,7.05+.94]]));newels.append(newel(7.8,7.3325,7.05))
for xx in np.arange(4.25,7.70,.145):balusters.append(baluster(float(xx),7.3325,7.042,7.99))
for label,ms in [('Turned_Balusters',balusters),('Ball_Finial_Newels',newels),('Rounded_Handrails',handles)]:put('V24_31_Stair_'+label,mf.Manifold.compose(ms),[wood],info={'smooth_wood':True})
OUT['remove'] += [n for n in INDEX if n.startswith('STAIR_V4_')]+['STAIR_V14_F3_HALL_OPEN_EDGE_GUARD_Geometry']
OUT['proof']['stair_railing']={'photos':['003716','003738'],'turned_balusters':len(balusters),'ball_finial_newels':len(newels),'handrail_segments':len(handles),'flight_lines':railmeta,'spindle_max_diameter_m':.068,'newel_base_width_m':.15,'newel_top_height_m':1.174,'handrail_diameter_m':.078,'approximation_from_photos_not_field_measurement':True,'stairs_and_landings_geometry_retained':True}
OUT['remove']=sorted(set(n for n in OUT['remove']if n in INDEX))
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False),encoding='utf8');print('V31_PREPARED',len(OUT['raw_objects']),len(OUT['remove']),flush=True)
