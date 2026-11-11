"""Restore V24's actual stone-carving surfaces into the current gate."""
from pathlib import Path
import bpy, numpy as np, json, hashlib, sys, shutil
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
import v24_qa_blender as q
from v24_06_common import snapshot
from v26_12_fast_display import set_local_ao
D=W/'v26_12';D.mkdir(exist_ok=True)
OLD=Path('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend')
BASE=Path('E:/jz/JIA/Rebuild_V26_11')
SRC=BASE/'Blender/Architecture_Complete_V26_11.blend'
O=Path('E:/jz/JIA/Rebuild_V26_12');P=O/'Blender/Architecture_Complete_V26_12.blend'
for path in[P.parent,O/'Reports',O/'Sources',O/'Roam',O/'Textures',O/'References']:
 path.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def topology_uv_hash(me):
 h=hashlib.sha256()
 for seq,key,n,dt in[(me.loops,'vertex_index',1,np.int32),(me.polygons,'loop_start',1,np.int32),(me.polygons,'loop_total',1,np.int32),(me.polygons,'material_index',1,np.int32),(me.polygons,'use_smooth',1,np.bool_)]:h.update(q._bulk(seq,key,n,dt).tobytes())
 for uv in me.uv_layers:h.update(q._bulk(uv.data,'uv',2).tobytes())
 h.update(json.dumps([m.name if m else None for m in me.materials]).encode());return h.hexdigest()
assert sha(SRC)=='22cb029f59c8acfba426c18a8bd907a6757381543ececebb7883f72ef248c520'
assert sha(OLD)=='303bef3310e5f65d55d1c2f1cd9014b77f1e21f69fcf07222fb2675e2b00183e'
bpy.ops.wm.open_mainfile(filepath=str(OLD));originals={};reference_positions={};reference_meshes={}
for ob in bpy.data.objects:
 if ob.type!='MESH'or not ob.name.startswith('V24_Gate_Reference_Relief_'):continue
 info={'mesh_hash':q._mesh_hash(ob.data),'matrix':q._matrix(ob.matrix_world),'topology_uv_hash':topology_uv_hash(ob.data),'header_translation_m':.4 if 'Header'in ob.name else 0.}
 reference_positions[ob.name]=q._bulk(ob.data.vertices,'co',3,np.float64).reshape(-1,3)
 me=ob.data
 reference_meshes[ob.name]={'loops':q._bulk(me.loops,'vertex_index',1,np.int32),'start':q._bulk(me.polygons,'loop_start',1,np.int32),'total':q._bulk(me.polygons,'loop_total',1,np.int32),'mi':q._bulk(me.polygons,'material_index',1,np.int32),'smooth':q._bulk(me.polygons,'use_smooth',1,np.bool_),'uvs':[(uv.name,q._bulk(uv.data,'uv',2))for uv in me.uv_layers],'materials':[m.name for m in me.materials]}
 originals[ob.name]=info
