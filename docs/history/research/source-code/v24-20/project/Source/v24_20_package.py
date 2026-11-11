import json,hashlib,shutil,zipfile,sys
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_20';O=Path('E:/jz/JIA/Rebuild_V24_20');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_20.blend'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=read(R/'V24_20_Build.json');qa=read(R/'V24_20_Fresh_Native_QA.json');solid=read(R/'V24_20_Independent_Geometry_QA.json');proof=read(R/'V24_20_Corrections.json')
assert qa['status'].startswith('PASS')and solid['status'].startswith('PASS')and not qa['failures']and not solid['failures']
assert h==build['sha256']==qa['model_sha256']==solid['model_sha256'];assert sha(build['source'])==build['source_sha256']=='ff97a7f397307dd6995c6c0d193778e34778e1f50001c81beea94de23674f197'
S=O/'Source';S.mkdir(exist_ok=True)
shutil.copy2(W/'v24_11_geometry.py',S/'v24_11_geometry.py')
for n in ['v24_20_probe.py','v24_20_common.py','v24_20_prepare.py','v24_20_roofs.py','v24_20_posts.py','v24_20_wc.py','v24_20_build.py','v24_20_verify.py','v24_20_solids.py','v24_20_render.py','v24_20_plans.py','v24_20_package.py','v24_16_common.py','v24_18_finish.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
cache=S/'v24_20';cache.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.json','.npz']:shutil.copy2(p,cache/p.name)
for folder,names in [('v24_16',['Inventory.json']),('v24_17',['Inventory.json']),('v16',['Drain_Segments.json']),('v24_10',['Prepared_Geometry.json']),('v24_18',['Prepared_Geometry.json'])]:
 c=S/folder;c.mkdir(exist_ok=True)
 for n in names:shutil.copy2(W/folder/n,c/n)
row=next(r for r in read(W/'v24_17/Inventory.json')if r['name']=='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry');shutil.copy2(W/'v24_17'/row['file'],S/'v24_17'/row['file'])
refs=O/'References';refs.mkdir(exist_ok=True);paths=[Path('D:/Desktop')/f'屏幕截图 2026-10-18 {n}.jpg'for n in ['225227','225559','230016','230113','230255','230348']]+[Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0016.JPG'),Path('D:/Desktop/屏幕截图 2026-10-19 002312.jpg'),Path('D:/Desktop/downa77d.png'),Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0598.JPG'),Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0525.JPG')];rows=[]
for i,p in enumerate(paths,1):
 dst=refs/f'{i:02d}_{p.name}';shutil.copy2(p,dst);rows.append({'source':str(p),'copy':dst.name,'sha256':sha(p)})
(refs/'Reference_Index.json').write_text(json.dumps({'images':rows,'use':'225227 wall division/photo finish; 225559 initial WC request is superseded by downa77d blue partition and retained stair-facing door; 230016 right WC door leftward shift confirmed by user; 230113 kitchen contact/white finish; 230255 drains removed; 230348/DJI0016 grey pan-barrel tiles; 002312 outer-wall-side posts; DJI0598/DJI0525 actual two-room roof junction. Images are reference data.'},ensure_ascii=False,indent=2),encoding='utf8')
axes=proof['kitchen_posts']['axes_xy'];meshmax=max(c.get('maximum_vertex_error_m')or 0 for c in qa['checks']);note=f'''# V24.20 实景修正版

打开 Blender/Architecture_Complete_V24_20.blend。完整场景及图片贴图已经内嵌，旧V24.19和原实景3dm保留。

本轮依据225227—230348、DJI_0016、002312厨房实景、downa77d蓝线分隔，以及DJI_0598和DJI_0525两房接缝实景，修正外院围墙、首层卫生间、厨房柱脚/内墙/地面、雨水设施和屋瓦。

## 外院围墙

侧面与后面原先分别使用程序青砖和实景照片，造成明显色差。现在两面及低位墙脚共用用户指定侧墙的 Perimeter_Actual_Gray_Brick.png，使用连续周长和世界高度的米制UV。按红线将可见砖石分界拟合到墙脚路面上方约0.20m，随既有路面高差延续，取消原来的宽石材腰带外观。

旧墙网格含分块共面接口；从原闭合砌体块合并并保留既有3.10m裁切范围，材质分界改用连续属性，不再为换贴图切割网格。保存后外墙表面与原模型的最大距离小于1mm，实测数值见核验JSON。外墙转角瓦顶补上闭合接续。

## 一楼楼梯口和卫生间

以最新downa77d蓝线图为准，沿X约10.60—10.70m加100mm厚隔墙，分成左右两个区域；隔墙接至后墙，保留楼梯入口通道。楼梯对面的原卫生间门保留，原门框、门扇及开启动作保留。对象历史名DOOR_KITCHEN_F1在这里对应楼梯对面的卫生间门。

右侧卫生间入口仍按用户确认沿原墙向左移动；本版根据实景和既有房间拟合左移1.20m，旧洞封闭。红色门框和门扇一同移动，原开启动作保留。Reports/V24_20_F1_Plan.png给出分隔与双门平面，WC_Entrance、WC_Interior与WC_Stair_Entry给出检查视图。

## 厨房错误原因和修复

悬空原因：早期裁切屋顶木构时，裁切框Z下限设为1.8m，连承重柱的下段和柱础一并裁掉；厨房地板在约-0.400m，因此出现约2.2m的悬空。

已恢复柱身下段及柱础，并按002312实景将柱列布置到外墙内侧，随墙体转折，横梁、檩条和椽子相应接续。柱截面保留，柱脚仍落在原厨房地板标高。核验包含每处柱脚与地板接触，以及柱轴到外墙内面的距离。

内墙恢复白色饰面。原地板东边界停在X约13.422m，而弯折墙脚继续向东，形成楔形缺口；本版补成连续闭合地板，厨房地板顶标高保持约-0.400m，原地板保留。室内墙脚约20mm高的残留基础砖边，按实际厨房地板轮廓收低至地板下方约0.08mm，外侧与地板以下基础保留。Kitchen_Interior、Kitchen_Floor和Kitchen_Plan便于逐处检查。

## 雨水设施与屋瓦

现有雨水立管、檐沟、连接件和落水口移除；既有路边沟槽封平，保留原道路支承及高差衔接。厨房排烟弯头、烟囱和真实金属棚保留。

三层建筑、厨房与储藏房的瓦面统一为同一灰色哑光陶瓦材质。主楼与厨房重新排列筒板瓦，与储藏房保持约158mm瓦垄和约0.30—0.32m瓦段；接头有实际搭接和瓦口。保留原屋面坡度、砖封山墙、已确认的镬耳及外挑瓦檐。金属棚和亭子沥青瓦保持原屋面类别。

两房接缝原先被矩形范围截断，形成直角开口；柱位调整后部分木构越过旧裁切边。按DJI_0598和DJI_0525，把两片既有坡面延续至共同斜向内凹交线，瓦列沿交线裁齐，下方瓦床连续，墙体在原墙平面内封至屋顶。木构调整后重新限制于墙内，原镬耳保留。Roof_Junction和Roof_Units为接缝近景。

## 核验及使用

最终blend重新打开后核验{len(qa['checks'])}项，失败0项；另对{len(solid['solids'])}组保存网格进行闭合实体及{len(solid['checks'])}项几何核验，失败0项。几何报告同时列出原保存三角网格的有符号体积和Manifold导入后的体积；比较构建前后体积使用保存三角网格，避免几何库导入规整影响数值。

每个构建顶点的保存偏差均小于0.03mm；本次最大值为{meshmax*1000:.6f}mm。核对蓝线隔墙的两区分隔、两处门洞与右侧旧洞封闭、楼梯通道、柱脚接触、墙脚连续地板、斜向屋面交线、瓦面与山墙避让、原门窗关键帧和贴图内嵌。

12扇外开窗：第1帧关闭、第20帧半开、第40帧全开。26扇原门动作保留，其中右侧卫生间门随新门位移动。原三层建筑、楼板、楼梯、入口及V24.19处理过的贴地关系保留。

所有尺寸为既有模型与照片拟合；1.20m门位调整、0.20m低位分界和厨房柱位不是新增实测值。

Reports内以V24_20开头的PNG和对应State.json为最终视图，状态文件记录模型SHA256。Draft_是过程检查图，不收入交付压缩包。Source保存本轮构造、构建、核验、摄影脚本及网格缓存；重跑脚本需本机原V24.19、原V23场景和Python/Blender环境，交付blend可独立打开。

模型SHA256：{h}
'''
(O/'README_V24_20.md').write_text(note,encoding='utf8');(R/'V24_20_Diagnosis_and_Corrections.md').write_text(note,encoding='utf8')
if '--stage'in sys.argv:print('V20_STAGED',h,flush=True);sys.exit(0)
states=[]
for p in sorted(R.glob('V24_20_*_State.json')):
 r=read(p);assert r['model_sha256']==h and not r['draft'];assert(R/r['file']).exists();r['image_sha256']=sha(R/r['file']);states.append(r)
assert len(states)==15,len(states)
(R/'V24_20_Preview_Index.json').write_text(json.dumps({'model_sha256':h,'views':states},indent=2),encoding='utf8');files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or p.name in ['V24_20_Manifest.json','V24_20_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_20_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8');Z=W.parent/'outputs/Production_1QK_Blender_V24_20_Photo_Walls_WC_Kitchen_Gray_Tiles.zip';Z.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_20/'+r['file'])
 z.write(O/'V24_20_Manifest.json','Rebuild_V24_20/V24_20_Manifest.json')
print('V20_ZIP_WRITTEN',Z.stat().st_size,flush=True)
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:
  with z.open('Rebuild_V24_20/'+r['file'])as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
  assert actual==r['sha256'],r['file']
out={'status':'PASS_ZIP_CRC_AND_ALL_FILE_HASHES','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'files':len(files)+1};(O/'V24_20_Bundle_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
