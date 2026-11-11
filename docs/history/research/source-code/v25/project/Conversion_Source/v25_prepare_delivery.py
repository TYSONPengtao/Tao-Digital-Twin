# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from pathlib import Path
import json,shutil
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25';S=O/'Source_Metadata';S.mkdir(exist_ok=True)
for n in ['Export_Index.json','Material_Index.json','Texture_Index.json','Camera_Index.json','Door_Hinges.json','Source_Visible_Geometry.json','Export_Report.json']:shutil.copy2(D/n,S/n)
shutil.copy2(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json'),S/'LOCAL_to_Original_ENU.json')
for n in ['V24_37_Delivery_QA.json','V24_37_Interior_Physics_QA.json','V24_37_Exterior_Physics_QA.json','V24_37_Collision_Index.json']:
 shutil.copy2(Path('E:/jz/JIA/Rebuild_V24_37/Reports')/n,S/('Inherited_'+n))
source=O/'Conversion_Source';source.mkdir(exist_ok=True)
for n in ['v25_export_blender.py','v25_build_rhino.py','v25_rhino_common.py','v25_mesh_bridge.cs','v25_verify_rhino.py','v25_verify_companion.py','v25_viewport.py','v24_qa_blender.py']:shutil.copy2(W/n,source/n)
launch='''@echo off
chcp 65001 >nul
setlocal
set "V25_RHINO_EXE=D:\\AJAVIS01\\RHINO8\\RUNING\\System\\Rhino.exe"
if not exist "%V25_RHINO_EXE%" (
  echo 请使用 Rhino 8 打开 Rhino 文件夹中的 3dm 文件。
  pause
  exit /b 1
)
start "" "%V25_RHINO_EXE%" "%~dp0Rhino\\Architecture_Complete_V25.3dm"
'''
(O/'打开Rhino模型.cmd').write_text(launch,encoding='utf-8-sig');(O/'打开ENU坐标模型.cmd').write_text(launch.replace('Architecture_Complete_V25.3dm','Architecture_Complete_V25_ALIGNED_ENU.3dm'),encoding='utf-8-sig')
readme='''Rebuild_V25 — Rhino 8 分层模型及安全漫游配套

主要文件
Rhino/Architecture_Complete_V25.3dm
当前模型本地坐标，米，Z轴向上。打开Rhino模型.cmd可直接打开。

Rhino/Architecture_Complete_V25_ALIGNED_ENU.3dm
相同内容，应用原项目19.65度旋转及(-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002)米平移。
用于与原项目ENU模型叠合。不要将两份相同内容重复导入同一场景。
采用原有坐标依据，没有新增独立控制点或测量精度认证。

内容
以V24.37修正版为基础，包含当前建筑、院落、附属房屋、门窗、
连续红木楼梯扶手、围墙、原实景外景以及MB7和PTJIA6补充外景。
沿用“完整、连续成块，尽量保留信息和特征”的外景保留结果。
原有版本与摄影测量源数据均保留，没有改写。

Rhino模型包含2661个来源构件，按材质拆为2781个可独立编辑网格，
共13,793,693个三角面，其中摄影测量外景6,412,786个三角面。
没有简化有效三角面；去除10,774个零面积退化面。
保留原构件名称、父级分组、材质分组和来源属性。
本文件是网格3dm，不是重新拟合的NURBS实体。
原照片按字节及UV保留；程序颜色材质转为无光照烘焙贴图。
原有物理材质参数转为Rhino PBR；两种软件的显示光照存在差异。
照片及转换贴图共2154张，已嵌入3dm，并另附Textures文件夹。
使用Rhino“渲染”显示模式查看贴图，命名视图中可切换建筑、
完整外景、院落、青砖墙细部及外景道路。物件均以米为单位。

编辑与漫游
Rhino版门窗为原动画第40帧的静态姿态，按构件和父级保留分组，
Source_Metadata/Door_Hinges.json保留本地坐标铰链与交互元数据。
Rhino文件没有嵌入Blender的动画、行走或碰撞执行程序。

Blender/Architecture_Complete_V25.blend为配套原生文件，保留已验证的
门窗动作、1.65米人物、全模型支撑检查、边缘防跌落与安全回位。
启动漫游.cmd可直接进入。已有代码和碰撞网格与V24.37逐项保持。
WASD/方向键移动，右键转向，空格跳跃，Shift快走，V切换视角，
Home回院落，Esc退出，F8重新进入；N面板可切换各层和外景落点。
人物在有实际支撑及足够净空的位置通行，扫描缺口不会虚构地面。

核验
Reports/V25_Rhino_Readback_QA.json：由本机Rhino原生内核重新读取两份3dm，
检查全部网格/UV/法线/材质/图层/分组、嵌入贴图原始字节和坐标。
Reports/V25_Companion_QA.json：Blender配套与V24.37的构件、材质、
照片字节、门窗动作、碰撞网格及运行脚本保持性核验。
Reports/V25_Rhino_Desktop_QA.json及PNG：实际Rhino渲染显示截图。
Source_Metadata：导出索引、坐标依据及继承的安全漫游验证记录。
Conversion_Source：转换与核验源代码；重放需要原本地资料及相应运行环境。
全部主要文件SHA256见Manifest_SHA256.json。
'''
export=json.loads((D/'Export_Report.json').read_text('utf8'));readme=readme.replace('2781',str(export['exported_material_parts'])).replace('2154',str(export['textures']))
readme=readme.replace('13,793,693',format(export['export_triangles'],','))
if export.get('coplanar_internal_backfaces_removed'):
 readme=readme.replace('没有简化有效三角面；去除10,774个零面积退化面。','去除10,774个零面积退化面，并清除'+str(export['coplanar_internal_backfaces_removed'])+'个被保留表面完整覆盖的内部重面。\n保留表面的位置、法线和UV不变，未简化实景外景。')
readme=readme.replace('保留原构件名称、父级分组、材质分组和来源属性。','保留原构件名称、父级分组、材质分组和来源属性。\n可用Ctrl+Shift选择分组内的单个网格，或按需要使用Ungroup解组。')
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig');print('V25_DELIVERY_LAYOUT_READY',flush=True)
