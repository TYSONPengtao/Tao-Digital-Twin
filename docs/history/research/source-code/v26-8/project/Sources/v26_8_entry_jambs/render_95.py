from pathlib import Path
import bpy,sys,json
from mathutils import Vector
W=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent/'Candidate_95mm';P=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');sys.path.insert(0,str(W/'np1'));import numpy as np
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.render.resolution_x=1100;sc.render.resolution_y=1050;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.cycles.samples=24;sc.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except:pass
views=[('F1_Door_Bay_Right',[7.9,.40,1.15],[9.13,2.06,1.3],44),('F2_Door_Bay_Right',[7.8,.40,5.05],[9.13,2.06,5.2],44),('F3_Window_Bay_Right',[7.8,.40,8.65],[9.13,2.06,8.8],44)]
views=views[:1]
for stage in ['After']:
 if stage=='After':
  prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));r=prep['objects'][0];a=np.load(D/r['file']);o=bpy.data.objects[r['name']];me=bpy.data.meshes.new('EntryJambReview');me.from_pydata(a['v'].tolist(),[],a['f'].tolist());me.update()
  for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
  for p,mi in zip(me.polygons,a['mi']):p.material_index=int(mi)
  o.data=me
 for tag,pos,aim,lens in views:
  c=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;sc.camera=c
  ld=bpy.data.lights.new('ReviewFill','AREA');ld.energy=75;ld.shape='DISK';ld.size=2;light=bpy.data.objects.new('ReviewFill',ld);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler
  sc.render.filepath=str(D/(stage+'_'+tag+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);bpy.data.objects.remove(light,do_unlink=True);print('RENDER_DONE',stage,tag,flush=True)
