from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_23';O=Path('E:/jz/JIA/Rebuild_V24_23');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_23.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Solid','Physics','Launcher']:
 q=json.loads((R/('V24_23_'+stem+'_QA.json')).read_text(encoding='utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q['model_sha256'],h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=['Kitchen_North','Gate_Front','Gate_Pier','Storage_Joint','Storage_Wide','Storage_Foot']
for v in views:
 s=json.loads((R/('V24_23_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert (R/s['file']).stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_21/启动漫游.cmd').read_text(encoding='utf8').replace('Architecture_Complete_V24_21.blend','Architecture_Complete_V24_23.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+ 'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_23.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.23 厨房端柱、内大门与储藏房修正版

打开修正版模型.cmd：打开可编辑的原生模型，默认显示厨房靠三层楼端。
启动漫游.cmd：启动 1.65 米人物，默认第三人称跟随。

方向键 / WASD 走动，空格跳跃，Shift 快走。
鼠标右键拖动调整方向，滚轮调跟随距离。
V 切换人眼与第三人称，Esc 退出，F8 重新进入，Home 回院落。
顶部“进入人物漫游 / F8”按钮也可以进入。M 切换材质与流畅模式。
可沿真实楼梯步行上下二、三楼。直接打开 blend 时请运行内嵌启动脚本，
或退出后双击“启动漫游.cmd”，方向键才会由人物漫游接管。

本次按新截图修正
1. 123051：厨房靠三层楼端补落地木柱、柱础、柱头及支撑；端墙退回木立面后，檐廊可通行。
2. 123121 + 内大门理想模型：墙和灰色收边退出雕花门柱，墙接在柱后，门柱、雕花和门动作完整保留。
3. 123155：储藏房上下墙面接平；突出砖带收到原墙端，外挑屋檐以木收边衔接；屋顶交角补实；墙脚补面顺原地坪接坡，修掉裂缝及凸边。

上一版厨房木构、连续方格挂落、瓦面交接、镬耳和院墙装饰保留。
Reports 中六张检查图直接来自这个原生文件，状态记录和检查报告与其哈希一致。
原生 blend 已打包贴图。尺寸依照片及原模型拟合，未增加现场测量数据。
Sources 为修改及检查记录；重建脚本使用本机原有几何库和 V24.22 原文件。
本版独立保存，旧版未覆盖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+s+'.jpg'for s in ['123051','123121','123155']]+['D:/Desktop/问题大全（每个细节）/00004内大门/理想模型.png']:
 shutil.copy2(fn,refs/Path(fn).name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for name in ['v24_23_common.py','v24_16_common.py','v24_23_probe.py','v24_23_geometry.py','v24_23_build.py','v24_23_verify.py','v24_23_solid_qa.py','v24_23_physics_qa.py','v24_23_render.py','v24_23_launcher_smoke.py','v24_23_package.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,sources/name)
for name in ['Source.json','Prepared_Geometry.json','Inventory.json','Ground_Grade_Scene.json']:
 shutil.copy2(D/name,sources/name)
(R/'V24_23_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'references_are_photo_fitted':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith('Draft_')and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_23_Kitchen_Gate_Storage_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_23')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,entry in manifest.items():
  with z.open('Rebuild_V24_23/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
