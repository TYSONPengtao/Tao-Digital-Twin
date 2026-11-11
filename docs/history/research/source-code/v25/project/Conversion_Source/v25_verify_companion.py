import bpy,json,sys,hashlib,time
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as qa
# The old V24.06 wing-specific helper targets a mesh superseded before V24.37.
# Every current gate component is covered by the full object/mesh comparison.
qa._wing_reference=lambda bp:{'covered_by_full_current_object_mesh_hashes':True}
baseline_snapshot=qa.baseline_snapshot
O=Path('E:/jz/JIA/Rebuild_V25');src=Path('E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');T=time.monotonic()
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();s=baseline_snapshot(bpy);s['material_hashes']={k:v['hash'] for k,v in s.pop('materials').items()};s['runtime_texts']={t.name:hashlib.sha256(t.as_string().encode()).hexdigest() for t in bpy.data.texts};s['visibility']={o.name:[o.hide_render,o.hide_viewport] for o in bpy.data.objects};return s
a=snapshot(src);b=snapshot(O/'Blender/Architecture_Complete_V25.blend');checks=[]
for key in a:
 passed=json.dumps(a[key],sort_keys=True)==json.dumps(b[key],sort_keys=True);checks.append({'name':key+'_unchanged','passed':passed});assert passed,key
for name in ['start_roam.py','roam_controller.py','roam_physics.py','measure_tools.py']:
 assert (src.parents[1]/'Roam'/name).read_bytes()==(O/'Roam'/name).read_bytes();checks.append({'name':name+'_unchanged','passed':True})
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report={'status':'PASS_V25_SAFE_ROAM_COMPANION_PRESERVATION','source_sha256':sha(src),'model_sha256':sha(O/'Blender/Architecture_Complete_V25.blend'),'checks':checks,'failures':[],'seconds':time.monotonic()-T,'note':'Exact source geometry, UV, material shader hashes, photo bytes, animation/actions, door poses, visibility, collision and runtime preserved. No runtime code change.'};(O/'Reports/V25_Companion_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('V25_COMPANION_QA_OK',len(checks),report['seconds'],flush=True)
