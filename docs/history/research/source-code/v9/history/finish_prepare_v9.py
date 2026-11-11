import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;V8=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((W/'v9_current_baseline_check.json').read_text(encoding='utf-8'));assert not q['added_ids'] and not q['changed_geometry']
cur=V8/'04_Rhino/Reality_Hybrid_V8.3dm';assert sha(cur)==q['current_sha256']
snapshot=O/'01_Source/V8_Current_Before_V9.3dm';shutil.copy2(cur,snapshot);assert sha(snapshot)==q['current_sha256']
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));names={r['name'] for r in I}
deleted=set()
for r in q['removed_objects']:
 hit=next((n for n in names if r['name']==n or r['name'].startswith(n+'__')),None)
 assert hit is not None,r
 deleted.add(hit)
assert deleted=={'BEAM_X_F3_2.1_0'}
I=[r for r in I if r['name'] not in deleted];(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';S=json.loads(p.read_text(encoding='utf-8'));S['elements']=[e for e in S['elements'] if e['name'] not in deleted];S['v9_current_native_retired_elements']=sorted(deleted);p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
q['scope']='Only kitchen/gate roof relationship and visible eave layers; preserve current V8 deletion of BEAM_X_F3_2.1_0'
q.update(baseline_scene_sha256=sha(p),original_source_sha256=sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'),working_source_sha256=sha(O/'01_Source/Pure_Site_WORKING_V8.3dm'),baseline_V8_editable_sha256=sha(V8/'04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm'))
(O/'06_Report/V9_Baseline_Hashes.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(W/'v9_current_baseline_check.json',O/'06_Report/V8_Current_Versus_Delivered.json')
for src,dst in [('build_v8_patch.py','build_v9_patch.py'),('export_v8_native.py','export_v9_native.py'),('export_v8_editable.py','export_v9_editable.py'),('rhino_validate_v8.py','rhino_validate_v9.py'),('align_editable_rhino_v8.py','align_editable_rhino_v9.py'),('check_v8_exchange_photos.py','check_v9_exchange_photos.py')]:
 text=(W/src).read_text(encoding='utf-8').replace('Rebuild_V8_Hybrid','Rebuild_V9_Hybrid').replace('Reality_Hybrid_V8','Reality_Hybrid_V9').replace('Architecture_Edit_V8','Architecture_Edit_V9').replace('V8_','V9_').replace('V8 corrected','V9 corrected').replace('V8 LOCAL','V9 LOCAL')
 if src=='build_v8_patch.py':text=text.replace("V6=Path(r'E:\\jz\\JIA\\Rebuild_V7_Hybrid')","V6=Path(r'E:\\jz\\JIA\\Rebuild_V8_Hybrid')")
 (W/dst).write_text(text,encoding='utf-8')
print('Prepared V9 from current V8; its deleted beam stays deleted; V8 source unchanged',flush=True)
