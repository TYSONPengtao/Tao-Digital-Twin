"""Native court, buildable pad and anchored perimeter corrections."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union,triangulate,linemerge
from shapely.geometry.polygon import orient
from v24_16_common import solid,cube,union,section
D=W/'v24_30';INDEX={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
EXTRA={r['name']:r for r in json.loads((D/'Extra_Index.json').read_text('utf8'))}
OUT={'raw_objects':[],'remove':[],'proof':{},'offsets':[]};LOW=-.60;HIGH=-.45
def source(n):return np.load(D/(INDEX if n in INDEX else EXTRA)[n]['file'])
def polys(shape):return [shape]if shape.geom_type=='Polygon'else [p for p in shape.geoms if p.geom_type=='Polygon'and p.area>1e-9]
def prism(shape,z0,z1):
 ms=[]
 for p in polys(shape):
  m=section(list(p.exterior.coords)[:-1],z1-z0).translate([0,0,z0])
  for h in p.interiors:m-=section(list(h.coords)[:-1],z1-z0+.02).translate([0,0,z0-.01])
  if m.volume()>1e-9:ms.append(m)
 return union(ms)
def mesh(m):
 a=m.to_mesh64();return np.array(a.vert_properties[:,:3]),np.array(a.tri_verts)
def put(n,m,materials,mi=None,extra=None):
 v,f=mesh(m)if not isinstance(m,tuple)else m
 fn=n+'.npz';uv=v[f][:,:,:2].copy()
 if mi is None:mi=np.zeros(len(f),int)
 np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 row={'name':n,'file':fn,'materials':materials,'vertices':len(v),'triangles':len(f)}
 if extra:row.update(extra)
 OUT['raw_objects'].append(row);print('PREPARED',n,len(v),len(f),flush=True)
def footprint(n):
 a=source(n);t=a['v'][a['f']];ns=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[abs(ns[:,2])>1e-9]
 return unary_union([Polygon(np.round(p[:,:2],7))for p in t]).buffer(0)
soilshape=footprint('SITE_V16_GRADED_INTERIOR_SOIL_Geometry')
house=footprint('SLAB_JOINED_F1_Geometry').union(footprint('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry'))
kitchen=footprint('SITE_KITCHEN_STONE_FLOOR_Geometry')
road=footprint('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry').buffer(.00001).buffer(-.00001)
road=max(polys(road),key=lambda p:p.area)
whole=unary_union([soilshape,house,kitchen,road]+[footprint(n)for n in INDEX if n.startswith('SITE_V12_REBUILT_COURT_')]).buffer(.002).buffer(-.002)
site=Polygon(max(polys(whole),key=lambda p:p.area).exterior)
print('SITE_OUTLINE',site.area,site.bounds,flush=True)
# Replace the accidental stair-shaped soil/road boundary with the user's
# smooth blue-line boundary, from the outer gate to the level inner landing.
A=np.array([-14.80,-8.42]);B=np.array([-2.866426,-11.40]);C=np.array([-12.70,-9.70]);E=np.array([-7.00,-10.52])
def bezier(c):return np.array([((1-t)**3*A+3*(1-t)**2*t*c+3*(1-t)*t*t*E+t**3*B).tolist()for t in np.linspace(0,1,129)])
oldcurve=bezier(C).tolist()+[[-.212,-11.4]]
oldnorth=Polygon(oldcurve+[[-.212,14.],[-30.,14.],[-30.,-8.42]])
oldpad=site.intersection(box(-30,-20,-.212,14)).intersection(oldnorth)
# Leave the full bifold gate sweep on the graded road side of the curb.
# The rest of the editable yard remains exactly level and white.
gv=np.load(D/'Gate_Sweep.npz')['v'];gv=gv[(gv[:,0]>=A[0])&(gv[:,0]<=B[0])]
for yy in np.arange(-8.,-2.,.1):
 C=np.array([-13.60,float(yy)]);q=bezier(C);margin=np.interp(gv[:,0],q[:,0],q[:,1])-gv[:,1]
 if margin.min()>.065:break
assert margin.min()>.065
curve=q.tolist()+[[-.212,-11.4]];curbline=LineString(curve)
north_of_road=Polygon(curve+[[-.212,14.],[-30.,14.],[-30.,-8.42]])
pad=site.intersection(box(-30,-20,-.212,14)).intersection(north_of_road).buffer(0)
pad=max(polys(pad),key=lambda p:p.area)
apron=oldpad.difference(pad).buffer(0)
return_points=[p for p in pad.exterior.coords if abs(p[1]+8.42)<1e-5 and p[0]<A[0]-.001]
if return_points:curve=[min(return_points,key=lambda p:p[0])]+curve;curbline=LineString(curve)
# Existing outer yard is one horizontal editable solid, bounded by the road.
put('V24_30_Outer_Yard_White_Building_Pad',prism(pad,-4.8,LOW),['M_V24_30_White_Building_Pad'])
low=box(.020,-11.4,8.15,1.9).difference(house.buffer(.0002)).difference(kitchen.buffer(.0002)).intersection(site)
high=box(8.15,-3.12,16.,12.5).union(box(-.012,10.0,16.,12.5)).intersection(site).difference(house.buffer(.0002)).difference(kitchen.buffer(.0002))
# Follow the native inner wall, not the previous straight wedge cladding.
wall=footprint('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry')
high=high.difference(wall.buffer(.017))
for label,shape,z in [('Low_Main_Court',low,LOW),('High_North_Lane_And_Rear',high,HIGH)]:
 put('V24_30_'+label+'_Joint_Base',prism(shape,z-.25,z-.0015),['M_V22_Courtyard_Filled_Joint'])
 vv=[];ff=[];mm=[];count=0
 for iy in range(-3,39):
  y=-10.9+iy*.62;offset=.4-(.56 if iy%2 else 0)
  for ix in range(-2,17):
   x=offset+ix*1.12;p=shape.intersection(box(x+.003,y+.003,x+1.117,y+.617))
   if p.is_empty or p.area<1e-8:continue
   v,f=mesh(prism(p,z-.03,z));k=len(vv);vv.extend(v);ff.extend(f+k);mm.extend([((ix*7+iy*3)%4)]*len(f));count+=1
 put('V24_30_'+label+'_Running_Bond_Stone',(np.array(vv),np.array(ff)),['M_V22_Courtyard_Stone_'+str(i)for i in range(4)],np.array(mm),{'blocks':count})
 OUT['proof'][label]={'area_m2':shape.area,'finish_z_m':z,'blocks':count,'module_m':[1.12,.62],'joint_m':.006,'outline':shape.__geo_interface__}
# Raise the structural foundation of the rear internal lane to the same high datum.
rear=box(-.212,9.995,-.012,13.).intersection(site)
put('V24_30_Rear_Internal_External_Separation_Wall',prism(rear,LOW-.25,2.20),['M_V24_11_Plain_White_Limewash'])
put('V24_30_Rear_Separation_Wall_Stone_Cap',prism(rear.buffer(.035,join_style=2),2.20,2.27),['M_V22_Courtyard_Stone_2'])
put('V24_30_House_West_Pad_Foundation_Closure',cube([-.212,0.,-.70],[-.185,10.012,-.4499]),['M_Wall_Exterior'])
OUT['proof']['rear_separator']={'outer_face_x_m':-.212,'inner_face_x_m':-.012,'width_m':.20,'height_z_m':2.20,'internal_high_finish_m':HIGH,'outer_pad_finish_m':LOW,'outline':rear.__geo_interface__}

# Road retains its plan and original outside gate tie; its inner landing gently
# reaches the low courtyard. All original per-loop UVs/materials are retained.
n='SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry';a=source(n);v=a['v'].copy();t=np.clip((v[:,0]+12.)/13.,0,1);t=t*t*(3-2*t);v[:,2]-=.15*t
put(n,(v,a['f']),INDEX[n]['materials'],a['mi']);np.savez_compressed(D/(n+'.npz'),v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
OUT['proof']['road']={'endpoint_delta_m':-.15,'outer_gate_tie_retained_before_x_m':-12.,'plan_and_topology_unchanged':True,'transition':'smoothstep','original_mesh':INDEX[n]['file']}

# Curb follows the actual upper edge of the existing sloping approach. It
# retains the flat yard top while its exposed height fades with the road grade.
coords=np.array(curbline.coords)
if coords[0,0]>coords[-1,0]:coords=coords[::-1];curbline=LineString(coords)
def height_from_mesh(a,x,y):
 tri=a['v'][a['f']];p=tri[:,:,:2];A=p[:,1]-p[:,0];B=p[:,2]-p[:,0];Q=np.array([x,y])-p[:,0];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];safe=np.where(abs(det)>1e-9,det,1);u=(Q[:,0]*B[:,1]-Q[:,1]*B[:,0])/safe;w=(A[:,0]*Q[:,1]-A[:,1]*Q[:,0])/safe;ok=(abs(det)>1e-9)&(u>=-1e-5)&(w>=-1e-5)&(u+w<=1.00001)
 zz=tri[:,0,2]+u*(tri[:,1,2]-tri[:,0,2])+w*(tri[:,2,2]-tri[:,0,2]);return float(zz[ok].max())if ok.any()else None
roadnew=np.load(D/(n+'.npz'));outerramp=source('SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP_Geometry');body=[];caps=[];stations=[]
from shapely.ops import nearest_points
av,af=mesh(prism(apron,-4.8,0.))
for i,(x,y,z)in enumerate(av):
 h=height_from_mesh(roadnew,x,y)
 if h is None:h=height_from_mesh(outerramp,x,y)
 if h is None:
  rp=nearest_points(road,Point(x,y))[0];p=np.array(rp.coords[0]);u=np.array(road.centroid.coords[0])-p;u/=np.linalg.norm(u);h=height_from_mesh(roadnew,*(p+u*.02))
 if h is None:h=-.85
 av[i,2]=-4.8+(h+.002+4.8)*(z+4.8)/4.8
put('V24_30_Outer_Gate_Swing_Clearance_Graded_Apron',(av,af),['M_V12_Road_Concrete']);aprondata={'v':av,'f':af}
OUT['proof']['gate_apron']={'area_m2':apron.area,'minimum_horizontal_gate_sweep_clearance_m':float(margin.min()),'curve_control_y_m':float(C[1]),'gate_geometry_and_animation_unchanged':True,'road_material':'M_V12_Road_Concrete','outline':apron.__geo_interface__}
road_samples=np.vstack([roadnew['v'],outerramp['v']]);road_samples=road_samples[road_samples[:,2]>-1.45]
L=curbline.length
for s0 in np.arange(0,L,.75):
 s1=min(L,s0+.75);mid=(s0+s1)/2;p0=np.array(curbline.interpolate(s0).coords[0]);p1=np.array(curbline.interpolate(s1).coords[0]);u=(p1-p0)/np.linalg.norm(p1-p0);normal=np.array([-u[1],u[0]])
 pm=np.array(curbline.interpolate(mid).coords[0]);normal*=1 if pad.contains(Point(pm+normal*.05))else -1
 r0=height_from_mesh(roadnew,*(p0-normal*.025));r1=height_from_mesh(roadnew,*(p1-normal*.025))
 if r0 is None:r0=height_from_mesh(outerramp,*(p0-normal*.025))
 if r1 is None:r1=height_from_mesh(outerramp,*(p1-normal*.025))
 if r0 is None:r0=height_from_mesh(aprondata,*(p0-normal*.025))
 if r1 is None:r1=height_from_mesh(aprondata,*(p1-normal*.025))
 if r0 is None:r0=float(road_samples[np.linalg.norm(road_samples[:,:2]-p0,axis=1).argmin(),2])
 if r1 is None:r1=float(road_samples[np.linalg.norm(road_samples[:,:2]-p1,axis=1).argmin(),2])
 # Rounded top line stays flush with the pad; no barrier on the inner landing.
 top=LOW;cap_bottom=LOW-.065;bottom=min(r0,r1,cap_bottom)-.035
 footprint_=Polygon([p0-normal*.025,p1-normal*.025,p1+normal*.155,p0+normal*.155]).intersection(site.buffer(.04))
 if footprint_.area<1e-7:continue
 body.append(prism(footprint_,bottom,cap_bottom))
 cut=Polygon([p0+u*.002-normal*.027,p1-u*.002-normal*.027,p1-u*.002+normal*.157,p0+u*.002+normal*.157]).intersection(site.buffer(.04))
 caps.append(prism(cut,cap_bottom,top));stations.append({'s0':float(s0),'s1':float(s1),'xy':pm.tolist(),'road_z_m':(r0+r1)/2,'top_z_m':top,'exposed_height_m':max(0,top-(r0+r1)/2)})
assert body and caps,'No continuous road-side curb could be resolved'
put('V24_30_Graded_Approach_Curb_Retaining_Base',union(body),['M_V22_Courtyard_Stone_3'])
put('V24_30_Individual_Roadside_Curb_Stones',mf.Manifold.compose(caps),['M_V22_Courtyard_Stone_1'])
OUT['proof']['curb']={'route_xy':coords.tolist(),'length_m':L,'width_m':.18,'stone_module_m':.75,'stations':stations,'gate_end_high_then_fades':True,'pad_top_flat':True}

# Retire complete superseded court finish assemblies rather than leave
# coincident old triangles to bleed through the new stone finish.
names=[r['name']for r in json.loads((D/'Inventory.json').read_text('utf8'))]
OUT['remove']=[n for n in names if n.startswith(('SITE_V12_REBUILT_COURT_','V24_08_Exposed_Court_','V24_28_High_Approach_Stone_'))]
OUT['remove']+=['V24_24_House_Front_Matching_Stone_Paving','V24_08_Gate_Side_Exposed_Court_Strip','SITE_V16_COURT_EDGE_INFILL_STEP_Geometry','CONSTRUCTION_COURTYARD_DRAINAGE_FINISH_Geometry']
OUT['remove']=[n for n in OUT['remove']if n in names]
OUT['offsets']=[{'name':n,'offset':[0,0,-.15]}for n in names if n.startswith(('SITE_GAZEBO_','SITE_V22_PAVILION_'))and n.endswith('_Geometry')]
OUT['offsets']+=[{'name':n,'offset':[0,0,-.15]}for n in ['SITE_PLANTER_0_Geometry','SITE_PLANTER_2_Geometry']]
OUT['offsets'].append({'name':'CONSTRUCTION_RAINWATER_RECEIVER_WING_SW_Geometry','offset':[0,0,-.192]})
OUT['offsets'].append({'name':'CONSTRUCTION_RAINWATER_RECEIVER_NW_Geometry','offset':[0,0,-.192]})

# The old straight white core caused the visible wedge. Replace only that
# inward cladding; the complete native outside masonry remains byte-identical.
segs=json.loads((W/'v16/Drain_Segments.json').read_text());rs=[r for r in segs if r['ci']==0 and 45<=r['j']<=60]
centre=np.array([rs[0]['a']]+[r['b']for r in rs])[::-1];centre=centre[np.r_[True,np.linalg.norm(np.diff(centre,axis=0),axis=1)>1e-5]]
dirs=np.diff(centre,axis=0);dirs/=np.linalg.norm(dirs,axis=1)[:,None];normals=np.c_[dirs[:,1],-dirs[:,0]]
mitre=np.vstack([normals[0]]+[(normals[i-1]+normals[i])/(1+normals[i-1]@normals[i])for i in range(1,len(centre)-1)]+[normals[-1]])
def at_y(y):
 i=min(len(centre)-2,max(0,int(np.searchsorted(centre[:,1],y)-1)));q=np.clip((y-centre[i,1])/(centre[i+1,1]-centre[i,1]),0,1);p=centre[i]+q*(centre[i+1]-centre[i]);no=mitre[i]+q*(mitre[i+1]-mitre[i]);return p,no
Y0=-2.855;Y1=10.25;ys=sorted(set([Y0,Y1]+[float(p[1])for p in centre if Y0<p[1]<Y1]));inside=[];back=[]
for y in ys:
 p,no=at_y(y);inside.append(p-no*.176);back.append(p-no*.160)
facepoly=Polygon(inside+back[::-1]);put('V24_28_Continuous_White_Courtyard_Wall_Face',prism(facepoly,-.85,2.44720006),['M_V24_11_Plain_White_Limewash'])
# Reshape the retained native tile topology around the fixed outside wall
# reference; its former variable width is removed, while all Z levels stay.
n='SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry';wv=source(n)['v'];points=[]
for yy in np.unique(np.round(wv[(wv[:,0]>14.15)&(wv[:,1]>-1.94)&(wv[:,1]<10.3),1],5)):
 q=wv[(abs(wv[:,1]-yy)<1e-4)&(wv[:,0]>14.15)]
 if len(q):points.append((float(q[:,0].min()),float(yy)))
oldroute=np.array([(13.8188,-2.9254),(14.1694,-1.9877)]+sorted(points,key=lambda p:p[1]));n='V24_28_Level_White_Wall_Tile_Coping';a=source(n);v=a['v'].copy()
oldout=np.maximum(14.43,np.interp(v[:,1],oldroute[:,1],oldroute[:,0])+.33)+.075;fraction=(v[:,0]-14.025)/(oldout-14.025)
for i,y in enumerate(v[:,1]):
 p,no=at_y(float(y));v[i,:2]=p+no*(-.235+fraction[i]*.470)
put(n,(v,a['f']),INDEX[n]['materials'],a['mi']);np.savez_compressed(D/(n+'.npz'),v=v,f=a['f'],mi=a['mi'],uv=a['uv'])
OUT['proof']['wall']={'masonry_exterior_original_unchanged':True,'cause':'Straight inside core paired with curved outside trace created a wedge in plan.','native_core_nominal_thickness_m':.32,'inside_finish_thickness_m':.016,'tile_coping_nominal_width_m':.47,'normal_overhang_m':.075,'top_z_m':2.44720006,'outer_reference':'Original perimeter centreline + outward normal * 0.16m','stations':[{'y':float(y),'centre':at_y(y)[0].tolist(),'outward_mitre':at_y(y)[1].tolist()}for y in ys]}

# Store the exact replacement footprint for attribute-preserving terrain
# trimming. The new native solids fill every excavated portion.
trim=unary_union([pad,low,high,apron,rear]);OUT['trim_footprint']=trim.__geo_interface__
OUT['proof']['outer_pad']={'area_m2':pad.area,'finish_z_m':LOW,'white_flat_editable_solid':True,'outline':pad.__geo_interface__,'future_building_area':True}
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False),encoding='utf8')
print('V30_PREPARED',len(OUT['raw_objects']),'retired',len(OUT['remove']),'pad_area',pad.area,'low',low.area,'high',high.area,'curb',L,flush=True)
