"""Package the checked native Blender model, original materials, sources and views."""
import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_06');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_06.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_06_Fresh_Blend_QA.json').read_text(encoding='utf8'));view=json.loads((R/'V24_06_Preview_States.json').read_text(encoding='utf8'));build=json.loads((R/'V24_06_Build.json').read_text(encoding='utf8'));h=sha(P)
assert qa['status'].startswith('PASS')and not qa['failures']and qa['model_sha256']==view['model_sha256']==build['sha256']==h
assert len(view['views'])==6 and all((R/v['file']).is_file()for v in view['views'])
for n in ['v24_06_common.py','v24_06_build.py','v24_06_paving.py','v24_06_timber.py','v24_06_roof.py','v24_06_verify.py','v24_06_render.py','v24_06_package.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
refs=[
 ('D:/Desktop/屏幕截图 2026-10-17 081038.jpg','01_Roof_Side_Review.jpg'),
 ('D:/Desktop/屏幕截图 2026-10-17 081244.jpg','02_Eave_Underside_Review.jpg'),
 ('D:/Desktop/屏幕截图 2026-10-17 081609.jpg','03_Trees_and_Passage_Review.jpg'),
 ('D:/Desktop/屏幕截图 2026-10-17 081859.jpg','04_Wall_Centerline_Review.jpg'),
 ('D:/Desktop/屏幕截图 2026-10-17 082046.jpg','05_Kitchen_Facade_Review.jpg'),
 ('D:/Desktop/问题大全（每个细节）/厨房廊檐柱子/屏幕截图 2026-10-15 172938.jpg','06_Real_Timber_Underside.jpg'),
 ('D:/DJI/0002/DCIM/101MEDIA/DJI_0156.JPG','07_Real_Timber_DJI_0156.JPG'),
 ('D:/DJI/0002/DCIM/101MEDIA/DJI_0157.JPG','08_Real_Timber_DJI_0157.JPG')]
for src,dst in refs:
 assert Path(src).is_file(),src
 shutil.copy2(src,O/'References'/dst)
for src in [Path('E:/jz/JIA/Rebuild_V24/Textures/Gate_Carving_HeightAtlas.png'),Path('E:/jz/JIA/Rebuild_V24/Source/ImageGen_Prompt.txt')]:
 if src.is_file():shutil.copy2(src,O/('Textures'if src.suffix=='.png'else'Source')/src.name)
b=qa['roof_balance'];wall=build['wall'];t=qa['timber']
note=f'''# V24.06 修改结果

完整场地文件：Blender/Architecture_Complete_V24_06.blend，单位米，原贴图已打包。

|用户提出的问题|已完成的几何修改|
|---|---|
|侧面屋顶偏前，前檐出挑过多|屋顶中心由Y={b['old_roof_center_y']:.3f}m移到门柱中心Y={b['pier_center_y']:.3f}m；前檐收回{b['new_bounds'][0][1]-b['old_bounds'][0][1]:.3f}m，前后出挑各{b['front_projection_from_pier_m']:.3f}m|
|檐下最低边仍低于厨房|在V24.05基础上再抬高{b['additional_roof_raise_m']:.3f}m；最低檐底Z={b['minimum_eave_bottom_z']:.3f}m，高于共享屋顶投影范围内厨房斜檐最高线{b['highest_kitchen_roof_under_gate_plan_z']:.3f}m，净高差{qa['eave_bottom_clearance_m']:.3f}m|
|屋顶层次与比例|保留压薄的五层连续檐带、上部两坡及山花、下部四坡、九条屋脊、四角翘头与848个实体瓦件；只调整进深和中心，不增加屋顶厚度|
|圈内两棵树和土黄色地带|删除Tree 5、Tree 6和树根土环；约{qa['paved_area_m2']:.2f}平方米改用邻接过道同一M_V12_Road_Concrete材质、相同UV尺度；延续原场地坡度，原过道的圆形树坑已并入封平|
|院墙中线向外偏|墙线向内调{wall['inward_shift_m']:.3f}m，与门柱中线重合；北端连接点固定，墙体和瓦顶、花脊、装饰线一同调整|
|厨房檐廊下缺少木构|40对密排椽，保留6根圆檩；新增3处穿梁和垂瓜、6处曲线托木、实体卷草和木销；原直撑改为曲线托木，保留1根独立檐廊柱|

厨房后墙与外围墙的全高转折封闭保留。原107套材质、74张图像、15块实体灰度浮雕、26扇门的动画及其余场地均通过保存后复核。

檐下净高按真实三角面裁切到新门楼屋顶投影内计算，比较对象包括厨房瓦面、瓦垄、收边、望板及弧形山墙压顶。这里核对的是最低檐底，不只是屋面表面。

重新打开最终blend后检查{len(qa['checks'])}项，失败0项，见V24_06_Fresh_Blend_QA.json。原有院墙网格的边界拓扑沿用源模型；新增实体木构、屋顶和树坑修复均单独校验。6张彩色预览使用原材质，无白模覆盖。

预览：Gate_Courtyard（院内门楼）、Balanced_Side（侧面出挑）、Gate_Kitchen_Clearance（檐底与厨房）、Kitchen_Timber（檐下木构）、Passage_Paved（过道俯视）、Gate_Roof_Top（歇山结构）。

脚本顺序：v24_06_build.py → v24_06_verify.py → v24_06_render.py → v24_06_package.py。重建读取本机保留的V24.05和V24.02文件；直接打开交付blend不需要旧版本。保留原模型，当前版本单独存放在Rebuild_V24_06。
'''
(R/'V24_06_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name.endswith('_Draft_States.json')or f.name in ['V24_06_Manifest.json','V24_06_Bundle_QA.json','V24_06_Pit_Probe.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_06_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_06_Balanced_Gate_Wall_Passage_Timber.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for row in files:z.write(O/row['file'],arcname='Rebuild_V24_06/'+row['file'])
 z.write(O/'V24_06_Manifest.json',arcname='Rebuild_V24_06/V24_06_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_BUNDLE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_06_Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
