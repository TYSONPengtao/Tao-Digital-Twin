# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import json,shutil,csv,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');W=Path(__file__).parent;V6=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid')
selected={2:[38,41,429,478,508,509,623,282,153,158,410,96],3:[100,103,106,109]}
for folder,ids in selected.items():
 for n in ids:
  src=Path(fr'D:\DJI\{folder:04}\DCIM\101MEDIA\DJI_{n:04}.JPG');dst=O/'07_Evidence/Selected'/f'DJI_{folder:04}_{n:04}.JPG';shutil.copy2(src,dst)
user=O/'07_Evidence/User_Annotations';user.mkdir(parents=True,exist_ok=True)
for name in ['屏幕截图 2026-10-08 211428.jpg','屏幕截图 2026-10-08 212249.jpg','屏幕截图 2026-10-08 212307.jpg']:shutil.copy2(Path(r'D:\Desktop')/name,user/name)
video=O/'07_Evidence/Video';video.mkdir(parents=True,exist_ok=True)
for name in ['Wide_L0_0205s_Y+00.jpg','Wide_L1_0205s_Y+00.jpg']:shutil.copy2(Path(r'E:\jz\JIA\Rebuild_V5\12_Video_Layout_Evidence')/name,video/name)
for name in ['Center_L0_0165s.jpg','Center_L1_0165s.jpg','Center_L0_0200s.jpg','Center_L1_0200s.jpg']:shutil.copy2(W/'ue5_panorama_audit'/name,video/name)
shutil.copy2(V6/'06_Report/需求汇总与修模依据.md',O/'06_Report/前期需求汇总_V6留档.md')
for name in ['All_Reality_Model_Files.csv','New_Rhino_Summary.json','Pure_Baseline_Hashes.json']:
 src=W/'v6_reality_inventory'/name
 if src.exists():shutil.copy2(src,O/'07_Evidence'/name)
