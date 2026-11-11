import bpy,json,math
from mathutils import Vector
from pathlib import Path
O=Path(__file__).parent;D=json.loads((O/'Preview_Mesh.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for name,d in D['materials'].items():
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=tuple((x/255)**2.2 for x in d['color'])+(1,);bs.inputs['Roughness'].default_value=d.get('roughness',.8);bs.inputs['Metallic'].default_value=d.get('metallic',0);mats[name]=m
for d in D['nodes']:
    me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update();ob=bpy.data.objects.new(d['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(mats[d['material']])
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
sc.world.use_nodes=True;sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.72,.76,.84,1);sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25
bpy.ops.object.light_add(type='SUN',rotation=(.45,-.55,-.30));bpy.context.object.data.energy=1.8;bpy.context.object.data.angle=.20
bpy.ops.object.light_add(type='AREA',location=(8,-6,5));bpy.context.object.data.energy=700;bpy.context.object.data.size=6;bpy.context.object.rotation_euler=(Vector((2,-5,1))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
sc.view_settings.view_transform='AgX';sc.view_settings.exposure=-.20
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.452));bpy.context.object.data.materials.append(mats['M_Stone'])
for name,eye,target in [('V11_Pavilion_East_Southeast',[10,-12,5],[2.4,-5.35,1.2]),('V11_Pavilion_East_Underside',[10,-1,2.45],[2.4,-5.35,1.4]),('V11_Pavilion_Roof_Plan',[2.46,-5.35,10],[2.46,-5.35,0])]:
    bpy.ops.object.camera_add(location=eye);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=45
    if name.endswith('Plan'):c.data.type='ORTHO';c.data.ortho_scale=5.4
    sc.camera=c;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'V11_Pavilion_Review.blend'))
