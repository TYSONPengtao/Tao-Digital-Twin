"""Photo-fitted kitchen enclosure, supported timber and open outer fretwork.
Coordinates are metres. Existing roof, doors, tile valley and adjoining store remain.
"""
from v24_22_common import *
from shapely.geometry import box as rect, LineString
from shapely.ops import unary_union
WOOD='M_V12_Kitchen_HONEY_WOOD'
BRICK='M_V24_18_Continuous_Blue_Brick'
GRAY='M_V24_22_Gable_Gray_Lime'
main='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'
old=load(main)

def poly_at_y(m,y):
 return max((Polygon(p)for p in m.rotate([-90,0,0]).slice(-y).to_polygons()),key=lambda p:p.area).simplify(.000005)

def along_y(p,a,b):return profile_y(list(p.exterior.coords)[:-1],a,b)

# The former north wall's oblique internal leaf and south dogleg predate the
# present gables. Remove those leaves before making a single joined solid.
obsolete_n=Polygon([(9.10,-2.92),(13.97,-3.28),(13.86,-3.51),(9.10,-2.95)]).buffer(.006,join_style=2)
cut_n=cube([8.0,-3.56,-1],[14.11,-2.94,6])
cut_s=cube([8.,-12.01,-1],[13.20,-11.595,6])+cube([8.,-11.98,-1],[9.60,-10.70,6])
core=old-cut_n-cut_s
# Restore only the true east return, with a clean inner edge to the new end wall.
east_plan=Polygon([(13.848,-3.562),(14.206,-3.562),(14.26,-2.83),(13.971,-2.83),(13.959,-3.28)])
east_return=section(list(east_plan.exterior.coords)[:-1],5).translate([0,0,-.55])
roof_clip=profile_y([(12.5,-.6),(14.6,-.6),(14.6,4.18-.488*(14.6-11.7625)),(12.5,4.18-.488*(12.5-11.7625))],-3.57,-2.82)
core=union([core,east_return^roof_clip])
# At the kitchen/storage joint the old upper gable protruded 95mm beyond
# the lower wall. Continue the lower wall profile upward to remove that ledge.
joint_zone=cube([12.7,-11.62,2.15],[13.62,-8.88,4.45])
joint_roof=profile_y([(12.6,1.9),(13.7,1.9),(13.7,4.18-.488*(13.7-11.7625)),(12.6,4.18-.488*(12.6-11.7625))],-11.63,-8.87)
joint_zone=joint_zone^joint_roof
wall_column=old.slice(1.).extrude(5).translate([0,0,-.55])
core=union([core,wall_column^joint_zone])
shared_name='V24_14_Storage_West_Sealed_Gable'
put(shared_name,load(shared_name)-joint_zone,INDEX[shared_name]['materials'][0],False,transfer=True)

# A curved masonry return reaches from the brick jamb to the projecting eave.
arc=[(7.47+.68*math.cos(t),1.65+.58*math.sin(t))for t in np.linspace(0,math.pi/2,33)]
return_poly=Polygon(arc+[(7.43,2.425),(8.35,2.785),(8.35,1.65)])
gables=[]
for tag,n,y,a,b in [('South','V24_Kitchen_Gable_Upper_Brick_Infill',-11.8,-11.94,-11.62),('North','V24_03_Kitchen_Rear_Gable_Wall',-2.8,-2.935,-2.575)]:
 p=poly_at_y(load(n),y)
 p=p.union(rect(8.15,-.55,p.bounds[2],2.25)).union(return_poly)
 g=along_y(p,a,b);gables.append(g)
 # Dark grey raised verge, then a smaller bead below it, on the outer face.
 outside=a-.047 if tag=='South' else b-.003
 top=lambda x:2.425+(x-7.43)*(.395)
 for suffix,thick,dep,offset in [('Verge',.145,.055,0),('Verge_Bead',.030,.073,-.165)]:
  pp=Polygon([(7.43,top(7.43)+offset),(11.20,top(11.20)+offset),(11.20,top(11.20)+offset-thick),(7.43,top(7.43)+offset-thick)])
  yy=outside if tag=='North' else a-dep+.003
  put('V24_22_'+tag+'_'+suffix,along_y(pp,yy,yy+dep),GRAY,True)
 # Continuous quarter-ellipse corbel face, stepped jamb edge and projection tip.
 rr=LineString(arc).buffer(.057,cap_style=2,join_style=2)
 rr=rr.union(rect(8.09,-.41,8.205,1.68))
 yy=outside if tag=='North' else a-.055
 put('V24_22_'+tag+'_Curved_Gable_Return',along_y(rr,yy,yy+.061),GRAY,True)
 OUT['proof'][tag.lower()+'_gable']={'outer_y':a if tag=='South' else b,'inner_y':b if tag=='South' else a,'projection_m':.72,'curved_return_samples':arc,'reference':'084908','photo_fitted_not_surveyed':True}

