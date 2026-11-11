import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_10';O=Path('E:/jz/JIA/Rebuild_V24_10');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_10.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa=json.loads((R/'V24_10_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_10_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_10_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_10_Preview_States.json').read_text());build=json.loads((R/'V24_10_Build.json').read_text());proof=json.loads((R/'V24_10_AsBuilt_Storage_and_Entry.json').read_text());h=sha(P)
assert qa['status'].startswith('PASS')and not qa['failures']
assert solid['status'].startswith('PASS')and clr['status'].startswith('PASS')
assert qa['model_sha256']==solid['model_sha256']==clr['model_sha256']==views['model_sha256']==build['sha256']==h
assert len(views['views'])==9 and all((R/r['file']).is_file()for r in views['views'])
scripts=['v24_10_reference.py','v24_10_probe.py','v24_10_video.py','v24_10_sections.py','v24_10_fit.py','v24_10_plan.py','v24_10_prepare.py','v24_10_ground_probe.py','v24_10_ground.py','v24_10_drain_prepare.py','v24_10_build.py','v24_10_verify.py','v24_10_solid_audit.py','v24_10_clearance.py','v24_10_render.py','v24_10_package.py','v24_09_roof.py','v24_09_common.py','v24_08_geometry.py','v24_06_common.py','v24_03_junction_blender.py','v24_qa_blender.py']
for n in scripts:shutil.copy2(W/n,O/'Source'/n)
for n in['v14/Roof_Junction_QA.json','v19/Facade_Segments.json']:
 dst=O/'Source'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/n,dst)
cache=O/'Source/v24_10';cache.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.suffix in ['.json','.npz']and p.name not in['Final_Ray_Probe.json','Solid_Comparison.json']:shutil.copy2(p,cache/p.name)
for n in['REF_Top.png','REF_Entry.png','REF_Oblique.png','BASE_Top.png','BASE_Entry.png','AsBuilt_Sections.png','Plot_Boundary_Comparison.png']:shutil.copy2(D/n,R/('Evidence_'+n))
refs=[('D:/Desktop/屏幕截图 2026-10-17 135013.jpg','01_User_Plot_Comparison.jpg'),('D:/Desktop/屏幕截图 2026-10-17 211621.jpg','02_User_Entrance_Error.jpg'),('D:/Desktop/屏幕截图 2026-10-12 001239.jpg','03_User_AsBuilt_Entrance.jpg'),('D:/Desktop/问题/屏幕截图 2026-10-12 180115.jpg','04_Previous_Actual_Storage_Exterior.jpg'),('E:/jz/实景三维场景模型.3dm','05_Original_AsBuilt_Model_UNMODIFIED.3dm')]
for src,n in refs:shutil.copy2(src,O/'References'/n)
video=O/'References/MP4_Views';video.mkdir(exist_ok=True)
for p in (D/'Video').iterdir():shutil.copy2(p,video/p.name)
note=f'''# V24.10 储藏房地块、房体与小入口修正

完整模型为 Blender/Architecture_Complete_V24_10.blend。米制，贴图已内嵌，保留完整建筑和场地。1帧关门，20帧半开，40帧开门；26扇原有可动门继续使用原动作。V24.09原文件保留。

## 实景依据

主几何依据为用户指定 E:/jz/实景三维场景模型.3dm，原文件 SHA256：{proof['source_3dm']}。采用既有 JIA ENU→LOCAL 米制坐标转换，不缩放或变形实景原文件。保留原始参考3dm副本，以及同镜位的实景俯视、斜视和入口对照图。储藏房主体两坡从原始实景网格拟合，南、北坡加权残差分别约17mm、16mm；这是对该摄影测量模型的拟合残差，不是现场测量精度。

视频依据为 E:/VID_20260507_152114_00_001.mp4。MP4_Views保存4、8、10、12、14、34、38、54秒的透视抽帧和源视频SHA256。0–12秒说明厨房砖山墙、次照壁、金属雨棚和小入口关系；12–34秒说明檐廊、木构与储藏房入口；34–54秒说明檐廊尽端通向半开外储藏区。视频只用于外观和连接关系核对。

## 本次结果

储藏房局部基底按原实景模型Z=-0.8m的连续挡墙外边线修正，35mm简化后保留斜收前沿和东端圆折。西边是与保留厨房基础的内部接缝。原模型局部外轮廓近似面积59.43㎡，本次同区域模型轮廓约49.98㎡；这里比较的是重建模型局部轮廓，不是现场丈量面积。基础、房体、门窗、木构、屋顶、石栏、外金属棚和落水管一起调整。

取消把前沿推到Y=-17.15m的低矮后加延檐及旧基础扩块。主体瓦顶回到实景两坡和檐口，北边顺实景斜向收进，保留与厨房相连的屋面接缝。连续挡土基底使用闭合实体，毛石和上部深色条石依原有材质分带；七个石栏分格共十四个实际开口随地块移动。

小入口从砖山墙与次照壁之间进入檐廊，墙端开口延至木立面前。入口地面与檐廊连续，补齐视频中的金属雨棚、附墙框架、檐下连接及次照壁外侧白色框带。两扇储藏房门的门轴和门板随房体调整，动作保持。

清除缩回地块后遗留的高填土块、旧路肩与错位墙趾。相邻地形用原始实景地面控制点补齐并平滑微小扫描噪声，边缘最多185mm高程过渡；原照片颜色以原生顶点属性表达，原UV投影也保留，未修改或生成位图。与修正地面相交的一棵保留树只调整落地高程，XY未变。外围排水与墙趾从此前同一场地的高精度原生实体重建局部裁切，解决三角网格裁切后的微小破口。

原内大门最低檐底3.100m、门板与石浮雕、厨房向外退让0.450m、主体建筑、照壁分叉瓦顶与曲面承托及其他门动作继续保留。涉及厨房的改动限于储藏房接缝附近，厨房朝内院的立面和退让结果保持。

## 核验与预览

保存后重新打开核验{len(qa['checks'])}项，失败0项。独立实体核验{len(solid['solids'])}组；对既有CAD共边/UV分离坐标在1nm–10μm范围规范化后检查闭合定向实体，不把原生共边当作通道堵塞。入口、檐廊、储藏房门口、东端通道四个净空盒与保存的墙、柱、木构、栏板和开门状态门扇作实体相交检查，堵塞体积均为0。净空盒是校验采样空间，不是现场实测尺寸。完整检查数据在Reports。

九张彩色预览均来自同一最终模型：俯视、入口外侧、入口近景、入口上方、檐廊、储藏房内、外侧金属棚、外观和全场地。默认相机是入口近景。

模型SHA256：{h}
输入V24.09 SHA256：{build['source_sha256']}

Source提供构造、源几何缓存、视频抽帧、复开和独立实体检查脚本。重建须本机的V24.09输入模型和相应Python/Blender依赖；交付blend本身独立完整。隐藏结构和不能从实景辨认的节点仍按现有模型及照片拟合。
'''
(O/'README_V24_10.md').write_text(note,encoding='utf8');(R/'V24_10_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for f in sorted(O.rglob('*')):
 if not f.is_file()or f.suffix=='.blend1'or f.name.startswith('Draft_')or 'Draft_States'in f.name or f.name in['V24_10_Manifest.json','V24_10_Bundle_QA.json']:continue
 files.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'V24_10_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_10_Storage_Plot_AsBuilt_Entry_Correction.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_10/'+r['file'])
 z.write(O/'V24_10_Manifest.json','Rebuild_V24_10/V24_10_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_BUNDLE_CRC_AND_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_10_Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
