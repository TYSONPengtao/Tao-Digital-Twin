from v24_23_common import *
BRICK='M_V24_18_Continuous_Blue_Brick';WOOD='M_V12_Kitchen_HONEY_WOOD'
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';old=load(n);m=old
# Recess the north-end wall behind the veranda, keeping the roof and its verge.
north_clear=cube([7,-3.57,-.7],[9.43,-2.54,3.085])
m=m-north_clear
put('V24_03_Kitchen_Rear_Stone_Plinth',load('V24_03_Kitchen_Rear_Stone_Plinth')-cube([7,-3.57,-1],[9.43,-2.54,1]),'M_Stone_Frame',transfer=True)
OUT['remove'].append('V24_22_North_Curved_Gable_Return')
# The new end post is at the red line, on the established outer beam axis.
x,y=8.341,-3.12
put('V24_23_Kitchen_North_End_Stone_Base',cube([x-.17,y-.17,-.405],[x+.17,y+.17,-.05]),'M_V22_Kitchen_Chiselled_Gray_Stone',True)
put('V24_23_Kitchen_North_End_Round_Post',rod([x,y,-.055],[x,y,2.46],.122,40),WOOD,True)
put('V24_23_Kitchen_North_End_Abacus',cube([x-.155,y-.18,2.36],[x+.155,y+.18,2.445]),WOOD,True)
brace=[(0,2.35),(.44,2.35),(.44,2.27),(.31,2.20),(.16,2.06),(0,2.06)]
put('V24_23_Kitchen_North_End_Brace',vertical_profile(brace,[x,y],[x,y-.44],.10),WOOD,True)
OUT['proof']['kitchen_end']={'post_axis_xy':[x,y],'post_radius_m':.122,'base_z':[-.405,-.05],'wall_recess_x':9.43,'outer_beam_axis_x':8.341,'reference':'123051 red post and yellow setback','photo_fitted':True}

# Keep masonry and grey cornice out of the whole carved gate pier, including
# its bevel and waist carving; connect the wall behind the pier instead.
gate_clear=cube([6.9,-12.10,-.8],[8.34,-11.20,4.0])
gate_back=cube([8.30,-12.10,-.8],[8.62,-11.73,3.40])
m=m-gate_clear-gate_back
for name in ['V24_22_South_Curved_Gable_Return','V24_22_South_Verge','V24_22_South_Verge_Bead','V24_Kitchen_Curved_Gable_Coping']:
 q=load(name)-gate_clear-gate_back
 if name=='V24_Kitchen_Curved_Gable_Coping':q=q-cube([12.25,-12.10,2.9],[13.60,-11.48,4.5])
 if q.volume()<1e-10:OUT['remove'].append(name)
 else:put(name,q,INDEX[name]['materials'][0],transfer=True)
OUT['proof']['gate_clearance']={'gate_pier_max_x':8.291,'masonry_min_x_at_pier':8.34,'wall_front_behind_pier_y':-11.73,'reference':'123121 and 00004 inner gate ideal model','gate_pier_meshes_unmodified':True}

