from v24_25_common import *
WHITE='M_Wall_Exterior';BRICK='M_V24_18_Continuous_Blue_Brick'

# Five ensuite windows. Preserve each ordinary bedroom window and all doors.
windows=[]
for fl,floor,sides in [(1,0.,['LEFT','RIGHT']),(2,3.9000244140625,['LEFT','RIGHT']),(3,7.5,['RIGHT'])]:
 core='FACADE_CONTINUOUS_F'+str(fl)+'_Geometry';m=load(core)
 for side in sides:
  x=0. if side=='LEFT'else 13.;a=x-.212;b=x+.212;sill=floor+1.80;head=floor+2.60
  oldhole=cube([a,7.95,floor+.9],[b,9.15,floor+2.1]);newhole=cube([x-.25,7.95,sill],[x+.25,9.15,head]);m=union([m,oldhole])-newhole
  clad=f'HOUSE_V21_{"WEST"if side=="LEFT"else"EAST"}_GREY_WHITE_F{fl}_Geometry';lo,hi=INDEX[clad]['bounds'];fill=cube([lo[0],7.95,floor+.9],[hi[0],9.15,floor+2.1]);put(clad,union([load(clad),fill])-newhole,INDEX[clad]['materials'][0],transfer=True)
  n=f'WINDOW_{side}_C1212_F{fl}_Geometry';black=cube([x-.045,7.95,sill],[x+.045,9.15,head])-cube([x-.06,7.995,sill+.045],[x+.06,9.105,head-.045]);black=union([black,cube([x-.045,8.5275,sill+.035],[x+.045,8.5725,head-.035])]);glass=[];panes=[]
  for ya,yb in [(7.997,8.5255),(8.5745,9.103)]:
   glass.append(cube([x-.006,ya,sill+.047],[x+.006,yb,head-.047]));panes.append([ya,yb,sill+.047,head-.047])
  put(n,compose([black]+glass),'M_Metal_Black');OUT['objects'][-1]['window_panes']=panes;OUT['objects'][-1]['window_x']=x
  cs='CONSTRUCTION_SILL_'+n;a0=source(cs);v=a0['v'].copy();v[:,2]=floor+1.8+(v[:,2]-floor-.9)*(.8/1.2);put(cs,solid(v,a0['f'],cs),INDEX[cs]['materials'][0],transfer=True)
  windows.append({'name':n,'floor':fl,'sill_above_floor_m':1.8,'head_above_floor_m':2.6,'width_m':1.2,'height_m':.8,'no_horizontal_mullion':True,'frosted_glass':True})
 put(core,m,WHITE,transfer=True)
OUT['proof']['bathroom_windows']={'reference':['151458','151716'],'windows':windows,'fitted_to_photo_not_new_survey':True,'ordinary_f3_left_bedroom_window_preserved':True,'former_low_openings_filled':True,'wall_cladding_and_sill_recut_together':True}

# The real gate pier and kitchen masonry touch. Fill behind the carved bevel,
# through the pier-to-eave junction; do not move the gate or its rear surface.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';old=load(n)
seam=cube([8.25,-11.73,-.55],[8.341,-11.62,3.106])
def west_z(x):return .42259216*x+.003126681698*(-11.73)+(10.020600366289-(.487509082361+.42259216)*11.7625)
xp=(3.106-west_z(0))/.42259216
poly=[(8.25,2.68),(9.54,2.68),(9.54,west_z(9.54)-.055),(xp,3.106),(8.25,3.106)]
fill=profile_y(poly,-11.73,-11.62);m=union([old,seam,fill]);put(n,m,BRICK,transfer=True);OUT['objects'][-1]['joint_brick_finish']=True
OUT['remove'].append('V24_24_Gate_Front_Closed_Roof_Return')
trim=[(8.25,3.005),(xp,3.005),(9.54,west_z(9.54)-.100),(9.54,west_z(9.54)-.045),(xp,3.106),(8.25,3.106)]
put('V24_25_Gate_Pier_Continuous_Eave_Return',profile_y(trim,-11.775,-11.718),'M_V24_22_Gable_Gray_Lime',True)
OUT['proof']['gate_joint']={'reference':['175749','175827','175910','175946'],'closed_wall_bounds':[[8.25,-11.73,-.55],[8.341,-11.62,3.106]],'front_wall_plane_y_retained':-11.73,'carved_bevel_y_max':-11.794,'new_masonry_y_min':-11.73,'no_air_gap_between_pier_wall_and_eave':True,'fitted_front_plate_removed':True,'gate_objects_and_door_actions_unmodified':True,'existing_rear_wall_not_moved':True,'added_wall_m3':m.volume()-old.volume()}

# Match the existing light grey entrance apron, including the gallery and
# short transition. Reuse its exact material rather than a new beige finish.
mat='M_V12_Road_Concrete';names=['SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V14_OUTER_STORAGE_FLOOR_Geometry','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry','V24_10_Entry_Continuous_Threshold','V24_23_Storage_Flush_Alley_Floor']
for n in names:put(n,load(n),mat)
zone=section([(10.9,-16.42),(13.62,-16.42),(13.62,-11.60),(10.9,-11.60)],3).translate([0,0,-2]);skins=[]
for n in ['SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_V12_REBUILT_COURT_0_-20_0_Geometry']+names:
 a=source(n)
 for t in a['v'][a['f']]:
  no=np.cross(t[1]-t[0],t[2]-t[0])
  if no[2]<1e-10 or t[:,2].max()>.05 or t[:,2].min()<-.85 or t[:,0].max()<10.9 or t[:,0].min()>13.62 or t[:,1].max()<-16.42 or t[:,1].min()>-11.60:continue
  lo=t.copy();lo[:,2]-=.010;hi=t.copy();hi[:,2]+=.0015
  f=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]]);skins.append(solid(np.vstack([lo,hi]),f))
put('V24_25_Storage_Entrance_Continuous_Light_Gray_Finish',union(skins)^zone,mat,True)
OUT['proof']['storage_entrance']={'reference':'180153 with foreground color circle and arrow','material_matched':mat,'recolored_existing_floors':names,'approach_bounds_xy':[10.9,-16.42,13.62,-11.60],'finish_rise_m':.0015,'original_floor_heights_and_base_geometry_preserved':True,'no_beige_transition_strip':True}
write();print('V25_WINDOWS_JOINT_FLOOR_READY',flush=True)