wall=union([core,*gables])
put(main,wall,BRICK,False,transfer=True)
OUT['objects'][-1]['wall_finish']=True
OUT['remove'] += ['V24_03_Kitchen_Rear_Gable_Wall','V24_Kitchen_Gable_Upper_Brick_Infill','V24_17_Kitchen_North_Inner_Gable_Limewash','V24_17_Kitchen_South_Inner_Gable_Limewash','SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry']
# This detached remaining drain elbow is visible in 084853 after pipe removal.
OUT['remove'].append('V24_03_Kitchen_Rear_Drain_Elbow')
OUT['material_edits'].append({'name':'V24_14_Storage_West_Sealed_Gable','kind':'kitchen_side_below_existing_roof'})

# Same timber grain and established post stations; replace the piled-on porch
# cross beams with one supported beam per station. Purlins remain longitudinal.
YS=[-11.24,-8.26,-5.94,-2.96]
frames_name='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry'
oldframes=load(frames_name)
posts=oldframes^cube([12.5,-12,-.6],[14.5,-2.5,2.40])
purlin_name='SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry'
purlins=load(purlin_name);pcs=purlins.decompose()
keep=[p for p in pcs if p.bounding_box()[0]>9.0]
put(purlin_name,compose(keep),'M_Timber_Honey',False,transfer=True)

def centres(y):
 out=[]
 for p in keep:
  rings=p.rotate([-90,0,0]).slice(-y).to_polygons()
  if not rings:rings=p.rotate([-90,0,0]).slice(-float(np.clip(y,-11.20,-3.0))).to_polygons()
  q=max(rings,key=len);lo=q.min(0);hi=q.max(0);out.append(((lo+hi)/2).tolist())
 return sorted(out)

timber=[posts^cube([12.5,-12,-.6],[14.5,-2.5,-.20001])];braces=[];porch=[];post_x=[];contact_checks=[]
for i,y in enumerate(YS):
 centers=centres(y);front=centers[0];east=centers[-1];post_x.append(east[0])
 # Preserve the lower rear post/base exactly and join its upper extension.
 ps=posts^cube([12.5,y-.3,-.6],[14.5,y+.3,2.41])
 pv=ps.to_mesh64().vert_properties[:,:3];cx=(pv[:,0].min()+pv[:,0].max())/2
 end_z=east[1]-.13
 timber.append(rod([cx,y,-.215],[cx,y,end_z+.08],.13,24))
 x0=front[0];x1=cx
 def arch(x):
  t=(x-x0)/(x1-x0);return (front[1]-.20)*(1-t)+(east[1]-.20)*t+.49*4*t*(1-t)
 xs=np.linspace(x0-.06,x1+.06,65);poly=[(x,arch(x)-.12)for x in xs]+[(x,arch(x)+.12)for x in xs[::-1]]
 archbeam=profile_y(poly,y-.10,y+.10);timber.append(archbeam)
 for j,(x,z) in enumerate(centers):
  if x<x0-.05 or x>x1+.16:continue
  lo=arch(x)+.09;hi=z-.055
  if hi>lo:timber.append(cube([x-.085,y-.10,lo],[x+.085,y+.10,hi]))
 # One raking porch tie, fully joined to the two longitudinal members.
 pb=beam([8.28,y,2.57],[9.60,y,3.035],.16,.19);porch.append(pb)
 # Bracket at inner facade, short and attached, without a second crossing tie.
 bpoly=[(8.34,2.34),(8.34,2.57),(8.76,2.72),(8.63,2.55),(8.45,2.43)]
 braces.append(profile_y(bpoly,y-.09,y+.09))
 contact_checks.append({'station_y':y,'east_post_x':cx,'front_post_x':x0,'purlin_centres_xz':centers,'top_beam':'continuous cambered profile','porch_cross_beams':1})

frame=union(timber)
put(frames_name,frame,'M_Timber_Honey',False,transfer=True)
OUT['objects'][-1]['frame_base_material_by_z']=True
put('V24_22_Porch_Single_Cross_Beams',union(porch+braces),WOOD,True)

# Wall ties visible in the interior reference photographs. Lower east rail
# follows the original bent post line, joined at every post.
ties=[]
for y in [YS[0],YS[-1]]:
 east=contact_checks[0 if y==YS[0] else -1]['east_post_x']
 ties.append(cube([9.50,y-.075,1.92],[east+.10,y+.075,2.12]))
for a,b in zip(contact_checks[:-1],contact_checks[1:]):
 ties.append(beam([a['east_post_x'],a['station_y'],2.02],[b['east_post_x'],b['station_y'],2.02],.15,.20))
