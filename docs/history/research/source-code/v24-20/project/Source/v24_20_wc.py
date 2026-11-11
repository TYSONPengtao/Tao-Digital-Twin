from v24_20_common import *
n='PARTITIONS_JOINED_F1_Geometry'
# The latest blue markup supersedes the former merged-room layout.
cut=union([cube([10.65,7.405,-.02],[10.96,9.825,3.79]),cube([9.005,8.345,-.02],[10.96,8.655,3.79])])
body=load(n)-cut;side=cube([9.0,7.395,0],[9.20,9.605,3.7700195]);oldhole=cube([11.89,7.20,0],[12.71,7.40,3.7700195]);newhole=cube([10.70,7.18,-.01],[11.50,7.42,2.099976])
sidehole=cube([8.98,8.60,-.01],[9.22,9.40,2.099976])
blue_partition=cube([10.60,7.395,0],[10.70,9.825,3.7700195])
put(n,union([body,side,oldhole,blue_partition])-newhole-sidehole,'M_Wall_Interior',transfer=True)
n='HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS_Geometry';put(n,load(n)-newhole,'M_Wall_Interior',transfer=True)
# DOOR_KITCHEN_F1 is the original stair-facing WC door; preserve all four
# original objects and their actions, despite their historical object names.
OUT['door_changes']=[{'objects':['DOOR_BATH_F1_R__FRAME','DOOR_BATH_F1_R__LEAF'],'translation':[-1.20,0,0]}]
OUT['proof']['f1_wc_space']={'latest_reference':'downa77d.png','layout':'Two zones divided along the user blue line; retain the original stair-facing WC door and the relocated right WC entry.','former_rear_compartment_and_wc_united':False,'blue_partition_bounds':[[10.60,7.395,0],[10.70,9.825,3.7700195]],'partition_thickness_m':.10,'partition_to_rear_facade':True,'old_cross_partition_removed_y':[8.345,8.655],'stair_facing_wall_x':[9.,9.2],'stair_facing_original_door_y':[8.6,9.4],'stair_facing_original_door_objects':'DOOR_KITCHEN_F1__*','stair_facing_original_door_retained':True,'stair_access_retained_x':[7.8,9.0],'entry_wall_y':[7.2,7.4],'old_entry_x':[11.9,12.7],'new_entry_x':[10.7,11.5],'door_location_basis':'User confirmed moving left along the same wall. The 1.20m distance is fitted to photo 230016 and existing room dimensions, not a new survey measurement.','old_right_entry_filled':True}
