import sys,json,hashlib,struct,zipfile,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('E:/jz/JIA/Rebuild_V20');P=O/'04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V20_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));GP=O/'05_Export/Complete_Site_V20_LOCAL.glb'
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));g=json.loads(f.read(length));binlen,bintype=struct.unpack('<II',f.read(8));binary=f.read(binlen)
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert total==GP.stat().st_size and len(g['cameras'])==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])==5
I=json.loads((O/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
DM=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'));nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
def quatmat(q):
 x,y,z,w=q;return np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
def matworld(j):
 n=g['nodes'][j]
 if 'matrix' in n:m=np.array(n['matrix']).reshape(4,4).T
 else:
  m=np.eye(4);m[:3,:3]=quatmat(n.get('rotation',[0,0,0,1]))@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0])
 return matworld(parents[j])@m if j in parents else m
def acc(j):
 a=g['accessors'][j];b=g['bufferViews'][a['bufferView']];dtype={5126:np.float32,5125:np.uint32,5123:np.uint16}[a['componentType']];count={'VEC3':3,'VEC2':2,'VEC4':4,'SCALAR':1}[a['type']];return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=b.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,count).astype(float)
doorproof=[]
for r in DM['doors']:
 n=r['name'];j=nodes[n+'_Geometry'];m=matworld(j);vv=np.vstack([acc(p['attributes']['POSITION']) for p in g['meshes'][g['nodes'][j]['mesh']]['primitives']]);vv=np.c_[vv,np.ones(len(vv))]@m.T;local=vv[:,[0,2,1]];local[:,1]*=-1;d=np.load(O/'02_Data'/idx[n]['file']);v=d['vertices'];err=float(np.max(abs(np.array([local.min(0),local.max(0)])-np.array([v.min(0),v.max(0)]))));assert err<1e-5,(n,err);doorproof.append({'node':n,'default_open_bbox_error_m':err})
