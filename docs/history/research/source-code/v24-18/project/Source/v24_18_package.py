import json,hashlib,shutil,zipfile,sys,subprocess
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_18';O=Path('E:/jz/JIA/Rebuild_V24_18');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_18.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
h=sha(P);qa=read(R/'V24_18_Fresh_Blend_QA.json');solid=read(R/'V24_18_Independent_Solid_QA.json');build=read(R/'V24_18_Build.json');proof=read(R/'V24_18_Corrections.json')
assert qa['status'].startswith('PASS')and solid['status'].startswith('PASS')and not qa['failures'];assert qa['model_sha256']==solid['model_sha256']==build['sha256']==h;assert sha(build['source'])==build['source_sha256']
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_18_probe.py','v24_18_detail_probe.py','v24_18_extra_probe.py','v24_18_common.py','v24_18_prepare.py','v24_18_windows.py','v24_18_screen.py','v24_18_finish.py','v24_18_build.py','v24_18_verify.py','v24_18_solids.py','v24_18_render.py','v24_18_before_grade.py','v24_18_motion.py','v24_18_package.py','v24_16_common.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for n in scripts:shutil.copy2(W/n,S/n)
C=S/'v24_18';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.json','.npz']:shutil.copy2(p,C/p.name)
for folder,n in [('v24_16','Inventory.json'),('v12_screenwall_reference','Mutation.json')]:
 C=S/folder;C.mkdir(exist_ok=True);shutil.copy2(W/folder/n,C/n)
refs=O/'References';refs.mkdir(exist_ok=True);reference_paths=[Path('D:/Desktop/屏幕截图 2026-10-18 185635.jpg'),Path('C:/Users/PENG/AppData/Local/Temp/codex-clipboard-2bd0ee50-dabd-4df9-9c5c-67aafe6f4c07.jpg'),Path('C:/Users/PENG/AppData/Local/Temp/codex-clipboard-533278c8-aa17-43c6-941c-5e8ed8c1abc8.jpg')]+[Path('D:/Desktop')/f'屏幕截图 2026-10-18 {n}.jpg'for n in ['190241','190411','190522','190601','190829']]+[Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0509.JPG')];refmap=[]
for i,src in enumerate(reference_paths,1):
 dst=refs/f'{i:02d}_{src.name}';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst);assert sha(src)==sha(dst)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
