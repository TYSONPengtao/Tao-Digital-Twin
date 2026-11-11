from pathlib import Path
import bpy,bmesh,numpy as np,json,sys,hashlib,shutil,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';BASE=Path('E:/jz/JIA/Rebuild_V26');SRC=BASE/'Blender/Architecture_Complete_V26.blend';P=O/'Blender/Architecture_Complete_V26_1.blend'
for p in [P.parent,R,O/'Roam',O/'Sources',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,data):(R/n).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new('V26_1_穿模重面与实拍扶手修正');sc.collection.children.link(col);archivecol=bpy.data.collections.new('V26_1_原构件备份_隐藏不参与显示和碰撞');sc.collection.children.link(archivecol);archivecol.hide_render=True;archivecol.hide_viewport=True
preps=[json.loads((D/f'Prepared_{tag}.json').read_text('utf8'))for tag in ['House','Railing','Site','Context_Trim']];archive=set(n for p in preps for n in p.get('archive',[]));rows=[r for p in preps for r in p['objects']];changed=[];added=[]
for n in sorted(archive):
 o=bpy.data.objects[n]
 for c in list(o.users_collection):c.objects.unlink(o)
 archivecol.objects.link(o);o.hide_render=True;o.hide_set(True);o['V26_1_Retained_Original_Component']=True;o['V26_1_Excluded_From_Visible_Shell_And_Collision']=True;changed.append(n)
for r in rows:
 n=r['name'];a=np.load(D/r['file']);o=bpy.data.objects.get(n);old=o.data if o else None;smooth=bool(old and any(p.use_smooth for p in old.polygons));v=a['v'];f=a['f'];me=bpy.data.meshes.new(n+'_V26_1');inv=o.matrix_world.inverted()if o else None;me.from_pydata([inv@Vector(p)for p in v]if o else v,[],f)
 for mn in r['materials']:me.materials.append(bpy.data.materials[mn])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_1_Preserved_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());uv.active_render=True
 if smooth or r.get('smooth_wood'):
  me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool))
  if r.get('smooth_wood'):
   try:me.set_sharp_from_angle(angle=math.radians(38))
   except Exception:pass
 me.update()
 if o:o.data=me;changed.append(n)
 else:o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 o['V26_1_Repair']=r['reason'];o['V26_1_Base_SHA256']=sha(SRC)
 print('INSTALLED',n,len(f),flush=True)

# Build one material from the actual existing photo materials. World height
# selects the rubble plinth, dark stone belt, limewash belt and antique brick;
# no extra coplanar polygons are placed on the outside wall.
def shader_group(mat):
 old=mat.node_tree;g=bpy.data.node_groups.new('V26_1_Source_'+mat.name,'ShaderNodeTree');g.interface.new_socket(name='Shader',in_out='OUTPUT',socket_type='NodeSocketShader');mapping={}
 for nd in old.nodes:
  if nd.type=='OUTPUT_MATERIAL':continue
  nu=g.nodes.new(nd.bl_idname);mapping[nd]=nu
  for prop in nd.bl_rna.properties:
   k=prop.identifier
   if prop.is_readonly or k in ['rna_type','name','parent','location','select','dimensions']or prop.type=='COLLECTION':continue
   try:setattr(nu,k,getattr(nd,k))
   except Exception:pass
  nu.location=nd.location
  for a,b in zip(nd.inputs,nu.inputs):
   if hasattr(a,'default_value'):
    try:b.default_value=a.default_value
    except Exception:pass
  if nd.type=='VALTORGB':
   ca=nd.color_ramp;cb=nu.color_ramp;cb.interpolation=ca.interpolation
   while len(cb.elements)>2:cb.elements.remove(cb.elements[-1])
   for j,e in enumerate(ca.elements):
    ee=cb.elements[j]if j<2 else cb.elements.new(e.position);ee.position=e.position;ee.color=e.color
 for link in old.links:
  if link.to_node in mapping and link.from_node in mapping:g.links.new(mapping[link.from_node].outputs[list(link.from_node.outputs).index(link.from_socket)],mapping[link.to_node].inputs[list(link.to_node.inputs).index(link.to_socket)])
 out=g.nodes.new('NodeGroupOutput');output=next(n for n in old.nodes if n.type=='OUTPUT_MATERIAL');link=next(l for l in old.links if l.to_node==output and l.to_socket.name=='Surface');g.links.new(mapping[link.from_node].outputs[list(link.from_node.outputs).index(link.from_socket)],out.inputs['Shader']);return g
