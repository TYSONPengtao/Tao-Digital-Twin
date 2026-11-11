"""Stage native sources/references, then verify and package the final revision."""
import json,hashlib,shutil,zipfile,sys,subprocess
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_17';O=Path('E:/jz/JIA/Rebuild_V24_17');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_17.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
h=sha(P);qa=read(R/'V24_17_Fresh_Blend_QA.json');sol=read(R/'V24_17_Independent_Solid_QA.json');clr=read(R/'V24_17_Independent_Clearance_QA.json');gate=read(R/'V24_17_Gate_Junction_QA.json');build=read(R/'V24_17_Build.json');ret=read(R/'V24_17_Retired_Coping.json')
assert all(a['status'].startswith('PASS')and a['model_sha256']==h for a in [qa,sol,clr,gate])and not qa['failures']
assert build['sha256']==h
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_17_probe.py','v24_17_coping_probe.py','v24_17_diagnose.py','v24_17_common.py','v24_17_prepare.py','v24_17_secondary.py','v24_17_build.py','v24_17_verify.py','v24_17_solids.py','v24_17_gate_probe.py','v24_17_gate_check.py','v24_17_render.py','v24_17_orbit.py','v24_17_package.py','v24_16_common.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for n in scripts:shutil.copy2(W/n,S/n)
C=S/'v24_17';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.json','.npz']:shutil.copy2(p,C/p.name)
for folder,n in [('v24_16','Inventory.json'),('v24_11','QA_Obstacle_Index.json')]:
 C=S/folder;C.mkdir(exist_ok=True);shutil.copy2(W/folder/n,C/n)
refs=O/'References';refs.mkdir(exist_ok=True)
reference_paths=[Path('D:/Desktop/wt/0002储藏房外细碎')/f'屏幕截图 2026-10-18 {n}.jpg'for n in ['145856','145943','150016','150037','150136']]+[Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0509.JPG'),Path('D:/Desktop/wt/0002储藏房外细碎/屏幕截图 2026-10-18 150549.jpg'),Path('D:/Desktop/wt/0001储藏房/屏幕截图 2026-10-18 113659.jpg'),Path('D:/Desktop/wt/0001储藏房/屏幕截图 2026-10-18 135703.jpg')]
refmap=[]
for i,src in enumerate(reference_paths,1):
 dst=refs/f'{i:02d}_{src.name}';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst)
