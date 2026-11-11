from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_26';O=Path('E:/jz/JIA/Rebuild_V24_26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_26.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Solid','Physics','Measure_Math','Launcher']:
 q=json.loads((R/('V24_26_'+stem+'_QA.json')).read_text('utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[r[0]for r in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 s=json.loads((R/('V24_26_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert(R/s['file']).stat().st_size>10000
assert(R/'V24_26_Measure_UI.png').stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_25/启动漫游.cmd').read_text('utf8').replace('Architecture_Complete_V24_25.blend','Architecture_Complete_V24_26.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_26.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.26 青砖封墙、厨房短出檐、厚实内院墙瓦顶

双击“启动漫游.cmd”，直接进入1.65米人物漫游。
双击“打开修正版模型.cmd”，打开可编辑原生模型，默认查看内院墙瓦顶。

漫游：方向键/WASD移动；空格跳跃；Shift快走；右键拖动转向；滚轮调距离。
V切换人眼/第三人称，Home回院落，Esc退出，F8重新进入。
直接打开blend不会自动接管键盘；使用“启动漫游.cmd”进入。

测量（模型单位为米）：
L或顶栏“测长度”：点击模型表面的两个端点。
P或顶栏“测面积”：沿边界依次点选，按Enter完成，支持凹多边形。
面积结果同时给出面内面积、水平投影面积、周长。
Ctrl点击吸附命中面上的顶点。Backspace撤销一个点或最近一条结果。
Esc先回漫游，再按Esc退出；顶栏可导出CSV。Ctrl+S保存测量记录。

本次修正：
1. 厨房北端原白色封墙及旁边露出的窄转角，统一为相邻的青砖材质。
2. 厨房靠储藏房的南端出檐由约0.40米收至约0.12米。
   瓦面、灰色山墙收边及镬耳相应收进；原屋面坡度、规则瓦列与储藏房屋面保留。
3. 内院L形墙顶双坡瓦顶加宽至约0.90米，每侧从250毫米墙身挑出约0.325米。
   新增65毫米厚瓦下垫层、两排搭接筒瓦板瓦、花纹瓦当、花朵/菱形镂空花脊和圆脊帽。
   转角按同一45度斜接；墙身、勒脚及长短框饰保留，瓦顶收头避开雕花门柱。

尺寸为现有模型及实景照片的比例拟合，非新增现场实测。
V24.25的卫生间高窗、内大门墙缝封闭、储藏房浅灰铺装、门窗动作与测量功能保留。

Reports收录本版八张检查图、实际漫游测量界面截图及对应模型的验证报告。
References为本次六张参考图，模型已打包贴图。
Sources为修改与检查脚本，重建需本机几何库及V24.25源文件。
本版独立保存，未覆盖V24.25。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for p in [Path('D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg')for t in ['210452','210606','210832','211022','211048']]+[Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0095.JPG')]:shutil.copy2(p,refs/p.name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for n in ['common','probe','probe_extra','geometry','build','verify','solid_qa','physics_qa','measure_math_qa','render','launcher_smoke','package']:
 p=W/('v24_26_'+n+'.py');shutil.copy2(p,sources/p.name)
for n in ['v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,sources/n)
for n in ['Source.json','Prepared_Geometry.json','Inventory.json','Views.json']:shutil.copy2(D/n,sources/n)
(R/'V24_26_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'measurement_demo':'V24_26_Measure_UI.png','dimensions_photo_fitted':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_26_Brick_Short_Eave_Courtyard_Coping_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_26')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,e in manifest.items():
  with z.open('Rebuild_V24_26/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