assert len(originals)==15
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
col=bpy.data.collections.new('V26.12_内大门_V24原浮雕');sc.collection.children.link(col)
panels=[];old_names=list(originals)+sorted(o.name for o in bpy.data.objects if o.name.startswith('V26_10_Gate_Upper_Relief_'))
assert len(old_names)==21
for old_name in old_names:
 old=bpy.data.objects[old_name]
 if old_name in originals:
  info=originals[old_name];vref=reference_positions[old_name].copy();vref[:,2]+=info['header_translation_m'];cur=q._bulk(old.data.vertices,'co',3,np.float64).reshape(-1,3)
  info['reference_alignment_error_m']=float(abs(cur-vref).max());info['aligned_mesh_hash']=q._mesh_hash(old.data)
  assert info['reference_alignment_error_m']<.000002,(old_name,info['reference_alignment_error_m'])
  ref=reference_meshes[old_name];me=old.data;differences=[]
  for key,seq,attr,n,dt in[('loops',me.loops,'vertex_index',1,np.int32),('start',me.polygons,'loop_start',1,np.int32),('total',me.polygons,'loop_total',1,np.int32),('mi',me.polygons,'material_index',1,np.int32),('smooth',me.polygons,'use_smooth',1,np.bool_)]:
   curdata=q._bulk(seq,attr,n,dt)
   if not np.array_equal(curdata,ref[key]):differences.append(key)
  for name,uv in ref['uvs']:
   found=me.uv_layers.get(name)
   if not found or not np.array_equal(q._bulk(found.data,'uv',2),uv):differences.append('uv:'+name)
  if [m.name for m in me.materials]!=ref['materials']:differences.append('materials')
  info['later_archive_attribute_differences']=differences
  print('V24_REFERENCE_ATTRIBUTES',old_name,differences,flush=True)
 new=old.copy();new.data=old.data.copy();new.name='V26_12_Restored_'+old_name
 if old_name in originals:
  # Read the actual V24 topology and UVs, not the later archive's display flags.
  ref=reference_meshes[old_name];me=bpy.data.meshes.new(new.name+'_V24_Source')
  faces=[ref['loops'][start:start+total].tolist()for start,total in zip(ref['start'],ref['total'])]
  me.from_pydata(vref,[],faces)
  for name in ref['materials']:me.materials.append(bpy.data.materials[name])
  me.polygons.foreach_set('material_index',ref['mi']);me.polygons.foreach_set('use_smooth',ref['smooth'])
  for name,uv in ref['uvs']:me.uv_layers.new(name=name).data.foreach_set('uv',uv)
  me.update();new.data=me
 new.data.name=new.name+'_Baked';new.modifiers.clear();new.animation_data_clear();col.objects.link(new)
 new.hide_viewport=False;new.hide_render=False;new.hide_set(False)
 if 'V26_11_Archived_Original'in new:del new['V26_11_Archived_Original']
 new['V26_12_Source_Object']=old_name;new['V26_12_Source_Model']=str(OLD if old_name in originals else BASE/'Blender/Architecture_Complete_V26_11.blend')
 v=q._world(new.data,new.matrix_world)
 if 'Header'in old_name:inside=np.array([0.,1.,0.]);origin=np.array([0.,-11.80300045,0.]);face='header'
 elif '_front'in old_name:inside=np.array([0.,1.,0.]);origin=np.array([0.,-11.87,0.]);face='front'
 else:
  pi=1 if '_P1_'in old_name else 2
  x0,x1=([(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)])[pi-1]
  face='left'if '_left'in old_name else'right'
  inside=np.array([1.,0.,0.])if face=='left'else np.array([-1.,0.,0.]);origin=np.array([x0 if face=='left'else x1,0.,0.])
 depth=(v-origin)@inside;back=np.abs(depth-depth.max())<.000002
 assert back.any()and (~back).sum()>1000
 # The original sculpted front is translated as a whole, preserving its
 # actual V24 height differences. Its valleys now sit2mm into the field.
 shift=.002-float(depth[~back].max());v[~back]+=inside*shift
 v[back]+=inside*(.016-depth[back])[:,None]
 # Fit the two narrow45-degree source fields to the present flat side.
 # Relief heights and vertical stationing stay unchanged.
 width_fit=None
 if face in['left','right']:
  lo,hi=float(v[:,1].min()),float(v[:,1].max());v[:,1]=-11.7125+(v[:,1]-lo)/(hi-lo)*.085
  width_fit={'source_y_m':[lo,hi],'target_y_m':[-11.7125,-11.6275]}
 inv=np.linalg.inv(np.asarray(new.matrix_world));local=v@inv[:3,:3].T+inv[:3,3]
 new.data.vertices.foreach_set('co',local.astype(np.float32).ravel());new.data.update()
 new['V26_12_Actual_V24_Height_Differences_Preserved']=True
 new['V26_12_No_Live_Subdivision']=True
 panel={'name':new.name,'source_object':old_name,'source_is_original_V24':old_name in originals,
        'source_mesh_hash':q._mesh_hash(old.data),'source_matrix':q._matrix(old.matrix_world),
        'target_topology_uv_hash':topology_uv_hash(new.data),
        'inside':inside.tolist(),'origin':origin.tolist(),'front_rigid_inward_shift_m':shift,
        'back_seating_m':.016,'core_recess_depth_m':.014,'original_front_vertex_ids':np.flatnonzero(~back).tolist(),
        'width_fit':width_fit,'base_vertices':len(v),'triangles':sum(len(f.vertices)-2 for f in new.data.polygons),
        'outward_range_m':[-float(((v-origin)@inside)[~back].max()),-float(((v-origin)@inside)[~back].min())]}
 panels.append(panel);print('RESTORED_V24',new.name,panel['outward_range_m'],flush=True)
