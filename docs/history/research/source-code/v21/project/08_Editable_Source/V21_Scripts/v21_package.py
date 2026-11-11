import sys,json,hashlib,struct,zipfile,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('E:/jz/JIA/Rebuild_V21');P=O/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V21_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));GP=O/'05_Export/Complete_Site_V21_LOCAL.glb'
door_qa=json.loads((O/'06_Report/Final_Native_Door_QA.json').read_text(encoding='utf8'));assert door_qa['status'].startswith('PASS') and not door_qa['unresolved_collisions']
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));g=json.loads(f.read(length));binlen,bintype=struct.unpack('<II',f.read(8));binary=f.read(binlen)
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert V['native_model_sha256']==Q['sha256'];assert total==GP.stat().st_size and len(g['cameras'])==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])==5
I=json.loads((O/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
DM=json.loads((O/'02_Data/Door_Manifest_V21.json').read_text(encoding='utf8'));nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
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
AQ=json.loads((O/'06_Report/V21_Assembly_QA.json').read_text(encoding='utf8'));AQ['status']='PASS_FRESH_NATIVE_V21_QA';(O/'06_Report/V21_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'nodes':len(I),'triangles':tri,'glb_meshes':len(g['meshes']),'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'glb_animations':len(g.get('animations',[])),'independent_door_leaves':len(DM['doors']),'sliding_leaves':sum(r.get('operation')=='SLIDING' for r in DM['doors']),'default_open_door_parity':doorproof,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'v20_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
def comparison(name,rows):
 can=Image.new('RGB',(2200,len(rows)*840+100),(246,245,240));dr=ImageDraw.Draw(can)
 for row,pair in enumerate(rows):
  for k,(fp,title) in enumerate(pair):
   im=ImageOps.contain(Image.open(fp).convert('RGB'),(1070,745),Image.Resampling.LANCZOS);can.paste(im,(15+k*1100+(1070-im.width)//2,70+row*840+(745-im.height)//2));dr.text((24+k*1100,20+row*840),title,font=font,fill=(48,46,40))
 dr.text((24,len(rows)*840+35),'右侧为最终保存 3DM 的实际网格；照片拟合尺寸，楼房入口为推拉，其余活动门内开。',font=small,fill=(60,57,51));can.save(O/'06_Report'/name)

comparison('V21_House_Comparison.png',[
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 150915.jpg'),'批注：三层卧室门位置错误'),(O/'06_Report/V21_F3_Corrected_Door_Landing.png','V21：旧洞封实，门移至柱子另一侧')],
 [(Path('D:/Desktop/问题/download.jfif'),'实景：三层晾晒檐廊入口与墙面'),(O/'06_Report/V21_F3_Doorless_Terrace.png','V21：白色无门扇入口、矩形饰面砖')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 150622.jpg'),'实景扫描：灰白色楼房外墙'),(O/'06_Report/V21_House_Rear_Facade.png','V21：按原洞口范围修正背面与侧面外墙')]])
comparison('V21_Gate_Comparison.png',[
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-12 002727.jpg'),'实景：内大门比例、门柱与屋檐'),(O/'06_Report/V21_Inner_Gate_Reference_Front.png','V21：采用指定分层模型重整内大门')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 151254.jpg'),'批注：内门与厨房间多余饰墙'),(O/'06_Report/V21_Inner_Gate_Kitchen_Flush_Junction.png','V21：去掉多余饰墙，接缝平齐')],
 [(O/'07_Reference/V20_AsBuilt/gate_pavilion/INSV_0657s_L0_Y+00_P+25.jpg','实景抽帧：连续封闭檐底'),(O/'06_Report/V21_Inner_Gate_Reference_Underside.png','V21：修复模型薄片，补连续檐底')]])
comparison('V21_Gallery_Comparison.png',[
 [(W/'v21_site/Reference/INSV_1036s_L0_Y+00_P-10.jpg','实景抽帧：厨房檐廊与地面'),(O/'06_Report/V21_Kitchen_Gallery_Paving.png','V21：灰褐石板，保持原地面标高')],
 [(W/'v21_site/Reference/INSV_0710s_L0_Y+00_P+00.jpg','实景抽帧：储藏房木构与窗棂'),(O/'06_Report/V21_Storage_Front_Fretwork.png','V21：连续木构、双层八角与回字窗棂')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 035201.jpg'),'实景批注：储藏房檐廊与石栏位置'),(O/'06_Report/V21_Storage_Gallery_Detail.png','V21：廊面与端部通道')]])
readme="""V21 实景继续校正（2026-10-14）

主模型：04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm。Rhino 8，米，原 ENU 坐标。
漫游资产：05_Export/Complete_Site_V21_LOCAL.glb。可编辑检视场景：Actual_Rhino_V21_Readback_LOCAL.blend。两者 LOCAL 米，变换见02_Data/Coordinate.json。V20 原文件保留。

本轮修改依据：原始 VID_20260507_152114_00_001.insv 的新抽帧、用户10月13日15时批注及指定内大门原生模型。新抽帧和来源记录位于07_Reference/V21_AsBuilt；各部位设计判断、参考时间、拟合尺寸及未测量项记录于06_Report及08_Editable_Source/V21_Scripts。

内大门：按指定“内大门_实景复原_分层可编辑_Rhino8.3dm”的分层构件重新安置，统一毫米到米。保存来源对象对应关系；薄片构件加厚，檐底封闭。清理厨房侧多余饰墙、花砖和旧门楼重叠构件，校核门柱与厨房山墙接面。尺寸为既有场地与实景拟合，不是实测施工尺寸。
三层楼房：三层卧室门移到柱子南侧、靠书房门处，原错误洞口填实；移除通往晾晒檐廊的虚构木门和木门套，按实景保留白色通行洞口、矩形灰白砖墙。背面及侧面外墙修正为灰白色，保留实际窗洞及室内墙面。已补的首层红框缺墙和实心一阶入口保留并检查。
檐廊：按视频修正储藏房回字形窗棂及旧木色；厨房灰褐石板与储藏房灰米色水泥廊面分别处理。保留照壁齐排石栏、檐廊端部正确开口、亭子回收位置与木板底50mm净空，并复核相关支撑与接缝。
门：进入楼房的前玻璃门恢复两侧平移推拉，门框及固定侧玻璃不动；其余有门扇的通行口保留向内开。取消实景没有门扇的檐廊洞口虚构门。独立节点、铰链/平移量、开启方向与父子关系见02_Data/Door_Manifest_V21.json，GLB默认开启且含平移/内开动画。

请先打开06_Report中的实景对照图和对应命名视图。所有预览由最终保存3DM的回读网格生成，保留模型几何可见；室内检视灯只用于看清构件，不代表现场灯具。3DM及缓存、GLB的数值复核报告同时交付。
UE：保留节点层级和独立活动门，长度米转厘米100倍。02_Data/UE_Walkthrough_Settings.json提供胶囊/碰撞建议；实际UE项目导入、碰撞烘焙与交互逻辑尚未测试，不能将本地网格检查等同于引擎运行通过。
"""
(O/'README_V21_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
settings=json.loads((Path('E:/jz/JIA/Rebuild_V20')/'02_Data/UE_Walkthrough_Settings.json').read_text(encoding='utf8'))
settings.update(asset='05_Export/Complete_Site_V21_LOCAL.glb',default_door_pose='OPEN; main-house front glazing SLIDING, other moving leaves HINGED_INWARD',door_manifest='02_Data/Door_Manifest_V21.json')
(O/'02_Data/UE_Walkthrough_Settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf8')
for a in ['house','gate','site']:
 td=O/'08_Editable_Source/V21_Scripts'/a;td.mkdir(parents=True,exist_ok=True)
 ref=W/f'v21_{a}'/'Reference'
 if ref.exists():shutil.copytree(ref,O/'07_Reference/V21_AsBuilt'/a,dirs_exist_ok=True)
 for p in (W/f'v21_{a}').iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.npz','.md'] and 'Inventory' not in p.name:
   if p.suffix=='.json':
    data=json.loads(p.read_text(encoding='utf8'));state=data.get('status','') if isinstance(data,dict) else ''
    if state.startswith(('FAIL','MAJOR','NEEDS','DESIGN_WRITTEN')):continue
   shutil.copy2(p,td/p.name)
 for name in ['Design_Control.json','QA.json','Final_Native_QA.json','Preview_Review.json','House_QA.json','House_Native_QA.json','Source_QA.json','Final_Native_Review.json','Final_Review.json']:
  p=W/f'v21_{a}'/name
  if p.exists():shutil.copy2(p,O/'06_Report'/f'{a}_{name}')
for p in W.glob('v21_*.py'):
 if 'prepare_' in p.name:continue
 shutil.copy2(p,O/'08_Editable_Source/V21_Scripts'/p.name)
src=Path('E:/CODEXdata/before/内大门/内大门_实景复原_分层可编辑_Rhino8.3dm');dst=O/'07_Reference/V21_AsBuilt/Inner_Gate_Source';dst.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst/src.name)
userref=O/'07_Reference/V21_AsBuilt/User_Annotations';userref.mkdir(parents=True,exist_ok=True)
for name in ['屏幕截图 2026-10-13 150455.jpg','屏幕截图 2026-10-13 150622.jpg','屏幕截图 2026-10-13 033747.jpg','屏幕截图 2026-10-13 033535.jpg','屏幕截图 2026-10-13 150915.jpg','屏幕截图 2026-10-13 151254.jpg','屏幕截图 2026-10-13 035201.jpg','屏幕截图 2026-10-12 002727.jpg','download.jfif']:
 shutil.copy2(Path('D:/Desktop/问题')/name,userref/name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V21','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';zp=out/'Production_1QK_Rhino_V21_AsBuilt_Refinement.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V21/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
bundle={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files)}
(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle),flush=True)
