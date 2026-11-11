import sys,json,shutil,csv
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
from PIL import Image,ImageOps
O=Path(r'E:\jz\JIA\Rebuild_V3');OLD=Path(r'E:\jz\JIA\Rebuild')
S=json.loads((O/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture']:
 shutil.copytree(OLD/d,O/d,dirs_exist_ok=True)
for name in ['CCM_Orthographic_Local.png','CCM_Grid.png']:
 shutil.copy2(W/name,O/'04_ContextCapture'/name)
for p in (W/'evidence_v3').glob('*.png'):
 if p.name.startswith(('新建工程_3MX_Plan','新建工程_3MX_SW','ZZCLDQ_3MX_Plan','ZZCLDQ_3MX_SW')):continue
 shutil.copy2(p,O/'04_ContextCapture'/p.name)
for name in ['CASES_Inventory_V3.json','CASES_Model_Files_V3.csv','CC_SDK_Projects_V3.json','3MX_Roots_V3.json']:
 shutil.copy2(W/name,O/'04_ContextCapture'/name)
shutil.copytree(W/'cc_blocks_v3',O/'04_ContextCapture/CC_SDK_Block_Exports',dirs_exist_ok=True)
dr=O/'10_DJI_Reference';dr.mkdir(exist_ok=True)
for p in (W/'dji_v3').iterdir():
 if p.is_file():shutil.copy2(p,dr/p.name)
photos=[
 ('0002/DCIM/101MEDIA','0073','西南车辆入口；四扇金属门；土院低木栅栏'),
 ('0002/DCIM/101MEDIA','0092','南侧通道；内院门楼；照壁相互关系'),
 ('0002/DCIM/101MEDIA','0101','灰色雕饰门框；深色木门；门楼瓦顶'),
 ('0002/DCIM/101MEDIA','0107','照壁连续实体墙身；面板线脚；透空菱形瓦脊'),
 ('0002/DCIM/101MEDIA','0110','照壁曲线瓦顶及端部抬升'),
 ('0002/DCIM/101MEDIA','0120','内院门楼双扇深色木门；砖石框体'),
 ('0002/DCIM/101MEDIA','0156','厨房木柱、梁、格扇、实体木裙板'),
 ('0002/DCIM/101MEDIA','0161','厨房檐下木构；内院白色粉刷墙面'),
 ('0002/DCIM/101MEDIA','0276','主楼前立面、屋顶与阳台'),
 ('0002/DCIM/101MEDIA','0303','厨房两扇单门；绿灰色轻型覆面棚；院外低木栅栏'),
 ('0002/DCIM/101MEDIA','0508','东南附属砖房；灰瓦顶；端部金属棚延伸'),
 ('0002/DCIM/101MEDIA','0581','主楼侧立面与邻居院落；周边参照'),
 ('0002/DCIM/101MEDIA','0644','木构厨房屋顶形式参照'),
 ('0001/DCIM/100MEDIA','0862','主楼入口深弧形梁、罗马柱、阳台石栏板'),
 ('0001/DCIM/100MEDIA','0867','厨房中央木柱两侧各一扇木门；门窗格局'),
 ('0003/DCIM/101MEDIA','0025','土院一侧灰砖瓦墙及白色框带'),
 ('0003/DCIM/100MEDIA','0903','院落与道路空间关系'),
 ('0003/DCIM/100MEDIA','0912','院落俯视空间校核')]
rows=[]
for coll,n,note in photos:
 p=Path('D:/DJI')/coll/('DJI_'+n+'.JPG')
 if not p.exists():continue
 name=coll.replace('/','_')+'_'+p.stem+'_Reference.jpg'
 im=ImageOps.exif_transpose(Image.open(p));im.thumbnail((2000,2000));im.convert('RGB').save(dr/name,quality=93)
 rows.append([str(p),name,note,'Reference thumbnail only; original file remains untouched'])
with (dr/'Photo_Evidence_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Original_File','Reference_Thumbnail','Evidence','Processing']);w.writerows(rows)
cases=json.loads((W/'CC_SDK_Projects_V3.json').read_text(encoding='utf-8'))
roles={'JIA':'主要几何；4 分块 OBJ2、OBJ1 与 3MX；与 E:/jz/JIA 同源', 'PTHOUSE':'同一院落另一生产；OBJ 俯视及斜视校核', 'PT666PT666':'同场地项目；生产 3MX 子块缺失，使用项目元数据及照片集合', 'MB501':'同场地 MB7 及外围生产；根 3MX 存在但引用子块不完整', 'MB7':'同场地照片项目，未找到可用完整生产', 'ui':'同一院落 3MX 解码为只读参考；低 LOD 可确认围合、厨房、棚屋', 'ZZCLDQ':'西侧周边 3MX 参考，仅部分覆盖主体场地', 'DDD':'西侧同源周边生产元数据参照', '新建工程':'大范围外围 3MX 参考；坐标基准异常，只用于外围概览', '416':'同场地照片及空三块；没有可用重建生产', '9':'同场地项目；照片与项目元数据参照', 'quan':'西侧周边照片项目，没有可用重建生产', 'KC':'GPS 位于主体场地东北约 600m；作为异地资料排除'}
with (O/'04_ContextCapture/CASES_Reference_Audit.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Project','CCM_Path','SDK_Open_Error','Blocks','Photo_Count_Across_Blocks_Not_Unique','Role'])
 for c in cases:
  w.writerow([c['case'],c['path'],c.get('error'),len(c.get('blocks',[])),sum(b.get('photos',0) for b in c.get('blocks',[])),roles.get(c['case'],'已索引；未找到足够证据作为主体建模依据')])
