import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
from v24_03_junction_blender import _mesh,_box,_bounds,_closed_stats

SETBACK=.45;FIXED=14.10;RIGID=9.40
def dx(x):return SETBACK*max(0,min(1,(FIXED-x)/(FIXED-RIGID)))
def move_mesh(o,rigid=False):
 old=o.data;o.data=old.copy();wm=o.matrix_world.copy();inv=wm.inverted();cnt=0;maxd=0
 for v in o.data.vertices:
  p=wm@v.co;d=SETBACK if rigid else dx(p.x)
  if d>1e-8:p.x+=d;v.co=inv@p;cnt+=1;maxd=max(maxd,d)
 o.data.update();o['V24_08_Setback']='Inner-court edge +0.45m East; outer site line anchored at X14.10; facade rigid through X9.40'
 if not old.users:bpy.data.meshes.remove(old)
 return {'name':o.name,'vertices_changed':cnt,'max_displacement_m':maxd,'bounds':_bounds(o)}

def setback():
 sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();rows=[];roots=[]
 # Move kitchen doors rigidly, including hinge roots. Keep action curves unchanged.
 for o in bpy.data.objects:
  if o.name.startswith('DOOR_COURTYARD_KITCHEN_V12_')and o.get('UE_Interaction')=='HINGED_INWARD':
   m=o.matrix_world.copy();m.translation.x+=SETBACK;o.matrix_world=m;roots.append(o.name)
 bpy.context.view_layer.update()
 # Static door frames have no moving root; leaf geometry is deliberately excluded.
 for o in bpy.data.objects:
  if o.type=='MESH'and o.name.startswith('DOOR_COURTYARD_KITCHEN_V12_')and'__FRAME_'in o.name:rows.append(move_mesh(o,True))
 extra=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_CONTINUATION_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TILE_COURSES_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TIMBER_CONTINUATION_Geometry']
 for o in list(bpy.data.objects):
  n=o.name
  if o.type!='MESH':continue
  yes=n.startswith(('SITE_KITCHEN_','SITE_V22_KITCHEN_','KITCHEN_V22_','V24_Kitchen_','V24_03_Kitchen_','V24_06_Kitchen_'))or n in extra
  if not yes:continue
  # Keep the gate-side masonry endpoint fixed to the accepted stone pier.
  if n=='SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry':
   old=o.data;o.data=old.copy();wm=o.matrix_world.copy();inv=wm.inverted();a=8.242666;end=9.075
   for v in o.data.vertices:
    p=wm@v.co;p.x+=SETBACK*max(0,min(1,(p.x-a)/(end-a)));v.co=inv@p
   o.data.update();rows.append({'name':n,'operation':'Keep fixed gate pier endpoint; extend closed return to retreated kitchen facade','bounds':_bounds(o)})
  else:rows.append(move_mesh(o))
 sc.frame_set(40);bpy.context.view_layer.update()
 return {'setback_m':SETBACK,'direction':'LOCAL +X / away from courtyard','front_floor_edge_before_x_m':7.7,'front_floor_edge_after_x_m':8.15,'facade_before_x_m':9.05,'facade_after_x_m':9.50,'outer_anchor_x_m':FIXED,'rigid_facade_x_limit_m':RIGID,'new_exposed_courtyard_strip_m2':SETBACK*9.27,'moving_kitchen_door_roots':roots,'changed_objects':rows,'basis':'User-directed modest correction, real courtyard photographs and registered context; not a measured survey dimension'}

