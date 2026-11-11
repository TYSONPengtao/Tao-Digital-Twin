import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_16';BASE=Path('E:/jz/JIA/Rebuild_V26_15');O=Path('E:/jz/JIA/Rebuild_V26_16');SRC=BASE/'Blender/Architecture_Complete_V26_15.blend';P=O/'Blender/Architecture_Complete_V26_16.blend';prep=json.loads((D/'Prepared.json').read_text('utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(SRC)==prep['source_sha256']
for p in[P.parent,O/'Reports',O/'Sources',O/'Roam',O/'References',O/'Textures']:p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
col=bpy.data.collections.new('V26.16_局部修正原件存档');sc.collection.children.link(col);archives={};loaded={}
for r in prep['objects']:
 o=bpy.data.objects[r['name']];archive=o.copy();archive.data=o.data.copy();archive.name='V26_16_Previous_'+r['name'];col.objects.link(archive);archive.hide_render=True;archive.hide_set(True);archives[r['name']]=archive.name
 a=np.load(D/'Prepared'/r['file']);loaded[r['name']]=a;inv=o.matrix_world.inverted();me=bpy.data.meshes.new(r['name']+'_V26_16');me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'].astype(np.int64).tolist())
 for name in r['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.uv_layers.new(name='V26_16_Preserved_World_UV').data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o.data=me;o['V26_16_Correction']=r['reason']
for name in prep['archive']:
 o=bpy.data.objects[name]
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.hide_render=True;o.hide_set(True);archives[name]=name
cache=bpy.data.objects['V24_21_Navigation_Collision'];cm=cache.data;cm.calc_loop_triangles();cv=np.array([cache.matrix_world@v.co for v in cm.vertices]);cf=np.array([t.vertices[:]for t in cm.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_15_Collision_Index.json').read_text('utf8'))['objects'];vv=[];ff=[];ci=[];offset=0;first=0
for rr in ix:
 if rr['name']in prep['archive']:continue
 if rr['name']in loaded:v,f=loaded[rr['name']]['v'],loaded[rr['name']]['f'];reason='V26.16 corrected saved native geometry'
 else:
  f=cf[rr['first_triangle']:rr['first_triangle']+rr['triangles']];ids,rev=np.unique(f.ravel(),return_inverse=True);v=cv[ids];f=rev.reshape(-1,3);reason='Unchanged V26.15 collision data'
 vv.append(v);ff.append(f.astype(np.int64)+offset);ci.append({'name':rr['name'],'first_triangle':first,'triangles':len(f),'source':reason});offset+=len(v);first+=len(f)
cm=bpy.data.meshes.new('V26_16_Current_Collision');cm.from_pydata(np.vstack(vv),[],np.vstack(ff).astype(np.int64).tolist());cm.update();cache.data=cm;cache.matrix_world.identity();(O/'Reports/V26_16_Collision_Index.json').write_text(json.dumps({'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True},ensure_ascii=False),'utf8')
for name in ['start_roam.py','start_roam_fast.py','roam_controller.py','roam_controller_fast.py','roam_physics.py','measure_tools.py']:
 (O/'Roam'/name).write_text((BASE/'Roam'/name).read_text('utf8').replace('Rebuild_V26_15','Rebuild_V26_16').replace('Architecture_Complete_V26_15','Architecture_Complete_V26_16').replace('V26.15','V26.16').replace('V26_15_流畅显示','V26_16_流畅显示'),'utf8')
for text,name in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_25_测量工具.py','measure_tools.py')]:bpy.data.texts[text].clear();bpy.data.texts[text].write((O/'Roam'/name).read_text('utf8'))
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('V26_15','V26_16'),'utf8')
note=bpy.data.texts.new('V26_16_窗边收口修正');note.write('五组前房间内侧窗边节点：局部替换破碎梁头、窄墙边与窗台收口，保留200mm窗下墙和240mm房间隔墙；按原黑框端面留0.4mm收口，清除横档及窗台附近多余白块。统一窗顶水平面和侧面的原有涂层材质，消除三角拼接色块。三楼右侧飘窗按原房间完成顶面补齐连续封顶，与原结构合并，消除露出的屋面裁切尖片。将一楼两处窗角的阳台边板局部并入主体，裁掉低于室内完成顶面约2mm的外饰面，消除灰色三角露面，外侧阳台轮廓保持。原窗框、玻璃、开启扇动作、窗台高度、其他房间和V26.15已修正部位保持。尺寸为模型拟合，非新现场测量。')
sc['Version']='V26_16_Continuous_Front_Window_Jamb_Nodes';sc.frame_set(40);bpy.context.view_layer.update();changes={'source':str(SRC),'source_sha256':sha(SRC),'changed':list(loaded)+prep['archive']+[cache.name],'geometry_changed':list(loaded),'added':[a for n,a in archives.items()if n!=a],'archived':list(archives.values()),'archive_map':archives,'proof':prep['proof'],'runtime_version':'V26.16','active_user_window_not_replaced':True}
(O/'Reports/V26_16_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8');bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(O/'Reports/V26_16_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('V26_16_SAVED',sha(P),flush=True)
