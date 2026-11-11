from pathlib import Path
import bpy,bmesh,json,hashlib,shutil,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_35';O=Path('E:/jz/JIA/Rebuild_V24_35');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_35.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend')
for d in [R,O/'Blender',O/'Roam',O/'References']:d.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();prep=json.loads((D/'Prepared_Geometry.json').read_text());changed=[];removed=[]
for r in prep['changed']:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);me=bpy.data.meshes.new(r['name']+'_V35');inv=o.matrix_world.inverted();me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f']);me.polygons.foreach_set('material_index',a['mi']);me.update();layer=me.uv_layers.new(name='Original_Photo_UV_Barycentric_Cut');layer.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 for mat in o.data.materials:me.materials.append(mat)
 o.data=me;o['V24_35_Repair']='Native complete eave and wall exclusion, local annotated region only';changed.append(o.name)
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();base_n=json.loads(Path('E:/jz/JIA/Rebuild_V24_34/Reports/V24_34_Collision_Index.json').read_text())['original_architectural_triangles'];basefaces=[tuple(t.vertices)for t in list(old.loop_triangles)[:base_n]];nv=max(max(f)for f in basefaces)+1;verts=[tuple(cache.matrix_world@v.co)for v in list(old.vertices)[:nv]];faces=basefaces;proxy=[];deps=bpy.context.evaluated_depsgraph_get();photo=[o for o in bpy.data.objects if o.type=='MESH'and not o.hide_render and('ORIGINAL_EXTERIOR_'in o.name or o.name.startswith('V24_34_MB7_'))]
for j,o in enumerate(photo):
 me=o.data.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.to_mesh(me);bm.free();temp=bpy.data.objects.new('TEMP_V35_COLLISION',me);sc.collection.objects.link(temp);temp.matrix_world=o.matrix_world.copy()
 if len(me.polygons)>600:mod=temp.modifiers.new('Real_Surface_Proxy','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 deps.update();ev=temp.evaluated_get(deps);pm=bpy.data.meshes.new_from_object(ev);pm.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in pm.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in pm.loop_triangles);proxy.append({'object':o.name,'proxy_triangles':len(pm.loop_triangles),'display_triangles':len(o.data.polygons)});bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(pm);bpy.data.meshes.remove(me)
 if j%40==0:print('COLLISION',j,len(photo),flush=True)
me=bpy.data.meshes.new('V24_35_Clean_Eave_Navigation');me.from_pydata(verts,[],faces);me.update();cache.data=me;cache['V24_35_Ghost_Wall_Removed']=True;changed.append(cache.name);np.savez_compressed(D/'Final_Collision.npz',v=np.array(verts,np.float32),f=np.array(faces,np.int32))
for fn in ['start_roam.py','roam_controller.py','roam_physics.py','measure_tools.py']:shutil.copy2(SOURCE.parents[1]/'Roam'/fn,O/'Roam'/fn)
for fn in ['启动漫游.cmd','打开修正版模型.cmd']:(O/fn).write_text((SOURCE.parents[1]/fn).read_text('utf8').replace('V24_34','V24_35'),encoding='utf8')
col=bpy.data.collections.new('V24_35_屋檐与青砖外墙扫描残片清理');sc.collection.children.link(col)
for tag,pos,aim,lens in json.loads((D/'Views.json').read_text()):
 c=bpy.data.objects.new('V24_35_'+tag,bpy.data.cameras.new('V24_35_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=350
ref=Path('D:/Desktop/屏幕截图 2026-10-21 135627.jpg');im=bpy.data.images.load(str(ref),check_existing=True);im.pack();shutil.copy2(ref,O/'References'/ref.name);note=bpy.data.texts.new('V24_35_135627修正');note.write('截图圈出的白色破面来自MB7外景旧墙体与屋檐扫描残片。按完整原生厨房和储物间屋面、弯曲院墙保护范围，限定局部高度范围裁掉扫描残片，保留原青砖墙、瓦面、烟管、排气弯管与全部原建筑动作；同步重建实际扫描碰撞代理。')
sc['Version']='V24_35_CLEAN_KITCHEN_EAVE_AND_WALL_SOURCE_GHOSTS';sc.frame_set(40);sc.camera=bpy.data.objects['V24_35_01_Kitchen_East'];bpy.context.view_layer.update();report={'source':str(SOURCE),'source_sha256':sha(SOURCE),'changed':changed,'removed':removed,'native_roof_wall_pipes_unchanged':True,'proof':prep['proof']};(R/'V24_35_Changes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(R/'V24_35_Collision_Index.json').write_text(json.dumps({'original_architectural_triangles':base_n,'all_triangles':len(faces),'vertices':len(verts),'exterior_sources':proxy,'proxy_ratio':.28},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(R/'V24_35_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'source_sha256':sha(SOURCE)},indent=2));print('V35_SAVED',sha(P),flush=True)
