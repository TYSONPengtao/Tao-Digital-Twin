import bpy,json,math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V21/05_Export/Actual_Rhino_V21_Readback_LOCAL.blend')
sc=bpy.context.scene
lights=[]
for o in bpy.data.objects:
 if o.type=='LIGHT':lights.append({'name':o.name,'type':o.data.type,'power':o.data.energy,'pos':list(o.location),'size':getattr(o.data,'size',None),'rotation':list(o.rotation_euler),'visible_camera':getattr(o,'visible_camera',None)})
(D/'Preview_Light_Inventory.json').write_text(json.dumps(lights,indent=2))
for name,pos,power in [('Review_F3_Landing',[7.1,8.3,9.75],130),('Review_F3_Terrace',[2,6,9.4],130)]:
 ld=bpy.data.lights.new(name,'POINT');ld.energy=power;ld.shadow_soft_size=1.1;ob=bpy.data.objects.new(name,ld);sc.collection.objects.link(ob);ob.location=pos
for ob in bpy.data.objects:
 if ob.type=='LIGHT':
  ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False
cams=[['landing',[6.8,8.65,9.0],[9.1,7.0,8.55],86],['terrace',[1.45,4.2,8.95],[3.82,6.30,8.70],78]]
sc.render.resolution_x=1100;sc.render.resolution_y=760;sc.render.resolution_percentage=100;sc.cycles.samples=10;sc.cycles.use_denoising=True
for name,pos,tar,fov in cams:
 cam=sc.camera;cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.angle=math.radians(fov)
 sc.render.filepath=str(D/('review_final_'+name+'.png'));bpy.ops.render.render(write_still=True)
print('DONE')
