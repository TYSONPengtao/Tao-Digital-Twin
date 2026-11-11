import bpy,json,hashlib,sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_qa_blender import _mesh_hash
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P))
n='SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry';ob=bpy.data.objects[n];wm=ob.matrix_world;inv=wm.inverted();moved=0
for v in ob.data.vertices:
 p=wm@v.co
 if p.y> -2.94:
  t=max(0,min(1,(p.y+2.94)/(-2.834009885787964+2.94)));p.y+=.06401*t;v.co=inv@p;moved+=1
ob.data.update();ob['V24_03_Rear_Wall_Bearing']='Rear lintel end extended 64 mm to key 15 mm into the new rear masonry wall; original material and UV retained'
delta=json.loads((R/'V24_03_Changes.json').read_text(encoding='utf8'));delta['expected_mesh_hashes'][n]=_mesh_hash(ob.data);k=delta['module_reports']['kitchen'];k['changed_old_objects']=[n];k['rear_lintel_bearing']={'object':n,'extended_m':.06401,'new_end_y_m':-2.7699998858,'masonry_embed_m':.015,'vertices_moved':moved};k['corrections'].append('Rear lintel now keys into closed rear wall, removing previous 49 mm unsupported end gap')
(R/'V24_03_Kitchen_Additional_Fixes.json').write_text(json.dumps(k,ensure_ascii=False,indent=2),encoding='utf8');(R/'V24_03_Changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);b=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'))
with P.open('rb') as f:b['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Build.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf8');print('REAR LINTEL SUPPORTED',moved,flush=True)
