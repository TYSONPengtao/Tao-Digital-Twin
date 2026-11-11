import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_15';O=Path('E:/jz/JIA/Rebuild_V24_15');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_15.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_15_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_15_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_15_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_15_Preview_States.json').read_text());build=json.loads((R/'V24_15_Build.json').read_text())
assert all(r['status'].startswith('PASS')for r in [qa,solid,clr])and not qa['failures'];assert all(r['model_sha256']==h for r in [qa,solid,clr,views]);assert build['sha256']==h;assert len(views['views'])==7
assert all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
for n in ['v24_15_probe.py','v24_15_prepare.py','v24_15_build.py','v24_15_verify.py','v24_15_solids.py','v24_15_render.py','v24_15_package.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
C=S/'v24_15';C.mkdir(exist_ok=True)
for n in ['Before_Snapshot.json','Inventory.json','Prepared_Geometry.json','Solid_Export_Index.json','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry.npz']:shutil.copy2(D/n,C/n)
for p in D.glob('SAVED_*.npz'):shutil.copy2(p,C/p.name)
C=S/'v24_11';C.mkdir(exist_ok=True);shutil.copy2(W/'v24_11/QA_Obstacle_Index.json',C/'QA_Obstacle_Index.json')
refs=O/'References';refs.mkdir(exist_ok=True);refmap=[]
for i,n in enumerate(['124027','123950','124130','124221'],1):
 src=Path(f'D:/Desktop/wt/0001储藏房/屏幕截图 2026-10-18 {n}.jpg');dst=refs/f'{i:02d}_Storage_Reference_{n}.jpg';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst);assert sha(src)==sha(dst)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
shutil.copy2('E:/jz/JIA/Rebuild_V24_14/README_V24_14.md',refs/'Prior_V24_14_Corrections.md')
(refs/'Reference_Index.json').write_text(json.dumps({'images':refmap,'source_model':'Original_AsBuilt_Model_UNMODIFIED.3dm','previous_video':'E:/VID_20260507_152114_00_001.mp4','scope':'This turn uses the four supplied photographs to refit the storage eaves and interior timber frame. Earlier registered site, gables, foundation, screenwall and doorway placement are retained.'},ensure_ascii=False,indent=2),encoding='utf8')
note=f'''# V24.15 储藏房传统木构屋檐与四组花格横披

完整建筑和场地：Blender/Architecture_Complete_V24_15.blend。贴图内嵌，可独立打开。原V24.14保留未覆盖。全部26扇门的动作与1/20/40帧的关门、半开、开门姿态均保留。

本轮针对124027截图中的悬空断梁和重复屋架，结合123950、124130实景屋檐/室内仰视及124221室内横披照片重做。原储藏房上部旧屋架清除，原木门、下部隔扇和玻璃保留；三榀梁架、平梁、短柱、七道圆檩和62根密排圆椽、连续木望板分别为可编辑的封闭网格。梁、檩、椽有连续搭接，原来的独立断梁头没有继续保留。梁檩端头收在既有封闭山墙之内。

檐廊两根圆柱的平面位置、斜向柱列与柱础保留，柱头统一接入水平檐枋。补全挑檐梁、简化雀替及浅雕卷纹、通透的连续挂落。门上方补四组八角花格固定横披和木封板，木棂内外两面都可见，玻璃按木棂分格嵌入，四组之间用立框封闭。新木构沿构件方向设置木纹。

原已校正的两坡屋顶与瓦面、镬耳山墙、次照壁、储藏房地基及弧形后墙、厨房与连续后墙、其余全场建筑均保留。本轮没有再次移动门框、玻璃隔扇或铰链，门的原开合动作不变。入口铁皮棚继续删除。

广角照片的整幅弯曲没有直接做成梁檩歪斜。梁架形制、构件尺度和细部按照片近似拟合，模型数值并非新增现场实测。

保存后复开{len(qa['checks'])}项检查，失败0项；独立读取保存网格检查{len(solid['solids'])}组封闭实体和{len(solid['spatial_checks'])}项空间关系通过。新木构的主要实体形成连通整体，没有独立悬空梁段；木构与瓦屋面底层、玻璃与木棂无体积穿插。两根廊柱与墙体分开，后排木柱落在原石础上。入口、檐廊、门洞等五处通行盒采样通过。

Reports有同一最终模型的7张1600×1200预览：正面、檐廊近景、檐下仰视、室内门面、室内梁架仰视、入口廊道与全场。模型SHA256：{h}

输入V24.14 SHA256：{build['source_sha256']}

References保存本轮四张参考图、原始实景3dm副本、原配准地块信息和上版说明。Source保存构造/核验脚本与必要网格缓存。重建需本机原V24.14输入和Python/Blender依赖；交付blend本身完整独立。
'''
(O/'README_V24_15.md').write_text(note,encoding='utf8');(R/'V24_15_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_15_Manifest.json','V24_15_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_15_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_15_Traditional_Timber_Eaves.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_15/'+r['file'])
 z.write(O/'V24_15_Manifest.json','Rebuild_V24_15/V24_15_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_15/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_BUNDLE_CRC_AND_ALL_FILE_SHA256','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_15_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
