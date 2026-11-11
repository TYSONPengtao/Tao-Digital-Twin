from pathlib import Path
import json,csv,shutil,collections
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V4');OLD=Path(r'E:\jz\JIA\Rebuild_V3')
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture','10_DJI_Reference']:
 shutil.copytree(OLD/d,O/d,dirs_exist_ok=True)
for sub in ['v4_audit_codes','v4_audit_junction','v4_audit_safety']:
 target=O/'11_Construction_Reference'/sub;target.mkdir(parents=True,exist_ok=True)
 for p in (W/sub).iterdir():
  if p.is_file() and p.suffix in ['.md','.csv','.json','.pdf','.png','.txt','.py'] and p.name!='Scene_Repair_Test.json':shutil.copy2(p,target/p.name)
for n in ['Applicable_Constraints.json','Applicable_Constraints.csv','Code_And_Drawing_Audit_V4.md']:shutil.copy2(W/'v4_audit_codes'/n,O/'11_Construction_Reference'/n)
for n in ['Coordinate_System_Report.md','README.md']:
 if (OLD/'09_Report'/n).exists():shutil.copy2(OLD/'09_Report'/n,O/'09_Report'/('Source_'+n))
S=json.loads((O/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
with (O/'09_Report/Element_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 fields=['name','layer','family','classification','source','confidence','status','host','finished_surface_role'];wr=csv.writer(f);wr.writerow(['Element']+fields[1:]);wr.writerows([[e.get(k,'') for k in fields] for e in S['elements']])
with (O/'09_Report/Construction_Changes_V4.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.writer(f);wr.writerow(['ID','Description','Elements','Complete_Record']);wr.writerows([[r.get('id'),r.get('description',r.get('action',r.get('note',''))),' | '.join(r.get('elements',r.get('part',[]) if isinstance(r.get('part'),list) else [r.get('part','')])) ,json.dumps(r,ensure_ascii=False)] for r in S['v4_construction_changes']])
for n in ['build_scene_v4.py','export_v4.py','geometry_qa_v4.py','rhino_validate_v4.py','default_site_view_v4.py','blender_v4.py','repair_exchange_v4.py','check_exchange_v4.py','prepare_exports_v4.py','write_v4_reports.py','package_v4.py']:
 dst=O/'05_Intermediate/Scripts';dst.mkdir(exist_ok=True);shutil.copy2(W/n,dst/n)

def read(n):
 p=O/'09_Report'/n
 return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
g=read('Geometry_QA_V4.json');native=read('Native_Model_QA.json');inter=read('Interface_Repair_Check.json');co=read('Construction_Geometry_QA_V4.json')
report=f'''# 建筑与周边场地 V4 — 施工深化协调模型

更新：2026-10-08。沿用 V3 的建筑、完整院落、道路与周边环境，修改工程交接并增加防护、门窗收口及排水提案。V3 和原始 CCM、照片、图纸未覆盖。V4 中施工提案由构件 `status`、`host` 和修改登记区分，可单独选取。

## 本轮落地修改

|部位|V4处理|依据及边界|
|---|---|---|
|填充墙/框架梁|按梁底、梁顶分层扣除墙体占据的梁核心，墙梁实体交叉体积复测0|框架梁柱正式尺寸保持；抹灰不是结构核心|
|罗马柱/弧梁|完整水平柱头座，弧线从柱头内边起拱；完整柱头接触面|座436×436×55mm为接口推定；结构承载与连接未验算|
|楼梯|四跑逐级等分层高；140mm法向腰板；平台与梯板端部连续；井侧连续900mm扶手、100mm杆净距|D10/D11、住宅用途；保留每跑11级及10×260mm。原1175/50/1275为轴向分段，旧“1175/90/1175”误读已撤销|
|梯板/平台重复面|从梯板扣除已归属平台、楼板的公共混凝土，消除黑色重合顶面|联合体外形体积差0；保留约0.33～0.35m²几何接触面，未作为承载计算|
|楼梯横向|提案两跑各1100mm、中央井20mm，置于梁墙饰面后的净空内|扶手后约1075mm；未当作规范通过，须与原设计及住宅楼梯适用条文协调|
|阳台/露台|顶高为结构面以上1300mm，从提案完成面最高点复测净高；阳台1%、露台2%找坡及防水层|新增找坡属于施工提案；增高石栏的自重、防攀爬和锚固仍须设计复核|
|外窗/飘窗|逐窗外坡5%，实际窗台及上楣滴水槽，低窗台竖向防护|槽8×8mm、护栏与锚固尺寸为提案，窗台外排方向按实际旋转窗面核查|
|附属棚|12柱接连续支承梁，梁随屋面底面；下部补贴近相邻土面的外露石砌基座几何|解决浮空，不把基座当作经验证的基础或地基承载设计|
|中式木构厨房|门头/上亮填缝，保留门扇3mm安装缝；山墙随瓦顶底面收口|依据DJI木柱、木梁、格扇、木裙板证据；新增连接未设计配筋/锚固|
|门楼、照壁、瓦墙|基层贴瓦顶曲面；东侧墙顶独立于外侧低土高程；抹灰/饰框贴基层并压在墙顶下|中式木构、砖石照壁、瓦墙、金属车辆门分类继续保留；没有把装饰框当成门洞|
|二三层右浴室|关闭误设横向洞，转回x10.8纵向隔墙M0821及门实例|D03/D04；具体门框偏移待实测|
|西南车辆门|底横杆抬40mm，工作间隙与门槛分开|闭合形态提案；实际铰链、开启轨迹与现场坡面须复核|
|屋面排水|D04五个DN100符号全部落实为独立雨水管；新檐沟与连接段、西屋面找坡/两个排水口、集水接收点|管中心为按实际檐口协调的示意位置；雨量计算、管容量、外部接入高程未取得；未与WL污水立管混接|
|主要明院|新增0.2%双向找坡区及接收角点；摄影地面保留为基础参考|只覆盖主要明院，外围道路/土院仍为摄影重建，不能宣称全场地排水合规|

## 几何和文件验证

- 场景 {len(S['elements'])} 个语义构件、{len(S['definitions'])} 个组件定义，修改登记 {len(S['v4_construction_changes'])} 项。
- 闭合实体拓扑检查 {g.get('expanded_closed_parts','待更新')} 件；非流形 {len(g.get('nonmanifold_parts',[]))}、非正体积 {len(g.get('nonpositive_signed_volume',[]))}、完全重复实体 {len(g.get('exact_duplicate_solids',[]))}。
- 接口独立复验覆盖墙梁、12棚柱、门楼/照壁、4个柱头、2浴室门洞及8组饰框。结果见 `Interface_Repair_Check.json`。
- 原生 RhinoCommon 及 SketchUp SDK 回读、OBJ/FBX/GLB 独立回读、单位/UV/材质/退化面检查结果见 QA JSON。这些检查证明文件几何可用，不能代替承载设计或法定验收。
- 施工参数审查：{co.get('counts',{}).get('pass',0)}项限定几何检查通过、{co.get('counts',{}).get('fail',0)}项已建几何不符、{co.get('counts',{}).get('needs-design',0)}项仍须专业设计/实测。详见 Construction_Geometry_Checks_V4.csv，未把待核项算作通过。
- 楼梯协调图为剖开观察视图，暂隐框架和楼板以便观察梯板/扶手；导出模型保存完整建筑，全场地视图是默认打开视图。

## 规范核查与待核事项

按政府公布的 GB55038-2025《住宅项目规范》、GB55030-2022《建筑与市政工程防水通用规范》、GB55031-2022《民用建筑通用规范》、GB55032-2022《建筑与市政工程施工质量控制通用规范》正文逐项核对。原图是2020年家庭住宅，不将公共楼梯指标直接套用于户内梯。条文、官方URL、PDF正文和图纸裁图保存在 `11_Construction_Reference/`，真实几何核查逐项输出 pass/fail/needs-design。

尚需专业核审/现场实测：结构计算、配筋及增高栏板荷载；基础与地基承载、挡墙抗震；木构锚固和瓦顶抗风连接；门实际开启净宽；楼梯横向与首层177.273mm升高适用性；西屋面是否上人及其防护；厨卫结构沉板、完成面≤15mm过渡、地漏和2m淋浴防水做法（本轮只登记，没有凭空改变原板标高）；排水接入井底及容量；实测高程、法定用地界。

图示195m²用地与约{S['site']['area_m2']:.1f}m²摄影院落包络分别保留，后者不是产权界。CCM相对高程未用独立控制点校准，不能拿当前小数精度作为施工放样精度。成果名称为“施工深化协调模型，待专业核审”。

## 资料覆盖与使用

延续V3的完整资料索引：D:/DJI八个集合4803个媒体文件已索引并制作联系表，近景依据保存在10_DJI_Reference；ContextCapture CASES项目索引、原生SDK只读检查及能加载的相关生产模型在04_ContextCapture；31张图纸在02_PDF_Reference；视频关键帧在03_Insta360_Frames。未声称每张原图都做了逐像素量测，也不把缺失子块的生产当成完整可用模型。

`06_Rhino/Production_1QK_Rebuild.3dm` 与 `07_SketchUp/Production_1QK_Rebuild.skp` 为默认ARCH完整建筑与场地；VIS版增加瓦行、装饰等视觉细节。08_Export含OBJ/MTL、FBX、GLB和Blend；05_Intermediate含可追溯场景和脚本。分类、来源、置信度和施工提案状态可在原生构件属性及登记CSV查看。
'''
(O/'09_Report/REPORT_V4.md').write_text(report,encoding='utf-8')
print('V4 source, construction evidence and reports saved')
