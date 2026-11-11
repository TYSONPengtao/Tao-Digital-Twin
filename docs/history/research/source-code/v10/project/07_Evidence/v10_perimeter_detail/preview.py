import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).parent
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf8'))
M=json.loads((O/'Mutation.json').read_text(encoding='utf8'))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def linear(x):
 x=x/255;return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
mats={}
for name,properties in S['materials'].items():
 m=bpy.data.materials.new(name);m.diffuse_color=(*[linear(v) for v in properties['color']],1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=properties.get('roughness',.8)
 mats[name]=m
corner='--corner' in sys.argv
elements=[e for e in S['elements'] if e['name'] in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']]+M['replace']+M['add']
for e in elements:
 vv=[];ff=[];mi=[];names=[]
 for p in e['parts']:
  g=p['geometry'];v=g['vertices'];c=[sum(a[k] for a in v)/len(v) for k in range(3)]
  if not ((-27<c[0]<-22 and 2<c[1]<8) if corner else (-21<c[0]<-13 and 5<c[1]<10)):continue
  n=len(vv);vv+=v;ff += [[n+i for i in f] for f in g['faces']]
  if p['material'] not in names:names.append(p['material'])
  mi += [names.index(p['material'])]*len(g['faces'])
 if not vv:continue
 me=bpy.data.meshes.new(e['name']);me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(e['name'],me);sc.collection.objects.link(ob)
 for mat in names:me.materials.append(mats[mat])
 for polygon,m in zip(me.polygons,mi):polygon.material_index=m
world=bpy.data.worlds.new('Review_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.86,.9,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8;sc.world=world
sd=bpy.data.lights.new('Inspection_Sun','SUN');sd.energy=2.5;ob=bpy.data.objects.new('Inspection_Sun',sd);sc.collection.objects.link(ob);ob.rotation_euler=(.4,-.35,-.9)
cd=bpy.data.cameras.new('Perimeter_Finish_Review');cam=bpy.data.objects.new('Perimeter_Finish_Review',cd);sc.collection.objects.link(cam);cam.location=[-18,1.5,5.0];tar=Vector([-17.2,7.5,2.4]);cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=7;sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1500;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard';sc.render.film_transparent=False
if corner:
 cam.location=[-22.2,2.9,4.45];tar=Vector([-24.65,5.2,2.4]);cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=4.8
sc.render.filepath=str(O/('NW_Corner_Inside_Review.png' if corner else 'Perimeter_Detail_Review.png'));bpy.ops.render.render(write_still=True)
cam.location=[-18.2,4.8,5.25];tar=Vector([-17.25,7.6,3.24]);cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=3.05
if corner:
 cam.location=[-27.4,7.9,4.3];tar=Vector([-24.75,5.4,2.55]);cam.rotation_euler=(tar-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=4.8
sc.render.filepath=str(O/('NW_Corner_Outside_Review.png' if corner else 'Perimeter_Flower_Tile_Review.png'));bpy.ops.render.render(write_still=True)
print('Perimeter preview rendered',flush=True)
