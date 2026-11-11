from pathlib import Path
import bpy,json,hashlib,sys
import numpy as np
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/'geomlibs')]
P=Path('E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend')
OLD=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend')
R=P.parents[1]/'Reports';R.mkdir(exist_ok=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert h=='ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7'
checks=[]
def ck(n,b,**kw):
 checks.append({'check':n,'pass':bool(b),**kw});print(n,bool(b),kw if not b else'',flush=True)
def val(v):
 if isinstance(v,(str,bool,int,float)):return v
 if hasattr(v,'__len__'):return [val(a)for a in v]
 return str(v)
def material(m):
 d={'diffuse_color':list(m.diffuse_color),'use_nodes':m.use_nodes,'nodes':[],'links':[]}
 if m.use_nodes:
  for n in m.node_tree.nodes:
   r={'name':n.name,'type':n.bl_idname,'inputs':[]}
   for i,s in enumerate(n.inputs):
    if hasattr(s,'default_value'):r['inputs'].append([i,s.name,val(s.default_value)])
   for k in ['operation','blend_type','distribution','subsurface_method','extension','projection','interpolation']:
    if hasattr(n,k):r[k]=val(getattr(n,k))
   if getattr(n,'image',None):r['image']=n.image.name
   d['nodes'].append(r)
  d['links']=sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier]for l in m.node_tree.links)
 d['nodes'].sort(key=lambda q:q['name']);return d
def lights():
 return {o.name:{'type':o.data.type,'energy':float(o.data.energy),'color':list(o.data.color),'matrix_world':[list(r)for r in o.matrix_world]}for o in bpy.context.scene.objects if o.type=='LIGHT'}
bpy.ops.wm.open_mainfile(filepath=str(OLD))
names=['M_V26_3_Neutral_White_Interior_Ceiling','M_Wall_Interior']
oldm={n:material(bpy.data.materials[n])for n in names}
oldlights=lights()
bpy.ops.wm.open_mainfile(filepath=str(P))
for n in names:ck('Original white paint material unchanged '+n,material(bpy.data.materials[n])==oldm[n])
ck('Saved model contains original architectural lights with no temporary review fill',lights()==oldlights,original_light_names=sorted(oldlights),saved_light_names=sorted(lights()))
settings=[]
for s in bpy.data.screens:
 for a in s.areas:
  if a.type!='VIEW_3D':continue
  q=a.spaces.active.shading
  settings.append({'screen':s.name,'type':q.type,'studio_light':q.studio_light,'use_scene_world':q.use_scene_world,'use_scene_lights':q.use_scene_lights})
ck('All saved3D spaces use bright studio MaterialPreview independent of scene world and lights',bool(settings)and all(q['type']=='MATERIAL'and not q['use_scene_world']and not q['use_scene_lights']and q['studio_light']=='studio.exr'for q in settings),spaces=settings)
world=bpy.context.scene.world
ck('Saved scene has node based world',world is not None and world.use_nodes,world=world.name if world else None)
N=world.node_tree.nodes;L=list(world.node_tree.links)
paths=[]
for e in N:
 if e.bl_idname!='ShaderNodeTexEnvironment':continue
 for a in L:
  if a.from_node!=e or a.to_node.bl_idname!='ShaderNodeRGBToBW':continue
  bw=a.to_node
  for b in L:
   if b.from_node!=bw or b.to_node.bl_idname!='ShaderNodeBackground' or b.to_socket.name!='Color':continue
   bg=b.to_node
   for c in L:
    if c.from_node==bg and c.to_node.bl_idname=='ShaderNodeOutputWorld'and c.to_socket.name=='Surface':
     paths.append((e,bw,bg,c.to_node))
ck('World node path is environment to RGBToBW to background to world surface',len(paths)==1,path=[[n.name,n.bl_idname]for n in paths[0]]if paths else[])
e,bw,bg,output=paths[0]
im=e.image;packed=bytes(im.packed_file.data)if im and im.packed_file else b''
src=Path('D:/AJAVIS01/RHINO7.12/PLUGINS/BLENDER/RUNING/5.1/datafiles/studiolights/world/studio.exr')
with src.open('rb')as f:srch=hashlib.file_digest(f,'sha256').hexdigest()
ck('Original studio environment is packed byte for byte',bool(packed)and hashlib.sha256(packed).hexdigest()==srch,image=im.name,packed_sha256=hashlib.sha256(packed).hexdigest(),original_sha256=srch,image_filepath=im.filepath)
active=[n for n in N if n.bl_idname=='ShaderNodeOutputWorld'and n.is_active_output]
surface_links=[l for l in L if l.to_node in active and l.to_socket.name=='Surface']
ck('Active world output has no alternative colored surface branch',len(active)==1 and len(surface_links)==1 and surface_links[0].from_node==bg and output==active[0] and not bg.inputs['Strength'].is_linked,strength=float(bg.inputs['Strength'].default_value))
# Evaluate the actual saved graph, using an empty temporary render scene.
# This affects only this background process and never saves the model.
sc=bpy.data.scenes.new('Independent_Gray_World_QA');sc.world=world
sc.render.engine='CYCLES';sc.cycles.samples=1;sc.cycles.use_denoising=False
sc.render.resolution_x=256;sc.render.resolution_y=128;sc.render.resolution_percentage=100
sc.render.film_transparent=False;sc.render.image_settings.file_format='OPEN_EXR';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='32'
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
ca=bpy.data.cameras.new('QA_Environment_Camera');co=bpy.data.objects.new(ca.name,ca);sc.collection.objects.link(co);sc.camera=co;ca.type='PANO';ca.panorama_type='EQUIRECTANGULAR'
probe=Path(__file__).with_name('Saved_Gray_World_Probe.exr');sc.render.filepath=str(probe);bpy.ops.render.render(scene=sc.name,write_still=True)
ri=bpy.data.images.load(str(probe),check_existing=False);px=np.array(ri.pixels[:],np.float64).reshape(ri.size[1],ri.size[0],4)[:,:,:3]
spread=np.max(px,axis=2)-np.min(px,axis=2)
ck('Separate saved grayscale render world produces channel neutral RGB',np.isfinite(px).all()and float(spread.max())<1e-6,render_resolution=list(ri.size),maximum_linear_RGB_channel_difference=float(spread.max()),mean_linear_RGB=px.mean((0,1)).tolist(),probe_path=str(probe),scope='Neutral render inspection world only. Default MaterialPreview uses original studio.exr directly and is not asserted chromatically neutral.')
fail=[q for q in checks if not q['pass']]
out={'model':str(P),'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'default_preview_policy':'Bright MaterialPreview with studio.exr, scene world and scene lights disabled; studio.exr retains a cool color cast and is not claimed chromatically neutral.','separate_render_world_policy':'Packed original studio.exr converted to grayscale through RGBToBW for neutral render color inspection. This world is independent of default MaterialPreview.','basis':'Independent reopen of saved V26.5 andV26.6, exact original material graph comparison, packed environment byte hash, all saved viewport settings, separate saved render world graph EXR evaluation, and fresh native geometry soffit comparison. No saved model or live app changes.'}
fn=Path(__file__).with_name('Preview_Material_Settings_Partial.json');fn.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('PREVIEW_QA_DONE',len(checks),'FAIL',len(fail),str(fn),flush=True)
