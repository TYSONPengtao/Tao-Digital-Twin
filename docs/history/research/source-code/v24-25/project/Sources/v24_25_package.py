from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).parent;D=W/'v24_25';O=Path('E:/jz/JIA/Rebuild_V24_25');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_25.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);src=json.loads((D/'Source.json').read_text());assert sha(src['model'])==src['sha256'];summaries={}
for stem in ['Native','Solid','Physics','Measure_Math','Launcher']:
 q=json.loads((R/('V24_25_'+stem+'_QA.json')).read_text('utf8'));assert q['status'].startswith('PASS')and q['model_sha256']==h,(stem,q.get('status'),q.get('model_sha256'),h);summaries[stem]={'checks':len(q['checks']),'failures':len(q['failures'])}
views=['WC_Right_F1','WC_Left_F2','Gate_Contact','Gate_Eave','Storage_Entrance','Storage_Approach','Kitchen_Roof','Roof_Valley']
for v in views:
 s=json.loads((R/('V24_25_'+v+'_State.json')).read_text());assert s['model_sha256']==h and not s['draft'];assert(R/s['file']).stat().st_size>10000
assert(R/'V24_25_Measure_UI.png').stat().st_size>10000
launcher=Path('E:/jz/JIA/Rebuild_V24_24/启动漫游.cmd').read_text('utf8').replace('Architecture_Complete_V24_24.blend','Architecture_Complete_V24_25.blend')
(O/'启动漫游.cmd').write_text(launcher,encoding='utf8',newline='\r\n')
review=launcher[:launcher.index('start ""')]+'start "" "%ROAM_BLENDER_EXE%" --factory-startup "%~dp0Blender\\Architecture_Complete_V24_25.blend"\n'
(O/'打开修正版模型.cmd').write_text(review,encoding='utf8',newline='\r\n')
readme='''V24.25 高窗、无缝门墙、厨房屋面、入口地面和测量功能

双击“启动漫游.cmd”，直接进入1.65米人物漫游。
双击“打开修正版模型.cmd”，打开可编辑原生模型，默认查看厨房瓦面。

漫游：方向键/WASD移动；空格跳跃；Shift快走；右键拖动转向；滚轮调距离。
V切换人眼/第三人称，Home回院落，Esc退出，F8重新进入。
直接打开blend不会自动接管键盘；使用“启动漫游.cmd”进入，避免V被解释为编辑器快捷键。

测量（模型单位为米）：
顶栏“测长度 L”：点击模型表面的两个端点，显示直线长度。
顶栏“测面积 P”：沿边界依次点选，按Enter完成，支持凹多边形。
面积同时给出面内面积、水平投影面积及周长；非共面边界按三角面计算。
按住Ctrl点击可吸附命中面上的顶点。Backspace撤销一个点；没有待选点时撤销最近一条结果。
测量时人物停住，右键和滚轮仍能调整视角。Esc先回漫游，再按Esc退出。
顶栏“导出CSV”保存测量结果。Ctrl+S保存模型后，下次进入仍可读取测量记录。
本功能测量当前模型尺寸；模型依图纸和照片拟合，并非新现场实测数据。

本次修正：
1. 五扇房内卫生间窗改高窗：一、二楼左右及三楼右侧。
   窗台距本层地面1.80米，窗高0.80米，保留中央竖框，取消横档。
   墙洞、外饰面、窗台同时改动；三楼左侧普通房间大窗保留。
2. 内大门雕花柱与厨房砖墙贴紧，接到门楼檐底，不留透空缝；取消上版前侧平板。
   砖墙正面仍位于原白墙面，雕花及门扇动作保留。
3. 厨房底层屋面修为两片平直坡面，瓦排采用统一起点、节距及搭接；消除斜向扭曲带。
   原屋脊、镬耳、门楼及储藏房瓦面保留，两房交谷衔接保持。
4. 储藏房入口、过渡地带及檐廊统一现有浅灰色地面材质，消除米黄色拼接。
   旧地坪和台阶标高保持，过渡面层顺原坡面贴合。

Reports中的八张检查图、测量界面截图及全部验证报告对应同一原生模型哈希。
References收录本次八张参考图。Blender文件已打包贴图。
Sources为修改和检查记录，重建依赖本机原有几何库和V24.24源文件。
本版独立保存，V24.24未覆盖。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf-8-sig')
(O/'测量使用方法.txt').write_text(readme[readme.index('测量（'):readme.index('本次修正：')],encoding='utf-8-sig')
refs=O/'References';refs.mkdir(exist_ok=True)
for t in ['151458','151716','175749','175827','175910','175946','180153','180416']:
 p=Path('D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg');shutil.copy2(p,refs/p.name)
sources=O/'Sources';sources.mkdir(exist_ok=True)
for n in ['common','probe','probe_extra','geometry','roof','build','verify','solid_qa','physics_qa','measure_tools','measure_math_qa','roam_controller','start_roam','render','launcher_smoke','package','prepare_scripts']:
 p=W/('v24_25_'+n+'.py');shutil.copy2(p,sources/p.name)
for n in ['v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:shutil.copy2(W/n,sources/n)
for n in ['Source.json','Prepared_Geometry.json','Inventory.json','Material_Comparison.json']:shutil.copy2(D/n,sources/n)
(R/'V24_25_Delivery_QA.json').write_text(json.dumps({'status':'PASS_FINAL_DELIVERY','model_sha256':h,'source_sha256':src['sha256'],'checks':summaries,'review_views':views,'measurement_demo':'V24_25_Measure_UI.png','model_measurements_are_not_new_site_survey':True},ensure_ascii=False,indent=2),encoding='utf8')
files=[p for p in O.rglob('*')if p.is_file()and p.suffix!='.blend1'and not p.name.startswith('Draft_')and p.name!='Manifest_SHA256.json']
manifest={p.relative_to(O).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size}for p in files};(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');files.append(O/'Manifest_SHA256.json')
archive=W.parent/'outputs/Production_1QK_Blender_V24_25_Windows_Gate_Roof_Measure_Roam.zip';archive.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,Path('Rebuild_V24_25')/p.relative_to(O))
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for rel,e in manifest.items():
  with z.open('Rebuild_V24_25/'+rel)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==e['sha256'],rel
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'model_sha256':h,'files':len(files),'checks':summaries},ensure_ascii=False),flush=True)
