from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_31';O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_31.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text('utf8'));assert sha(src['model'])==src['sha256'];prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));qa={}
for stem in ['Native','Surface','Physics','Measure_Math','Launcher','Viewport']:
 q=json.loads((R/f'V24_31_{stem}_QA.json').read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);qa[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=[v[0]for v in json.loads((D/'Views.json').read_text('utf8'))]
for v in views:
 q=json.loads((R/f'V24_31_{v}_State.json').read_text('utf8'));assert q['model_sha256']==h and not q['draft']and(R/q['file']).stat().st_size>10000
for n in ['V24_31_Measure_UI.png','V24_31_Repair_Contact_Sheet.jpg']:assert(R/n).stat().st_size>10000
readme='''V24.31 补洞、重面清理、完整窗下墙、白天花与实景木扶手

打开修正版模型.cmd：打开可继续编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游，附长度和面积测量。

本版按 2026-10-21 凌晨的 14 张参考图修正：
1. 补齐内门、厨房及储藏间前的缺失地面，封闭厨房廊前台阶下的缝隙；
   入口道路、补洞及储藏间过渡统一使用原浅灰混凝土材质。
2. 删除重叠的旧道路和道路下方穿出的土面；白色场地与路沿石各有独立
   顶面，取消约 2.38 平方米完全共面的重叠。铺装和路沿底床让出石材
   体积，清除贴近表面的隐蔽重面，减少移动视角时的闪烁。
3. 五组飘窗下的墙体补成完整封闭实体，并接至楼板边；保留窗框、玻璃、
   开窗动画和原石材材质。
4. 房屋各层楼板、屋顶及楼梯的实际下表面改为白色；室内地坪仍为灰色。
5. 楼梯扶手按实景照片改为深红木色车木栏杆、圆球端柱和圆滑扶手；
   保留原楼梯位置与踏步标高。清理楼梯白墙上的框架凸台、内洞口边饰
   及角部多余柱面，墙体完整延伸至天花，楼板边缘与墙面收平。
6. 五个卫生间高窗的旧窗套和下方凸块清除；把旧补墙收回原墙面厚度，
   窗下恢复平整、完整的白墙。高窗及磨砂玻璃保留。
7. 删除三楼右卧室的红色地板面层，保留完整灰色结构楼板。

三层楼的标高、室内水平地坪、原大门和 26 组门动画保留。
外院白色场地仍为水平可编辑实体，可继续在上面建模。
旧 V24.30 原文件未覆盖。
扶手细部为依据照片及既有模型拟合，尺寸没有新增现场测量。

漫游：WASD / 方向键移动，空格跳跃，Shift 快走，右键拖动转向，
滚轮调距离，V 切换人眼 / 第三人称，M 切换材质预览，Home 回院落，
Esc 退出，F8 再进入。直接打开 blend 不会自动接管键盘。

测量：L 点两点测长度；P 沿边界点选后按 Enter 测面积。
Ctrl 点击吸附顶点，Backspace 撤销，Esc 返回漫游，顶栏可导出 CSV。
Ctrl+S 保存测量记录。测量值为模型尺寸。

Reports：最终检查图、材质预览、原生几何 / 重面 / 通行 / 启动检查。
References：本次 14 张原始标注及实景参考图。
Sources：保存的修复网格、源文件校验值和构建 / 验证脚本。
原生模型已打包纹理，可直接打开编辑，不需要执行 Sources。
重放 Sources 的构建脚本另需本机 V24.30 源文件；几何准备脚本作为
加工记录保留，另依赖工作目录的原始导出与本机几何 Python 库。
Manifest_SHA256.json：交付文件清单及校验值。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
S=O/'Sources';SD=S/'v24_31';SD.mkdir(parents=True,exist_ok=True)
for stem in ['build','prepare','verify','surface_qa','physics_qa','measure_math_qa','launcher_smoke','viewport_qa','render','package']:
 shutil.copy2(W/f'v24_31_{stem}.py',S/f'v24_31_{stem}.py')
for n in ['v24_06_common.py','v24_qa_blender.py','v24_16_common.py']:shutil.copy2(W/n,S/n)
for n in ['Source.json','Views.json','Prepared_Geometry.json','Before_Snapshot.json','Final_Geometry_Index.json']:shutil.copy2(D/n,SD/n)
for row in prep['raw_objects']:shutil.copy2(D/row['file'],SD/row['file'])
for row in json.loads((D/'Final_Geometry_Index.json').read_text('utf8')):shutil.copy2(D/row['file'],SD/row['file'])
(R/'V24_31_Corrections.json').write_text(json.dumps(prep['proof'],ensure_ascii=False,indent=2),encoding='utf8')
(R/'V24_31_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':qa,'review_views':views,'reference_images':14,'source_version':'V24.30','dimensions_basis':'Retained model levels and marked photographs; railing proportions fitted to photos, no new field survey'},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix not in ['.blend1','.blend2']and not p.name.startswith(('Draft_','Before_'))and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_31_Repaired_Surfaces_White_Ceilings_Photo_Stairs_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_31')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,info in manifest.items():
  with z.open('Rebuild_V24_31/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==info['sha256'],rel
out={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':qa};(D/'Delivery_Result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
