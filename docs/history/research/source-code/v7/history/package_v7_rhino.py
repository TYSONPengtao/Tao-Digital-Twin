import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
P=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V7'
P.mkdir(parents=True,exist_ok=True)
manifest=[]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def register(p,source=None):
    row={'file':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
    if source:row['source']=str(source)
    manifest.append(row)
def copy(src,rel):
    dst=P/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    assert sha(src)==sha(dst),(src,dst)
    register(dst,src)
def report(name):return json.loads((O/'06_Report'/name).read_text(encoding='utf-8'))
ind=report('Independent_V7_QA.json')
assert not any(c['status']!='PASS' for c in ind['checks'])
assert ind['native_sha256']==sha(O/'04_Rhino/Reality_Hybrid_V7.3dm')
assert not report('Native_Hybrid_QA.json')['invalid']
assert not report('Editable_Rhino_Kernel_QA.json')['invalid']
assert not report('Editable_Rhino_Kernel_QA.json')['unexpected_open_solids']
align=report('Editable_Rhino_Alignment_QA.json')
assert not align['invalid']
assert align['sha256']==sha(O/'04_Rhino/Architecture_Edit_V7_ALIGNED_ENU.3dm')
assert report('Actual_Source_Rim_3D_QA.json')['status']=='PASS'
assert report('V7_Exchange_Photo_Readback.json')['passed']
assert report('Native_Embedded_Texture_QA.json')['status']=='PASS'
preflight={'status':'PASS','main_native_sha256':ind['native_sha256'],'editable_native_sha256':align['sha256'],'independent_checks_passed':len(ind['checks']),'embedded_original_images':ind['native_embedded_images'],'source_real_meshes_unchanged':ind['source_original_meshes'],'patch_outside_main_void_m2':ind['patch_outside_m2'],'native_invalid_objects':0,'editable_invalid_objects':0,'native_rim_3d':'PASS','fbx_glb_obj_image_and_uv_readback':'PASS','field_survey_precision_certified':False}
(O/'06_Report/Delivery_Preflight_QA.json').write_text(json.dumps(preflight,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in ['01_Source','02_Data','03_Textures','04_Rhino','06_Report','07_Evidence','08_Editable_Source']:
    for src in sorted((O/folder).rglob('*')):
        if src.is_file() and src.name!='Delivery_Package_QA.json':copy(src,src.relative_to(O))
copy(O/'使用说明.md','使用说明.md')
text='''# V7 Rhino 交付包

主模型：04_Rhino/Reality_Hybrid_V7.3dm，场地原五个实景网格保持不变，仅在主空洞内修补。
实体编辑：04_Rhino/Architecture_Edit_V7_ALIGNED_ENU.3dm；LOCAL 参数及完整实体源见 08_Editable_Source。
本包保存主模型、编辑模型、原场地副本、全部补块数据、10 张原贴图、照片／全景证据与核查报告。
修改内容、参考图片和待补测项见 06_Report/需求汇总与修模依据_V7.md。

大体积交换文件单独保存于 E:/jz/JIA/Rebuild_V7_Hybrid/05_Export：
Reality_Hybrid_V7_LOCAL.fbx / .glb / .obj / .mtl，以及原贴图和 .blend。
本 Rhino ZIP 未重复包含上述交换文件。使用说明中的 05_Export 指该作者目录。
核查通过不等于现场施工测量精度认证；门偏距、净尺寸及部分砖瓦尺寸仍需量尺确认。
'''
readme=P/'先读此文件.md';readme.write_text(text,encoding='utf-8');register(readme)
mp=P/'文件校验_SHA256.json'
mp.write_text(json.dumps({'files':manifest,'count':len(manifest),'total_bytes':sum(x['bytes'] for x in manifest),'author_directory':str(O),'main_model':'04_Rhino/Reality_Hybrid_V7.3dm','preflight':preflight,'manifest_self_excluded':True,'exchange_directory':str(O/'05_Export')},ensure_ascii=False,indent=2),encoding='utf-8')
z=W.parent/'outputs/Production_1QK_Rhino_Hybrid_V7.zip'
print('Packaging',len(manifest)+1,'files',flush=True)
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=4) as ar:
    for p in sorted(P.rglob('*')):
        if p.is_file():ar.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(z,'r') as ar:
    assert ar.testzip() is None
    assert len(ar.namelist())==len(manifest)+1
    for m in manifest:
        assert sha(P/m['file'])==m['sha256'],m['file']
    result={'status':'PASS','package':str(P),'zip':str(z),'files':len(ar.namelist()),'zip_bytes':z.stat().st_size,'zip_sha256':sha(z),'file_copy_hashes_all_pass':True,'zip_crc_all_pass':True,'preflight':preflight}
(O/'06_Report/Delivery_Package_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(z.parent/(z.stem+'_Delivery_QA.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
