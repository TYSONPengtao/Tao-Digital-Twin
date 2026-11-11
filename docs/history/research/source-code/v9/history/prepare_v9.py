import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;V8=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
assert not O.exists(),'V9 output already exists; reuse deliberately rather than restart'
for folder in ['01_Source','02_Data','03_Textures','07_Evidence']:
 shutil.copytree(V8/folder,O/folder)
for folder in ['04_Rhino','05_Export','06_Report','08_Editable_Source/05_Intermediate','08_Editable_Source/06_Rhino']:(O/folder).mkdir(parents=True,exist_ok=True)
scene=V8/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';shutil.copy2(scene,O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json')
prior=O/'07_Evidence/Prior_V8_Reports';prior.mkdir(exist_ok=True)
for p in (V8/'06_Report').iterdir():
 if p.is_file() and p.suffix in ['.json','.md','.csv']:shutil.copy2(p,prior/p.name)
refs=O/'07_Evidence/V9_User_Relation_Diagrams';refs.mkdir(exist_ok=True)
for name in ['1aeb5b24-97ff-45f0-a8e3-f2916523ffb3.png','4daa4b13-ab29-4a24-81ca-0a7345c7eecb.png']:shutil.copy2(Path(r'D:\Desktop')/name,refs/name)
for name in ['Materials.json','Base_Index.json']:
 p=O/'02_Data'/name;text=p.read_text(encoding='utf-8');text=text.replace(str(V8).replace('\\','\\\\'),str(O).replace('\\','\\\\')).replace(str(V8).replace('\\','/'),str(O).replace('\\','/'));p.write_text(text,encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qa=json.loads((V8/'06_Report/Independent_V8_QA.json').read_text(encoding='utf-8'))
assert qa['native_sha256']==sha(V8/'04_Rhino/Reality_Hybrid_V8.3dm')
(O/'06_Report/V9_Baseline_Hashes.json').write_text(json.dumps({'baseline_V8_primary_sha256':qa['native_sha256'],'baseline_V8_editable_sha256':sha(V8/'04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm'),'baseline_scene_sha256':sha(scene),'original_source_sha256':sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'),'working_source_sha256':sha(O/'01_Source/Pure_Site_WORKING_V8.3dm'),'scope':'Only kitchen/gate roof relationship and visible eave layers; no interior, terrain or Roman changes'},ensure_ascii=False,indent=2),encoding='utf-8')
for src,dst in [('build_v8_patch.py','build_v9_patch.py'),('export_v8_native.py','export_v9_native.py'),('export_v8_editable.py','export_v9_editable.py'),('rhino_validate_v8.py','rhino_validate_v9.py'),('align_editable_rhino_v8.py','align_editable_rhino_v9.py'),('check_v8_exchange_photos.py','check_v9_exchange_photos.py')]:
 text=(W/src).read_text(encoding='utf-8').replace('Rebuild_V8_Hybrid','Rebuild_V9_Hybrid').replace('Reality_Hybrid_V8','Reality_Hybrid_V9').replace('Architecture_Edit_V8','Architecture_Edit_V9').replace('V8_','V9_').replace('V8 corrected','V9 corrected').replace('V8 LOCAL','V9 LOCAL')
 if src=='build_v8_patch.py':
  text=text.replace("V6=Path(r'E:\\jz\\JIA\\Rebuild_V7_Hybrid')","V6=Path(r'E:\\jz\\JIA\\Rebuild_V8_Hybrid')")
 (W/dst).write_text(text,encoding='utf-8')
print('V9 isolated working tree prepared; V8 untouched',flush=True)