def exterior_bands(work):
 # V19 outer facade segments explicitly contain the outward wall faces only.
 fd=json.loads((Path(work)/'v19/Facade_Segments.json').read_text());seg=[]
 for r in fd['brick']:
  a,b=Vector((*r['a'],0)),Vector((*r['b'],0));d=b-a;L=d.length
  if L>.1:seg.append((a,d/L,L))
 o=bpy.data.objects['SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry'];old=o.data;o.data=old.copy();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);left=set(bm.verts);remove=[];kept=[]
 while left:
  v=left.pop();part={v};stack=[v]
  while stack:
   for e in stack.pop().link_edges:
    for q in e.verts:
     if q in left:left.remove(q);part.add(q);stack.append(q)
  pts=[o.matrix_world@v.co for v in part];c=sum(pts,Vector())/len(pts);c.z=0
  dist=min((c-a-d*max(0,min(L,(c-a).dot(d)))).length for a,d,L in seg)
  # Preserve the decorated raised south entrance screen wall as well as all inside frames.
  screen=3.20<c.x<10.85 and c.y<-16.8
  info={'center_xy':[c.x,c.y],'outer_face_distance_m':dist,'vertices':len(part)}
  if dist<.085 and not screen:remove.extend(part);remove_info=info;kept_flag=False
  else:kept_flag=True
  if kept_flag:kept.append(info)
 bmesh.ops.delete(bm,geom=remove,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 if not old.users:bpy.data.meshes.remove(old)
 return {'name':o.name,'removed_vertices':len(remove),'retained_components':len(kept),'rule':'Remove complete closed exterior strips/frames within 85mm of registered outward facade; retain inside white finish and south decorated screen','closed_stats_after':_closed_stats(o)}

def metric_uv(o,repeat=(1.6,.90)):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_08_Metric_Exterior')
 for f in o.data.polygons:
  no=o.matrix_world.to_3x3()@f.normal
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   u=p.y+20 if abs(no.x)>abs(no.y)else p.x-11.515
   uv.data[li].uv=(u/repeat[0],p.z/repeat[1])

def finishes():
 # Reuse the supplied site's existing photographic images, without raster edits.
 photo=bpy.data.materials['M_V19_Perimeter_Brick'];mat=photo.copy();mat.name='M_V24_08_AsBuilt_Kitchen_Exterior_Brick';mat['Source']='Existing actual gray brick photo, metric facade UV; no texture nested inside individual masonry units'
 affected=[]
 names=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_03_Kitchen_Rear_Gable_Wall','V24_Kitchen_Gable_Upper_Brick_Infill','SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','V24_04_Kitchen_Perimeter_Upper_Return']
 for n in names:
  o=bpy.data.objects[n]
  for i,m in enumerate(o.data.materials):
   if m and m.name=='M_Grey_Brick':o.data.materials[i]=mat
  metric_uv(o);affected.append(n)
 # Physical individual bricks receive just one ceramic surface, not another brickwork pattern.
 m=bpy.data.materials.new('M_V24_08_Individual_Weathered_Brick');m.use_nodes=True;m.diffuse_color=(.07,.078,.074,1);nt=m.node_tree;ns=nt.nodes;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.94
 tx=ns.new('ShaderNodeTexNoise');tx.inputs['Scale'].default_value=28;tx.inputs['Detail'].default_value=3;co=ns.new('ShaderNodeTexCoord');nt.links.new(co.outputs['Object'],tx.inputs['Vector']);r=ns.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.032,.038,.035,1);r.color_ramp.elements[1].color=(.105,.115,.108,1);nt.links.new(tx.outputs['Fac'],r.inputs['Fac']);nt.links.new(r.outputs['Color'],bs.inputs['Base Color']);b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=.0012;b.inputs['Strength'].default_value=.35;nt.links.new(tx.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
 o=bpy.data.objects['SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS_Geometry'];o.data.materials[0]=m;affected.append(o.name)
 return {'changed_objects':affected,'new_materials':[mat.name,m.name],'photo_repeat_m':[1.6,.9],'original_shaders_untouched':True}

def tube(col,name,points,radius,thick,mat,segments=32,radii=None):
 V=[];F=[];n=len(points)
 for j,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(j+1,n-1)])-Vector(points[max(j-1,0)])).normalized();a=t.cross(Vector((0,1,0))).normalized()
  if a.length<.1:a=t.cross(Vector((1,0,0))).normalized()
  b=t.cross(a).normalized();r=radius if radii is None else radii[j]
  for rr in[r,r-thick]:
   for k in range(segments):V.append(tuple(p+(a*math.cos(2*math.pi*k/segments)+b*math.sin(2*math.pi*k/segments))*rr))
 for j in range(n-1):
  for k in range(segments):
   K=(k+1)%segments;A=j*2*segments;B=(j+1)*2*segments
   F.append((A+k,A+K,B+K,B+k));F.append((A+segments+k,B+segments+k,B+segments+K,A+segments+K))
 for j in[0,n-1]:
  A=j*2*segments
  for k in range(segments):K=(k+1)%segments;F.append((A+k,A+segments+k,A+segments+K,A+K))
 o=_mesh(bpy,col,name,V,F,mat)
 for f in o.data.polygons:f.use_smooth=True
 return o

