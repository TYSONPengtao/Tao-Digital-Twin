from v24_16_common import *
from v24_13_geometry import roof_z
# Correct the entrance post forward, keeping two upright posts and the
# oblique plan relation to the railing. Door roots and fixed facade stay put.
posts=[(13.72,-15.22),(18.26,-15.60)]
n='V24_11_Storage_Veranda_Column_1';put(n,load(n).translate([0,-.57,0]),axis='Z')
n='V24_11_Storage_Veranda_Column_Base_1';put(n,load(n).translate([0,-.57,0]),'M_Stone',axis='Z')
# A solid west return, with the interior white bay carried from the post
# behind to the recessed front. It sits on the existing floor/foundation.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';m=load(n);ret=cube([13.295,-15.24,-.408],[13.535,-14.18,2.83]);put(n,m+ret,INDEX[n]['materials'][0],transfer=True)
put('V24_16_Storage_Entrance_White_Wall_Return',cube([13.532,-15.24,-.397],[13.550,-14.12,2.835]),WHITE,True,axis='Y')
# The original side wall reaches beyond this return; the plaster joins its
# existing inner finish and the sealed upper gable without a gap.
a=np.array(posts[0]);b=np.array(posts[1]);L=float(np.linalg.norm(b-a));u=(b-a)/L;lat=np.array([-u[1],u[0]])
gallery=[];profile=[(0,2.905),(L,2.905)]+[(float(t),2.685+.035*math.sin(math.pi*t/L))for t in np.linspace(L,0,33)]
gallery.append(vertical_profile(profile,a,b,.17));gallery.append(beam([*a,2.42],[*b,2.42],.070,.075));gallery.append(beam([13.535,-16.48,2.91],[18.405,-16.48,2.91],.070,.12))
for x,y in posts:
 end=fy(x)+.07;ll=end+16.10;prof=[(0,2.827),(ll,2.827),(ll,2.657),(.05,2.657),(0,2.707)];gallery.append(vertical_profile(prof,[x,-16.10],[x,end],.14))
put('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails',union(gallery))
fret=[]
for j in range(11):
 t0=.17+j*(L-.34)/11;ww=(L-.34)/11;pts=[(t0,2.740),(t0,2.535),(t0+ww*.26,2.535),(t0+ww*.26,2.455),(t0+ww*.74,2.455),(t0+ww*.74,2.535),(t0+ww,2.535),(t0+ww,2.740)]
 for (t,z),(tt,zz)in zip(pts,pts[1:]):p=a+u*t;q=a+u*tt;fret.append(beam([*p,z],[*q,zz],.03,.03))
put('V24_15_Storage_Veranda_Open_Stepped_Fretwork',union(fret))
braces=[];carve=[]
for i,p in enumerate([a,b]):
 sign=1 if i==0 else-1;q=p+u*sign*.42;profile=[(0,2.715),(.42,2.715),(.40,2.625),(.33,2.60),(.27,2.55),(.20,2.46),(.12,2.36),(0,2.36)];braces.append(vertical_profile(profile,p,q,.10))
 for sg in [-1,1]:
  cen=p+u*sign*.18+lat*sg*.052;pts=[]
  for j in range(40):
   t=j/39;r=.057*(1-.62*t);ang=-.4+math.tau*1.1*t;dd=u*sign*r*math.cos(ang);pts.append([cen[0]+dd[0],cen[1]+dd[1],2.54+r*math.sin(ang)])
  for aa,bb in zip(pts,pts[1:]):carve.append(rod(aa,bb,.004,8))
put('V24_15_Storage_Veranda_Queti_Brackets',union(braces));put('V24_15_Storage_Queti_Carved_Scroll_Lines',union(carve))
OUT['proof']['entrance']={'old_column_xy':[13.72,-14.65],'new_column_xy':posts[0],'outward_shift_m':.57,'two_column_axes':posts,'plan_angle_degrees':math.degrees(math.atan2(u[1],u[0])),'white_return_x':[13.532,13.550],'white_return_y':[-15.24,-14.12],'visible_white_bay_depth_m':fy(13.72)-(-15.22+.106),'door_and_glazing_plane_unchanged':True,'tie_top_z':2.905,'fit_basis':'135637 / 135703 / 135741 / 123950 photographs; approximate fitted geometry'}
from v24_16_screen import prepare_screen
prepare_screen()
OUT['proof']['scope']={'all_26_door_animations_preserved':True,'storage_roof_and_curved_rear_wall_preserved':True,'kitchen_and_outer_canopy_preserved':True,'secondary_screenwall_preserved':True,'bearing_checks_are_geometric_not_structural_calculations':True}
write()
