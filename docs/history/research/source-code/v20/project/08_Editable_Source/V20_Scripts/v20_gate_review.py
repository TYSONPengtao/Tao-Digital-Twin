import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V20');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'));sc=bpy.context.scene
ob=bpy.data.objects['V20_INSPECTION_Gate_Soffit'];ob.data.type='AREA';ob.data.energy=35;ob.data.shape='DISK';ob.data.size=3.0;ob.location=[6.6,-13.0,2.3];ob.rotation_euler=(Vector([6.6,-11.6,3.2])-ob.location).to_track_quat('-Z','Y').to_euler();sc.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'));sc.camera=bpy.data.objects['V20_Inner_Gate_Closed_Soffit'];sc.render.filepath=str(O/'06_Report/V20_Inner_Gate_Closed_Soffit.png');bpy.ops.render.render(write_still=True)
p=O/'06_Report/Interior_Inspection_Lighting.json';d=json.loads(p.read_text(encoding='utf8'));d['gate_light_revision']={'type':'AREA','energy_w':35,'size_m':3,'position_m':[6.6,-13.0,2.3],'purpose':'Even inspection illumination; not a physical as-built light fixture'};p.write_text(json.dumps(d,indent=2),encoding='utf8');print('GATE INSPECTION COMPLETE')