def exhaust(col):
 mat=bpy.data.materials['M_Metal_Stainless'].copy();mat.name='M_V24_08_Brushed_Exhaust_Stainless';bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Metallic'].default_value=.85;bs.inputs['Roughness'].default_value=.42;bs.inputs['Base Color'].default_value=(.46,.48,.46,1);new=[]
 y=-5.95;x=14.38;wall=13.53+(y+8.5)*.104
 pts=[(wall-.035,y,1.56),(x-.12,y,1.56)]
 for j in range(1,13):a=j/12*math.pi/2;pts.append((x-.12+.12*math.sin(a),y,1.68-.12*math.cos(a)))
 pts.append((x,y,4.02));new.append(tube(col,'V24_08_Kitchen_Open_Round_Flue',pts,.065,.0025,mat))
 for z in[1.89,2.73,3.54]:
  new.append(tube(col,'V24_08_Flue_Clamp_'+str(z),[(x,y,z-.014),(x,y,z+.014)],.070,.003,mat));new.append(_box(bpy,col,'V24_08_Flue_StandOff_'+str(z),(wall-.02,y-.017,z-.017),(x-.062,y+.017,z+.017),mat))
 y2=-4.97;x2=14.32;wall2=13.53+(y2+8.5)*.104;pts=[]
 # Larger flexible elbow, turned downward as in the reference photographs.
 for j in range(17):
  a=j/16*math.pi/2;pts.append((wall2-.04+.39*math.sin(a),y2,2.12-.39*(1-math.cos(a))))
 pts.extend([(wall2+.35,y2,1.59),(wall2+.35,y2,1.48)])
 radii=[.10+.004*math.cos(j*math.pi)for j in range(len(pts))];new.append(tube(col,'V24_08_Kitchen_Corrugated_Exhaust_Elbow',pts,.1,.0025,mat,48,radii))
 # Closely spaced physical collars give the flexible duct its visible corrugation.
 for j in range(1,33):
  a=j/34*math.pi/2;p=Vector((wall2-.04+.39*math.sin(a),y2,2.12-.39*(1-math.cos(a))));t=Vector((math.cos(a),0,-math.sin(a)))
  new.append(tube(col,'V24_08_Exhaust_Rib_'+str(j),[p-t*.003,p+t*.003],.106,.007,mat,32))
 for yy,ww,zz,rr in[(y,wall,1.56,.086),(y2,wall2,2.12,.124)]:new.append(tube(col,'V24_08_Wall_Exhaust_Collar_'+str(yy),[(ww-.015,yy,zz),(ww+.025,yy,zz)],rr,.018,mat))
 return {'added_objects':[o.name for o in new],'basis':'DJI_0513/0523 visible round open flue and larger flexible downturned elbow; photo-fit positions','round_flue_outer_diameter_m':.13,'large_duct_outer_diameter_m':.20,'open_bores_and_closed_tube_walls':True}

def east_eave_tiles(col):
 from v24_03_junction_blender import _tree
 strip=bpy.data.objects['SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry'];tr=_tree(strip);mat=bpy.data.materials['M_Roof'];V=[];F=[];units=0;mins=[];maxs=[]
 def h(x,y):
  p,no,i,d=tr.ray_cast(Vector((x,y,7)),Vector((0,0,-1)),8)
  return p.z if p else None
 def patch(xs,ys,barrel):
  nonlocal units
  pts=[]
  for x in xs:
   for y,off in ys:
    z=h(x,y)
    if z is None:return
    pts.append((x,y,z+.012+off))
  nx,ny=len(xs),len(ys);N=len(pts);off=len(V);V.extend(pts);V.extend((x,y,z-.009)for x,y,z in pts)
  for i in range(nx-1):
   for j in range(ny-1):
    a=i*ny+j;b=a+ny;F.append(tuple(off+k for k in[a,b,b+1,a+1]));F.append(tuple(off+N+k for k in[a,a+1,b+1,b]))
  ring=list(range(ny))+[(i+1)*ny-1 for i in range(1,nx)]+list(range((nx-1)*ny+ny-2,(nx-1)*ny-1,-1))+[i*ny for i in range(nx-2,0,-1)]
  for a,b in zip(ring,ring[1:]+ring[:1]):F.append((off+a,off+N+a,off+N+b,off+b))
  units+=1
 for j in range(33):
  cy=-8.43+j*.18
  # Locate the actual registered irregular edge from rays rather than a box.
  xs=[13.63+i*.004 for i in range(240)];valid=[x for x in xs if h(x,cy-.078)is not None and h(x,cy+.078)is not None]
  if not valid:continue
  start,end=min(valid),max(valid)-.008
  if end-start<.08:continue
  mins.append(start);maxs.append(end);n=max(1,math.ceil((end-start)/.25))
  for i in range(n):
   a=start+i*(end-start)/n+.0015;b=start+(i+1)*(end-start)/n-.0015;xx=[a,(a+b)/2,b];yy=[(cy-.085+k*.17/10,.016*(2*k/10-1)**2)for k in range(11)];patch(xx,yy,False)
   yy=[(cy+.09+.064*math.sin(-math.pi/2+k*math.pi/12),.028*math.cos(-math.pi/2+k*math.pi/12))for k in range(13)];patch(xx,yy,True)
 if not V:return {'added_objects':[],'tile_units':0}
 o=_mesh(bpy,col,'V24_08_Registered_Kitchen_East_Eave_Ceramic_Courses',V,F,mat)
 return {'added_objects':[o.name],'tile_units':units,'pitch_m':.18,'outer_edge_range_x_m':[min(maxs),max(maxs)],'method':'Closed 9mm ceramic pan and cover units continue over the existing registered east eave surface; actual ray-fitted edge retained'}
