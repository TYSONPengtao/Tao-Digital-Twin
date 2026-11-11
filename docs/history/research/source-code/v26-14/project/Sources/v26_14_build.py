import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_14';BASE=Path('E:/jz/JIA/Rebuild_V26_13');O=Path('E:/jz/JIA/Rebuild_V26_14');SRC=BASE/'Blender/Architecture_Complete_V26_13.blend';P=O/'Blender/Architecture_Complete_V26_14.blend';prep=json.loads((D/'Prepared.json').read_text('utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(SRC)==prep['proof']['source_sha256']
for p in[P.parent,O/'Reports',O/'Sources',O/'Roam',O/'References',O/'Textures']:p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
HN='V26_3_House_Connected_Walls_And_Stairs';o=bpy.data.objects[HN];archive=o.copy();archive.data=o.data.copy();archive.name='V26_14_Previous_WC_Wall_Returns_Archive';col=bpy.data.collections.new('V26.14_墙角原件存档');sc.collection.children.link(col);col.objects.link(archive);archive.hide_render=True;archive.hide_set(True)
r=prep['objects'][0];a=np.load(D/r['file']);inv=o.matrix_world.inverted();me=bpy.data.meshes.new(HN+'_V26_14');me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'].tolist())
for name in r['materials']:me.materials.append(bpy.data.materials[name])
me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.uv_layers.new(name='V26_14_Preserved_World_UV').data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o.data=me;o['V26_14_Correction']='Four actual WC L-return faces aligned; local bonded geometry, not an overlay'
cache=bpy.data.objects['V24_21_Navigation_Collision'];cm=cache.data;cm.calc_loop_triangles();cv=np.array([cache.matrix_world@v.co for v in cm.vertices]);cf=np.array([t.vertices[:]for t in cm.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_13_Collision_Index.json').read_text('utf8'))['objects'];vv=[];ff=[];ci=[];offset=0;first=0
for rr in ix:
 if rr['name']==HN:v,f=a['v'],a['f'];reason='V26.14 saved house with four flush WC returns'
 else:
  f=cf[rr['first_triangle']:rr['first_triangle']+rr['triangles']];ids,rev=np.unique(f.ravel(),return_inverse=True);v=cv[ids];f=rev.reshape(-1,3);reason='Unchanged V26.13 collision data'
 vv.append(v);ff.append(f+offset);ci.append({'name':rr['name'],'first_triangle':first,'triangles':len(f),'source':reason});offset+=len(v);first+=len(f)
cm=bpy.data.meshes.new('V26_14_Current_Collision');cm.from_pydata(np.vstack(vv),[],np.vstack(ff).astype(np.int64).tolist());cm.update();cache.data=cm;cache.matrix_world.identity();(O/'Reports/V26_14_Collision_Index.json').write_text(json.dumps({'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True},ensure_ascii=False),'utf8')
for name in ['start_roam.py','start_roam_fast.py','roam_controller.py','roam_controller_fast.py','roam_physics.py','measure_tools.py']:
 (O/'Roam'/name).write_text((BASE/'Roam'/name).read_text('utf8').replace('Rebuild_V26_13','Rebuild_V26_14').replace('Architecture_Complete_V26_13','Architecture_Complete_V26_14').replace('V26.13','V26.14').replace('V26_13_流畅显示','V26_14_流畅显示'),'utf8')
for text,name in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_25_测量工具.py','measure_tools.py')]:bpy.data.texts[text].clear();bpy.data.texts[text].write((O/'Roam'/name).read_text('utf8'))
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('V26_13','V26_14'),'utf8')
note=bpy.data.texts.new('V26_14_房间卫浴墙角修正');note.write('房间卫生间交接：原前墙端面X2.20/10.80与门边侧墙外饰面X2.29/10.71错开90mm，产生通高竖棱和梁头台阶。将一二楼左侧、二三楼右侧四处L形交点的前墙端面接到原门边侧墙饰面，局部实体并入原墙，不叠盖白片。原门洞、门套、门扇及动作、层高、地面、顶板、楼梯、大门雕刻均保留。尺寸为模型与既有实景关系拟合，并非现场新测。')
sc['Version']='V26_14_Four_Flush_WC_L_Returns';sc.frame_set(40);bpy.context.view_layer.update();changes={'source':str(SRC),'source_sha256':sha(SRC),'changed':[HN,cache.name],'geometry_changed':[HN],'added':[archive.name],'archived':[archive.name],'proof':prep['proof'],'runtime_version':'V26.14','active_user_window_not_replaced':True}
(O/'Reports/V26_14_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8');bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(O/'Reports/V26_14_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('V26_14_SAVED',sha(P),flush=True)
