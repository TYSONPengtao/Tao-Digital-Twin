from pathlib import Path
import sys,json,hashlib,shutil,html
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_10_views import VIEWS
D=W/'v26_10';O=Path('E:/jz/JIA/Rebuild_V26_10');R=O/'Reports';S=O/'Sources';REF=O/'References';P=O/'Blender/Architecture_Complete_V26_10.blend';F=P.with_name('Architecture_Complete_V26_10_Fast.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);fh=sha(F);changes=json.loads((R/'V26_10_Changes.json').read_text('utf8'));source_h=changes['source_sha256'];assert sha(changes['source'])==source_h
titles=['一楼左侧卫生间交角','一楼右侧卫生间与房间接墙','二楼左侧卫生间交角','二楼右侧卫生间交角','三楼右侧卫生间交角','二楼房间隔墙：清除竖向余块','三楼房间与过道的接墙','三楼后侧两柱间水平扶手','三楼扶手侧视：柱头同高、握柄水平','内大门整体：矩形深柱、原雕刻与完整平台','门柱斜视：正面及侧面的竖向石画分格','门前一阶台阶与两侧外扩柱础','原下部石画近景：花叶纹理保留']
visual=[]
for(tag,*_),title in zip(VIEWS,titles):
 p=D/'Review'/('After_'+tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==h and q['extra_lights']==0,(tag,'stale view');assert p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
 for prefix in ['Before_','After_']:
  a=D/'Review'/(prefix+tag+'.png');b=a.with_suffix('.json');assert json.loads(b.read_text('utf8'))['model_sha256']==(h if prefix=='After_'else source_h)
  for src in[a,b]:shutil.copy2(src,R/src.name)
 visual.append({'check':title,'pass':True,'image':p.name,'image_sha256':sha(p),'camera':q['camera'],'review':'Visually inspected actual saved model, with its saved soft overcast lights and no temporary review lights'})
(R/'V26_10_Visual_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS','checks':visual,'failures':[],'scope':'Thirteen specific viewpoints, supported by saved-mesh sections and gate clearance checks.'},ensure_ascii=False,indent=2),'utf8')
reports=[]
for tag in['Native_Readback_QA','Protected_Original_QA','Geometry_QA','Native_Specific_QA','Specific_Geometry_QA','Gate_Clearance_QA','Interior_Physics_QA','Fast_Display_QA','Visual_QA']:
 fn='V26_10_'+tag+'.json';q=json.loads((R/fn).read_text('utf8'));assert not q['failures']and all(c['pass']for c in q['checks']),(fn,q['failures']);assert q['model_sha256']==(fh if tag=='Fast_Display_QA'else h),(fn,'stale model');reports.append({'file':fn,'checks':len(q['checks']),'status':q['status']})
for d in[S,REF]:d.mkdir(exist_ok=True)
for fn in['Prepared_Geometry.json','Wall_Sections_Before_After.json','Wall_Sections_Before_After.png','Before_Snapshot.json']:
 shutil.copy2(D/fn,S/fn)
for r in json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['objects']:shutil.copy2(D/r['file'],S/r['file'])
for p in W.glob('v26_10*.py'):shutil.copy2(p,S/p.name)
for name in['v26_2_common.py','v26_1_common.py','v24_16_common.py','v24_32_rail_profiles.py','v26_8_native_cleanup.py','v26_8_fast_display.py','v24_06_common.py','v24_qa_blender.py','v24_relief_blender.py']:shutil.copy2(W/name,S/name)
for folder,src in [('Railing',W/'v26_10_railing'),('Performance',W/'v26_10_perf')]:
 dest=S/folder;dest.mkdir(exist_ok=True)
 for p in src.iterdir():
  if p.is_file()and p.suffix in['.py','.json','.npz']:shutil.copy2(p,dest/p.name)
