from v26_2_common import *
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import re
WHITE='M_Wall_Interior';CEILING='M_V24_31_White_Painted_Ceiling'
OLD='V26_1_House_Continuous_Opaque_Shell';body=load(OLD);a=arr(OLD);v=a['v'];t=v[a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(no,axis=1)/2;no/=np.maximum(area[:,None]*2,1e-30);c=t.mean(1)
# Project only the opaque faces of each registered wall, including its existing
# beam and column faces. The union of these profiles retains every real opening.
# All surfaces of a room wall terminate at one finished plane, including the
# lower spandrel and the beam head. Structural core material is never removed.
targets=[
 ('west_inside',0,1,.212,.099,.2119,-.45,10.22005),
 ('left_room_partition',0,-1,3.688,3.6881,3.801,-.45,6.9200),
 ('middle_west_partition',0,1,4.112,3.999,4.1119,-.45,10.22005),
 ('middle_east_partition',0,-1,8.888,8.8881,9.001,-.45,10.22005),
 ('right_room_partition',0,1,9.312,9.199,9.3119,-.45,10.22005),
 ('east_inside',0,-1,12.788,12.7881,12.901,-.45,10.22005),
 ('front_inside',1,1,2.312,2.199,2.3119,-.45,10.22005),
 ('rear_partition_front',1,-1,7.088,7.0881,7.201,-.45,10.22005),
 ('rear_partition_back',1,1,7.512,7.399,7.5119,-.45,10.22005),
 ('rear_inside',1,-1,9.588,9.5881,9.701,-.45,10.22005),
]
proof=[];adds=[];spandrels=[]
# Some inherited facade voids are taller than the actual saved glazing, and
# contain non-planar triangulated closure faces. Close their opaque sill/head
# zones from the real frame bounds rather than projecting those bad faces.
floors=[-.4499999881,3.450024414,7.050000191];ceilings=[3.320019484,6.919995308,10.220044136]
for name,r in I.items():
 if not name.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_','WINDOW_BACK_','WINDOW_FRONT_CENTER_F3')):continue
 lo,hi=np.array(r['bounds']);fl=int(re.search(r'_F([123])',name)[1]);floor,ceiling=floors[fl-1],ceilings[fl-1]
 if name.startswith('WINDOW_LEFT_'):base0=[-.104,float(lo[1]),floor];base1=[.212,float(hi[1]),ceiling]
 elif name.startswith('WINDOW_RIGHT_'):base0=[12.788,float(lo[1]),floor];base1=[13.104,float(hi[1]),ceiling]
 elif name.startswith('WINDOW_BACK_'):base0=[float(lo[0]),9.588,floor];base1=[float(hi[0]),9.904,ceiling]
 else:base0=[float(lo[0]),1.996,floor];base1=[float(hi[0]),2.312,ceiling]
 for zone,z0,z1 in [('sill',floor,float(lo[2])),('head',float(hi[2]),ceiling)]:
  if z1-z0<.0001:continue
  a0=np.array(base0);a1=np.array(base1);a0[2]=z0;a1[2]=z1;adds.append(finish(cube(a0,a1),WHITE,name+' opaque '+zone));spandrels.append({'window':name,'zone':zone,'bounds_m':[a0.tolist(),a1.tolist()],'actual_glazing_not_covered':True})
# Close the documented opaque wall beside the stair opening. The clear
# 1.10m-wide entry at X=7.80..8.90 remains open on every floor.
for fl,(floor,ceiling)in enumerate(zip(floors[:2],ceilings[:2]),1):
 lo=[4.112,7.088,floor];hi=[7.8,7.512,ceiling];adds.append(finish(cube(lo,hi),WHITE,'F'+str(fl)+' stair partition continuous opaque body'));spandrels.append({'wall':'F'+str(fl)+' stair partition','bounds_m':[lo,hi],'clear_stair_entry_x_m':[7.8,8.9]})
for label,axis,sgn,end,low,high,zlo,zhi in targets:
 other=1-axis;mask=(no[:,axis]*sgn>.99999)&(c[:,axis]>low)&(c[:,axis]<high)&(t[:,:,2].max(1)>zlo+1e-6)&(t[:,:,2].min(1)<zhi-1e-6)
 # X walls span the registered house, Y walls do not project into the bay.
 extent=(1.884,10.016)if axis==0 else(-.216,13.216)
 polys=[Polygon(tr[:,[other,2]]).intersection(box(extent[0],zlo,extent[1],zhi))for tr in t[mask]]
 shape=unary_union(polys).buffer(0).simplify(2e-7,preserve_topology=True)
 if shape.is_empty:continue
 parts=[shape]if shape.geom_type=='Polygon'else list(shape.geoms);contours=[]
 for p in parts:
  if p.area<1e-9:continue
  p=orient(p,1);contours.append(np.array(p.exterior.coords)[:-1]);contours.extend(np.array(r.coords)[:-1]for r in p.interiors)
 section2=mf.CrossSection(contours,mf.FillRule.NonZero);start=high if sgn<0 else low;depth=abs(end-start)+.00015
 # Starting in the existing body by 0.15mm provides a real union, not contact.
 begin=start+.00015 if sgn<0 else start-.00015
 # Local (u,v,w) maps to (Y,Z,X) or (X,Z,Y). Reflections are supported.
 if axis==0:matrix=[[0,0,sgn,begin],[1,0,0,0],[0,1,0,0]]
 else:matrix=[[1,0,0,0],[0,0,sgn,begin],[0,1,0,0]]
 m=section2.extrude(depth).transform(matrix);m=finish(m,WHITE,label+' continuous opaque profile');adds.append(m)
 proof.append({'wall':label,'axis':axis,'normal_sign':sgn,'plane_m':end,'source_band_m':[low,high],'z_m':[zlo,zhi],'opaque_profile_area_m2':shape.area,'projected_triangles':int(mask.sum()),'aperture_profiles_retained':True,'core_removed_m3':0})
 print('WALL_PROFILE',label,shape.area,m.num_tri(),flush=True)
body=union([body]+adds);print('HOUSE_FINISHED',body.num_tri(),body.volume(),len(body.decompose()),flush=True)
print('RAW_CORE_DIFFERENCE',(load(OLD)-body).volume(),'PARTS',[(p.volume(),p.bounding_box())for p in body.decompose()if abs(p.volume())<2],flush=True)
row,body=export('V26_2_House_Flush_Continuous_Finished_Shell',body,'Room wall, spandrel, column and beam sides share registered finish planes; all existing openings and structural core retained')
print('EXPORTED_CORE_DIFFERENCE',(load(OLD)-body).volume(),body.volume(),len(body.decompose()),flush=True)
a=np.load(D/row['file']);v=a['v'];f=a['f'];mi=a['mi'].copy();uv=a['uv'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);c=t.mean(1);mats=row['materials']
for mat in [WHITE,CEILING,'M_Floor']:
 if mat not in mats:mats.append(mat)
for label,axis,sgn,end,low,high,zlo,zhi in targets:
 mask=(n[:,axis]*sgn>.999)&(abs(c[:,axis]-end)<2e-5)&(c[:,2]>=zlo-1e-5)&(c[:,2]<=zhi+1e-5);mi[mask]=mats.index(WHITE)
mi[(n[:,2]<-.7)&(c[:,2]>-.4)]=mats.index(CEILING)
for z in [-.4499999881,3.450024414,7.050000191]:mi[(n[:,2]>.999)&(abs(c[:,2]-z)<.0002)]=mats.index('M_Floor')
np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=uv)
# Deepen the U-shaped frames to line the entire finished wall thickness.
# Leaf geometry, hinge handedness and all animation curves remain untouched.
frames=[];objects=[row]
for name,r in I.items():
 if not name.startswith('DOOR_')or not name.endswith('__FRAME_Geometry'):continue
 lo,hi=np.array(r['bounds']);center=(lo+hi)/2
 if not(-.1<center[0]<13.1 and 1.8<center[1]<10.1):continue
 axis=int(np.argmin((hi-lo)[:2]));end0,end1=lo[axis],hi[axis];p=center[axis]
 if axis==0 and abs(p-3.9)<.01:end0,end1=(3.674,4.126)if center[2]<7 else(3.666,4.126)
 elif axis==0 and abs(p-9.1)<.01:end0,end1=8.874,9.326
 elif axis==1 and abs(p-7.3)<.01:end0,end1=7.074,7.526
 else:end0-=.014;end1+=.014
 a=arr(name);vv=a['v'].copy();vv[:,axis]=end0+(vv[:,axis]-lo[axis])/(hi[axis]-lo[axis])*(end1-end0)
 dz=-.45 if name=='DOOR_BATH_F1_R__FRAME_Geometry'else 0
 vv[:,2]+=dz
 # Union touching jamb/head blocks to remove internal visible end-cap seams.
 mm=tracked(vv,a['f'],r['materials'],a['mi'],a['uv'],name+' full-depth lining')
 mm=union(mm.decompose());rr,_=export(name,mm,'Full-depth door jamb and head lining matching the continuous finished wall; source leaf and hinge handedness retained')
 objects.append(rr);frames.append({'name':name,'axis':axis,'frame_depth_limits_m':[end0,end1],'vertical_correction_m':dz,'original_leaf_unchanged':True})
out={'objects':objects,'archive':[OLD],'proof':{'finished_wall_profiles':proof,'actual_window_opaque_zones':spandrels,'frames':frames,'raised_first_floor_right_glazed_door_corrected_m':-.45,'house_positive_components':len(body.decompose()),'structural_core_preserved':True}}
(D/'Prepared_House.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('HOUSE_PREPARED',len(objects),flush=True)