# Storage west gable and the wall beneath used different face planes. Join
# them into one mass, extending the lower wall to the existing upper face.
west='V24_14_Storage_West_Sealed_Gable';g=load(west)
wall_fill=cube([13.205,-15.24,-.55],[13.535,-11.62,2.46])
m=union([m,g,wall_fill])
# Return the gable to the existing front wall/post station. The outer roof
# overhang is finished in wood, instead of an unsupported low brick apron.
porch_trim=cube([13.10,-16.14,2.3],[13.56,-15.24,5.1]);m=m-porch_trim
cap='V24_14_Storage_West_Gable_Stone_Coping'
put(cap,load(cap)-cube([13.1,-16.14,2.3],[13.56,-15.24,5.1]),INDEX[cap]['materials'][0],transfer=True)
rz=lambda yy:4.35+((4.35-3.03)/4.33)*(yy+12.15)
board=[(-16.48,rz(-16.48)-.07),(-15.20,rz(-15.20)-.07),(-15.20,rz(-15.20)-.22),(-16.48,rz(-16.48)-.22)]
put('V24_23_Storage_Outer_Gable_Wood_Edge',section(board,.16).transform(np.array([[0,0,1,13.40],[1,0,0,0],[0,1,0,0]],float)),'M_V24_15_Traditional_Storage_Wood',True)
OUT['remove'].append(west)
# Close the kitchen/storage triangular junction to the existing upper-envelope
# roof underside. Neither roof pitch nor the accepted tile valley is moved.
plan=m.slice(1.).extrude(5)
kc=np.array([-.487509082361,.003126681698,10.020600366289]);sc=np.array([0.,-.4243148162,4.35-.022-.4243148162*12.15])
def under_plane(co):
 q=cube([12.25,-12.05,0],[13.60,-11.48,1]);d=q.to_mesh64();v=np.array(d.vert_properties[:,:3]);f=np.array(d.tri_verts)
 for p in v:p[2]=2.1+p[2]*(co@np.r_[p[:2],1]-.066-2.1)
 return solid(v,f)
roof_under=union([under_plane(kc),under_plane(sc)])
seal=plan^roof_under
m=union([m,seal])
m=m-cube([12.25,-12.10,-.55],[13.205,-11.94001,4.6])
m=compose([c for c in m.decompose()if abs(c.volume())>1e-8])
put(n,m,BRICK,transfer=True);OUT['objects'][-1]['transfer_sources']=[n,west];OUT['objects'][-1]['wall_finish']=True
OUT['proof']['storage_walls']={'joined_shared_west_gable':True,'single_exterior_west_plane_x':13.205,'lower_wall_fill_y':[-15.24,-11.62],'unsupported_brick_apron_trimmed_to_original_wall_end_y':-15.24,'wood_edge_finishes_roof_overhang':True,'roof_junction_infill_m3':seal.volume(),'kitchen_roof_plane':kc.tolist(),'storage_roof_plane':sc.tolist(),'unchanged_roof_pitches_and_tile_valley':True,'reference':'123155 upper triangle and horizontal gap'}

# Cap the exposed foot ledge and connect the alley floor to the two existing
# slabs; the foundation below remains intact.
base='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry';cut=cube([12.90,-15.24,-.57],[13.56,-11.60,.1])
put(base,load(base)-cut,INDEX[base]['materials'][0],transfer=True)
grades=json.loads((D/'Ground_Grade_Scene.json').read_text());patches=[]
for (ya,za,_),(yb,zb,_) in zip(grades[:-1],grades[1:]):
 q=cube([12.9,ya,-.57],[13.55,yb,-.4]);d=q.to_mesh64();v=np.array(d.vert_properties[:,:3]);f=np.array(d.tri_verts)
 for p in v:
  if p[2]>-.41:
   zg=za+(zb-za)*(p[1]-ya)/(yb-ya);t=min(1.,max(0.,(p[0]-12.90)/.40));p[2]=zg*(1-t)-.4*t
 patches.append(solid(v,f))
patch=union(patches)-load('SITE_V14_INNER_STORAGE_FLOOR_Geometry')-load('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry')
put('V24_23_Storage_Flush_Alley_Floor',patch,'M_V12_Court_Stone',True)
OUT['proof']['storage_floor']={'new_flush_floor_patch_bounds':[[12.9,-15.24,-.57],[13.55,-11.60,-.4]],'outer_grade_samples':grades,'foundation_toe_trim_top':-.57,'reference':'123155 floor circle','foundation_below_floor_retained':True,'continuous_ramp_to_original_court_grade':True,'original_storage_floor_preserved':True}
OUT['proof']['preserved']=['26 doors and window actions','gate carved columns and handles','all roof tile fields and ears','1.65m avatar and stair roaming','outer perimeter decorations']
write();print('V23_GEOMETRY_READY',len(OUT['objects']),len(OUT['remove']),flush=True)
