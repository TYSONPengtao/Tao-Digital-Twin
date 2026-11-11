import bpy,json
from pathlib import Path
O=Path('E:/jz/JIA/Rebuild_V21')
bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V21_Readback_LOCAL.blend'))
sc=bpy.context.scene
for name,power in [('V20_INSPECTION_F1_Hall',100),('V20_INSPECTION_F1_Rear',60)]:
 bpy.data.objects[name].data.energy=power
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V21_Readback_LOCAL.blend'))
names=['V21_House_Sliding_Entry','V21_Inner_Gate_Reference_Front','V21_Inner_Gate_Kitchen_Flush_Junction','V21_Inner_Gate_Reference_Underside','V21_Kitchen_Gallery_Paving']
for n in names:
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(O/'06_Report'/f'{n}.png');bpy.ops.render.render(write_still=True)
 print('FINAL LIGHTING',n,flush=True)
p=O/'06_Report/Interior_Inspection_Lighting.json';d=json.loads(p.read_text());d['f1_inspection_power_w']={'hall':100,'rear':60};d['rerendered_views']=names;p.write_text(json.dumps(d,indent=2))
print('FINAL LIGHTING COMPLETE',flush=True)
