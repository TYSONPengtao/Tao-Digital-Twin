import bpy,numpy as np,json,hashlib,sys,shutil
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_13';BASE=Path('E:/jz/JIA/Rebuild_V26_12');SRC=BASE/'Blender/Architecture_Complete_V26_12.blend';O=Path('E:/jz/JIA/Rebuild_V26_13');P=O/'Blender/Architecture_Complete_V26_13.blend'
for p in[P.parent,O/'Reports',O/'Sources',O/'Roam',O/'Textures',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(SRC)=='bb27b6d00aed01d019214ea5d9936846c37c8463cfc4278d0dd78ec3f9990fb4'
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
if not(D/'Before_Snapshot.json').exists():(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
prep=json.loads((D/'Prepared.json').read_text('utf8'));oldch=json.loads((BASE/'Reports/V26_12_Changes.json').read_text('utf8'));matmap={};newmats=[]
for kind,color,source in[('Core',(.285,.300,.305),'M_V21_GATE_REF_02'),('Edge',(.295,.308,.310),'M_V21_GATE_REF_03'),('Carving',(.300,.310,.315),'M_V21_GATE_REF_04'),('Sill',(.270,.280,.285),'M_V21_GATE_REF_01')]:
 name='M_V26_13_Gate_Gray_Stone_'+kind;mat=bpy.data.materials[source].copy();mat.name=name;mat.use_nodes=True;mat.diffuse_color=(*color,1);nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.88;bs.inputs['Metallic'].default_value=0.;bs.inputs['Specular IOR Level'].default_value=.25
 geo=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=230.;noise.inputs['Detail'].default_value=2.;ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(c*.94 for c in color),1);ramp.color_ramp.elements[1].color=(*(c*1.06 for c in color),1);bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.10;bump.inputs['Distance'].default_value=.00012;nt.links.new(geo.outputs['Position'],noise.inputs['Vector']);nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color']);nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);matmap[source]=name;newmats.append(name)
matmap['M_V21_GATE_REF_05']='M_V26_13_Gate_Gray_Stone_Core'
col=bpy.data.collections.new('V26.13_实景门柱与低台基');sc.collection.children.link(col);changed=[];added=[];archived=[]
for rr in prep['objects']:
 a=np.load(D/rr['file']);o=bpy.data.objects.get(rr['name'])
 if rr.get('vertex_correspondence'):
  old=bpy.data.objects[rr['source']];o=old.copy();o.data=old.data.copy();o.name=rr['name'];o.modifiers.clear();col.objects.link(o);inv=np.asarray(o.matrix_world.inverted());local=a['v']@inv[:3,:3].T+inv[:3,3];assert len(local)==len(o.data.vertices);o.data.vertices.foreach_set('co',local.astype(np.float32).ravel())
  for k,mat in enumerate(o.data.materials):o.data.materials[k]=bpy.data.materials[matmap.get(mat.name,mat.name)]
  o.hide_render=False;o.hide_set(False);o['V26_13_Source']=rr['source'];added.append(o.name);old.hide_render=True;old.hide_set(True);archived.append(old.name)
 else:
  inv=o.matrix_world.inverted();me=bpy.data.meshes.new(rr['name']+'_V26_13');me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'])
  for mat in rr['materials']:me.materials.append(bpy.data.materials[mat])
  me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.uv_layers.new(name='V26_13_World_Stone_UV').data.foreach_set('uv',a['uv'].astype(np.float32).ravel());o.data=me
 o.data.update();o['V26_13_Photo_Fit']=True;changed.append(o.name);print('INSTALLED',o.name,len(o.data.polygons),flush=True)
# Keep the header's shape and three original pictures; harmonize only stone color.
header_names=['SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']+[r['name']for r in oldch['restored']if'Header'in r['source_object']]
for name in header_names:
 o=bpy.data.objects[name];o.data=o.data.copy()
 for k,mat in enumerate(o.data.materials):o.data.materials[k]=bpy.data.materials[matmap.get(mat.name,mat.name)]
 changed.append(name)
waist_old=bpy.data.objects['V24_Gate_Waist_Carving_Retained'];waist=waist_old.copy();waist.data=waist_old.data.copy();waist.name='V26_13_Original_Faceted_Waist_Carving';col.objects.link(waist);waist.hide_render=False;waist.hide_set(False)
for k,mat in enumerate(waist.data.materials):waist.data.materials[k]=bpy.data.materials[matmap.get(mat.name,mat.name)]
waist_old.hide_render=True;waist_old.hide_set(True);changed.append(waist.name);added.append(waist.name);archived.append(waist_old.name)
# Replace only changed structural surfaces in the existing collision index.
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;me.calc_loop_triangles();cv=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',cv);cv=cv.reshape(-1,3);cf=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);ix=json.loads((BASE/'Reports/V26_12_Collision_Index.json').read_text('utf8'))['objects'];need={'V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_01_Geometry'};vv=[];ff=[];ci=[];offset=0;first=0
def append(v,f,name,source):
 global offset,first
 vv.append(v);ff.append(f+offset);ci.append({'name':name,'first_triangle':first,'triangles':len(f),'source':source});offset+=len(v);first+=len(f)
for r in ix:
 if r['name']in need:continue
 f=cf[r['first_triangle']:r['first_triangle']+r['triangles']];used,rev=np.unique(f.ravel(),return_inverse=True);append(cv[used],rev.reshape(-1,3),r['name'],'Unchanged V26.12 collision data')
for name in sorted(need):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();append(np.array([o.matrix_world@v.co for v in o.data.vertices]),np.array([t.vertices[:]for t in o.data.loop_triangles],np.int32),name,'Current V26.13 structural geometry')
me=bpy.data.meshes.new('V26_13_Current_Collision');me.from_pydata(np.vstack(vv),[],np.vstack(ff));me.update();cache.data=me;cache.matrix_world.identity();changed.append(cache.name);(O/'Reports/V26_13_Collision_Index.json').write_text(json.dumps({'objects':ci,'triangles':first,'frame':40,'no_infinite_ground':True},ensure_ascii=False),'utf8')
for name in['start_roam.py','roam_controller.py','roam_physics.py','measure_tools.py','start_roam_fast.py','roam_controller_fast.py']:
 p=BASE/'Roam'/name
 if p.exists():(O/'Roam'/name).write_text(p.read_text('utf8').replace('Rebuild_V26_12','Rebuild_V26_13').replace('Architecture_Complete_V26_12','Architecture_Complete_V26_13').replace('V26.12','V26.13').replace('V26_12_流畅显示','V26_13_流畅显示'),'utf8')
for text,name in[('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_25_测量工具.py','measure_tools.py')]:bpy.data.texts[text].clear();bpy.data.texts[text].write((O/'Roam'/name).read_text('utf8'))
(O/'启动漫游.cmd').write_text((BASE/'启动漫游.cmd').read_text('utf8').replace('Rebuild_V26_12','Rebuild_V26_13').replace('Architecture_Complete_V26_12','Architecture_Complete_V26_13'),'utf8')
for im in bpy.data.images:
 if im.source!='VIEWER'and im.type not in['RENDER_RESULT','COMPOSITING']:im.use_fake_user=True
sc['Version']='V26_13_Photo_Fitted_Faceted_Gate_Piers_And_Low_Plinths';sc.frame_set(40);bpy.context.view_layer.update()
note=bpy.data.texts.new('V26_13_实景门柱修正');note.write('按两张实景对照：前角由12mm小倒角改成90mm斜转面，三个朝前面都有石画；下段花卉板延伸150mm，底框距门槛约45mm；恢复82mm高原折面腰线。柱脚改成35mm高、最大外扩20mm的薄斜收口；入口仍一阶，前沿从原柱前280mm收至90mm，宽度随小柱脚收窄。石体、边框与雕刻使用同一灰石色系和细微颗粒。尺寸为照片及原模型拟合，保留V24石画纹样与原门扇动作。阴天和局部AO设置继承。')
changes={'source':str(SRC),'source_sha256':sha(SRC),'proof':prep['proof'],'changed':sorted(set(changed)),'added':added,'archived':archived,'panels':prep['proof']['panels'],'waist':waist.name,'retained_headers':header_names,'material_only_changed':header_names,'structural_changed':sorted(need),'new_materials':newmats,'source_live_file_not_overwritten':True}
(O/'Reports/V26_13_Changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),'utf8');bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);(O/'Reports/V26_13_Build.json').write_text(json.dumps({'model':str(P),'sha256':sha(P),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('V26_13_SAVED',sha(P),flush=True)
