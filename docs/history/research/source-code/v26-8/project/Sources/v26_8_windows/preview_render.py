from pathlib import Path
import bpy,json,sys,numpy as np
from mathutils import Vector
BASE=Path(__file__).resolve().parent;P=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');prep=json.loads((BASE/'Prepared_Geometry.json').read_text('utf8'))
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
def put(row,d):
 o=bpy.data.objects[row['name']];a=np.load(d/row['file']);inv=np.array(o.matrix_world.inverted());v=np.column_stack([a['v'],np.ones(len(a['v']))])@inv.T
 m=bpy.data.meshes.new(row['name']+'_Window_Review');m.from_pydata(v[:,:3].tolist(),[],a['f'].tolist());m.materials.clear()
 for n in row['materials']:m.materials.append(bpy.data.materials[n])
 for poly,mi in zip(m.polygons,a['mi']):poly.material_index=int(mi)
 uv=m.uv_layers.new(name='UVMap');uv.data.foreach_set('uv',a['uv'].reshape(-1).tolist());m.update();o.data=m
for r in prep['objects']+prep['optional_f1_guard_rows']:put(r,BASE/'Prepared')
for n in prep['remove']:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
put(json.loads((BASE/'Preview/Preview_House.json').read_text('utf8')),BASE/'Preview')
sc.render.engine='CYCLES';sc.render.resolution_x=1150;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.cycles.samples=20;sc.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('F2_Sills_Stone_Rail',(6.5,-5.8,5.15),(6.5,1.1,4.35),27),('F1_Low_Sill',(5.3,-1.5,.95),(2.5,1.2,.5),25),('F3_High_Sill',(11.,4.8,8.8),(11.,1.1,8.8),22)]
for tag,pos,aim,lens in views:
 if '--f3-only'in sys.argv and tag!='F3_High_Sill':continue
 c=bpy.data.objects.new('Temp_'+tag,bpy.data.cameras.new('Temp_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;sc.camera=c
 ld=bpy.data.lights.new('Temporary_window_review_fill','AREA');ld.energy=150.;ld.shape='DISK';ld.size=2.;light=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler
 sc.render.filepath=str(BASE/'Preview'/f'{tag}.png');bpy.ops.render.render(write_still=True);print('WINDOW_PREVIEW',tag,flush=True);bpy.data.objects.remove(light,do_unlink=True);bpy.data.objects.remove(c,do_unlink=True)
print('NO_NATIVE_SAVED',flush=True)
