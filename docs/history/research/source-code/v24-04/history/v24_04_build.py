"""Focused V24.04: lighter gate roof and continuous kitchen rear/end enclosure."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_04_common import *
from v24_03_junction_blender import _bounds,_tree,_mesh,_box,_difference,_closed_stats
import v24_04_roof as xr
for n in ['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40)
base=snapshot(bpy);write('V24_04_Before_Snapshot.json',base)
oldroof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')]
zmin=min(_bounds(o)[0][2]for o in oldroof);zmax=max(_bounds(o)[1][2]for o in oldroof)
for ob in oldroof:bpy.data.objects.remove(ob,do_unlink=True)
roof=xr.apply_v24_xieshan_roof(bpy,R)
newroof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')]
roof['proportion_change']={'old_roof_stack_m':zmax-zmin,'new_roof_stack_m':max(_bounds(o)[1][2]for o in newroof)-zmin,'old_eave_bearing_m':.762,'new_eave_bearing_m':.402,'roof_width_and_depth_preserved':True,'ceiling_bearing_z_m':2.538}
print('LIGHTER ROOF GENERATED',roof['proportion_change'],flush=True)

# Recover only former junction components; the old large roof had removed too
# much material from them. Keep their original shaders and all other site data.
oldrep=json.loads(Path('E:/jz/JIA/Rebuild_V24_03/Reports/V24_03_Junction_Report.json').read_text(encoding='utf8'))
restore=oldrep['kitchen_candidates'];origmat={m.name:m for m in bpy.data.materials}
beforeids={k:set(getattr(bpy.data,k))for k in ['objects','meshes','materials','images','collections']}
with bpy.data.libraries.load('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend',link=False)as(a,b):b.objects=[n for n in restore if n in a.objects]
restored=[]
for src,n in zip(b.objects,[n for n in restore if n in a.objects]):
 if src is None:continue
 dst=bpy.data.objects[n];me=src.data
 for i,m in enumerate(me.materials):
  if not m:continue
  key=m.name
  if key not in origmat and len(key)>4 and key[-4]=='.'and key[-3:].isdigit():key=key[:-4]
  assert key in origmat,(n,key);me.materials[i]=origmat[key]
 old=dst.data;dst.data=me
 if not old.users:bpy.data.meshes.remove(old)
 restored.append(n)
for ob in list(bpy.data.objects):
 if ob not in beforeids['objects']:bpy.data.objects.remove(ob,do_unlink=True)
for k in ['meshes','collections','materials','images']:
 for data in list(getattr(bpy.data,k)):
  if data not in beforeids[k]and data.users==0:getattr(bpy.data,k).remove(data)
# Retain the 15 mm rear lintel bearing achieved in V24.03.
beam=bpy.data.objects['SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry'];inv=beam.matrix_world.inverted()
for v in beam.data.vertices:
 p=beam.matrix_world@v.co
 if p.y>-2.835:p.y=-2.770;v.co=inv@p
beam.data.update();print('LOCAL JUNCTION SOURCES RECOVERED',len(restored),flush=True)

# Follow the underside of the existing roof. A continuous end return connects
# the brick wall to the actual retaining-wall endpoint, including the former
# half-metre slot. All surfaces are real, capped, and have metre-based UVs.
col=bpy.data.collections.new('V24_04_厨房端墙连续封闭');sc.collection.children.link(col)
rt=[_tree(bpy.data.objects[n])for n in ['SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry']]
xs=sorted(set([7.70+i*(14.10-7.70)/64 for i in range(65)]+[9.05,11.515,13.13,13.25,13.35,13.60,13.88,14.10]))
path=[];fitting=[]
for x in xs:
 t=max(0,(x-13.25)/.85);yc=-2.69-.13*t
 hits=[tr.ray_cast(Vector((x,yc,1.0)),Vector((0,0,1)),5)for tr in rt]
 hits=[h[0].z for h in hits if h[0]is not None]
 if hits:z=min(hits)+.012
 else:z=3.367-(x-13.35)*.4
 path.append((x,yc,z));fitting.append({'x':x,'y':yc,'wall_top_z':z,'roof_hit':bool(hits)})
def wall_data(bottom,top=None):
 V=[];F=[];n=len(path)
 for side in [-1,1]:
  for upper in [False,True]:
   V.extend((x,y+side*.115,(z if top is None else top)if upper else bottom)for x,y,z in path)
 for i in range(n-1):
  j=i+1;F.extend([[i,j,n+j,n+i],[2*n+i,3*n+i,3*n+j,2*n+j],[i,2*n+i,2*n+j,j],[n+i,n+j,3*n+j,3*n+i]])
 F.extend([[0,n,3*n,2*n],[n-1,3*n-1,4*n-1,2*n-1]])
 return V,F
def replace_solid(name,V,F,mat):
 old=bpy.data.objects.get(name);ob=_mesh(bpy,col,name+'_TEMP',V,F,bpy.data.materials[mat])
 uv=ob.data.uv_layers.active
 for p in ob.data.polygons:
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x,v.z)
 if old:
  me=old.data;old.data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);ob=old
  if not me.users:bpy.data.meshes.remove(me)
 else:ob.name=name
 assert _closed_stats(ob)['nonmanifold_edges']==0,(name,_closed_stats(ob))
 return ob
wall=replace_solid('V24_03_Kitchen_Rear_Gable_Wall',*wall_data(-.424),'M_Grey_Brick')
wall['V24_04_Closure']='Continuous masonry to retaining wall, roof-fitted top; 230 mm solid thickness'
replace_solid('V24_03_Kitchen_Rear_Stone_Plinth',*wall_data(-.434,-.15),'M_Stone_Frame')
# Put the retained pipe on the exterior of the newly continuous rear face.
for n in ['V24_03_Kitchen_Rear_Corner_Downpipe','V24_03_Kitchen_Rear_Drain_Elbow']:
 ob=bpy.data.objects[n];ob.location.y+=.30

# Form a new bedding envelope for the thinner roof, then trim only actual
# intersecting neighbouring components. This is not an axis-aligned box cut.
V,F=xr.xieshan_clearance_mesh_data(.006);vv=list(V);ff=list(F)
for ro in newroof:
 k=len(vv);vv.extend(tuple(ro.matrix_world@v.co)for v in ro.data.vertices);ff.extend([k+i for i in p.vertices]for p in ro.data.polygons)
cutter=_mesh(bpy,col,'V24_04_TEMP_Bedding',vv,ff,bpy.data.materials['M_Roof'])
for ob in bpy.context.selected_objects:ob.select_set(False)
cutter.select_set(True);bpy.context.view_layer.objects.active=cutter
mod=cutter.modifiers.new('Actual_roof_union','REMESH');mod.mode='VOXEL';mod.voxel_size=.012;mod.adaptivity=.15;bpy.ops.object.modifier_apply(modifier=mod.name)
mod=cutter.modifiers.new('Concealed_20mm_bedding','DISPLACE');mod.strength=.020;mod.mid_level=0;bpy.ops.object.modifier_apply(modifier=mod.name);cutter.select_set(False)
ct=_tree(cutter);cb=_bounds(cutter);trim=[]
for n in restored:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob)
 if any(hi[i]<cb[0][i]or lo[i]>cb[1][i]for i in range(3)):continue
 if ct.overlap(_tree(ob)):
  row=_difference(bpy,ob,cutter);trim.append(row);print('REFIT',n,row['boundary_edges'],flush=True)
bpy.data.objects.remove(cutter,do_unlink=True)
# Legacy rafters can leave zero-area cut slivers; remove only these.
for row in trim:
 ob=bpy.data.objects[row['name']];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 tiny=[f for f in bm.faces if f.calc_area()<1e-7 and any(e.is_boundary for e in f.edges)]
 if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
 wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 bm.to_mesh(ob.data);bm.free();ob.data.update();row.update(_closed_stats(ob))
rows=[(o,_bounds(o),_tree(o))for o in newroof];collisions=[]
for n in restored:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob);tr=_tree(ob)
 for ro,rb,tree in rows:
  if any(hi[i]<rb[0][i]or lo[i]>rb[1][i]for i in range(3)):continue
  ov=tr.overlap(tree)
  if ov:collisions.append({'kitchen':n,'gate':ro.name,'triangle_pairs':len(ov)})
print('INTERSECTION RESULTS',collisions,flush=True)
write('V24_04_Closure_and_Contact.json',{'wall':_bounds(wall),'wall_thickness_m':.23,'terminal_x_before_m':13.35,'terminal_x_after_m':14.10,'roof_top_fit':fitting,'restored_for_new_roof':restored,'trim':trim,'remaining_intersections':collisions,'all_roof_top_samples_hit':all(r['roof_hit']for r in fitting)})

sc.frame_set(40);bpy.context.view_layer.update();after=snapshot(bpy)
changed=[n for n,r in base['objects'].items()if n in after['objects']and after['objects'][n]!=r]
removed=sorted(set(base['objects'])-set(after['objects']));added=sorted(set(after['objects'])-set(base['objects']))
write('V24_04_Changes.json',{'changed_objects':changed,'removed_objects':removed,'added_objects':added,'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'roof':roof})
for m in bpy.data.materials:m.use_fake_user=True
for im in bpy.data.images:
 if im.source!='VIEWER'and im.type not in ['RENDER_RESULT','COMPOSITING']:im.use_fake_user=True
sc['Version']='V24_04_LIGHTER_XIESHAN_CONTINUOUS_KITCHEN_WALL';sc['Source_SHA256']=sha(B)
guide='''V24.04：内大门屋顶减薄与厨房墙端封闭。
屋顶檐下厚度由0.762m收至0.402m，屋面主脊降低；保留歇山六坡、九脊、五级檐线和独立瓦件。未整体压缩门柱及浮雕。
厨房后墙延伸到外围墙端部，墙顶按屋面下表面拟合，230mm厚实体封墙。檐廊保留一根独立柱。
保留实景材质、15块灰度浮雕和26扇门原动画。1–40帧查看门动作，默认40帧。
完整基地米制Blender模型；原V24.03保留。Reports含新旧尺寸、校验和实景材质预览。
'''
(O/'README_V24_04.txt').write_text(guide,encoding='utf-8-sig');txt=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');txt.clear();txt.write(guide)
# Save immediately reviewable views, without adding preview lights to the file.
for n,pos,tar,lens in [('V24_04_Saved_Gate_Rear',(4.6,-7.4,2.5),(6.6,-11.9,1.85),25),('V24_04_Saved_Kitchen_Closure',(4.2,-.6,2.1),(10.8,-2.8,1.5),28)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
sc.camera=bpy.data.objects['V24_04_Saved_Kitchen_Closure'];sc.frame_set(40)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
write('V24_04_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'blender':bpy.app.version_string,'roof':roof,'intersections':collisions})
print('V24.04 SAVED',P,flush=True)
