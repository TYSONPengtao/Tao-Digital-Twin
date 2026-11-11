from pathlib import Path
import json,hashlib,shutil,sys
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_8_views import VIEWS
O=Path('E:/jz/JIA/Rebuild_V26_8');D=W/'v26_8';R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_8.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);reports=[]
for tag in ['Native_Readback_QA','Geometry_QA','Interior_Physics_QA','Protected_Original_QA','Scoped_Overlap_QA','Stair_Well_QA','Window_Sill_QA','Railing_Regression_QA','Overcast_QA','Visual_QA','Dynamic_Visual_QA']:
 name='V26_8_'+tag+'.json';q=json.loads((R/name).read_text('utf8'));assert q['model_sha256']==h,(name,'stale hash');assert not q['failures']and all(c['pass']for c in q['checks']),(name,q['failures']);reports.append({'file':name,'checks':len(q['checks']),'status':q['status']})
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));assert sha(prep['source'])==prep['source_sha256'];assert prep['proof']['stair_gap_fit_m']==.10;assert len(prep['remove'])==15
S=O/'Sources';S.mkdir(exist_ok=True)
for p in[D/'Prepared_Geometry.json']+[D/r['file']for r in prep['objects']]:shutil.copy2(p,S/p.name)
for fn in ['v26_8_prepare.py','v26_8_native_cleanup.py','v26_8_make_railing.py','v26_8_build.py','v26_8_readback.py','v26_8_protection_qa.py','v26_8_geometry_qa.py','v26_8_physics_qa.py','v26_8_overlap_after.py','v26_8_overlap_gate.py','v26_8_render.py','v26_8_views.py','v26_8_dynamic_render.py','v26_8_overcast_qa.py','v26_8_visual_qa.py','v26_8_package.py','v26_2_common.py','v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/fn,S/fn)
for folder in ['v26_8_windows','v26_8_entry_jambs','v26_8_railing','v26_8_stair_audit']:
 target=S/folder;target.mkdir(exist_ok=True);src=W/folder
 for p in src.iterdir():
  if p.is_file()and p.suffix in ['.py','.md','.json']and p.stat().st_size<5000000:shutil.copy2(p,target/p.name)
 for sub in ['Prepared','Foot_Closure']:
  if(src/sub).exists():shutil.copytree(src/sub,target/sub,dirs_exist_ok=True)
 for fn in ['Entry_Jamb_Cutters.npz']:
  if(src/fn).exists():shutil.copy2(src/fn,target/fn)
(S/'源码存档说明.txt').write_text('本目录保存本轮输入和脚本供审阅。它依赖原工作目录 '+str(W)+'、历史几何缓存、Python库与V26.7源模型，不是独立可移植的复建程序包。请按使用说明打开Blender模型和漫游入口，不在Sources中直接运行构建覆盖模型。','utf8')
REF=O/'References';REF.mkdir(exist_ok=True)
for k in ['094935','095156','095619','095737','095716','130324']:
 src=Path('D:/Desktop')/f'屏幕截图 2026-10-24 {k}.jpg';shutil.copy2(src,REF/src.name)
shutil.copytree(W/'v26_8_stair_audit/Representative_References',REF/'楼梯原视频实景',dirs_exist_ok=True)
railref=REF/'扶手实景';railref.mkdir(exist_ok=True)
for k in ['015859','015914']:
 p=Path('E:/jz/JIA/Rebuild_V26_6/References/楼梯实景')/f'屏幕截图 2026-10-23 {k}.jpg';shutil.copy2(p,railref/p.name)
for tag,*_ in VIEWS:
 f=D/'Review'/('After_'+tag+'_Cycles.json');q=json.loads(f.read_text('utf8'));assert q['model_sha256']==h;assert q['temporary_review_fill_watts']==0
 for p in [f,f.with_suffix('.png')]:shutil.copy2(p,R/p.name)
for ext in ['.json','.png']:
 p=D/'Review'/('Before_13_Stair_Well_Overhead_Cycles'+ext);q=json.loads(p.read_text('utf8'))if ext=='.json'else None
 if q:assert q['model_sha256']==prep['source_sha256']
 shutil.copy2(p,R/p.name)
shutil.copytree(D/'Dynamic',R/'楼梯斜视复核',dirs_exist_ok=True)
readme='''Rebuild_V26.8 — 实景结构修正与阴天柔光

模型：Blender/Architecture_Complete_V26_8.blend
漫游：启动漫游.cmd
实景与修正图：Reports/V26_8_实景与修正复核.html

本轮按最新130324实景进一步收窄中央楼梯井；净宽约100mm是照片关系与原模型拟合，不是现场实测。原两跑仅20mm狭缝；早期后墙修正另将一楼下跑切至Y9.50，和实际后墙Y9.68之间形成180mm模型空腔。四跑现均连续贴墙，原11级X/Z、半平台和楼层标高保留，净井两侧各约1.08m。平台完整，扶手内轴随井边调整；恢复较小半转回弯、中心转角柱和起步小U，取消放大的回弯和额外颈环。

按用户明确说明，三层前部房间湾窗原误加的15件铁护栏全部移除，真实二楼石栏保留。一楼窗台按室内完成面起30cm；二三楼与二楼石栏连续扶手顶相对等高（继承模型约1.150m，不取装饰柱头顶）。固定窗、玻璃和活动扇共35组件配合高度，XY/原开合与UV保持在原生浮点精度内。后侧卫生间高窗、楼梯窗等不机械改高。门边白垛参照实景收窄，普通深度不超过240mm；窗框与白墙的竞争共面解除，固定框保持原位置。窗墙基脚原150mm漏空按当前院坪有限封齐，不是新增现场测量数据。

显示与光照已保存为中性阴天环境：关闭直射太阳，保留宽软环境光和室内柔光，低对比AgX。材质预览使用保存的世界与柔光。13张修正图和连续斜视12帧均直接使用保存模型，无临时附加渲染补光。阴天是用户的显示偏好，不表示拍摄当天或现场实测照明。

原V26.7文件未覆盖。原次照壁11构件、院墙分层、门槛、入口坡、后部房间关系、原照片和共享材质保持。专项检查范围见JSON报告：逐级墙侧/井侧射线、井口贯通、支座、共面、玻璃、扶手、63条真实碰撞路线和保存显示设置。静态共面检查与斜视序列用于核查修正区域；不声称全场所有GPU/驱动显示问题均已排除。贴图周期重复和原场景的部分未修改构件接触仍可继续细化。仅保留启动漫游.cmd。

Sources是依赖原工作目录的源码与几何输入存档，不是独立可移植复建程序包。
'''
(O/'使用说明.txt').write_text(readme,'utf8')
style='body{font:17px/1.7 "Microsoft YaHei",sans-serif;max-width:1380px;margin:25px auto;padding:20px;background:#eef1f3;color:#26333b}article{background:#fff;padding:24px;margin:24px 0;border-radius:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}img,video{width:100%;max-height:850px;object-fit:contain;background:#e5e9ec}small{overflow-wrap:anywhere}a{color:#176482}h1{font-size:29px}h2{font-size:22px}@media(max-width:850px){.grid{grid-template-columns:1fr}}'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.8 实景与修正复核</title><style>'+style+'</style><h1>V26.8 实景结构修正与阴天柔光</h1><p>按最新实景收窄梯井并顺直扶手；三层房间窗前无铁栏；保存阴天柔光。原次照壁、石栏、后部高窗、入口坡与门窗开合保留。</p><p>一楼30cm来自用户明确说明；上层窗台约1.150m来自原石扶手等高关系；梯井100mm与门边宽度为照片/模型拟合，未经现场测量。</p>']
pairs=[('门边白墙：实景与修正','../References/屏幕截图 2026-10-24 095156.jpg','After_01_F1_Thin_Door_Jamb_Cycles.png'),('最新扶手实景与较小转折','../References/屏幕截图 2026-10-24 130324.jpg','After_09_Upper_Turn_Cycles.png'),('梯边贴墙：实景与修正','../References/屏幕截图 2026-10-24 095619.jpg','After_05_F1_Step_To_Wall_Cycles.png'),('井口俯视：前版与本版（光照也不同）','Before_13_Stair_Well_Overhead_Cycles.png','After_13_Stair_Well_Overhead_Cycles.png')]
for title,left,right in pairs:parts.append('<article><h2>'+title+'</h2><div class="grid"><img src="'+left+'"><img src="'+right+'"></div></article>')
parts.append('<article><h2>梯边连续斜视复核</h2><video controls loop muted src="楼梯斜视复核/楼梯贴墙斜视复核.mp4"></video><p>12帧相机斜视序列，使用保存的模型和阴天柔光；另有逐级射线和近共面检查。此序列不等同于所有硬件驱动的交互视口测试。</p><img src="楼梯斜视复核/斜视连续帧复核.jpg"></article>')
titles=['一楼门边白条与原黑框','二楼窗台与石扶手同高','一楼30cm窗台，无铁栏','三楼房间窗台，无铁栏','一楼踏步连续贴墙','一楼中央窄井','二楼中央窄井','较小半转回弯与中心柱','楼层柱顺直接合','三楼护栏与井边','室外阴天柔光','室内均匀柔光','中央窄井俯视']
for (tag,*_),title in zip(VIEWS,titles):parts.append('<article><h2>'+title+'</h2><a href="After_'+tag+'_Cycles.png"><img src="After_'+tag+'_Cycles.png"></a></article>')
parts.append('<article><h2>保存模型专项检查</h2><p>修正图均来自本保存文件，没有临时渲染补光。检查覆盖指定部位；不表示整栋模型已完成全场实测还原。原照片贴图仍有周期重复等细化空间。</p><ul>')
for q in reports:parts.append('<li><a href="'+q['file']+'">'+q['file']+'</a>：'+q['status']+'，'+str(q['checks'])+'项</li>')
parts.append('</ul><small>模型SHA256：'+h+'</small></article></html>');(R/'V26_8_实景与修正复核.html').write_text(''.join(parts),'utf8')
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd'];assert not list(O.rglob('*.3dm'))
files=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name!='Manifest_SHA256.json']
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'source_model':prep['source'],'source_sha256':prep['source_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(files),'CHECKS',sum(r['checks']for r in reports),h,flush=True)
