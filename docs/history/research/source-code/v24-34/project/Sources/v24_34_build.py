from pathlib import Path
import bpy,bmesh,sys,json,hashlib,shutil,time,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_33/Blender/Architecture_Complete_V24_33.blend')
for p in [R,O/'Blender',O/'Roam',O/'Source_Metadata'] :p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update()
col=bpy.data.collections.new('V24_34_MB7_缺失外景扩展_原始照片材质');sc.collection.children.link(col);old=[o for o in bpy.data.objects if o.type=='MESH'and'ORIGINAL_EXTERIOR_'in o.name];vv=[];ff=[]
for o in old:
 me=o.data;me.calc_loop_triangles();k=len(vv);vv.extend(tuple(o.matrix_world@p.co)for p in me.vertices);ff.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles)
seam_bvh=BVHTree.FromPolygons(vv,ff,all_triangles=True);added=[];new=[];seams=[];rows=json.loads((D/'Missing_Exterior_Index.json').read_text());textures={};finalindex=[]
for j,r in enumerate(rows):
 a=np.load(D/r['file']);v=a['v'].copy();f=a['f'];changes=[]
 for i in np.flatnonzero(a['seam_weight']>0):
  q,no,face,dist=seam_bvh.find_nearest(Vector(v[i]),.8)
  if q is not None and np.linalg.norm(np.array(q)[:2]-v[i,:2])<.12:
   dz=(q.z-v[i,2])*a['seam_weight'][i]
   if abs(dz)<.65:v[i,2]+=dz;changes.append(abs(float(dz)))
 me=bpy.data.meshes.new('MB7_'+Path(r['node']).stem);me.from_pydata(v,[],f);me.polygons.foreach_set('material_index',a['mi']);me.update();uv=me.uv_layers.new(name='MB7_Original_Photo_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel())
 for tx in r['textures']:
  key=tx['sha256']
  if key not in textures:
   im=bpy.data.images.load(str(D/tx['file']),check_existing=True);im.name='MB7_'+Path(tx['file']).name;im.pack();mat=bpy.data.materials.new('M_MB7_'+Path(tx['file']).stem);mat.use_nodes=True;ns=mat.node_tree.nodes;p=ns.get('Principled BSDF');p.inputs['Roughness'].default_value=.88;p.inputs['Specular IOR Level'].default_value=.15;tex=ns.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);textures[key]=mat
  me.materials.append(textures[key])
 o=bpy.data.objects.new('V24_34_MB7_'+Path(r['node']).stem,me);col.objects.link(o);o['Source_OSGB']=str(Path('D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model')/r['node']);o['Source_SHA256']=r['source_sha256'];o['Scope']='Only outside existing native/context coverage';o['Original_JPEG_Bytes_Preserved']=True;o['LOD']='Finest non-overlapping leaf frontier';o['Seam_Transition_Width_m']=.75;new.append(o);added.append(o.name)
 np.savez_compressed(D/('FINAL_'+Path(r['node']).stem+'.npz'),v=v,f=f,uv=a['uv'],mi=a['mi']);finalindex.append({'name':o.name,'file':'FINAL_'+Path(r['node']).stem+'.npz','source_node':r['node'],'triangles':len(f),'vertices':len(v)});seams.append({'node':r['node'],'adjusted_vertices':len(changes),'max_z_adjust_m':max(changes,default=0)})
 if j%20==0:print('IMPORT',j,len(rows),flush=True)
# Preserve every architectural collision triangle, extend it with real scan
# surfaces. The reduced proxy follows the displayed model, not an added plane.
cache=bpy.data.objects['V24_21_Navigation_Collision'];base=cache.data;base.calc_loop_triangles();verts=[tuple(cache.matrix_world@v.co)for v in base.vertices];faces=[tuple(t.vertices)for t in base.loop_triangles];base_n=len(faces);proxy=[];deps=bpy.context.evaluated_depsgraph_get()
for j,o in enumerate(old+new):
 me=o.data.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.to_mesh(me);bm.free();temp=bpy.data.objects.new('TEMP_MB7_COLLISION',me);sc.collection.objects.link(temp);temp.matrix_world=o.matrix_world.copy()
 if len(me.polygons)>600:
  mod=temp.modifiers.new('Real_Surface_Decimation','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
 deps.update();ev=temp.evaluated_get(deps);proxyme=bpy.data.meshes.new_from_object(ev);proxyme.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in proxyme.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in proxyme.loop_triangles);proxy.append({'object':o.name,'display_triangles':len(o.data.polygons),'proxy_triangles':len(proxyme.loop_triangles)});bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(proxyme);bpy.data.meshes.remove(me)
 if j%25==0:print('COLLISION',j,len(old+new),len(faces),flush=True)