put('V24_22_Interior_Horizontal_Wall_Ties',union(ties),WOOD,True)

header=cube([8.20,-11.63,2.345],[8.48,-2.93,2.635])
put('SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry',header,WOOD)
OUT['remove'] += ['SITE_KITCHEN_V12_BEFORE_WOOD_16_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_18_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_19_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_22_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_30_Geometry','SITE_V22_KITCHEN_TRANSVERSE_EAVE_TIES_AND_HANGING_ENDS_Geometry','KITCHEN_V22_CARVED_PROJECTING_TIE_ENDS_Geometry','V24_06_Kitchen_Fluted_Melon_Pendants']
# Preserve facade-side details; retire only the superseded exterior attachments.
for n in ['SITE_KITCHEN_V12_BEFORE_WOOD_29_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_35_Geometry','V24_06_Kitchen_Bracket_Scroll_Relief','V24_06_Kitchen_Exposed_Timber_Pegs']:
 m=load(n)-cube([7,-12,-1],[9.35,-2,5])
 put(n,m,INDEX[n]['materials'][0],False,transfer=True)

# Square/stepped hanging lattice on the OUTER porch line. Real openings are
# modelled with solid bars, not an opaque surface or facade-window duplication.
fret_solids=[];pattern_rows=[]
for bay,(a,b) in enumerate([(-11.60,-7.28),(-6.92,-2.96)]):
 rails=[rect(a,2.315,b,2.385)]
 count=round((b-a)/.61);w=(b-a)/count
 for i in range(count):
  u=a+i*w;z=2.035
  pp=[(u,z+.285),(u+w,z+.285),(u+w,z+.17),(u+.76*w,z+.17),(u+.76*w,z),(u+.24*w,z),(u+.24*w,z+.17),(u,z+.17),(u,z+.285)]
  rails.append(LineString(pp).buffer(.014,join_style=2,cap_style=2))
  rails.append(LineString([(u+.10*w,z+.075),(u+.90*w,z+.075),(u+.90*w,z+.225),(u+.10*w,z+.225),(u+.10*w,z+.075)]).buffer(.012,join_style=2))
  rails.append(rect(u+.48*w,z+.25,u+.52*w,2.37))
 # Stepped end returns hang deeper beside the end jamb / centre abacus.
 for u,sgn in [(a,1),(b,-1)]:
  pp=[(u,2.34),(u,1.91),(u+sgn*.15,1.91),(u+sgn*.15,2.015),(u+sgn*.30,2.015),(u+sgn*.30,2.14)]
  rails.append(LineString(pp).buffer(.018,cap_style=2,join_style=2))
 shape=unary_union(rails)
 polygons=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
 solids=[]
 for pp in polygons:
  pp=orient(pp,1)
  cs=mf.CrossSection([np.array(pp.exterior.coords)[:-1]]+[np.array(r.coords)[:-1]for r in pp.interiors])
  # Ring winding of the union is normalised by CrossSection's nonzero fill.
  g=cs.extrude(.052).transform(np.array([[0,0,1,8.202],[1,0,0,0],[0,1,0,0]],float));solids.append(g)
 fret=union(solids);fret_solids.append(fret)
 pattern_rows.append({'bay':bay+1,'y_span':[a,b],'stepped_motifs':count,'bar_width_m':.028,'depth_m':.052,'bottom_z_m':1.892,'walking_headroom_m':2.292,'source':'DJI_0114 / DJI_0116 / 084117'})
put('V24_22_Outer_Stepped_Square_Fretwork',compose(fret_solids),'M_V12_Kitchen_GOLDEN_WOOD',True)

protected=cube([14.6,-30,-5],[40,10,15])+cube([0,-30,-5],[40,-12.10,15])
diff=((wall^protected)-(old^protected)).volume()+((old^protected)-(wall^protected)).volume()
assert diff<1e-7,('outside kitchen end scope changed',diff)
OUT['proof']['walls']={'joined_gable_solid':True,'overlapping_thin_plaster_leaves_removed':True,'old_oblique_end_leaves_removed':True,'protected_store_volume_difference_m3':diff,'inside_finish':'white limewash on the actual inner wall faces'}
OUT['proof']['timber_frames']=contact_checks
OUT['proof']['outer_fretwork']=pattern_rows
OUT['proof']['retained']=['all doors and animations','roof tile valley and ears','single porch centre column','bent east wall post line','all perimeter frieze','1.65m avatar and stair controller']
OUT['proof']['references_are_dimensional_fits']=True
write()
print('V22_GEOMETRY_READY',len(OUT['objects']),len(OUT['remove']),flush=True)