(refs/'Reference_Index.json').write_text(json.dumps({'images':refmap,'source_model':'Original_AsBuilt_Model_UNMODIFIED.3dm','basis':'185635 fits smaller narrow gable ears; the floating-house screenshot is checked against saved slab and soil geometry; 190241 and the fan annotation require a recessed triangular end roof; 190411/190522/190601 require continuous exterior material courses; 190829 defines twelve outward sashes and ten false white corner posts. DJI 0509 retains closed brick exterior roof edges.'},ensure_ascii=False,indent=2),encoding='utf8')
ground=proof['house_grounding'];gcheck=next(r for r in solid['checks']if 'grade at interior'in r['check']);nstat=len(gcheck['interior_samples'])+len(gcheck['edge_samples']);umin=min(r['horizontal_metric_scale_min']for r in qa['uv_checks']if r['horizontal_metric_scale_min']is not None);umax=max(r['horizontal_metric_scale_max']for r in qa['uv_checks']if r['horizontal_metric_scale_max']is not None)
note=f'''# V24.18 接地、窄镬耳、凹照壁与外开窗修正

完整可编辑模型：Blender/Architecture_Complete_V24_18.blend。贴图内嵌，可独立打开；V24.17和原始资料保留。

## 三层建筑离地原因与处理

检查原保存网格后，首层楼板底面标高为{ground['slab_bottom_z']:.6f}m；房屋周边及楼内原地坪取样约-0.462至-0.480m。楼板与地坪之间缺少连续的封闭基座，因此出现约0.312至0.330m的透空缝。原楼板、楼层、楼梯和门洞之间没有发生整体平移。

本版沿原首层楼板的真实平面轮廓补齐连续实体勒脚，主体顶边精确接至楼板底，底部至-0.720m；内退8mm的舌口伸入原楼板12mm。外侧竖面不与原楼板侧面重合，避免接缝争面。按原地面可取样范围检查{nstat}处，均接地。Reports/V24_18_House_Grade_Before_V17.png与V24_18_House_Grade.png使用同一机位和照明，分别展示原V24.17透空缝和本版补齐后的状态。

## 其余修改

- 储藏房、厨房四处镬耳按185635参考改为窄直立轮廓，根部宽由2.36m收至1.24m，窄头约0.32m宽。耳峰相对屋脊由0.90m改为0.56m，储藏房砖体耳峰标高由5.25m降至4.91m。保留青砖封闭山墙与连续灰压顶。
- 主照壁两端分叉脊之间重做下凹三角瓦面。短檐中心比两侧分叉边线低约0.43m，中心沿外排方向微降约0.07m；筒板瓦、边脊、瓦床与下部承托同步适配。裁去旧白灰内饰高出墙冠的局部残片，凹面内没有白色尖片穿出。
- 围墙与储藏房外侧共用材质分界标高：-1.05m以下毛石，-1.05至-0.38m条石，以上青砖。按原墙线弧长和世界高度重新排UV，青砖与条石灰缝使用米制程序纹理，并保留原照片的风化色；毛石照片镜像重复，减少照片边缘断缝。保存网格的水平纹理比例为{umin:.6f}至{umax:.6f}，竖向为原高度坐标；墙体和基础外轮廓保留。
- 红圈位置共12扇独立外开窗：五组凸窗正面两端各2扇，以及三层中部大窗两端2扇。保留中间固定玻璃、上亮和原室内窗栏；大窗10处错误的白色转角实体柱移除，斜侧玻璃接至薄黑色窗框。原建筑网格柱保留。

## 窗扇操作

第1帧：关闭。第20帧：向外半开32.5度。第40帧：向外全开65度。文件默认显示第40帧。12个独立铰链对象带HINGED_OUTWARD属性与各自动作，原26扇门的动作及1/20/40帧姿态保留。

Reports/V24_18_Outward_Windows.mp4为40帧外开演示；House_Front、Windows_Detail及相应Closed图片用于对比开启状态。

## 核验与文件

最终文件复开{len(qa['checks'])}项核验通过；独立读取{len(solid['solids'])}组实体和{len(solid['checks'])}项接地、屋面承托、旧白片清理、假柱切除及窗扇碰撞检查通过。原地坪、楼层、楼梯、原门动画和完整场地保留。造型与细部尺寸为参考照片及既有模型拟合。

Reports含11张最终状态图、1张原V24.17接地问题对照、外开窗视频及3张动作抽帧，另附核验报告。References含本轮8张原标注图、DJI 0509实景照片、未修改的原始3dm副本和配准信息。Source含构造、材质、检查和预览脚本及网格缓存；重跑构造脚本依赖本机原V24.17输入及Python/Blender环境，交付blend本身无需这些输入。

最终模型SHA256：{h}
'''
(O/'README_V24_18.md').write_text(note,encoding='utf8');(R/'V24_18_Diagnosis_and_Changes.md').write_text(note,encoding='utf8')
if '--stage'in sys.argv:
 print('STAGED_V24_18',flush=True);sys.exit(0)
views=read(R/'V24_18_Preview_States.json');motion=read(R/'V24_18_Window_Motion_States.json');cmp=read(R/'V24_18_Grade_Comparison_States.json')
assert views['model_sha256']==motion['model_sha256']==h and len(views['views'])==11
assert all((R/r['file']).is_file()for r in views['views']);assert cmp['before_model_sha256']==build['source_sha256']and(R/cmp['before_file']).is_file();assert len(motion['frames'])==motion['frame_count']==40 and motion['fps']==12 and len(motion['outward_sashes'])==12
for f in motion['frames']:assert sha(D/'Window_Frames'/f"Window_{f['frame']:04d}.png")==f['sha256']
for f in [1,20,40]:assert sha(R/f'V24_18_Window_Motion_{f:02d}.png')==motion['frames'][f-1]['sha256']
video=R/'V24_18_Outward_Windows.mp4';ffprobe=Path('C:/Users/PENG/anaconda3/Library/bin/ffprobe.exe');vs=json.loads(subprocess.check_output([str(ffprobe),'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames,duration','-of','json',str(video)],text=True))['streams'][0];assert int(vs['nb_read_frames'])==40 and vs['avg_frame_rate']=='12/1'and int(vs['width'])==960 and int(vs['height'])==720
(R/'V24_18_Video_QA.json').write_text(json.dumps({'status':'PASS_OUTWARD_WINDOW_PREVIEW','model_sha256':h,'sha256':sha(video),'video':vs},indent=2),encoding='utf8');files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_18_Manifest.json','V24_18_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_18_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8');Z=W.parent/'outputs/Production_1QK_Blender_V24_18_Grounded_House_Outward_Windows.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_18/'+r['file'])
 z.write(O/'V24_18_Manifest.json','Rebuild_V24_18/V24_18_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_18/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_BUNDLE_CRC_AND_ALL_FILE_SHA256','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_18_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
