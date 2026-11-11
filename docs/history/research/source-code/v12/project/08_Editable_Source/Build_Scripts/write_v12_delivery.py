"""Finalize an evidence-backed, Rhino-first V12 handover and verified ZIP."""
import sys,json,hashlib,shutil,zipfile,datetime
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V12');OUT=W.parent/'outputs';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
N=read(O/'06_Report/Native_Assembly_QA.json');X=read(O/'06_Report/Modeled_Exchange_QA.json');P=read(O/'07_Reference/Panorama/Extraction_QA.json');assert N['status']==X['status']==P['status']=='PASS'
T=read(O/'07_Reference/v12_terrain/Geometry_QA.json');J=read(O/'07_Reference/v12_terrain/Terrain_Seam_Continuity_QA.json');V=read(O/'06_Report/Visual_Review_V12.json');assert T['status']==J['status']==V['status']=='PASS'
assert read(O/'06_Report/Native_Ground_Shading_QA.json')['status']=='PASS'
assert V['primary_sha256']==N['sha256'] and V['glb_sha256']==X['glb_sha256']
for row in V['images']:assert sha(O/row['file'])==row['sha256']
terrain_area=T['terrain_domain_m2'];terrain_relief=max(T['domain_height_m_range'])-min(T['domain_height_m_range'])
manifest=read(O/'01_Source/Source_Manifest_V12.json');source_checks=[]
audit=read(O/'06_Report/Source_Preservation_QA.json');assert audit['status']=='PASS';audited={row['source']:row for row in audit['sources']}
for row in manifest['sources']:
 p=Path(row['source']);ar=audited[str(p)];st=p.stat();ok=ar['sha256']==row['sha256'] and (st.st_size==ar['bytes'] and st.st_mtime_ns==ar['mtime_ns'] or sha(p)==row['sha256']);source_checks.append(dict(source=str(p),unchanged=ok));assert ok,str(p)
closeups=read(O/'07_Reference/User_Kitchen_Closeups/Reference_Index.json')
for row in closeups['images']:assert sha(Path(row['source']))==row['sha256']
S=read(O/'08_Editable_Source/Architecture_Scene_V12.json');assert not any(e['name'].startswith('PHOTO_') or e.get('family')=='VIS_MODEL' for e in S['elements']);assert not any(e['name'].startswith('CONSTRUCTION_SHED_') for e in S['elements'])
for folder in ['v12_kitchen','v12_terrain','v12_screenwall_reference','v12_final_cleanup']:
 q=read(O/'07_Reference'/folder/'Geometry_QA.json');assert q['status']=='PASS'
sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm'));assert len(F.Objects)==N['objects'];assert len(F.EmbeddedFiles)==N['embedded_files'];textures=[]
for m in F.Materials:
 t=m.GetBitmapTexture()
 if t:
  assert Path(t.FileName).is_file(),t.FileName;textures.append(dict(material=m.Name,file=Path(t.FileName).name))
