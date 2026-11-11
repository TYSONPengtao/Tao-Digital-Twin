from pathlib import Path
import json,shutil,csv,hashlib
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V5');S=json.loads((O/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
report='''# V5：按全景视频修正室内门位与逐层布局

本版在 V4 上局部修改室内，不覆盖 V4。图纸提供暂定的米制尺寸；全景视频提供房间用途、前后方向、门的连通关系与材质证据。视频拍摄于 2026-05-07，未经过相机标定，不能据此输出毫米级实测坐标。

## 本轮已经改入模型

1. 一、二层四樘卧室门从靠楼梯的后端移至靠入口／阳台的前端；旧洞补齐，新门洞同步扣墙。模型 Y=2.4m 是可继续调整的暂定偏距。
2. 三层右翼卧室红木门移到楼梯平台侧，暂定 X=9.1m、Y=7.55m；后段平台隔墙补建并留独立门洞。中心浅木门通向睡眠房，保留两个房间的独立连接。
3. 三层中心房的用途从“设计书房”改为视频中的睡眠房。关闭与平台实墙不符的 3.6m 设计室内窗，原设计对象存入 retired_design_elements。
4. 三个楼层分别移除右翼卧室与后凹段间错误封堵的墙段，保留湿区前墙和侧墙。一层右侧湿区门从横墙改为侧墙入口；具体偏距尚未量尺核实。
5. 五樘视频可见的湿区门改为红框磨砂玻璃。楼梯旁原图“厨房”改为洗手间用途，旧构件 ID 保留作追溯。
6. 13 樘室内平开门均分离固定门框和门扇。门扇使用独立块，实际几何原点位于铰轴；框扇保留共同 door_id。19 个逐层房间／核对区域提供房间信息及连通记录。

## 文件选择

- 06_Rhino/Production_1QK_Rebuild.3dm：可编辑建筑、场地原生模型；默认显示全场地。
- 07_SketchUp/Production_1QK_Rebuild.skp：可编辑模型；各室内门 FRAME 与 LEAF 独立组件。
- 08_Export/Production_1QK_ARCH.fbx、.glb：保留语义组、材质、门扇铰轴与自定义信息；闭门状态。OBJ 保留几何与材质，但不承载门扇原点和交互层级。
- *_VIS 文件增加建筑／场地装饰细节。
- 05_Intermediate/Architecture_Scene.json：完整可追溯的中间模型、逐层房间与门注册数据。
- 09_Report/V5_F*_Before_After_Plan.png：每层前后门位和隔墙对照。
- 09_Report/V5_F*_Interior_Cutaway.png：仅用于看布局的剖切预览，原生模型没有被剖切。
- 12_Video_Layout_Evidence：56 张新增透视、时间索引、4 张联系表、独立逐层视频分析。

## 仍需现场确认的部分

门偏距、实际净宽净高、墙厚、铰链端和最大开角仍是暂定参数；图纸门洞宽与扣除门框后的模型净宽在 Door_Registry_V5 中分别列出。三层右湿区、西后部洗衣间、中心房外窗关系和正面玻璃门的开启机构尚未充分确认。房间 review_polygon 仅为信息核对区，不可当作实测面积；一层洗手间与楼梯的投影关系另有备注。

V4 的 CONSTRUCTION_*、楼梯／栏杆及排水构造仍保留为施工协调建议，不代表现场已经这样建造。施工或正式竣工成果还需量尺核对并完成相应设计审查。本轮只修改室内隔墙、主体室内门与一樘室内设计窗，已核对的室外场地、围墙、照壁、中式木构、外立面及罗马柱继续使用原模型。

本版文件是在本机生成；尚未导入用户的 UE5 项目，也未创建运行中的开门蓝图或房间查询系统。
'''
(O/'V5_使用说明.md').write_text(report,encoding='utf-8')
(O/'09_Report/V5_房间与门位核对说明.md').write_text(report,encoding='utf-8')
for p in (W/'v5_model_audit').glob('V5_*'):
 if p.suffix.lower() in ['.json','.csv','.md','.png','.jpg']:shutil.copy2(p,O/'09_Report'/p.name)
scripts=O/'05_Intermediate/Scripts';scripts.mkdir(exist_ok=True)
for n in ['build_scene_v5','prepare_v5','preview_v5_interiors','write_v5_report']:shutil.copy2(W/(n+'.py'),scripts/(n+'.py'))
# Machine-readable room properties are independent per floor; no copied floor template.
with (O/'09_Report/Room_Registry_V5.csv').open('w',encoding='utf-8-sig',newline='') as f:
 keys=['room_id','floor','label','use','door_ids','boundary_status'];wr=csv.DictWriter(f,keys,extrasaction='ignore');wr.writeheader();wr.writerows(S['rooms'])
print('V5 source/evidence and usage report written')
