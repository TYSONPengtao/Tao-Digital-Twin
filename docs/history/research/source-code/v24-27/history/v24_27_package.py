from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_27';O=Path('E:/jz/JIA/Rebuild_V24_27');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_27.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Grade','Physics','Measure_Math','Launcher']:
 q=json.loads((R/('V24_27_'+stem+'_QA.json')).read_text('utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[r[0]for r in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 s=json.loads((R/('V24_27_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert(R/s['file']).stat().st_size>10000
assert(R/'V24_27_Measure_UI.png').stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_26/启动漫游.cmd').read_text('utf8').replace('Architecture_Complete_V24_26.blend','Architecture_Complete_V24_27.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_27.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.27 主屋、院坪与西侧地面高差修正

双击“启动漫游.cmd”进入1.65米人物漫游。
双击“打开修正版模型.cmd”查看可编辑原生模型，默认看卫生间外侧地坪。

本次修正：
1. 主屋近墙院坪恢复至一层楼面下约150毫米，保留原一级入口台阶及门廊楼板。
2. 门前院坪按现有高、低标高顺坡连接厨房檐廊；厨房檐廊-0.40米及排水边带保留。
3. 西侧旧贴墙鼓起坡面改为较长的连续坡面：近墙约-0.15米，外侧约-0.504米，主要过渡宽约5.875米。
4. 将接地面连续收至楼板边缘下方，修整铺装下层，消除墙脚与铺装边缘露底。
5. 碰撞网格由修改后的可见地坪更新，已复测台阶上下、外侧行走和到厨房檐廊的连续路线。

尺寸以既有一层楼板及实景关系拟合，非新增现场测量。
原房屋、厨房、储藏房楼板、门窗动作、卫生间高窗、门柱、屋面及内院墙瓦顶保留。

漫游：方向键/WASD移动；空格跳跃；Shift快走；右键拖动转向；滚轮调距离。
V切换人眼/第三人称，Home回院落，Esc退出，F8重新进入。
直接打开blend不会自动接管键盘；请使用“启动漫游.cmd”。

测量：L点两点测长度；P沿边界依次点选并按Enter测面积。
Ctrl点击可吸附顶点，Backspace撤销，Esc返回漫游；顶栏可导出CSV。
Ctrl+S保存测量记录。测量结果为模型尺寸。

Reports中的六张检查图及测量界面对应本版文件；References收录本次两张参考图。
Sources为修改与检查脚本，重建需要本机几何依赖和V24.26源文件。
本版独立保存，V24.26未覆盖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for t in ['123610','123632']:
 p=Path('D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg');shutil.copy2(p,refs/p.name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for n in ['probe','grade','build','verify','grade_qa','physics_qa','measure_math_qa','render','launcher_smoke','package']:
 p=W/('v24_27_'+n+'.py');shutil.copy2(p,sources/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,sources/n)
for n in ['Source.json','Prepared_Geometry.json','Inventory.json','Views.json','Ground_Samples.json']:shutil.copy2(D/n,sources/n)
(R/'V24_27_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'measurement_demo':'V24_27_Measure_UI.png','dimensions_photo_fitted':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_27_House_Courtyard_Grade_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_27')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,e in manifest.items():
  with z.open('Rebuild_V24_27/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
