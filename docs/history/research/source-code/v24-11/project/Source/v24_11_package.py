import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_11';O=Path('E:/jz/JIA/Rebuild_V24_11');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_11.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_11_Fresh_Blend_QA.json').read_text(encoding='utf8'));solid=json.loads((R/'V24_11_Independent_Solid_QA.json').read_text(encoding='utf8'));clr=json.loads((R/'V24_11_Independent_Clearance_QA.json').read_text(encoding='utf8'));views=json.loads((R/'V24_11_Preview_States.json').read_text(encoding='utf8'));build=json.loads((R/'V24_11_Build.json').read_text(encoding='utf8'));proof=json.loads((R/'V24_11_Corrections.json').read_text(encoding='utf8'))
assert qa['status'].startswith('PASS')and not qa['failures'];assert solid['status'].startswith('PASS')and clr['status'].startswith('PASS')
assert qa['model_sha256']==solid['model_sha256']==clr['model_sha256']==views['model_sha256']==build['sha256']==h
assert len(views['views'])==11 and all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_11_probe.py','v24_11_analyze.py','v24_11_geometry.py','v24_11_prepare.py','v24_11_build.py','v24_11_verify.py','v24_11_solid_clearance.py','v24_11_render.py','v24_11_plan.py','v24_11_package.py','v24_09_roof.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for n in scripts:shutil.copy2(W/n,S/n)
C=S/'v24_11';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.suffix in ['.npz','.json']and p.name not in ['Ray_Probe.json']:shutil.copy2(p,C/p.name)
prior=S/'v24_10';prior.mkdir(exist_ok=True)
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json','AsBuilt_Section_Segments.json']:shutil.copy2(W/'v24_10'/n,prior/n)
refs=O/'References';refs.mkdir(exist_ok=True)
for src,name in [('D:/Desktop/屏幕截图 2026-10-18 010230.jpg','01_User_Entrance_and_Column.jpg'),('D:/Desktop/屏幕截图 2026-10-18 010519.jpg','02_User_Two_Posts_and_Eave.jpg'),('D:/Desktop/屏幕截图 2026-10-18 011039.jpg','03_User_Oblique_Post_Axis_Plan.jpg'),('D:/Desktop/屏幕截图 2026-10-18 010559.jpg','04_User_Rear_Wall_Continuity.jpg'),('D:/Desktop/屏幕截图 2026-10-18 010754.jpg','05_User_Kitchen_Wall_Continuity.jpg'),('E:/jz/实景三维场景模型.3dm','06_Original_AsBuilt_Model_UNMODIFIED.3dm')]:shutil.copy2(src,refs/name)
for sub in ['v24_10','v24_11']:
 dst=refs/('MP4_Views_'+sub);dst.mkdir(exist_ok=True)
 for p in(W/sub/'Video').iterdir():shutil.copy2(p,dst/p.name)
vref=json.loads((W/'v24_10/Video/Frame_Index.json').read_text(encoding='utf8'));(refs/'Source_MP4.json').write_text(json.dumps({'source':'E:/VID_20260507_152114_00_001.mp4','sha256':vref['source_sha256'],'method':'Perspective v360 views from the original equirectangular MP4; appearance/connection evidence, not a calibrated measurement'},ensure_ascii=False,indent=2),encoding='utf8')
note=f'''# V24.11 储藏房双柱斜廊、连续后墙与照壁修正

打开 Blender/Architecture_Complete_V24_11.blend。完整建筑和场地均保留，单位为米，照片贴图内嵌。1帧关门、20帧半开、40帧开门。默认相机为储藏房外观。V24.10原文件未覆盖。

## 本次修正

- 删除储藏房小入口的铁皮棚面和附属框架。外侧半开储藏区的另一处薄金属棚继续保留。
- 檐廊改为两根竖直木柱及两组柱础。入口柱藏在山墙后，两柱在平面内的连线与围栏斜交，入口端宽于尽端。原来错误的三根前柱、柱础及相应前梁/斜撑从合并木架中移除；补齐斜向承托、节点与前段椽尾。室内后排屋架承托另属房内结构。
- 储藏房入口端瓦檐覆盖次照壁端部，檐口、筒瓦、木承托和房体顶边一起调整。北侧瓦檐随新弧墙收边，厨房谷缝锚点保持。
- 储藏房后墙沿原实景场景模型的地基轮廓转弧。厨房背侧原缺口、错台与断开的墙脚补为连续墙体，并清理转角外露的旧铺地舌片。旧东侧凸砖和砂浆皮在改动区域内统一为连续青砖饰面。排烟圆管、波纹弯管及其固定件保留。
- 转角基础与墙体实体分别闭合，墙根扣除与基础重叠的部分，避免同面叠层产生黑边。条石与毛石分带使用共边的双精度外表面切分，无重复内部盖面。局部多余的微小边简化上限0.05毫米。
- 主照壁内侧改为原生白灰材质，无照片节点。檐下改为实体分层叠涩：横向底面平整、沿长度起翘，端部与墙冠承接；下部增加参考内大门的连续三层石底座。分叉脊、四角翘饰和瓦件保留。

## 依据与保留

依据本轮五张标记图、此前厨房/储藏房资料、E:/jz/实景三维场景模型.3dm 和 E:/VID_20260507_152114_00_001.mp4。References保留原3dm未修改副本、标记图及MP4透视抽帧。模型尺寸与节点为实景模型、视频和照片拟合，不是独立现场测绘或施工结构验算。

此前厨房向院外退让0.450米、内大门最低檐底3.100米、门板和石雕细节、主楼及其他场地构件保留。所有26扇可动门的原动作与1/20/40帧门轴姿态一致。原照片、着色器和动画资产未改写；照壁白墙使用新材质替换原表面分配。

## 核验与预览

最终保存后复开检查 {len(qa['checks'])} 项，失败0项；独立核验 {len(solid['solids'])} 组保存实体均通过。原CAD的共边/UV分离坐标按1纳米至10微米范围归一，非零面积边界必须闭合。入口、檐廊主路径、廊端柱旁、储藏房门口、尽端出口五处采样净空与实际保存的墙、木架、柱础、栏板和开门状态门扇均无相交。采样盒用于模型检查，不是现场通道尺寸或规范判定。

Reports有11张同一最终模型的彩色预览、两柱与后墙平面示意、完整检查数据。V24_11_Veranda_and_Rear_Wall_Plan.png中的红虚线是柱位平面连线，柱身保持竖直。

模型 SHA256：{h}

输入 V24.10 SHA256：{build['source_sha256']}

Source提供构造与核验脚本、几何缓存。重建脚本需要本机V24.10输入及Python/Blender依赖；交付blend本身为完整独立文件。
'''
(O/'README_V24_11.md').write_text(note,encoding='utf8');(R/'V24_11_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_11_Manifest.json','V24_11_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_11_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_11_Two_Posts_Continuous_Walls.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_11/'+r['file'])
 z.write(O/'V24_11_Manifest.json','Rebuild_V24_11/V24_11_Manifest.json')
with zipfile.ZipFile(Z)as z:assert z.testzip()is None
result={'status':'PASS_BUNDLE_CRC_AND_SHA','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_11_Bundle_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False),flush=True)
