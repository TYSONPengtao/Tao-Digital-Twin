"""Create a separately saved fast viewport model; retain the corrected master exactly."""
from pathlib import Path
import bpy, sys, json, hashlib, shutil

W=Path(__file__).parent
sys.path.insert(0,str(W))
from v24_06_common import snapshot
from v26_20_fast_display import apply

D=W/'v26_20_perf'
O=Path('E:/jz/JIA/Rebuild_V26_20')
SRC=O/'Blender/Architecture_Complete_V26_20.blend'
P=O/'Blender/Architecture_Complete_V26_20_Fast.blend'
S=O/'Sources/Performance'
S.mkdir(exist_ok=True)


def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()


assert sha(SRC)==json.loads((O/'Reports/V26_20_Build.json').read_text('utf8'))['sha256']
bpy.ops.wm.open_mainfile(filepath=str(SRC))
bpy.context.preferences.filepaths.save_version=0
assert (W/'v26_20/Native_Snapshot_Source_SHA256.txt').read_text('utf8')==sha(SRC)
before=json.loads((W/'v26_20/Native_After_Snapshot.json').read_text('utf8'))
(D/'Preservation_Before.json').write_text(json.dumps(before,ensure_ascii=False),'utf8')
settings=apply()
# Preserve packed assets which are archived but no longer referenced by the active world.
for im in bpy.data.images:
    if im.source!='VIEWER'and im.type not in ['RENDER_RESULT','COMPOSITING']:
        im.use_fake_user=True
code=(D/'roam_controller_fast.py').read_text('utf8')
bpy.data.texts['V24_21_漫游控制器.py'].clear()
bpy.data.texts['V24_21_漫游控制器.py'].write(code)
display_text=bpy.data.texts.new('V26_20_流畅显示.py')
display_text.write((W/'v26_20_fast_display.py').read_text('utf8'))
start=(O/'Roam/start_roam.py').read_text('utf8')
start=start.replace('_prepared=False',"exec(compile(bpy.data.texts['V26_20_流畅显示.py'].as_string(),'<fast viewport display>','exec'),{'__name__':'__main__'})\n\n_prepared=False",1)
bpy.data.texts['V24_21_启动漫游.py'].clear()
bpy.data.texts['V24_21_启动漫游.py'].write(start)
(O/'Roam/start_roam_fast.py').write_text(start,'utf8')
(O/'Roam/roam_controller_fast.py').write_text(code,'utf8')
bpy.context.scene['V26_8_Display_Profile']='Fast overcast interactive; unchanged architectural data'
bpy.context.scene['V26_8_Fast_Source_SHA256']=sha(SRC)
bpy.context.scene.frame_set(40)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
(D/'Fast_Build.json').write_text(json.dumps({'source':str(SRC),'source_sha256':sha(SRC),
                                         'model':str(P),'model_sha256':sha(P),'settings':settings},ensure_ascii=False,indent=2),'utf8')
for n in ['v26_8_fast_display.py','v26_8_make_fast_controller.py','v26_8_build_fast.py','v26_8_perf_viewport_bench.py','v26_8_perf_audit.py']:
    shutil.copy2(W/n,S/n)
shutil.copy2(D/'Preservation_Before.json',S/'Preservation_Before.json')
print('FAST_MODEL_SAVED',sha(P),flush=True)