with (O/'09_Report/Element_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Element','Layer','Family','Classification','Source','Confidence']);w.writerows([[e.get(k,'') for k in ['name','layer','family','classification','source','confidence']] for e in S['elements']])
with (O/'09_Report/Uncertain_Items_V3.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Element','Confidence','Source','Verification']);w.writerows([[e['name'],e['confidence'],e['source'],'尺寸、断面或位置由影像/实景估测；继续编辑前按原始资料复核'] for e in S['elements'] if e['confidence']!='HIGH'])
scripts=O/'05_Intermediate/Scripts';scripts.mkdir(exist_ok=True)
for name in ['prepare_scene_v3.py','site_detail_v3.inc.py','refine_scene_v2.py','refine_scene_v3.py','prepare_exports_v3.py','export_v3.py','v2_geometry.py','su_hole_fill.py','skp_api.py','blender_v3.py','blender_v3_final.py','rhino_validate_v3.py','geometry_qa_v3.py','repair_exchange_v3.py','default_site_view_v3.py','check_exchange_v3.py','v3_plan_preview.py','annotate_site_v3.py','package_v3.py','gate_levels_v3.py','write_v3_reports.py','cc_sdk_inventory_v3.py','cc_sdk_photos_v3.py','inventory_cases_v3.py','dji_inventory_v3.py','decode_3mx_v3.py','decoded_reference_views_v3.py']:
 if (W/name).exists():shutil.copy2(W/name,scripts/name)
