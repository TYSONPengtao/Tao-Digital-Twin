from pathlib import Path
import bpy,json,hashlib,numpy as np
W=Path(__file__).parent;D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend';bpy.ops.wm.open_mainfile(filepath=str(P));a=np.load(D/'Final_Collision.npz');o=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_37_Final_Cleaned_Real_Surfaces');me.from_pydata(a['v'],[],a['f']);me.update();old=o.data;o.data=me
if old.users==0:bpy.data.meshes.remove(old)
o['V24_37_Retention_Boundary_Clipped']=True;bpy.context.scene.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
q=json.loads((R/'V24_37_Build.json').read_text());q.update(sha256=h,boundary_clip_pending=False);(R/'V24_37_Build.json').write_text(json.dumps(q,indent=2));print('V37_FINAL_NATIVE',h,flush=True)
