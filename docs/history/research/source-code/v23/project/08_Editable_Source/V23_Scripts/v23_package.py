import sys,json,hashlib,struct,zipfile,shutil,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path('E:/jz/JIA/Rebuild_V23');P=O/'04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
Q=json.loads((O/'06_Report/V23_Native_Readback_QA.json').read_text(encoding='utf8'));assert Q['status'].startswith('PASS') and Q['sha256']==sha(P);F=rh.File3dm.Read(str(P));GP=O/'05_Export/Complete_Site_V23_LOCAL.glb'
door_qa=json.loads((O/'06_Report/Final_Native_Door_QA.json').read_text(encoding='utf8'));assert door_qa['status'].startswith('PASS') and not door_qa['unresolved_collisions'] and door_qa['native_model_sha256']==Q['sha256']
detail_qa=json.loads((O/'06_Report/Final_Detail_Review_V23.json').read_text(encoding='utf8'));assert detail_qa['status'].startswith('PASS') and detail_qa['native_model_sha256']==Q['sha256']
with GP.open('rb') as f:
 magic,version,total=struct.unpack('<4sII',f.read(12));assert magic==b'glTF' and version==2;length,ctype=struct.unpack('<II',f.read(8));g=json.loads(f.read(length));binlen,bintype=struct.unpack('<II',f.read(8));binary=f.read(binlen)
V=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));assert V['native_model_sha256']==Q['sha256'];assert total==GP.stat().st_size and len(g['cameras'])==V['camera_count'] and len(g['meshes'])==Q['nodes'];assert all('bufferView' in im and 'uri' not in im for im in g['images']);assert sum(im.get('name','').startswith('Tile_') for im in g['images'])>=5
I=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};tri=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives']);assert tri==Q['triangles']==sum(r['triangles'] for r in I)
DM=json.loads((O/'02_Data/Door_Manifest_V23.json').read_text(encoding='utf8'));nodes={n.get('name'):j for j,n in enumerate(g['nodes'])};parents={c:j for j,n in enumerate(g['nodes']) for c in n.get('children',[])}
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
AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'));AQ['status']='PASS_FRESH_NATIVE_V23_QA';(O/'06_Report/V23_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
delivery={'status':'PASS_DELIVERY_FILES','native_objects':len(F.Objects),'nodes':len(I),'triangles':tri,'glb_meshes':len(g['meshes']),'glb_embedded_images':len(g['images']),'glb_cameras':len(g['cameras']),'glb_animations':len(g.get('animations',[])),'independent_door_leaves':len(DM['doors']),'sliding_leaves':sum(r.get('operation')=='SLIDING' for r in DM['doors']),'default_open_door_parity':doorproof,'native_model_sha256':sha(P),'glb_sha256':sha(GP),'v22_preserved_sha256':AQ['base_model_sha256'],'ue5_import_tested':False};(O/'06_Report/Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')

