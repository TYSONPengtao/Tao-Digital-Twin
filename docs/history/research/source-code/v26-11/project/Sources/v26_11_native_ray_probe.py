import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_11_views import VIEWS
D=W/'v26_11';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_11/Blender/Architecture_Complete_V26_11.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1100;sc.render.resolution_y=900;sc.render.resolution_percentage=100;out=[]
for tag,pos,aim,lens in VIEWS[:2]:
 c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;bpy.context.view_layer.update();frame=c.data.view_frame(scene=sc);xmin=min(p.x for p in frame);xmax=max(p.x for p in frame);ymin=min(p.y for p in frame);ymax=max(p.y for p in frame);z=frame[0].z;pixels=[(x,y)for x in range(640,686,6)for y in range(370,423,6)]if tag.startswith('01')else[(x,y)for x in range(1000,1071,8)for y in range(530,768,12)]
 for px,py in pixels:
  v=Vector((xmin+(xmax-xmin)*px/1100,ymin+(ymax-ymin)*(1-py/900),z));direction=(c.matrix_world.to_3x3()@v).normalized();hit,point,normal,fi,obj,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,direction)
  if hit:out.append({'tag':tag,'pixel':[px,py],'object':obj.name,'face':fi,'world_m':list(point),'normal':list(normal),'material':obj.data.materials[obj.data.polygons[fi].material_index].name if obj.type=='MESH'and fi<len(obj.data.polygons)else None})
 bpy.data.objects.remove(c,do_unlink=True)
(D/'Pixel_Ray_Attribution.json').write_text(json.dumps(out,indent=2),'utf8');print('RAY_OBJECTS',sorted(set(r['object']for r in out)),flush=True)
for o in bpy.data.objects:
 if o.name.startswith('V26_11_Gate_Gray_Relief_'):
  attr=o.data.attributes.get('sharp_edge')
  if attr:attr.data.foreach_set('value',np.zeros(len(attr.data),bool))
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
tag,pos,aim,lens=VIEWS[7];c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;sc.camera=c;sc.render.filepath=str(D/'Diagnosis/Gray_Relief_Smooth_Test.png');bpy.ops.render.render(write_still=True)