assert sha(src)==sha(dst)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
shutil.copy2('E:/jz/JIA/Rebuild_V24_16/README_V24_16.md',refs/'Prior_V24_16_Corrections.md')
(refs/'Reference_Index.json').write_text(json.dumps({'images':refmap,'source_model':'Original_AsBuilt_Model_UNMODIFIED.3dm','video_reference':'E:/VID_20260507_152114_00_001.mp4','basis':'Current annotations 145856/145943 specify blue brick gables and white inner secondary wall; 150016/150037 remove the projecting screen plinth; 150549 removes the small junction adapter. DJI 0509 constrains closed exterior brick roof edges. Earlier porch photos retain visible timber inside the covered gallery. Photographic fit, not a new survey.'},ensure_ascii=False,indent=2),encoding='utf8')
gap=next(c['minimum_top_surface_separation_m']for c in sol['spatial_checks']if 'Visible storage tiles above'in c['check'])
note=f'''# V24.17 青砖封边、镬耳放大与屋面闪烁修正

完整可编辑文件：Blender/Architecture_Complete_V24_17.blend。贴图内嵌，blend可独立打开。V24.16及原始资料保留。

本轮修改：

- 储藏房两侧上部山墙改青砖，厨房外侧山墙及屋面交接处用砖墙封齐。外侧木基层、梁头和小瓦檐收进墙内；按实景保留檐廊内部的圆柱、梁枋、挂落及门窗。
- 重塑储藏房和厨房的镬耳，采用约2.36m宽的连续肩部与圆顶轮廓。储藏房砖体耳峰由原标高约4.79m提高至5.25m，灰色压顶沿坡面连续收边。厨房与内大门交接处另做局部退让，保留原大门屋顶。
- 储藏房瓦面重新分层：原基层顶面与板瓦争面，现基层下移，筒瓦、凹板瓦和木基层各在正确层位。最终保存网格中，可见瓦面距基层的最小间隔约{gap*1000:.1f}mm。消除旧交接小瓦檐和重复旧瓦帽；新增砖、瓦材质降低微小凹凸与高光。
- 撤去图150016、150037中打叉的主照壁内外凸出底条，保留既有弧墙、基础及已对中的照壁顶。
- 次照壁重做连续实体承托、双坡瓦帽、平直正脊、筒板瓦、瓦当和端部卷头，白色框带与内外白墙收齐。合并的旧围墙瓦帽仅局部撤去{ret['retired_secondary_faces']}个重复三角面，其余原瓦帽网格、UV和材质保留。

保留入口两根竖直圆柱、柱后白墙区域、已退后的木门位置、全部26扇门的动画和1/20/40帧姿态；原地基、后部弧墙、其它建筑与完整场地保持。

保存后复开检查{len(qa['checks'])}项，失败0项。{len(sol['solids'])}组保存实体与{len(sol['spatial_checks'])}项屋面分层/木构封边/次照壁承托检查通过，五处通行空间采样和厨房与内大门交接检查通过。尺寸及轮廓来自照片与既有模型拟合，不是新增实测或工程结构计算。

Reports含8张最终预览、3秒72帧移动视角视频、4张移动视角抽帧，以及保存和独立几何核验报告。视频固定源场景第40帧，仅移动相机，用于查看屋面随视角变化的表现；实际软件的抗锯齿和视口质量设置仍影响远处细瓦线的显示。

References含本轮7张参考图、2张前轮实景檐廊照片、未修改的实景3dm副本及配准信息。Source含本轮构造、检查和预览脚本及网格缓存；重跑完整构造脚本依赖本机原V24.16模型、Blender和Python环境，交付的blend本身不需要这些输入。

最终模型SHA256：{h}
'''
(O/'README_V24_17.md').write_text(note,encoding='utf8');(R/'V24_17_Resolved_Issues.md').write_text(note,encoding='utf8')
if '--stage'in sys.argv:
 print('STAGED sources and references',flush=True);sys.exit(0)
views=read(R/'V24_17_Preview_States.json');orbit=read(R/'V24_17_Orbit_States.json')
assert views['model_sha256']==orbit['model_sha256']==h
assert len(views['views'])==8 and all((R/r['file']).is_file()for r in views['views'])
assert orbit['frame_count']==len(orbit['frames'])==72 and orbit['source_scene_frame']==40
for row in orbit['frames']:
 assert sha(D/'Orbit_Frames'/f"Orbit_{row['frame']:04d}.png")==row['sha256']
for i in [1,24,48,72]:assert sha(R/f'V24_17_Orbit_Check_{i:03d}.png')==orbit['frames'][i-1]['sha256']
ffprobe=Path('C:/Users/PENG/anaconda3/Library/bin/ffprobe.exe');video=R/'V24_17_Exterior_Orbit.mp4'
vr=json.loads(subprocess.check_output([str(ffprobe),'-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,avg_frame_rate,nb_read_frames,duration','-of','json',str(video)],text=True))['streams'][0]
assert int(vr['width'])==960 and int(vr['height'])==720 and int(vr['nb_read_frames'])==72 and vr['avg_frame_rate']=='24/1'
assert abs(float(vr['duration'])-3)<.01
(R/'V24_17_Video_QA.json').write_text(json.dumps({'status':'PASS_ENCODED_72_FRAME_PREVIEW','model_sha256':h,'sha256':sha(video),'video':vr},indent=2),encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_17_Manifest.json','V24_17_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_17_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_17_Brick_Gables_Stable_Roof.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_17/'+r['file'])
 z.write(O/'V24_17_Manifest.json','Rebuild_V24_17/V24_17_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_17/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_BUNDLE_CRC_AND_ALL_FILE_SHA256','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1}
(O/'V24_17_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
