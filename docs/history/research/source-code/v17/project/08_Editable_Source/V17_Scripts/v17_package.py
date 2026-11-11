import sys,json,hashlib,struct,zipfile,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V17');P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V17_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P)
F=rh.File3dm.Read(str(P));assert len(F.Objects)==Q['native_objects'];GP=O/'05_Export/Complete_Site_V17_LOCAL.glb'
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));assert ctype==0x4E4F534A;g=json.loads(f.read(length))
assert total==GP.stat().st_size and len(g.get('cameras',[]))==15 and len(g['meshes'])==Q['nodes']
assert len(g['images'])>=5 and all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum('Tile_' in im.get('name','') for im in g['images'])==5
native=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));tri=sum(r['triangles'] for r in native);gtri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==gtri
views=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'))['view_names']
for n in views:assert (O/'06_Report'/f'{n}.png').stat().st_size>10000
AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));mesh_node_names={g['nodes'][n].get('name') for n in range(len(g['nodes'])) if 'mesh' in g['nodes'][n]}
for n in AQ.get('removed_nodes',[]):assert n+'_Geometry' not in mesh_node_names
packqa={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'native_nodes':Q['nodes'],'glb_meshes':len(g['meshes']),'triangles':gtri,'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'native_named_views':[v.Name for v in F.NamedViews],'native_model_sha256':sha(P),'glb_sha256':sha(GP),'ue5_import_tested':False}
(O/'06_Report/Delivery_QA.json').write_text(json.dumps(packqa,ensure_ascii=False,indent=2),encoding='utf8')
readme='''V17 厨房／储藏房转角、木桁架与檐廊修复（2026-10-12）

主文件：04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm，单位米，使用原 ENU 坐标。
05_Export 的 Blender 和 GLB 使用 LOCAL 米坐标，转换见 02_Data/Coordinate.json。
V16 原文件保留，本版另存。

本版内容：
1. 以 DJI_0525、DJI_0526 以及 INSV 中的可辨认关系为参考，删除穿过储藏房重建区域的旧围墙、压顶、花冠和内侧饰面。外边界沿厨房与储藏房真实模型外墙转折。去除外側转角被填高的黄色土楔，在石砌基座下方恢复较低的外侧地面，局部切除残留实景面片，并与原航测切边接合。
2. 储藏房补齐落在石柱础上的木柱、抬梁、短柱、檩条、椽子及檐枋。所有可见木件形成连续实体；屋顶瓦面和厨房屋面交接水沟保持原拟合形状，新木构在交接处裁切收口。
3. 储藏房檐口内设置开敞檐廊和后退的木格扇门窗，保留厨房—内储藏房、内储藏房—外储藏房的连通口。石护栏采用实景可辨认的方头栏柱、下部栏板、上部透空栏杆比例，转角连续，栏板与栏柱接实。新增浅浮雕为简化几何表达，未复制不可辨认的具体纹样。
4. 合并相邻砖墙、木构和石栏的重复接合面，处理墙脚／楼板与石砌基座的共面重叠，消除这些节点的黑缝。石砌基座局部外出 3 mm、外储藏房石基座顶面回退 8 mm，均为模型表面收口值。
5. 入口、主体建筑及三楼等本次未涉及的几何以原生对象哈希核对保留。场地其余排水沟与道路延续 V16，未整体压平外部实景地形。

参考：07_Reference/INSV 保留原抽帧；INSV_Storage 增补 688、705、715 秒双镜头画面。700、705、715 秒木构、门窗和檐廊细节作为做法参考，725 秒可辨认外凸储藏区金属棚。原 INSV：E:/jz/VID_20260507_152114_00_001.insv，时长 1274.7735 秒，已核验 SHA256 为 3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f。

模型尺寸由照片和原模型拟合；檐廊约 1.30 m 的进深、木构截面与护栏比例尚未独立现场测量。抽帧为未标定鱼眼平面投影，不能视为测量照片。低地标高取自保留的实景网格；土体底面和隐藏基座深度仅用于闭合显示，不作为施工或承载力设计。

验证与预览：06_Report/V17_Native_Readback_QA.json 为最后保存的 3DM 回读检查，包括保留对象哈希、闭合体方向、完整 UV／法线、实际网格回读一致性、墙脚与低地高程、木柱—柱础接合、木构／石栏连通性和房间开口。预览与 GLB 来自实际保存模型的网格与材质，GLB 三角形数量对应回读索引，贴图内嵌；未进行 UE5 导入试验。

08_Editable_Source 保留模型几何 JSON、组成部件记录和编辑脚本。脚本是分阶段编辑记录，依赖本机 Python 库、原模型及工作目录，不是可任意重复运行的安装程序。3DM 为最终可编辑主文件。
'''
(O/'README_V17_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
for p in W.glob('v17_*.py'):shutil.copy2(p,O/'08_Editable_Source/V17_Scripts'/p.name)
for p in (W/'v17').glob('*.geojson'):shutil.copy2(p,O/'08_Editable_Source'/p.name)
active={Path(r['file']).as_posix() for r in native};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 rel=p.relative_to(O).as_posix()
 if rel.startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V17','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V17_Storage_Timber_Gallery_Junction.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V17/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert len(z.infolist())==len(files) and z.testzip() is None
bq={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files),'native_model_sha256':packqa['native_model_sha256']};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bq,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bq,ensure_ascii=False),flush=True)
