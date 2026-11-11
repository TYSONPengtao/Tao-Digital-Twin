import sys,json,math,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');B=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);co=math.cos(a);si=math.sin(a)
def enu(q):return [q[0]*co-q[1]*si+C['origin'][0],q[0]*si+q[1]*co+C['origin'][1],q[2]+C['origin'][2]]
cams=[('V10_Courtyard_Corner',[4,-15,6],[.2,-10.7,2.25]),('V10_Wall_Detail',[4,-5.8,3.7],[0,-6,2.1]),('V10_Perimeter_Detail',[-27,1,7],[-23,1,2.6])]
for filename in ['Reality_Hybrid_V10.3dm','Architecture_Edit_V10_ALIGNED_ENU.3dm','Courtyard_Walls_V10_ALIGNED_ENU.3dm']:
 p=O/'04_Rhino'/filename;F=rh.File3dm.Read(str(p))
 for name,pos,tar in cams:
  vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=enu(pos);tar=enu(tar);vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.065,.065,.1,10000);vp.SetScreenPort((0,1600,1040,0,0,1));F.NamedViews.Add(vi)
 vi=rh.ViewInfo();vi.Name='V10_Wall_Review';vp=vi.Viewport;pos=enu(cams[1][1]);tar=enu(cams[1][2]);vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.065,.065,.1,10000);vp.SetScreenPort((0,1600,1040,0,0,1));F.Views.Add(vi)
 F.Strings['V10_Wall_Reference']='../07_Evidence/User_Chinese_Courtyard_Wall_Detail.png';F.Strings['V10_Dimensions']='Wall centerline, existing opening and retaining core inherited from V9; decoration and tile modules based on supplied reference diagram and DJI_0161. Not measured construction shop drawings.'
 F.Strings['Source_Scene']='../08_Editable_Source/05_Intermediate/Architecture_Scene.json';assert F.Write(str(p),8)
q=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');q['sha256']=sha(O/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm');q['walls_only_sha256']=sha(O/'04_Rhino/Courtyard_Walls_V10_ALIGNED_ENU.3dm');(O/'06_Report/Editable_Rhino_Alignment_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
history=O/'07_Evidence/V9_Previous_Repairs';history.mkdir(exist_ok=True)
for n in ['需求汇总与修模依据_V9.md','Final_V9_Reference_QA.json','Final_V9_Reference_QA.md','Independent_V9_QA.json']:shutil.copy2(B/'06_Report'/n,history/n)
M=read(O/'02_Data/Materials.json')
for m in M.values():
 if m.get('texture'):shutil.copy2(m['texture'],O/'05_Export'/Path(m['texture']).name)
for b in read(O/'02_Data/Base_Index.json'):shutil.copy2(b['texture'],O/'05_Export'/Path(b['texture']).name)
(O/'使用说明.md').write_text('''# V10 院墙围墙 Rhino 模型

本轮按用户提供的中式围墙大样图和 DJI_0161 等现场照片深化院墙。请打开 `04_Rhino/Courtyard_Walls_V10_ALIGNED_ENU.3dm` 查看完整院墙单独模型；`04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm` 是完整建筑及场地构件的可编辑实体版本。

`04_Rhino/Reality_Hybrid_V10.3dm` 是实景融合版本，保留实景源模型，只在原缺失／接缝修补范围内替换本轮院墙构件。完整院墙实体在前述两个文件内。两套版本切换查看；同位叠加会有重复面。

三份文件单位均为米，使用原项目 ENU 坐标、Z 向上。命名视图 `V10_Wall_Detail`、`V10_Courtyard_Corner` 和 `V10_Perimeter_Detail` 用于检查。院墙构件按墙段分组，砖、瓦、瓦当、线脚、花砖可独立选取编辑。墙身与砖饰采用原生 Brep／挤出实体；密集陶瓦及花砖采用双精度封闭网格实体，保留完整几何，避免逐三角面转为 Brep 导致文件过大。新冠顶参考造型有明确的暂定状态，可按后续实测调整。

本轮保留现有墙线、实际门洞、石砌挡土基座、主楼连接、木大门、照壁与厨房飞檐关系。参考图 2700 mm 总高、3500 mm 铁门等没有覆盖现场尺寸，也没有重新增建此前已删除的西院棚屋或铁门。

墙体及饰件截面未全面实测，模型检查不构成施工尺寸认证。原室内布局、楼梯与门位的已确认修正保留，尚未实测的部分沿用原不确定性。UE5 的实际导入、碰撞、漫游和开门交互仍需另行测试。

贴图在主模型内嵌并附外部原图，实景源和 V9 快照在 `01_Source`。本轮依据与检查报告位于 `06_Report` 和 `07_Evidence`。LOCAL FBX/GLB/OBJ/Blender 交换文件在本目录 `05_Export`。
''',encoding='utf-8')
(O/'06_Report/院墙深化依据与版本说明_V10.md').write_text('''# V10 院墙深化依据与版本说明

用户新图用于青砖勒脚、白墙框脚、双坡瓦帽、滴水瓦当、镂空花砖和灰色压顶的造型深化。图中材料强度、基础和隐蔽节点没有现场证据，未据此生成声称已核实的施工构造。

| 项目 | 本轮处理 |
|---|---|
| 外周挡土墙 | 保留两组中心线与石砌／抹灰墙身，共约121.885米；墙顶随原地形起伏 |
| 内院西瓦墙 | 保留 `[0,1.9] → [0,-10.7] → [4.9,-11.7]`，上端继续接建筑实柱 |
| 木门楼东侧墙 | 保留 X8.3～13.3/Y-11.7 原墙芯；新增冠顶在厨房砌体相接处收头 |
| 砖瓦及线脚 | 单独实体单元；花砖有真实贯穿孔洞；转角沿现有角平分线裁切 |
| 开口 | 西南周界断口中心线跨度约5.169米、内木门净宽2.60米均保留，无新增示意铁门 |
| 参考图尺寸 | 2700/450/300/1500/3500等为参考；保留原250/320毫米墙厚及现场墙顶 |

DJI_0161 支持内院真镂空花脊、筒瓦与长短框交替，DJI_0073 支持外周较低瓦帽、白色内面和石砌外基。外周新增花冠单独标为参考造型暂定，不混同为实测原状。具体高度变化、构件数量与几何核查见各补丁 Geometry_QA 和独立 Final_V10_Wall_QA。

V9 已修正的厨房低檐伸入门楼高檐、门楼装饰层、照壁上翘、罗马柱顶楼板与拱梁侧接、楼梯右侧上行、楼层门位与布局、西院只留地形等要求继续保留。V9 原需求与检查记录在 `../07_Evidence/V9_Previous_Repairs`；本轮只改围墙院墙构件。

实景主模型采用增量替换：旧实景与贴图保持，新增细节仍受既有修补范围裁切。完整实体可编辑建筑和单独围墙文件用于查看全部细节，不能用主模型裁切边界判断实体缺失。预览中的局部院墙图显示完整可编辑院墙；整场地图显示实景融合。

需要补测：院墙各转角和端点位置／高程、砖基高度、檐口挑出、瓦距、花砖净孔与顶高、厨房侧收头尺寸。可用手机正侧照片附量尺，或全景相机连续走线，沿用既有采集上传清单。
''',encoding='utf-8')
print('Named views, cumulative evidence, original texture companions and V10 guide written',flush=True)