assert len(textures)==N['pbr_textured_materials'];del F
changes=read(O/'02_Data/V12_Changed_Nodes.json')
for row in changes['sources']:assert sha(W/row['folder']/'Mutation.json')==row['mutation_sha256'],row['folder']
assert sha(O/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm')==N['sha256']
code=O/'08_Editable_Source/Build_Scripts';code.mkdir(exist_ok=True)
for name in ['assemble_v12.py','harmonize_v12_native_ground_normals.py','validate_v12_native.py','blender_v12_modeled.py','verify_v12_exchange.py','verify_v12_fbx.py','verify_v12_sources.py','record_v12_visual_review.py','v12_finishing.py','prepare_v12.py','v12_inventory.py','export_v5.py','write_v12_delivery.py']:shutil.copy2(W/name,code/name)
text=f'''# V12 全建模场地与建筑 · Rhino 主交付

打开 `04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm`。这是完整建筑和新建地形的主模型，单位为米，沿用原 ENU 坐标。材质与纹理已设置并内嵌。Kitchen 和 Terrain 文件是拆出的局部模型，单独检查即可，避免与主模型重复叠加。

## 本次修模

- 厨房以 `before` 最新木构模型为细部参考，结合 INSV 漫游和 10 月 11 日近景调整门窗、回纹、双八角格心、上宽格带/下窄横格、对向抬高的门板弧形压条、露明梁、圆檩和密排椽。清理相交窗棂的共面叠面，将固定门框和活动门扇独立分组。柱脚逐一检查石础承托；保留航拍确认的偏心屋脊、长短两坡和大门高檐/厨房低檐关系。
- 根据同组室内近景补建三叶吊扇、两侧外露灯与中央贴柱线管，保持独立可编辑。扇叶与梁檩已做实体净距检查，安装位置和尺寸按照片关系拟合，尚未现场量测。
- 照壁按原屋面和墙身位置补两端上翘脊饰、瓦当和檐下线脚，原瓦排与墙身范围保留。
- 重建约 {terrain_area:,.0f} 平方米场地为新闭合网格，缺失区域由新几何补齐，主模型不含原倾斜摄影三角面。保留场地约 {terrain_relief:.1f} 米高差，完善外门压槽坡坪和接路过渡面，消除原入口前方土色楔块，统一各地面分块共享边界的标高；衔接主楼三级入口台阶、厨房台基和亭子地台。
- 西侧指定清空区只保留新建地形，删除旧棚屋残留支承裙边。已修正的主楼楼层布局、房间门、楼梯和围墙/亭子关系沿用原模型。
- 木材、瓦、石材、抹灰、混凝土和土面的 PBR 纹理采用实景参考配色与程序生成微纹理。原影像用于比对，主模型未铺回摄影浮片纹理。

## 参考资料

`07_Reference/Panorama` 包含本轮从原 INSV 重新解码的 {P['extracted_views']} 张视图及同一视频此前提取复用的 {P['reused_prior_interior_views']} 张视图，共 {P['total_indexed_views']} 张索引。索引记录原视频哈希、时间、镜头、朝向、输出图哈希和可见性。鱼眼透视视图适合核对构件关系，不用于直接量尺寸。

`07_Reference/Aerial_Inventory.json` 索引 `G:/处理` 的 895 张 JPG、893 张 DNG；按全局屋面和高处细部选择的 32 张原图随包。`Before` 保留原厨房和照壁参考模型；`User_Kitchen_Closeups` 保留最新四张近景。

`04_Rhino/Pure_Site_Cleaned_Ground_REFERENCE_ENU.3dm` 是独立的有效摄影地面参考版，保留原地面 UV 和五张原始贴图，已筛除高处屋面/树体浮影。它用于比对原始高程，**不合并进全建模主模型**。原 INSV 约 22GB，随包提供源路径与哈希，不重复复制。

## 校验和使用

RhinoCommon 8 读回检查全部对象有效，新建/替换的 {N['new_parts_valid_closed']} 个几何部件闭合；对 {N['retained_geometry_crc_checks']} 个保留对象逐一比较原几何 CRC，无差异。厨房、场地、门底净空和纹理检查详见 `06_Report` 与各参考目录的 QA。

工作目录 `05_Export/Complete_Site_V12_LOCAL.glb`、FBX 和 Blender 文件单独提供，使用 LOCAL 米制坐标，材质、UV、门扇枢轴和标识随模型保留；转换回 ENU 使用 `02_Data/Coordinate.json`。Rhino 主 ZIP 包含原生模型、纹理和参考资料，交换文件可从同一工作目录获取。GLB、FBX 已读回核对数量、UV、包内纹理和位置，UE5 中的碰撞、开门蓝图、房间查询和性能尚未实机测试。

FBX 读回的长对象名称可能缩短，完整构件名称保存在父级 `Parameters` 字段，门扇另保留 `door_id`。Rhino 与交换模型统一相邻地面分块顶部的法线，排除闭合网格底面/侧面对顶部阴影的影响；坡道沟槽与侧边保留几何轮廓。地形位置、面片连接与 UV 保持不变。

重建顺序：`v12_finishing.py` → `assemble_v12.py` → `harmonize_v12_native_ground_normals.py` → `validate_v12_native.py`；交换与预览使用 `blender_v12_modeled.py`，随后进行 GLB/FBX 读回核对。

尺寸、高程、坡度及新建隐蔽/缺失处依据参考模型和影像拟合，未完成现场控制测量；文件 1mm 建模公差不能等同于实测毫米精度。示意图中的参考尺寸不作为施工验收依据。后续需实测门窗净尺寸、层高、墙厚、台阶高宽和坡道高差，校准施工使用。
'''
(O/'使用说明.md').write_text(text,encoding='utf8')
Q=dict(status='PASS',primary='04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm',primary_sha256=N['sha256'],objects=N['objects'],new_closed_parts=N['new_parts_valid_closed'],unchanged_native_geometry=N['retained_geometry_crc_checks'],source_files_unchanged=source_checks,source_photogrammetric_triangles_in_primary=0,source_video_extracted_views=P['extracted_views'],all_indexed_views=P['total_indexed_views'],textures_embedded=N['embedded_files'],pbr_textured_materials=N['pbr_textured_materials'],new_nodes=changes['changed'],retired_nodes=changes['removed'],checks=dict(native='PASS',kitchen='PASS',terrain='PASS',terrain_seams='PASS',screenwall='PASS',video='PASS',glb='PASS',fbx='PASS',visual='PASS'),field_measurement_certified=False,ue5_playtested=False)
dump(O/'06_Report/Delivery_QA_V12.json',Q)
# Keep the Rhino-first bundle complete; heavyweight exchange files remain directly accessible beside it.
files=[p for p in O.rglob('*') if p.is_file() and p.name!='Package_File_Manifest.json' and '05_Export' not in p.relative_to(O).parts and '__pycache__' not in p.relative_to(O).parts]
inventory=[dict(file=str(p.relative_to(O)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]
dump(O/'06_Report/Package_File_Manifest.json',dict(files=inventory,exchange_files_separate=['05_Export/Complete_Site_V12_LOCAL.glb','05_Export/Complete_Site_V12_LOCAL.fbx','05_Export/Complete_Site_V12_LOCAL.blend']))
zpath=OUT/'Production_1QK_Rhino_V12_All_Modeled.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for row in inventory:z.write(O/row['file'],arcname='Rebuild_V12/'+row['file'])
 z.write(O/'06_Report/Package_File_Manifest.json',arcname='Rebuild_V12/06_Report/Package_File_Manifest.json')
with zipfile.ZipFile(zpath) as z:
 assert len(z.namelist())==len(inventory)+1;bad=z.testzip();assert bad is None,bad
receipt=dict(status='PASS',zip=str(zpath),bytes=zpath.stat().st_size,files=len(inventory)+1,sha256=sha(zpath),zip_crc_test='PASS',primary_sha256=N['sha256'],delivered_date='2026-10-11');dump(OUT/'V12_Package_Receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False),flush=True)
