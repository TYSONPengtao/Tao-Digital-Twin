import bpy,numpy as np,json,hashlib
from pathlib import Path
D=Path(__file__).parent/'v24_17';P=Path('E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend');names=['V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core']
with bpy.data.libraries.load(str(P),link=False)as(a,b):b.objects=list(names)
rows=[]
for n,o in zip(names,b.objects):
 bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@v.co for v in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'GATE_{len(rows):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':o.name,'file':fn})
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Gate_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':rows},indent=2));print('GATE_EXPORTED',len(rows),flush=True)
