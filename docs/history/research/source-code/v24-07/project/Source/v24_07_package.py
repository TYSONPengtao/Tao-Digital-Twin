import json,shutil,hashlib,zipfile
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_07');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_07.blend';PREV=Path('E:/jz/JIA/Rebuild_V24_06')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_07_Fresh_Blend_QA.json').read_text(encoding='utf8'));view=json.loads((R/'V24_07_Preview_States.json').read_text(encoding='utf8'));build=json.loads((R/'V24_07_Build.json').read_text(encoding='utf8'));h=sha(P)
assert qa['status'].startswith('PASS')and not qa['failures']and qa['model_sha256']==view['model_sha256']==build['sha256']==h
assert len(view['views'])==6 and all((R/v['file']).is_file()for v in view['views'])
for n in ['v24_07_common.py','v24_07_build.py','v24_07_doors.py','v24_07_finish.py','v24_07_verify.py','v24_07_render.py','v24_07_package.py','v24_06_common.py','v24_06_roof.py','v24_03_junction_blender.py','v24_qa_blender.py']:shutil.copy2(W/n,O/'Source'/n)
for f in (PREV/'References').iterdir():
 if f.is_file():shutil.copy2(f,O/'References'/f.name)
for src,dst in [('D:/Desktop/问题大全（每个细节）/00004内大门/实景照片.jpg','09_Gate_Door_Real.jpg'),('D:/Desktop/问题大全（每个细节）/00004内大门/理想模型.png','10_Gate_Ideal_Relation.png'),('D:/Desktop/download.png','11_User_Supplied_Junction_View.png')]:
 assert Path(src).is_file(),src
 shutil.copy2(src,O/'References'/dst)
for src in [Path('E:/jz/JIA/Rebuild_V24/Textures/Gate_Carving_HeightAtlas.png'),Path('E:/jz/JIA/Rebuild_V24/Source/ImageGen_Prompt.txt')]:
 if src.is_file():shutil.copy2(src,O/('Textures'if src.suffix=='.png'else'Source')/src.name)
for n in ['V24_06_Fresh_Blend_QA.json','V24_06_Changes.json','V24_06_Resolved_Issues.md','V24_06_Wall_Centerline.json','V24_06_Passage_Paving.json','V24_06_Kitchen_Timber.json']:shutil.copy2(PREV/'Reports'/n,O/'Source'/n)
for n in ['V24_06_Kitchen_Timber.png','V24_06_Passage_Paved.png']:shutil.copy2(PREV/'Reports'/n,R/('Previous_'+n))
note=f'''# V24.07 最终修改结果

完整模型：Blender/Architecture_Complete_V24_07.blend。单位米，原贴图已打包，直接打开无需旧版本。

按最新“1到2”和“正确关系”标注，将V24.06门楼最低檐底由3.500m向下回落0.400m，现为3.100m。2点附近厨房斜檐Z约3.071m。局部按门楼的封闭檐底、台阶线脚和真实屋面轮廓收口；保留居中短檐、前后平衡出挑和压薄的歇山结构。两侧上部柱段及素面墙颈相应缩短，灯笼和顶灯随檐底一起下移。

内大门双扇门已改进：高上芯板、中芯板、窄菱饰格与踢板；芯板通过8mm榫舌嵌入边框，压线为有截面转折的实体闭合构件。每扇下部3颗菱形饰块，增补三处铰链及木门框；保留原曲柄铜拉手和花形底座，细化上方固定门额。沿用深红木色和原铜材质。

门扇原始名称、父级、铰轴、26扇门的动作数据全部保留。默认40帧全开；1帧关闭，20帧半开。新增门扇实体与原石柱、束腰、门额、固定木门框在1、10、20、30、40帧均未发现非五金承接部位的实际三角面穿插；门扇高度和约10mm门头间隙沿用原模型。

厨房只有5组与新檐位相交的构件作局部闭合收口：瓦屋面、瓦垄、弧形压顶、山墙上部补砖、深色压顶边。截口均封闭，材质和UV保留，保存后与全部门楼屋顶构件的实际三角面穿插检查为0。

V24.06已完成的前檐收回约0.618m、院墙向内约0.118m对齐门柱、圈内两树删除、约39.32平方米同材质过道与树坑封平、厨房40对密排椽和曲线托木垂瓜，以及厨房后墙全高封闭均继续保留。厨房仍为一根独立檐廊柱。Reports内Previous前缀的厨房木构和过道图来自V24.06，这些相应构件已逐一比对未变。

保存后重新打开校验{len(qa['checks'])}项，失败0项。原{qa['materials']}套材质、{qa['images']}张图像、15块实体灰度浮雕、26扇门原动作与其他场地通过复核。6张V24.07预览使用原材质，并记录相同模型SHA256。

脚本执行次序：v24_07_build.py → v24_07_finish.py → v24_07_verify.py → v24_07_render.py → v24_07_package.py。重建脚本使用本机保留的V24.06；交付blend本身独立完整。全部旧版本继续保留。
'''
(R/'V24_07_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or f.name.endswith('_Draft_States.json')or f.name in ['V24_07_Manifest.json','V24_07_Bundle_QA.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_07_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_07_Marked_Eave_Height_Improved_Doors.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for row in files:z.write(O/row['file'],arcname='Rebuild_V24_07/'+row['file'])
 z.write(O/'V24_07_Manifest.json',arcname='Rebuild_V24_07/V24_07_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_BUNDLE_CRC_AND_MODEL_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_07_Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
