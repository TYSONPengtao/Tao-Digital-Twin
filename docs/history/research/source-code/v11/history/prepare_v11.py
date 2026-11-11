import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;B=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert not O.exists(),'V11 exists: inspect, do not reset'
for d in ['01_Source','02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Evidence','08_Editable_Source/05_Intermediate']:(O/d).mkdir(parents=True)
for d in ['02_Data','03_Textures']:shutil.copytree(B/d,O/d,dirs_exist_ok=True)
for n in ['Pure_Site_UNMODIFIED.3dm','Pure_Site_WORKING_V8.3dm']:shutil.copy2(B/'01_Source'/n,O/'01_Source'/n)
shutil.copy2(B/'04_Rhino/Reality_Hybrid_V10.3dm',O/'01_Source/V10_Current_Before_V11.3dm')
scene=B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';shutil.copy2(scene,O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');shutil.copy2(scene,O/'07_Evidence/V10_Scene_Before_V11.json')
save(O/'06_Report/V11_Baseline_Hashes.json',{'baseline_scene_sha256':sha(scene),'baseline_native_sha256':sha(B/'04_Rhino/Reality_Hybrid_V10.3dm'),'baseline_editable_sha256':sha(B/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm'),'original_source_sha256':sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'),'working_source_sha256':sha(O/'01_Source/Pure_Site_WORKING_V8.3dm'),'author_baseline':str(B)})
def relocate(x):
 if isinstance(x,dict):return {k:relocate(v) for k,v in x.items()}
 if isinstance(x,list):return [relocate(v) for v in x]
 if isinstance(x,str):return x.replace(str(B),str(O)).replace(B.as_posix(),O.as_posix())
 return x
for name in ['Materials.json','Base_Index.json']:save(O/'02_Data'/name,relocate(read(O/'02_Data'/name)))
scope=read(B/'02_Data/V10_Allowed_Repair_Scope.json');scope['V11_scope_note']='Inherited repair region plus user explicitly corrected pavilion, right-angle wall, kitchen contact and missing outer gate/wall footprints. Source meshes and original photos untouched.';save(O/'02_Data/V11_Allowed_Repair_Scope.json',scope)
history=O/'07_Evidence/V10_Previous_Delivery';history.mkdir()
for p in (B/'06_Report').iterdir():
 if p.is_file() and p.suffix in ['.json','.md']:shutil.copy2(p,history/p.name)
for name in ['DJI_0511.DNG','DJI_0513.DNG','屏幕截图 2026-10-09 115821.jpg','屏幕截图 2026-10-09 120147.jpg','屏幕截图 2026-10-09 115843.jpg','屏幕截图 2026-10-09 121112.jpg','f1fdc71e-760c-4549-a971-7d56dae45c39.png','d15a543f-dee1-492a-8cbb-cb87cb3bffa1.png','f5e2d2aa-b7ef-4bc3-8b39-c35d600db64b.png','f9db2bcf-fe61-400b-9a97-12857a7cb553.png']:
 p=Path('D:/Desktop')/name
 if p.exists():shutil.copy2(p,O/'07_Evidence'/name)
for p in (W/'v11_reference_audit').glob('*decoded.png'):shutil.copy2(p,O/'07_Evidence'/p.name)
save(O/'07_Evidence/New_Reference_Provenance.json',{'DNG':{'originals_unchanged':True,'processing':'rawpy LibRaw use_camera_wb=True, output 8-bit PNG for inspection; no geometry or metric extraction from an uncalibrated single view','photo_subject':'Kitchen external bare grey brick walls above existing stone retaining base; tile-coped wall connection, L corner'},'user_generated_diagrams':'Design shape/detail references, dimensions provisional, not an as-built measured construction drawing','references':[{'file':p.name,'sha256':sha(p)} for p in (O/'07_Evidence').iterdir() if p.is_file() and p.suffix.lower() in ['.dng','.jpg','.png']]})
print('V11 exact V10 baseline prepared',flush=True)
