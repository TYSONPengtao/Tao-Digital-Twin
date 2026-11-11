import bpy,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent));from v24_07_common import *
from v24_07_doors import improve_doors
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;d=improve_doors(bpy);base=json.loads((R/'V24_07_Before_Snapshot.json').read_text(encoding='utf8'));allnames=d['changed_objects']+d['added_objects'];d['changed_objects']=[n for n in allnames if n in base['objects']];d['added_objects']=[n for n in allnames if n not in base['objects']];write('V24_07_Doors.json',d)
delta=json.loads((R/'V24_07_Changes.json').read_text(encoding='utf8'));delta['doors']=d
for n in allnames:delta['expected_mesh_hashes'][n]=q._mesh_hash(bpy.data.objects[n].data)
write('V24_07_Changes.json',delta)
c=bpy.data.objects['V24_07_Gate_Whole'];c.location=(6.6,-15.9,2.1);target=Vector((6.6,-11.582,1.95));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=19;sc.camera=c;sc.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
b=json.loads((R/'V24_07_Build.json').read_text(encoding='utf8'));b['sha256']=sha(P);b['doors']=d;b['default_camera_fitted_inside_screenwall']=True;write('V24_07_Build.json',b);print('CONTINUOUS WOOD FRAME AND DEFAULT CAMERA FITTED',flush=True)