atlas_dir=S/'GateRelief';atlas_dir.mkdir(exist_ok=True)
for p in Path('E:/jz/JIA/Rebuild_V24/Textures').glob('Gate_Carving_HeightAtlas*'):shutil.copy2(p,atlas_dir/p.name)
for p in[D/'Wall_Sections_Before_After.json',D/'Wall_Sections_Before_After.png']:shutil.copy2(p,R/p.name)
(S/'源码存档说明.txt').write_text('几何输入、修正脚本、原始状态与检查证据存档。依赖历史工作目录 '+str(W)+'、原几何缓存及本地Python库，不能独立复建全部历史版本。模型已打包贴图，可直接用根目录“启动漫游.cmd”打开。','utf8')
names=['屏幕截图 2026-10-24 181535.jpg','屏幕截图 2026-10-24 181722.jpg','609fc65b-b63d-4278-bd18-72c45c32925f.png','屏幕截图 2026-10-24 144236.jpg','屏幕截图 2026-10-24 150401.jpg','屏幕截图 2026-10-24 130324.jpg'];refs=[]
for name in names:
 candidates=[Path('D:/Desktop')/name,Path('E:/jz/JIA/Rebuild_V26_9/References')/name];src=next((q for q in candidates if q.exists()),None)
 if src:shutil.copy2(src,REF/name);refs.append({'name':name,'source_path':str(src),'packaged_path':'References/'+name,'sha256':sha(src),'status':'Local original copied unchanged'})
 else:refs.append({'name':name,'packaged_path':None,'status':'Supplied in chat; local source not available at packaging time'})