independent=json.loads((W/'v23_independent_review.json').read_text(encoding='utf8'))
assert independent['status'].startswith('PASS') and independent['native_sha256']==Q['sha256']
shutil.copy2(W/'v23_independent_review.json',O/'06_Report/V23_Independent_Contact_Review.json')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
U=Path('D:/Desktop/问题大全（每个细节）/00004内大门')
can=Image.new('RGB',(2200,1760),(246,245,240));dr=ImageDraw.Draw(can)
panels=[(U/'理想模型.png','理想模型（用户提供）'),(U/'实景照片.jpg','实景参考（用户提供）'),(Path('E:/jz/JIA/Rebuild_V22/06_Report/V22_Inner_Gate_Ideal_Compare.png'),'V22：上一版保存模型'),(O/'06_Report/V23_Inner_Gate_Ideal_Compare.png','V23：新保存模型回读，局部内开姿态')]
for j,(p,title) in enumerate(panels):
 col=j%2;row=j//2;im=ImageOps.contain(Image.open(p).convert('RGB'),(1060,750),Image.Resampling.LANCZOS)
 can.paste(im,(20+col*1100+(1060-im.width)//2,66+row*835+(750-im.height)//2));dr.text((24+col*1100,22+row*835),title,font=font,fill=(44,43,39))
dr.text((24,1695),'前外侧雕花、院内侧素面；尺寸按图像拟合。原生/GLB 默认为完全内开，白模仅用于比较。',font=small,fill=(60,58,53))
can.save(O/'06_Report/V23_内大门_四图对比.png')

readme='''V23 内大门细部优化（2026-10-16）

主模型：04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm，Rhino 8，米，原 ENU 坐标。
漫游资产：05_Export/Complete_Site_V23_LOCAL.glb，LOCAL 米；变换见02_Data/Coordinate.json。
检视场景：05_Export/Actual_Rhino_V23_Readback_LOCAL.blend。
V22 保持原文件不变，本轮重点细化内大门，并补墙柱连接；厨房、储藏房、亭子、楼房和场地其余几何逐对象保留。

依据：用户最新00004内大门理想/目前/实景对照及DJI_0086、DJI_0118。0086用于瓦件搭接做法，0118用于院内侧檐底，未把照壁比例套到门楼。参照图片在07_Reference。

1. 两根石柱前缘改90mm折角，正面和两斜面设12组有鼓起花瓣、竹叶中脊和花心的体积浮雕，腰线统一为下段比例；背面保留素面。门楣三格卷草花卉细化。
2. 屋面改为510件分段筒瓦、凹板瓦，86件圆花瓦当，配分段圆脊瓦；前后檐均补短椽尾、深檐枋、三角纹带和雕花波形滴水板。按用户最后反馈收短屋檐、压低翘角：总宽6.107m改为5.313m、屋面最高点3.928m改为3.292m；瓦件、檐口、翼角和封闭檐底同步连续变形，保留中央承托标高；将原被门楣埋住的圆盘调整到前后可见檐底。
3. 门叶补实际承接的凸芯板和背面细压线，拉手改为曲柄铜拉手及花形长底座，随门叶运动；木上亮补非文字卷草冠饰。灯笼补细金线与细穗，吊线在檐底承接，去掉穿出屋面的过长杆。
4. 补齐左围墙与门柱之间原有约33mm断缝，并保留原砖面/白灰层分界；保留厨房齐平接口、一道浅石阶和13mm门底间隙；修正新腰线闭门穿插及右门全开时压线碰墙。

全部26扇活动叶保留：楼房4扇前门为推拉，其余有门扇处向内开；GLB含24段动画，默认开启。门轴、平移量及父子关系见Door_Manifest_V23.json。白模正面对比及五金图使用局部内开动画姿态以显示门板；原生3DM、GLB与Blend保持完全开启。

06_Report有原生保存后回读、保留对象哈希、闭合与正体积、UV/法线、瓦件承接、厨房接口、门运动采样、导出几何和门姿态校验。浮雕是图像拟合的可编辑网格，并非实物石刻扫描或逐毫米测绘；未凭照片虚构隐藏榫卯。未在真实UE项目内运行导入及漫游，UE碰撞体/导航仍需在项目中验证。
'''
(O/'README_V23_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
settings=json.loads((Path('E:/jz/JIA/Rebuild_V22')/'02_Data/UE_Walkthrough_Settings.json').read_text(encoding='utf8'))
settings.update(asset='05_Export/Complete_Site_V23_LOCAL.glb',door_manifest='02_Data/Door_Manifest_V23.json')
(O/'02_Data/UE_Walkthrough_Settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf8')
srcdir=O/'08_Editable_Source/V23_Scripts';srcdir.mkdir(parents=True,exist_ok=True)
for task in ['gate_relief','gate_roof','gate_wood','gate_junction','gate_roof_refit']:
 td=srcdir/task;td.mkdir(exist_ok=True)
 for p in (W/f'v23_{task}').iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.npz']:shutil.copy2(p,td/p.name)
 shutil.copy2(W/f'v23_{task}'/'Design_Control.json',O/'06_Report'/f'{task}_Design_Control.json')
for p in W.glob('v23_*.py'):shutil.copy2(p,srcdir/p.name)
for n in ['export_v5.py','v2_geometry.py','v19_design.py']:
 shutil.copy2(W/n,srcdir/n)
(srcdir/'v11_wall_junction').mkdir(exist_ok=True);shutil.copy2(W/'v11_wall_junction/mutation.py',srcdir/'v11_wall_junction/mutation.py')
shutil.copy2(W/'v23_reference_audit.md',O/'06_Report/v23_reference_audit.md')
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json','Architecture_Complete_V23_ALIGNED_ENU.3dm','Architecture_Complete_V23_COMPACT_PENDING.3dm'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V23','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
zp=W.parent/'outputs/Production_1QK_Rhino_V23_Inner_Gate_Refinement.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V23/'+p.relative_to(O).as_posix())
  if i%200==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
bundle={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files)}
(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle),flush=True)