mat=bpy.data.materials.new('M_V26_1_Reference_Wall_Rubble_Stone_Limewash_Brick');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();output=nt.nodes.new('ShaderNodeOutputMaterial');geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0]);base=[]
for name in ['M_V24_18_Continuous_Rubble','M_V19_Perimeter_Dark_Stone','M_V19_Limewash_Band','M_V24_20_Shared_AsBuilt_Perimeter_Brick']:
 node=nt.nodes.new('ShaderNodeGroup');node.node_tree=shader_group(bpy.data.materials[name]);base.append(node.outputs['Shader'])
cur=base[-1]
for threshold,shader in reversed(list(zip([-.68,-.20,.04],base[:3]))):
 test=nt.nodes.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=threshold;nt.links.new(xyz.outputs['Z'],test.inputs[0]);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(test.outputs[0],mix.inputs[0]);nt.links.new(cur,mix.inputs[1]);nt.links.new(shader,mix.inputs[2]);cur=mix.outputs[0]
nt.links.new(cur,output.inputs['Surface']);mat['Photo_Basis']='2026-10-23 020742 and 021028; proportion fit to registered wall geometry';mat['No_Added_Coplanar_Finish']=True;outer=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','V26_1_Secondary_Wall_Continuous_Upper_Brick']:
 o=bpy.data.objects[n];me=o.data.copy();o.data=me;ix=len(me.materials);me.materials.append(mat);count=0
 for p in me.polygons:
  c=o.matrix_world@p.center;no=(o.matrix_world.to_3x3()@p.normal).normalized()
  if 3.18<c.x<13.65 and -17.95<c.y<-16.1 and no.y<-.45:p.material_index=ix;count+=1
 me.update();changed.append(n);outer.append({'name':n,'outer_faces_material_reassigned':count,'inside_white_faces_unchanged':True,'division_z_m':[-.68,-.20,.04]})
write('V26_1_Outer_Wall_Photo_Strata.json',outer)

# Preserve untouched exterior collision ranges. Replace only archived/edited
# ranges with the current saved geometry; archived meshes cannot block a user.
cache=bpy.data.objects['V24_21_Navigation_Collision'];oldme=cache.data;oldme.calc_loop_triangles();cv=np.array([v.co[:]for v in oldme.vertices],np.float64);cf=np.array([t.vertices[:]for t in oldme.loop_triangles],np.int32);oldci=json.loads((BASE/'Reports/V26_Collision_Index.json').read_text('utf8'))['objects'];edited=set(changed)|set(added);vv=[];ff=[];ci=[]
def append(v,f,name,kind):
 k=len(vv);first=len(ff);vv.extend(v);ff.extend(np.asarray(f)+k);ci.append({'name':name,'first_triangle':first,'triangles':len(f),'source':kind})
for r in oldci:
 n=r['name']
 if n in edited or n in archive:continue
 fs=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,ix=np.unique(fs.ravel(),return_inverse=True);append(cv[used],ix.reshape(-1,3),n,'Unchanged V26 proxy')
need=set(added)|{r['name']for r in oldci if r['name']in edited and r['name']not in archive};need.discard(cache.name);deps=bpy.context.evaluated_depsgraph_get()
for j,n in enumerate(sorted(need)):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH' or o.hide_render:continue
 me=o.data;proxy=None
 if any(k in n for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_'])and len(me.polygons)>600:
  tmp=bpy.data.objects.new('V26_1_Temporary_Collision_Proxy',me.copy());sc.collection.objects.link(tmp);tmp.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(tmp.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005);bm.to_mesh(tmp.data);bm.free();mod=tmp.modifiers.new('Actual_Surface_Proxy','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True;deps.update();proxy=bpy.data.meshes.new_from_object(tmp.evaluated_get(deps));me=proxy
 me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];f=[t.vertices[:]for t in me.loop_triangles];append(v,f,n,'Current V26.1 surface'+(' decimated exterior'if proxy else''))
 if proxy:
  data=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True);bpy.data.meshes.remove(proxy);bpy.data.meshes.remove(data)
 if j%15==0:print('COLLISION',j,len(need),len(ff),flush=True)
