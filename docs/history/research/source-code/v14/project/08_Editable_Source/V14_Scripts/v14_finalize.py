import sys,json,math,hashlib,shutil,struct
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V14');P=O/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for table in [F.NamedViews,F.Views]:
 for v in table:
  for old in ['V12_','V13_']:
   if v.Name.startswith(old):v.Name=v.Name.replace(old,'V14_',1)
for name,pos,tar in [('V14_Roof_Junction',[26,-28,17],[13,-10.5,2.8]),('V14_Valley_Detail',[18,-18,9],[12.4,-10.8,3.6]),('V14_Outer_Storage',[25,-20,5.2],[19,-13,1]),('V14_F3_Hall',[7.65,6.82,9],[3.1,6.8,8.15])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
F.Strings['V14_Status']='Original pure-site exterior with original UV; L roof valley cut; metal lean-to under tile eave; roof/wall overlap cleared; F3 exit through supported hall and finish opening. Geometric contact reviewed, no strength calculation.'
F.Strings['V14_Roof_References']='DJI_0525.JPG; DJI_0526.JPG; registered original OBJ; MP4 frame index'
F.Strings['V14_Editable_Scene_SHA256']=hashlib.sha256((O/'08_Editable_Source/Architecture_Scene_V14.json').read_bytes()).hexdigest();assert F.Write(str(P),8);sha=hashlib.sha256(P.read_bytes()).hexdigest()
Q=json.loads((O/'06_Report/V14_Native_Readback_QA.json').read_text(encoding='utf8'));Q['sha256']=sha;Q['final_metadata']='Named review views and scene/reference strings updated after mesh readback; geometric objects unchanged';(O/'06_Report/V14_Native_Readback_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
A=json.loads((O/'06_Report/V14_Assembly_QA.json').read_text(encoding='utf8'));A['status']='PASS_NATIVE_READBACK_AND_VISIBLE_CONTACT_REVIEW';A['final_model_sha256']=sha;(O/'06_Report/V14_Assembly_QA.json').write_text(json.dumps(A,ensure_ascii=False,indent=2),encoding='utf8')
for n in ['Contact_QA.json','Roof_Junction_QA.json','Review_Fix_QA.json','Merge_Route_QA.json','Opening_QA.json']:shutil.copy2(W/'v14'/n,O/'06_Report'/n)
for n in ['DJI_0525.JPG','DJI_0526.JPG']:shutil.copy2(Path(r'D:/DJI/0002/DCIM/101MEDIA')/n,O/'07_Reference'/n)
shutil.copy2(Path(r'E:/jz/纯场地版本.3dm'),O/'07_Reference/Pure_Site_Source.3dm')
scripts=O/'08_Editable_Source/V14_Scripts';scripts.mkdir(exist_ok=True)
for n in ['v14_extract.py','v14_terrain.py','v14_building.py','v14_roof_junction.py','v14_review_fixes.py','v14_relief_repair.py','v14_f3_column_clearance.py','v14_finish_opening.py','v14_opening_qa.py','v14_assemble.py','v14_readback.py','v14_contact_audit.py','v14_merge_route_audit.py','v14_render_native.py','v14_roof_survey.py','v14_finalize.py']:shutil.copy2(W/n,scripts/n)
shutil.copy2(W/'v14/Building_Mutation.json',O/'08_Editable_Source/Building_Mutation_V14.json');shutil.copy2(W/'v14/Terrain_Mutation.json',O/'08_Editable_Source/Terrain_Mutation_V14.json');shutil.copy2(W/'v14/data/Registered_Actual_Roof.npz',O/'07_Reference/Registered_Actual_Roof_LOCAL.npz');shutil.copy2(W/'v14/Roof_Source_Materials.json',O/'07_Reference/Roof_Source_Materials.json')
readme='''V14 模型修订说明（2026-10-12）

打开 04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm。模型单位为米，使用原始 ENU 测量坐标。05_Export 中 GLB 和 Blender 文件使用 LOCAL 米坐标，转换关系见 02_Data/Coordinate.json。

本版完成的修订：
1. 外围采用用户指定的“纯场地版本.3dm”五个原始贴图网格。保留坐标、原 UV、原贴图字节；清除基地内重建区域和入口坡道范围的源网格，内部空缺继续使用建模补齐。旧的外围土黄色合成地形已移除。原始文件未改写，副本与 SHA256 留作核对。
2. 对照 DJI_0525、DJI_0526 和已配准航测屋面，调整厨房主体与内储藏房的横向屋脊、两侧坡面和斜向汇水交线。裁去交线内重复的主屋瓦面/瓦行，补充内储藏房筒瓦、屋脊、卷曲脊端、木构及交角下支承。
3. 内储藏房连接厨房主体；另一侧通过开放门洞接外储藏区。外储藏区采用外凸折线平面、金属低棚顶、钢柱梁和半开石栏板，棚顶伸入瓦檐下。取消无实景依据的内储藏房外侧新门。保留地坪高差和可见石基。
4. 清除误穿储藏房山墙的旧围墙瓦帽、花砖压顶和线脚，仅在建筑占用范围裁切上部墙饰，保留下部挡土基础和其余围墙。
5. 三楼出口移至楼板支承的侧廊；关闭原楼梯井旁开口、调整相邻房门与隔墙、补充临楼梯井栏杆。原楼梯及楼板开口不变。门洞同时裁切墙芯和瓷砖面层，避免面层封住入口。
6. 延续 V13 的原生挤出体内轮廓修复和阳台雨棚连接，保留本版修改范围之外的原生几何及门窗块定义。

视频依据：对 E:/VID_20260507_152114_00_001.mp4 的 64.397734 秒全景视频每 2 秒抽帧，共 33 帧。07_Reference/MP4 有帧图、联系表及带时间和源文件校验值的 Frame_Index.json。18–30 秒可见传统木构内室；34–52 秒可见通向半开外储藏区的开口、金属棚顶与栏板；54 秒可见返回内室关系。

校核与预览：
06_Report/V14_Native_Readback_QA.json 记录新 3DM 实际回读、有效性、几何保留哈希、原 UV 和新旧顶点一致性。变化后的 Mesh 和 Extrusion.Profile3d 直接读取原生文件；未修改部分在几何哈希相等后复用 V13 原生内核网格，移动门块在定义相等后应用本版实际变换。本次 RhinoCommon 内核未能启动；未将场景 JSON 渲染冒充新的内核验证。
Contact_QA.json 是新增储藏房构件的几何接触检查，857 个筒瓦与底层接触。Merge_Route_QA.json 记录范围裁切、入口坡道和三楼地坪关系，挡土墙的上缘和低侧地面具有真实高差，不能当作同一条路面的接缝误差。门洞另以实际回读网格射线核查。
V14_Native_*.png 为原生回读几何检视。三楼侧廊的两张图临时隐藏两片关闭门扇并使用检视灯，以看清门洞和连续地坪；3DM/GLB 仍保留关闭门扇、合页信息。其余图保留全部索引几何。详见 Preview_View_States.json。

尺寸与隐藏节点为照片及配准网格拟合，未进行现场复测、构件承载力计算或 UE5 导入验收。这里的接触校核说明几何连接，不等同于结构设计验算。原始外围文件自身的树木、邻房和纹理缺失边界保持原样。
08_Editable_Source 包含当前场景与改动数据。V14_Scripts 是本机处理脚本，依赖本机已有的 V13 基础数据和 Python 库；不是脱离基础项目即可独立重建的安装包。
'''
(O/'README_V14_请先阅读.txt').write_text(readme,encoding='utf-8-sig');print('FINALIZED',sha,flush=True)
