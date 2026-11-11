from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_24';O=Path('E:/jz/JIA/Rebuild_V24_24');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_24.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Solid','Physics','Launcher']:
 q=json.loads((R/('V24_24_'+stem+'_QA.json')).read_text('utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q['model_sha256'],h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=['Kitchen_Closure','Gate_Front','Gate_Junction_High','Gate_Back','Paving_Overview','Paving_Close']
for v in views:
 s=json.loads((R/('V24_24_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert(R/s['file']).stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_23/启动漫游.cmd').read_text('utf8').replace('Architecture_Complete_V24_23.blend','Architecture_Complete_V24_24.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_24.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.24 厨房封墙、门前退墙及院落补铺

打开修正版模型.cmd：打开可编辑的原生模型，默认查看厨房北端封墙。
启动漫游.cmd：直接进入1.65米人物第三人称漫游。

方向键 / WASD：走动；空格：跳跃；Shift：快走。
鼠标右键拖动：转向；滚轮：调跟随距离。
V：切换人眼与第三人称；Esc：退出；F8：重新进入；Home：回院落。
顶部“进入人物漫游 / F8”按钮也可以进入。M切换材质与流畅模式。
人物可沿真实楼梯步行上下二、三楼。
直接打开blend不会自动接管按键；请用“启动漫游.cmd”，避免V被编辑器解释为跳关键帧。

本次按150017 / 150243 / 150306 / 150819修正：
1. 厨房靠三层楼端，木柱至木立面之间的红框用白墙封实。
   墙从地面接至现有斜梁，保留落地木柱和柱础外露。
2. 内大门正面侧边砖墙退至原白墙位置Y=-11.73米，退让0.21米。
   正面的灰色收边随墙后退，屋檐交接处补前侧灰色收口。
   内大门后方墙面、门扇动作、雕花柱和门楼屋顶保留。
3. 主楼前黄线范围补同款灰色长方石板，含中间原来较高的灰地坪。
   沿用原石板材料、1.12×0.62米模数、半块错缝、6毫米缝宽，砖缝对齐。
   面层顺原地坪贴合，高于原面2毫米，填缝低1.5毫米，原地坪基体和台阶保持。

储藏房上版修正、院墙装饰、现有瓦面和镬耳、门窗动作均保留。
Reports中六张检查图和全部检查报告来自同一最终原生文件，并记录文件哈希。
尺寸依照片及原模型拟合。本版独立保存，V24.23未覆盖。
Blender原生文件已打包贴图。Sources是修改和检查记录；重建依赖本机原有几何库及V24.23源文件。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for t in ['150017','150243','150306','150819']:
 p=Path('D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg');shutil.copy2(p,refs/p.name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for name in ['v24_24_common.py','v24_16_common.py','v24_24_probe.py','v24_24_geometry.py','v24_24_build.py','v24_24_verify.py','v24_24_solid_qa.py','v24_24_physics_qa.py','v24_24_render.py','v24_24_launcher_smoke.py','v24_24_package.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,sources/name)
for name in ['Source.json','Prepared_Geometry.json','Inventory.json']:
 shutil.copy2(D/name,sources/name)
(R/'V24_24_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'references_are_photo_fitted':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith('Draft_')and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_24_Closure_Gate_Paving_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_24')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,entry in manifest.items():
  with z.open('Rebuild_V24_24/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
