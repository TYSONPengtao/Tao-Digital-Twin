import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work/v24_roof_probe');O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend')
rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 if not any(t in ob.name for t in ['GATE_REFERENCE_LAYER_09','GATE_REFERENCE_LAYER_10','GATE_REFERENCE_LAYER_14','Sculpted_Wings','GABLE','KITCHEN','ROOF','Ridge','ridge']):continue
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 if hi[0]<3.5 or lo[0]>13 or hi[1]<-13.5 or lo[1]>-10.:continue
 rows.append({'name':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),'bbox':[lo,hi],'materials':[m.name if m else None for m in ob.data.materials],'uv':[u.name for u in ob.data.uv_layers],'modifiers':[(m.name,m.type) for m in ob.modifiers]})
(O/'Roof_Audit.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows))
# Show the exact current gate roof and kitchen interface with existing material.
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
for name,pos,tar in [('V24_Roof_Audit',[7.2,-14.4,5.6],[6.8,-11.53,2.9]),('V24_Junction_Audit',[9.7,-13.4,4.0],[8.65,-11.72,2.85])]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=40;sc.camera=cam;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
