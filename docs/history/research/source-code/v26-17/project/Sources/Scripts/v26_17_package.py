from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_17';O=Path('E:/jz/JIA/Rebuild_V26_17');R=O/'Reports';V=R/'Views';V.mkdir(exist_ok=True);S=O/'Sources'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa_names=['Native_QA','Geometry_QA','Fast_Display_QA','Interior_Physics_QA','Window_Motion_QA','Runtime_Viewport_QA'];reports={n:json.loads((R/('V26_17_'+n+'.json')).read_text('utf8'))for n in qa_names};assert all(q['status'].startswith('PASS')and not q['failures']for q in reports.values())
master=O/'Blender/Architecture_Complete_V26_17.blend';fast=O/'Blender/Architecture_Complete_V26_17_Fast.blend';mh,fh=sha(master),sha(fast)
for n,q in reports.items():assert q['model_sha256']==(fh if n in['Fast_Display_QA','Runtime_Viewport_QA']else mh),(n,q['model_sha256'])
cases=[('F1_L_Head_Joint','一楼左侧梁柱窗节点'),('F1_R_Head_Joint','一楼右侧梁柱窗节点'),('F1_L_Full_Window_Jamb','一楼左侧整段窗边'),('F1_R_Full_Window_Jamb','一楼右侧整段窗边'),('F2_L_Full_Window_Jamb','二楼左侧整段窗边'),('F2_R_Full_Window_Jamb','二楼右侧整段窗边'),('F3_R_Full_Window_Jamb','三楼右侧整段窗边'),('F1_R_Entry_Exterior','外侧玻璃门边与窗脚'),('F1_R_Outer_Column','外侧窗角的完整柱身'),('Front_Facade','整栋正立面复核')]
for ver in['V26_16','V26_17']:
 for tag,_ in cases:
  for ext in['png','json']:shutil.copy2(D/'Review'/(ver+'_'+tag+'.'+ext),V)
runtime=reports['Runtime_Viewport_QA']
for row in runtime['captures']:
 for ext in['png','json']:shutil.copy2(D/'Review'/Path(row['image']).with_suffix('.'+ext),V)
refs=[]
for name,label in[('屏幕截图 2026-10-25 090838.jpg','待修正窗边'),('屏幕截图 2026-10-25 145947.jpg','实景梁柱、墙与窗头关系'),('屏幕截图 2026-10-25 150122.jpg','本次轴线图')]:
 p=Path('D:/Desktop')/name;shutil.copy2(p,O/'References'/name);refs.append({'label':label,'file':'References/'+name,'sha256':sha(p)})
ch=json.loads((R/'V26_17_Changes.json').read_text('utf8'));si=json.loads((D/'Input/Source_Index.json').read_text('utf8'));needed=set(ch['geometry_changed'])|{f'BAY_WINDOW_F{b["floor"]}_{b["side"]}_1_Geometry'for b in ch['proof']['bays']};sr=[r for r in si['objects']if r['name']in needed]
for folder in['Input','Prepared','Final','Scripts']:(S/folder).mkdir(exist_ok=True)
for row in sr:shutil.copy2(D/'Input'/row['file'],S/'Input')
(S/'Input/Source_Index.json').write_text(json.dumps(dict(si,objects=sr),ensure_ascii=False,indent=2),'utf8');shutil.copy2(D/'Before_Snapshot.json',S/'Input/Before_Snapshot.json')
for folder in['Prepared','Final']:
 for p in(D/folder).glob('*'):
  if p.is_file():shutil.copy2(p,S/folder)
for name in['Prepared.json','Check_Run.json','Prepared_Geometry_QA.json']:
 shutil.copy2(D/name,S/name)
for name in['probe','prepare','build','build_fast','fast_display','native_qa','geometry_qa','physics_qa','window_motion_qa','native_viewport_review','verify_fast','render','views','diagrams','run_checks','package','verify_package']:
 p=W/('v26_17_'+name+'.py')
 if p.exists():shutil.copy2(p,S/'Scripts')
