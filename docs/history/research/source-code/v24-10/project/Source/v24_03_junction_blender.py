"""V24.03 real-geometry west-wall return and xieshan / kitchen termination.

Run after apply_v24_xieshan. No load/save and no shader or gate-leaf edits.
"""
import json,math,time
from pathlib import Path

def _bounds(ob):
 from mathutils import Vector
 p=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 return [[min(v[i]for v in p)for i in range(3)],[max(v[i]for v in p)for i in range(3)]]

def _closed_stats(ob):
 import bmesh
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 result={'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':abs(bm.calc_volume(signed=True)),'vertices':len(bm.verts),'faces':len(bm.faces)}
 bm.free();return result

def _extend_return(bpy,ob,front_rake=True):
 import bmesh
 from mathutils import Vector
 old=ob.data;me=old.copy();bm=bmesh.new();bm.from_mesh(me)
 wm=ob.matrix_world;inv=wm.inverted();cut=4.72
 co=inv@Vector((cut,0,0));no=wm.to_3x3().transposed()@Vector((1,0,0))
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=co,plane_no=no,dist=1e-7,clear_inner=False,clear_outer=False)
 changed=0;maxmove=0
 for v in bm.verts:
  p=wm@v.co
  if p.x<cut-1e-6 or p.y>-11.45:continue
  t=max(0,min(1,(p.x-cut)/(4.9-cut)))
  q=p.copy();q.x+=(4.9343-4.9)*t
  if front_rake:
   # Hide the masonry end behind the pier's existing 90 mm chamfer.
   # The last 180 mm becomes a short side return, not a second coplanar filler.
   influence=max(0,min(1,(-11.575-p.y)/.25));q.y+=.052*t*influence
  maxmove=max(maxmove,(q-p).length);v.co=inv@q;changed+=1
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();ob.data=me
 if not old.users:bpy.data.meshes.remove(old)
 ob['V24_03_Pier_Return']='Continuous original wall end, 180 mm transition, follows straight pier side behind front chamfer'
 return {'name':ob.name,'operation':'continuous endpoint extension / short recessed return','changed_vertices':changed,'max_displacement_m':maxmove,'endpoint_x_m':4.9343,**_closed_stats(ob)}

def _mesh(bpy,col,name,V,F,mat):
 import bmesh
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(V,[],F);me.materials.append(mat);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='V24_03_Metric_UV')
 for l in me.loops:
  v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=(v.x+v.y,v.z)
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);return ob

def _box(bpy,col,name,lo,hi,mat):
 x,y,z=lo;X,Y,Z=hi
 return _mesh(bpy,col,name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def _tree(ob):
 from mathutils.bvhtree import BVHTree
 return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices)for p in ob.data.polygons],all_triangles=False,epsilon=1e-7)

def _difference(bpy,ob,cutter):
 import bmesh
 # Prepare a watertight mesh from the native triangulated readback. Original
 # face material indices and face-corner UVs are retained by bmesh / Boolean.
 old=ob.data;me=old.copy();bm=bmesh.new();bm.from_mesh(me)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();ob.data=me
 before=len(me.vertices);vol0=_closed_stats(ob)['volume_m3'];mats=[m.name if m else None for m in me.materials]
 for o in bpy.context.selected_objects:o.select_set(False)
 ob.select_set(True);bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new('V24_03_Xieshan_Conforming_Termination','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;mod.use_self=True;mod.use_hole_tolerant=True;mod.material_mode='INDEX'
 bpy.ops.object.modifier_apply(modifier=mod.name);ob.select_set(False)
 # Boolean cuts inherit an existing local slot; do not import cutter material.
 for p in ob.data.polygons:
  if p.material_index>=len(mats):p.material_index=0
 while len(ob.data.materials)>len(mats):ob.data.materials.pop(index=len(ob.data.materials)-1)
 # Repair the tiny new cut loops in intersecting legacy timber pieces. Existing
 # UV loops stay intact; new hidden return faces use the local first material.
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 boundary=[e for e in bm.edges if e.is_boundary]
 if boundary:
  filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0).get('faces',[])
  for f in filled:f.material_index=0
 tiny=[f for f in bm.faces if f.calc_area()<1e-7 and any(e.is_boundary for e in f.edges)]
 if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
 wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 if not old.users:bpy.data.meshes.remove(old)
 if not me.users:bpy.data.meshes.remove(me)
 stats=_closed_stats(ob);stats.update(name=ob.name,operation='exact closed envelope subtraction; cut faces capped',vertices_before=before,volume_before_m3=vol0,removed_volume_m3=vol0-stats['volume_m3'],materials_preserved=mats==[m.name if m else None for m in ob.data.materials],uv_preserved=bool(ob.data.uv_layers))
 ob['V24_03_Junction']='Conforming closed termination around new six-slope xieshan eaves, no exposed roof interpenetration'
 return stats

