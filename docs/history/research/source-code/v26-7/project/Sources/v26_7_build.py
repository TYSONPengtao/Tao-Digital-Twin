from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_7';BASE=Path('E:/jz/JIA/Rebuild_V26_6');SRC=BASE/'Blender/Architecture_Complete_V26_6.blend';O=Path('E:/jz/JIA/Rebuild_V26_7');P=O/'Blender/Architecture_Complete_V26_7.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf8')
assert sha(SRC)=='ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));changed=[];added=[];geom=[]
for r in prep['objects']:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n)
 if o is None:
  o=bpy.data.objects.new(n,bpy.data.meshes.new(n));sc.collection.objects.link(o);added.append(n)
 smooth=bool(r.get('smooth_wood'))or any(p.use_smooth for p in o.data.polygons)
 iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V26_7');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_7_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if smooth:
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  if r.get('smooth_wood'):me.set_sharp_from_angle(angle=math.radians(38))
 me.update();o.data=me;o['V26_7_Repair']=r['reason'];changed.append(n);geom.append(n);print('INSTALLED',n,len(a['f']),flush=True)
sys.path.insert(0,str(W/'v26_7_site_audit'));from apply_site_materials import apply_site_material_repairs
matproof=apply_site_material_repairs();write('V26_7_Site_Material_Changes.json',matproof)
for row in matproof['outer_material_replacements']:changed.append(row['object'])
changed.append('V26_2_Continuous_Ground_And_Perimeter_Shell')
# Collision cache rebuilt from current visible native changed meshes only.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_6_Collision_Index.json').read_text('utf8'))['objects'];need=set(geom);vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.6 actual native surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.7 saved current native surface')
me=bpy.data.meshes.new('V26_7_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_7_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_6','Rebuild_V26_7').replace('Architecture_Complete_V26_6.blend','Architecture_Complete_V26_7.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,'utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_6','Rebuild_V26_7').replace('Architecture_Complete_V26_6.blend','Architecture_Complete_V26_7.blend'),'utf8')
sc['Version']='V26_7_Photo_Referenced_Wall_Column_Railing_Gate_And_Site_Repairs';sc['V26_7_Source_SHA256']=sha(SRC)
t=bpy.data.texts.new('V26_7_实景与截图修正');t.write('按实景修正各层旧柱芯和窗下凸块、楼梯井92.2mm楼层带；保留实景梁下挂、踏步和平台。红木扶手整理U形起步回弯、球下接头与斜柱帽，并补齐端部立杆节奏。内大门低石门槛按现有低院坪重新配合，门扇下沿同步延伸，门后角补齐现有走廊地面。院墙白腰线仅留照壁，其余青砖连续；清除次照壁旁重复斜檐装饰，原次照壁11构件不动。尺寸为原模型坐标上的实景关系拟合，未作现场测量。')
write('V26_7_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'geometry_changed':geom,'added':added,'archived':[],'wall_limit_m':.24,'wall_corner_exception':True,'specific_repair_proof':prep['proof'],'original_secondary_11':'Geometry transforms UVs materials and visibility retained exactly; only explicitly wrong lower site base finish is wrapped to matching strata','no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_7_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_7_SAVED',sha(P),flush=True)
