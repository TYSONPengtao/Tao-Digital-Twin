from v24_24_common import *

# Close only the opening marked 150017, behind the exposed north timber post.
# The top follows the underside of the existing raking porch beam.
def top(x):return 2.57+(x-8.28)*(3.035-2.57)/(9.60-8.28)-.095+.012
poly=[(8.341,-.425),(9.61,-.425),(9.61,top(9.61)),(8.341,top(8.341))]
put('V24_24_Kitchen_North_Veranda_White_Closure',profile_y(poly,-3.035,-2.855),'M_V24_11_Plain_White_Limewash',True)
OUT['proof']['kitchen_closure']={'reference':'150017','bounds_xy':[8.341,-3.035,9.61,-2.855],'thickness_m':.18,'floor_to_raking_beam':True,'post_axis_preserved':[8.341,-3.12],'white_face_behind_exposed_post':True}

# The white connector face is at Y=-11.73. Recess the brick front to it,
# leaving all material at Y>=-11.73 and the entire courtyard side untouched.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';old=load(n)
front_cut=cube([8.34,-12.25,-.8],[13.205,-11.73,6.])
wall=old-front_cut
put(n,wall,'M_V24_18_Continuous_Blue_Brick',transfer=True)
OUT['objects'][-1]['gate_front_finish']=True
for cap in ['V24_22_South_Verge','V24_22_South_Verge_Bead']:
 put(cap,load(cap).translate([0,.21,0]),INDEX[cap]['materials'][0],transfer=True)
# Close the exposed front roof notch seen in 150243. This fitted grey return
# is entirely in front of the retained white plane, so the rear is untouched.
def rz(x):return 3.29432559+(x-9.5)*.42259216
return_profile=[(8.34,3.08),(9.0875,3.08),(9.53,rz(9.53)-.010),(9.53,rz(9.53)+.030),(9.0875,3.12),(8.34,3.12)]
put('V24_24_Gate_Front_Closed_Roof_Return',profile_y(return_profile,-12.13,-11.73001),'M_V24_20_Unified_Weathered_Gray_Clay',True)
OUT['proof']['gate_front']={'reference':['150243','150306'],'new_front_y':-11.73,'previous_front_y':-11.94,'recess_m':.21,'front_extent_x':[8.34,13.205],'removed_volume_m3':old.volume()-wall.volume(),'front_cornice_recess_m':.21,'gate_back_region_y_min':-11.73,'back_geometry_symmetric_difference_m3':abs(((old^cube([0,-11.73,-2],[25,5,10]))-(wall^cube([0,-11.73,-2],[25,5,10]))).volume()),'gate_piers_roof_and_actions_unmodified':True}
OUT['proof']['gate_front']['roof_notch_closed_only_at_y']=[-12.13,-11.73001]

# Extend the adjacent running-bond stone pattern across the unpaved band.
# Fit a 2mm surface finish to the original triangular grades. The original
# imported terrain, which has non-manifold internal seams, stays untouched.
outline=[(.125,-3.60),(13.10,-3.60),(13.10,1.90),(.125,1.90)]
zone=section(outline,3).translate([0,0,-2.])
skins=[];samples=[]
for n in ['SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_V12_REBUILT_COURT_0_0_0_Geometry']:
 a=source(n);tris=a['v'][a['f']];count=0
 for t in tris:
  no=np.cross(t[1]-t[0],t[2]-t[0])
  if no[2]<1e-10 or t[:,1].max()<-3.60 or t[:,1].min()>1.90 or t[:,0].max()<.125 or t[:,0].min()>13.10:continue
  lo=t.copy();lo[:,2]-=.010;hi=t.copy();hi[:,2]+=.002
  f=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
  skins.append(solid(np.vstack([lo,hi]),f));count+=1
 samples.append({'name':n,'upward_source_triangles':count})
finish=union(skins)^zone;tiles=[];boxes=[]
for iy in range(11,21):
 y=-10.9+iy*.62;offset=.4-(.56 if iy%2 else 0)
 for ix in range(-1,14):
  x=offset+ix*1.12;b=cube([x+.003,y+.003,-1.5],[x+1.117,y+.617,.4]);tile=finish^b
  if tile.volume()>1e-10:boxes.append(b);tiles.append(tile)
grout=(finish-union(boxes)).translate([0,0,-.0015])^finish
new=union([grout]+tiles)
put('V24_24_House_Front_Matching_Stone_Paving',new,'M_V22_Courtyard_Filled_Joint',True);OUT['objects'][-1]['paving_finish']=True
OUT['proof']['paving']={'reference':'150819 yellow outline and arrow from adjacent stone paving','outline_xy':outline,'matches_existing_materials':'M_V22_Courtyard_Stone_0..3 and Filled_Joint','module_m':[1.12,.62],'joint_m':.006,'alternate_row_offset_m':.56,'grid_origin':[.4,-10.9],'existing_grade_followed':True,'finish_above_source_m':.002,'joint_recess_m':.0015,'tiles':len(tiles),'source_floors_unchanged':samples}
OUT['proof']['preserved']=['all inner gate back geometry','carved gate piers and roof','existing north timber post','storage repairs from V24.23','all door/window actions','roof tiles valley and ears','1.65m human roam and stairs','perimeter wall frieze']
write();print('V24_24_GEOMETRY_READY',len(OUT['objects']),flush=True)
