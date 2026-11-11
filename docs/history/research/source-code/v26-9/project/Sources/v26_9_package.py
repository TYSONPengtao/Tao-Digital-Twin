from pathlib import Path
import json,hashlib,shutil,sys,html
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_9_views import VIEWS
D=W/'v26_9';O=Path('E:/jz/JIA/Rebuild_V26_9');R=O/'Reports';S=O/'Sources';REF=O/'References';P=O/'Blender/Architecture_Complete_V26_9.blend';F=P.with_name('Architecture_Complete_V26_9_Fast.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);fh=sha(F);changes=json.loads((R/'V26_9_Changes.json').read_text('utf8'));source_h=changes['source_sha256'];assert sha(changes['source'])==source_h
titles=['一楼：下部固定玻璃与缩短的开启扇','窗脚：斜面与窄门垛的完整收口','二楼：开启扇下面为实墙低窗台','三楼：降低后的水平通道护栏','三楼：清除通道顶面多余下凸结构','房间：保留实景门侧墙垛，回收多包饰面','阳台：罗马柱连接处连续四边','厨房内部：墙面与原木构清开','厨房外侧：青砖墙顶贴合原山墙帽','储藏房石栏：原端部延续抵到次照壁','两房青砖交接：清除外侧白缝','内大门：提高门头，缩小上方大片留白','内大门：原横楣雕刻仅整体提高，侧柱石画保留','屋后：双轨水平推拉窗，左扇开启状态','露台雨棚：移除补光灯穿出形成的白片','总览：本版保存的阴天柔光']
visual=[]
for (tag,*_),title in zip(VIEWS,titles):
 p=D/'Review'/('After_'+tag+'.png');j=p.with_suffix('.json');q=json.loads(j.read_text('utf8'));assert q['model_sha256']==h and q['extra_lights']==0,(tag,'stale review')
 assert p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
 for src in [p,j]:shutil.copy2(src,R/src.name)
 visual.append({'check':title,'pass':True,'image':p.name,'image_sha256':sha(p),'camera':q['camera'],'review':'Visually inspected; saved native model and saved lighting, with geometric checks in linked reports'})
(R/'V26_9_Visual_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS','checks':visual,'failures':[],'scope':'The sixteen specified viewpoints and reference relationships; source scan background artifacts are retained.'},ensure_ascii=False,indent=2),'utf8')
for tag in ['09_Kitchen_North_Outside','10_Storage_Fence_End','11_Brick_Junction','12_Gate_Front','15_Terrace_Roof_White_Fragment']:
 p=D/'Review'/('Before_'+tag+'.png');j=p.with_suffix('.json');assert json.loads(j.read_text('utf8'))['model_sha256']==source_h
 for src in [p,j]:shutil.copy2(src,R/src.name)

reports=[]
for tag in ['Native_Readback_QA','Protected_Original_QA','Geometry_QA','Native_Specific_QA','Specific_Geometry_QA','Interior_Physics_QA','Fast_Display_QA','Visual_QA']:
 fn='V26_9_'+tag+'.json';q=json.loads((R/fn).read_text('utf8'));assert not q['failures']and all(c['pass']for c in q['checks']),(fn,q['failures'])
 assert q['model_sha256']==(fh if tag=='Fast_Display_QA'else h),(fn,'stale check hash')
 if tag=='Fast_Display_QA':assert q['source_sha256']==h
 reports.append({'file':fn,'checks':len(q['checks']),'status':q['status']})

