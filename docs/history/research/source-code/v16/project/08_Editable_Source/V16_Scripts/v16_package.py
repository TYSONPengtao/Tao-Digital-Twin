import sys,json,hashlib,struct,zipfile,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V16');P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V16_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P)
F=rh.File3dm.Read(str(P));assert len(F.Objects)==Q['native_objects'];views=[v.Name for v in F.NamedViews];assert 'V16_West_Wall_Drain' in views and 'V16_Screenwall_Inside' in views
GP=O/'05_Export/Complete_Site_V16_LOCAL.glb'
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));assert ctype==0x4E4F534A;g=json.loads(f.read(length))
assert total==GP.stat().st_size and len(g.get('cameras',[]))==8 and len(g['meshes'])==Q['nodes']
assert len(g['images'])>=5 and all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum('Tile_' in im.get('name','') for im in g['images'])==5
native=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));tri=sum(r['triangles'] for r in native);gtri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==gtri
previews=['Whole_Site','Top','Graded_Courtyard','Screenwall_Inside','West_Wall_Drain','South_Wall_Drain','Outer_Storage_Base','Entry_Route']
for name in previews:assert (O/'06_Report'/f'V16_Native_{name}.png').stat().st_size>10000
packqa={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'native_nodes':Q['nodes'],'glb_meshes':len(g['meshes']),'triangles':gtri,'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'named_views':views,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'ue5_import_tested':False}
(O/'06_Report/Delivery_QA.json').write_text(json.dumps(packqa,ensure_ascii=False,indent=2),encoding='utf8')
readme='''V16 场地与墙脚排水沟修复（2026-10-12）

主文件：04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm，单位米，保持原 ENU 坐标。
05_Export 的 Blender 与 GLB 使用 LOCAL 米坐标，转换见 02_Data/Coordinate.json。

本版修复：
1. 合并重建黄色土面的旧碎片，重新生成完整连续土体，补齐院内旧地形缺面。主要土面设为约 -0.48 m，西侧保留 0.4% 的缓坡；邻近入口坡道与既有道路，在 3 m 范围内柔和衔接。照壁内侧沿墙填平旧模型多米深的凹沟。旧路面与庭院地坪转角约 24 mm 宽、54 mm 高的接合处采用有土体支承的石材实体收口，避免陡斜土面。去除会形成假沟纹的旧土面贴图，改为细颗粒土质表面。
2. 按原 INSV 749、775、950、972 秒可辨认的墙边关系，建模补齐外墙脚、窄排水沟、沟底及路肩，墙脚闭合体与既有墙底重叠接实。保留排水沟的凹槽和道路原有高差。外储藏房凸出部分墙脚同步接到外围地面。
3. 仅裁切墙脚连接带内的旧实景网格，保留原贴图与 UV；沟口处新建道路边线与实景道路切边使用同一高程线，并在外侧 0.35 m 内过渡。包含倾斜扫描沟壁在内的边界顶点已接到同一条线，避免露白裂口。
4. 入口坡道、台阶、树池、主体建筑、三楼及屋面延续 V15，几何经完整哈希核对保持不变。V15 原文件保留。

验证：实际保存 3DM 回读，核对 20659 个保留对象几何哈希、新增/改动网格的坐标、UV、法线、闭合体方向；土面与道路没有重复顶面，树池保留，照壁土面连续；墙脚道路交界顶点高程误差小于 2 mm。详见 06_Report。预览来自实际 3DM 网格与材质，GLB 三角形数量与回读数据一致，贴图内嵌。

本次标高和沟槽尺寸为模型拟合值，未独立现场复测。土体 -4.80 m 的底面及墙脚向下封闭用于模型完整显示，不作为基础施工图。保留真实道路坡度；未进行水力计算或结构承载力验算。
原 INSV SHA256：3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f，时长 1274.7735 秒。07_Reference/INSV 中保留抽帧的时间与源文件校验记录。
保留 Brep/块的预览使用 V15 已核对的原生内核网格，新改网格直接回读；本次没有新运行 RhinoCommon 曲面内核。
脚本依赖本机项目和 Python 库，不是无依赖安装程序。
'''
(O/'README_V16_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
for p in W.glob('v16_*.py'):shutil.copy2(p,O/'08_Editable_Source/V16_Scripts'/p.name)
for p in (W/'v16').glob('*.json'):
 if p.name!='Probe.json':shutil.copy2(p,O/'08_Editable_Source'/p.name)
active={Path(r['file']).as_posix() for r in native};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 rel=p.relative_to(O).as_posix()
 if rel.startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V16','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V16_Ground_Drain_Fixes.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V16/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert len(z.infolist())==len(files) and z.testzip() is None
bq={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files),'native_model_sha256':packqa['native_model_sha256']};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bq,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bq,ensure_ascii=False),flush=True)
