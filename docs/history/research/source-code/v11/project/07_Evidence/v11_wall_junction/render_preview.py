import bpy,json,math
from mathutils import Vector
from pathlib import Path
O=Path(__file__).parent
D=json.loads((O/'Preview_Mesh.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for name,data in D['materials'].items():
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=tuple((x/255)**2.2 for x in data['color'])+(1,);b.inputs['Roughness'].default_value=data.get('roughness',.8);materials[name]=m
for d in D['nodes']:
    me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update();ob=bpy.data.objects.new(d['name'],me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[d['material']])
bpy.ops.mesh.primitive_plane_add(size=32,location=(4,-5,-.45));p=bpy.context.object;p.name='Preview_Ground';m=bpy.data.materials.new('ground');m.diffuse_color=(.20,.21,.19,1);p.data.materials.append(m)
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1400;sc.render.resolution_y=1050;sc.render.resolution_percentage=100
sc.world.use_nodes=True;sc.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.65,.72,.85,1);sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.7
bpy.ops.object.light_add(type='SUN',rotation=(math.radians(25),math.radians(-25),math.radians(-20)));bpy.context.object.data.energy=2.4;bpy.context.object.data.angle=math.radians(12)
sc.view_settings.view_transform='AgX'
for name,eye,target in [('V11_Right_Angle_Wall_Close',[3.1,-8.4,4.0],[.55,-11.1,1.6]),('V11_Inner_Wall_Outside_Corner',[-2,-14,3.8],[.3,-11.4,1.3])]:
    bpy.ops.object.camera_add(location=eye);c=bpy.context.object;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=43;sc.camera=c;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Courtyard_Detail_Review.blend'))
