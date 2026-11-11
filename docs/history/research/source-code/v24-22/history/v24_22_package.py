from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_22';O=Path('E:/jz/JIA/Rebuild_V24_22');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_22.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256']
summaries={}
for stem in ['Native','Solid','Physics','Launcher']:
 q=json.loads((R/('V24_22_'+stem+'_QA.json')).read_text(encoding='utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q['model_sha256'],h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=['Side_Enclosure','Porch_Eye','Facade','Interior_East','Interior_Gable','Side_South']
for v in views:
 s=json.loads((R/('V24_22_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert (R/s['file']).stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_21/启动漫游.cmd').read_text(encoding='utf8').replace('Architecture_Complete_V24_21.blend','Architecture_Complete_V24_22.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+ 'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_22.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.22 厨房山墙、木梁与檐廊修正版

打开修正版模型.cmd：打开可编辑的 Blender 原生模型，默认显示侧墙围合。
启动漫游.cmd：启动 1.65 米人物漫游，默认第三人称跟随。

方向键 / WASD：走动；空格：跳跃；Shift：快走。
鼠标右键拖动：调整方向；滚轮：跟随距离。
V：人眼 / 第三人称切换；Esc：退出；F8：重新进入。
顶部“进入人物漫游 / F8”按钮也可以进入，Home 回院落。
M 切换材质预览与流畅模式。可按真实楼梯上二楼、三楼。
直接打开 blend 后尚未加载漫游脚本时，请用“启动漫游.cmd”。
本次调整
1. 按 084908，厨房侧墙上部顺屋面出挑，灰色线脚及弧形收口接回砖墙。
2. 合并山墙与墙身，清除重复斜墙、薄饰面和露砖问题；厨房内侧统一白墙。
3. 按 083528 / 083630 整理靠墙柱列、水平木枋、弧形梁及短承木，柱脚落地。
4. 檐廊每处保留一根横向挑梁，清理重复横梁和旧悬挂构件。
5. 按 DJI_0114 / DJI_0116 / 084117，补齐外侧连续方格、阶梯纹镂空挂落。
6. 更新建筑碰撞，保留 1.65 米人物、门窗动作、瓦面接缝与外院装饰。

Reports 中六张图是从这个原生文件重新渲染的检查图。报告与模型文件哈希一致。
本次几何尺寸依照片和原模型拟合；未新增现场测量数据。
Sources 为修改及检查脚本记录。重建脚本使用本机既有几何库和上一版原文件。
原生 blend 已打包贴图，可直接编辑与查看；旧版本没有覆盖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+s+'.jpg'for s in ['083528','083630','084117','084853','084908']]+['D:/DJI/0003/DCIM/101MEDIA/DJI_0114.JPG','D:/DJI/0003/DCIM/101MEDIA/DJI_0116.JPG']:
 shutil.copy2(fn,refs/Path(fn).name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for name in ['v24_22_common.py','v24_16_common.py','v24_22_probe.py','v24_22_shared_gable_probe.py','v24_22_geometry.py','v24_22_build.py','v24_22_verify.py','v24_22_solid_qa.py','v24_22_physics_qa.py','v24_22_render.py','v24_22_launcher_smoke.py','v24_22_package.py','v24_06_common.py','v24_qa_blender.py','v24_21_start_roam.py']:
 shutil.copy2(W/name,sources/name)
for name in ['Source.json','Prepared_Geometry.json','Inventory.json']:
 shutil.copy2(D/name,sources/name)
reviewdata={'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'references_are_photo_fitted':True}
(R/'V24_22_Delivery_QA.json').write_text(json.dumps(reviewdata,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for p in O.rglob('*'):
 if not p.is_file():continue
 rel=p.relative_to(O)
 if p.suffix=='.blend1' or p.name.startswith('Draft_') or p.name in ['Manifest_SHA256.json']:continue
 files.append(p)
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files}
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_22_Kitchen_Enclosure_Timber_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_22')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,entry in manifest.items():
  with z.open('Rebuild_V24_22/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
