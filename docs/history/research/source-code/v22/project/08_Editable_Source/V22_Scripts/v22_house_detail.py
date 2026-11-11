from v22_common import *
D=W/'v22_house';D.mkdir(exist_ok=True);Q=start();checks=[]
RED='MAT_DOOR_FRAME_RED';STONE='M_Stone';WHITE='M_Wall_Exterior'
# Restore a genuinely glazed upper entrance instead of an opaque wall band.
for fl,bottom,oldhead,newhead,top in [(1,0.,2.1,2.54,3.58),(2,3.9,6.,6.44,7.22)]:
 n=f'FACADE_CONTINUOUS_F{fl}';old=raw(n);cut=cube([4.10,1.98,oldhead-.002],[4.8,.47,top-oldhead+.004]);new=old-cut
 put(Q,n,[pp(new,'M_Wall_Exterior')],v22_entrance_upper_glazing=[newhead,top])
 checks.append({'check':n+' upper light really opened','removed_volume_m3':old.volume()-new.volume(),'pass':old.volume()-new.volume()>.1})
 n=f'DOOR_FRONT_CENTER_F{fl}__FIXED';ps=[]
 for mat in I[n]['materials']:
  m=raw(n,mat);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();v[:,2]=bottom+(v[:,2]-bottom)*(newhead-bottom)/(oldhead-bottom)
  ps.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),mat))
 put(Q,n,ps,v22_fixed_glazed_head_m=newhead)
 z0=newhead-.003;z1=top+.001;y=2.060
 frame=rectframe(4.10,8.90,z0,z1,y,.045,.085);bars=[frame]
 for x in np.linspace(4.10,8.90,9)[1:-1]:bars.append(cube([float(x)-.0175,y,z0],[.035,.085,z1-z0]))
 bars.append(cube([4.10,y,z0+.27],[4.80,.085,.027]))
 # Repeated stepped light patterns reproduce the front transom seen in the
 # ideal and real photographs, with frame-connected members rather than decals.
 for x in np.linspace(4.40,8.60,8):
  pts=[[x-.18,z0+.31],[x-.18,z1-.10],[x+.18,z1-.10],[x+.18,z0+.31]]
  bars.append(stroke(pts,.0085,.031).translate([0,y-.004,0]))
 glass=cube([4.145,y+.039,z0+.045],[4.71,.010,z1-z0-.09])
 put(Q,f'HOUSE_V22_FRONT_TRANSOM_F{fl}',[pp(uni(bars),RED),pp(glass,'M_Glass_Clear')],classification='TRUE_FIXED_GLAZED_TRANSOM_WITH_STEPPED_LATTICE')

changed=[]
for n in ['DOOR_FRONT_CENTER_F1__LEAF_1','DOOR_FRONT_CENTER_F1__LEAF_2','DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2']:
 fl=1 if '_F1' in n else 2;floor=0. if fl==1 else 3.9;ps=[]
 for mat in I[n]['materials']:
  m=raw(n,mat);q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();v[:,2]=floor+(v[:,2]-floor)*((2.48)/(2.04) if fl==1 else (2.48)/(2.05))
  ps.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),mat))
 vv=np.vstack([p['geometry']['vertices'] for p in ps]);lo=vv.min(0);hi=vv.max(0);x0=lo[0]+.075;x1=hi[0]-.075;z0=lo[2]+.10;z1=hi[2]-.10;y=lo[1]-.003
 m=rectframe(x0,x1,z0,z1,y,.017,.047)
 for x in [x0+.115,x1-.115]:m+=cube([x-.006,y,z0],[.012,.047,z1-z0])
 for z in [z0+.20,z1-.20]:m+=cube([x0,y,z],[x1-x0,.047,.014])
 ps.append(pp(m,RED))
 # Half-round handles follow each moving leaf, so the exported sliding motion
 # cannot leave decorative hardware hanging in the passage.
 hc=(x1-.020 if n.endswith(('LEAF_1','SLIDE_1')) else x0+.020);hz=floor+1.18
 tt=np.linspace(-math.pi/2,math.pi/2,25);sign=-1 if n.endswith(('LEAF_1','SLIDE_1')) else 1
 path=[[hc+sign*.085*math.cos(t),hz+.11*math.sin(t)] for t in tt]
 handle=stroke(path,.009,.027).translate([0,y-.024,0])
 ps.append(pp(handle,'M_Metal_Black'));put(Q,n,ps,v22_door=True,operation='SLIDING',v22_detail='Raised photo-fitted leaf, connected lattice and independent half-round handle')
 changed.append(n)