# OBJ exporter needs actual external copies beside its relative map_Kd paths.
for folder in ['Base','Patch']:
 for src in (O/'03_Textures'/folder).iterdir():
  if src.is_file():shutil.copy2(src,O/'05_Export'/src.name)
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
text='''# V7 需求汇总、依据与修模记录

以 Rhino 为主交付建筑及周边场地，沿用新纯场地实景模型作基底。在主建筑和院落空洞内修补，原五个完整实景网格、原坐标、UV、材质和原图比特保留。V6 与全部原始 OBJ／3dm／CCM／无人机／视频文件未覆盖。

## 本次标注的执行结果

| 用户要求 | V7 处理 | 证据 |
|---|---|---|
| 红线三角面应封闭 | 前山墙改为单个封闭实体，底接拱梁顶、顶随两坡屋面底，中央补盖脊盖 | 211428 标注、0002/0429、0003/0100 |
| 二层楼梯前墙封闭 | Y7.3 的中央楼梯前墙封闭，保留右侧平台绕行通道 | 用户明确指示；分层墙体独立处理 |
| 三层打叉墙去掉 | 拆掉西侧 Y7.3 横向误墙，前雨棚与后部窗前区域连通；原混凝土柱梁保留 | 212249 标注、全景 165/200/205 秒 |
| 出阳台门改到垂直墙 | 原 DOOR_LAUNDRY_F3 稳定 ID 留存用于追踪；门框、门扇整体旋转到 X3.9 侧墙，连接楼梯平台与西侧阳台 | 标注、全景 165/200/205 秒、0002/0623 |
| 阳台有分隔 | 补齐西侧阳台与中心房间的侧墙分隔；后部平台侧开门。窗前帷幕按软隔断证据识别，没有恢复成实体横墙 | 0002/0623、全景 200 秒 |
| 正面窗门准确区别 | 三层中央保持窗下墙，上部三格上亮、两个窄开启扇及大固定玻璃；二层阳台出口独立为固定边玻璃与两片推拉门 | 0002/0038、0429、0478 |
| 一砖一瓦一墙细化 | 瓦列改成独立弧形薄壳盖瓦；灰砖附房独立砖面及错缝；阳台陶砖面、镂空菱形栏带、石栏分格及雨棚檩条分别建模 | 0002/0038、0429、0478、0508、0623 |
| 实景材质、贴图融合 | 屋面、地面和场地保留或投射原实景照片；封闭山墙直接使用原 DJI 0429 照片 UV。白灰墙、柱梁和浅色石栏采用照片支持的统一饰面，清除不正确的红门／阴影投射花块 | 10 张未改像素原图嵌入；原场地材质不变 |

## 本次完整目录参考

0002/101MEDIA 的 633 张 JPG 与 0003/101MEDIA 的 120 张 JPG，共 753 个照片帧全部编入 13 页联系表并查看目录全景。另索引 751 个 DNG 配对原片；同一帧的 JPG 用于可视核对，未将 DNG 配对重复算作额外机位。照片原路径、时间、尺寸、RAW 配对及页码见 All_Target_Captures.csv/json。选取 16 张原分辨率图片核对结构、开口、木构和砖瓦。

前期已经索引 E:/jz 新旧 OBJ、3dm、D:/AJAVIS01/ContextCapture/CASES 及 DJI 其余集合，详见随包前期汇总及源模型索引；本次没有重新声称其余集合逐张精审。室内门墙以全景实际连通关系及本次明确标注修正，每层保持自己的记录。

## 构件分类

中式厨房：木柱、梁、格栅与门窗单独归为木构，不用砖墙替代。照壁：独立墙身、装饰分格及瓦顶。瓦墙／围墙：墙身、压顶和屋面瓦分开。东南附房为可见灰砖砌体，下部不规则石砌挡墙维持其独立类别。主楼白灰或陶砖饰面不虚构可见裸砖，也不推测墙内隐蔽构造。

## 精度与交付边界

输出单位为米，Rhino 模型绝对公差 0.001 米。该数值是几何运算公差，不能作为实测精度承诺。门洞偏距、净尺寸、墙厚、瓦片轮廓、灰缝宽度和部分栏杆尺寸仍为设计比例或照片估计；需手机照片、量尺记录和全景补测锁定。本次独立砖瓦数量是所建模块数，不是现场逐件清点数量。

原场地裁口与补面距离检查和原数据不变检查分别记录；补模型并未宣称成为一个布尔焊接的全场闭合体。原扫描范围外及完整场地网格本身的树冠／背面空洞按“空洞外不变”保留。

门框与可动门扇分开，13 个平开门扇保留真实几何铰轴原点，新增两片推拉门为独立块。房间、门 ID 与连接表随包提供。已导出 LOCAL FBX/GLB/OBJ；未声称已经完成 UE5 工程导入、碰撞、开门蓝图或房间信息界面。

## 后续用现有设备补测

优先拍摄并量取三层西侧新出口的净宽、净高、门框到后墙角偏距、门槛高及开启侧；二层楼梯前封墙的左右端、厚度和平台通道净宽；阳台侧墙长度和与立柱接头。每处上传一张量尺入镜近照、一张能定位到窗／楼梯／柱的远照、一段开关门视频、一张全景；文件名含楼层、房间 ID、门 ID。避免从全景鱼眼畸变读厘米尺寸。
'''
(O/'06_Report/需求汇总与修模依据_V7.md').write_text(text,encoding='utf-8')
readme='''# Rhino V7 使用说明

优先打开 **04_Rhino/Reality_Hybrid_V7.3dm**。这是原实景场地与空洞内修补的主交付，保留 5 个原实景网格、UV 和材质；墙门按本次标注修正，照片嵌入文件。

**04_Rhino/Architecture_Edit_V7_ALIGNED_ENU.3dm** 为可编辑实体／块模型，与主文件同 ENU、米、Z 向上。其前期辅助场地和施工建议默认隐藏。用该文件编辑实体时，避免同时叠显主文件里同一建筑补块造成重复面。

**08_Editable_Source** 保存本次 LOCAL 参数场景与实体源文件。主文件的补块按场地空洞掩膜裁切；实体源模型保持完整部件，便于后续调整。

**05_Export** 提供 LOCAL FBX／GLB／OBJ。LOCAL 到 ENU：绕 Z +19.65°，平移 (-3.45191261, -3.90043098, TAO_PRIVATE_SITE_002) 米。UE5 使用 LOCAL 文件，按米到厘米换算；不要再把两个坐标版本当作同一原点重叠导入。UE5 工程导入和交互搭建未在本包执行。

**06_Report** 包含修改依据、几何核查、源数据不变核查、边界检查和预览。**07_Evidence** 包含两个指定照片目录全部 JPG 联系表／索引、16 张精选原图、用户标注和全景片段。DNG 对应原片路径已索引，未修改。

本次新增可见独立盖瓦、灰砖面、陶砖面及栏带构件，轮廓和尺寸未全部经过量尺实测。原图像素保留、门墙拓扑修正及运算公差均不等同于施工测量精度。待补测项见需求说明最后一节。
'''
(O/'使用说明.md').write_text(readme,encoding='utf-8')
with (O/'06_Report/本次关键补测上传清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['优先级','楼层部位','编号','用量尺记录','手机照片','全景及视频','上传状态'])
 for row in [('P0','三层西侧阳台出口','DOOR_LAUNDRY_F3','净宽净高、门框到后墙角偏距、门槛高','门内外各一远照；三张量尺入镜近照','开关门20秒；平台与阳台各一全景'),('P0','二层楼梯前封墙','F2-STAIR-WALL','厚度、墙两端到柱偏距、侧平台通道净宽','正面全景远照；墙两端与楼梯交接近照','平台转一圈及走到厅内'),('P1','三层阳台侧墙分隔','F3-TERRACE-SEPARATOR','墙长墙厚及窗角/柱接头尺寸','雨棚、墙、窗及门同框；各接头近照','阳台前后各一全景'),('P1','二层阳台推拉出口','DOOR_FRONT_CENTER_F2','门洞总宽高、固定与可动扇宽、轨道数','正面含全部门框；把手轨道近照','各门扇开关过程'),('P1','屋檐前山墙与瓦件','CANOPY-GABLE-TILES','可安全量取的瓦宽瓦长和檐口厚度','地面长焦正面与侧面；勿冒险登高','地面全景定位')]:wr.writerow([*row,'待上传'])
print('V7 evidence and reports written',flush=True)
