from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math
from mathutils import Vector,Matrix
W=Path(__file__).parent;D=W/'v26_10';BASE=Path('E:/jz/JIA/Rebuild_V26_9');SRC=BASE/'Blender/Architecture_Complete_V26_9.blend';O=Path('E:/jz/JIA/Rebuild_V26_10');P=O/'Blender/Architecture_Complete_V26_10.blend';R=O/'Reports'
for p in[P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf8')
assert sha(SRC)=='854c6dff5c5582a506725a0187292401bb05ad0f77d75f5b2f0238e945879c70'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));rail=json.loads((W/'v26_10_railing/Prepared_Railing.json').read_text('utf8'));rr=rail['objects'][0];rr['file']=str((W/'v26_10_railing'/rr['file']).resolve());prep['objects'].append(rr);changed=[];added=[];geom=[]
for r in prep['objects']:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n)
 if o is None:o=bpy.data.objects.new(n,bpy.data.meshes.new(n));sc.collection.objects.link(o);added.append(n)
 me=bpy.data.meshes.new(n+'_V26_10');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_10_Preserved_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if r.get('smooth_wood')or r.get('smooth_stone'):
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool));me.set_sharp_from_angle(angle=math.radians(38))
 me.update();o.data=me;o['V26_10_Repair']=r['reason'];changed.append(n);geom.append(n);print('INSTALLED',n,len(a['f']),flush=True)
for r in prep['rigid_transforms']:
 o=bpy.data.objects[r['name']];o.matrix_world=Matrix(r['matrix_world_left_multiply'])@o.matrix_world;changed.append(o.name);print('RIGID',o.name,flush=True)
for n in prep['remove']:
 o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True);changed.append(n)
sc.frame_set(40);bpy.context.view_layer.update()
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32)
ix=json.loads((BASE/'Reports/V26_9_Collision_Index.json').read_text('utf8'))['objects'];need=set(geom)-{r['name']for r in prep['objects']if r.get('smooth_stone')};archived=set(prep['remove']);vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need or r['name']in archived:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.9 saved surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.10 current native surface at40')
me=bpy.data.meshes.new('V26_10_Current_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_10_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_9','Rebuild_V26_10').replace('Architecture_Complete_V26_9','Architecture_Complete_V26_10');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,'utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_9','Rebuild_V26_10').replace('Architecture_Complete_V26_9','Architecture_Complete_V26_10'),'utf8')
for im in bpy.data.images:
 if im.source!='VIEWER'and im.type not in ['RENDER_RESULT','COMPOSITING']:im.use_fake_user=True
for ac in bpy.data.actions:ac.use_fake_user=True
sc['Version']='V26_10_Wall_Plane_Intersections_Level_F3_Rail_And_Detailed_Rectangular_Gate'
t=bpy.data.texts.new('V26_10_修正说明');t.write('房间与卫生间交角：清理旧柱块残留，按相邻墙面定位重接，共11个局部节点；卫生间18cm分隔墙及24cm前墙延续，房间隔墙24cm延续，门洞保留。三楼后侧两柱头同高，柱间握柄改为水平直线，原四跑及半转弯不变。内门楼改矩形深柱，原正面与横楣雕刻不动，原窄侧石画刚体转放侧面，无拉伸；增加上部花叶分格的闭合真实网格浮雕、腰线、外扩柱础，入口平台连两侧柱础形成一阶，门洞与开合保留。阴天与流畅配置继承。')
write('V26_10_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'geometry_changed':geom,'added':added,'archived':prep['remove'],'rigid_transforms':prep['rigid_transforms'],'proof':prep['proof'],'railing_proof':rail['proof'],'ordinary_wall_max_m':.24,'original_secondary_11':'Exact source geometry UV materials and visibility retained','previous_fixes_inherited':True,'no_rhino_export':True})
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_10_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_10_SAVED',sha(P),flush=True)
