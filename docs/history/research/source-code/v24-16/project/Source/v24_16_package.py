import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_16';O=Path('E:/jz/JIA/Rebuild_V24_16');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_16.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_16_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_16_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_16_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_16_Preview_States.json').read_text());build=json.loads((R/'V24_16_Build.json').read_text())
assert all(r['status'].startswith('PASS')for r in [qa,solid,clr])and not qa['failures'];assert all(r['model_sha256']==h for r in [qa,solid,clr,views]);assert build['sha256']==h;assert len(views['views'])==9;assert all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
for n in ['v24_16_probe.py','v24_16_analyse.py','v24_16_common.py','v24_16_prepare.py','v24_16_screen.py','v24_16_build.py','v24_16_verify.py','v24_16_solids.py','v24_16_alignment_plot.py','v24_16_render.py','v24_16_package.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
C=S/'v24_16';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.json','.npz']:shutil.copy2(p,C/p.name)
for folder,n in [('v24_11','QA_Obstacle_Index.json'),('v12_screenwall_reference','Mutation.json')]:
 C=S/folder;C.mkdir(exist_ok=True);shutil.copy2(W/folder/n,C/n)
refs=O/'References';refs.mkdir(exist_ok=True);reference_paths=[Path('D:/Desktop/wt/0001储藏房')/f'屏幕截图 2026-10-18 {n}.jpg'for n in ['135637','135703','135741','123950','124623','140132']]+[Path('D:/Desktop/屏幕截图 2026-10-18 101233.jpg'),Path('D:/DJI/0003/DCIM/101MEDIA/DJI_0068.JPG'),Path('D:/DJI/0003/DCIM/101MEDIA/DJI_0069.JPG'),Path('D:/Desktop/DJI_0069.jpg')];refmap=[]
for i,src in enumerate(reference_paths,1):
 dst=refs/f'{i:02d}_{src.name}';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst);assert sha(src)==sha(dst)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
shutil.copy2('E:/jz/JIA/Rebuild_V24_15/README_V24_15.md',refs/'Prior_V24_15_Corrections.md')
(refs/'Reference_Index.json').write_text(json.dumps({'images':refmap,'source_model':'Original_AsBuilt_Model_UNMODIFIED.3dm','video_reference':'E:/VID_20260507_152114_00_001.mp4','basis':'Entrance bay fitted from 135703, with 135637/135741 model annotations; screen roof centred on the saved native wall faces, end fan and horns fitted to 101233/140132 and DJI 0068/0069. Photographic fit, not new surveyed dimensions.'},ensure_ascii=False,indent=2),encoding='utf8')
align=[r for r in solid['spatial_checks']if 'centred on actual lower wall'in r['check']];maxerr=max(r['maximum_offset_m']for r in align)
note=f'''# V24.16 入口白墙与照壁中线修正

完整可编辑模型：Blender/Architecture_Complete_V24_16.blend。贴图均内嵌。原V24.15保留，未覆盖。

入口圆柱和柱础向檐廊外侧移0.57m，柱后至退后的木隔扇之间补齐白灰侧墙；白墙可见深度约0.82m，按照片近似拟合。仍为两根竖直圆柱，柱列在平面上相对围栏斜置，入口一端较宽。檐枋保持同一标高，并按新柱位重接挑梁、雀替和挂落。木门窗和铰链位置未再次移动，26扇门的全部动作及1/20/40帧姿态均保留。

照壁旧瓦顶沿固定直线布置，而既有墙身在平面上有缓弯，最大轴线偏离约0.305m。本版从原墙两侧面在1m高处取中点，按同一条中线重建石底座、墙冠、连续窄承托、三道叠涩、瓦面、正脊和分叉脊。两侧等挑，端面白芯位于墙心。分叉段延长，端部有横向扇铺筒板瓦；宽根陶质翘角与斜脊及实体脊床相接。长檐瓦当逐一对应60道筒瓦排。

独立读取最终保存网格，屋顶、承托和底座共检查{sum(r['section_count']for r in align)}个截面，距原墙身中线的最大误差{maxerr*1000:.2f}mm。主要屋顶、承托、分叉脊床和翘角根部形成一个连通的正体积实体；原复合墙体仅调整墙冠，平面坐标和2.65m以下的原几何保持不变。检查包括屋顶与承托的实际体积搭接、柱与石础接触、柱与白墙分开、木构/屋面及玻璃/木棂无误穿插，以及五处通行空间采样。

保留储藏房既有两坡瓦顶、封闭镬耳山墙、三榀传统梁架及室内四组花格横披、原地基和后部弧墙、厨房退让与连续后墙、平直次照壁、原场地和其它建筑。照壁内面继续使用白灰墙。入口铁皮棚继续删除。

本版是照片和既有模型的几何修正。柱位、墙段和细部尺寸不是新增现场实测；对中、承托及搭接检查不等同于工程结构计算。

保存后复开检查{len(qa['checks'])}项、失败0项；{len(solid['solids'])}组独立实体及{len(solid['spatial_checks'])}项空间/承托检查通过，五处通行空间采样通过。Reports中9张最终预览与核验报告对应同一模型SHA256：{h}

预览包括入口白墙、储藏房正面、檐下、照壁外侧/端部/斜俯视/俯视/内侧及全场。References包含本轮10张原参考图、未修改的实景3dm副本和原配准信息。Source包含构造及核验脚本和网格缓存；重建依赖本机原V24.15输入及Python/Blender环境，交付blend本身可独立打开。
'''
(O/'README_V24_16.md').write_text(note,encoding='utf8');(R/'V24_16_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_16_Manifest.json','V24_16_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_16_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8');Z=W.parent/'outputs/Production_1QK_Blender_V24_16_Centred_Screenwall_White_Entry.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_16/'+r['file'])
 z.write(O/'V24_16_Manifest.json','Rebuild_V24_16/V24_16_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_16/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_BUNDLE_CRC_AND_ALL_FILE_SHA256','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_16_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
