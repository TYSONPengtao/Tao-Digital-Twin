import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_12';O=Path('E:/jz/JIA/Rebuild_V24_12');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_12.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_12_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_12_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_12_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_12_Preview_States.json').read_text());build=json.loads((R/'V24_12_Build.json').read_text())
assert all(r['status'].startswith('PASS')for r in[qa,solid,clr])and not qa['failures'];assert all(r['model_sha256']==h for r in[qa,solid,clr,views]);assert build['sha256']==h;assert len(views['views'])==6
assert all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_12_probe.py','v24_12_geometry.py','v24_12_prepare.py','v24_12_build.py','v24_12_verify.py','v24_12_solids.py','v24_12_render.py','v24_12_package.py','v24_11_geometry.py','v24_09_roof.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for name in scripts:shutil.copy2(W/name,S/name)
C=S/'v24_12';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.suffix in['.json','.npz']:shutil.copy2(p,C/p.name)
# The rebuild script reads the two original ornament islands from V24.10.
C=S/'v24_11';C.mkdir(exist_ok=True);shutil.copy2(W/'v24_11/SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz',C/'SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz');shutil.copy2(W/'v24_11/QA_Obstacle_Index.json',C/'QA_Obstacle_Index.json')
for p in(W/'v24_11').glob('QA_Obstacle_*.npz'):shutil.copy2(p,C/p.name)
refs=O/'References';refs.mkdir(exist_ok=True)
shutil.copy2('D:/Desktop/屏幕截图 2026-10-18 082437.jpg',refs/'01_User_Level_Secondary_Screen_and_Storage_Roof.jpg')
for name in['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:
 shutil.copy2(W/'v24_10'/name,refs/name)
shutil.copy2('E:/jz/实景三维场景模型.3dm',refs/'Original_AsBuilt_Model_UNMODIFIED.3dm')
shutil.copy2('E:/jz/JIA/Rebuild_V24_11/README_V24_11.md',refs/'Prior_V24_11_Corrections.md')
note=f'''# V24.12 次照壁调平与储藏房屋顶校正

打开 Blender/Architecture_Complete_V24_12.blend。完整场地、建筑、内嵌照片贴图及26扇门动画均保留。1帧关门，20帧半开，40帧开门。默认相机 V24_12_User_Front。V24.11文件保留未覆盖。

## 本次修正

- 次照壁的墙冠、瓦压顶、内侧檐带和外侧两块装饰框一起调平。外侧装饰带为平直墙面，顶部和底部采用固定水平标高；主照壁旁藏在接头内的旧斜墙冠同时校正。
- 储藏房屋脊和前檐改为平行、水平的直线，两处主坡恢复平面。取消上一版依据斜向柱位对整片屋面的扭曲映射；筒瓦、仰瓦与脊瓦按新平面重排。原脊端装饰保留。
- 厨房侧原谷缝锚点保留，以局部平面连接片接入新屋面。山墙顶部、后墙顶部、上部木架、椽尾和柱头随屋面校正。旧粗面木基层裁切至新檐线与檐底之内，清除穿过瓦面的旧木片。前廊的两根柱身仍竖直，柱位平面连线继续与栏杆斜交，入口端更宽。
- 次照壁端部继续在储藏房檐口之下。檐下净空从最终保存文件重新测取。

## 此前已确认内容

储藏房占地、厨房向院外退让、两根廊柱的位置与柱础、储藏房弧形后墙、连续厨房后墙、无入口铁皮棚、照壁内侧白灰饰面、主照壁分叉脊和石底座、内大门以及其他建筑均保留。外侧另一处储藏区薄金属棚继续保留。全部26扇门在1/20/40帧的门轴姿态与V24.11相同。

## 检查与图像

最终保存后复开核对 {len(qa['checks'])} 项，失败0项。屋脊、前檐、两个主坡与次照壁墙冠使用几何射线采样检查。16组变更网格通过独立闭合实体重建；原有围墙整体是带内部共面的分段复合网格，沿用原结构，外边界开边数仍为0，内部共边数和退化三角形数未增加。该复合组未宣称已转为单一流形实体。五处入口及檐廊通行采样无相交。

Reports有同一最终保存模型的6张预览：User_Front、Level_Elevation、Eave_Junction、Top、Rear_Arc、Whole_Site。正立面采用正交相机，可直接检查水平关系；透视图中的线条随视点产生透视收敛。

修改依据用户本轮标记和已配准的实景模型。数值为现有模型坐标下的校正与检查，不是新增现场测量。

## 文件与复现

模型 SHA256：{h}

输入 V24.11 SHA256：{build['source_sha256']}

References提供本轮标记、实景3dm原文件副本、此前校正记录和拟合元数据。Source提供生成、复核脚本及实际保存网格缓存。完整blend可独立打开；重建脚本需原V24.11输入和本机Python/Blender依赖。
'''
(O/'README_V24_12.md').write_text(note,encoding='utf8');(R/'V24_12_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in['V24_12_Manifest.json','V24_12_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_12_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_12_Level_Screenwall_Storage_Roof.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_12/'+r['file'])
 z.write(O/'V24_12_Manifest.json','Rebuild_V24_12/V24_12_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
out={'status':'PASS_BUNDLE_CRC_AND_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_12_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
