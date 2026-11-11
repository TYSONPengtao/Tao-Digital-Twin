from pathlib import Path
import bpy,json,sys,hashlib
W=Path(__file__).parent
sys.path.insert(0,str(W))
from v24_06_common import snapshot
O=Path('E:/jz/JIA/Rebuild_V26_8')
D=W/'v26_8_perf'
P=O/'Blender/Architecture_Complete_V26_8_Fast.blend'


def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()


bpy.ops.wm.open_mainfile(filepath=str(P))
before=json.loads((D/'Preservation_Before.json').read_text('utf8'))
after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False))
(D/'Preservation_After.json').write_text(json.dumps(after,ensure_ascii=False),'utf8')
for group in ['materials','images']:
    differing=[n for n in before[group]if before[group][n]!=after[group].get(n)]
    for n in differing[:4]:
        if group=='images':print('PRESERVATION_DIFFERENCE',group,n,before[group][n],after[group].get(n),flush=True)
        else:print('PRESERVATION_DIFFERENCE',group,n,before[group][n]['hash'],after[group][n]['hash'],flush=True)
checks=[]


def ck(name,passed,**kw):checks.append(dict(check=name,pass_=bool(passed),**kw))


ck('All original objects, meshes, UVs, material slots, transforms, parents and visibility retained',
   before['objects']==after['objects'],objects=len(before['objects']))
audit=json.loads((D/'Audit_Before.json').read_text('utf8'))
visible={r['name']:r['visible']for r in audit['meshes_sorted']}
ck('Original viewport visibility of every native mesh retained',all(bpy.data.objects[n].visible_get()==v for n,v in visible.items()),meshes=len(visible))
ck('All material node graphs unchanged',before['materials']==after['materials'],materials=len(before['materials']))
ck('All original image pixels and packed bytes unchanged',before['images']==after['images'],images=len(before['images']))
ck('All animated actions unchanged',before['actions']==after['actions'],actions=len(before['actions']))
ck('Moving doors retain original poses at frames 1,20,40',before['door_poses']==after['door_poses'])
ck('Collision geometry and UV hash unchanged',before['objects']['V24_21_Navigation_Collision']==after['objects']['V24_21_Navigation_Collision'])
master=O/'Blender/Architecture_Complete_V26_8.blend'
ck('Corrected master file not overwritten',sha(master)=='e21a89f9b617a541790a383295266e852182c6b915559cddf93d070e7137da72')
ck('Physics code unchanged',bpy.data.texts['V24_21_碰撞控制.py'].as_string()==(O/'Roam/roam_physics.py').read_text('utf8'))
sc=bpy.context.scene
ck('Saved fast display uses Eevee and half-resolution interactive preview',sc.render.engine=='BLENDER_EEVEE'and sc.render.preview_pixel_size=='2')
ck('Overcast world and zero direct sun retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Fast controller and display profile embedded',bpy.data.texts['V24_21_漫游控制器.py'].as_string()==(O/'Roam/roam_controller_fast.py').read_text('utf8')and bool(bpy.data.texts.get('V26_8_流畅显示.py')))
bench=json.loads((D/'Viewport_Benchmark.json').read_text('utf8'))
for test in bench['controller_tests']:
    checks.append(dict(check=test['check'],pass_=test['pass'],evidence=test))
for view in ['court','stairs']:
    rows={r['profile']:r for r in bench['measurements']if r['view']==view}
    ck('Native moving viewport faster for '+view,rows['fast']['effective_fps']>rows['baseline']['effective_fps'],before_fps=rows['baseline']['effective_fps'],after_fps=rows['fast']['effective_fps'],viewport_pixels=rows['fast']['area_pixels'])
for c in checks:c['pass']=c.pop('pass_')
failures=[c for c in checks if not c['pass']]
report={'status':'PASS'if not failures else'FAIL','model':str(P),'model_sha256':sha(P),
        'source_model':str(master),'source_sha256':sha(master),'checks':checks,'failures':failures,
        'viewport_benchmark':bench,'scope':'Saved profile, full native asset preservation, native redraw comparisons and native modal walking tests. Frame rates are measured in the recorded window size with other running applications, not guaranteed across all hardware or display sizes.'}
(O/'Reports/V26_8_Performance_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('FAST_READBACK',report['status'],len(checks),len(failures),report['model_sha256'],flush=True)
if failures:raise AssertionError(failures)
