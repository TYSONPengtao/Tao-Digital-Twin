# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
W=Path(__file__).parent;out=W/'evidence_v3';out.mkdir(exist_ok=True)
for name,p,origin in [('JIA_OBJ1',r'D:\AJAVIS01\ContextCapture\CASES\JIA\Productions\Production_OBJ\Data\Model\Model.obj',(-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002)),('PTHOUSE',r'D:\AJAVIS01\ContextCapture\CASES\PTHOUSE\Productions\PTHouse\Data\Model\Model.obj',(-7.5,4.65,1364.4))]:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.obj_import(filepath=p,forward_axis='Y',up_axis='Z');R=Matrix.Rotation(-math.radians(19.65),4,'Z');org=Vector(origin)
 for ob in list(bpy.context.selected_objects):
  for v in ob.data.vertices:v.co=R@(v.co-org)
 for mat in bpy.data.materials:
  if not mat.use_nodes:continue
  nt=mat.node_tree;tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE'),None)
  if tex:
   em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL').inputs[0])
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.view_settings.view_transform='Standard';scene.render.image_settings.file_format='PNG';scene.render.resolution_x=1800;scene.render.resolution_y=1800
 cd=bpy.data.cameras.new('ReferenceCamera');cam=bpy.data.objects.new('ReferenceCamera',cd);scene.collection.objects.link(cam);cam.location=(-3,-6,65);cd.type='ORTHO';cd.ortho_scale=52;scene.camera=cam
 scene.render.filepath=str(out/(name+'_Plan_Approx.png'));bpy.ops.render.render(write_still=True)
 cd.type='PERSP';cd.lens=30;cam.location=(-35,-36,27);cam.rotation_euler=(Vector((-3,-5,1))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.filepath=str(out/(name+'_SW_Approx.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(W/(name+'_Reference_Local_Approx.blend')))
 print('Source view',name,'Approximate placement; not metric approved',flush=True)
