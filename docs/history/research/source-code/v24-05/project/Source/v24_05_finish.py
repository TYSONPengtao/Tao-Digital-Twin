"""Remove coplanar faces where the new neck meets the retained carved lintel."""
import bpy,json,sys
from mathutils import Vector
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_05_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));names=[]
for k,(x0,x1)in enumerate([(4.9333333333,5.4571428571),(7.7428571429,8.2666666667)]):
 n='V24_05_Gate_Upper_Pier_Bearing_'+str(k+1);o=bpy.data.objects[n];poly=[(x0,-11.78),(x0+.09,-11.87),(x1-.09,-11.87),(x1,-11.78),(x1,-11.294),(x0,-11.294)];cx=(x0+x1)/2;cy=(-11.87-11.294)/2
 for i,v in enumerate(o.data.vertices):
  x,y=poly[i%6];v.co.x=x+(.001 if x<cx else-.001);v.co.y=y+(.001 if y<cy else-.001)
 o.data.update();names.append(n)
n='V24_05_Gate_Plain_Neck_Above_Carved_Lintel';o=bpy.data.objects[n]
for v in o.data.vertices:
 if v.co.y>-11.5:v.co.y=-11.370
 if v.co.z<2.70:v.co.z=2.688
o.data.update();names.append(n)
delta=json.loads((R/'V24_05_Changes.json').read_text(encoding='utf8'))
for n in names:delta['expected_mesh_hashes'][n]=q._mesh_hash(bpy.data.objects[n].data)
delta['bearing_finish']='New neck starts at 2.688m and the courtyard face is 12mm proud of the retained lintel; pier bearing sides inset 1mm to avoid coplanar overlap';write('V24_05_Changes.json',delta)
c=bpy.data.objects['V24_05_Gate_Raised_Review'];c.data.lens=22;c.rotation_euler=(Vector((6.6,-11.9,2.35))-c.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);build=json.loads((R/'V24_05_Build.json').read_text(encoding='utf8'));build['sha256']=sha(P);build['bearing_finish']=delta['bearing_finish'];write('V24_05_Build.json',build);print('BEARING FINISH SAVED',flush=True)
