import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;A=json.loads((P/'Preview_Geometry.json').read_text());bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);mats={}
for name,spec in A['materials'].items():
 m=bpy.data.materials.new(name);m.diffuse_color=(*[x/255 for x in spec['color']],1);m.use_nodes=True;m.node_tree.nodes.clear();n=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(n.outputs['BSDF'],out.inputs['Surface']);n.inputs['Base Color'].default_value=m.diffuse_color;n.inputs['Roughness'].default_value=.75;mats[name]=m
for e in A['elements']:
 for row in e['meshes']:
  me=bpy.data.meshes.new(e['name']);me.from_pydata(row['vertices'],[],row['faces']);me.update();ob=bpy.data.objects.new(e['name'],me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mats[row['material']])
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=1250;sc.render.resolution_y=850;sc.render.resolution_percentage=100
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.9,.92,.94,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.75
ld=bpy.data.lights.new('Sun','SUN');ld.energy=2.1;lo=bpy.data.objects.new('Sun',ld);bpy.context.collection.objects.link(lo);lo.rotation_euler=(.4,-.5,-.25)
cam=bpy.data.cameras.new('Camera');ob=bpy.data.objects.new('Camera',cam);bpy.context.collection.objects.link(ob);sc.camera=ob;cam.lens=45
for name,pos,target in [('V8_Kitchen_Gate_Roofs',[1,-22,9],[8.8,-10,3.2]),('V8_Screenwall_Flying_Eaves',[6.8,-25.7,6.5],[7,-16.9,3.45])]:
 ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(name+'.png'));bpy.ops.render.render(write_still=True)
