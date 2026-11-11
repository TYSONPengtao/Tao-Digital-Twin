from pathlib import Path
import json,hashlib,zipfile,shutil,py_compile
W=Path(__file__).parent;D=W/'v24_33';O=Path('E:/jz/JIA/Rebuild_V24_33');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_33.blend'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text('utf8'));assert sha(source['model'])==source['sha256'];prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));qa={}
for stem in ['Native','Surface','Physics','Measure_Math','Launcher','Viewport']:
 q=json.loads((R/f'V24_33_{stem}_QA.json').read_text('utf8'));assert q['status'].startswith('PASS') and not q['failures'] and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);qa[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[v[0] for v in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 q=json.loads((R/f'V24_33_{v}_State.json').read_text('utf8'));assert q['model_sha256']==h and not q['draft'] and (R/q['file']).stat().st_size>10000
for n in ['V24_33_Measure_UI.png','V24_33_Repair_Contact_Sheet.jpg','V24_33_Overall_Review.jpg']:assert (R/n).stat().st_size>10000
readme='''V24.33 本次8张标注图的问题修正

打开修正版模型.cmd：打开可继续编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游，附长度和面积测量。

042455 / 042615：楼梯口的白带是下层墙体占据了楼板带。
将这部分归并到真实楼板，统一灰色表面，保留楼层标高与楼梯空洞。
042534：删除最高高出约8厘米的旧露台找坡板，恢复原楼板的连续灰色
地面；裁掉门廊瓦屋面穿进露台的小角，裁切底部低于楼面，避免重面。
003911：复核楼梯白墙的横向凸带，保留上一版已收平的墙面。
042705：删除厨房北端旧柱头、立柱延续段，收回饰条端头，消除砖墙
上的悬挂木件和小木屑；其余门廊柱、屋檐木构与木门保持原状。
042738：删除与连续通道重叠的旧门槛；将廊下高出6毫米的地面降至
原储物间-0.40米楼面并合并到灰色通道，保持原入口坡度。
025023：三楼标记的木门已在V24.32换到对侧铰链；本次保留正确
开向，复核全部26组门在闭合、中间、打开时的动作，不再次翻回。
042922：去除南侧青砖墙末段错误的白色覆盖层，恢复下方原有青砖
照片贴图和连续墙体；删除打叉的单根多余石栏端柱，保留相邻栏板、
白色装饰顶带和瓦压顶。

本版另存，V24.32原模型未覆盖。纹理与本次8张标注图均已打包。
本次未改变楼梯踏步尺寸、原外墙登记线及门窗洞口。
修复依据已有模型和用户标注，没有新增现场实测尺寸。

漫游：WASD / 方向键移动，空格跳跃，Shift快走，右键拖动转向，
滚轮调距离，V切换人眼 / 第三人称，M切换材质，Home回院落，
Esc退出，F8再进入。直接打开blend不会自动接管键盘。
测量：L点两点测长度；P沿边界点选后按Enter测面积。
Ctrl点击吸附顶点，Backspace撤销，Esc返回漫游，顶栏可导出CSV。
Ctrl+S保存测量记录；测量值为模型尺寸。

Reports：本版最终画面、材质预览、逐项几何与通行检查。
References：本次8张原始标注图。
Sources：修复源代码、修前/准备/最终读回网格、定位与检查数据。
原生模型不依赖Sources即可编辑；重放构建需本机V24.32源文件。
几何准备脚本需Python3.12、NumPy、Manifold3D、SciPy。
Sources/v24_10/Prepared_Geometry.json仅保留所用石栏端柱定位数据。
Manifest_SHA256.json：交付文件清单及校验值。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
S=O/'Sources';SD=S/'v24_33';SD.mkdir(parents=True,exist_ok=True)
scripts=list(W.glob('v24_33_*.py'))
for p in scripts:
 compile(p.read_text('utf8'),str(p),'exec');shutil.copy2(p,S/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py','v24_16_common.py']:shutil.copy2(W/n,S/n)
for p in D.glob('*.json'):
 if p.name!='Delivery_Result.json':shutil.copy2(p,SD/p.name)
for p in D.glob('SRC_*.npz'):shutil.copy2(p,SD/p.name)
for row in prep['raw_objects']+json.loads((D/'Final_Geometry_Index.json').read_text('utf8')):shutil.copy2(D/row['file'],SD/row['file'])
sd=S/'v24_16';sd.mkdir(exist_ok=True);shutil.copy2(W/'v24_16/Inventory.json',sd/'Inventory.json')
sd=S/'v24_10';sd.mkdir(exist_ok=True);old=json.loads((W/'v24_10/Prepared_Geometry.json').read_text('utf8'));(sd/'Prepared_Geometry.json').write_text(json.dumps({'scope':'Only original stone guard bay stations used to locate the marked terminal column.','guard_bays':old['guard_bays']},ensure_ascii=False),encoding='utf8')
(R/'V24_33_Corrections.json').write_text(json.dumps(prep['proof'],ensure_ascii=False,indent=2),encoding='utf8')
(R/'V24_33_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':source['sha256'],'checks':qa,'review_views':views,'reference_images':8,'source_version':'V24.32','dimensions_basis':'Existing model and annotated photographs; no new field measurements.'},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*') if p.is_file() and p.suffix not in ['.blend1','.blend2'] and not(p.parent==R and p.name.startswith(('Draft_','Before_'))) and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_33_Flush_Floors_Clean_Walls_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,Path('Rebuild_V24_33')/p.relative_to(O))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for rel,info in manifest.items():
  with z.open('Rebuild_V24_33/'+rel) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256'],rel
out={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':qa};(D/'Delivery_Result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
