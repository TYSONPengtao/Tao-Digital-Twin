import sys,json,math,shutil,hashlib,gc
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);co=math.cos(a);si=math.sin(a)
def enu(q):return [q[0]*co-q[1]*si+C['origin'][0],q[0]*si+q[1]*co+C['origin'][1],q[2]+C['origin'][2]]
cams=[('V11_Right_Angle',[7,-17,8],[.2,-11.5,1.9]),('V11_Pavilion',[6,-10,4.3],[2.5,-5.35,1.1]),('V11_Outer_Gate',[-23,-17,6],[-14,-10.5,1.3]),('V11_Kitchen_Interface',[23,-7,5.5],[13.7,-5.5,.3])]
for filename in ['Reality_Hybrid_V11.3dm','Architecture_Edit_V11_ALIGNED_ENU.3dm','Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm']:
 p=O/'04_Rhino'/filename;F=rh.File3dm.Read(str(p))
 F.Strings['Usage']=('V11 original-photo reality hybrid with local corrected structure patches' if filename=='Reality_Hybrid_V11.3dm' else 'V11 full editable architecture' if filename=='Architecture_Edit_V11_ALIGNED_ENU.3dm' else 'V11 independent surrounding site structures, courtyard/perimeter walls, pavilion, kitchen and gates')+'; original ENU metres Z-up; source and reference provenance in companion data.'
 for name,pos,tar in cams:
  vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=enu(pos);tar=enu(tar);vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.065,.065,.1,10000);vp.SetScreenPort((0,1600,1040,0,0,1));F.NamedViews.Add(vi)
 F.Strings['Source_Scene']='../08_Editable_Source/05_Intermediate/Architecture_Scene.json';F.Strings['V11_Evidence']='../07_Evidence: original DNGs, decoded inspections, actual outer-gate panorama and user shape diagrams';F.Strings['V11_Scope']='User-specified right-angle courtyard wall, internal modern Chinese timber pavilion, continuous DNG/OBJ-supported kitchen outside wall/stone base and completed outer gate/west wall. Source scans and photos unchanged.';F.Strings['V11_Dimensions']='Reference fitted dimensions, no independent field certification; four outer gate leaves have hinge metadata and Blender fold hierarchy, actual operating sweep needs on-site/UE5 verification.'
 assert F.Write(str(p),8);del F;gc.collect();print('Final native views',filename,flush=True)
q=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');q['sha256']=sha(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm');q['site_only_sha256']=sha(O/'04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm');save(O/'06_Report/Editable_Rhino_Alignment_QA.json',q)
for m in read(O/'02_Data/Materials.json').values():
 if m.get('texture'):shutil.copy2(m['texture'],O/'05_Export'/Path(m['texture']).name)
for b in read(O/'02_Data/Base_Index.json'):shutil.copy2(b['texture'],O/'05_Export'/Path(b['texture']).name)
(O/'使用说明.md').write_text('''# V11 直角院墙、木亭、厨房外壁与外围门墙

主要打开 `04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm`：完整可编辑建筑，含本轮院墙、木亭和外围门墙，以及既有楼层/门位/楼梯/罗马柱/飞檐修正。

`04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm` 是独立建筑周边构件文件，便于检查完整院墙、亭子、厨房、门楼和外围墙。

`04_Rhino/Reality_Hybrid_V11.3dm` 是实景融合主文件，增量替换本轮修正构件，补齐用户标定的缺失外墙和门。五个实景网格、原始照片像素/UV及完整实景区域保持不变。原实景、可编辑构件会同位重叠，应切换版本查看，不同时叠加整套模型。

三份模型使用原 ENU 坐标，米为单位、Z 向上。命名视图 `V11_Right_Angle`、`V11_Pavilion`、`V11_Outer_Gate`、`V11_Kitchen_Interface` 用于检查。

本轮处理：亭旁院墙斜折改90°并重做墙芯、框脚、瓦帽、花砖与压顶拼角；木亭全部缩入院墙内，按用户四坡新中式图建908个分件，包括440片沥青瓦、木梁柱、椽子、内衬、防水面、金属天沟、竹帘、栏杆、石台与柱脚；西南外门按全景897秒真实四分格金属门造型建四独立扇和青砖门柱；西侧外围墙实体保持原线，补齐融合版裁切造成的缺段；厨房外侧按两张DNG和注册OBJ剖面修正灰砖/石基/东檐连接，取消模型虚构的双墙夹缝。

砖、瓦、木构及门叶分件可编辑。墙和梁柱主要为原生Brep/挤出实体，密集复杂瓦、花砖等采用双精度闭合网格，未降低原几何精度。四扇外门在Rhino融合版是独立铰轴块，在可编辑建筑版是独立门组且各件附`Hinge_ENU_m`；Blender/FBX/GLB含四轴与暂定折门父子层级。登记在 `02_Data/Interaction_Registry_V11.json`，室内原登记/布局不改。

照片支持几何关系，图示构件尺寸按当前场地适配，未全面实测。厨房端部局部过渡、木亭截面、外门尺寸与真实折叠开启范围仍需量尺核实。没有将参考图中基础/材料强度等标成已核实施工数据；UE5实际导入、碰撞、漫游及联动开门仍待测试。

参考照片、DNG原件/解码图和用户示意图位于`07_Evidence`，检查结果及预览在`06_Report`，原实景和V10快照在`01_Source`。原贴图已内嵌并附外部同字节照片。LOCAL FBX/GLB/OBJ/Blender在`05_Export`，使用`02_Data/Coordinate.json`转换原ENU。
''',encoding='utf8')
print('V11 guides, views and texture companions complete',flush=True)
