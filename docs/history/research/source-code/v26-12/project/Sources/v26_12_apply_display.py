import bpy,sys,json,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_12_fast_display import set_local_ao
O=Path('E:/jz/JIA/Rebuild_V26_12');P=O/'Blender/Architecture_Complete_V26_12.blend';bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;settings=set_local_ao(sc)
ch=json.loads((O/'Reports/V26_12_Changes.json').read_text('utf8'));ch['display_cause']='Verified with identical actual geometry and lights: disabling EEVEE local occlusion flattens the stone fields to white plates. Ambient-occlusion-only Fast GI restores carving contrast. Whole-gate photo crops additionally lost V24 motif detail.';ch['local_ao']=settings
note=bpy.data.texts['V26_12_门楼修正说明'];note.write('\n实际白板显示根因：流畅版关闭EEVEE局部遮蔽。相同网格/灯光A/B测试已复现，启用局部AO恢复雕刻。半分辨率、8采样、2条AO光线、8步、20cm范围；无需增加实时细分。')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
ch['display_only_save']=True;(O/'Reports/V26_12_Changes.json').write_text(json.dumps(ch,ensure_ascii=False,indent=2),'utf8')
(O/'Reports/V26_12_Build.json').write_text(json.dumps({'model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'bytes':P.stat().st_size,'blender':bpy.app.version_string},indent=2),'utf8');print('DISPLAY_FIXED_SAVED',settings,flush=True)
