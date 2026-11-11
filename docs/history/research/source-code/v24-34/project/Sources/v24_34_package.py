# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text());assert sha(source['model'])==source['sha256'];qa={}
for n in ['Native','Surface','Interior_Physics','Exterior_Physics','Measure_Math','Launcher','Viewport']:
 q=json.loads((R/f'V24_34_{n}_QA.json').read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(n,q['status'],q['model_sha256'],h);qa[n]={'checks':len(q['checks']),'failures':0}
for name,*_ in json.loads((D/'Views.json').read_text()):
 q=json.loads((R/f'V24_34_{name}_State.json').read_text());assert q['model_sha256']==h and not q['draft'];assert(R/q['file']).stat().st_size>10000
assert(R/'V24_34_Exterior_Roam_UI.png').stat().st_size>10000
clip=json.loads((D/'Clip_Report.json').read_text());surface=json.loads((R/'V24_34_Surface_QA.json').read_text());area=next(x['added_ground_projection_m2']for x in surface['checks']if'added_ground_projection_m2'in x)
readme=f'''V24.34 MB7 缺失外景扩展与全模型安全漫游

打开修正版模型.cmd：打开可编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游及长度、面积测量。

外景来源：D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model
MB7 原始 OSGB 为分级模型。本版采用最高精度的不重叠叶节点，
按共同建筑和道路做照片特征及表面配准，再按当前模型的实际覆盖
边界裁切。仅补入缺失区域，原建筑、院落、已有外景及全部门窗
动作保持原样。保留 {clip['added_tiles']} 块扩展、{clip['added_triangles']:,} 个三角面，
新增平面覆盖约 {area:.1f} 平方米，不包含重叠楼面与树冠的重复投影。
原始 JPEG 逐字节提取打包，裁切边缘保留原照片 UV；在新模型
靠近旧模型的 0.75 米范围内渐变贴合高度，避免接缝错层。

源坐标 EPSG:32647、源原点 TAO_PRIVATE_SITE_020,TAO_PRIVATE_SITE_005,0。与当前模型的
高程基准不同，本版用 71 处共同照片特征校准，特征复核 RMS
约 0.132 米。此为摄影测量模型配准，未使用新的独立测量控制点。
没有据此改动原生建筑尺寸或原模型坐标。

原有实景外景和新增 MB7 外景都加入真实表面碰撞代理。
原建筑碰撞保持，室内、楼梯、院落仍可通行。脚底按九点取样并
校正胶囊底部与扫描起伏的接触；扫描范围边缘和无支撑缺口会阻止
人物迈出，意外失去支撑时返回最近安全位置。不添加穿过建筑的
无限平地。第一人称和第三人称使用同一套安全移动逻辑。

扫描资料本身的树冠孔洞、叶片拉伸及边界缺失仍属于源资料范围；
人物在有支撑、可通过的真实表面行走，陡壁和实体障碍会阻挡。

操作：WASD / 方向键移动；空格跳跃；Shift 快走；右键拖动转向；
滚轮调整距离；V 切换人眼 / 第三人称；M 切换材质 / 流畅预览；
Home 回院落；Esc 退出；F8 再进入。按 N 打开右侧“建筑漫游”，
可直接选择“外景道路”和“新增地块”，也可回各层楼面。
L 点两点测长度，P 沿边界点选并 Enter 测面积；Backspace 撤销，
Esc 返回人物移动，顶栏可导出 CSV；Ctrl+S 保存测量记录。

检查：原生对象、材质、照片、门窗动作保持；新增区域无重面和
父子 LOD 叠加；原室内与楼梯 35 项通行检查；约 112 米外景道路
双向实走；新地块低于 -12 米的支撑与跳跃；扫描边缘持续行走、
跳跃防掉落；实际键盘漫游及长度、面积 UI；原生材质预览。
所有检查报告绑定同一个最终模型 SHA256。

Reports：全景、材质预览、实际漫游截图和检查记录。
Source_Metadata：原 OSGB 层级清单、源 metadata.xml、配准和裁切边界。
Sources：新增网格及原照片、处理脚本、前后核对数据。
原生模型已打包纹理，编辑与漫游不依赖 Sources。重放构建需要
本机原 V24.33 文件，解码与裁切需原 MB7 文件及本机 OSG 工具。
旧 V24.33 与用户 MB7 源文件没有覆盖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
S=O/'Sources';SD=S/'v24_34';SD.mkdir(parents=True,exist_ok=True)
for p in W.glob('v24_34_*.py'):
 compile(p.read_text('utf8'),str(p),'exec');shutil.copy2(p,S/p.name)
for n in ['v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
for p in D.glob('*.json'):
 if p.name!='Delivery_Result.json':shutil.copy2(p,SD/p.name)
for p in D.glob('*.geojson'):shutil.copy2(p,SD/p.name)
for p in D.glob('FINAL_*.npz'):shutil.copy2(p,SD/p.name)
for p in D.glob('SRC_*.npz'):shutil.copy2(p,SD/p.name)
rows=json.loads((D/'Missing_Exterior_Index.json').read_text())
for row in rows:
 for rel in [row['file']]+[t['file']for t in row['textures']]:
  target=SD/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/rel,target)
for name in ['Existing_Context_Top.png','MB7_Geographic_Seed_Top.png','Registration_Matches.jpg','Route_Support_Map.png']:
 if(D/name).exists():shutil.copy2(D/name,O/'Source_Metadata'/name)
shutil.copy2(D/'Planned_Routes.json',R/'V24_34_Tested_Route_Waypoints.json')
total=sum(q['checks']for q in qa.values());(R/'V24_34_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_model_sha256':source['sha256'],'checks':qa,'total_checks':total,'new_tiles':clip['added_tiles'],'new_triangles':clip['added_triangles'],'new_coverage_m2':area,'source_unchanged':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix not in ['.blend1','.blend2']and not p.name.startswith('Draft_')and p.name!='Manifest_SHA256.json'];manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_34_MB7_Exterior_Safe_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
 for p in files:z.write(p,Path('Rebuild_V24_34')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,q in manifest.items():
  with z.open('Rebuild_V24_34/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==q['sha256'],rel
out={'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'model':str(P),'model_sha256':h,'total_checks':total,'files':len(files)};(D/'Delivery_Result.json').write_text(json.dumps(out,indent=2));print('DELIVERY_VERIFIED',json.dumps(out),flush=True)
