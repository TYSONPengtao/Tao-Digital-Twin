from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_12';O=Path('E:/jz/JIA/Rebuild_V26_12');R=O/'Reports';S=O/'Sources';REF=O/'References'
P=O/'Blender/Architecture_Complete_V26_12.blend';F=P.with_name('Architecture_Complete_V26_12_Fast.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
h,fh=sha(P),sha(F);ch=json.loads((R/'V26_12_Changes.json').read_text('utf8'))
assert sha(ch['source'])==ch['source_sha256']and sha(ch['reference_model'])==ch['reference_sha256']
visual=[]
for tag in['01_Gate_Whole','02_Stone_Corner','03_Stone_Flowers','04_Header']:
 name='V26_12_'+tag
 p=D/'Review'/(name+'.png');m=p.with_suffix('.json');q=json.loads(m.read_text('utf8'));assert q['model_sha256']==h and q['extra_lights']==0
 for src in[p,m]:copy(src,R/src.name)
 visual.append({'check':tag,'pass':True,'image':p.name,'image_sha256':sha(p),'model_sha256':h,'review':'Visually inspected saved native master under saved overcast lighting'})
for tag in['01_Gate_Whole','02_Stone_Corner']:
 p=D/'Review'/('V26_11_'+tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==ch['source_sha256']
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
for tag in['Viewport_01_Actual_Tour','Viewport_02_Stone_Corner']:
 p=D/'Review'/(tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==fh and q['actual_viewport']and q['shading']=='MATERIAL'
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
 visual.append({'check':tag,'pass':True,'image':p.name,'image_sha256':sha(p),'model_sha256':fh,'review':'Visually inspected actual delivered Fast model material viewport, including real tour startup'})
(R/'V26_12_Visual_QA.json').write_text(json.dumps({'status':'PASS','model_sha256':h,'checks':visual,'failures':[]},ensure_ascii=False,indent=2),'utf8')
reports=[]
for tag in['Native_QA','Gate_Clearance_QA','Interior_Physics_QA','Fast_Display_QA','Runtime_Viewport_QA','Visual_QA']:
 fn='V26_12_'+tag+'.json';q=json.loads((R/fn).read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and all(c['pass']for c in q['checks']),fn
 assert q['model_sha256']==(fh if tag in['Fast_Display_QA','Runtime_Viewport_QA']else h)
 reports.append({'file':fn,'status':q['status'],'checks':len(q['checks'])})
for p in W.glob('v26_12*.py'):copy(p,S/p.name)
copy(D/'Before_Snapshot.json',S/'Before_Snapshot.json')
for name in['V24_Probe.json','V26_11_Probe.json','V26_11_Fast_Probe.json']:copy(D/name,S/name)
for name in['v24_06_common.py','v24_qa_blender.py','v26_8_fast_display.py']:copy(W/name,S/name)
for p in(D/'Diagnosis').iterdir():
 if p.is_file()and p.suffix in['.png','.json']:copy(p,R/'Diagnosis'/p.name)
copy(D/'Viewport_Flags_Diagnosis.json',S/'Viewport_Flags_Diagnosis.json')
for p in(W/'v26_12_perf').iterdir():
 if p.is_file()and p.suffix in['.json','.py']:copy(p,S/'Performance'/p.name)
for p in Path('E:/jz/JIA/Rebuild_V24/Textures').iterdir():
 if p.is_file():copy(p,O/'Textures'/p.name)
(S/'源码存档说明.txt').write_text('本轮从指定V24原生文件读取石画网格、UV和拓扑，再适配V26.11的门柱和抬高后的门楣。修正脚本依赖原V24与V26.11模型、历史工作目录和本地库。两个交付blend已打包所有贴图，可直接打开。源文件路径及校验值见Reports/V26_12_Changes.json。','utf8')
refs=[]
for src,name in[(Path('D:/Desktop/屏幕截图 2026-10-24 224803.jpg'),'用户反馈_白板.jpg'),(Path('E:/jz/JIA/Rebuild_V24/Reports/V24_Gate_Carving_Closeup.png'),'V24_原浮雕近景.png'),(Path('E:/jz/JIA/Rebuild_V24/Reports/V24_Gate_Front_Real_Materials.png'),'V24_原门楼整体.png')]:
 if src.exists():copy(src,REF/name);refs.append({'file':name,'source':str(src),'sha256':sha(src)})
(REF/'Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(O/'使用说明.txt').write_text('''V26.12 — 恢复指定V24版本的内大门真实雕刻

启动：根目录“启动漫游.cmd”，默认流畅版、阴天柔光。启动后定位内大门，左下显示V26.12；Home回院落。
完整模型：Blender/Architecture_Complete_V26_12.blend
实际视口与对照：Reports/V26_12_内大门浮雕复核.html

从Architecture_Complete_V24.blend直接读取15幅原石画的基础雕刻网格、拓扑和UV，恢复竹叶、花卉、侧面枝叶和三幅门楣图案；另6幅上段花叶沿用V24原高度图纹样。门楣保持此前抬高40cm的位置，窄侧石画适配当前矩形柱侧面。

原石画表面的起伏差保持；整体入槽后谷部低于石柱基面约2mm，正面隆起最高约18mm，背面延长到16mm并坐入原14mm槽内。活动石画没有实时细分或置换修改器。原V24源件与V26.11照片灰度片均可编辑保留，后者已隐藏。

当前门洞、柱础、一阶平台、门扇及开合动作、整栋建筑、墙梁修正、一楼四边形平台和储藏房梯形青砖保持原数据。完整模型和流畅版建筑几何相同；流畅版沿用此前轻量显示与待机跳过更新配置，本轮未新增FPS测量。

漫游：WASD/方向键移动，Shift快走，空格跳跃，右键拖动转向，滚轮调距离，V切换人眼/第三人称，M切换材质/实体显示，Esc退出，F8恢复。默认40帧，原门窗动作保留。

V24雕刻纹样属于原版本的灰度图建模结果，深度不是现场实测。Sources为依赖原文件和历史工作目录的源码存档。V24及V26.11源模型文件保持不变。
''','utf8')
css='body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1440px;margin:auto;padding:28px;background:#edf1f4;color:#263b45}header,article,section{background:white;padding:24px;border-radius:12px;margin-bottom:22px}h1{font-size:30px;margin:0 0 12px}h2{font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;max-height:850px;object-fit:contain;display:block;background:#e5e9eb}figcaption{font-size:14px;color:#627681}a{color:#176f8a}.ok{color:#236544;background:#dff1e6;padding:8px 15px;border-radius:14px;display:inline-block}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #d9e1e5;padding:8px}.hash{font-size:12px;overflow-wrap:anywhere}summary{cursor:pointer}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'
def img(src,cap):return '<figure><a href="'+html.escape(src)+'"><img loading="lazy" src="'+html.escape(src)+'" alt="'+html.escape(cap)+'"></a><figcaption>'+html.escape(cap)+'</figcaption></figure>'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.12 内大门浮雕复核</title><style>'+css+'</style><header><h1>V26.12 恢复V24内大门原浮雕</h1><p>从用户指定的Architecture_Complete_V24.blend直接提取原石画网格，恢复竹叶、花卉、枝叶和门楣纹样。门洞高度、矩形柱、柱础及单阶平台延续当前版本。</p><p class="ok">原生模型与真实材质视口复核通过 · 门扇80个姿态通过 · 阴天柔光</p><p>用根目录“启动漫游.cmd”打开新版；左下显示V26.12，启动时定位内大门，Home回院落。</p><p><a href="../Blender/Architecture_Complete_V26_12.blend">完整可编辑模型</a>　<a href="../Blender/Architecture_Complete_V26_12_Fast.blend">流畅模型</a>　<a href="../使用说明.txt">使用说明</a></p></header>']
parts.append('<article><h2>V24原纹样与本次恢复结果</h2><div class="grid">'+img('../References/V24_原浮雕近景.png','指定V24版本的历史近景；使用该版原光照。')+img('V26_12_02_Stone_Corner.png','V26.12保存模型近景；使用当前已保存的阴天光照。')+'</div><p>上版整门照片裁切生成的灰度细节偏弱。本次恢复V24的15幅原石画，并保留6幅来自V24高度图的上部花叶。原门楣沿当前版本抬高40cm，侧面图案适配矩形柱面；雕刻起伏差保持。</p></article>')
parts.insert(1,'<article><h2>白板显示的直接原因：流畅版局部遮蔽被关闭</h2><p>下面两图使用同一份真实雕刻网格、同一相机和同一阴天灯光。关闭局部遮蔽时，石画呈白板；启用20cm范围的局部AO后，纹样显现。此前的隐藏状态、局部视图和背面剔除检查均已排除。</p><div class="grid">'+img('Diagnosis/EEVEE_01_AO_Off.png','单变量对照：关闭遮蔽，已恢复的V24网格也显示为平白板。')+img('Diagnosis/EEVEE_02_Local_AO.png','相同网格与灯光：仅启用局部遮蔽，雕刻显现。')+'</div><p>模型和启动配置已保存局部AO：半分辨率、2条光线、8步、20cm范围；漫游仍使用8采样和半分辨率预览。M键可切换实体显示，本轮没有新增FPS测量。参数说明参见<a href="https://docs.blender.org/manual/fi/5.1/render/eevee/render_settings/raytracing.html">Blender5.1官方手册</a>。</p></article>')
for tag,title in[('01_Gate_Whole','整体对照：当前门楼结构与原雕刻'),('02_Stone_Corner','同视角对照：竹叶、花卉与侧面枝叶')]:
 parts.append('<article><h2>'+title+'</h2><div class="grid">'+img('V26_11_'+tag+'.png','修改前V26.11；相同相机与该版已保存的阴天光照。')+img('V26_12_'+tag+'.png','修改后V26.12；相同相机，无附加检查灯光。')+'</div></article>')
parts.append('<article><h2>花卉下段与门楣石画</h2><div class="grid">'+img('V26_12_03_Stone_Flowers.png','下段原花卉石画；真实网格起伏。')+img('V26_12_04_Header.png','三幅门楣石画；位置沿用已抬高的门楣。')+'</div><p>谷部约低于柱面2mm，正面最高隆起约18mm，背面伸入原凹槽形成实体支承。活动石画不使用实时细分或置换修改器。原腰线、门扇和一阶平台保持原数据。</p></article>')
parts.append('<article><h2>真实漫游与材质视口</h2><div class="grid">'+img('Viewport_01_Actual_Tour.png','交付流畅版的真实第三人称漫游视口；检查时在门外定位。')+img('Viewport_02_Stone_Corner.png','同一流畅模型的真实材质视口近景；未替换为离线渲染结果。')+'</div><p>已检查流畅版启动、21块活动石画可见状态和版本号。材质视口采用原阴天光照，没有临时附加灯。流畅版保留同一建筑几何，本轮没有新增FPS测量。</p></article>')
parts.append('<section><h2>保留内容与检查记录</h2><p>整栋建筑、墙梁交接、一楼四边形平台、储藏房梯形青砖、原门窗动作与碰撞网格保持V26.11原数据。V24源件与上版照片灰度片保留为可编辑存档。原版本模型文件校验值保持不变。</p><details><summary>用户反馈原图</summary>'+img('../References/用户反馈_白板.jpg','用户截图。截图本身不能确认当时打开的blend版本；新版漫游已加入V26.12显示。')+'</details><table><tr><th>记录</th><th>检查项</th></tr>')
for q in reports:parts.append('<tr><td><a href="'+q['file']+'">'+q['file']+'</a></td><td>'+str(q['checks'])+'</td></tr>')
parts.append('</table><p><a href="V26_12_Changes.json">原网格来源、配准与入槽深度记录</a>　<a href="../References/Reference_Index.json">历史参考与原图校验</a></p><p>雕刻深度来自原版本的灰度图建模，不能代表现场实测深度。</p><p class="hash">完整模型SHA256：'+h+'<br>流畅模型SHA256：'+fh+'<br>指定V24参考SHA256：'+ch['reference_sha256']+'</p></section></html>')
parts[0]=parts[0].replace('<p>从用户指定的Architecture_Complete_V24.blend','<p>已修复流畅版关闭局部遮蔽导致的白板显示。</p><p>从用户指定的Architecture_Complete_V24.blend')
(R/'V26_12_内大门浮雕复核.html').write_text(''.join(parts),'utf8')
readme=O/'使用说明.txt';readme.write_text(readme.read_text('utf8')+'\n白板显示的直接原因是流畅版关闭EEVEE局部遮蔽。已通过相同网格、相同相机和灯光的A/B对照复现并修复；局部AO已写入模型及启动配置，仍保留8采样与半分辨率。真实材质视口另有导出图及细节梯度检查。\n','utf8')
files=[{'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['Manifest_SHA256.json','V26_12_Package_QA.json']]
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'fast_model_sha256':fh,'source_model':ch['source'],'source_sha256':ch['source_sha256'],'reference_model':ch['reference_model'],'reference_sha256':ch['reference_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8')
print('PACKAGED',len(files),'CHECKS',sum(q['checks']for q in reports),flush=True)
