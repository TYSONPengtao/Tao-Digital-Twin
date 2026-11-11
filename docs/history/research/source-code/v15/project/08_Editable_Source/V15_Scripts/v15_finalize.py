import sys,json,math,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs']]
import numpy as np,rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V15');B=Path(r'E:/jz/JIA/Rebuild_V14');P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for tab in [F.NamedViews,F.Views]:
 for v in tab:
  if v.Name.startswith(('V12_','V13_','V14_')):v.Name='V15_'+v.Name.split('_',1)[1]
for name,pos,tar in [('V15_Inner_Gate',[6.55,-15.4,1.8],[6.55,-11.75,1.95]),('V15_Entry_Route',[-10,-11.22,1.3],[6.6,-11.95,1.0]),('V15_F3_Bedroom',[11.4,3.4,8.7],[9.3,1.35,7.75]),('V15_Exterior_Wall',[27,-24,4.8],[18,-13.2,1.2])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
paths=set()
for m in F.Materials:
 for get in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,get)()
  if tx:paths.add(Path(tx.FileName))
embedded=[];already={ef.Filename for ef in F.EmbeddedFiles}
for p in sorted(paths):
 assert p.exists(),p
 if 'Original_Exterior' not in str(p):
  if str(p) not in already:F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(p)))
  embedded.append({'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
S=json.loads((O/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'));md=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
for n in S['materials']:
 if n in md:S['materials'][n]['native_bitmap']=md[n]['native_bitmap'];S['materials'][n]['native_bump']=md[n]['native_bump']
sp=O/'08_Editable_Source/Architecture_Scene_V15.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V15_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V15_Status']='Mesh UV and normals verified; closed orientations repaired; continuous entrance pavement with contacting fill; no porch roof in F3 bedroom; INSV source relationships and grey carved inner gate fitted. Material texture display reviewed; no force-capacity calculation.';assert F.Write(str(P),8);sha=hashlib.sha256(P.read_bytes()).hexdigest()
q=json.loads((O/'06_Report/V15_Native_Readback_QA.json').read_text(encoding='utf8'));q['sha256']=sha;q['final_metadata']='Named inspection views, material paths and embedded texture bytes finalized; geometric objects unchanged after native readback.';(O/'06_Report/V15_Native_Readback_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
aq=json.loads((O/'06_Report/V15_Assembly_QA.json').read_text(encoding='utf8'));aq['status']='PASS_NATIVE_READBACK_UV_ROUTE_AND_BEDROOM';aq['sha256']=sha;(O/'06_Report/V15_Assembly_QA.json').write_text(json.dumps(aq,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/Embedded_Texture_Index.json').write_text(json.dumps(embedded,ensure_ascii=False,indent=2),encoding='utf8')
for n in ['Geometry_QA.json','Route_Probe.json']:shutil.copy2(W/'v15'/n,O/'06_Report'/n)
shutil.copy2(W/'v15/Mutation.json',O/'08_Editable_Source/Mutation_V15.json')
shutil.copytree(B/'07_Reference/MP4',O/'07_Reference/MP4_V14_Supplement',dirs_exist_ok=True)
for n in ['DJI_0525.JPG','DJI_0526.JPG','Pure_Site_Source.3dm']:
 if (B/'07_Reference'/n).exists():shutil.copy2(B/'07_Reference'/n,O/'07_Reference'/n)
for root,names in [(Path(r'D:/Desktop/问题'),['002422','002455','002534','003632','002742','002727']),(Path(r'D:/Desktop'),['070323','070357','070444','070514','071105','071212','071526'])]:
 for n in names:
  pp=root/f'屏幕截图 2026-10-12 {n}.jpg'
  if pp.exists():shutil.copy2(pp,O/'07_Reference'/pp.name)
scripts=O/'08_Editable_Source/V15_Scripts';scripts.mkdir(exist_ok=True)
for n in ['v15_reference.py','v15_geometry.py','v15_assemble.py','v15_subgrade.py','v15_readback.py','v15_final_qa.py','v15_materials_fix.py','v15_tree_pit.py','v15_ground_overlap.py','v15_lower_support.py','v15_overlap_verify.py','v15_make_renderer.py','v15_render_native.py','v15_finalize.py','v15_package.py']:shutil.copy2(W/n,scripts/n)
readme='''V15 修模说明（2026-10-12）

主文件：04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm，单位米，保留原 ENU 测量坐标。
05_Export 的 GLB 与 Blender 文件使用 LOCAL 米坐标，转换见 02_Data/Coordinate.json。

本版修正：
• 给重建网格写入完整 UV 和单位法线，修复缺少贴图坐标的黑面；硬墙面使用分离面法线，修正 16 个朝内封闭网格。旧灰砖、石材、抹灰贴图中的斜纹场也已替换。入口处新路面与旧地坪重面已布尔清除，储藏房范围内 24 处墙基顶面从 -0.40 m 降至 -0.55 m，使其处于完成楼板下面。
• 外大门至内大门增加连续混凝土路面与下方填土，保留原外大门坡道和内院地坪高差；已有树位保留，在路面内留 0.40 m 半径树池并补根部土面。按路线 0.20 m 采样，模型没有路线缺口；路面下表面与填土顶面接触。渐变高程来源于原模型标高控制与影像辨识，未现场复测。
• 围墙外侧灰砖、内侧白色抹灰分开建模；清除墙体附近 4247 个重复的原航测竖向面片。原始“纯场地版本.3dm”文件未改写，其余外围道路、邻房和植被沿用原来源。
• 裁去侵入三楼右卧室的二楼门廊瓦顶和筒瓦。三楼转折过道和内凹区域参考 INSV 160、232、235、265、268 秒的影像保留，避免把真实通道封成墙。照片未提供可推导的准确米制门洞偏移，本版保持 V14 已校正的通行门位。
• 按实景内大门调整过高的檐下空白体块，细化灰色倒角门柱、框式浅浮雕、木门上槛、五金和有吊绳连接的灯笼。石雕为简化建模，未声称复刻全部雕刻细节。
• 延续 V14 的厨房—内储藏房斜向屋面交接、瓦檐下的金属外储藏棚顶，以及三楼通向阳台的有楼板支承通道。

参考依据：原 INSV 是 1274.7735 秒、两路 3840×3840 鱼眼视频，SHA256 为 3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f。V15 从原文件重新抽取 22 个检视图，覆盖三楼、道路和内外储藏房；07_Reference/INSV 内有时间、镜头、投影和图片校验值。未标定鱼眼视图用于辨认关系，不作为尺寸测量。V14 的 64 秒 MP4 为补充参考，未将其当成整段 INSV。

验证：06_Report 有实际 3DM 回读、UV/法线、道路高程与路面填土接触、卧室屋顶排除检查。变化后的网格直接读取保存文件；未改动 Brep/块经哈希证明后复用先前原生内核网格。少量仅修 UV 的混合 Mesh/Brep 组，另证明网格三角形坐标与 Brep 哈希不变后复用既有内核网格，详见 V15_Mixed_Group_Readback.json。本次未运行新的 RhinoCommon 曲面内核或结构承载力验算。

预览使用保存模型中的贴图与 UV。室内检视附加的灯光和侧廊两片暂时隐藏的门扇仅用于看清构造，3DM/GLB 保留门扇，未将检视灯当作实景灯具。材质是依据实景外观生成的参数化灰砖、毛石、抹灰表面；不是对相机曝光和现场色彩的精确还原。
脚本依赖本机 V14 项目、Python 库及 Blender，不是无依赖安装包。保留 V14，避免覆盖上一版。
'''
(O/'README_V15_请先阅读.txt').write_text(readme,encoding='utf-8-sig');print('FINALIZED',sha,len(F.Objects),'embedded',len(embedded),flush=True)