for d in [S,REF]:d.mkdir(exist_ok=True)
prep=json.loads((D/'Prepared_All_Geometry.json').read_text('utf8'))
for p in [D/'Prepared_All_Geometry.json',D/'Prepared_Geometry.json',D/'Extra_Source_Index.json',D/'Site_Probe.json',D/'Roof_White_Fragment_Probe.json',D/'Fragment_Raycast.json',D/'Corner_Raycast.json']+[D/r['file']for r in prep['objects']]:shutil.copy2(p,S/p.name)
for rr in json.loads((D/'Extra_Source_Index.json').read_text('utf8')):shutil.copy2(D/rr['file'],S/rr['file'])
for p in W.glob('v26_9*.py'):shutil.copy2(p,S/p.name)
for name in ['v26_2_common.py','v26_1_common.py','v24_16_common.py','v24_32_rail_profiles.py','v26_8_native_cleanup.py','v26_8_fast_display.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,S/name)
rail=S/'Railing';rail.mkdir(exist_ok=True)
for p in(W/'v26_9_railing').iterdir():
 if p.is_file()and p.suffix in ['.py','.json','.npz']:shutil.copy2(p,rail/p.name)
shutil.copy2(W/'v26_9_perf/Fast_Build.json',S/'Performance/Fast_Build.json')
(S/'源码存档说明.txt').write_text('本目录存放本轮几何输入、修正脚本与检查证据。它依赖原工作目录 '+str(W)+'、历史几何缓存、Blender及本地Python库，不是独立可移植的复建程序。请使用包根目录的启动漫游.cmd打开模型。','utf8')
refs=['142610','142814','143050','143117','143426','143452','144236','144430','144516','144653','145108','145131','145540','145636','145618','150124','150401','150646','150915','095156','095619','130324']
refrows=[];available_refs=[]
for k in refs:
 name='屏幕截图 2026-10-24 '+k+'.jpg';original=Path('D:/Desktop')/name
 candidates=[original,Path('E:/jz/JIA/Rebuild_V26_8/References')/name];p=next((p for p in candidates if p.exists()),None)
 if p:
  shutil.copy2(p,REF/name);available_refs.append(k);refrows.append({'name':name,'source_path':str(p),'packaged_path':'References/'+name,'sha256':sha(p),'status':'Local original copied unchanged'})
 else:refrows.append({'name':name,'original_user_path':str(original),'packaged_path':None,'status':'Image was supplied and inspected in chat; declared local source file is absent at packaging time. View the original attachment in chat.'})
(REF/'Reference_Index.json').write_text(json.dumps(refrows,ensure_ascii=False,indent=2),'utf8')

readme='''V26.9 — 本轮实景与截图修正

漫游：启动漫游.cmd（默认流畅版、阴天柔光）
完整可编辑模型：Blender/Architecture_Complete_V26_9.blend
流畅模型：Blender/Architecture_Complete_V26_9_Fast.blend
逐项对照：Reports/V26_9_实景与修正复核.html

本轮：一楼房间湾窗分出下部固定玻璃，开启扇缩短，30cm实墙窗脚保留；二三楼窗台比原石扶手相对等高位置降低100mm，开启扇下面为实墙。斜窗台和窄门垛下部补齐。实景有门侧墙垛，保留原生柱体，只回收多包饰面，连接墙保持连续。三楼标注的下凸顶梁清至原平顶，水平通道护栏降低150mm，四条楼梯斜握柄、半转回弯及100mm梯井继承前版修正。阳台边带补成完整矩形四边，罗马柱保留。

厨房北山墙恢复此前被内退280mm的外侧墙线，180mm墙身与200mm转角相接，按原山墙帽的实际下沿补全封口；室内墙面与原木架清开，室外青砖墙顶连续。储藏房石栏从原截断端继续接到次照壁，两房外角白缝改青砖，室内白墙保留。

内大门门楣和木门头提高400mm，429mm大块素面承接段缩成22mm隐蔽承接。两侧原雕刻石画不变形，横楣三块浮雕只整体平移。屋后9樘窗改双轨水平推拉，共20扇；保留原窗洞与上部固定亮窗。露台顶白月牙实际是圆形柔光灯与低雨棚相交，现将整盏灯移到棚下；雨棚实体与材质保留。

窗动画：退出漫游后，时间轴1帧关闭、40帧左扇开启、60帧关闭、80帧右扇开启、100帧关闭。漫游默认40帧。WASD/方向键移动，Shift快走，空格跳跃，右键拖动转向，滚轮调距离，V切换人眼/第三人称，M切换材质/实体显示，Esc退出，F8恢复。

保存原有阴天环境与低对比显示，厨房增设宽柔补光。流畅版继承已验证的待机/失焦跳过更新控制器与轻量显示设置；几何、贴图、动作及碰撞网格与完整模型一致。保留全部原照片与共享材质；原次照壁11件、院落入口坡和前版修正不变。旧V26.8文件保持原字节。

检查：从保存文件重新打开读取，逐项几何、UV、原构件保护、窗扇开合避让、63项实际胶囊漫游物理检查与16张指定视角图。检查范围和模型SHA256见报告。场景原扫描背景仍保留其既有残片与贴图周期；本轮没有新增现场测绘。30cm来自用户明确说明，其余调整量是照片与原模型关系拟合。

本轮新上传标注图可在聊天原消息中复看；References只打包当前本地可读的原图，逐张来源与缺失本地路径见Reference_Index.json。
Sources为依赖历史工作目录的输入与脚本存档。
'''
(O/'使用说明.txt').write_text(readme,'utf8')
css='''body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1420px;margin:0 auto;padding:30px;background:#edf0f2;color:#27343d}header,article,section{background:white;border-radius:12px;padding:25px;margin-bottom:22px}h1{font-size:30px;margin:0 0 12px}h2{font-size:22px}p{margin:10px 0}a{color:#165e79}img{width:100%;display:block;background:#dfe5e7;max-height:850px;object-fit:contain}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption{font-size:14px;color:#59666e;margin-top:8px}.ok{display:inline-block;background:#e1f2e9;padding:6px 14px;border-radius:20px;color:#176242}.hash{font-size:12px;overflow-wrap:anywhere}.links a{margin-right:24px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #d8e0e4;text-align:left;padding:9px}summary{cursor:pointer}small{color:#59666e}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'''
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.9 实景与修正复核</title><style>'+css+'</style><header><h1>V26.9 实景与修正复核</h1><p>雨棚白片清除；屋后改推拉窗；内大门提高并保留雕刻石画。本页与模型均为本次保存版本。</p><p class="ok">'+str(sum(r['checks']for r in reports))+'项检查通过 · 63项实际漫游物理检查 · 16张指定视角图</p><p>默认使用包根目录的“启动漫游.cmd”打开流畅版；阴天柔光已保存。</p><p class="links"><a href="../Blender/Architecture_Complete_V26_9.blend">完整可编辑模型</a><a href="../Blender/Architecture_Complete_V26_9_Fast.blend">流畅模型</a><a href="../使用说明.txt">使用说明与窗动画</a></p></header>']
def img(src,cap):return '<figure><a href="'+html.escape(src)+'"><img loading="lazy" src="'+html.escape(src)+'" alt="'+html.escape(cap)+'"></a><figcaption>'+html.escape(cap)+'</figcaption></figure>'
comparisons=[('露台顶白片：补光灯从雨棚下穿出，已移到棚下','15_Terrace_Roof_White_Fragment'),('内大门：缩小顶部留白，原石画保留','12_Gate_Front'),('厨房北端：按原山墙帽补全青砖封口','09_Kitchen_North_Outside'),('储藏房：原石栏截断端接次照壁','10_Storage_Fence_End'),('青砖交接：外侧白缝收口','11_Brick_Junction')]
for title,tag in comparisons:parts.append('<article><h2>'+title+'</h2><div class="grid">'+img('Before_'+tag+'.png','修改前 · V26.8')+img('After_'+tag+'.png','修改后 · 本次保存的V26.9')+'</div></article>')
parts.append('<section><h2>窗台、墙体和扶手的处理依据</h2><p>一楼分出下部固定玻璃，保留用户确认的30cm实墙窗脚；二三楼开启扇下面为实墙，窗台降低100mm。原误加铁栏继续移除，真实石制栏杆保留。</p><p>144236实景显示门侧存在墙垛，保留原柱体并回收多包的约12.2mm饰面，避免把实景墙垛整体抹平。三楼标注的通道顶面凸起清至原10.22m平顶；通道水平木栏降低150mm，楼梯斜握柄与转折保留。</p><p>厨房此前在V24.28内退280mm，导致北端墙与木架冲突；现恢复外侧墙线，墙顶按现有山墙帽逐段封齐。石栏由栏端接墙，次照壁本体不移动。</p><p>内大门横楣雕刻整体提高400mm，侧柱原石画不拉伸。屋后9樘窗保留洞口和固定上亮，增加双轨20扇水平推拉。</p><small>30cm来自用户明确说明。其余调整尺寸为实景照片与原模型关系拟合，并非现场测绘数据。</small></section>')
for(tag,*_),title in zip(VIEWS,titles):parts.append('<article><h2>'+title+'</h2>'+img('After_'+tag+'.png','由本版保存模型直接渲染；使用保存的阴天光照，无临时附加灯光。')+'</article>')
parts.append('<section><h2>参考图来源</h2><p>本轮新上传标注图已按聊天原消息查看，其桌面源文件当前不可读取；原始附件可在聊天中复看。下列图片为当前可读取并原样打包的实景参考。</p><p><a href="../References/Reference_Index.json">逐张参考图来源记录</a></p><details><summary>展开本地实景参考</summary><div class="grid">')
for k in available_refs:parts.append(img('../References/屏幕截图 2026-10-24 '+k+'.jpg','用户实景参考：2026-10-24 '+k+'；原图未编辑。'))
parts.append('</div></details></section><section><h2>保存文件与检查记录</h2><table><tr><th>记录</th><th>通过项</th></tr>')
for r in reports:parts.append('<tr><td><a href="'+r['file']+'">'+r['file']+'</a></td><td>'+str(r['checks'])+'</td></tr>')
parts.append('</table><p>检查覆盖本轮指定部位。原照片、共享材质与动画保留，次照壁11件按原几何、UV、材质和可见性逐项核对。流畅版未额外宣称本轮新的FPS测量。</p><p class="hash">完整模型SHA256：'+h+'<br>流畅模型SHA256：'+fh+'</p></section></html>')
(R/'V26_9_实景与修正复核.html').write_text(''.join(parts),'utf8')
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd'];assert not list(O.rglob('*.3dm'))
files=[{'file':str(p.relative_to(O)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in ['Manifest_SHA256.json','V26_9_Package_QA.json']]
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'fast_model_sha256':fh,'source_model':changes['source'],'source_sha256':source_h,'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8');print('V26_9_PACKAGED',len(files),'CHECKS',sum(r['checks']for r in reports),h,flush=True)