assert len(g.get('animations',[]))>=len(DM['doors'])-2
for name in V['view_names']:assert (O/'06_Report'/f'{name}.png').stat().st_size>10000
AQ=json.loads((O/'06_Report/V20_Assembly_QA.json').read_text(encoding='utf8'));AQ['status']='PASS_FRESH_NATIVE_V20_QA';(O/'06_Report/V20_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'nodes':len(I),'triangles':tri,'glb_meshes':len(g['meshes']),'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'glb_animations':len(g.get('animations',[])),'independent_inward_door_leaves':len(DM['doors']),'default_open_door_parity':doorproof,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'v19_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
def comparison(name,rows):
 can=Image.new('RGB',(2200,len(rows)*840+100),(246,245,240));dr=ImageDraw.Draw(can)
 for row,pair in enumerate(rows):
  for k,(fp,title) in enumerate(pair):
   im=ImageOps.contain(Image.open(fp).convert('RGB'),(1070,745),Image.Resampling.LANCZOS);can.paste(im,(15+k*1100+(1070-im.width)//2,70+row*840+(745-im.height)//2));dr.text((24+k*1100,20+row*840),title,font=font,fill=(48,46,40))
 dr.text((24,len(rows)*840+35),'右侧为最终保存 3DM 的实际网格；照片拟合尺寸，门内开方向按本次要求设置。',font=small,fill=(60,57,51));can.save(O/'06_Report'/name)
comparison('V20_AsBuilt_Comparison.png',[
 [(O/'07_Reference/V20_AsBuilt/gate_pavilion/INSV_0600s_L0_Y+00_P-20.jpg','实景：主宅入口及亭子位置'),(O/'06_Report/V20_House_Entry_One_Solid_Step.png','V20：实心一阶入口、下部填实')],
 [(O/'07_Reference/V20_AsBuilt/gate_pavilion/INSV_0625s_L1_Y-30_P-20.jpg','实景：靠墙亭子及木平台'),(O/'06_Report/V20_Pavilion_Wood_Deck.png','V20：收回主轴侧，木板底留 5 cm')],
 [(O/'07_Reference/V20_AsBuilt/gate_pavilion/INSV_0657s_L0_Y+00_P+25.jpg','实景：内大门封闭檐底'),(O/'06_Report/V20_Inner_Gate_Closed_Soffit.png','V20：连续檐底、门扇向内打开')]])
comparison('V20_Storage_Comparison.png',[
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 035201.jpg'),'实景：石栏与照壁齐排，留出檐廊入口'),(O/'06_Report/V20_Storage_Aligned_Gallery.png','V20：石栏、廊地板、檐下连续通道')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 035635.jpg'),'实景：正确墙洞位于檐廊尽头'),(O/'06_Report/V20_Storage_Correct_End_Portal.png','V20：正确尽头开口，两处旧错洞封实')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-12 180115.jpg'),'实景：木檐廊及连续石砌台基'),(O/'06_Report/V20_Storage_Exterior.png','V20：齐排石栏、连续石基座和沟路接合')]])
readme='''V20 实景建筑与通行修正（2026-10-13）

主文件：04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm，米单位、原 ENU 坐标。
导出：05_Export/Complete_Site_V20_LOCAL.glb、Actual_Rhino_V20_Readback_LOCAL.blend，LOCAL 米。坐标转换见02_Data/Coordinate.json。V19基线保持原文件完整。

1. 按红框补首层楼梯前隔墙、右后缺墙，保持楼梯右侧和各正确房门通道。二、三层外观相似的开口按实际门路核对，没有盲目封堵其正确通道。三层已确认右卧室补红棕木地面。
2. 原入口三阶改为150mm高单阶实心体，檐廊底部填实；入口邻近庭院地面渐变接至-0.15m，实际保存网格复核拼缝。
3. 亭子墙侧固定，朝主轴一侧回收约0.60m，屋顶、柱、木构、帘、护栏同步调整；取消厚石平台。木板底相对平整后地面留50mm，板厚25mm，木龙骨及小脚支撑。亭子原位置地面补齐并平顺接庭院。
4. 内大门改完整连续浅灰檐底，清除分离椽头与飞椽，保留实景可见的窄线脚、垂花边和曲瓦。照壁及外围V19的实景砖石层次保留并检查与储藏廊连接。
5. 封闭厨储共享墙与东山墙中部的错误洞口，正确洞口在储藏房檐廊尽头，连接外侧薄棚。内部白灰面与外棚灰砖、木桁架分开处理。石栏与照壁y=-16.90m轴线齐排，保留西侧入口，同步延展廊地板、粗石基座、深色石条、南檐及局部前沟路肩。新沟路按原扫描路高程拟合，侵入沟槽的旧路面/沟肩只在局部裁切，外围其它段保留。
6. 活动门扇独立拆分，朝室内开，按墙/框/柱/地面检查铰链位置和开角，默认姿态已打开。外大门按两组外框轴带中间折叠扇内开。固定窗、两侧玻璃和门框保持固定。中央玻璃活动扇按用户内开要求改为内开操作。02_Data/Door_Manifest_V20.json记录每扇LOCAL铰链坐标、朝向、角度和亲子关系。GLB包含内开动画与独立pivot，实际UE导入/交互逻辑尚未运行验证。

建议优先打开Rhino命名视图 V20_Entry_Review、V20_Storage_Gallery_Review，检视一阶入口和檐廊正确洞口。室内预览使用检视照明，所有原生模型几何均保持可见；本地Blender中的检视灯用于看清几何，不代表现场灯具。
UE漫游建议参数见02_Data/UE_Walkthrough_Settings.json：保留独立节点，米转厘米100倍，角色胶囊半径30cm、半高85cm、跨阶20cm，便于通过保留的窄门框和150mm入口阶。参数为建议，导入后的轴向、碰撞及动画仍需在具体UE项目核对。

依据：原始E:/jz/VID_20260507_152114_00_001.insv及航拍、用户批注。新增实景抽帧在07_Reference/V20_AsBuilt，各帧有时间/镜头/视角；以连续漫游核对房间、门洞、檐廊关系。50mm木板净空和内开为用户明确要求，0.60m回收及其它未实测尺寸为实景拟合。

06_Report有保存3DM回读生成的实际预览、实景对照、原生几何/通行验证和导出检查。08_Editable_Source保存几何、修改记录和脚本。依赖原模型/本机运行时的脚本用于编辑记录；可编辑主文件为3DM。
'''
(O/'README_V20_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
for a in ['house','storage','gate_pavilion']:
 td=O/'08_Editable_Source/V20_Scripts'/a;td.mkdir(exist_ok=True)
 for p in (W/f'v20_{a}').iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.npz','.md'] and 'Inventory' not in p.name:
   if p.suffix=='.json':
    data=json.loads(p.read_text(encoding='utf8'));state=data.get('status','') if isinstance(data,dict) else ''
    if state.startswith(('FAIL','MAJOR','NEEDS')):continue
   shutil.copy2(p,td/p.name)
for p in W.glob('v20_*.py'):
 if any(x in p.name for x in ['probe','inventory','prepare_render']):continue
 shutil.copy2(p,O/'08_Editable_Source/V20_Scripts'/p.name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V20','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]};mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';out.mkdir(exist_ok=True);zp=out/'Production_1QK_Rhino_V20_AsBuilt_Architecture_Walkthrough.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V20/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
bundle={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files)};(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle),flush=True)
