import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');P=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V8'
P.mkdir(parents=True,exist_ok=True);manifest=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def report(n):return json.loads((O/'06_Report'/n).read_text(encoding='utf-8'))
ind=report('Independent_V8_QA.json');assert ind['status']=='PASS' and all(c['status']=='PASS' for c in ind['checks'])
assert ind['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V8.3dm')
assert not report('Native_Hybrid_QA.json')['invalid']
kernel=report('Editable_Rhino_Kernel_QA.json');assert not kernel['invalid'] and not kernel['unexpected_open_solids']
assert not report('Editable_Local_Native_QA.json')['invalid']
align=report('Editable_Rhino_Alignment_QA.json');assert not align['invalid'] and align['sha256']==sha(O/'04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm')
assert report('V8_Exchange_Photo_Readback.json')['passed']
assert report('Final_Merged_Interior_QA.json')['status']=='PASS'
assert report('Terrain_Clearance_QA.json')['status']=='PASS'
assert report('Independent_Terrain_Clearance_QA.json')['status']=='PASS'
assert report('Contact_Gap_Ground_Integration_QA.json')['status']=='PASS'
assert len(ind['embedded_original_images'])==10
assert (O/'06_Report/需求汇总与修模依据_V8.md').exists()
preflight={'status':'PASS','main_native_sha256':ind['native_sha256'],'editable_native_sha256':align['sha256'],'independent_checks_passed':len(ind['checks']),'embedded_original_images':len(ind['embedded_original_images']),'source_original_file_unchanged':True,'source_complete_meshes_fully_unchanged':4,'source_Base0_authorized_west_clearance_crop':True,'original_void_projection_residual_m2':ind['original_void_projection_residual_m2'],'native_invalid_objects':0,'editable_invalid_objects':0,'independent_interior_checks':len(report('Final_Merged_Interior_QA.json')['checks']),'fbx_glb_obj_original_images_and_uv_readback':'PASS','field_survey_precision_certified':False,'UE5_actual_import_and_playtest':False}
(O/'06_Report/Delivery_Preflight_QA.json').write_text(json.dumps(preflight,ensure_ascii=False,indent=2),encoding='utf-8')
def register(p,src=None):
 r={'file':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
 if src:r['source']=str(src)
 manifest.append(r)
def copy(src,rel):
 dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 assert sha(src)==sha(dst),(src,dst)
 register(dst,src)
for folder in ['01_Source','02_Data','03_Textures','04_Rhino','06_Report','07_Evidence','08_Editable_Source']:
 for src in sorted((O/folder).rglob('*')):
  if src.is_file() and src.name!='Delivery_Package_QA.json':copy(src,src.relative_to(O))
copy(O/'使用说明.md','使用说明.md')
readme='''# V8 Rhino 交付包

主模型：04_Rhino/Reality_Hybrid_V8.3dm。
可编辑实体／块：04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm。
两者均为原项目 ENU，单位米，Z 向上；请优先打开主模型，可编辑文件供修改建筑。

本次包含：柱顶接楼板与拱梁侧接、厨房木构与门楼飞檐交接、照壁曲面飞檐及逐瓦排列、院墙接主体、右墙首跑楼梯与分层门墙布局、西侧红线区清建筑留地形。

原纯场地、V7 和全部原照片保留；局部授权工作基底及补块、10 张贴图、参数场景、证据和核查报告随包。
详细修改及限制见 06_Report/需求汇总与修模依据_V8.md，手机补测任务见 V8_优先补测上传清单.csv。

约159㎡遮挡地面为插值和暂定土色；楼梯对面洗手间门偏距及房界为候选，需尺量。核查通过不代表施工现场实测精度认证，也不代表已经完成 UE5 实际导入与交互测试。

LOCAL FBX/GLB/OBJ/MTL 和 Blender 交换文件另在 E:/jz/JIA/Rebuild_V8_Hybrid/05_Export；ZIP 未重复包含这些大文件。
'''
rp=P/'先读此文件.md';rp.write_text(readme,encoding='utf-8');register(rp)
mp=P/'文件校验_SHA256.json';mp.write_text(json.dumps({'files':manifest,'count':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest),'author_directory':str(O),'main_model':'04_Rhino/Reality_Hybrid_V8.3dm','preflight':preflight,'manifest_self_excluded':True,'exchange_directory':str(O/'05_Export')},ensure_ascii=False,indent=2),encoding='utf-8')
z=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V8.zip';print('Packaging',len(manifest)+1,'files',flush=True)
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as ar:
 for p in sorted(P.rglob('*')):
  if p.is_file():ar.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z) as ar:
 assert ar.testzip() is None
 assert len(ar.namelist())==len(manifest)+1
 for r in manifest:assert sha(P/r['file'])==r['sha256'],r['file']
result={'status':'PASS','package':str(P),'zip':str(z),'files':len(manifest)+1,'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'file_copy_hashes_all_pass':True,'zip_crc_all_pass':True,'preflight':preflight}
(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(z.parent/(z.stem+'_Delivery_QA.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
