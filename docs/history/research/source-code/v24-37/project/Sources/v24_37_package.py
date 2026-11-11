from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);source=json.loads((D/'Source.json').read_text());assert sha(source['model'])==source['sha256'];qa={}
for name in ['Native','Surface','Interior_Physics','Exterior_Physics','Measure_Math','Launcher','Viewport']:
 q=json.loads((R/f'V24_37_{name}_QA.json').read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and q['model_sha256']==h,(name,q['status'],q['model_sha256'],h);qa[name]={'checks':len(q['checks']),'failures':0}
for tag in ['Kitchen_Wall_Eave','Kitchen_Wall_Close','House_And_Context','Expanded_Context','PTJIA6_Road_Eye','PTJIA6_Field','Clean_Context_Top']:
 q=json.loads((R/f'V24_37_{tag}_State.json').read_text());assert q['model_sha256']==h and not q['draft'];assert(R/q['file']).stat().st_size>10000
plan=json.loads((D/'Cleanup_Report.json').read_text());percent=plan['retained_triangles']/plan['source_triangles']*100;reg=json.loads((W/'v24_36/PTJIA6_Registration.json').read_text());ci=json.loads((R/'V24_37_Collision_Index.json').read_text());total=sum(q['checks']for q in qa.values())
readme=f'''V24.37 连片外景清理、PTJIA6扩展与全模型安全漫游

打开修正版模型.cmd：打开可编辑的 Blender 原生模型。
启动漫游.cmd：进入 1.65 米人物漫游，支持第一人称和第三人称。

本次完成
1. 清除截图135627中厨房青砖外墙和屋檐上的白色扫描残片。
   原青砖墙、连续瓦顶、两根烟管、原房屋及门窗动作保持。
2. 在已有建筑和MB7外景之外，加入PTJIA6缺失外景。采用不重叠的
   最高精度3MXB叶节点，只保留现有模型覆盖范围之外的部分。
3. 按“保留完整、连续成块、尽量保留信息和特征”整理全部扫描外景。
   田块、道路、房屋、主要植被块继续保留；裁掉北侧拉长扫描幕片、
   孔洞密集的破碎外缘和微小悬浮碎片。未填造不存在的扫描地形。
   共移除{plan['fully_removed_meshes']}个仅剩残片的对象，保留{plan['retained_meshes']}个扫描部分，
   {plan['retained_triangles']:,}个显示三角面，占清理前扫描面的{percent:.2f}%。
   所有保留的照片贴图和原始UV继续使用；裁切边界采用原UV插值。
4. 按清理后可见几何重建全部实景外景碰撞，原建筑碰撞完整保留。
   碰撞共{ci['all_triangles']:,}个三角面，原建筑{ci['architectural_triangles_preserved']:,}个三角面逐项保持。
   人物在有实际支撑和足够净空的表面漫游。缺失边缘和无支撑缺口
   会阻止迈出；意外失去支撑会回到最近的安全落脚点。

外景来源
MB7：D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model
PTJIA6：D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model
原3MXB及MB7源资料未修改。原V24.34、V24.35、V24.36均保留。
模型纹理已打包，编辑和漫游不依赖上述原始资料路径。

坐标和精度
PTJIA6使用源ENU坐标，经地理坐标转换及共同照片特征、表面配准
对齐当前模型。{reg['landmark_inliers']}处局部共同特征的RMS约{reg['inlier_rms_m']:.3f}米。
该数值用于局部摄影测量模型衔接，不是独立测量验收精度，
也不代表全部远景具有同样的绝对坐标精度。原建筑尺寸未更改。

操作
WASD / 方向键：移动；空格：跳跃；Shift：快走；右键拖动：转向。
滚轮：调整跟随距离；V：切换人眼/第三人称；M：材质/流畅预览。
Home：回院落；Esc：退出；F8：再进入。
按N打开“建筑漫游”：可回院落和各层，也可选择“外景道路”、
“新增地块”、“PTJIA6道路”和“PTJIA6地块”。
L：两点测长度；P：沿边界点选后Enter测面积；Backspace：撤销。
测量时Esc回人物移动；顶栏可导出CSV；Ctrl+S可保存测量记录。

验证
{total}项检查通过。包含原建筑、材质、贴图字节及门窗动作核对；
35项原室内和楼梯通行；约197米PTJIA6道路及原道路接缝双向实走；
远处地块支撑与跳跃；有限扫描边缘行走、跳跃和丢失支撑回位；
实际键盘输入、视角切换、外景预设、长度面积UI及材质预览。
全部最终报告绑定同一个模型SHA256：{h}

Reports：原生渲染、实际漫游及材质预览截图、逐项检查记录。
Source_Metadata：原资料清单、配准依据、保留边界及清理统计。
Sources：处理及检查脚本、保留/移除清单和裁切后改动的扫描网格。
修改后的原生.blend包含全部网格和打包照片，可直接继续编辑。
重放处理脚本需本机V24.36原模型及相应本地Python依赖。

摄影测量树冠内部的遮挡空隙不作为虚构地形填满；本次删除的
是严重拉长破面、残碎外缘和小碎片。保留的完整特征块之间，
人物仍以实际碰撞支撑、坡度与净空判断通行，不能踏入无资料空间。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig');S=O/'Sources';SD=S/'v24_37';SD.mkdir(parents=True,exist_ok=True)
scripts=['export','quality_probe','quality_mask','refine_complete_border','prepare','build','clip_collision','finalize_collision','verify','surface_qa','interior_physics_qa','exterior_physics_qa','measure_math_qa','launcher_smoke','viewport_qa','render','record_visual_review','package']
for name in scripts:
 p=W/('v24_37_'+name+'.py')
 if p.exists():compile(p.read_text('utf8'),str(p),'exec');shutil.copy2(p,S/p.name)
for name in ['v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/name,S/name)
for name in ['Source.json','Source_Scan_Index.json','Final_Scan_Index.json','Cleanup_Report.json','Quality_Plan.json','Before_Snapshot.json','Final_Scan_Retention.geojson','Reviewed_Stretched_Skirt_Exclusion.geojson','Retention_Before_Refine.geojson']:shutil.copy2(D/name,SD/name)
rows=json.loads((D/'Final_Scan_Index.json').read_text())
for row in rows:
 if not row['unchanged']:
  target=SD/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/row['file'],target)
for folder in ['v24_34','v24_36']:
 shutil.copy2(W/folder/'Planned_Routes.json',R/('V24_37_'+folder+'_Tested_Route_Waypoints.json'))
for name in ['North_Skirt_Review.png','Retention_Overlay.png']:
 if(D/name).exists():shutil.copy2(D/name,O/'Source_Metadata'/name)
for name in ['PTJIA6_Registration.json','Coordinate_Seed.json','Filled_Current_Outline.geojson','Decoded_L99_Index.json']:shutil.copy2(W/'v24_36'/name,O/'Source_Metadata'/('PTJIA6_'+name))
shutil.copy2(Path('E:/jz/JIA/Rebuild_V24_35/Reports/V24_35_Repair_QA.json'),R/'Earlier_V24_35_Annotated_Repair_QA.json')
delivery={'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_model_sha256':source['sha256'],'checks':qa,'total_checks':total,'scan_triangles_retained':plan['retained_triangles'],'scan_triangles_retained_percent':percent,'fully_removed_scrap_objects':plan['fully_removed_meshes'],'retained_scan_parts':plan['retained_meshes'],'collision_triangles':ci['all_triangles'],'source_unchanged':True};(R/'V24_37_Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix not in ['.blend1','.blend2']and not p.name.startswith('Draft_')and p.name!='Manifest_SHA256.json'];manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_37_Clean_PTJIA6_Safe_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
 for p in files:z.write(p,Path('Rebuild_V24_37')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,meta in manifest.items():
  with z.open('Rebuild_V24_37/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==meta['sha256'],rel
out={'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'model':str(P),'model_sha256':h,'total_checks':total,'files':len(files)};(D/'Delivery_Result.json').write_text(json.dumps(out,indent=2));print('DELIVERY_VERIFIED',json.dumps(out),flush=True)
