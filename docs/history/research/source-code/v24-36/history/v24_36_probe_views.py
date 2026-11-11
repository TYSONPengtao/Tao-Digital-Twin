from pathlib import Path
import bpy,json,numpy as np,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_36.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=1;sc.cycles.use_denoising=False;sc.render.resolution_x=2400;sc.render.resolution_y=1600;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard';sc.view_settings.exposure=0
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 imgs=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image]
 if mat.name.startswith(('M_PTJIA6_','M_MB7_','M_V14_ORIGINAL_EXTERIOR_'))and imgs:
  ns=mat.node_tree.nodes;out=next(n for n in ns if n.type=='OUTPUT_MATERIAL');em=ns.new('ShaderNodeEmission');mat.node_tree.links.new(imgs[0].outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
bounds=np.array(json.loads((R/'V24_36_Collision_Index.json').read_text())['all_bounds']);center=bounds.mean(0);c=bpy.data.objects.new('QA_Context_Top',bpy.data.cameras.new('QA_Context_Top'));sc.collection.objects.link(c);c.location=(center[0],center[1],1200.);c.rotation_euler=(0,0,0);c.data.type='ORTHO';c.data.ortho_scale=850.;c.data.clip_end=3000;sc.camera=c;sc.render.filepath=str(R/'V24_36_Context_Top.png');bpy.ops.render.render(write_still=True);(D/'Top_Projection.json').write_text(json.dumps({'center':center.tolist(),'width_m':850.,'resolution':[2400,1600]}));print('CONTEXT_TOP_DONE',flush=True)
