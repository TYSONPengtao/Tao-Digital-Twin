from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,math,shutil
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_11';BASE=Path('E:/jz/JIA/Rebuild_V26_10');SRC=BASE/'Blender/Architecture_Complete_V26_10.blend';O=Path('E:/jz/JIA/Rebuild_V26_11');P=O/'Blender/Architecture_Complete_V26_11.blend';R=O/'Reports'
for p in[P.parent,R,O/'Roam',O/'Sources',O/'References',O/'Textures']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(SRC)=='8ebd26627f8fe260a35dc476a1821b1670696e350e1890c7edf36776436fcb98'
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
sc.frame_set(40);bpy.context.view_layer.update();preps={k:json.loads((D/fn).read_text('utf8'))for k,fn in[('house','Prepared_House.json'),('storage','Prepared_Storage.json'),('gate','Prepared_Gate_Relief.json')]};rows=[q for p in preps.values()for q in p['objects']];archive=[n for p in preps.values()for n in p.get('archive',[])];changed=[];added=[]
atlas_src=Path(preps['gate']['proof']['height_atlas']);atlas_path=O/'Textures'/atlas_src.name;shutil.copy2(atlas_src,atlas_path);im=bpy.data.images.load(str(atlas_path),check_existing=False);im.name='V26_11_User_Reference_16bit_Gray_Height';im.colorspace_settings.name='Non-Color';im.use_fake_user=True;im.pack()
mat=bpy.data.materials['M_V21_GATE_REF_04'].copy();mat.name='M_V26_11_Reference_Gray_Carved_Stone';mat.use_nodes=True;nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');tex=nt.nodes.new('ShaderNodeTexImage');tex.name='User Reference Grayscale Height';tex.label='16位参考图灰度高度；已烘焙为真实隆起与下凹';tex.image=im;tex.interpolation='Linear';tex.extension='EXTEND';bump=nt.nodes.new('ShaderNodeBump');bump.name='Subgrid Stone Detail';bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0004;nt.links.new(tex.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);mat['Geometry_Already_Baked']=True
for rr in rows:
 n=rr['name'];a=np.load(D/rr['file']);o=bpy.data.objects.get(n)
 if o is None:o=bpy.data.objects.new(n,bpy.data.meshes.new(n));sc.collection.objects.link(o);added.append(n)
 me=bpy.data.meshes.new(n+'_V26_11');inv=o.matrix_world.inverted();me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'])
 for name in rr['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_11_Preserved_Or_Photo_Registered_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if rr.get('smooth_stone'):
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  # Smooth the sampled height field continuously. An angle threshold on
  # its interior grid produces artificial stair-step stripes on leaves.
  if not n.startswith('V26_11_Gate_Gray_Relief_'):me.set_sharp_from_angle(angle=math.radians(38))
 me.update();o.data=me;o['V26_11_Repair']=rr['reason'];changed.append(n)
 if rr.get('non_collision_detail'):o['Gray_Height_Image']=im.name;o['Signed_Relief_Baked']=True
 print('INSTALLED',n,len(a['f']),flush=True)
for n in archive:o=bpy.data.objects[n];o.hide_render=True;o.hide_set(True);o['V26_11_Archived_Original']=True;changed.append(n)
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;old.calc_loop_triangles();cv=np.empty(len(old.vertices)*3,np.float32);old.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in old.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_10_Collision_Index.json').read_text('utf8'))['objects'];need={r['name']for r in rows if not r.get('non_collision_detail')};vv=[];ff=[];ci=[];offset=0;first=0
def append(v,f,n,kind):
 global offset,first
 vv.append(v);ff.append(f+offset);ci.append({'name':n,'first_triangle':first,'triangles':len(f),'source':kind});offset+=len(v);first+=len(f)
for rr in ix:
 if rr['name']in need or rr['name']in archive:continue
 fs=cf[rr['first_triangle']:rr['first_triangle']+rr['triangles']];used,rev=np.unique(fs.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),rr['name'],'Unchanged V26.10 saved collision surface')
for n in sorted(need):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();append(np.array([o.matrix_world@v.co for v in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles],np.int32),n,'Current V26.11 saved native geometry at40')
me=bpy.data.meshes.new('V26_11_Current_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);(R/'V26_11_Collision_Index.json').write_text(json.dumps({'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True},ensure_ascii=False),'utf8')
for txt,fn in[('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string().replace('Rebuild_V26_10','Rebuild_V26_11').replace('Architecture_Complete_V26_10','Architecture_Complete_V26_11');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code);(O/'Roam'/fn).write_text(code,'utf8')
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_10','Rebuild_V26_11').replace('Architecture_Complete_V26_10','Architecture_Complete_V26_11'),'utf8')
for image in bpy.data.images:
 if image.source!='VIEWER'and image.type not in['RENDER_RESULT','COMPOSITING']:image.use_fake_user=True
for ac in bpy.data.actions:ac.use_fake_user=True
sc['Version']='V26_11_Beam_Seats_Cap_Materials_Rectangular_F1_Porch_Photo_Gray_Relief_And_Storage_Brick_Closure';sc.frame_set(40);bpy.context.view_layer.update()
text=bpy.data.texts.new('V26_11_修正说明');text.write('梁端：上轮墙身截面裁切误入梁高，一二楼按原梁底标高接回完整梁端；三楼保持既有平顶要求。地脚白片：清理50–200微米封口余量，地面回接原地面UV和材质，顶面封口改回顶面材质。入口：一楼平台按二楼四边形XY边界补齐并与原楼板合并。一阶高差保留。门楼：用户参考图分区校正、16位灰度高度图、21块带正负深度的闭合网格浮雕和14mm真实凹槽，原石画保留于隐藏可编辑对象。储藏房：斜屋面下梯形青砖封口，接原山墙和屋面，清除无砖墙承托的白色饰面，旧装饰檐板存档，主体木构与屋顶保留。阴天柔光与流畅配置继承。')
changes={'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'geometry_changed':[r['name']for r in rows],'added':added,'archived':archive,'proof':{k:p['proof']for k,p in preps.items()},'new_images':[im.name],'new_materials':[mat.name],'source_core_and_previous_gate_pictures_archived_editably':True,'ordinary_wall_max_m':.24,'original_secondary_11':'Exact original geometry UV materials and visibility retained','no_rhino_export':True}
(R/'V26_11_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8');bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(R/'V26_11_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('V26_11_SAVED',sha(P),flush=True)