report=f'''# 建筑及全场地重建 V3

本版继续修正建筑与场地，重点按 DJI 原片重新区分木构、砖石瓦墙、照壁和金属棚，纠正 V2 的围墙开口与入口位置。原始资料、V1 与 V2 保留。主模型默认显示完整场地。

## 打开成果

- `06_Rhino/Production_1QK_Rebuild.3dm`：ARCH 主模型，Rhino 8 原生 Extrusion、Brep、Block、Curve，单位米。
- `07_SketchUp/Production_1QK_Rebuild.skp`：ARCH 主模型，SketchUp 2019 原生 Group / Component，单位米。
- ARCH / VIS 两版主体尺寸一致；VIS 增加可独立关闭的瓦垄等细节。
- `08_Export` 包含 OBJ、FBX、GLB 和 BLEND；FBX/GLB 保留分组、材质、UV、12 个核查相机。
- 主模型重新构建了建筑和场地；04_ContextCapture 中的实景参考没有混作主模型实体。

## 已修正的现场判断

|部位|V3 处理|原始证据|
|---|---|---|
|南侧外围墙中央|连续照壁；撤销错误的 7m 红色大门及对应坡道；增加抬升墙身、曲线瓦顶、透空菱形脊、框带|DJI_0107、0110，JIA/PTHOUSE 参考|
|西南斜边入口|撤销错误封闭墙段；建立约 4.70m 边界间距内的银灰金属车辆门及地面过渡；门框间保留接缝|DJI_0073、视频 897s，CCM 俯视|
|内院门楼|约 2.60m 净宽；灰色砖石/粉刷雕饰框体、深色双扇木门、抬升端部瓦顶；灰框不归类为木柱|DJI_0101、0120|
|厨房朝内院立面|三处木柱及石柱础、木梁、两扇独立木门、六段窗格、上亮格扇、木裙板和檐下椽条；侧后墙为砖石|DJI_0156、0303、0867|
|土院与车道之间|低木栅栏；撤销 V2 的高瓦墙隔断|DJI_0073、0303|
|内院西瓦墙|土院一侧灰砖及白色框带；内院一侧白色粉刷；墙体、饰面、瓦顶分别可编辑|DJI_0025、0156、0161|
|内院绿灰色四坡棚|轻型金属覆面棚及金属立柱；未归类为中式瓦亭|DJI_0303|
|西侧棚架|木棚架、茅草覆盖；西侧三处蓝/灰棚保持金属覆面|DJI_0073 及各集合俯视|
|东南附属房|灰砖/石墙、瓦顶；现有照片不足以判定内部全木承重体系|DJI_0508，CCM|
|主楼罗马柱与入口弧梁|按近景缩短饰面柱比例；柱脚、16 道凹槽柱身、柱头分别可编辑；加深弧梁及三块阳台面板框带|DJI_0862，D22 结构柱芯 D250，视频|

V3 建筑与场地共 {len(S['elements'])} 个语义构件组，{len(S['definitions'])} 个重复组件定义。尺寸仍按图纸轴网和层高优先；罗马柱饰面柱高 2.65m / 2.90m、场地门洞及木构断面是现场资料估测，不能当作图纸明确标注。

## 资料覆盖与 ContextCapture 使用

已扫描 D:/DJI 的全部 8 个媒体集合，共 4,803 个文件（包含 JPG/DNG 配对，数量不是独立照片数），保存逐文件路径、时间、GPS 和集合清单。每个集合生成并检查缩略图总览；相关部位再打开原分辨率 JPG 核查。10_DJI_Reference 保存总览、关键原片的等比缩略图及证据登记。未声称逐张完整审阅全部 4,803 个文件，也未把异地 003 集合用于推定本场地。

D:/AJAVIS01/ContextCapture/CASES 全目录已索引。使用安装的 ContextCapture MasterKernel 10.20 SDK 只读打开 {len(cases)} 个 CCM 项目，读取照片、空三块、重建范围和生产信息，并导出可审查的 Block XML。JIA 的 OBJ1/OBJ2、PTHOUSE OBJ 以及 ui / ZZCLDQ / 新建工程 可用 3MX/3MXB 参考均读取或解码检查。3MX 采用较低层级 LOD 作为范围和形式参考，不作为主模型原始网格复制。

部分项目只有照片、空三或缺失生产子块，逐项见 04_ContextCapture/CASES_Reference_Audit.csv；不能声称这些缺失模型已完整加载。新建工程的异常坐标与各自由 GNSS 空三高程没有控制点校验；其概览仅作为周边参考。JIA、PTHOUSE、ui 的参考视角相互确认照壁连续墙身、西南入口和木构厨房的位置。原模型和 CCM 文件保持只读。

总图 D01 确定建筑、厨房、主院和道路关系；真实围墙及西侧附属土院范围由 JIA 实景追踪。现状模型围合面积约 {S['site']['area_m2']:.1f}m²，属于模型包络面积，不是法定用地面积。正式图纸轴网、门窗和楼梯依据见 02_PDF_Reference；视频关键帧见 03_Insta360_Frames。

## 几何与导出检查

09_Report 中提供可回读的检查结果。原生 Rhino 使用 Rhino 8 内核校验有效性和建筑闭合性；SketchUp 回读检查根级散面、散边、实体体积和 900mm 门尺寸。展开封闭构件检查非流形边、反向体积和完全重复实体。FBX/GLB 独立导入，核查尺寸、UV、材质、场地构件和退化面。上述检查可发现几何/交换错误，但不能证明整个现场达到测量验收精度，也不能代替所有构件两两碰撞检查。

优先查看 V3_Site_Classification 分类图、VIS_CAM_06_Whole_Site、VIS_CAM_09_SW_Gate、VIS_CAM_10_Screenwall、VIS_CAM_11_Chinese_Kitchen、VIS_CAM_12_Inner_Gate 以及罗马柱和交接近景。厨房椽条统一按屋面中心与下表面定位；西南入口过渡面裁去道路重叠，并接到门槛和院坪。实景地面采样显示入口低于主院：门槛两端按约 -0.85m / -1.20m、金属门底沿坡、车辆通道向内院 -0.45m 过渡。源网格门下有孔洞及局部噪声，这些取值是邻近地面样本与照片的近似拟合，列为 MEDIUM，需现场水准测量复核。

## 仍需实测或更细资料

墙厚、场地门洞净高、木构榫卯、细雕纹样、陶瓦逐片形状、隐蔽结构、砖石砌缝、场地管线及树种尚未完成逐件测绘。格扇以可识别的八角/矩形构图重建，未声称逐根吻合复杂回纹。门楼、照壁和阳台保留可编辑面板框，不虚造未经测量的图案。厨房及附属房内部房间布局未经核实。门窗表 C1212 第六处仍未明确定位，没有虚设。全部 MEDIUM / LOW 构件列入 Uncertain_Items_V3.csv。

生成脚本在 05_Intermediate/Scripts；依赖与原始路径仍按本机配置。此版可用于继续设计和修改，不能声称毫米级现状测绘成果。
'''
(O/'09_Report/Model_Report_V3.md').write_text(report,encoding='utf-8')
(O/'README_V3.md').write_text('建筑及完整场地 V3\n\n打开 06_Rhino/Production_1QK_Rebuild.3dm 或 07_SketchUp/Production_1QK_Rebuild.skp。\n\nV3 重点：西南真实入口、连续南侧照壁、灰色内院门楼、厨房中式木构、瓦墙、罗马柱比例及交接。\n\n详细证据、估测项及文件校验见 09_Report/Model_Report_V3.md；全部 DJI 集合清单及关键参考见 10_DJI_Reference。\n',encoding='utf-8')
coord=S['coordinate']
(O/'09_Report/Coordinate_System_Report_V3.md').write_text('# 坐标系统 V3\n\n单位：米；本地建筑 X/Y 轴、Z 向上。源系统：'+coord['srs']+'\n\n本地转 ENU：\n```json\n'+json.dumps(coord['local_to_survey'],indent=2)+'\n```\n\n真北本地向量：[0.3362735, 0.9417644, 0]。本地 0.000 对应 JIA ENU 高度 1303.750；水平转角 19.65°。其他生产仅作初步相对叠合与形式参考，尚无独立控制点统一其高程与异常坐标。\n',encoding='utf-8')
print('V3 evidence, source audit, reports and scripts prepared; selected photo previews',len(rows))
