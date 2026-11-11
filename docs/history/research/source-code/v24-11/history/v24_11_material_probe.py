import bpy,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_11/Blender/Architecture_Complete_V24_11.blend');sc=bpy.context.scene;sc.frame_set(40)
m=bpy.data.materials['M_V18_Storage_Dark_Courses'].copy();m.name='DIAG_Dark_Stone_No_Bump';bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for l in list(bs.inputs['Normal'].links):m.node_tree.links.remove(l)
o=bpy.data.objects['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry']
em=bpy.data.materials.new('DIAG_Fresh_Photo_Stone');em.use_nodes=True;nt=em.node_tree;nt.nodes.clear();tx=nt.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images['Photo_Dark_Stone_Courses.png'];uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=o.data.uv_layers.active.name;nt.links.new(uv.outputs[0],tx.inputs[0]);e=nt.nodes.new('ShaderNodeBsdfDiffuse');e.inputs['Roughness'].default_value=.9;nt.links.new(tx.outputs['Color'],e.inputs['Color']);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
for i,ma in enumerate(o.material_slots):
 print('SLOT',i,ma.link,ma.material.name,flush=True)
 mm=bpy.data.materials.new('DIAG_Index_'+str(i));mm.use_nodes=True;nn=mm.node_tree;nn.nodes.clear();ee=nn.nodes.new('ShaderNodeEmission');ee.inputs['Color'].default_value=(1,.03,.03,1)if i==0 else(.03,.03,1,1);oo=nn.nodes.new('ShaderNodeOutputMaterial');nn.links.new(ee.outputs[0],oo.inputs[0]);ma.material=mm
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100
for name,pos,target,power,size in [('D_Soft',(15,-15,10),(15,-14,.5),1300,8),('D_Fill',(10,-20,5),(15,-14,.5),650,6),('D_Back',(18,-4,7),(14,-8,1),750,7)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
sc.camera=bpy.data.objects['V24_11_Kitchen_Continuous_Wall'];sc.render.use_border=True;sc.render.use_crop_to_border=True;sc.render.border_min_x=.25;sc.render.border_max_x=.58;sc.render.border_min_y=.18;sc.render.border_max_y=.52;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(W/'v24_11/DIAGNOSTIC_Base_Index.png');bpy.ops.render.render(write_still=True)
