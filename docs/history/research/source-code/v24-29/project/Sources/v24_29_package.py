from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_29';O=Path('E:/jz/JIA/Rebuild_V24_29');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_29.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text('utf8'));assert sha(source['model'])==source['sha256'];summaries={}
for stem in ['Native','Physics','Measure_Math','Launcher']:
 q=json.loads((R/f'V24_29_{stem}_QA.json').read_text('utf8'))
 assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h)
 summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[r[0]for r in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 q=json.loads((R/f'V24_29_{v}_State.json').read_text('utf8'));assert q['model_sha256']==h and not q['draft'] and (R/q['file']).stat().st_size>10000
assert (R/'V24_29_Measure_UI.png').stat().st_size>10000
for name in ['启动漫游.cmd','打开修正版模型.cmd']:
 s=(Path('E:/jz/JIA/Rebuild_V24_28')/name).read_text('utf8').replace('Architecture_Complete_V24_28.blend','Architecture_Complete_V24_29.blend')
 (O/name).write_text(s,encoding='utf8',newline='\r\n')
readme='''V24.29 三层楼整体降低、门前与原院坪齐平

双击“启动漫游.cmd”进入1.65米人物漫游。
双击“打开修正版模型.cmd”查看可编辑原生模型，默认显示本次门前交接。

按最新指示处理：
1. 三层楼整体下移0.45米，以模型原有院坪-0.45米为基准。
   三层楼的墙、楼板、梁柱、楼梯、门窗、阳台、屋顶及附属管线一起移动；
   各构件相对位置、原层高和门窗动作保持，各层室内地面保持水平。
2. 门前原先分成高低两块的铺装统一齐平，撤掉上一版为承接高楼面增加的分界台阶和抬高部分。
3. 西侧外院按同一基准平顺衔接，清除照片中贴三层楼抬高的横向坡带。
4. 清除原先填在楼房内部、会在降低楼房后穿入室内的土体；院内原排水面压到铺装以下。
5. 厨房、储藏房和院墙保留原位；厨房原檐廊与院坪的正常小高差保留。
6. 前版白墙与青砖墙90度交接、木窗收口、高窗、短檐和厚实院墙瓦顶继续保留。

0.45米来自既有模型的原院坪标高，非本次新增现场测量。
原V24.28未覆盖；本版为独立文件。

漫游：方向键/WASD移动，空格跳跃，Shift快走，右键拖动转向，滚轮调距离。
V切换人眼/第三人称，Home回院落，Esc退出，F8重新进入。
直接打开blend不会自动接管键盘；请使用“启动漫游.cmd”。

测量：L点两点测长度，P沿边界点选后按Enter测面积。
Ctrl点击吸附顶点，Backspace撤销，Esc返回漫游，顶栏可导出CSV。
Ctrl+S保存测量记录；结果为模型尺寸。

Reports中的检查图、原生几何、室内地坪、通行路线与测量界面检查对应本版同一模型哈希。
References收录本次三张用户标注图。Sources为本地重建及检查脚本，重建需要原V24.28文件和本地依赖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
dest=O/'Sources';dest.mkdir(exist_ok=True)
for n in ['build','verify','physics_qa','measure_math_qa','launcher_smoke','render','package']:
 p=W/f'v24_29_{n}.py';shutil.copy2(p,dest/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,dest/n)
for n in ['Source.json','Views.json']:shutil.copy2(D/n,dest/n)
(R/'V24_29_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':source['sha256'],'house_vertical_offset_m':-.45,'courtyard_datum_m':-.45,'checks':summaries,'review_views':views,'dimensions_basis':'Existing model original courtyard datum; no new field survey'},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_29_Lowered_House_Flush_Court_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_29')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,info in manifest.items():
  with z.open('Rebuild_V24_29/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
