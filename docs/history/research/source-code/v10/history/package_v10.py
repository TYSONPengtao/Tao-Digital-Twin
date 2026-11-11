import json,shutil,zipfile,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');P=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V10';P.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
q=read(O/'06_Report/Independent_V10_QA.json');assert q['status']=='PASS';assert q['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V10.3dm');assert q['editable_sha256']==sha(O/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm')
assert read(O/'06_Report/Final_V10_Wall_QA.json')['status']=='PASS';assert read(O/'06_Report/V10_Exchange_Photo_Readback.json')['passed']
manifest=[]
def copy(src):
 dst=P/src.relative_to(O);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst);manifest.append({'file':dst.relative_to(P).as_posix(),'bytes':dst.stat().st_size,'sha256':sha(dst)})
for folder in ['01_Source','02_Data','03_Textures','04_Rhino','06_Report','07_Evidence','08_Editable_Source']:
 for src in sorted((O/folder).rglob('*')):
  if src.is_file() and src.name not in ['V10_Changed_Wall_Solids_LOCAL.3dm','Delivery_Package_QA.json']:copy(src)
copy(O/'使用说明.md')
guide=P/'先读此文件.md';guide.write_text('''# V10 中式院墙围墙

完整围墙独立模型：`04_Rhino/Courtyard_Walls_V10_ALIGNED_ENU.3dm`。

完整建筑可编辑模型：`04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm`。

实景融合模型：`04_Rhino/Reality_Hybrid_V10.3dm`。本轮细节在此文件仍按既有空洞/接缝修补范围裁切，完整院墙请看上面两个实体文件。单位米，原项目 ENU 坐标，Z 向上。

原墙线、开口、石基、木大门与照壁、厨房及室内保留，按用户新图深化逐块砖瓦、瓦当、镂空花砖和框脚。参考图尺寸／外周花冠造型为暂定，未进行全面实测。已通过原模型保留、贴图和新实体闭合检查；UE5实际导入及交互仍待测试。

详细依据与预览在 `06_Report`。参数、原图、原模型和V9快照已附。LOCAL FBX/GLB/OBJ与Blender文件另在 `E:/jz/JIA/Rebuild_V10_Hybrid/05_Export`。
''',encoding='utf-8');manifest.append({'file':guide.relative_to(P).as_posix(),'bytes':guide.stat().st_size,'sha256':sha(guide)})
mp=P/'文件校验_SHA256.json';mp.write_text(json.dumps({'files':manifest,'count':len(manifest),'author_directory':str(O),'main_model':'04_Rhino/Reality_Hybrid_V10.3dm','complete_editable_walls':'04_Rhino/Courtyard_Walls_V10_ALIGNED_ENU.3dm','new_closed_native_solids':q['new_closed_native_solids'],'checks_passed':q['passed_checks'],'source_outside_repair_scope_preserved':True,'manifest_self_excluded':True},ensure_ascii=False,indent=2),encoding='utf-8')
z=P.with_suffix('.zip');print('Packaging',len(manifest)+1,'V10 files',flush=True)
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as ar:
 for p in sorted(P.rglob('*')):
  if p.is_file():ar.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z) as ar:assert ar.testzip() is None;assert len(ar.namelist())==len(manifest)+1
for r in manifest:assert sha(P/r['file'])==r['sha256']
r={'status':'PASS','zip':str(z),'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'files':len(manifest)+1,'copy_hashes':'PASS','zip_crc':'PASS','new_closed_native_solids':q['new_closed_native_solids'],'checks_passed':q['passed_checks']};(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2),flush=True)
