from pathlib import Path
import bpy,json,hashlib,numpy as np
W=Path(__file__).parent;D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1680;sc.render.resolution_y=1160;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.15
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for device in pref.devices:device.use=device.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
jobs=[('Kitchen_Wall_Eave','V24_35_01_Kitchen_East'),('Kitchen_Wall_Close','V24_35_02_Kitchen_East_Close'),('House_And_Context','V24_37_02_House_And_PTJIA6'),('Expanded_Context','V24_37_01_Expanded_Context_Overview'),('PTJIA6_Road_Eye','V24_37_04_PTJIA6_Road_Eye'),('PTJIA6_Field','V24_37_05_PTJIA6_Field_Context')]
for tag,cam in jobs:
 sc.camera=bpy.data.objects[cam];name='V24_37_'+tag+'.png';sc.render.filepath=str(R/name);bpy.ops.render.render(write_still=True);(R/(name[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':name,'camera':cam,'frame':40,'samples':24,'draft':False,'mode':'Original native materials; Cycles'}));print('RENDER_DONE',tag,flush=True)
# Independent plan view of the original packed photographs, without relighting
# already photographed terrain. This is a read-only QA rendering, not a saved
# material change to the native delivery.
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 imgs=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image]
 if mat.name.startswith(('M_PTJIA6_','M_MB7_','M_V14_ORIGINAL_EXTERIOR_'))and imgs:
  ns=mat.node_tree.nodes;out=next(n for n in ns if n.type=='OUTPUT_MATERIAL');em=ns.new('ShaderNodeEmission');mat.node_tree.links.new(imgs[0].outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
sc.cycles.samples=1;sc.cycles.use_denoising=False;sc.view_settings.view_transform='Standard';sc.view_settings.exposure=0;sc.render.resolution_x=2400;sc.render.resolution_y=1600;meta=json.loads((W/'v24_36/Top_Projection.json').read_text());cx,cy,_=meta['center'];c=bpy.data.objects.new('QA_Clean_Context_Top',bpy.data.cameras.new('QA_Clean_Context_Top'));sc.collection.objects.link(c);c.location=(cx,cy,1200.);c.rotation_euler=(0,0,0);c.data.type='ORTHO';c.data.ortho_scale=850.;c.data.clip_end=3000.;sc.camera=c;name='V24_37_Clean_Context_Top.png';sc.render.filepath=str(R/name);bpy.ops.render.render(write_still=True);(R/(name[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':name,'draft':False,'mode':'Read-only original photo emission plan, no native material changes saved','projection':meta}));print('CLEAN_TOP_RENDER_DONE',flush=True)