# Raise the two upper sliding tracks with the taller leaves; bottom tracks
# remain at the original floor elevation and retain their drainage detail.
for fl,rise in [(1,.44),(2,.43)]:
 n=f'HOUSE_V21_F{fl}_SLIDING_DOOR_TRACKS';ps=[];floor=0 if fl==1 else 3.9
 for mat in I[n]['materials']:
  q=raw(n,mat).to_mesh64();v=np.asarray(q.vert_properties)[:,:3].copy();v[v[:,2]>floor+1,2]+=rise
  ps.append(pp(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':np.asarray(q.tri_verts).tolist()}),mat))
 put(Q,n,ps,v22_detail='Upper guide raised to retain original leaf clearance; lower track fixed')

# Thin, correctly cut tile faces on existing bay-window plinth surfaces. The
# source facade face polygons determine all window holes and setbacks.
tiles=[]
for fl in [1,2,3]:
 d=np.load(B/'02_Data'/I[f'FACADE_CONTINUOUS_F{fl}']['file']);v=d['vertices'];f=d['faces'];planes={}
 for tri in f:
  t=v[tri];no=np.cross(t[1]-t[0],t[2]-t[0])
  if no[1]>=-1e-8 or abs(no[0])+abs(no[2])>abs(no[1])*1e-5 or t[:,1].mean()>2.11:continue
  y=round(float(t[:,1].mean()),5);planes.setdefault(y,[]).append(Polygon(t[:,[0,2]]))
 for y,polys in planes.items():
  face=unary_union(polys)
  if fl in [1,2] and y>1.98:
   face=face.difference(shbox(4.10,2.098 if fl==1 else 5.998,8.90,3.582 if fl==1 else 7.222))
  if face.is_empty or face.area<1e-9:continue
  x0,z0,x1,z1=face.bounds
  for iz,z in enumerate(np.arange(math.floor(z0/.45)*.45,z1,.45)):
   for x in np.arange(math.floor(x0/.6)*.6,x1,.6):
    p=face.intersection(shbox(x+.0025,z+.0025,x+.5975,z+.4475))
    ppys=[p] if p.geom_type=='Polygon' else list(getattr(p,'geoms',[]))
    for poly in ppys:
     poly=poly.simplify(1e-7,preserve_topology=True)
     if poly.area<.006:continue
     g=manifold({'type':'prism','profile':[[float(xx),y-.004,float(zz)] for xx,zz in list(poly.exterior.coords)[:-1]],'vector':[0,.005,0]})
     tiles.append(pp(g,'M_Stone'))
put(Q,'HOUSE_V22_FRONT_BAY_TILE_FACES',tiles,classification='THIN_JOINTED_WHITE_TILES_CLIPPED_TO_NATIVE_FACADE_FACE_OPENINGS',face_projection_m=.004)

# Balcony panels: recessed borders, continuous scrolling floral relief and
# rounded post finials fitted to the existing guard (not a new projecting rail).
rel=[]
for cx in [4.70,6.50,8.30]:
 rel.append(rectframe(cx-.65,cx+.65,4.18,4.58,-.109,.025,.020))
 rel.append(flower(cx,4.38,.13,.013).translate([0,-.122,0]))
 for side in [-1,1]:
  pts=[[cx+side*t,4.38+.05*math.sin(t*12)] for t in np.linspace(.08,.54,25)]
  rel.append(stroke(pts,.007,.013).translate([0,-.122,0]))
  for j,t in enumerate([.23,.40]):rel.append(petal(cx+side*t,4.41 if j%2 else 4.34,.12,.05,side*30,.014).translate([0,-.123,0]))
put(Q,'HOUSE_V22_BALCONY_FLORAL_PANELS',[pp(uni(rel),STONE)],classification='REFERENCE_IDEAL_GUARD_PANEL_BORDER_AND_PLANT_RELIEF')

# Real one-step porch stays solid; the courtyard receives individually modeled
# stone slabs and filled joints without altering its existing drainage surface.
n='CONSTRUCTION_COURTYARD_DRAINAGE_FINISH';floor=raw(n);bb=floor.bounding_box();pieces=[];boxes=[];slabs=[]
Q['materials']['M_V22_Courtyard_Filled_Joint']={'color':[92,94,88],'roughness':.97}
for j,c in enumerate([[135,137,129],[142,141,131],[128,131,125],[149,148,137]]):Q['materials'][f'M_V22_Courtyard_Stone_{j}']={'color':c,'roughness':.88}
for iy,y in enumerate(np.arange(-10.9,-.899,.62)):
 for ix,x in enumerate(np.arange(.4-(.56 if iy%2 else 0),7.251,1.12)):
  b=cube([float(x)+.003,float(y)+.003,-.55],[1.114,.614,.20]);tile=floor^b
  if tile.is_empty() or tile.volume()<1e-8:continue
  boxes.append(b);slabs.append(tile);pieces.append(pp(tile,f'M_V22_Courtyard_Stone_{(ix+iy*3)%4}'))
grout=floor-uni(boxes);pieces.insert(0,pp(grout,'M_V22_Courtyard_Filled_Joint'))
allfloor=uni(slabs+[grout]);err=(floor-allfloor).volume()+(allfloor-floor).volume();assert err<1e-8,err
recessed_grout=grout.translate([0,0,-.0015])^floor
pieces[0]=pp(recessed_grout,'M_V22_Courtyard_Filled_Joint')
put(Q,n,pieces,classification='INDIVIDUAL_STONE_PAVERS_AND_FILLED_JOINTS_IN_ORIGINAL_GRADED_VOLUME')
checks.append({'check':'Stone slab drainage surfaces retained; filled joints recessed only 1.5 mm','partition_symmetric_difference_before_joint_recess_m3':err,'joint_recess_m':.0015,'pass':True,'individual_slabs':len(slabs)})
Q['cameras']=[['V22_Courtyard_Ideal_Compare',[6.65,-10.4,1.25],[5.25,.85,2.9],68],['V22_House_Entrance_Compare',[7.10,-5.0,1.15],[6.3,1.8,1.95],75],['V22_House_Balcony_Detail',[6.3,-3.1,4.6],[6.5,.0,4.55],65]]
Q['change_notes']=['楼房入口实心空白高带改成真实上亮玻璃及回纹格，门扇按比例提高、细化边框和随动半圆拉手，继续保留横向推拉。','前立面窗下及楼层带按原墙面切分薄砖面、留细缝；阳台栏板增加浅框、卷草花卉细节。','内院铺地按原排水实体分割成石板与填缝，完整保留坡面、边界和实心一阶台阶。']
save(Q,D,checks)
