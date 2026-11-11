from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_32';O=Path('E:/jz/JIA/Rebuild_V24_32');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_32.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text('utf8'));assert sha(source['model'])==source['sha256'];prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));qa={}
for stem in ['Native','Surface','Physics','Measure_Math','Launcher','Viewport']:
 q=json.loads((R/f'V24_32_{stem}_QA.json').read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);qa[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[v[0]for v in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 q=json.loads((R/f'V24_32_{v}_State.json').read_text('utf8'));assert q['model_sha256']==h and not q['draft']and(R/q['file']).stat().st_size>10000
for n in ['V24_32_Measure_UI.png','V24_32_Repair_Contact_Sheet.jpg']:assert(R/n).stat().st_size>10000
readme='''V24.32 外墙平整、窗下去重、完整扶手与三楼门开向修正

打开修正版模型.cmd：打开可继续编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游，附长度和面积测量。

本版按 2026-10-21 02:45—02:58 标注图修正：
1. 五个卫生间高窗下，旧补块外饰面多出 112 毫米。将补块切回与
   相邻外饰面一致的平面，高窗、磨砂玻璃及窗洞位置保留。
2. 删除两圈独立的楼层饰带，补齐后方墙体；收平突出的梁板边。
   清除后立面楼板边剩余的小凸块，保持竖向墙面连续。
3. 飘窗下完整墙体与原石材窗套合并；删除与下一层墙体重叠的面。
   三个原重面交接位置各约 0.161 平方米重复表面已清除。
4. 删除圈出的两段平台短栏杆，连接四跑楼梯扶手与端柱，补齐三楼
   楼梯口后侧的缺失护栏。二楼后侧是继续上三楼的入口，保持畅通；
   三楼前侧护栏的立柱脚收回楼板支撑范围。
5. 清理楼梯前白墙留下的横梁凸带，墙体延续至楼板交接处。
6. 三楼标记的蜂蜜色房门改到另一侧铰接，仍向房间内开启；同步
   修正闭合、中间、打开动画。原门框洞口与其他 25 组门动作保留。
7. 三楼露台瓷砖网格中保留了一个旧门洞形缺口。按原矩形瓷砖
   材质与分缝继续补齐，取消白色大块与周边瓷砖的色差。
8. 删除四棵简单树模型；青砖墙外露的白色背面、端面改用原青砖
   材质和连续的米制贴图，保留内侧白墙及上部装饰白带。

内外院铺装、白色建模场地、道路及台阶采用 V24.31 已修复版本。
模型纹理和本次 10 张标注图已打包。旧 V24.31 原文件未覆盖。
扶手细部比例依据实景照片及既有模型拟合，没有新增现场测量。

漫游：WASD / 方向键移动，空格跳跃，Shift 快走，右键拖动转向，
滚轮调距离，V 切换人眼 / 第三人称，M 切换材质预览，Home 回院落，
Esc 退出，F8 再进入。直接打开 blend 不会自动接管键盘。

测量：L 点两点测长度；P 沿边界点选后按 Enter 测面积。
Ctrl 点击吸附顶点，Backspace 撤销，Esc 返回漫游，顶栏可导出 CSV。
Ctrl+S 保存测量记录。测量值为模型尺寸。

Reports：最终修正图、移动视角材质预览、原生几何 / 表面去重 /
通行 / 启动与测量检查。检查报告的 SHA256 对应本次最终模型。
References：本次 10 张原始标注图。
Sources：修复前导出、准备后的修复网格、最终模型读回网格和源代码。
原生模型无需 Sources 即可直接打开编辑。重放构建需要本机 V24.31
源文件；几何准备脚本另需 Python 3.12、NumPy、Manifold3D、Shapely。
Sources 中的 v24_20/Prepared_Geometry.json 只保存本次使用的贴图路径
字段，完整旧版加工记录仍在本机工作目录。
Manifest_SHA256.json：交付文件清单及校验值。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
S=O/'Sources';SD=S/'v24_32';SD.mkdir(parents=True,exist_ok=True)
for stem in ['inspect','probe','prepare','rail_profiles','build','verify','surface_qa','physics_qa','measure_math_qa','launcher_smoke','viewport_qa','render','contact_sheet','package']:
 shutil.copy2(W/f'v24_32_{stem}.py',S/f'v24_32_{stem}.py')
for n in ['v24_06_common.py','v24_qa_blender.py','v24_16_common.py','v24_18_finish.py']:shutil.copy2(W/n,S/n)
for n in ['Source.json','Views.json','Prepared_Geometry.json','Before_Snapshot.json','Geometry_Index.json','Inventory.json','Materials.json','Final_Geometry_Index.json','Perimeter_Exterior_Probe.json','Target_Door_Before.json']:shutil.copy2(D/n,SD/n)
for n in ['v16/Drain_Segments.json','v24_16/Inventory.json']:
 dst=S/n;dst.parent.mkdir(exist_ok=True);shutil.copy2(W/n,dst)
sr=S/'v24_20';sr.mkdir(exist_ok=True);old=json.loads((W/'v24_20/Prepared_Geometry.json').read_text('utf8'));(sr/'Prepared_Geometry.json').write_text(json.dumps({'scope':'finish mapping only','wall_uv_route':old['wall_uv_route']},ensure_ascii=False),encoding='utf8')
for p in D.glob('SRC_*.npz'):shutil.copy2(p,SD/p.name)
for row in prep['raw_objects']+json.loads((D/'Final_Geometry_Index.json').read_text('utf8')):shutil.copy2(D/row['file'],SD/row['file'])
(R/'V24_32_Corrections.json').write_text(json.dumps(prep['proof'],ensure_ascii=False,indent=2),encoding='utf8')
(R/'V24_32_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':source['sha256'],'checks':qa,'review_views':views,'reference_images':10,'source_version':'V24.31','dimensions_basis':'Retained model geometry and marked photographs; railing profiles fitted to photos, no new field survey'},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix not in ['.blend1','.blend2']and not(p.parent==R and p.name.startswith(('Draft_','Before_')))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_32_Flat_Facades_Continuous_Railing_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_32')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,info in manifest.items():
  with z.open('Rebuild_V24_32/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256'],rel
out={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':qa};(D/'Delivery_Result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
