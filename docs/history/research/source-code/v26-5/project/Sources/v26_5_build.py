from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_5';BASE=Path('E:/jz/JIA/Rebuild_V26_4');SRC=BASE/'Blender/Architecture_Complete_V26_4.blend';O=Path('E:/jz/JIA/Rebuild_V26_5');P=O/'Blender/Architecture_Complete_V26_5.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert sha(SRC)=='c5f5465eea815fa3c3545855b25036629ed2a5ceda091ac6f2c6850fd4b81663'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));rows=prep['objects'];changed=[]
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects[n];iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V26_5');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_5_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True;me.update();o.data=me;o['V26_5_Repair']=r['reason'];changed.append(n);print('INSTALLED',n,len(a['f']),flush=True)
# Rebuild only collision source ranges actually changed by this local repair.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_4_Collision_Index.json').read_text('utf8'))['objects'];need=set(changed);vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.4 actual surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.5 saved current native surface')
me=bpy.data.meshes.new('V26_5_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_5_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_4','Rebuild_V26_5').replace('Architecture_Complete_V26_4.blend','Architecture_Complete_V26_5.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_4','Rebuild_V26_5').replace('Architecture_Complete_V26_4.blend','Architecture_Complete_V26_5.blend'),encoding='utf8')
sc['Version']='V26_5_F1_Rear_WC_Window_Junctions_Facade_Bands_Bay_Fin_Clearance';sc['V26_5_Source_SHA256']=sha(SRC)
text=bpy.data.texts.new('V26_5_本次局部修正');text.write('对应2026-10-24五张问题截图：首层后墙在原柱间连续收平，厚220.2mm；卫生间100mm隔墙接入后墙，窗台窗头不得穿过隔墙；首层三个后高窗窗头封齐；西院墙瓦顶临飘窗端局部裁切，保留原窗框玻璃与次照壁；补接一二楼东、西、后侧外墙与楼板边缘，仅限外墙带不封楼梯井；清理五组飘窗正斜面转角多余白色残片。原玻璃、门窗动画、梁柱、三楼白色天花、次照壁和入口坡保留。')
write('V26_5_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(changed),'added':[],'archived':[],'wall_limit_m':.24,'wall_corner_exception':True,'specific_repair_proof':prep['proof'],'secondary_screenwall':'All original geometry, placement, photo mapping and source height field untouched','no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_5_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_5_SAVED',sha(P),flush=True)
