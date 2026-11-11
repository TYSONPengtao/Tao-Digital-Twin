from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_9';BASE=Path('E:/jz/JIA/Rebuild_V26_8');SRC=BASE/'Blender/Architecture_Complete_V26_8.blend';O=Path('E:/jz/JIA/Rebuild_V26_9');P=O/'Blender/Architecture_Complete_V26_9.blend';R=O/'Reports'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),'utf8')
assert sha(SRC)=='e21a89f9b617a541790a383295266e852182c6b915559cddf93d070e7137da72'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
prep=json.loads((D/'Prepared_All_Geometry.json').read_text('utf8'));rail=json.loads((W/'v26_9_railing/Prepared_Railing.json').read_text('utf8'));rr=rail['objects'][0];rr['file']=str((W/'v26_9_railing'/rr['file']).resolve());prep['objects'].append(rr)
changed=[];added=[];geom=[]
for r in prep['objects']:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n)
 if o is None:
  o=bpy.data.objects.new(n,bpy.data.meshes.new(n));sc.collection.objects.link(o);added.append(n)
 smooth=bool(r.get('smooth_wood'))or any(p.use_smooth for p in o.data.polygons)
 iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V26_9');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_9_Source_And_Metric_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if smooth:
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  if r.get('smooth_wood'):me.set_sharp_from_angle(angle=math.radians(38))
 me.update();o.data=me;o['V26_9_Repair']=r['reason'];changed.append(n);geom.append(n);print('INSTALLED',n,len(a['f']),flush=True)

# New rear sashes translate horizontally in the same1..40 timeline used
# by the existing window/door controls. Keep source object transforms.
for r in prep['new_sliding_animations']:
 o=bpy.data.objects[r['object']]
 for fr,dx in [(1,0.),(40,r['open_translation_m']),(60,0.),(80,r['alternate_open_translation_m']),(100,0.)]:
  o.location.x=dx;o.keyframe_insert(data_path='location',index=0,frame=fr)
 o['V26_9_Sliding_Window']=True;o['Track_Center_Y_m']=r['track_center_y_m']
 if o.animation_data and o.animation_data.action:
  o.animation_data.action.name='V26_9_Slide_'+o.name
sc.frame_end=100;sc.frame_set(40);bpy.context.view_layer.update()

# The crescent on the roof is the disk of the overcast area light crossing
# the lower canopy plane. Place the complete disk below its lowest edge.
ln='V26_8_Overcast_Interior_F3_left';light=bpy.data.objects[ln];old_light_z=light.location.z;light.location.z=9.50;changed.append(ln)
for k,y in enumerate([-4.,-7.,-10.],1):
 ld=bpy.data.lights.new('V26_9_Overcast_Kitchen_Fill_'+str(k),'POINT');ld.energy=45.;ld.shadow_soft_size=2.;ob=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(ob);ob.location=(11.7,y,2.35);added.append(ob.name);changed.append(ob.name)
write('V26_9_Roof_White_Fragment_Diagnosis.json',{'cause':'Area emitter crossed the sloping low terrace canopy; camera rays hit unchanged canopy rather than a stray white mesh','ray_evidence':json.loads((D/'Fragment_Raycast.json').read_text('utf8')),'light':ln,'old_center_z_m':old_light_z,'new_center_z_m':light.location.z,'canopy_minimum_z_m':9.720000267,'light_energy_and_diameter_unchanged':True,'canopy_geometry_and_material_unchanged':True})

# Update the actual collision cache, preserving old source membership and
# adding the twenty physical rear sashes, not decorative relief surfaces.
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32)
ix=json.loads((BASE/'Reports/V26_8_Collision_Index.json').read_text('utf8'))['objects'];old_names={r['name']for r in ix};need=(set(geom)&old_names)|{r['object']for r in prep['new_sliding_animations']};vv=[];ff=[];ci=[];off=0;first=0
def append(v,f,n,kind):
 global off,first
 vv.append(v);ff.append(f+off);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});off+=len(v);first+=len(f)
for r in ix:
 if r['name']in need:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.8 native surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'V26.9 actual current native surface at frame40')
me=bpy.data.meshes.new('V26_9_Current_Geometry_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);write('V26_9_Collision_Index.json',{'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True})

for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_8','Rebuild_V26_9').replace('Architecture_Complete_V26_8.blend','Architecture_Complete_V26_9.blend');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,'utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_8','Rebuild_V26_9').replace('Architecture_Complete_V26_8','Architecture_Complete_V26_9'),'utf8')
sc['Version']='V26_9_Photo_Referenced_Windows_Local_Construction_And_Gate';sc['V26_9_Source_SHA256']=sha(SRC)
for image in bpy.data.images:
 if image.type!='RENDER_RESULT' and image.type!='COMPOSITING':image.use_fake_user=True
for action in bpy.data.actions:action.use_fake_user=True
t=bpy.data.texts.get('V26_9_修正说明')or bpy.data.texts.new('V26_9_修正说明');t.write('一楼新增下部独立固定玻璃，开启扇缩短，30cm实墙窗脚保留；二三楼窗台下调100mm，开启扇下面为实墙，斜窗脚补齐。实景存在的门侧柱垛保留，削除多包的饰面。三楼露台开口残余顶梁移除，水平通道木栏降低150mm，其余楼梯斜握柄和100mm梯井保留。阳台边带补成完整四边。厨房北山墙恢复此前被内退280mm的外侧位置，180mm墙身与200mm转角接回，避免墙木相穿。石栏端部接次照壁，两房外角青砖收口。内大门门楣和门头提高400mm，压缩大块素面留白，原雕刻石画全部保留；横楣雕刻只整体平移，侧柱石画不变形。屋后9樘窗改为双轨水平推拉，共20扇。雨棚上白月牙是圆形补光灯露出棚顶，灯移至棚下。尺寸除用户给定30cm外属于实景与原模型关系拟合，非现场测绘。')
write('V26_9_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'geometry_changed':geom,'added':added,'archived':[],'wall_limit_m':.24,'wall_corner_and_retained_core_exception':True,'specific_repair_proof':prep['proof'],'railing_proof':rail['proof'],'new_sliding_animations':prep['new_sliding_animations'],'original_secondary_11':'Exact geometry, transforms, UVs, materials and visibility retained','overcast_lighting_preserved':True,'no_rhino_export':True})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_9_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string});print('V26_9_SAVED',sha(P),flush=True)