archived=[]
for ob in list(bpy.data.objects):
 if ob.name.startswith('V26_11_Gate_Gray_Relief_'):
  ob.hide_render=True;ob.hide_set(True);ob['V26_12_Archived_Low_Resolution_Photo_Relief']=True;archived.append(ob.name)
assert len(archived)==21
# The original waist, current structural piers, threshold and collision cache
# remain byte-for-byte unchanged. Only visual carving inserts are restored.
for name in ['start_roam.py','roam_controller.py','roam_physics.py','measure_tools.py','start_roam_fast.py','roam_controller_fast.py']:
 src=BASE/'Roam'/name
 if src.exists():(O/'Roam'/name).write_text(src.read_text('utf8').replace('Rebuild_V26_11','Rebuild_V26_12').replace('Architecture_Complete_V26_11','Architecture_Complete_V26_12'),'utf8')
for name in ['roam_controller.py','roam_controller_fast.py']:
 path=O/'Roam'/name;code=path.read_text('utf8').replace("'1.65m 漫游人物  ·  '","'V26.12  ·  1.65m 漫游人物  ·  '")
 code=code.replace("PRESETS={'COURT':", "PRESETS={'INNER_GATE':(6.6,-10.9,-.6),'COURT':")
 path.write_text(code,'utf8')
for name in ['start_roam.py','start_roam_fast.py']:
 path=O/'Roam'/name;code=path.read_text('utf8')
 code=code.replace("print('ARCH_ROAM_LAUNCHER_READY:","if control._running is not None:\n     control._running.walker.place(control.PRESETS['INNER_GATE']);control._running.camera_pos=None;control._running._input_dirty=True\n    print('ARCH_ROAM_LAUNCHER_READY:")
 path.write_text(code,'utf8')
for text,name in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_25_测量工具.py','measure_tools.py')]:
 bpy.data.texts[text].clear();bpy.data.texts[text].write((O/'Roam'/name).read_text('utf8'))
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_11','Rebuild_V26_12').replace('Architecture_Complete_V26_11','Architecture_Complete_V26_12'),'utf8')
for im in bpy.data.images:
 if im.source!='VIEWER'and im.type not in['RENDER_RESULT','COMPOSITING']:im.use_fake_user=True
sc['Version']='V26_12_Restored_Actual_V24_Gate_Sculpt'
set_local_ao(sc)
sc['V26_12_Source_SHA256']=sha(SRC);sc['V26_12_V24_Reference_SHA256']=sha(OLD)
note=bpy.data.texts.new('V26_12_门楼修正说明')
note.write('恢复Architecture_Complete_V24.blend的15块真实雕刻网格，保留其竹叶、花卉、枝叶和门楣纹样。沿用6块采自V24高度图的上部石画，适配当前矩形柱侧面。原浮雕正面整体内移至谷部低于基面2mm，起伏差保持；背面延伸至16mm，接入14mm原凹槽。原腰线与门楼柱础、一阶平台和门扇均保持原数据。关闭活动石画实时细分，保留源件可编辑存档。V26.11低清照片石画隐藏保留。漫游显示V26.12版本号，启动时定位内大门，Home仍回院落。')
changes={'source':str(SRC),'source_sha256':sha(SRC),'reference_model':str(OLD),'reference_sha256':sha(OLD),
         'restored':panels,'archived_photo_reliefs':archived,'original_V24_meshes':originals,
         'active_relief_triangles':sum(p['triangles']for p in panels),'architectural_geometry_modified':False,
         'collision_geometry_modified':False,'cause':'The V26.11 whole-gate photo crops lost much of V24 carving definition; saved panels were present and visible. The supplied screenshot cannot establish which saved Blender version was open. V26.12 restores actual V24 geometry and labels its running viewport.'}
(O/'Reports/V26_12_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
(O/'Reports/V26_12_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8')
print('V26_12_SAVED',sha(P),changes['active_relief_triangles'],flush=True)
