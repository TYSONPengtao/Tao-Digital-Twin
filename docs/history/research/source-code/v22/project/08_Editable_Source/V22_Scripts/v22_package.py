import sys,json,hashlib,struct,zipfile,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('E:/jz/JIA/Rebuild_V22');P=O/'04_Rhino/Architecture_Complete_V22_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V22_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));GP=O/'05_Export/Complete_Site_V22_LOCAL.glb'
door_qa=json.loads((O/'06_Report/Final_Native_Door_QA.json').read_text(encoding='utf8'));assert door_qa['status'].startswith('PASS') and not door_qa['unresolved_collisions']
detail_qa=json.loads((O/'06_Report/Final_Detail_Review_V22.json').read_text(encoding='utf8'));assert detail_qa['status'].startswith('PASS') and detail_qa['native_model_sha256']==Q['sha256']
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));g=json.loads(f.read(length));binlen,bintype=struct.unpack('<II',f.read(8));binary=f.read(binlen)
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert V['native_model_sha256']==Q['sha256'];assert total==GP.stat().st_size and len(g['cameras'])==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])==5
I=json.loads((O/'02_Data/Native_Readback_Index_V22.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
DM=json.loads((O/'02_Data/Door_Manifest_V22.json').read_text(encoding='utf8'));nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
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
AQ=json.loads((O/'06_Report/V22_Assembly_QA.json').read_text(encoding='utf8'));AQ['status']='PASS_FRESH_NATIVE_V22_QA';(O/'06_Report/V22_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'nodes':len(I),'triangles':tri,'glb_meshes':len(g['meshes']),'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'glb_animations':len(g.get('animations',[])),'independent_door_leaves':len(DM['doors']),'sliding_leaves':sum(r.get('operation')=='SLIDING' for r in DM['doors']),'default_open_door_parity':doorproof,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'v21_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')

font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
U=Path('D:/Desktop/问题大全（每个细节）')
plates=[
 ('01_内院入口','00001内院入口','目前建模V21.jpg','实景照片.jpg','V22_Courtyard_Ideal_Compare'),
 ('02_建筑入口','00002建筑入口前','目前模型.jpg','屏幕截图 2026-10-16 001056.jpg','V22_House_Entrance_Compare'),
 ('03_亭子','00003正确亭子','目前模型.jpg','实景图片.jpg','V22_Pavilion_Ideal_Compare'),
 ('04_内大门','00004内大门','目前模型.jpg','实景照片.jpg','V22_Inner_Gate_Ideal_Compare')]
for name,folder,current,real,view in plates:
 can=Image.new('RGB',(2200,1760),(246,245,240));dr=ImageDraw.Draw(can)
 for j,(p,title) in enumerate([(U/folder/current,'当前模型（用户提供）'),(U/folder/'理想模型.png','理想模型（用户提供）'),(U/folder/real,'实景参考（用户提供）'),(O/'06_Report'/f'{view}.png','V22：最终保存模型实际网格，白模对比')]):
  col=j%2;row=j//2;im=ImageOps.contain(Image.open(p).convert('RGB'),(1060,750),Image.Resampling.LANCZOS)
  can.paste(im,(20+col*1100+(1060-im.width)//2,66+row*835+(750-im.height)//2));dr.text((24+col*1100,22+row*835),title,font=font,fill=(44,43,39))
 footer='几何按理想图和实景细化；原生及 GLB 保留材质。浮雕为图像拟合轮廓，尺寸未经现场复测。'
 if name.startswith('04'):footer='内门采用动画中的局部内开姿态展示门叶；原生/GLB默认为完全开启。浮雕为图像拟合轮廓。'
 dr.text((24,1695),footer,font=small,fill=(60,58,53))
 can.save(O/'06_Report'/f'V22_Compare_{name}.png')
readme='''V22 理想模型对照细化（2026-10-16）

主模型：04_Rhino/Architecture_Complete_V22_ALIGNED_ENU.3dm，Rhino 8、米、原 ENU 坐标。
漫游资产：05_Export/Complete_Site_V22_LOCAL.glb，LOCAL 米，变换见02_Data/Coordinate.json。
可编辑检视场景：05_Export/Actual_Rhino_V22_Readback_LOCAL.blend。V21文件保留。

最新依据：D:/Desktop/问题大全（每个细节）的四组“目前模型—理想模型—实景”及厨房柱子对比。全部随包保存于07_Reference/V22_AsBuilt/Latest_Comparison。06_Report有四张对应对比板和细部命名视图；右下图由最终保存原生3DM网格回读生成。白模材质仅作对比，交付模型保留木色、石材与玻璃。

本轮实际几何变化：
1. 楼房入口：实心空白墙带开为玻璃上亮，增设回纹格；提高门扇比例，增加细边框与半圆拉手，仍为横向推拉。前立面窗下和楼层带增加薄砖分缝，阳台栏板增加浅框与卷草花卉细节。补齐阳台边梁及柱脚/栏杆底脚接触，保留排水管孔。
2. 内院及厨房：原排水地面按实际实体体积分割成石板和填缝，保留石板坡面、边界，填缝仅下凹1.5mm；四处厨房柱础改方足、八角鼓身和圆承接，补横向穿头木、短垂饰和花形端头。处理围墙勒脚重面。
3. 亭子：长Y形撑改短曲线角托，两端补细木竖杆；细化竹帘及吊带、檐沟、空腔落水管与管箍。保留已收回的主轴侧位置和木板底50mm离地净空。
4. 内大门：门柱原孤立三角图形改为连续底板上的曲线植物浅浮雕；三格花卉石门楣下设深木固定上亮，院内补窄木侧板。增设圆瓦端、短波形滴水花边、檐底圆盘和随动拉手/菱饰；原厨房齐平接口和内开门轴保留。按理想图显出一道约100mm石阶，门叶底端相应重配并留13mm净空。

理想图中部分台阶数量与用户既定“一阶、实心”的要求不一致。本版保留实景与既定要求的一阶实心门廊。浮雕为理想图/实景启发的可编辑体积轮廓，不能当作逐毫米石刻测绘；未凭图像虚构隐藏榫卯。

门：26扇独立活动叶，楼房4扇前玻璃叶推拉，其余有门扇处向内开，默认开启，GLB有24段动画。门轴、平移量及父子关系见02_Data/Door_Manifest_V22.json。饰面/拉手纳入实际门节点，随门运动。
检查：原生回读核对保留及修改构件、网格/材质/UV、导出三角形数量、门默认位和修改门的运动采样；相关报告随包。未在真实UE项目内导入、烘焙碰撞或运行漫游。UE长度从米换算厘米100倍，保留独立门节点与层级。
'''
(O/'README_V22_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
settings=json.loads((Path('E:/jz/JIA/Rebuild_V21')/'02_Data/UE_Walkthrough_Settings.json').read_text(encoding='utf8'))
settings.update(asset='05_Export/Complete_Site_V22_LOCAL.glb',door_manifest='02_Data/Door_Manifest_V22.json')
(O/'02_Data/UE_Walkthrough_Settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf8')
srcdir=O/'08_Editable_Source/V22_Scripts';srcdir.mkdir(parents=True,exist_ok=True)
for task in ['house','gate','kitchen','pavilion','wall']:
 td=srcdir/task;td.mkdir(exist_ok=True)
 for p in (W/f'v22_{task}').iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.npz'] and not p.name.startswith(('Preview_Meshes','Inventory')):
   if p.suffix=='.json':
    a=json.loads(p.read_text(encoding='utf8'));st=a.get('status','') if isinstance(a,dict) else ''
    if st.startswith(('NEEDS','PENDING','FAIL','DETAIL_CONTACTS_NEED')):continue
   shutil.copy2(p,td/p.name)
 for fn in ['Design_Control.json','Contact_QA.json']:
  p=W/f'v22_{task}'/fn
  if p.exists():shutil.copy2(p,O/'06_Report'/f'{task}_{fn}')
for p in W.glob('v22_*.py'):
 if 'prepare_' not in p.name:shutil.copy2(p,srcdir/p.name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V22','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
zp=W.parent/'outputs/Production_1QK_Rhino_V22_Ideal_Detail_Refinement.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V22/'+p.relative_to(O).as_posix())
  if i%200==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
bundle={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files)}
(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle),flush=True)
