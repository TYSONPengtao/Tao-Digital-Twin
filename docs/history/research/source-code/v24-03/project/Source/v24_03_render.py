import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.7
light=bpy.data.lights.new('V24_03_Preview_Soft_Daylight','AREA');light.energy=1400;light.shape='DISK';light.size=8;lo=bpy.data.objects.new('V24_03_Preview_Soft_Daylight',light);sc.collection.objects.link(lo);lo.location=(4,-10,9);lo.rotation_euler=(Vector((8,-5,1.5))-lo.location).to_track_quat('-Z','Y').to_euler()
views=[]
for name,pos,tar,lens in [('V24_03_Gate_Front',(6.6,-15.75,1.65),(6.6,-11.9,1.9),19),('V24_03_Xieshan_Top',(10.8,-18.2,6.8),(6.9,-11.8,3.0),45),('V24_03_Kitchen_Rear_Single_Column',(4.7,-1.2,2.4),(8.7,-6.6,1.4),32),('V24_03_Kitchen_Rear_Closure',(15.,-.9,3.4),(10.3,-2.8,1.8),24),('V24_03_Gate_Left_Return',(3.6,-14.7,2.),(4.95,-11.7,1.1),46),('V24_03_Gate_Kitchen_Intersection',(8.4,-16.7,5.4),(8.2,-11.9,3.5),45)]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;views.append((name,name,20 if name=='V24_03_Gate_Front' else 40))
only=set(sys.argv[sys.argv.index('--only')+1:])if '--only'in sys.argv else set()
for label,name,frame in views:
 if only and label not in only:continue
 sc.frame_set(frame);sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/(label+'.png'));bpy.ops.render.render(write_still=True);print('COLOR VIEW',label,flush=True)
with P.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Preview_States.json').write_text(json.dumps({'model_sha256':h,'real_materials':True,'material_override':None,'views':[{'file':l+'.png','camera':n,'frame':f}for l,n,f in views],'saved_default_frame':40},indent=2),encoding='utf8')
rows=[];sc.frame_set(40);bpy.context.view_layer.update()
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 p=[ob.matrix_world@Vector(v)for v in ob.bound_box];lo=[min(v[i]for v in p)for i in range(3)];hi=[max(v[i]for v in p)for i in range(3)];rows.append({'name':ob.name,'bbox':[lo,hi]})
(R/'V24_03_Whole_Site_Inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print('V24.03 ALL COLOR VIEWS COMPLETE',flush=True)