def apply_v24_03_junction(bpy,report_dir):
 from mathutils import Vector
 import v24_xieshan_roof_blender as xr
 start=time.perf_counter();out=Path(report_dir);out.mkdir(parents=True,exist_ok=True)
 assert bpy.data.objects.get('V24_XIESHAN_01_Lower_Four_Hip_Shells') or any(o.name.startswith('V24_XIESHAN_')for o in bpy.data.objects),'Apply new xieshan roof first'
 changed=[];removed=[];new=[];checks=[]
 oldkey=bpy.data.objects.get('GATE_V23_LEFT_WALL_JAMB_CLOSURE_Geometry')
 if oldkey:removed.append(oldkey.name);bpy.data.objects.remove(oldkey,do_unlink=True)
 col=bpy.data.collections.get('V24_03_双侧交接')
 if not col:col=bpy.data.collections.new('V24_03_双侧交接');bpy.context.scene.collection.children.link(col)
 # Edit only original terminal meshes, eliminating the overlapping old filler.
 names=['SITE_COURTYARD_WEST_TILE_WALL_Geometry','SITE_COURTYARD_WEST_WHITE_INSIDE_Geometry','SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_RIDGE_SEAT_AND_CAP_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry']
 for n in names:
  ob=bpy.data.objects.get(n)
  if ob:changed.append(_extend_return(bpy,ob,True))
 roof=bpy.data.materials['M_Roof'];stone=bpy.data.materials['M_Stone_Frame']
 # Solid terminal bearing below the flower-lattice end; only the 34 mm joint.
 ob=_box(bpy,col,'V24_03_Wall_Flower_Ridge_Terminal_Bearing',(4.898,-11.744,2.1968),(4.9343,-11.654,2.41965),roof);new.append(ob.name)
 # Exact shell envelope follows real slopes and stepped tiers, not a box.
 V,F=xr.xieshan_clearance_mesh_data(padding=.008)
 cutter=_mesh(bpy,col,'V24_03_TEMP_Conforming_Cutter',V,F,roof)
 cs=_closed_stats(cutter);assert cs['nonmanifold_edges']==0,cs
 # Complete envelope union includes the actual corner finials, round tile ends
 # and layered mouldings. A conservative 12 mm hidden bedding seat avoids the
 # previous analytical shell missing these protruding parts.
 vv=[tuple(v.co) for v in cutter.data.vertices];ff=[list(p.vertices) for p in cutter.data.polygons]
 for ro in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V24_XIESHAN_')]:
  k=len(vv);vv.extend(tuple(ro.matrix_world@v.co)for v in ro.data.vertices);ff.extend([k+i for i in p.vertices]for p in ro.data.polygons)
 data=bpy.data.meshes.new('V24_03_Complete_Bedding_Cutter');data.from_pydata(vv,[],ff);data.materials.append(roof);data.update();cutter.data=data
 for ob in bpy.context.selected_objects:ob.select_set(False)
 cutter.select_set(True);bpy.context.view_layer.objects.active=cutter
 rem=cutter.modifiers.new('Union_actual_roof_into_bedding_seat','REMESH');rem.mode='VOXEL';rem.voxel_size=.018;rem.adaptivity=.20;bpy.ops.object.modifier_apply(modifier=rem.name)
 dis=cutter.modifiers.new('Hidden_bedding_clearance_30mm','DISPLACE');dis.strength=.030;dis.mid_level=0;bpy.ops.object.modifier_apply(modifier=dis.name);cutter.select_set(False)
 cutter.display_type='WIRE';cutter.hide_render=True
 candidates=[]
 bounds=_bounds(cutter);ct=_tree(cutter)
 for ob in list(bpy.data.objects):
  if ob.type!='MESH' or ob==cutter:continue
  if not(ob.name.startswith('SITE_KITCHEN_') or ob.name.startswith('SITE_V22_KITCHEN_') or ob.name.startswith('KITCHEN_V22_') or ob.name in ['SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'] or ob.name.startswith('V24_Kitchen_')):continue
  lo,hi=_bounds(ob)
  if any(hi[i]<bounds[0][i]or lo[i]>bounds[1][i]for i in range(3)):continue
  if ct.overlap(_tree(ob)):candidates.append(ob)
 for ob in candidates:
  r=_difference(bpy,ob,cutter);changed.append(r);print('V24_03 JUNCTION TRIM',r,flush=True)
 # No permanent collision cutters. Cut ends remain real closed geometry.
 bpy.data.objects.remove(cutter,do_unlink=True)
 # Actual triangle intersections with complete new gate roof, across all groups.
 roofobs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V24_XIESHAN_')]
 roofdata=[(o,_bounds(o),_tree(o))for o in roofobs]
 collisions=[]
 for ob in candidates:
  lo,hi=_bounds(ob);tr=_tree(ob)
  for ro,rb,rt in roofdata:
   if any(hi[i]<rb[0][i]or lo[i]>rb[1][i]for i in range(3)):continue
   ov=tr.overlap(rt)
   if ov:collisions.append({'kitchen':ob.name,'gate':ro.name,'triangle_pairs':len(ov)})
 checks.append({'check':'Exact triangle intersections against every new xieshan mesh','pass':not collisions,'collisions':collisions})
 # Every new endpoint is a capped 3D solid; original material shaders untouched.
 for n in new:
  ob=bpy.data.objects[n];s=_closed_stats(ob);checks.append({'check':'Closed positive-volume end bearing '+n,'pass':s['nonmanifold_edges']==0 and s['volume_m3']>0,**s})
 for r in changed:
  if 'materials_preserved'in r:checks.append({'check':'Closed material/UV preserving kitchen cut '+r['name'],'pass':r['boundary_edges']==0 and r['materials_preserved']and r['uv_preserved'],**r})
 proof={'status':'PASS_V24_03_JUNCTION'if all(r['pass']for r in checks)else'FAIL_V24_03_JUNCTION','removed_objects':removed,'changed_old_objects':[r['name']for r in changed],'new_objects':new,'geometry_changes':changed,'checks':checks,'kitchen_candidates':[o.name for o in candidates],'left_return_method':'Original wall endpoints extended into recessed side joint; old overlapping filler removed; pier relief unmodified','left_terminal_x_m':4.9343,'left_front_terminal_y_m':-11.773,'source_dimension_note':'Registered LOCAL metre coordinates; wall/pier profiles read from current model, roof contact fitted to new xieshan shell','material_shaders_modified':False,'build_seconds':round(time.perf_counter()-start,3)}
 (out/'V24_03_Junction_Report.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
 print('V24_03 JUNCTION COMPLETE',proof['status'],flush=True)
 return proof
