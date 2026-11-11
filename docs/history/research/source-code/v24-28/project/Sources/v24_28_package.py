from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_28';O=Path('E:/jz/JIA/Rebuild_V24_28');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_28.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Grade','Physics','Measure_Math','Launcher']:
 q=json.loads((R/('V24_28_'+stem+'_QA.json')).read_text('utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[r[0]for r in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 s=json.loads((R/('V24_28_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert(R/s['file']).stat().st_size>10000
assert(R/'V24_28_Measure_UI.png').stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_26/启动漫游.cmd').read_text('utf8').replace('Architecture_Complete_V24_26.blend','Architecture_Complete_V24_28.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_28.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.28 外部齐平、内部连续台阶、厨房端墙及平直白墙修正

双击“启动漫游.cmd”进入1.65米人物漫游。
双击“打开修正版模型.cmd”查看可编辑原生模型，默认检查连续台阶。

本次合并修正：
1. 三层楼卫生间外侧至内院墙转角的外部地面改为齐平，去掉贴墙鼓起的坡面。
2. 按最新download.png红线，台阶沿厨房檐廊外缘直线接到三层楼入口，取消原斜台阶；东侧高、西侧低。
3. 三层楼所有室内楼板、地坪、门槛及柱体保留原标高，室内不跟随外部起伏。
4. 厨房北端山墙退回原封墙平面，屋檐、灰边及耳部收回正常端线；窗边墙体按180毫米收口，裁掉穿过木窗的部分。
5. 面对的白墙取消靠厨房的上抬端，墙顶和檐线水平；白墙与厨房青砖墙呈90度直接交接，合并为单一闭合墙体，清除折面、窄条和内部重复面。
6. 补齐高侧墙脚铺装，并将原花盆放回修改后的地面。

台阶两端按原厨房檐廊与主屋入口标高衔接；中间几何依据照片标注拟合，非新增现场实测。
三层楼各层楼板均保留，门窗动作、高窗、内大门、储藏房、厨房南端短檐和内院厚瓦顶保留。

漫游：方向键/WASD移动；空格跳跃；Shift快走；右键拖动转向；滚轮调距离。
V切换人眼/第三人称，Home回院落，Esc退出，F8重新进入。
直接打开blend不会自动接管键盘；请使用“启动漫游.cmd”。

测量：L点两点测长度；P沿边界点选并按Enter测面积。
Ctrl点击吸附顶点，Backspace撤销，Esc返回漫游；顶栏可导出CSV。
Ctrl+S保存测量记录；结果为模型尺寸。

Reports检查图、原生几何、通行路线、室内地坪和测量界面检查均对应本版模型哈希。
References收录本次参考图；Sources为本机重建/检查脚本，重建需原缓存及几何依赖。
V24.26与V24.27未覆盖，本版独立保存。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for t in ['123610','123632','151433','151622','151816','152427']:
 p=Path('D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg');shutil.copy2(p,refs/p.name)
for p in (D/'References').glob('*.png'):shutil.copy2(p,refs/p.name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for n in ['extra','prepare','build','verify','grade_qa','physics_qa','measure_math_qa','render','launcher_smoke','mark_probe','finalize','package']:
 p=W/('v24_28_'+n+'.py');shutil.copy2(p,sources/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py','v24_16_common.py','v24_27_grade.py']:shutil.copy2(W/n,sources/n)
for n in ['Source.json','Prepared_Geometry.json','Inventory.json','Views.json','Extra_Files.json']:shutil.copy2(D/n,sources/n)
(R/'V24_28_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'measurement_demo':'V24_28_Measure_UI.png','dimensions_photo_fitted':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_28_Level_Yard_Step_Wall_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_28')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,e in manifest.items():
  with z.open('Rebuild_V24_28/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
