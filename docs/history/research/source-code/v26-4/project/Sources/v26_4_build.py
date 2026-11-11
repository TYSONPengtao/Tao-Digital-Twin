from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_4';BASE=Path('E:/jz/JIA/Rebuild_V26_3');SRC=BASE/'Blender/Architecture_Complete_V26_3.blend';O=Path('E:/jz/JIA/Rebuild_V26_4');P=O/'Blender/Architecture_Complete_V26_4.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
assert sha(SRC)=='e257037e222d76990f3a644f11d8d3597071f1fcf849925e215aaa3a1e08eb68'
if not(D/'Before_Snapshot.json').exists():
 before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));rows=prep['objects'];changed=[];added=[];archive=set(prep['archive']);col=bpy.data.collections.new('V26_4_墙厚上限240_首层关系_三层实景平顶');sc.collection.children.link(col);ar=bpy.data.collections.new('V26_4_交接重合构件备份_隐藏');sc.collection.children.link(ar);ar.hide_render=True;ar.hide_viewport=True
for n in archive:
 o=bpy.data.objects[n]
 for c in list(o.users_collection):c.objects.unlink(o)
 ar.objects.link(o);o.hide_set(True);o.hide_render=True;changed.append(n)
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n);iv=o.matrix_world.inverted()if o else None;me=bpy.data.meshes.new(n+'_V26_4');me.from_pydata([iv@Vector(v)for v in a['v']]if o else a['v'],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_4_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True;me.update()
 if o:o.data=me;changed.append(n)
 else:o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 o['V26_4_Repair']=r['reason'];print('INSTALLED',n,len(a['f']),flush=True)
# Replace exactly the affected cache ranges. Exterior scan/ramp and the
# restored secondary screenwall remain the original collision surfaces.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_3_Collision_Index.json').read_text('utf8'))['objects'];need={r['name']for r in rows};edited=archive|need;vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in edited:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.3 actual surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.4 current saved native surface')
me=bpy.data.meshes.new('V26_4_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_4_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'archived_components_excluded':True,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_3','Rebuild_V26_4').replace('Architecture_Complete_V26_3.blend','Architecture_Complete_V26_4.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_3','Rebuild_V26_4').replace('Architecture_Complete_V26_3.blend','Architecture_Complete_V26_4.blend'),encoding='utf8')
sc['Version']='V26_4_240mm_Wall_Spans_F1_WC_Relations_F3_Photo_Flat_Ceiling';sc['V26_4_Source_SHA256']=sha(SRC)
text=bpy.data.texts.new('V26_4_本次优化说明');text.write('普通墙段厚度上限240mm；转角及原梁柱节点单独保留。首层楼梯对面卫生间与右侧卫生间保持两区、两个入口和100mm内隔墙，纠正过厚墙饰层及门套，清理楼梯与平台重合面。三层按实景160、212、218、235秒的白色平天花和梁下挂关系补足顶面；标高沿用原模型，不作为现场实测。外屋顶和次照壁保留。滑动门固定框、上亮及雨棚交接去重；所有门扇与动画保留。只提供Blender模型和原有漫游入口。')
write('V26_4_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'added':added,'archived':sorted(archive),'wall_limit_m':.24,'wall_corner_exception':True,'f1_room_basis':'User marked downa77d plan, two WC zones, distinct stair-facing and bedroom-facing entries','f3_ceiling_basis':'Actual INSV perspective images 160,212,218,235s; flat white ceiling with exposed beam drops, absolute heights inherited from model','secondary_screenwall':'All original V26.3 geometry, transforms, UVs, source photo fields and materials retained exactly','no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_4_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_4_SAVED',sha(P),flush=True)