me=bpy.data.meshes.new('V24_34_All_Model_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;cache['V24_34_All_Existing_And_MB7_Exterior']=True;cache['V24_34_Exterior_Proxy']='Welded real scan surfaces, 28 percent decimation, no flat artificial ground';cache['V24_34_Source_Model_SHA256']=sha(SOURCE)
for text,fn in [('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py')]:
 code=(W/('v24_34_'+fn)).read_text('utf8');bpy.data.texts[text].clear();bpy.data.texts[text].write(code)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:(O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('01_Expanded_Site',(-100.,-140.,118.),(0.,-4.,0.),38),('02_Original_House_And_Context',(-43.,-62.,40.),(4.,-4.,1.),32),('03_Added_South_Road',(8.,-58.,5.),(10.,-32.,-5.),24),('04_Outer_Road_Connection',(-33.,-28.,6.),(-15.,-18.,-2.),26),('05_East_Context',(56.,-12.,12.),(24.,-8.,0.),24),('06_Existing_Courtyard',(5.,-8.,1.1),(6.5,2.,2.),24)]
for tag,pos,aim,lens in views:
 cam=bpy.data.objects.new('V24_34_'+tag,bpy.data.cameras.new('V24_34_'+tag));col.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.025;cam.data.clip_end=500.;added.append(cam.name)
for n in ['启动漫游.cmd','打开修正版模型.cmd']:(O/n).write_text((SOURCE.parents[1]/n).read_text('utf8').replace('V24_33','V24_34'),encoding='utf8')
for n in ['MB7_Registration.json','Clip_Report.json','Existing_Coverage.geojson','OSGB_Inventory.json'] :shutil.copy2(D/n,O/'Source_Metadata'/n)
shutil.copy2('D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/metadata.xml',O/'Source_Metadata/MB7_metadata.xml')
sc['Version']='V24_34_MB7_MISSING_EXTERIOR_AND_ALL_MODEL_SAFE_ROAM';sc['MB7_Exterior_Source']='D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model';sc['MB7_Registration_Basis']='Shared photogrammetric surfaces, not independently surveyed control';sc.camera=bpy.data.objects['V24_34_01_Expanded_Site'];sc.frame_set(40);bpy.context.view_layer.update()
note=bpy.data.texts.new('V24_34_MB7外景扩展与安全漫游');note.write('保留V24.33原建筑、院落与已有实景网格；对MB7最高精度非重叠叶节点做地理初始定位和共同照片特征配准，只裁入现有覆盖以外的部分。接缝0.75米范围内对新模型高度做局部渐变贴合，原模型坐标不改。原始JPEG逐字节提取打包，裁边纹理用重心坐标插值。已有实景与新外景均加入真实表面碰撞代理，边界与缺失数据处停止人物，不生成穿过建筑的无限地板；意外失去支撑回到最近安全位置。')
(D/'Final_Exterior_Index.json').write_text(json.dumps(finalindex,indent=2));(D/'Views.json').write_text(json.dumps(views),encoding='utf8');write('V24_34_Changes.json',{'source_model':str(SOURCE),'source_sha256':sha(SOURCE),'changed':['V24_21_Navigation_Collision'],'added':added,'removed':[],'display_triangles':sum(r['triangles']for r in rows),'original_jpeg_images':len(textures),'seams':seams});write('V24_34_Collision_Index.json',{'original_architectural_triangles':base_n,'all_triangles':len(faces),'vertices':len(verts),'exterior_sources':proxy,'proxy_ratio':.28,'no_infinite_flat_floor':True})
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_34_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P)});print('V34_SAVED',sha(P),flush=True)
