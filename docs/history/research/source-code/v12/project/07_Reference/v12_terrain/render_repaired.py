import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent;P=Path(r'E:\jz\JIA\Rebuild_V12')
bpy.ops.wm.open_mainfile(filepath=str(P/'05_Export/Complete_Site_V12_LOCAL.blend'))
sc=bpy.context.scene;M=json.loads((D/'Mutation.json').read_text())
for ob in list(bpy.data.objects):
 if ob.name.startswith(('SITE_V12_REBUILT_','SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP')):bpy.data.objects.remove(ob,do_unlink=True)
for e in M['add']:
 g=e['parts'][0]['geometry'];v=g['vertices'];f=g['faces'];mat=e['parts'][0]['material'];me=bpy.data.meshes.new(e['name']);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(e['name']+'_Geometry',me);sc.collection.objects.link(ob);me.materials.append(bpy.data.materials[mat]);uv=me.uv_layers.new(name='Modeled_Metre_UV')
 for p in me.polygons:
  if 'EARTH' in e['name']:p.use_smooth=p.normal.z>.35
  for j in p.loop_indices:
   co=me.vertices[me.loops[j].vertex_index].co;uv.data[j].uv=(co.x,co.y) if abs(p.normal.z)>.35 else ((co.y,co.z) if abs(p.normal.x)>.5 else (co.x,co.z))
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
sc.camera=bpy.data.objects['V12_Entrance_Ramp'];sc.render.filepath=str(D/'Entrance_Ramp_Repaired_Preview.png');bpy.ops.render.render(write_still=True)
cd=bpy.data.cameras.new('V12_Ramp_Road_Approach_Repaired');cam=bpy.data.objects.new('V12_Ramp_Road_Approach_Repaired',cd);sc.collection.objects.link(cam);cam.location=[-21.5,-16,1.4];target=Vector([-15.5,-11.4,-.8]);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(60);sc.camera=cam;sc.render.filepath=str(D/'Entrance_Ramp_Road_Approach_Repaired.png');bpy.ops.render.render(write_still=True)
print('Repaired previews rendered',flush=True)
