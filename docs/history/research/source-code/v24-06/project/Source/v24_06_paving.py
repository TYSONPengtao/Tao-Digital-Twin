"""Extend the existing passage material over the selected south-side earth strip."""
import math,numpy as np
from mathutils import Vector
def apply_paving(bpy):
 import bmesh
 from v24_03_junction_blender import _tree
 ref=bpy.data.objects['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry'];soil=bpy.data.objects['SITE_V16_GRADED_INTERIOR_SOIL_Geometry'];target=ref.data.materials[0];ref.data.calc_loop_triangles();triangles=[];uvdata=[];uvref=ref.data.uv_layers.active
 for f in ref.data.polygons:
  if (ref.matrix_world.to_3x3()@f.normal).z<.3:continue
  for li in f.loop_indices:
   v=ref.matrix_world@ref.data.vertices[ref.data.loops[li].vertex_index].co;uv=uvref.data[li].uv;uvdata.append([v.x,v.y,uv.x,uv.y])
 for tri in ref.data.loop_triangles:
  if(ref.matrix_world.to_3x3()@tri.normal).z>.3:triangles.append([ref.matrix_world@ref.data.vertices[i].co for i in tri.vertices])
 d=np.asarray(uvdata);A=np.column_stack([d[:,:2],np.ones(len(d))]);fit=np.linalg.lstsq(A,d[:,2:],rcond=None)[0];rmse=float(np.sqrt(np.mean((A@fit-d[:,2:])**2)))
 def ymin(x):
  ys=[]
  for tri in triangles:
   if x<min(p.x for p in tri)-1e-6 or x>max(p.x for p in tri)+1e-6:continue
   for a,b in zip(tri,tri[1:]+tri[:1]):
    if abs(b.x-a.x)<1e-8:
     if abs(x-a.x)<1e-5:ys.extend([a.y,b.y])
    elif min(a.x,b.x)-1e-7<=x<=max(a.x,b.x)+1e-7:ys.append(a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x))
  return min(ys)if ys else None
 # Witness sections follow the corridor edge and bridge the old tree notch.
 # The far-west edge is the actual entry throat, rather than a tiled side bay.
 xs=[-11.88,-11.54,-9.83,-4.50,-3.13,7.90];line=[(-12.85,-12.48)]+[(x,ymin(x))for x in xs];line=[p for p in line if p[1]is not None]
 # Simplify only truly straight runs; the new pavement follows the old path.
 def simplify(points):
  if len(points)<=2:return points
  a,b=Vector(points[0]),Vector(points[-1]);u=b-a;err=[abs((Vector(p)-a).x*u.y-(Vector(p)-a).y*u.x)/u.length for p in points];j=max(range(len(err)),key=lambda i:err[i])
  if err[j]<.012:return[points[0],points[-1]]
  return simplify(points[:j+1])[:-1]+simplify(points[j:])
 line=simplify(line);assert len(line)>=2,line
 ring=[];rt=_tree(ref)
 for k in range(24):
  a=math.tau*k/24;x=-4+.55*math.cos(a);y=-13.5+.55*math.sin(a);h=rt.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),10)
  if h[0]is not None:ring.append([x,y,h[0].z])
 assert len(ring)>=5
 rr=np.asarray(ring);rootfit=np.linalg.lstsq(np.column_stack([rr[:,:2],np.ones(len(rr))]),rr[:,2],rcond=None)[0]
 # The 0.8m tree pit clips the edge of the original road. Union a fitted
 # closed plug into the original road so the rim is sealed on both skins.
 oldref=ref.data;rme=oldref.copy();rbm=bmesh.new();rbm.from_mesh(rme);bmesh.ops.remove_doubles(rbm,verts=list(rbm.verts),dist=1e-6);rbm.to_mesh(rme);rbm.free();rme.update();ref.data=rme
 if not oldref.users:bpy.data.meshes.remove(oldref)
 from v24_03_junction_blender import _mesh
 sec=96;V=[]
 for dz in [-.22,0]:
  for k in range(sec):
   a=math.tau*k/sec;x=-4+.410*math.cos(a);y=-13.5+.410*math.sin(a);V.append((x,y,float(np.array([x,y,1.])@rootfit)+dz))
 F=[list(range(sec-1,-1,-1)),list(range(sec,sec*2))]+[[k,(k+1)%sec,(k+1)%sec+sec,k+sec]for k in range(sec)]
 plug=_mesh(bpy,bpy.context.scene.collection,'V24_06_Temporary_Road_Pit_Plug',V,F,target)
 for o in bpy.context.selected_objects:o.select_set(False)
 ref.select_set(True);bpy.context.view_layer.objects.active=ref;mod=ref.modifiers.new('V24_06_Seal_Tree_Notch','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=plug;bpy.ops.object.modifier_apply(modifier=mod.name);pdata=plug.data;bpy.data.objects.remove(plug,do_unlink=True)
 if not pdata.users:bpy.data.meshes.remove(pdata)
 rbm=bmesh.new();rbm.from_mesh(ref.data);bmesh.ops.remove_doubles(rbm,verts=list(rbm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(rbm,faces=list(rbm.faces));ruv=rbm.loops.layers.uv.active
 for f in rbm.faces:
  for lp in f.loops:
   p=ref.matrix_world@lp.vert.co
   if math.hypot(p.x+4,p.y+13.5)<.412:lp[ruv].uv=tuple(np.array([p.x,p.y,1.])@fit)
 rbm.to_mesh(ref.data);rbm.free();ref.data.update()
 def boundary(x):
  for(a,b)in zip(line,line[1:]):
   if a[0]-1e-6<=x<=b[0]+1e-6:return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])+.035
  return None
 prior=_tree(soil);height_samples=[]
 for x in [-12,-10,-7,-4,0,3,6]:
  yy=boundary(x)
  if yy is None:continue
  for y in [yy-.30,yy-.80,yy-1.40]:
   h=prior.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),12)
   if h[0]is not None:height_samples.append({'x':x,'y':y,'old_ground_z':h[0].z})
 old=soil.data;me=old.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 inv=soil.matrix_world.inverted();wm=soil.matrix_world
 def bisect(geom,point,normal):
  return bmesh.ops.bisect_plane(bm,geom=geom,dist=1e-6,plane_co=inv@Vector(point),plane_no=wm.to_3x3().transposed()@Vector(normal),clear_inner=False,clear_outer=False)
 for x,_ in line:bisect(list(bm.verts)+list(bm.edges)+list(bm.faces),(x,0,0),(1,0,0))
 for a,b in zip(line,line[1:]):
  if b[0]-a[0]<1e-5:continue
  fs=[f for f in bm.faces if a[0]-1e-5<=(wm@f.calc_center_median()).x<=b[0]+1e-5];es={e for f in fs for e in f.edges};vs={v for e in es for v in e.verts};m=(b[1]-a[1])/(b[0]-a[0]);intercept=a[1]-m*a[0]+.035
  bisect(list(vs)+list(es)+fs,(0,intercept,0),(-m,1,0))
 slot=me.materials.find(target.name)
 if slot<0:me.materials.append(target);slot=len(me.materials)-1
 uv=bm.loops.layers.uv.active
 if uv is None:uv=bm.loops.layers.uv.new('V24_06_Passage_Metric_UV')
 area=0;faces=0;polys=[];bm.normal_update()
 for f in bm.faces:
  c=wm@f.calc_center_median();bound=boundary(c.x)
  if bound is None or c.y>bound+1e-5 or(wm.to_3x3()@f.normal).z<.35:continue
  f.material_index=slot;area+=f.calc_area();faces+=1
  for loop in f.loops:
   v=wm@loop.vert.co;u=np.array([v.x,v.y,1.])@fit;loop[uv].uv=tuple(u)
  polys.append([tuple(wm@v.co)for v in f.verts])
 bm.to_mesh(me);bm.free();me.update();soil.data=me
 if not old.users:bpy.data.meshes.remove(old)
 soil['V24_06_Paving']='Selected strip follows south edge of existing gate-to-inner-gate path; same material and metre UV; original grade retained'
 removed=[]
 for n in ['SITE_TREE_5_Geometry','SITE_TREE_6_Geometry','SITE_V15_EXISTING_TREE_ROOT_SOIL_Geometry']:
  ob=bpy.data.objects.get(n)
  if ob:removed.append(n);bpy.data.objects.remove(ob,do_unlink=True)
 return {'changed_objects':[soil.name,ref.name],'removed_objects':removed,'reference_path':ref.name,'material':target.name,'material_slot':slot,'uv_fit':fit.tolist(),'uv_fit_rms':rmse,'south_edge_xy':line,'paved_surface_area_m2':area,'paved_faces':faces,'height_samples':height_samples,'changed_face_world_polygons':polys,'site_grade_preserved':True,'root_pit_repair':{'center_xy':[-4,-13.5],'diameter_m':.8,'matching_road_plane':rootfit.tolist(),'recess_below_reference_road_m':0,'neighbor_witness_points':len(ring),'union_in_original_road_mesh':True,'plug_overlap_m':.010}}
