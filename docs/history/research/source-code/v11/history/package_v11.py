import json,shutil,zipfile,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');P=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V11'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
q=read(O/'06_Report/Independent_V11_QA.json');assert q['status']=='PASS';assert q['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V11.3dm');assert q['editable_sha256']==sha(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm')
assert read(O/'06_Report/Final_V11_Site_QA.json')['status']=='PASS';assert read(O/'06_Report/V11_Exchange_Photo_Readback.json')['passed']
assert read(O/'06_Report/Standalone_Companion_Cleanup_QA.json')['status']=='PASS'
assert read(O/'06_Report/Final_Ground_Coverage_QA.json')['status']=='PASS'
independent=read(O/'06_Report/Independent_Actual_Pavilion_Gate_QA.json');assert independent.get('status')=='PASS' or independent.get('passed') is True
P.mkdir(parents=True,exist_ok=True);manifest=[]
for folder in ['01_Source','02_Data','03_Textures','04_Rhino','06_Report','07_Evidence','08_Editable_Source']:
 for src in sorted((O/folder).rglob('*')):
  if not src.is_file() or src.name in ['V11_Changed_Wall_Solids_LOCAL.3dm','Delivery_Package_QA.json'] or src.suffix in ['.blend','.blend1'] or ('07_Evidence' in src.parts and src.suffix=='.3dm'):continue
  dst=P/src.relative_to(O);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);h=sha(src);assert h==sha(dst);manifest.append({'file':dst.relative_to(P).as_posix(),'bytes':dst.stat().st_size,'sha256':h})
for name in ['使用说明.md']:
 src=O/name;dst=P/name;shutil.copy2(src,dst);manifest.append({'file':name,'bytes':dst.stat().st_size,'sha256':sha(dst)})
(P/'文件校验_SHA256.json').write_text(json.dumps({'count':len(manifest),'files':manifest,'native_primary':'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm','reality_hybrid':'04_Rhino/Reality_Hybrid_V11.3dm','site_components':'04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm','checks_passed':q['passed_checks'],'new_closed_native_solids':q['new_closed_native_solids'],'coordinate':'Metres, original ENU, Z-up','exchange_directory':str(O/'05_Export'),'manifest_self_excluded':True},ensure_ascii=False,indent=2),encoding='utf8')
z=P.with_suffix('.zip');print('Packaging V11',len(manifest)+1,'files',flush=True)
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as ar:
 for p in sorted(P.rglob('*')):
  if p.is_file():ar.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z) as ar:assert ar.testzip() is None;assert len(ar.namelist())==len(manifest)+1
for r in manifest:assert sha(P/r['file'])==r['sha256']
r={'status':'PASS','zip':str(z),'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'files':len(manifest)+1,'copy_hashes':'PASS','zip_crc':'PASS','new_closed_native_solids':q['new_closed_native_solids'],'checks_passed':q['passed_checks']};(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r,ensure_ascii=False,indent=2),flush=True)
