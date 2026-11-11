from pathlib import Path
import bpy,bmesh,sys,json,hashlib,shutil,collections,time,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_36/Blender/Architecture_Complete_V24_36.blend')
for p in [R,O/'Blender',O/'Roam',O/'References',O/'Source_Metadata']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,data):(R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
source=json.loads((D/'Source.json').read_text());assert sha(SOURCE)==source['sha256'];bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=json.loads((D/'Final_Scan_Index.json').read_text());report=json.loads((D/'Cleanup_Report.json').read_text());start=time.perf_counter();oldmeshes=[]
for j,r in enumerate(rows):
 if r['unchanged']:continue
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);M=np.array(o.matrix_world.inverted());v=a['v']@M[:3,:3].T+M[:3,3];me=bpy.data.meshes.new(r['name']+'_V37_Complete_Part');me.from_pydata(v,[],a['f']);me.polygons.foreach_set('material_index',a['mi']);me.update()
 if r['has_uv']:u=me.uv_layers.new(name=r['uv_name']);u.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 for m in o.data.materials:me.materials.append(m)
 oldmeshes.append(o.data);o.data=me;o['V24_37_Cleaning']='Retained coherent detailed source geometry; original photo UV; no invented surface'
 if j%200==0:print('APPLIED_SCAN',j,len(rows),'seconds',time.perf_counter()-start,flush=True)
for n in report['removed']:
 assert 'ORIGINAL_EXTERIOR_'in n or n.startswith(('V24_34_MB7_','V24_36_PTJIA6_'))
 o=bpy.data.objects.get(n)
 if o:oldmeshes.append(o.data);bpy.data.objects.remove(o,do_unlink=True)
for me in oldmeshes:
 if me.users==0:bpy.data.meshes.remove(me)
# Native architectural collision is a fixed verified prefix. Rebuild every
# photographic proxy from the now-visible cleaned scans, never from old ghosts.
base_n=json.loads(Path('E:/jz/JIA/Rebuild_V24_35/Reports/V24_35_Collision_Index.json').read_text())['original_architectural_triangles'];base=np.load(W/'v24_35/Final_Collision.npz');basef=base['f'][:base_n];base_nv=int(basef.max())+1;verts=[tuple(v)for v in base['v'][:base_nv]];faces=[tuple(f)for f in basef];groups=collections.defaultdict(list)
for r in rows:
 a=np.load(D/r['file']);v=a['v'];f=a['f'];c=(v.min(0)+v.max(0))/2;groups[tuple(np.floor(c[:2]/40).astype(int))].append((v,f,r['name']))
deps=bpy.context.evaluated_depsgraph_get();proxies=[]
for j,(key,parts)in enumerate(groups.items()):
 vs=[];fs=[];offset=0
 for v,f,n in parts:vs.append(v);fs.append(f+offset);offset+=len(v)
 vv=np.concatenate(vs);ff=np.concatenate(fs);me=bpy.data.meshes.new('TEMP_V37_PHOTO_PROXY');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(me);bm.free();temp=bpy.data.objects.new('TEMP_V37_PHOTO_PROXY',me);sc.collection.objects.link(temp)
 if len(me.polygons)>600:mod=temp.modifiers.new('Measured_Surface_Proxy','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 deps.update();ev=temp.evaluated_get(deps);pm=bpy.data.meshes.new_from_object(ev);pm.calc_loop_triangles();k=len(verts);verts.extend(tuple(v.co)for v in pm.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in pm.loop_triangles);proxies.append({'batch':list(map(int,key)),'source_meshes':[n for v,f,n in parts],'source_triangles':len(ff),'proxy_triangles':len(pm.loop_triangles)});bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(pm);bpy.data.meshes.remove(me)
 if j%20==0:print('CLEAN_PROXY',j,len(groups),'triangles',len(faces),'seconds',time.perf_counter()-start,flush=True)
np.savez_compressed(D/'Raw_Collision.npz',v=np.array(verts,np.float32),f=np.array(faces,np.int32));cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_37_Cleaned_Actual_Scan_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me
if old.users==0:bpy.data.meshes.remove(old)
cache['V24_37_Cleaned_Exterior']=True;cache['V24_37_Architectural_Prefix_Triangles']=base_n
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:(O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
for fn in ['启动漫游.cmd','打开修正版模型.cmd']:(O/fn).write_text((SOURCE.parents[1]/fn).read_text('utf8').replace('V24_36','V24_37'),encoding='utf8')
for p in (SOURCE.parents[1]/'References').glob('*'):shutil.copy2(p,O/'References'/p.name)
for fn in ['3MX_Inventory.json','Scene_Metadata.json','PTJIA6_Registration.json','Existing_Coverage.geojson','Native_Complete_Envelope.geojson','Filled_Current_Outline.geojson']:
 p=W/'v24_36'/fn
 if p.exists():shutil.copy2(p,O/'Source_Metadata'/('PTJIA6_'+fn))
for fn in ['Final_Scan_Retention.geojson','Reviewed_Stretched_Skirt_Exclusion.geojson','Quality_Plan.json','Cleanup_Report.json']:shutil.copy2(D/fn,O/'Source_Metadata'/fn)
meta=Path('E:/jz/JIA/Rebuild_V24_34/Source_Metadata')
if meta.exists():
 for p in meta.glob('*'):
  if p.is_file():shutil.copy2(p,O/'Source_Metadata'/('MB7_'+p.name))
note=bpy.data.texts.new('V24_37_完整外景保留与残片清理');note.write('保留有实测信息的连续地形、梯田、道路、建筑和植被主体，裁掉孔洞密集的破碎边缘、北侧拉长扫描幕片和微小悬浮碎片。原青砖墙、瓦顶、烟管、房屋、门窗、楼梯扶手与动作未修改；外景仍只补充当前模型缺失的区域。原始照片贴图已打包，裁切使用原UV的重心插值，不生成虚构外景。全部外景碰撞由清理后可见几何重建，保留原建筑碰撞与缺失落脚面边缘防掉落控制。')
col=bpy.data.collections.new('V24_37_完整外景检查视图');sc.collection.children.link(col);views=json.loads((W/'v24_36/Views.json').read_text())
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new('V24_37_'+tag,bpy.data.cameras.new('V24_37_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.03;c.data.clip_end=3000
(D/'Views.json').write_text(json.dumps(views));write('V24_37_Changes.json',{'source':str(SOURCE),'source_sha256':source['sha256'],'changed':report['changed']+['V24_21_Navigation_Collision'],'removed':report['removed'],'cleanup':report,'native_architecture_unchanged':True});write('V24_37_Collision_Index.json',{'architectural_triangles_preserved':base_n,'architectural_vertices_preserved':base_nv,'all_triangles':len(faces),'vertices':len(verts),'photo_batches':proxies,'proxy_ratio':.28,'all_bounds':[np.array(verts).min(0).tolist(),np.array(verts).max(0).tolist()],'boundary_clip_pending':True})
sc['Version']='V24_37_COMPLETE_COHERENT_MB7_PTJIA6_SAFE_EXTERIOR';sc.camera=bpy.data.objects['V24_37_02_House_And_PTJIA6'];sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_37_Build.json',{'model':str(P),'sha256':sha(P),'source':str(SOURCE),'source_sha256':source['sha256'],'boundary_clip_pending':True});print('V37_SAVED_STAGE1',sha(P),'seconds',time.perf_counter()-start,flush=True)
