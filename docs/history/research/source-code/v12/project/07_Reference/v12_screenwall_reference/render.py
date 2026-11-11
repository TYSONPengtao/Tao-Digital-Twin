import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
S=json.loads((O/'Preview_Scene.json').read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={}
for name,spec in S['materials'].items():
 m=bpy.data.materials.new(name);m.diffuse_color=tuple((c/255)**2.2 for c in spec['color'])+(1,);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=spec.get('roughness',.6);mats[name]=m
def data(g):
 if g['type']=='polyhedron':return g['vertices'],g['faces']
 x,y,z=g['origin'];w,d,h=g['size']
 return [[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z],[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]],[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
groups={}
for e in S['elements']:
 for j,p in enumerate(e['parts']):
  v,f=data(p['geometry']);key=p['material'];verts,faces=groups.setdefault(key,([],[]));offset=len(verts);verts.extend(v);faces.extend([[i+offset for i in face] for face in f])
for key,(v,f) in groups.items():
 me=bpy.data.meshes.new(key);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(key,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mats[key])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.35,.35,.35);scene.view_settings.view_transform='Standard'
bpy.ops.object.light_add(type='AREA',location=(3,-20,11));light=bpy.context.object;light.data.energy=1800;light.data.shape='DISK';light.data.size=10
bpy.ops.object.light_add(type='AREA',location=(15,-13,7));bpy.context.object.data.energy=900;bpy.context.object.data.size=7
camera_data=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',camera_data);bpy.context.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO'
for name,pos,target,scale in [('Front',(7.025,-31,5),(7.025,-16.9,2.4),10.6),('End',(17,-21,6),(10.2,-16.9,3.8),5.8),('Roof',(15,-25,13),(7.025,-16.9,3.1),11.8),('DripDetail',(7.025,-22,4),(7.025,-17.63,3.65),1.5)]:
 camera.location=pos;direction=Vector(target)-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=scale;scene.render.filepath=str(O/f'V12_Screenwall_{name}.png');bpy.ops.render.render(write_still=True)