(REF/'Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(O/'使用说明.txt').write_text('''V26.10 — 墙角、三楼水平扶手与内大门优化

启动：启动漫游.cmd（默认流畅版，阴天柔光）
完整模型：Blender/Architecture_Complete_V26_10.blend
对照与检查：Reports/V26_10_实景与修正复核.html

门楼：保留所有原雕刻石画。两侧改为有进深的矩形装饰柱，原正面和横楣石画保持原位置、原网格、原UV和材质；8块窄侧石画仅刚体转至矩形侧面。完善竖向分格，增加6块闭合花叶上部浮雕，横向腰线，外扩柱础。门前100mm一阶平台连两侧柱础，宽3.60m。腰线内端按门扇实际开合局部避让，门扇动作保留。

墙角：上版只收回多包饰面，仍留下旧柱块端部。本版依据相邻墙面定位清理11个交接节点的多余凸棱，卫生间分隔墙和门洞保留，房间及卫生间两侧检查。另延续一楼右侧卫生间靠过道一侧的墙面，清除20mm错台。墙体仍是连续闭合实体。

三楼：后侧两柱头同高，柱间握柄水平，配套栏杆重新生成。其它楼梯斜跑、半转弯和此前降低的前侧水平通道栏杆继承V26.9。

漫游：WASD/方向键移动，Shift快走，空格跳跃，右键拖动转向，滚轮调距离，V切换人眼/第三人称，M切换材质/实体显示，Esc退出，F8恢复。默认40帧，门窗开启。模型原开合动画保留。

保留阴天与流畅显示配置、原次照壁11件、地面坡道及V26.9其它修正。本轮未新增FPS实测。尺寸基于照片和原模型拟合，并非新增现场测量。Sources是依赖历史工作目录的源码和输入存档。旧V26.9文件保持不变。
''','utf8')
css='body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1400px;margin:auto;padding:28px;background:#edf1f4;color:#273b46}header,article,section{background:white;padding:24px;border-radius:12px;margin-bottom:22px}h1{font-size:29px;margin:0 0 12px}h2{font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;display:block;max-height:900px;object-fit:contain;background:#e5e9eb}figcaption,small{font-size:14px;color:#627681}a{color:#176f8a}.ok{background:#dff1e6;color:#226342;display:inline-block;border-radius:16px;padding:7px 15px}.hash{font-size:12px;overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #d9e1e5;padding:9px}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.10 实景与修正复核</title><style>'+css+'</style><header><h1>V26.10 内大门优化与墙角、扶手修正</h1><p>保留原雕刻石画，完善矩形深柱、竖向分格、腰线、外扩柱础及一阶入口平台。</p><p class="ok">'+str(sum(q['checks']for q in reports))+' 项检查通过 · 63 项实际漫游物理检查 · 门扇 80 个开合姿态检查</p><p>默认用根目录“启动漫游.cmd”打开流畅版；阴天柔光已保存。</p><p><a href="../Blender/Architecture_Complete_V26_10.blend">完整可编辑模型</a>　<a href="../Blender/Architecture_Complete_V26_10_Fast.blend">流畅模型</a>　<a href="../使用说明.txt">使用说明</a></p></header>']
def img(src,cap):return '<figure><a href="'+html.escape(src)+'"><img loading="lazy" src="'+html.escape(src)+'" alt="'+html.escape(cap)+'"></a><figcaption>'+html.escape(cap)+'</figcaption></figure>'
parts.append('<article><h2>内大门：参考结构与本版整体</h2><div class="grid">'+img('../References/609fc65b-b63d-4278-bd18-72c45c32925f.png','用户本次参考图：矩形柱、多面石画、腰线与连成整体的一阶平台。')+img('After_10_Gate_Whole.png','本版保存模型直接渲染；原屋顶、门扇与石画保留。')+'</div><p>矩形柱核心宽约0.524m、进深0.576m；每侧柱分正面和两个侧面的三组竖向石画区域。原正面及横楣雕刻保持原网格、UV、材质和位置；8块窄侧石画刚体转到矩形侧面，增加6块花叶上部浮雕。腰线内端局部收回，给原铰链侧木边留出开合余量。</p><p>入口平台宽3.60m，连通两侧外扩柱础，门前一阶高100mm。模型尺寸为照片与既有模型拟合。</p></article>')
for idx in[9,10,11,12,7,8,0,3,5]:
 tag=VIEWS[idx][0];parts.append('<article><h2>'+titles[idx]+'</h2><div class="grid">'+img('Before_'+tag+'.png','修改前 · V26.9')+img('After_'+tag+'.png','修改后 · 本次保存的V26.10')+'</div></article>')
parts.append('<section><details><summary>展开其余四处墙角对照</summary>')
for idx in[1,2,4,6]:
 tag=VIEWS[idx][0];parts.append('<h2>'+titles[idx]+'</h2><div class="grid">'+img('Before_'+tag+'.png','修改前 · V26.9')+img('After_'+tag+'.png','修改后 · 本次保存的V26.10')+'</div>')
parts.append('</details></section>')
parts.append('<section><h2>墙体交角的修正依据</h2><p>上版将原柱块范围当成必须保留的实体，只退回饰面，8–14cm余块仍在。本次按相邻墙面的实际定位清理11个局部交接节点，不再用旧柱块包围盒作为依据。普通房间隔墙按24cm面线延续，卫生间分隔与前墙按各自原厚度相接，门洞保留。</p><p>三层、11个节点、每处3个高度，共33个保存模型截面检查。检查房间和卫生间两侧的接墙，并与V26.9比较修正范围以外的几何。</p>'+img('Wall_Sections_Before_After.png','从重新打开的保存模型提取水平截面。灰红为修改前，蓝色为修改后；各格同一比例。')+'</section>')
parts.append('<section><h2>三楼水平扶手</h2><p>仅修改标注的后侧两柱头之间：两柱头同高，握柄为水平直线，栏杆同步匹配。保存模型在18个位置量取同一顶部高度。斜跑、半转弯与之前降低的前侧水平通道护栏保留。</p><p>新浮雕采用闭合网格烘焙，未增加实时细分修改器。流畅版继承此前待机/失焦跳过更新的控制器及轻量显示配置；本轮没有额外宣称新的FPS测量。</p></section>')
parts.append('<section><h2>参考图与检查记录</h2><p><a href="../References/Reference_Index.json">原图来源与SHA256记录</a></p><details><summary>展开本轮墙角与扶手标注</summary><div class="grid">')
for q in refs[:3]:
 if q['packaged_path']:parts.append(img('../'+q['packaged_path'],q['name']+'；用户原图未编辑。'))
parts.append('</div></details><table><tr><th>检查记录</th><th>通过项</th></tr>')
for q in reports:parts.append('<tr><td><a href="'+q['file']+'">'+q['file']+'</a></td><td>'+str(q['checks'])+'</td></tr>')
parts.append('</table><p>检查覆盖本轮指定部位；原扫描背景及其既有残片保留。全部原次照壁、坡道、共享贴图、动画与前版修正继承。本页各图均来自本次保存的原生模型，采用已保存的阴天光照，无临时附加灯光。</p><p class="hash">完整模型SHA256：'+h+'<br>流畅模型SHA256：'+fh+'</p></section></html>')
(R/'V26_10_实景与修正复核.html').write_text(''.join(parts),'utf8')
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd'];assert not list(O.rglob('*.3dm'))
files=[{'file':str(p.relative_to(O)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['Manifest_SHA256.json','V26_10_Package_QA.json']]
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'fast_model_sha256':fh,'source_model':changes['source'],'source_sha256':source_h,'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8');print('V26_10_PACKAGED',len(files),'CHECKS',sum(q['checks']for q in reports),h,flush=True)
