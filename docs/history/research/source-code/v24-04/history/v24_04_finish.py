import bpy,json,sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_04_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));base=json.loads((R/'V24_04_Before_Snapshot.json').read_text(encoding='utf8'));removed=[]
for k in ['materials','images']:
 for d in list(getattr(bpy.data,k)):
  if d.name in base[k]or(k=='images'and d.type in ['RENDER_RESULT','COMPOSITING']):continue
  d.use_fake_user=False
  if d.users==0:removed.append(k+':'+d.name);getattr(bpy.data,k).remove(d)
for k in ['meshes','collections']:
 for d in list(getattr(bpy.data,k)):
  if d.users==0:getattr(bpy.data,k).remove(d)
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
build=json.loads((R/'V24_04_Build.json').read_text(encoding='utf8'));build['sha256']=sha(P);build['unused_import_assets_removed']=removed;write('V24_04_Build.json',build);print('FINISHED',len(removed),flush=True)
