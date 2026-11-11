from pathlib import Path
import bpy,bmesh,sys,json,hashlib,shutil,collections,time,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_36.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_35/Blender/Architecture_Complete_V24_35.blend')
for p in [R,O/'Blender',O/'Roam',O/'References',O/'Source_Metadata']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8');(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)}));sc.frame_set(40);bpy.context.view_layer.update();cache=bpy.data.objects['V24_21_Navigation_Collision'];base=cache.data;base.calc_loop_triangles();verts=[tuple(cache.matrix_world@v.co)for v in base.vertices];faces=[tuple(t.vertices)for t in base.loop_triangles];base_n=len(faces);base_v=len(verts);old_bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True);col=bpy.data.collections.new('V24_36_PTJIA6_仅补充缺失外景');sc.collection.children.link(col);rows=json.loads((D/'Missing_Exterior_Index.json').read_text());textures={};added=[];final=[];seams=[];groups=collections.defaultdict(list);start=time.perf_counter()
for j,r in enumerate(rows):
 a=np.load(D/r['file']);v=a['v'].copy();f=a['f'];dzs=[]
 if r.get('seam_weight_file'):
  weights=np.load(D/r['seam_weight_file'])['w']
  for k in np.flatnonzero(weights>0):
   q,no,face,dist=old_bvh.find_nearest(Vector(v[k]),1.05)
   if q is not None and no.z>=.64 and np.linalg.norm(np.array(q)[:2]-v[k,:2])<.15:
    dz=(q.z-v[k,2])*weights[k]
    if abs(dz)<.90:v[k,2]+=dz;dzs.append(abs(float(dz)))
 me=bpy.data.meshes.new('PTJIA6_'+Path(r['node']).stem);me.from_pydata(v,[],f);me.polygons.foreach_set('material_index',a['mi']);me.update();uv=me.uv_layers.new(name='PTJIA6_Original_Photo_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 for tx in r['textures']:
  key=tx['sha256']
  if key not in textures:
   im=bpy.data.images.load(str(D/tx['file']),check_existing=True);im.name='PTJIA6_'+Path(tx['file']).name;im.pack();mat=bpy.data.materials.new('M_PTJIA6_'+Path(tx['file']).stem);mat.use_nodes=True;ns=mat.node_tree.nodes;principled=next(n for n in ns if n.type=='BSDF_PRINCIPLED');principled.inputs['Roughness'].default_value=.88;principled.inputs['Specular IOR Level'].default_value=.15;tex=ns.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],principled.inputs['Base Color']);textures[key]=mat
  me.materials.append(textures[key])
 o=bpy.data.objects.new('V24_36_PTJIA6_'+Path(r['node']).stem,me);col.objects.link(o);o['Source_3MXB']=str(Path('D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model')/r['node']);o['Source_SHA256']=r['source_sha256'];o['Original_JPEG_Bytes_Preserved']=True;o['Scope']='Only outside current model coverage and complete native roof wall envelope';added.append(o.name);fn='FINAL_'+Path(r['node']).stem+'.npz';np.savez_compressed(D/fn,v=v,f=f,uv=a['uv'],mi=a['mi']);final.append({'name':o.name,'file':fn,'source_node':r['node'],'vertices':len(v),'triangles':len(f)});seams.append({'node':r['node'],'adjusted_vertices':len(dzs),'max_z_adjust_m':max(dzs,default=0)})
 centre=(v.min(0)+v.max(0))/2;group=tuple(np.floor(centre[:2]/40).astype(int));groups[group].append((v,f))
 if j%100==0:print('IMPORT_PTJIA6',j,len(rows),'seconds',time.perf_counter()-start,flush=True)
