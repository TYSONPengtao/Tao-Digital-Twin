# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import json,hashlib,base64,csv,shutil
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');W=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
local=O/'06_Report/Editable_Local_Native_QA.json'
old=json.loads(local.read_text(encoding='utf-8'))
kernel=json.loads((O/'06_Report/Editable_Rhino_Kernel_QA.json').read_text(encoding='utf-8'))
old['raw_pre_kernel_invalid_count']=old.get('raw_pre_kernel_invalid_count',len(old.get('invalid',[])))
old['invalid']=kernel['invalid'];old['final_object_count']=kernel['object_count'];old['unexpected_open_solids']=kernel['unexpected_open_solids']
old['validation_stage']='Final RhinoCommon 8 kernel after native tolerance initialization';old['raw_pre_kernel_errors_resolved']=True
local.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# Rhino V8 使用说明

优先打开 **04_Rhino/Reality_Hybrid_V8.3dm**：以新纯场地实景模型为基底，补入主楼和院落建筑；本次修正飞檐、木构屋面交接、院墙收口、罗马柱拱梁、楼梯及分层布局，并按标注把西侧棚屋区清为地形。原始文件与 V7 留存。

**04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm** 为可编辑实体／块文件，与主文件同 ENU、米、Z 向上。辅助场地和施工建议默认隐藏。它供修改建筑；与主文件同时显示相同建筑会出现重面。主模型的实景融合部分主要是带 UV 网格，不能把它误认为全部可编辑 NURBS。

**08_Editable_Source/06_Rhino/Production_1QK_ARCH.3dm** 为 LOCAL 实体源；05_Intermediate/Architecture_Scene.json 保存每层墙、门、房间连接和铰轴信息。门框与可动门叶分离，13 个平开门铰轴及 2 片推拉门独立保存。历史 DOOR_KITCHEN_F1 ID 为了追踪保留，当前语义是楼梯对面的候选洗手间门，查询连接见 Scene。

**01_Source/Pure_Site_UNMODIFIED.3dm** 是原始纯场地未改副本；WORKING_V8 为局部授权裁切后的工作基底。5 个源网格的原顶点、UV、法线和材质保存，其中 Base_0 的西侧清理边界接触面局部裁切，其余 4 个源网格完整保留。10 张原贴图保留字节并嵌入主文件，外部副本见 03_Textures。新增修复区使用有支持的照片投射或模型材质；遮挡地面的土色部分没有真实地面照片。

**05_Export** 单独位于 E:/jz/JIA/Rebuild_V8_Hybrid/05_Export，提供 LOCAL FBX/GLB/OBJ/MTL、贴图和 Blender 文件。Rhino ZIP 不重复包含这些大体积交换文件。LOCAL 转原 ENU：绕 Z +19.65°，平移 (-3.45191261, -3.90043098, TAO_PRIVATE_SITE_002) 米。UE5 导入需做米到厘米单位转换，确认轴方向和玻璃材质；未执行 UE5 工程实际导入、碰撞或开门蓝图测试。

Rhino 命名视图包括整体场地、飞檐交接、罗马柱拱梁、右墙楼梯及西侧地形。06_Report 含实际几何渲染预览、需求记录、独立核查及待补测清单。原扫描的其他树冠、背面或残片按授权保留规则仍可能存在；本版本未宣称全场布尔焊接为封闭体。

核查证明文件与几何数据的一致性，不能证明现场施工测量精度。楼梯对面洗手间门的准确偏距及房界、门净尺寸、楼梯尺寸、砖瓦轮廓等仍需量尺确认。几何运算公差与图纸／照片估计尺寸不能替代现场实测。详见 06_Report/需求汇总与修模依据_V8.md。
'''
(O/'使用说明.md').write_text(readme,encoding='utf-8')
rows=[
 ('V8-01','最高','楼梯对面洗手间门','量门净宽净高、门框到两侧墙角距离、墙厚、门槛高；记录合页侧、开启方向、房间内部尺寸','远景定位照＋量尺近照＋开关门视频＋站位全景','L1_WC_OPPOSITE_STAIR','候选门轴 X9.1/Y8.6 需要实测'),
 ('V8-02','最高','两层楼梯与平台','逐跑记录踏步数量、踏步宽高、跑宽、平台长宽、进出口净宽、上方最低净高','尺量记录＋每跑上下端手机照＋连续上楼全景视频','L1_L2_STAIR_RIGHT','首跑靠右墙；入口无门；模型净高只是几何值'),
 ('V8-03','高','罗马柱与拱梁接头','量楼板下皮高、柱顶和柱头高、柱径；正面和侧面拍清拱梁端部接柱关系','接头近照＋整跨正照＋量尺入镜照','PORCH_COLUMN_ARCH','确认柱到楼板、拱梁抵柱侧'),
 ('V8-04','高','厨房与门楼屋檐交接','量两檐最低净距、滴水外沿、檐口高、木柱梁截面；拍完整交接侧面','安全地面手机照片＋尺寸记录；全景只作定位','KITCHEN_GATE_EAVES','扫描拟合净距约0.693m，需实测'),
 ('V8-05','高','照壁两端飞檐','量安全可达处墙宽、墙厚、檐口低点高；拍两端侧面、正立面、瓦当与花纹近照','手机正侧照＋全景＋可达尺寸记录','SCREENWALL_EAVES','飞檐高度和瓦轮廓为扫描／照片拟合'),
 ('V8-06','高','院墙与主体收口','量墙端到主体柱、窗框距离，墙厚及压顶高；拍内外两侧','两侧近照＋远景定位＋量尺入镜','COURTYARD_WALL_END','主体实体柱接头需核对'),
 ('V8-07','中','西侧清理后地面','拍原棚屋遮挡区真实地面、台阶沟坎；量相邻地面的相对高差和坡向','连续重叠手机照＋全景＋相对高差记录','WEST_GROUND_ONLY','约159㎡目前为插值地形／暂定土色'),
 ('V8-08','高','每层房间差异','按层逐间记录门窗与墙角偏距、房间长宽及每个转折；二层右侧逐间核对镜像','每间全景＋手机门窗定位照＋平面手绘尺寸','ROOM_BY_FLOOR','一层右卫生间遵图；二层镜像按用户指示；其余需实测')]
with (O/'06_Report/V8_优先补测上传清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['任务ID','优先级','位置','用手机与量尺采集','上传文件','命名前缀','当前模型依据与状态','完成状态']);w.writerows([list(x)+['待采集'] for x in rows])
task='''# V8 补测与上传

继续使用原来的手机、量尺、全景相机任务包，不需要新增设备。优先任务见 V8_优先补测上传清单.csv。每处放入一个含任务 ID 的文件夹，带远照定位、量尺入镜近照、尺寸文字记录和全景原片；门另加开关视频。尺寸写毫米并标明量的是净尺寸还是外框尺寸，门偏距注明从哪一个墙角量起；全景用于判断布局和连通，厘米尺寸以量尺记录为准。

逐层上传，不用等全场拍完。文件名示例：V8-01_L1_WC_OPPOSITE_STAIR_门框至北墙_20261009.jpg。保留原片、原视频和全景相机原始文件，另可附拼接预览；不要只交截图或压缩聊天图片。

原完整任务包：C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/outputs/手机量尺全景_任务上传清单_20261008。
'''
(O/'06_Report/V8_补测上传说明.md').write_text(task,encoding='utf-8')
print('Final editable report and V8 use/upload instructions written',flush=True)
