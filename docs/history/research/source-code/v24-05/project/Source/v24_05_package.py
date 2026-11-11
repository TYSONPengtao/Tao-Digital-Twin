import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_05');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_05.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_05_Fresh_Blend_QA.json').read_text(encoding='utf8'));view=json.loads((R/'V24_05_Preview_States.json').read_text(encoding='utf8'));build=json.loads((R/'V24_05_Build.json').read_text(encoding='utf8'));h=sha(P);assert qa['status'].startswith('PASS')and qa['model_sha256']==view['model_sha256']==build['sha256']==h
for n in ['v24_05_common.py','v24_05_build.py','v24_05_finish.py','v24_05_verify.py','v24_05_render.py','v24_05_package.py','v24_04_roof.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
for src,dst in [('D:/DJI/0003/DCIM/101MEDIA/DJI_0117.JPG','Gate_Kitchen_Level_Real.jpg'),('D:/Desktop/download.png','User_Height_Review.png'),('D:/Desktop/屏幕截图 2026-10-17 064317.jpg','Kitchen_Wall_Problem.jpg'),('D:/Desktop/屏幕截图 2026-10-16 124258.jpg','Gate_Real.jpg'),('D:/Desktop/问题大全（每个细节）/00004内大门/理想模型.png','Gate_Ideal.png'),('D:/Desktop/dee25fed-2a01-4d56-a898-f44155e0a2aa (1).png','Kitchen_Reference.png')]:
 if Path(src).is_file():shutil.copy2(src,O/'References'/dst)
for src in [Path('E:/jz/JIA/Rebuild_V24/Textures/Gate_Carving_HeightAtlas.png'),Path('E:/jz/JIA/Rebuild_V24/Source/ImageGen_Prompt.txt')]:
 if src.is_file():shutil.copy2(src,O/('Textures'if src.suffix=='.png'else'Source')/src.name)
shutil.copy2('E:/jz/JIA/Rebuild_V24_04/Reports/V24_04_Closure_and_Contact.json',O/'Source/V24_04_Previous_Closure_Proof.json')
note=f'''# V24.05 屋顶抬高与封墙结果

Blender/Architecture_Complete_V24_05.blend 为完整场地模型，单位米，贴图已打包。默认相机定位到内大门与厨房交接。

|项目|结果|
|---|---|
|内大门屋面与檐下20组构件|整体向全局Z轴正向平移0.500m，网格形状、UV、宽深及压薄后的厚度全部保留|
|檐口与主脊|檐口中点2.94m→3.44m；主脊基准3.38m→3.88m|
|檐下承接|吊顶底面2.538m→3.038m；新增两侧上部石柱段和门楣上方素面墙颈，消除悬空及共面重叠|
|屋顶与厨房交接|恢复局部构件后重新收口，保存后未检出实际三角面穿插|
|圈示共享投影范围的屋面高差|门楼屋面高于厨房坡面，采样最小高差{qa['marked_junction_minimum_gap_m']:.3f}m|
|厨房封墙|保留230mm厚屋面贴合后墙及通向外围墙上部的300mm厚转折墙，墙基和压顶连续|
|其余场地|保留实景材质{qa['retained_materials']}套、图像{qa['retained_images']}张、15块灰度实体浮雕及26扇门原动画|

高差采样区域为用户圈示交接处，详见V24_05_Changes.json的junction_height_samples。屋顶整体0.50m位移由原始/最终对象矩阵逐一验证。

保存后重新打开校验：{len(qa['checks'])}项检查，0项失败，见V24_05_Fresh_Blend_QA.json。最终预览采用原材质，无白模覆盖；图像状态记录与模型SHA256一致。

源代码执行次序：v24_05_build.py → v24_05_finish.py → v24_05_verify.py → v24_05_render.py。重建脚本读取保留在本机的V24.04及V24.02；打开交付blend不需要这些旧文件。
'''
(R/'V24_05_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name in ['V24_05_Draft_States.json','V24_05_Manifest.json','V24_05_Bundle_QA.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_05_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_05_Raised_Gate_Sealed_Kitchen.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for row in files:z.write(O/row['file'],arcname='Rebuild_V24_05/'+row['file'])
 z.write(O/'V24_05_Manifest.json',arcname='Rebuild_V24_05/V24_05_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_BUNDLE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_05_Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
