import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent
B=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
assert not O.exists(),'V10 already exists; inspect rather than overwrite'
for d in ['01_Source','02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Evidence','08_Editable_Source/05_Intermediate']:(O/d).mkdir(parents=True)
for d in ['02_Data','03_Textures']:shutil.copytree(B/d,O/d,dirs_exist_ok=True)
for n in ['Pure_Site_UNMODIFIED.3dm','Pure_Site_WORKING_V8.3dm']:shutil.copy2(B/'01_Source'/n,O/'01_Source'/n)
shutil.copy2(B/'04_Rhino/Reality_Hybrid_V9.3dm',O/'01_Source/V9_Current_Before_V10.3dm')
scene=B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
shutil.copy2(scene,O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json')
shutil.copy2(scene,O/'07_Evidence/V9_Scene_Before_Wall_Detail.json')
ref=Path(r'C:\Users\PENG\AppData\Local\Temp\codex-clipboard-9c94e772-aef6-49e7-8ca8-408562170f8a.png')
shutil.copy2(ref,O/'07_Evidence/User_Chinese_Courtyard_Wall_Detail.png')
save(O/'06_Report/V10_Baseline_Hashes.json',{'baseline_scene_sha256':sha(scene),'baseline_native_sha256':sha(B/'04_Rhino/Reality_Hybrid_V9.3dm'),'baseline_editable_sha256':sha(B/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm'),'original_source_sha256':sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'),'working_source_sha256':sha(O/'01_Source/Pure_Site_WORKING_V8.3dm'),'reference_image_sha256':sha(ref),'author_baseline':str(B)})
for d in ['Materials.json','Base_Index.json']:
 p=O/'02_Data'/d;p.write_text(p.read_text(encoding='utf-8').replace(str(B),str(O)),encoding='utf-8')
scope=json.loads((B/'02_Data/V9_Allowed_Repair_Scope.json').read_text(encoding='utf-8'))
scope['V10_scope_note']='New wall details in hybrid are clipped to inherited void/contact repair area. Full editable walls are separate native solids. Original source geometry outside inherited repairs unchanged.'
save(O/'02_Data/V10_Allowed_Repair_Scope.json',scope)
print('V10 prepared from exact current V9, original textures/source copied',flush=True)
