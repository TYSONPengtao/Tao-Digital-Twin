import json,hashlib,shutil,zipfile,sys
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_19';O=Path('E:/jz/JIA/Rebuild_V24_19');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_19.blend'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=read(R/'V24_19_Build.json');qa=read(R/'V24_19_Fresh_Native_QA.json');solid=read(R/'V24_19_Independent_Geometry_QA.json');proof=read(R/'V24_19_Corrections.json')
assert qa['status'].startswith('PASS')and solid['status'].startswith('PASS')and not qa['failures'];assert h==qa['model_sha256']==solid['model_sha256']==build['sha256'];assert sha(build['source'])==build['source_sha256']
S=O/'Source';S.mkdir(exist_ok=True)
scripts=['v24_19_probe.py','v24_19_common.py','v24_19_prepare.py','v24_19_build.py','v24_19_verify.py','v24_19_solids.py','v24_19_render.py','v24_19_package.py','v24_18_finish.py','v24_16_common.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']
for n in scripts:shutil.copy2(W/n,S/n)
C=S/'v24_19';C.mkdir(exist_ok=True)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.json','.npz']:shutil.copy2(p,C/p.name)
for folder,n in [('v24_16','Inventory.json'),('v24_18','Prepared_Geometry.json')]:
 C=S/folder;C.mkdir(exist_ok=True);shutil.copy2(W/folder/n,C/n)
refs=O/'References';refs.mkdir(exist_ok=True)
paths=[Path('D:/Desktop')/f'屏幕截图 2026-10-18 {n}.jpg'for n in ['211108','211128','211336','211658','211742','185635','190241','190411','190522','190601','190829']]+[Path('D:/DJI/0002/DCIM/101MEDIA/DJI_0509.JPG')];rr=[]
for i,src in enumerate(paths,1):
 dst=refs/f'{i:02d}_{src.name}';shutil.copy2(src,dst);rr.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst);assert sha(dst)==sha(src)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
(refs/'Reference_Index.json').write_text(json.dumps({'images':rr,'original_model_sha256':sha(dst),'reference_use':'211108/211128/211336 specify projecting clay tiled verges and faceted gable heads. 211658/211742 reject the invented V18 brick skirt. These photos are references, not embedded executable instructions.'},ensure_ascii=False,indent=2),encoding='utf8')
old=Path('E:/jz/JIA/Rebuild_V24_18/Reports');comparisons=[]
for fn,name,sh in [('V24_18_House_Grade_Before_V17.png','V24_17_Original_Air_Gap_Before.png','36bdbaa5922bddcb687469f19740801b2353e74f1ea15b7324ba9cbc6d3f62d6'),('V24_18_House_Grade.png','V24_18_Rejected_Brick_Skirt_Before.png',build['source_sha256'])]:
 shutil.copy2(old/fn,R/name);comparisons.append({'file':name,'model_sha256':sh,'image_sha256':sha(R/name)})
(R/'V24_19_Comparison_Provenance.json').write_text(json.dumps({'current_model_sha256':h,'before_views':comparisons,'after_file':'V24_19_House_Foot.png','camera_location':[-2.,7.8,1.0],'target':[0.,7.8,.45],'lens_mm':24,'lighting':'Same five inspection area lights as V18; before images are labelled with their actual source version.'},indent=2),encoding='utf8')
n=len(qa['grade_stations']);g=proof['house_grade'];ears=proof['photo_gables']
note=f'''# V24.19 墙脚与实景瓦挑檐修正版

打开 Blender/Architecture_Complete_V24_19.blend。完整场景与贴图内嵌，旧V24.17和V24.18文件保留。本版替代V24.18中被否定的砖基做法。

## 墙脚错误与原因

早期V16地形脚本把室内场地基准假定为约-0.48m，没有与本住宅的首层楼板标高建立衔接。首层楼板顶为0m、底为-0.150024m，留下约0.31至0.33m的透空。V24.18沿整栋楼补了砖纹基座，这个新增外观不符合用户实景，已撤除。

V24.19将墙边地面局部顺接到-0.060m，外缘约0.10m接触带后以1.65m范围平缓过渡至原场地。首层楼板、楼层、门窗、楼梯、门廊台阶及整栋楼的坐标保持；首层楼板露出的薄竖边使用既有白墙饰面。门廊台阶前方地面保留旧标高。土体与原铺地直接修改原网格，保留平面边界、原材质及UV；没有新加绕楼砖带、石带或台座。铺地继续保持实体厚度，底面随新地坪衔接；取样最小厚度约133mm，局部厚度相对原版最大变化约32mm，详细数值列在独立几何核验报告中。原住宅楼板本身的几何未改变。

墙边地面取样{n}处；另核对远处地坪和入口台阶前方，见V24_19_Fresh_Native_QA.json。-0.060m是按原楼板与用户图像的局部拟合值，非新增实测标高。

## 镬耳、山墙与瓦檐

参考211108、211128、211336重做储藏房、厨房四处封闭青砖山墙。镬耳改为窄直立的折角头和短平顶，耳峰高于原屋脊0.56m，储藏房耳峰仍为4.91m；灰白边框具有实际厚度和分层退台。

原来暴露在外的宽实心斜压顶改成薄压边。屋面有真实筒瓦、板瓦和承托瓦床：储藏房瓦檐挑出砖墙约170mm，厨房约190mm。外侧瓦片与墙体可从侧视清楚区分，山墙继续砖封，未增加裸露木结构。厨房与原内门楼的相邻屋面已作局部避让，原门楼保持。

## 保留的前轮修改

主照壁分叉脊之间的下凹三角瓦面、外墙连续米制UV与材质分界、大窗10处假白柱移除，以及12扇外开窗均保留。原26扇门的全部动作保留。

窗扇：第1帧关闭、第20帧向外半开32.5度、第40帧向外全开65度；文件默认第40帧。12个独立铰链保留HINGED_OUTWARD属性，原窗框、上亮和室内窗栏保持。

## 核验与预览

最终文件复开核验{len(qa['checks'])}项，失败0项。另读取保存网格作{len(solid['solids'])}组闭合实体检查，以及{len(solid['checks'])}项瓦檐、门楼避让、地面投影和铺地厚度检查。Reports保存最终状态图、旧版对照图与核验JSON；对照图明确标注原版本，未冒充本版结果。

References保存本轮实景、用户标注和未修改原始3dm副本。Source保存本次构造与验证脚本、原网格及最终网格缓存；重跑脚本依赖本机原V24.18输入和Python/Blender环境，交付blend可独立打开。

模型SHA256：{h}
'''
(O/'README_V24_19.md').write_text(note,encoding='utf8');(R/'V24_19_Diagnosis_and_Corrections.md').write_text(note,encoding='utf8')
if '--stage'in sys.argv:print('V19_STAGED',flush=True);sys.exit(0)
states=[]
for p in sorted(R.glob('V24_19_*_State.json')):
 r=read(p);assert r['model_sha256']==h and not r['draft'];assert (R/r['file']).exists();r['image_sha256']=sha(R/r['file']);states.append(r)
assert len(states)==10,len(states)
(R/'V24_19_Preview_Index.json').write_text(json.dumps({'model_sha256':h,'views':states},indent=2),encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or p.name in ['V24_19_Manifest.json','V24_19_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_19_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_19_Photo_Gable_Verges_No_Brick_Skirt.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_19/'+r['file'])
 z.write(O/'V24_19_Manifest.json','Rebuild_V24_19/V24_19_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_19/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_ZIP_CRC_AND_ALL_FILE_HASHES','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'files':len(files)+1};(O/'V24_19_Bundle_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