shutil.copy2(W/'v26_15_native_cleanup.py',S/'Scripts');shutil.copy2(W/'v26_17_perf/Fast_Build.json',R/'V26_17_Fast_Build.json')
for p in Path('E:/jz/JIA/Rebuild_V26_16/Textures').glob('*'):
 if p.is_file():shutil.copy2(p,O/'Textures')
(S/'脚本说明.txt').write_text('保存了本次输入、修改参数、最终读回网格、材质槽、UV和执行脚本。复核脚本依赖原工作区的v26_2_common.py、v24_16_common.py及geomlibs；日常编辑和漫游直接打开本版原生模型即可，无需运行脚本。模型内“V26.17_局部修正原件存档”集合保存了修改前的精确网格。','utf8')
(O/'使用说明.txt').write_text('''V26.17｜梁柱板与固定斜窗接合修正

双击根目录“启动漫游.cmd”进入本版Fast漫游。F8开始/停止，WASD或方向键移动，Shift快走，右键拖动转向，V切换人眼/跟随，空格跳跃，M测量，Esc结束。
完整编辑模型：Blender/Architecture_Complete_V26_17.blend
流畅漫游模型：Blender/Architecture_Complete_V26_17_Fast.blend
结构与前后对照：Reports/V26_17_梁柱板与窗边复核.html

按本次图中的3900+5200+3900轴线核对，恢复原模型梁柱完整节点；五组窗共十处固定斜窗收至柱前，避免窗框反切梁柱。原中央开启扇、窗台标高和后侧滑动窗保持。窗脚与板边在原标高并合，保留铺面边界与阴天流畅显示。
V26.16源模型保留；请从本版入口查看修正。梁柱截面沿用原文件定义，收口尺寸为模型拟合值。
''','utf8')
cards=''.join(f'<section><p class="num">{i:02d}</p><h2>{title}</h2><div class="pair"><figure><img loading="lazy" src="Views/V26_16_{tag}.png"><figcaption>修改前 · V26.16</figcaption></figure><figure><img loading="lazy" src="Views/V26_17_{tag}.png"><figcaption>修改后 · V26.17</figcaption></figure></div></section>'for i,(tag,title)in enumerate(cases,1))
labels={'Native_QA':'原生网格与节点探测','Geometry_QA':'梁柱完整性与窗框避让','Fast_Display_QA':'Fast模型保真','Interior_Physics_QA':'漫游碰撞','Window_Motion_QA':'窗扇开合采样','Runtime_Viewport_QA':'实际材质视口'};qa_html=''.join(f'<a href="V26_17_{n}.json">{labels[n]} · {len(reports[n]["checks"])}项通过</a>'for n in qa_names)
ref_html=''.join(f'<figure><img loading="lazy" src="../{html.escape(r["file"])}"><figcaption>{r["label"]}</figcaption></figure>'for r in refs)
vp_html=''.join(f'<figure><img loading="lazy" src="Views/{r["image"]}"><figcaption>{"实际人眼漫游"if i==0 else "实际Blender材质视口"}</figcaption></figure>'for i,r in enumerate(runtime['captures']))
count=sum(len(q['checks'])for q in reports.values());filename='V26_17_梁柱板与窗边复核.html'
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.17｜梁柱板与窗边复核</title><style>body{{margin:0;background:#f2f4f3;color:#203638;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1240px;margin:auto;padding:42px 28px}}header{{border-bottom:1px solid #cbd6d3;padding-bottom:28px}}h1{{font-size:34px;line-height:1.45}}h2{{font-size:23px;margin:5px 0 18px}}a{{color:#126c71;text-underline-offset:4px}}nav{{display:flex;gap:22px;flex-wrap:wrap}}section{{padding:30px 0;border-bottom:1px solid #cbd6d3}}.pair,.refs,.vp{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:white}}img{{width:100%;display:block;height:auto}}figcaption{{padding:10px 16px;font-size:14px;color:#52706d}}.num,.kicker{{font-size:13px;letter-spacing:2px;color:#65837b}}.num{{margin:0}}.qa{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.qa a{{display:block;background:white;padding:14px}}.status{{display:inline-block;background:#deede2;color:#286146;padding:5px 14px;border-radius:5px}}details{{margin:18px 0}}summary{{cursor:pointer;color:#126c71}}.diagram{{background:white;margin:20px 0}}.node{{max-width:900px;margin:20px auto}}footer{{font-size:13px;color:#627a70;padding:26px 0}}code{{font-size:12px;word-break:break-all}}@media(max-width:760px){{main{{padding:24px 15px}}h1{{font-size:27px}}.pair,.refs,.vp,.qa{{grid-template-columns:1fr}}}}</style><main><header><p class="kicker">建筑重建 / V26.17 / 2026.10.25</p><h1>梁柱完整，窗框止于柱前</h1><p>按本次实景与轴线图复查五组房间窗边，修正十处固定斜窗及其梁柱板节点。</p><p class="status">{count}项复核通过 · 原V26.16保留</p><nav><a href="../Blender/Architecture_Complete_V26_17.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_17_Fast.blend">Fast漫游模型</a><a href="../使用说明.txt">启动说明</a></nav></header><section><h2>这次查明的结构原因</h2><p>原固定斜窗进入了既有柱芯和梁端的范围。前几轮为保持窗框位置，反向裁切了梁柱，虽然补过局部缺角，节点仍然缺少完整的矩形截面。</p><p>此次以3900＋5200＋3900毫米柱轴为基准，恢复原模型的完整柱身、矩形梁和连续板边；十处固定斜窗的端点调整至柱前，中央开启扇保持。窗脚与板边合并为实体，楼板标高、窗台高度及原铺面边界保持。</p><p>室内保留实景中可见的正常柱身突出和梁下挂，节点连续接合，不再出现被窗切出的三角碎角。外侧玻璃门旁保留窄白边，后侧滑动窗、四边阳台和其他已修部位保留。</p><details><summary>本次实景与图纸依据</summary><div class="refs">{ref_html}</div></details><img class="diagram" src="V26_17_轴线与梁柱板平面.svg"><img class="diagram node" src="V26_17_窗框柱前节点.svg"></section>{cards}<section><h2>保存后检查</h2><div class="qa">{qa_html}</div><p>从保存后的原生模型读回网格，核对柱和梁的完整截面；65处梁底、60处柱面及60处板面探测验证节点与标高。十处调整后的固定斜窗不与主体实体相交。所有中央窗框和开启扇保持原网格与动作，40帧共800个窗扇组件姿态采样通过。</p><p>Fast模型与完整模型核对网格、UV、材质、动作和碰撞。延续阴天柔光与既有流畅显示设置，本版未新增FPS测速。</p></section><section><h2>实际Blender视口</h2><p>下列图片来自交付Fast模型的原生材质视口；首图运行实际人眼漫游，其余临时隐藏人物以便检查。没有额外补灯，复核未写回模型。</p><div class="vp">{vp_html}</div></section><footer><p>轴线尺寸取本次图纸。梁柱截面沿用原文件定义，窗边收口为模型拟合，未作为新增现场实测尺寸。</p><p>主模型SHA256：<code>{mh}</code><br>Fast模型SHA256：<code>{fh}</code></p></footer></main></html>'''
(R/filename).write_text(page,'utf8');(R/'V26_17_Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8');(R/'V26_17_Delivery_Summary.json').write_text(json.dumps({'status':'PASS','master_sha256':mh,'fast_sha256':fh,'qa_checks':count,'reports':qa_names,'reference_count':3,'html':str(R/filename)},ensure_ascii=False,indent=2),'utf8')
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['V26_17_Manifest.json','V26_17_Package_QA.json']];(R/'V26_17_Manifest.json').write_text(json.dumps({'version':'V26.17','files':manifest},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(manifest),count,str(R/filename),flush=True)
