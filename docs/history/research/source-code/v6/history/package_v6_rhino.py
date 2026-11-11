import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;CWD=W.parent
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');V5=Path(r'E:\jz\JIA\Rebuild_V5');V4=Path(r'E:\jz\JIA\Rebuild_V4')
P=CWD/'outputs/Production_1QK_Rhino_Hybrid_V6';P.mkdir(parents=True,exist_ok=True)
manifest=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def copy(src,rel):
 src=Path(src);dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 a=sha(src);b=sha(dst);assert a==b,(src,dst);manifest.append({'file':str(Path(rel)).replace('\\','/'),'bytes':dst.stat().st_size,'sha256':b})
qa=json.loads((O/'06_Report/Native_Hybrid_QA.json').read_text(encoding='utf-8'));assert not qa['invalid']
edge=json.loads((O/'06_Report/Actual_Source_Rim_3D_QA.json').read_text(encoding='utf-8'));assert edge['status']=='PASS'
ind=json.loads((W/'v6_alignment_audit/Hybrid_V6_Independent_QA.json').read_text(encoding='utf-8'));assert not any(c['status']=='FAIL' for c in ind['checks'])
assert ind['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V6.3dm')
for name in ['Reality_Hybrid_V6.3dm','Architecture_Edit_V5_ALIGNED_ENU.3dm']:copy(O/'04_Rhino'/name,'04_Rhino/'+name)
copy(O/'01_Source/Pure_Site_UNMODIFIED.3dm','01_Source/Pure_Site_UNMODIFIED.3dm')
for folder in ['Base','Patch']:
 for f in (O/'03_Textures'/folder).iterdir():
  if f.is_file():copy(f,'03_Textures/'+folder+'/'+f.name)
for name in ['Hole_Polygon.json','Coordinate.json','Base_Index.json','Patch_Index.json','Materials.json']:
 copy(O/'02_Data'/name,'02_Data/'+name)
copy(V5/'05_Intermediate/Architecture_Scene.json','02_Data/Editable_Architecture_V5_LOCAL.json')
for f in (O/'06_Report').iterdir():
 if f.is_file() and f.suffix in ['.json','.md','.csv','.png']:
  copy(f,'06_Report/'+f.name)
for name in ['Hybrid_V6_Independent_QA.json','Hybrid_V6_Independent_QA.md','Hybrid_Boundary_Height_QA.json','Hybrid_Boundary_Height_Samples.csv','Hybrid_XY_Residual.json','Fast_Ground_Edge_Height_V6.json','Fast_Ground_Edge_Height_V6.csv']:
 copy(W/'v6_alignment_audit'/name,'06_Report/'+name)
for name in ['V6_Exchange_Photo_Readback.json','FBX_Patch_UV_Readback.json']:
 copy(W/'v6_reality_inventory'/name,'06_Report/'+name)
for f in (V5/'09_Report').iterdir():
 if f.is_file() and (f.name.startswith(('V5_','Door_','Room_','Video_')) or f.name in ['Geometry_QA_V5.json','Native_Model_QA.json','Exchange_Readback_QA.json']):
  copy(f,'07_Layout_And_Doors/'+f.name)
for f in (V5/'10_DJI_Reference').iterdir():
 if f.is_file():copy(f,'08_Evidence/DJI/'+f.name)
for f in (V5/'12_Video_Layout_Evidence').rglob('*'):
 if f.is_file():copy(f,Path('08_Evidence/Video')/f.relative_to(V5/'12_Video_Layout_Evidence'))
for name in ['REPORT_V4.md','Interface_Repair_Check.json','Construction_Geometry_Checks_V4.csv','PENDING_ITEMS_V4.md']:
 copy(V4/'09_Report'/name,'08_Evidence/Construction_Coordination/'+name)
for name in ['CASES_Inventory_V3.json','CASES_Reference_Audit.csv','CC_SDK_Projects_V3.json','OBJ_Metadata.json']:
 copy(V5/'04_ContextCapture'/name,'08_Evidence/ContextCapture/'+name)
copy(O/'使用说明.md','使用说明.md')
manifestpath=P/'文件校验_SHA256.json';manifestpath.write_text(json.dumps({'files':manifest,'count':len(manifest),'total_bytes':sum(r['bytes'] for r in manifest),'author_directory':str(O),'main_model':'04_Rhino/Reality_Hybrid_V6.3dm','source_unchanged':True},ensure_ascii=False,indent=2),encoding='utf-8')
z=CWD/'outputs/Production_1QK_Rhino_Hybrid_V6.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as archive:
 for p in sorted(P.rglob('*')):
  if p.is_file():archive.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z,'r') as archive:
 assert archive.testzip() is None
 report={'package':str(P),'zip':str(z),'files':len(archive.namelist()),'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'file_copy_hashes_all_pass':True,'zip_crc_all_pass':True}
(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
