import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_13';O=Path('E:/jz/JIA/Rebuild_V24_13');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_13.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_13_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_13_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_13_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_13_Preview_States.json').read_text());build=json.loads((R/'V24_13_Build.json').read_text())
assert all(r['status'].startswith('PASS')for r in[qa,solid,clr])and not qa['failures'];assert all(r['model_sha256']==h for r in[qa,solid,clr,views]);assert build['sha256']==h;assert len(views['views'])==6
assert all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_13_probe.py','v24_13_geometry.py','v24_13_prepare.py','v24_13_build.py','v24_13_verify.py','v24_13_solids.py','v24_13_render.py','v24_13_package.py','v24_12_geometry.py','v24_11_geometry.py','v24_09_roof.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for name in scripts:shutil.copy2(W/name,S/name)
C=S/'v24_13';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.suffix in['.json','.npz']:shutil.copy2(p,C/p.name)
# The rebuild script reads the two original ornament islands from V24.10.
C=S/'v24_11';C.mkdir(exist_ok=True);shutil.copy2(W/'v24_11/SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz',C/'SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz');shutil.copy2(W/'v24_11/QA_Obstacle_Index.json',C/'QA_Obstacle_Index.json')
for p in(W/'v24_11').glob('QA_Obstacle_*.npz'):shutil.copy2(p,C/p.name)
refs=O/'References';refs.mkdir(exist_ok=True)
shutil.copy2('D:/Desktop/downl5oad.png',refs/'01_User_Blue_Front_Roof_Outline.png')
shutil.copy2('D:/Desktop/屏幕截图 2026-10-18 094354.jpg',refs/'02_User_AsBuilt_and_Model_Plan_Comparison.jpg')
for name in['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:
 shutil.copy2(W/'v24_10'/name,refs/name)
shutil.copy2('E:/jz/实景三维场景模型.3dm',refs/'Original_AsBuilt_Model_UNMODIFIED.3dm')
shutil.copy2('E:/jz/JIA/Rebuild_V24_12/README_V24_12.md',refs/'Prior_V24_12_Corrections.md')
note=f'''# V24.13 按蓝线收正储藏房前坡

完整建筑和场地：Blender/Architecture_Complete_V24_13.blend。原V24.12保留未覆盖。1/20/40帧为门关闭/半开/打开；全部26扇门的动作和姿态保留。照片贴图内嵌，blend可独立打开。

本次按D:/Desktop/downl5oad.png蓝线和094354实景对比，收回前坡左侧多伸出的楔形部分约0.438米。前坡两侧为平行直边，前檐与屋脊在平面中平行，标高各自水平，两主坡均为平面。前檐在模型坐标Y=-16.480，屋脊Y=-12.150；其余边界保留场景配准位置。木基层、屋架、椽尾、山墙上部和柱头一起适配，旧木基层不会穿出新瓦面。

次照壁已调平的墙冠、内外装饰和白色框线保持。仅藏在储藏房入口侧的末端短回墙向檐下转入，以保持次照壁端部低于储藏房瓦檐。屋顶与原右侧薄金属棚保持两处独立结构。储藏房地基、弧形后墙、厨房退让和连续后墙等此前校正保留。

最终保存文件复开检查{len(qa['checks'])}项，失败0项。新增及修改实体独立检查通过，旧木基层与屋面无穿插，五处通行采样无相交。Reports有6张同一最终模型的正立面、俯视、接头、背面及全场预览，配套完整检查数据。检查值为当前模型坐标中的几何数据，不是新增现场测量。

模型SHA256：{h}

输入V24.12 SHA256：{build['source_sha256']}

References保存本轮两张标记图、实景3dm原文件副本、上一版记录和拟合信息。Source保存构造与核验脚本、输入及保存网格缓存。重建需本机原V24.12输入和Python/Blender依赖，交付blend本身独立完整。
'''
(O/'README_V24_13.md').write_text(note,encoding='utf8');(R/'V24_13_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in['V24_13_Manifest.json','V24_13_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_13_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_13_Squared_Storage_Front_Roof.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_13/'+r['file'])
 z.write(O/'V24_13_Manifest.json','Rebuild_V24_13/V24_13_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
out={'status':'PASS_BUNDLE_CRC_AND_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_13_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
