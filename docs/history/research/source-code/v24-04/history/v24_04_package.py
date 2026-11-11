import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent
O=Path('E:/jz/JIA/Rebuild_V24_04');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_04.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_04_Fresh_Blend_QA.json').read_text(encoding='utf8'));view=json.loads((R/'V24_04_Preview_States.json').read_text(encoding='utf8'));build=json.loads((R/'V24_04_Build.json').read_text(encoding='utf8'));h=sha(P)
assert qa['status'].startswith('PASS')and qa['model_sha256']==view['model_sha256']==build['sha256']==h
for n in ['v24_04_common.py','v24_04_build.py','v24_04_roof.py','v24_04_finish.py','v24_04_close_upper_return.py','v24_04_verify.py','v24_04_render.py','v24_04_package.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
for source,target in [('D:/Desktop/屏幕截图 2026-10-17 064317.jpg','Kitchen_Open_Joint_User.jpg'),('D:/Desktop/屏幕截图 2026-10-16 220256.jpg','Kitchen_Original_Problem.jpg'),('D:/Desktop/dee25fed-2a01-4d56-a898-f44155e0a2aa (1).png','Kitchen_Reference.png'),('D:/Desktop/屏幕截图 2026-10-16 215115.jpg','Gate_Courtyard_Reference.jpg'),('D:/Desktop/屏幕截图 2026-10-16 124258.jpg','Gate_Exterior_Reference.jpg'),('D:/Desktop/问题大全（每个细节）/00004内大门/理想模型.png','Gate_Ideal.png')]:
 if Path(source).is_file():shutil.copy2(source,O/'References'/target)
for src in [Path('E:/jz/JIA/Rebuild_V24/Textures/Gate_Carving_HeightAtlas.png'),Path('E:/jz/JIA/Rebuild_V24/Source/ImageGen_Prompt.txt')]:
 if src.is_file():shutil.copy2(src,O/('Textures'if src.suffix=='.png'else'Source')/src.name)
roof=build['roof']['proportion_change'];newheight=roof['new_roof_stack_m'];oldheight=roof['old_roof_stack_m'];note=f'''# V24.04 已修正问题

主模型：Blender/Architecture_Complete_V24_04.blend。全场地保留，坐标单位米。

|位置|原问题|本版处理|
|---|---|---|
|内大门顶部|屋顶体量与檐下叠层过厚|屋顶垂直总高 {oldheight:.3f}m → {newheight:.3f}m，降低 {(1-newheight/oldheight)*100:.1f}%；檐下承接层 0.762m → 0.402m。保留原宽深、歇山结构、九脊、四角翘起与独立筒板瓦|
|厨房后墙端部|封到主体墙，但没有接到外围墙|墙端由 X13.35m 延至 X14.10m，折向原外围墙端部；230mm厚实体，底至石基、顶至屋面下表面|
|山墙顶部|砖墙呈锯齿状，局部透缝|根据现有屋面下表面逐点拟合封墙顶部，隐藏接缝处留12mm咬合|
|内大门与厨房交接|旧切口针对厚屋顶，新比例下可能空缺或碰撞|先恢复局部旧构件，再按新屋顶真实外形重新收口；不使用整块包围盒挖切|

实景材质、贴图打包内容、15块浮雕、26扇门的原动画及其余场地几何均通过新文件重新打开后的保留检查。檐廊保留1根独立柱。

Reports/V24_04_Fresh_Blend_QA.json 为保存后回读校验；V24_04_Closure_and_Contact.json 为墙顶与屋顶交接检查。
最终彩色预览使用原材质，未使用白模覆盖；预览角度及模型SHA记录在V24_04_Preview_States.json。Draft预览仅供几何检查，不计入交付。

旧版V24.03没有覆盖。新文件默认定位到厨房封墙查看角度；另有V24_04_Saved_Gate_Rear相机。
'''
(R/'V24_04_Resolved_Issues.md').write_text(note,encoding='utf8')
items=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name in ['V24_04_Manifest.json','V24_04_Bundle_QA.json','V24_04_Draft_States.json']:continue
 items.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_04_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':items},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_04_Lighter_Roof_Sealed_Wall.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in items:z.write(O/r['file'],arcname='Rebuild_V24_04/'+r['file'])
 z.write(O/'V24_04_Manifest.json',arcname='Rebuild_V24_04/V24_04_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
bundle={'status':'PASS_PACKAGE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(items)+1}
(O/'V24_04_Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle,ensure_ascii=False),flush=True)
