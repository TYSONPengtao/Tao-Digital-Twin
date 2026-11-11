import json,hashlib,shutil,zipfile
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_14';O=Path('E:/jz/JIA/Rebuild_V24_14');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_14.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);qa=json.loads((R/'V24_14_Fresh_Blend_QA.json').read_text());solid=json.loads((R/'V24_14_Independent_Solid_QA.json').read_text());clr=json.loads((R/'V24_14_Independent_Clearance_QA.json').read_text());views=json.loads((R/'V24_14_Preview_States.json').read_text());build=json.loads((R/'V24_14_Build.json').read_text())
assert all(r['status'].startswith('PASS')for r in [qa,solid,clr])and not qa['failures'];assert all(r['model_sha256']==h for r in [qa,solid,clr,views]);assert build['sha256']==h;assert len(views['views'])==7
assert all((R/r['file']).is_file()for r in views['views'])
S=O/'Source';S.mkdir(exist_ok=True)
for n in ['v24_14_probe.py','v24_14_prepare.py','v24_14_build.py','v24_14_verify.py','v24_14_solids.py','v24_14_render.py','v24_14_package.py','v24_13_geometry.py','v24_12_geometry.py','v24_11_geometry.py','v24_09_roof.py','v24_03_junction_blender.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,S/n)
C=S/'v24_14';C.mkdir(exist_ok=True)
for n in ['Before_Snapshot.json','Inventory.json','Prepared_Geometry.json','Solid_Export_Index.json','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry.npz','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz']:
 shutil.copy2(D/n,C/n)
for p in D.glob('SAVED_*.npz'):shutil.copy2(p,C/p.name)
C=S/'v24_11';C.mkdir(exist_ok=True);shutil.copy2(W/'v24_11/QA_Obstacle_Index.json',C/'QA_Obstacle_Index.json')
refs=O/'References';refs.mkdir(exist_ok=True);refmap=[]
images=['113325','113347','113449','113532','113602','113659','113730','113752','113814','114422']
for i,n in enumerate(images,1):
 src=Path(f'D:/Desktop/wt/0001储藏房/屏幕截图 2026-10-18 {n}.jpg');dst=refs/f'{i:02d}_Storage_Reference_{n}.jpg';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('D:/Desktop/屏幕截图 2026-10-18 101233.jpg');dst=refs/'11_Screenwall_Roof_Fork_101233.jpg';shutil.copy2(src,dst);refmap.append({'source':str(src),'copy':dst.name,'sha256':sha(src)})
src=Path('E:/jz/实景三维场景模型.3dm');dst=refs/'Original_AsBuilt_Model_UNMODIFIED.3dm';shutil.copy2(src,dst);assert sha(src)==sha(dst)=='78d30b55d3301dee562a36b4c96f0da832d8b70d24809e4e7ea211b9a679f23f'
for n in ['AsBuilt_Fit.json','AsBuilt_Plan.json','AsBuilt_Reference.json']:shutil.copy2(W/'v24_10'/n,refs/n)
shutil.copy2('E:/jz/JIA/Rebuild_V24_13/README_V24_13.md',refs/'Prior_V24_13_Corrections.md')
(refs/'Reference_Index.json').write_text(json.dumps({'images':refmap,'video':{'source':'E:/VID_20260507_152114_00_001.mp4','sha256':'db665a05beaa59bb7c758b4142878b7f6a61aa2d2326da39c18ed7abfd12fd80','note':'Previously reviewed reference; original video is not duplicated in this bundle. Latest 11 still references and the registered 3dm provide this turn detail corrections.'}},ensure_ascii=False,indent=2),encoding='utf8')
note=f'''# V24.14 储藏房封闭山墙与檐廊修正

完整建筑和场地：Blender/Architecture_Complete_V24_14.blend。照片贴图内嵌，模型可独立打开。原V24.13保留未覆盖。1/20/40帧为门关闭/半开/打开，26扇门原动画动作均保留。

依据本轮113325—114422照片及101233照壁顶参考，储藏房木隔扇、玻璃和两扇门的铰链整体向室内后退0.48米，形成连续檐廊。门叶、门框和玻璃一起调整，原开合动作没有重录。檐廊仍为两根竖直圆柱，柱列斜向于栏杆；原入口柱嵌在山墙中，连同柱础向廊内沿X移0.30米，消除与侧墙穿插。柱位为模型内的照片拟合位置，非新增现场实测。

侧墙顶部改成封闭的仿镬耳山墙与圆润耳头，外侧梁头、檩头和木封檐板不再穿出墙面。白色墙面、灰色连续压顶与瓦面分层表达。檐廊去掉厚重的木封板及大块木头，改为薄望板、细椽、顺柱承梁和曲线托木。

删除上版入口多余短回墙及其瓦盖，次照壁原来的直墙、水平墙冠及两格装饰框保留，端部增加白色山花、圆卷头、灰边及三层檐口。主照壁分叉屋脊、端部扇形瓦及原有分层底座保留，四支翘尖改成较宽圆头陶构，端部扇形瓦补全厚度收口。此前明确删除的储藏房入口铁皮棚没有恢复。

储藏房已校正的地块、弧形后墙、厨房退让及连续后墙、全场地和其他建筑保留。独立外侧储藏区的薄金属棚保留，与已删除的入口铁皮棚是不同构件。

复开检查共{len(qa['checks'])}项，失败0项。独立读取保存网格核验{len(solid['solids'])}组封闭实体及{len(solid['spatial_checks'])}项空间关系通过；两根圆柱与墙体无体积穿插。入口、檐廊、门洞等五处通行盒采样通过。检查仅覆盖模型几何、资产保留和动画；细部按照片近似拟合。

Reports包含同一最终模型的7张1600×1200预览：正面、廊下、次照壁端头、封闭山墙、主照壁顶、俯视及全场。对应SHA256为{h}。

References含本轮11张图、未修改的实景3dm副本、原配准地块信息和上版记录。Source保存本轮构造、修正及核验脚本和必要网格缓存。重建脚本需本机原V24.13输入与Python/Blender依赖；交付blend本身完整独立。

输入V24.13 SHA256：{build['source_sha256']}
'''
(O/'README_V24_14.md').write_text(note,encoding='utf8');(R/'V24_14_Resolved_Issues.md').write_text(note,encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file()or p.suffix=='.blend1'or p.name.startswith('Draft_')or 'Draft_States'in p.name or p.name in ['V24_14_Manifest.json','V24_14_Bundle_QA.json']:continue
 files.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'V24_14_Manifest.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
Z=W.parent/'outputs/Production_1QK_Blender_V24_14_Sealed_Gables_Recessed_Veranda.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=4)as z:
 for r in files:z.write(O/r['file'],'Rebuild_V24_14/'+r['file'])
 z.write(O/'V24_14_Manifest.json','Rebuild_V24_14/V24_14_Manifest.json')
with zipfile.ZipFile(Z)as z:
 assert z.testzip()is None
 for r in files:assert hashlib.sha256(z.read('Rebuild_V24_14/'+r['file'])).hexdigest()==r['sha256']
out={'status':'PASS_BUNDLE_CRC_AND_ALL_FILE_SHA256','zip':str(Z),'bytes':Z.stat().st_size,'sha256':sha(Z),'model_sha256':h,'file_count':len(files)+1};(O/'V24_14_Bundle_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
