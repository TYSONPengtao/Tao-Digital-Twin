import sys,json,hashlib,struct,zipfile,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path(r'E:/jz/JIA/Rebuild_V19');P=O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V19_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));assert len(F.Objects)==Q['native_objects'];GP=O/'05_Export/Complete_Site_V19_LOCAL.glb'
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));assert ctype==0x4E4F534A;g=json.loads(f.read(length))
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert total==GP.stat().st_size and len(g.get('cameras',[]))==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert len(g['images'])>=5 and all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])==5
I=json.loads((O/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I);AQ=json.loads((O/'06_Report/V19_Assembly_QA.json').read_text(encoding='utf8'));mesh_names={n.get('name') for n in g['nodes'] if 'mesh' in n}
for n in AQ['removed_nodes']:assert n+'_Geometry' not in mesh_names,n
for n in V['view_names']:assert (O/'06_Report'/f'{n}.png').stat().st_size>10000
AQ['status']='PASS_FRESH_NATIVE_PERIMETER_QA';(O/'06_Report/V19_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);can=Image.new('RGB',(2200,1800),(246,245,240));dr=ImageDraw.Draw(can)
rows=[[(O/'07_Reference/INSV_Perimeter/INSV_0935s_L1_Y+45_P+15.jpg','实景：同次漫游的照壁与石砌基座'),(O/'06_Report/V19_Perimeter_Screenwall_Road.png','V19：保存模型回读后的照壁外侧')],[(O/'07_Reference/INSV_Perimeter/INSV_0890s_L1_Y+50_P+05.jpg','实景：14 分 50 秒围墙沿道路视角'),(O/'06_Report/V19_Perimeter_Ordinary_South.png','V19：灰砖、浅色框带和实心瓦压顶')]]
for row,pair in enumerate(rows):
 for k,(fp,title) in enumerate(pair):
  im=ImageOps.contain(Image.open(fp).convert('RGB'),(1070,780),Image.Resampling.LANCZOS);can.paste(im,(15+k*1100+(1070-im.width)//2,80+row*850+(780-im.height)//2));dr.text((24+k*1100,23+row*850),title,font=font,fill=(48,46,40))
dr.text((24,1742),'按实景与原墙线拟合；右侧来自最终 3DM 的实际网格。各视角保留原实景场地模型。',font=small,fill=(60,57,51));cp=O/'06_Report/V19_Perimeter_Real_Photo_Comparison.png';can.save(cp)
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'native_nodes':Q['nodes'],'glb_meshes':len(g['meshes']),'triangles':tri,'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'native_named_views':[v.Name for v in F.NamedViews],'native_model_sha256':sha(P),'glb_sha256':sha(GP),'base_file_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
readme='''V19 外围围墙实景修正（2026-10-12）

主文件：04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm。单位米，沿用原 ENU 坐标。
05_Export 的 Blender 和 GLB 使用 LOCAL 米坐标；转换见 02_Data/Coordinate.json。
本版另存，当前 V18 原文件保持完整。

参考：以用户指定的 E:/jz/VID_20260507_152114_00_001.insv 第 14 分 50 秒（890 秒）为锚点，读取同一段连续外墙漫游。07_Reference/INSV_Perimeter 保存原双镜头抽帧、朝向截取和时间索引，870—972 秒的连续视角用于核对墙体层次、照壁和储藏房连接。935 秒可见完整照壁外侧；DJI_0073 用于复核普通墙顶。不同朝向均有镜头编号、时间、偏航和俯仰记录。原视频未被修改。

本版修正：
1. 外围墙保留注册墙线、原挡土高度、外大门位置及通行开口。将下部按粗石砌基座、深色规则石条带（拟合约 0.56 m）、上部灰砖分层。灰砖和整石表面由真实漫游帧提取，校正拍摄透视和贴图接边；毛石与 V18 储藏房基座统一。沿墙展开纹理，减弱先前规整假砖和材质断裂。
2. 普通围墙的外侧檐下改为窄浅色带，保留实际墙线上的长短阶形边框；内侧保持白色墙面。按视频重做照壁上部：灰砖连续延伸至弯曲瓦顶，删除原来突出的大片空白白色墙板。上部墙体沿下部墙线定位，与下墙和保留瓦顶有实体搭接。
3. 照壁檐下采用四个长框、三个短框交替排列。框带和边框的面按墙线及弯曲檐口逐段细分，防止大对角面跨过弧形轮廓而造成悬离。
   清除旧照壁中部留下的普通墙檐带，使灰砖从石基座连续到上部框带。西北转角按两条现有墙线的交点补齐石基座、石条和砖墙收口，约 2 mm 的搭接用于闭合接头；侧面贴图改按实际面方向展开，消除被挤成竖条的纹理。
4. 普通墙顶采用实心低瓦脊，删除全周未经实景确认的花形透空冠带。保留专门照壁上原有的拟合曲瓦、边饰及端部形态。普通瓦件下移约 7 mm，瓦底层下移约 2 mm，脊底下伸约 30 mm，以形成明确落座。清理旧裁切产生的零体积薄片及不受支承的小瓦尖；主要压顶段逐个检查实体支承。
5. 外墙脚与排水沟采用 V18 的闭合几何，保留沟宽、纵坡、道路航测边线。沟体直接复制 V18 原生网格，包括其内腔和既有贴图坐标；沟体及道路过渡带统一为灰色细骨料混凝土表面，墙脚使用对应石材。重新检查沿外围墙各处墙脚—沟体的实体搭接。
6. 储藏房石基座、石栏、木桁架、薄金属棚，厨房—内储藏房屋顶交接及主体建筑均继承当前 V18 的几何，保存后核对保留对象的几何哈希。

Rhino 新命名视图：V19_Perimeter_Screenwall_Road、V19_Perimeter_Ordinary_South、V19_Perimeter_West_Road、V19_Perimeter_Northwest_Corner、V19_Perimeter_Coping_Detail、V19_Perimeter_Storage_Junction。06_Report 中有实际保存模型网格生成的道路视角、压顶细节、总图及俯视图；实景对比图为未改动的实景帧与模型预览并排。

验证：V19_Native_Readback_QA.json 核对最后保存的 3DM：保留对象哈希、删除对象、修改网格的有效性与闭合、正向体积、完整 UV／单位法线、原生网格与缓存的坐标／UV／材质逐项一致、主要瓦压顶落座、装饰面支承、照壁上部与瓦顶接合、保留挡土外形及排水沟几何、墙脚—沟体的局部接合。Delivery_QA.json 核对导出网格与三角形数量、相机和嵌入贴图。

范围：各尺寸根据实景和注册模型拟合，未增加现场实测尺寸。隐蔽基础的封口仍属于显示闭合。航测植被和模型外缘的原始缺面不在本次围墙修正范围。没有进行结构承载计算或 UE5 导入测试。

08_Editable_Source 保存几何 JSON、修改记录、材质与编辑脚本；脚本依赖本机库、旧模型和指定运行时，是编辑记录。最终可编辑主文件为 3DM。
'''
(O/'README_V19_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
for p in W.glob('v19_*.py'):
 if any(s in p.name for s in ['probe','prepare_render']):continue
 shutil.copy2(p,O/'08_Editable_Source/V19_Scripts'/p.name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak'] or p.name.startswith('V19_Camera_Probe_'):continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V19','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V19_Perimeter_AsBuilt_Walls.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V19/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert len(z.infolist())==len(files) and z.testzip() is None
qa={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files),'native_model_sha256':delivery['native_model_sha256']};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(qa,ensure_ascii=False),flush=True)
