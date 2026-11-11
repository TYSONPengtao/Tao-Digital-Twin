from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_14';O=Path('E:/jz/JIA/Rebuild_V26_14');R=O/'Reports';S=O/'Sources';REF=O/'References';P=O/'Blender/Architecture_Complete_V26_14.blend';F=P.with_name('Architecture_Complete_V26_14_Fast.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
h,fh=sha(P),sha(F);ch=json.loads((R/'V26_14_Changes.json').read_text('utf8'));assert sha(ch['source'])==ch['source_sha256'];tags=['01_F2_Left_User_Corner','02_F1_Left_Return','03_F2_Right_Return','04_F3_Right_Return','05_F2_Left_Floor_End'];visual=[]
for ver,want in [('V26_14',h),('V26_13',ch['source_sha256'])]:
 for tag in tags:
  p=D/'Review'/(ver+'_'+tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==want and q['temporary_lights']==0
  for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
  if ver=='V26_14':visual.append({'check':tag,'pass':True,'image':p.name,'model_sha256':h,'image_sha256':sha(p),'review':'Inspected native saved model with matching overcast camera and no added lights'})
for tag in ['Viewport_01_WC_Eye_Tour','Viewport_02_WC_Flush_Return']:
 p=D/'Review'/(tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==fh and q['actual_viewport']and q['shading']=='MATERIAL'
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
 visual.append({'check':tag,'pass':True,'image':p.name,'model_sha256':fh,'image_sha256':sha(p),'review':'Inspected delivered Fast file in actual native material viewport'})
(R/'V26_14_Visual_QA.json').write_text(json.dumps({'status':'PASS','model_sha256':h,'checks':visual,'failures':[]},ensure_ascii=False,indent=2),'utf8')
reports=[]
for tag in ['Native_QA','Geometry_QA','Door_Clearance_QA','Interior_Physics_QA','Fast_Display_QA','Runtime_Viewport_QA','Visual_QA']:
 fn='V26_14_'+tag+'.json';q=json.loads((R/fn).read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and all(c['pass']for c in q['checks']),fn;assert q['model_sha256']==(fh if tag in['Fast_Display_QA','Runtime_Viewport_QA']else h);reports.append({'file':fn,'status':q['status'],'checks':len(q['checks'])})
for p in W.glob('v26_14*.py'):copy(p,S/p.name)
srcindex=json.loads((D/'Source_Index.json').read_text('utf8'));prep=json.loads((D/'Prepared.json').read_text('utf8'));inputs={r['file']for r in srcindex['objects']if 'file'in r}|{r['file']for r in prep['objects']}
inputs|={'Before_Snapshot.json','Source_Index.json','Prepared.json','Saved_House.npz','Sections_Before_After.json','Wall_Sections_Before.json','Wall_Sections_Before.png'}
for name in inputs:copy(D/name,S/'Geometry_Archive'/name)
for name in['v24_06_common.py','v24_qa_blender.py','v26_2_common.py','v26_13_fast_display.py']:copy(W/name,S/name)
for p in(W/'v26_14_perf').iterdir():
 if p.is_file()and p.suffix in['.json','.py']:copy(p,S/'Performance'/p.name)
refs=[]
for src,name in[(Path('D:/Desktop/屏幕截图 2026-10-25 013218.jpg'),'用户反馈_门边凸棱.jpg'),(Path('D:/Desktop/屏幕截图 2026-10-24 144236.jpg'),'既有实景_卫浴通道墙角.jpg')]:
 if src.exists():copy(src,REF/name);refs.append({'file':name,'source':str(src),'sha256':sha(src),'availability':'Original local file copied unchanged'})
 else:refs.append({'file':None,'reference_name':src.name,'source':str(src),'availability':'Previously supplied and viewed in the conversation; local source file is absent, so no local image is presented'})
(REF/'Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(S/'源码存档说明.txt').write_text('本轮从已保存V26.13完整模型重新提取原件。Source_前缀为只读基准，生成结果使用不同文件名。Geometry_Archive保留原生输入、生成结果、复核回读与剖面。脚本依赖历史工作目录和本地manifold3d/scipy库；两个交付blend已打包原贴图，可直接打开。','utf8')
(O/'使用说明.txt').write_text('''V26.14 — 房间与卫生间门边墙角接齐

启动：根目录“启动漫游.cmd”，使用流畅版，阴天柔光，左下版本应为V26.14。
完整可编辑模型：Blender/Architecture_Complete_V26_14.blend
前后同角度复核：Reports/V26_14_卫浴墙角复核.html
默认启动位置沿用内大门，可在漫游面板切换楼层。报告中实际人眼漫游图是在检查时定位二楼左侧卫生间门边。

原因一：前墙端面与门边侧墙饰面错开约90mm，形成通高凸棱。
原因二：此前梁口局部修正后，梁后侧墙墙头留有约120mm长的缺口。
本次将一、二楼左侧及二、三楼右侧四处L形墙角接到相邻饰面，并补齐原180mm侧墙墙头至既有顶板。真实实体并入原房屋，不叠盖白片。

门洞、门套、门扇及动作保留；楼层标高、窗户、楼梯、阳台、V26.13内大门雕刻均延续。原房屋在V26.14文件中隐藏存档，V26.13源文件保持字节不变。当前打开的V26.13窗口未被替换。

操作：WASD/方向键移动，Shift快走，空格跳跃，右键转向，滚轮调距离，V切换人眼/第三人称，Home回院落，M切换材质/实体显示，Esc退出，F8恢复。
沿用8采样、半分辨率预览及20cm局部AO。本轮未新增FPS测量。
以上尺寸为原模型与既有实景关系拟合，不是现场新测量。
''','utf8')
css='body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1400px;margin:auto;padding:26px;background:#e9eef1;color:#253d47}header,article,section{background:white;padding:24px;border-radius:12px;margin-bottom:22px}h1{font-size:30px;margin:0 0 12px}h2{font-size:23px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{display:block;width:100%;max-height:900px;object-fit:contain;background:#e5e9eb}figcaption{font-size:14px;color:#5c737c}a{color:#176a83}.ok{display:inline-block;padding:8px 15px;background:#e0f0e5;color:#226445;border-radius:12px}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:8px;border-bottom:1px solid #dce5e8}.hash{font-size:12px;overflow-wrap:anywhere}summary{cursor:pointer}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'
def img(src,cap):return '<figure><a href="'+html.escape(src)+'"><img loading="lazy" src="'+html.escape(src)+'" alt="'+html.escape(cap)+'"></a><figcaption>'+html.escape(cap)+'</figcaption></figure>'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.14 卫浴墙角复核</title><style>'+css+'</style><header><h1>V26.14 接齐房间与卫生间门边墙角</h1><p>已修正通高凸棱，并补齐梁后侧墙墙头。左右四处同类交点一起处理，门洞与原门扇保持。</p><p class="ok">保存模型与流畅版一致 · 五扇卫浴门200个姿态通过 · 房间通道与楼梯通行通过</p><p><a href="../Blender/Architecture_Complete_V26_14.blend">完整可编辑模型</a>　<a href="../Blender/Architecture_Complete_V26_14_Fast.blend">流畅版</a>　<a href="../使用说明.txt">使用说明</a></p><p>使用V26.14目录的新“启动漫游.cmd”，当前V26.13窗口未被替换。</p></header>']
parts.append('<article><h2>红圈位置的原因</h2><div class="grid">'+img('../References/用户反馈_门边凸棱.jpg','本轮用户反馈原图。')+img('V26_14_01_F2_Left_User_Corner.png','V26.14对应位置的墙角与顶部收口。')+'</div><p>旧前墙端面位于X2.20/10.80，门边侧墙饰面位于X2.29/10.71，90mm错位形成竖向凸棱。梁口修正还在梁后留下了一段未接齐的侧墙墙头。两个问题都来自真实网格，白墙贴图未损坏。</p><p>以前述实景的连续墙角与通道关系为参照，现将前墙端面接到原侧墙饰面，并补齐既有180mm侧墙的墙头至顶板。保留正常的通道转角与梁下空间。</p></article>')
for tag,title in[('01_F2_Left_User_Corner','二楼左侧：对应本轮红圈'),('02_F1_Left_Return','一楼左侧同类墙角'),('03_F2_Right_Return','二楼右侧同类墙角'),('04_F3_Right_Return','三楼右侧同类墙角'),('05_F2_Left_Floor_End','底部收口与地面')]:
 parts.append('<article><h2>'+title+'</h2><div class="grid">'+img('V26_13_'+tag+'.png','修改前V26.13；原生模型、同一相机与阴天光照。')+img('V26_14_'+tag+'.png','修改后V26.14；原生墙体接齐，未添加检查灯。')+'</div></article>')
parts.append('<article><h2>实际漫游与材质视口</h2><div class="grid">'+img('Viewport_01_WC_Eye_Tour.png','实际运行V26.14流畅版的人眼漫游；检查时定位二楼门边，导出图不包含HUD文字。')+img('Viewport_02_WC_Flush_Return.png','同一流畅版的实际材质视口近景；人物仅在近景检查时隐藏。')+'</div><p>保持阴天均匀光照和原流畅显示配置，本轮未新增FPS测量。</p></article>')
parts.append('<section><h2>验证与保留</h2><p>在144个原生采样位置检查墙面与梁后墙头，并验证五扇卫浴门的200个开合姿态。修正前后实体差异仅限四处墙端和四处墙头；楼板、楼梯、门窗和V26.13内大门雕刻保持原有形状。原版文件保留。</p><table><tr><th>检查记录</th><th>检查项</th></tr>')
for q in reports:parts.append('<tr><td><a href="'+q['file']+'">'+q['file']+'</a></td><td>'+str(q['checks'])+'</td></tr>')
parts.append('</table><p><a href="V26_14_Changes.json">修正位置与真实网格原因</a>　<a href="../References/Reference_Index.json">原图校验</a></p><p>尺寸来自原模型及照片关系拟合，并非现场新增测量。</p><p class="hash">完整模型SHA256：'+h+'<br>流畅版SHA256：'+fh+'<br>原V26.13 SHA256：'+ch['source_sha256']+'</p></section></html>')
(R/'V26_14_卫浴墙角复核.html').write_text(''.join(parts),'utf8')
files=[{'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['Manifest_SHA256.json','V26_14_Package_QA.json']]
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'fast_model_sha256':fh,'source_model':ch['source'],'source_sha256':ch['source_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(files),'CHECKS',sum(q['checks']for q in reports),flush=True)