me=bpy.data.meshes.new('V26_1_Current_Shell_Railing_Ground_And_Exterior_Collision');me.from_pydata(vv,[],ff);me.update();cache.data=me;cache.matrix_world.identity();cache['V26_1_Current_Visible_Geometry_Only']=True;changed.append(cache.name);write('V26_1_Collision_Index.json',{'objects':ci,'triangles':len(ff),'frame':40,'archived_components_excluded':True,'no_infinite_ground':True})
for text,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 code=bpy.data.texts[text].as_string().replace('Rebuild_V26','Rebuild_V26_1').replace('Architecture_Complete_V26.blend','Architecture_Complete_V26_1.blend');bpy.data.texts[text].clear();bpy.data.texts[text].write(code);(O/'Roam'/fn).write_text(code,encoding='utf8')
for n in ['启动漫游.cmd','打开修正版模型.cmd']:(O/n).write_text((BASE/n).read_text('utf8').replace('Architecture_Complete_V26.blend','Architecture_Complete_V26_1.blend').replace('Rebuild_V26','Rebuild_V26_1'),encoding='utf8')
views=[('01_Stair_Flush_Treads',(7.5,9.1,2.75),(4.6,8.6,1.7),22),('02_Half_Landing_Wreath',(5.95,8.0,3.0),(5.13,8.55,2.42),36),('03_Floor_Newel_Sockets',(8.65,7.9,5.2),(7.82,8.55,4.35),34),('04_Stair_White_Corner',(4.65,8.2,5.7),(5.95,9.67,6.75),20),('05_Terrace_Flush_Wall',(1.5,8.3,8.5),(3.9,8.3,10.1),17),('06_F3_Guard_Base',(8.75,6.8,8.35),(5.9,7.25,7.8),23),('07_Reference_Screenwall',(18,-25,4.0),(11.7,-16.7,1.8),35),('08_Gate_Floor',(6.35,-11.0,1.05),(8.0,-10.8,-.4),20),('09_White_Wall_Ground',(12.65,9.,.8),(14.3,8.,-.3),24),('10_West_Courtyard_Wall',(3.5,-9.0,1.0),(0,-7.5,.9),25),('11_House_Exterior',(24,-22,17),(6,4,4.5),36),('12_Original_Entrance_Ramp',(-20.5,-16.5,4.3),(-13.9,-10.55,-.3),35)]
for tag,pos,aim,lens in views:
 n='V26_1_'+tag;c=bpy.data.objects.new(n,bpy.data.cameras.new(n));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;added.append(n)
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8');sc.camera=bpy.data.objects['V26_1_11_House_Exterior'];sc['Version']='V26_1_Single_Visible_Surface_Continuous_Photo_Railing_And_Clean_Context';sc['V26_1_Base_File_SHA256']=sha(SRC)
txt=bpy.data.texts.new('V26_1_逐项修正说明');txt.write('以V26为唯一底稿另存，Blender模型。梁墙板楼梯整理成单一可见实体，旧构件保留在隐藏备份集合，不参与显示和漫游碰撞。平台梁只在露出踏步的部位做局部避让，保留支承接触；统一楼面顶面材质。按实拍改深红木扶手为椭圆握持截面、连续180度回弯及接柱颈口，球头和立柱相连，加密车木杆并检查落脚。露台墙面陶瓷饰面在柱外连续收平。地面和院墙重合层归并；只裁掉已经被重建建筑和院墙覆盖的扫描碎片，保留外景。南侧靠廊房的短墙按补图改为连续白色水平线脚和浅瓦压顶，外侧恢复青砖、灰石和毛石层次。原入口坡面与照片、全体门窗动作保留。图像比例用于外观拟合，不能代替现场测量和结构承载验算。')
write('V26_1_Changes.json',{'source':str(SRC),'source_sha256':sha(SRC),'changed':sorted(set(changed)),'added':sorted(set(added)),'archived':sorted(archive),'removed':[],'house_proof':preps[0]['proof'],'railing_proof':preps[1]['proof'],'site_proof':preps[2]['proof'],'context_trim_proof':preps[3]['proof'],'no_rhino_export':True})
for t in ['015559','015632','015726','015859','015914','020006','020049','020115','020141','020200','020444','020742','021028']:
 p=Path('D:/Desktop/屏幕截图 2026-10-23 '+t+'.jpg')
 if p.exists():shutil.copy2(p,O/'References'/p.name)
sc.frame_set(40);bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V26_1_Build.json',{'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'source':str(SRC),'source_sha256':sha(SRC),'blender':bpy.app.version_string});print('V26_1_SAVED',str(P),sha(P),flush=True)
