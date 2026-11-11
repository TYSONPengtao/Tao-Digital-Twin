import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_15';BASE=Path('E:/jz/JIA/Rebuild_V26_14');O=Path('E:/jz/JIA/Rebuild_V26_15');SRC=BASE/'Blender/Architecture_Complete_V26_14.blend';P=O/'Blender/Architecture_Complete_V26_15.blend';prep=json.loads((D/'Prepared.json').read_text('utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(SRC)==prep['source_sha256']
for p in[P.parent,O/'Reports',O/'Sources',O/'Roam',O/'References',O/'Textures']:p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
col=bpy.data.collections.new('V26.15_局部修正原件存档');sc.collection.children.link(col);archives={};loaded={}
for r in prep['objects']:
 o=bpy.data.objects[r['name']];archive=o.copy();archive.data=o.data.copy();archive.name='V26_15_Previous_'+r['name'];col.objects.link(archive);archive.hide_render=True;archive.hide_set(True);archives[r['name']]=archive.name
 a=np.load(D/'Prepared'/r['file']);loaded[r['name']]=a;inv=o.matrix_world.inverted();me=bpy.data.meshes.new(r['name']+'_V26_15');me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'].astype(np.int64).tolist())
 for name in r['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.uv_layers.new(name='V26_15_Preserved_World_UV').data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o.data=me;o['V26_15_Correction']=r['reason']
for name in prep['archive']:
 o=bpy.data.objects[name]
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);o.hide_render=True;o.hide_set(True);archives[name]=name
cache=bpy.data.objects['V24_21_Navigation_Collision'];cm=cache.data;cm.calc_loop_triangles();cv=np.array([cache.matrix_world@v.co for v in cm.vertices]);cf=np.array([t.vertices[:]for t in cm.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_14_Collision_Index.json').read_text('utf8'))['objects'];vv=[];ff=[];ci=[];offset=0;first=0
for rr in ix:
 if rr['name']in prep['archive']:continue
 if rr['name']in loaded:v,f=loaded[rr['name']]['v'],loaded[rr['name']]['f'];reason='V26.15 corrected saved native geometry'
 else:
  f=cf[rr['first_triangle']:rr['first_triangle']+rr['triangles']];ids,rev=np.unique(f.ravel(),return_inverse=True);v=cv[ids];f=rev.reshape(-1,3);reason='Unchanged V26.14 collision data'
 vv.append(v);ff.append(f.astype(np.int64)+offset);ci.append({'name':rr['name'],'first_triangle':first,'triangles':len(f),'source':reason});offset+=len(v);first+=len(f)
cm=bpy.data.meshes.new('V26_15_Current_Collision');cm.from_pydata(np.vstack(vv),[],np.vstack(ff).astype(np.int64).tolist());cm.update();cache.data=cm;cache.matrix_world.identity();(O/'Reports/V26_15_Collision_Index.json').write_text(json.dumps({'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True},ensure_ascii=False),'utf8')
for name in ['start_roam.py','start_roam_fast.py','roam_controller.py','roam_controller_fast.py','roam_physics.py','measure_tools.py']:
 (O/'Roam'/name).write_text((BASE/'Roam'/name).read_text('utf8').replace('Rebuild_V26_14','Rebuild_V26_15').replace('Architecture_Complete_V26_14','Architecture_Complete_V26_15').replace('V26.14','V26.15').replace('V26_14_流畅显示','V26_15_流畅显示'),'utf8')
for text,name in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_25_测量工具.py','measure_tools.py')]:bpy.data.texts[text].clear();bpy.data.texts[text].write((O/'Roam'/name).read_text('utf8'))
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('V26_14','V26_15'),'utf8')
note=bpy.data.texts.new('V26_15_重面与局部接合修正');note.write('门廊旧地面与四边平台重叠：局部实体合并，归属单一表面。楼梯西前角两块楼板补洞凸块：仅将超出原墙线的190×190×130mm部分裁回原墙面。储藏房门洞固定残余细木片：删除6个三角面。内大门后地面：从旧补地边延伸至真实墙根，与邻地面同标高，合并为实体支撑。所有尺寸为既有模型边界拟合，并非新现场测量。当前用户Blender未保存窗口未替换。')
sc['Version']='V26_15_Four_Local_Geometry_Joins';sc.frame_set(40);bpy.context.view_layer.update();changes={'source':str(SRC),'source_sha256':sha(SRC),'changed':list(loaded)+prep['archive']+[cache.name],'geometry_changed':list(loaded),'added':[a for n,a in archives.items()if n!=a],'archived':list(archives.values()),'archive_map':archives,'proof':prep['proof'],'runtime_version':'V26.15','active_user_window_not_replaced':True}
(O/'Reports/V26_15_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8');bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(O/'Reports/V26_15_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('V26_15_SAVED',sha(P),flush=True)
