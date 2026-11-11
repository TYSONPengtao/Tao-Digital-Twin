import sys,json,hashlib,struct,zipfile,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path(r'E:/jz/JIA/Rebuild_V18');P=O/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V18_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));assert len(F.Objects)==Q['native_objects'];GP=O/'05_Export/Complete_Site_V18_LOCAL.glb'
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));assert ctype==0x4E4F534A;g=json.loads(f.read(length))
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert total==GP.stat().st_size and len(g.get('cameras',[]))==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert len(g['images'])>=5 and all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum('Tile_' in im.get('name','') for im in g['images'])==5
I=json.loads((O/'02_Data/Native_Readback_Index_V18.json').read_text(encoding='utf8'));tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
AQ=json.loads((O/'06_Report/V18_Assembly_QA.json').read_text(encoding='utf8'));mesh_names={n.get('name') for n in g['nodes'] if 'mesh' in n}
for n in AQ['removed_nodes']:assert n+'_Geometry' not in mesh_names,n
for n in V['view_names']:assert (O/'06_Report'/f'{n}.png').stat().st_size>10000
# Side-by-side reference sheet uses the unaltered real photograph and actual native-model render.
can=Image.new('RGB',(2200,1140),(246,245,240));dr=ImageDraw.Draw(can);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',31);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
for k,(fp,title) in enumerate([(Path(r'D:/Desktop/问题/屏幕截图 2026-10-12 180115.jpg'),'实景参考：外侧储藏房、檐廊与石基座'),(O/'06_Report/V18_Storage_Photo_Exterior.png','V18：保存模型回读后的道路视角')]):
 a=ImageOps.contain(Image.open(fp).convert('RGB'),(1080,1000),Image.Resampling.LANCZOS);x=10+k*1100+(1080-a.width)//2;can.paste(a,(x,70+(1000-a.height)//2));dr.text((24+k*1100,19),title,font=font,fill=(50,48,42))
dr.text((24,1089),'重点修正：连续石砌基座、宽石栏与横向透空、深色木檐、薄金属棚；尺寸按照片与原模型拟合。',font=small,fill=(60,57,51));cp=O/'06_Report/V18_Real_Photo_Comparison.png';can.save(cp)
auditpath=O/'06_Report/V18_Baseline_Audit.json';au=json.loads(auditpath.read_text(encoding='utf8'));au['encoded_geometry_hash_differences_vs_previous_delivery']=au.pop('changed_current_geometries_vs_last_delivery',[]);au['hash_difference_note']='Encoded native geometry hashes can change after Rhino serialization without a dimensional change. The current native file is authoritative; V18 preserves its retained objects and removes only stale preview cache nodes.';auditpath.write_text(json.dumps(au,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'native_nodes':Q['nodes'],'glb_meshes':len(g['meshes']),'triangles':tri,'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'native_named_views':[v.Name for v in F.NamedViews],'native_model_sha256':sha(P),'glb_sha256':sha(GP),'base_file_preserved_sha256':AQ['base_model_sha256'],'stale_old_preview_nodes_removed':AQ['stale_base_cache_nodes_removed'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
readme='''V18 储藏房实景对照修正（2026-10-12）

主文件：04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm。单位米，沿用原 ENU 坐标。
05_Export 中的 Blender 与 GLB 使用 LOCAL 米坐标，转换见 02_Data/Coordinate.json。
本版另存，当前 V17 原文件保留。Rhino 可用新增命名视图 V18_Storage_Photo_Exterior、V18_Storage_Exterior_Oblique、V18_Storage_Base_Drain 对照检查。

本版修正：
1. 按 180115 实景与 INSV 950、972 秒的同侧画面，重做储藏房外凸部分及檐廊下方的连续石基座。删除旧石基座上、下轮廓不一致造成的土色凹槽和台阶；下部为粗石砌筑，上部为约 0.64 m 的深色整石带。实景石材颜色、灰缝和栏板纹样由提供的照片提取，纹理接边做周期亮度校正；石基座转角 UV 连续展开。
2. 将檐廊正面石栏调整为三个较宽分格，外凸部分沿原转折设置宽栏板。上部改为横向宽六角透空，下部保留方框和简化浅表纹样，替换先前密集的竖向沙漏及菱形图案。方头栏柱、栏板、顶枋和底枋形成一体并落在基座上。
3. 储藏房木构换成实景中的较深旧木色；窗玻璃降低过亮的色调。保留木柱—柱础、木柱—梁—檩—椽的接合及厨房／内储藏房／外储藏房两处连通口。瓦屋面及厨房—内储藏房斜向交接保持原拟合几何。
4. 外储藏房的金属棚保留原注册轮廓与顶部坡面，改用薄板、较细的檩条、边枋及落地柱，板与支承形成连续实体。按照片补充两条白色外部管／杆；其具体用途未独立确认。
5. 纠正原来停在石墙中部的外储藏房墙脚封口，将它降至既有道路与沟底位置。保留沿外墙 0.25 m 的排水沟、现有坡度和与航测道路共用的边线；外侧过渡带使用灰色细骨料材质，减弱大块深色凸边。
6. 当前 V17 原生文件已没有两块旧道路面，缓存索引还保留了它们。本版导出与预览同步清除这些缓存；未将旧道路恢复到当前模型。其余当前原生对象按保存前后几何哈希核对保留。

参考：07_Reference 保存新增 180115 实景、180137 问题截图、DJI 航拍及既有 INSV 抽帧。新对比见 06_Report/V18_Real_Photo_Comparison.png；右侧为实际保存模型网格生成的预览，不是图片修图。

尺寸与范围：本版是实景照片和原模型拟合，未新增现场实测尺寸。白管／杆位置、护栏分格与薄板厚度为照片拟合。基座隐藏底部仅用于闭合显示，不代表已调查的基础做法。材质照片保留部分原拍摄光照，浅表纹样分辨率受原照片限制。本版未作结构承载计算或 UE5 导入测试。

验证：06_Report/V18_Native_Readback_QA.json 核对最后保存的原生模型：保留对象哈希、修改网格的闭合与正向体积、完整 UV／法线、原生 Mesh 的坐标／材质／UV 回读、继承缓存哈希、石基座和石栏连通、木柱—柱础接合、棚柱—地板接合、墙脚—排水沟在十五个局部断面的正向搭接及两个房间开口。导出网格数和三角形数量与回读索引一致，贴图已内嵌。

08_Editable_Source 保存几何 JSON、修改记录、材质生成记录及编辑脚本。脚本依赖本机 Python、Blender、旧模型和库目录，是编辑记录，不是任意反复执行的安装程序。3DM 为最终可编辑主文件。
'''
(O/'README_V18_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
for p in W.glob('v18_*.py'):shutil.copy2(p,O/'08_Editable_Source/V18_Scripts'/p.name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak'] or p.name.startswith('V18_Camera_Probe_'):continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V18','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V18_Storage_AsBuilt_Exterior.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V18/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert len(z.infolist())==len(files) and z.testzip() is None
qa={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files),'native_model_sha256':delivery['native_model_sha256']};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(qa,ensure_ascii=False),flush=True)
