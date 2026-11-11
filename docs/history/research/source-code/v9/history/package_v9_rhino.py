import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');P=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V9'
P.mkdir(parents=True,exist_ok=True);manifest=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def report(n):return json.loads((O/'06_Report'/n).read_text(encoding='utf-8'))
ind=report('Independent_V9_QA.json');assert ind['status']=='PASS' and all(c['status']=='PASS' for c in ind['checks']);assert ind['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V9.3dm')
assert not report('Native_Hybrid_QA.json')['invalid']
kernel=report('Editable_Rhino_Kernel_QA.json');assert not kernel['invalid'] and not kernel['unexpected_open_solids']
assert not report('Editable_Local_Native_QA.json')['invalid']
align=report('Editable_Rhino_Alignment_QA.json');assert not align['invalid'] and align['sha256']==sha(O/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm')
assert report('V9_Exchange_Photo_Readback.json')['passed'];assert report('Final_V9_Reference_QA.json')['status']=='PASS';assert len(ind['embedded_original_images'])==10
assert (O/'06_Report/需求汇总与修模依据_V9.md').exists()
preflight={'status':'PASS','main_native_sha256':ind['native_sha256'],'editable_native_sha256':align['sha256'],'checks_passed':len(ind['checks']),'embedded_original_images':10,'current_V8_unchanged_and_user_beam_deletion_preserved':True,'retained_native_objects_exact':ind['retained_native_objects_exact'],'original_source_meshes_V9_unchanged':True,'original_void_projection_residual_m2':ind['original_void_projection_residual_m2'],'native_invalid_objects':0,'editable_invalid_objects':0,'fbx_glb_obj_original_images_and_uv_readback':'PASS','independent_roof_collision_audit':'PASS','field_survey_precision_certified':False,'UE5_actual_import_and_playtest':False}
(O/'06_Report/Delivery_Preflight_QA.json').write_text(json.dumps(preflight,ensure_ascii=False,indent=2),encoding='utf-8')
def register(p,src=None):
 r={'file':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
 if src:r['source']=str(src)
 manifest.append(r)
def copy(src,rel):
 dst=P/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst);register(dst,src)
for folder in ['01_Source','02_Data','03_Textures','04_Rhino','06_Report','07_Evidence','08_Editable_Source']:
 for src in sorted((O/folder).rglob('*')):
  if src.is_file() and src.name!='Delivery_Package_QA.json':copy(src,src.relative_to(O))
copy(O/'使用说明.md','使用说明.md')
readme='''# V9 Rhino 交付包

主模型：04_Rhino/Reality_Hybrid_V9.3dm。
可编辑实体／块：04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm。
两者均为原项目 ENU，单位米，Z 向上；请优先打开主模型。可编辑文件用于修改建筑及本轮屋檐；两文件轮流查看，叠加会显示重复建筑。

本轮修正较低厨房木房端部伸入较高门楼檐下的交接，清除门楼墙芯穿入木房瓦坡的问题，分别细化封檐、椽头、装饰、木构和实拍金属收边。普通屋面高程保留，实际木房檐下重叠投影 2.4252㎡。当前 V8 中已删除的三层梁不恢复；其他当前模型几何、原材质和贴图保留。

原纯场地、当前 V8 快照、参数源、10 张原照片贴图、依据和核查报告随包。详细使用见 使用说明.md 及 06_Report/需求汇总与修模依据_V9.md。

示意图用于关系核对；隐蔽构造及饰件截面未实测。质量核查不代表现场施工精度认证，UE5 实际导入和交互尚未测试。室内偏距和遮挡地面沿用 V8 标记的不确定性。

LOCAL FBX/GLB/OBJ/MTL 和 Blender 文件另在 E:/jz/JIA/Rebuild_V9_Hybrid/05_Export；ZIP 未重复包含这些大交换文件。
'''
rp=P/'先读此文件.md';rp.write_text(readme,encoding='utf-8');register(rp)
mp=P/'文件校验_SHA256.json';mp.write_text(json.dumps({'files':manifest,'count':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest),'author_directory':str(O),'main_model':'04_Rhino/Reality_Hybrid_V9.3dm','preflight':preflight,'manifest_self_excluded':True,'exchange_directory':str(O/'05_Export')},ensure_ascii=False,indent=2),encoding='utf-8')
z=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V9.zip';print('Packaging',len(manifest)+1,'files',flush=True)
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as ar:
 for p in sorted(P.rglob('*')):
  if p.is_file():ar.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z) as ar:
 assert ar.testzip() is None;assert len(ar.namelist())==len(manifest)+1
 for r in manifest:assert sha(P/r['file'])==r['sha256'],r['file']
result={'status':'PASS','package':str(P),'zip':str(z),'files':len(manifest)+1,'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'file_copy_hashes_all_pass':True,'zip_crc_all_pass':True,'preflight':preflight}
(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');(z.parent/(z.stem+'_Delivery_QA.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
