import bpy,sys,json
from pathlib import Path
W=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work');sys.path.insert(0,str(W))
from v24_roof_detail_blender import apply_v24_roof_detail
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend')
r=apply_v24_roof_detail(bpy,W/'v24_roof_detail_probe');print(json.dumps(r),flush=True)
# Same top/junction cameras as the read-only before comparison; no blend save.
from mathutils import Vector
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
for name,pos,tar in [('V24_Roof_After',[7.2,-14.4,5.6],[6.8,-11.53,2.9]),('V24_Junction_After',[9.7,-13.4,4.0],[8.65,-11.72,2.85])]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40;sc.camera=cam;sc.render.filepath=str(W/'v24_roof_detail_probe'/(name+'.png'));bpy.ops.render.render(write_still=True)
