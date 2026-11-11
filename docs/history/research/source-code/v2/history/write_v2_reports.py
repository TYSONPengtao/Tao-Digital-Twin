import json,shutil,csv,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V2');OLD=Path(r'E:\jz\JIA\Rebuild')
S=json.loads((O/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture']:shutil.copytree(OLD/d,O/d,dirs_exist_ok=True)
for name in ['CCM_Orthographic_Local.png','CCM_Grid.png']:shutil.copy2(W/name,O/'04_ContextCapture'/name)
for p in [Path(r'D:\Desktop')/f'屏幕截图 2026-10-07 {stamp}.jpg' for stamp in ['210403','210850','210905','210925','210951']]:
 if p.exists():shutil.copy2(p,O/'01_Source'/p.name)
scripts=O/'05_Intermediate'/'Scripts';scripts.mkdir(exist_ok=True)
for name in ['refine_scene_v2.py','export_v2.py','prepare_export_v2.py','v2_geometry.py','su_hole_fill.py','skp_api.py','blender_v2.py','rhino_validate_v2.py','geometry_qa_v2.py','roof_check_v2.py','repair_exchange_v2.py','default_site_view.py','check_exchange_v2.py']:
 shutil.copy2(W/name,scripts/name)
qa=json.loads((O/'09_Report/Native_Model_QA.json').read_text(encoding='utf-8'));geom=json.loads((O/'09_Report/Geometry_QA_V2.json').read_text(encoding='utf-8'));roof=json.loads((O/'09_Report/Roof_Reality_Comparison.json').read_text(encoding='utf-8'))
report=f'''# 建筑及周边环境重建 V2

本次针对“边界交接错误、完整场地缺失、罗马柱需优化”重新建立建筑外壳和场地。原 V1 文件保留。新版主模型同时包含主楼与完整现状院落，60_SITE 默认显示。

## 主文件

- 06_Rhino/Production_1QK_Rebuild.3dm：ARCH 主模型，原生 Extrusion、Brep、Block、Curve，单位米。
- 07_SketchUp/Production_1QK_Rebuild.skp：ARCH 主模型，独立 Group / Component，单位米。
- 同目录 ARCH、VIS 是两个版本；VIS 增加可关闭的瓦垄细节，主体尺寸一致。
- 08_Export：OBJ、FBX、GLB、BLEND；FBX/GLB 含层级、材质、UV 和相机。
- 04_ContextCapture 中带 REFERENCE 的 3dm 仅供叠合核对，实景三角网格没有被作为主楼模型交付。

## 本次改动

1. 每层外墙按门窗标高切片，统一墙体平面，处理柱边与转角；内墙平面去除重复交叠。
2. 分散楼板改成连续轮廓，保留楼梯开口周边承托；层间线脚按同一轮廓连续生成，绕过折角飘窗。
3. 主屋顶改为实景中的矩形四坡屋顶；西侧改为平屋面设备露台与金属棚，不再保留错误的 L 形瓦屋顶。
4. 罗马柱建立柱脚、16 道凹槽柱身、渐变柱径与线脚柱头。结构 D250 来自 D22，成品外径、线脚及柱高由视频比例估计。柱脚与柱头为旋转 Brep；凹槽柱身为独立可编辑 Brep，SketchUp 使用重复组件。入口弧形梁与柱顶接合。
5. 建立西侧土院、主院铺装、分隔墙、厨房及木门窗、东南附属房、3 处棚屋、院内亭棚与西侧棚架、两道门楼、入口坡道、种植区、道路与周边地形。
6. 现状围墙范围由 CCM 对应实景成果的正射视角描取。整条周界共用曲线端点与转角截面，石基、粉刷段、瓦顶分件接合。南侧道路低于院坪的高差保留。
7. 补上西侧屋面太阳能热水器。瓦垄、设备、树冠尺寸等为实景辅助估计，均带来源与可信度属性。

## 场地依据与范围

- JIA.ccm 是本地 ContextCapture 项目索引；模型几何采用同项目已有 Production_OBJ (2) 四分块和 Production_1QK.3mx/3mxb 生产成果。没有把 CCM 当作普通网格解码，也没有修改原项目。
- D01 总平面确定主楼、厨房、南院、入口及周边道路的建模关系；该图没有提供现状围墙的完整尺寸。西侧棚屋院落作为现状周边环境补建。
- 实景围墙包络约 {S['site']['area_m2']:.1f} 平方米，包含现状西侧附属院落。此数值是模型包络面积，不能用作用地或权属面积。
- PDF 示意范围在 00_REFERENCE，实景周界在 60_SITE；两者没有混作法定地籍边界。
- 道路和土院以实景水平面样本的低分位值重建，先在 0.75m 网格平滑，再按 0.9–2m 网格裁切成可编辑地形曲面。不是将原始实景三角面直接复制到主模型。被屋顶覆盖或缺少地面观测的位置采用相邻样本插值；主院地坪按图纸 -0.450m。
- 实景生产为 2025 年资料，视频为 2026 年资料；西侧土院优先保留 CCM 截图中的土质状态，主院采用视频和图纸确认的硬质地坪。

## 已完成检查

- SketchUp ARCH / VIS 重新打开成功；无根级散面、散边；实体体积检查无失败；900mm 门回读为 0.900m。
- Rhino ARCH / VIS 使用 Rhino 8 内核初始化边缘公差并重新写入，重新打开检查：无无效对象，无意外开放的建筑 Brep。地形曲面本来就是开放曲面。
- 交换几何 {geom['expanded_closed_parts']} 个展开实体：无非流形实体、无反向或非正体积、无完全重复实体。这个检查不能代替所有实体之间的碰撞检查。
- 通过全场、正面、背面、柱身及窗台收口的渲染视角检查。近景参见 VIS_CAM_07_Column.png 和 VIS_CAM_08_Junction.png。
- 主瓦屋面与 7,778 个实景面心作竖向对比：中位差 {roof['median_m']:.3f}m、90 分位 {roof['p90_m']:.3f}m，最大差 {roof['maximum_m']:.3f}m。最大差含设备和非屋面观测的影响，未作人工剔除。坐标配准没有独立控制点，此数值不代表工程验收精度。

## 精度边界及待实测项

主体轴网、层高、正式门窗规格、楼梯采用图纸。飘窗局部净高、厨房及棚屋构件厚度、围墙厚度、道路边缘宽度、罗马柱线脚、门楼装饰和植被体量由实景估计，标为 MEDIUM。C1212 门窗表为 6 处，主楼明确定位 5 处，第 6 处位置仍未确认，未虚设。细石砌缝、雕花、门楼翘角曲面、树种、场地管线并未逐件精细复原。模型适合继续设计和修改，不能声称已完成独立控制测量或毫米级现状测绘。

源文件只读。生成脚本保留在 05_Intermediate/Scripts，使用本机原项目路径及安装 SDK；运行前需配置 numpy 1.26、shapely、mapbox-earcut、scipy 1.11、rhino3dm 和 pythonnet / rhinoinside，Rhino 验证需要本机 Rhino 8。
'''
(O/'09_Report/Model_Report_V2.md').write_text(report,encoding='utf-8')
(O/'README_V2.md').write_text('建筑及周边环境重建 V2\n\n优先打开 06_Rhino/Production_1QK_Rebuild.3dm 或 07_SketchUp/Production_1QK_Rebuild.skp。场地默认显示。\n\n全场预览：09_Report/VIS_CAM_06_Whole_Site.png\n罗马柱：09_Report/VIS_CAM_07_Column.png\n交接近景：09_Report/VIS_CAM_08_Junction.png\n\n详细改动、来源、校验与估测项见 09_Report/Model_Report_V2.md。\n',encoding='utf-8')
coord=S['coordinate'];(O/'09_Report/Coordinate_System_Report_V2.md').write_text('# 坐标系统\n\n单位：米；本地建筑轴 X/Y、Z 向上。\n\n源系统：'+coord['srs']+'\n\n本地转 ENU：\n```json\n'+json.dumps(coord['local_to_survey'],indent=2)+'\n```\n\n真北本地向量：[0.3362735, 0.9417644, 0]。本地 0.000 对应 ENU 高度 1303.750。水平转角 19.65°。建筑对齐沿用正式轴网与实景外墙的初步配准；没有独立控制点与独立高程基准校验。\n',encoding='utf-8')
with (O/'09_Report/Uncertain_Items_V2.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['Element','Confidence','Source','Verification']);wr.writerows([[e['name'],e['confidence'],e['source'],'尺寸估测，按来源属性复核'] for e in S['elements'] if e['confidence']!='HIGH'])
print('V2 source references and reports prepared')