# Spatial batches reduce collision mesh complexity and preserve every existing
# collision triangle from the already repaired model.
deps=bpy.context.evaluated_depsgraph_get();proxies=[]
for j,(key,parts)in enumerate(groups.items()):
 vs=[];fs=[];offset=0
 for v,f in parts:vs.append(v);fs.append(f+offset);offset+=len(v)
 vv=np.concatenate(vs);ff=np.concatenate(fs);me=bpy.data.meshes.new('TEMP_PTJIA6_PROXY');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(me);bm.free();temp=bpy.data.objects.new('TEMP_PTJIA6_PROXY',me);sc.collection.objects.link(temp)
 if len(me.polygons)>600:mod=temp.modifiers.new('Real_Scan_Collision_Proxy','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 deps.update();ev=temp.evaluated_get(deps);pm=bpy.data.meshes.new_from_object(ev);pm.calc_loop_triangles();k=len(verts);verts.extend(tuple(v.co)for v in pm.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in pm.loop_triangles);proxies.append({'batch':list(map(int,key)),'source_meshes':len(parts),'source_triangles':len(ff),'proxy_triangles':len(pm.loop_triangles)});bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(pm);bpy.data.meshes.remove(me)
 if j%20==0:print('PROXY_PTJIA6',j,len(groups),'triangles',len(faces),'seconds',time.perf_counter()-start,flush=True)
me=bpy.data.meshes.new('V24_36_All_Architecture_MB7_PTJIA6_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;cache['V24_36_PTJIA6_All_Surfaces']=True;cache['V24_36_Base_Preserved_Triangles']=base_n;np.savez_compressed(D/'Final_Collision.npz',v=np.array(verts,np.float32),f=np.array(faces,np.int32));groups.clear()
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[txt].as_string()
 if fn=='roam_controller.py':code=code.replace('self.space.clip_end=300.','self.space.clip_end=1500.');bpy.data.texts[txt].clear();bpy.data.texts[txt].write(code)
 (O/'Roam'/fn).write_text(code,encoding='utf8')
for n in ['启动漫游.cmd','打开修正版模型.cmd']:(O/n).write_text((SOURCE.parents[1]/n).read_text('utf8').replace('V24_35','V24_36'),encoding='utf8')
allv=np.array(verts);lo=allv.min(0);hi=allv.max(0);center=(lo+hi)/2;span=max(hi[0]-lo[0],hi[1]-lo[1]);views=[('01_Expanded_Context_Overview',tuple(center+np.array([-.42*span,-.85*span,.95*span])),tuple(center),38),('02_House_And_PTJIA6',(46.,-79.,42.),(-20.,-2.,4.),30),('03_West_Expansion',(-135.,-96.,43.),(-85.,-22.,0.),30)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new('V24_36_'+tag,bpy.data.cameras.new('V24_36_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.03;c.data.clip_end=3000.
(D/'Views.json').write_text(json.dumps(views));(D/'Final_Exterior_Index.json').write_text(json.dumps(final,indent=2));write('V24_36_Changes.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'changed':['V24_21_Navigation_Collision'],'added':added,'removed':[],'source_images':len(textures),'display_triangles':sum(r['triangles']for r in rows),'seams':seams});write('V24_36_Collision_Index.json',{'previous_complete_model_triangles':base_n,'previous_complete_model_vertices':base_v,'all_triangles':len(faces),'vertices':len(verts),'PTJIA6_batches':proxies,'proxy_ratio':.28,'all_bounds':[lo.tolist(),hi.tolist()]})
for fn in ['3MX_Inventory.json','Scene_Metadata.json','PTJIA6_Registration.json','Clip_Report.json','Existing_Coverage.geojson','Native_Complete_Envelope.geojson']:shutil.copy2(D/fn,O/'Source_Metadata'/fn)
for p in (SOURCE.parents[1]/'References').glob('*'):shutil.copy2(p,O/'References'/p.name)
note=bpy.data.texts.new('V24_36_PTJIA6外景扩展');note.write('在V24.35屋檐与青砖墙残片修正版上，加入PTJIA6的非重叠最高精度3MXB叶节点，仅保留当前实景与完整原生建筑外壳之外的缺失外景。原始CTM/JPEG读取并保留照片UV，原建筑与MB7有效外景不变。保留原完整碰撞数据并加入PTJIA6真实表面碰撞；边缘阻止迈出与最近安全位置回位继续生效。')
sc['Version']='V24_36_CLEAN_WALL_MB7_PTJIA6_COMPLETE_SAFE_EXTERIOR';sc.camera=bpy.data.objects['V24_36_02_House_And_PTJIA6'];sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_36_Build.json',{'model':str(P),'sha256':sha(P),'source':str(SOURCE),'source_sha256':sha(SOURCE)});print('V36_SAVED',sha(P),'seconds',time.perf_counter()-start,flush=True)
