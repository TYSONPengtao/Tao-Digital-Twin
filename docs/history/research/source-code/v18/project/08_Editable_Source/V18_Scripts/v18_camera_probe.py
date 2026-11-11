import bpy,math,json
from pathlib import Path
from mathutils import Vector
O=Path(r'E:/jz/JIA/Rebuild_V18');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V18_Readback_LOCAL.blend'));sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();target=Vector([17.9,-15.8,-.35])
poses=[[x,y,-3.10] for x in [17.5,19,21,23,25] for y in [-24,-21,-19]];scores=[]
points=[[15.4,-16.3,-2.7],[17,-16.3,-1.8],[19.7,-16.3,-2],[17,-16.0,0],[17,-15.6,1.7],[20.8,-15.3,0]]
for pos in poses:
 orig=Vector(pos);rows=[];score=0
 for pp in points:
  hit,loc,norm,face,ob,mat=sc.ray_cast(dg,orig,(Vector(pp)-orig).normalized());name=ob.name if hit else 'NONE';good=hit and 'ORIGINAL_EXTERIOR' not in name and 'TREE' not in name;score+=good;rows.append(name)
 scores.append({'pos':pos,'score':score,'hits':rows})
scores.sort(key=lambda r:r['score'],reverse=True);print(json.dumps(scores,indent=2),flush=True);sc.cycles.samples=12;sc.render.resolution_x=1100;sc.render.resolution_y=800;sc.render.resolution_percentage=100
choices=[scores[0]['pos'],[21,-21,-3.10],[17.5,-21,-3.1]]
for k,pos in enumerate(choices):
 name='V18_Camera_Probe_'+str(k);cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(86 if Vector(pos).xy.length<26 else 72);sc.camera=cam;sc.render.filepath=str(O/'06_Report'/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PROBE DONE',flush=True)
