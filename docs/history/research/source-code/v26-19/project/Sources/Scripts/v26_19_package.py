from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_19';O=Path('E:/jz/JIA/Rebuild_V26_19');R=O/'Reports';V=R/'Views';S=O/'Sources';V.mkdir(exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
names=['Native_QA','Geometry_QA','Fast_Display_QA','Interior_Physics_QA','Runtime_Viewport_QA']
qs={n:json.loads((R/('V26_19_'+n+'.json')).read_text('utf8'))for n in names}
assert all(q['status'].startswith('PASS')and not q['failures']for q in qs.values())
master=O/'Blender/Architecture_Complete_V26_19.blend';fast=O/'Blender/Architecture_Complete_V26_19_Fast.blend';mh,fh=sha(master),sha(fast)
for n,q in qs.items():assert q['model_sha256']==(fh if n in['Fast_Display_QA','Runtime_Viewport_QA']else mh),(n,'stale QA')
cases=[('01_Front_Pipe_And_Planter','罗马柱旁的推定支管移除，木圆柱改成陶盆'),('02_F3_West_Window_Head','三楼侧窗梁柱交接'),('03_F2_West_Window_Head','二楼同类窗角连接'),('04_F1_West_Window_Head','一楼同类窗角连接'),('05_F3_Hall_Ceiling','三楼楼梯厅梁侧多余包边'),('06_F2_Hall_Ceiling','二楼楼梯厅梁端'),('07_F1_Right_Outer_Window_Head','一楼外侧窗头与柱边')]
for ver in['V26_18','V26_19']:
 for tag,_ in cases:
  for ext in['png','json']:shutil.copy2(D/'Review'/(ver+'_'+tag+'.'+ext),V)
runtime=qs['Runtime_Viewport_QA']
for row in runtime['captures']:
 for ext in['png','json']:shutil.copy2(D/'Review'/Path(row['image']).with_suffix('.'+ext),V)
refs=[]
for n in['屏幕截图 2026-10-25 205051.jpg','屏幕截图 2026-10-25 205237.jpg','屏幕截图 2026-10-25 205157.jpg']:
 p=Path('D:/Desktop')/n;shutil.copy2(p,O/'References'/n);refs.append({'path':'References/'+n,'sha256':sha(p)})
for folder in['Input','Prepared','Final','Scripts']:
 (S/folder).mkdir(exist_ok=True)
 if folder!='Scripts':
  for p in(D/folder).glob('*'):
   if p.is_file():shutil.copy2(p,S/folder)
for name in['Prepared.json','Before_Snapshot.json','Check_Run.json','Prepared_Geometry_QA.json','Pixel_Probe.json','Structure_Sections.json']:
 if(D/name).exists():shutil.copy2(D/name,S/name)
for p in W.glob('v26_19_*.py'):shutil.copy2(p,S/'Scripts')
shutil.copy2(W/'v26_15_native_cleanup.py',S/'Scripts')
shutil.copy2(W/'v26_19_perf/Fast_Build.json',R/'V26_19_Fast_Build.json')
for p in Path('E:/jz/JIA/Rebuild_V26_18/Textures').glob('*'):
 if p.is_file():shutil.copy2(p,O/'Textures')
(S/'脚本说明.txt').write_text('本次原模型索引、修改前快照、输入网格、修改参数、最终读回网格、UV、材质分配、定位证据及脚本随包保留。重跑依赖原工作区 v26_2_common.py、v24_06_common.py、geomlibs 和原 v26 结构索引。日常编辑与漫游直接使用本包原生模型，无需执行重建脚本。原部件隐藏保存在 V26.19_局部修正原件存档 集合。','utf8')
(O/'使用说明.txt').write_text('''V26.19｜梁端、窗角与院内构件修正

双击根目录“启动漫游.cmd”进入本版 Fast 漫游。
F8 开始/停止；WASD 或方向键移动；Shift 快走；右键拖动转向；V 切换人眼/跟随；空格跳跃；M 测量；Esc 结束。
完整编辑模型：Blender/Architecture_Complete_V26_19.blend
流畅漫游模型：Blender/Architecture_Complete_V26_19_Fast.blend
对照报告：Reports/V26_19_梁端窗角与院内构件复核.html

1. 移除罗马柱旁早期推定的 DN100 雨水支管，原罗马柱保留。
2. 将标注的木材实心占位圆柱，按既有实景花盆形态改成收脚陶盆，补出盆沿、内壁和低于盆口的土面。
3. 梁端旧封口沿用了过宽的柱面/包边轮廓，造成凸条和端部台阶。本次按相邻墙面收齐，保留现有原梁芯。
4. 西侧窗边按原矩形柱截面恢复完整连续的柱面，清除梁柱之间的短缺和细碎台阶；统一竖面及底面的白色材质。

本版继承 V26.18 的楼梯板底、白色平台侧面及内大门后部修正，保留原窗扇动作、窗台标高、楼梯井及阴天柔光。延续原 Fast 显示配置，本次没有新增帧率测试。
原 V26.18 保留。当前用户打开的 Blender 窗口没有被替换，请通过本版入口查看。
''','utf8')
cards=''.join(f'<section><p class="num">{i:02d}</p><h2>{title}</h2><div class="pair"><figure><img loading="lazy" src="Views/V26_18_{tag}.png"><figcaption>修改前 · V26.18</figcaption></figure><figure><img loading="lazy" src="Views/V26_19_{tag}.png"><figcaption>修改后 · V26.19</figcaption></figure></div></section>'for i,(tag,title)in enumerate(cases,1))
labels={'Native_QA':'保存后原生模型','Geometry_QA':'结构边界与材质','Fast_Display_QA':'Fast 模型保真','Interior_Physics_QA':'漫游与碰撞','Runtime_Viewport_QA':'实际材质视口'}
links=''.join(f'<a href="V26_19_{n}.json">{labels[n]} · 通过</a>'for n in names)
vp=''.join(f'<figure><img loading="lazy" src="Views/{c["image"]}"><figcaption>{"实际人眼漫游"if i==0 else "实际 Blender 材质视口"}</figcaption></figure>'for i,c in enumerate(runtime['captures']))
reference_html=''.join(f'<figure><img loading="lazy" src="../{html.escape(q["path"])}"></figure>'for q in refs)
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.19｜梁端窗角与院内构件复核</title><style>body{{margin:0;background:#f2f4f3;color:#203638;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1240px;margin:auto;padding:38px 28px}}header{{padding-bottom:28px;border-bottom:1px solid #cbd6d3}}h1{{font-size:33px;line-height:1.5}}h2{{font-size:23px;margin:5px 0 18px}}a{{color:#126c71;text-underline-offset:4px}}nav{{display:flex;gap:20px;flex-wrap:wrap}}section{{padding:30px 0;border-bottom:1px solid #cbd6d3}}.pair,.vp,.refs{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:white}}img{{width:100%;height:auto;display:block}}figcaption{{padding:10px 16px;color:#52706d;font-size:14px}}.num,.kicker{{font-size:13px;color:#65837b;letter-spacing:2px}}.num{{margin:0}}.qa{{display:flex;gap:12px;flex-wrap:wrap}}.qa a{{background:white;padding:14px}}.status{{display:inline-block;background:#deede2;color:#286146;padding:5px 14px;border-radius:5px}}summary{{cursor:pointer;color:#126c71}}footer{{font-size:13px;color:#627a70;padding:26px 0}}code{{font-size:12px;word-break:break-all}}@media(max-width:760px){{main{{padding:24px 15px}}h1{{font-size:27px}}.pair,.vp,.refs{{grid-template-columns:1fr}}}}</style><main><header><p class="kicker">建筑重建 / V26.19 / 2026.10.25</p><h1>梁端与窗角收齐，院内占位构件修正</h1><p>根据最新三张标注，从原始结构截面、网格连接及材质分配定位原因，修正窗角台阶、梁端凸条、细白支管和木色圆柱。</p><p class="status">保存后复核通过 · 原 V26.18 保留</p><nav><a href="../Blender/Architecture_Complete_V26_19.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_19_Fast.blend">Fast 漫游模型</a><a href="../使用说明.txt">启动说明</a></nav></header><section><h2>查明的原因与修正</h2><p>窗头和楼梯厅梁侧的问题来自实体边界。早期屋顶/墙顶封口沿用了较宽的柱面和包边轮廓，超出原梁芯，形成凸条和不连续端头。此次按相邻墙身截面收齐封口，保留已有原梁芯；西侧窗边柱恢复原约 400 × 400 毫米矩形截面，使梁柱交接连续，玻璃净空保持。</p><p>旧封口还混有不同的白色材质分配。此次将竖向完成面和朝下底面分别统一到原白墙和中性白色底面材质；没有用贴图遮盖几何缺口。</p><p>罗马柱旁的细白柱是早期推定的 DN100 雨水支管，本次归档隐藏，罗马柱保留。院内木色圆柱是被赋予 M_Wood 材质的实心花盆占位体；按既有实景中的收脚陶盆重做盆体，补出盆沿、内壁及低于盆口 45 毫米的土面，原位置和底标高保持。</p><p>继承 V26.18 已修好的楼梯板底与楼板连接、平台白色侧面、内大门后部。窗扇动作、各层原标高和阴天柔光保留。</p><details><summary>本次标注与实景依据</summary><div class="refs">{reference_html}</div></details></section>{cards}<section><h2>保存后的实际检查</h2><div class="qa">{links}</div><p>重读保存后的原生网格，核对实体封闭、原梁芯保留、玻璃净空、楼板及踏步标高，并检查更新后的漫游碰撞。上方对照采用相同相机和光照；以下图片来自交付 Fast 模型的实际材质视口。</p><p>Fast 版延续既有流畅显示配置，本次没有新增 FPS 测速。</p><div class="vp">{vp}</div></section><footer><p>旧部件在模型内归档隐藏。当前用户打开的 Blender 窗口未被替换，请从 V26.19 入口查看。</p><p>主模型 SHA256：<code>{mh}</code><br>Fast 模型 SHA256：<code>{fh}</code></p></footer></main></html>'''
(R/'V26_19_梁端窗角与院内构件复核.html').write_text(page,'utf8')
(R/'V26_19_Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(R/'V26_19_Delivery_Summary.json').write_text(json.dumps({'status':'PASS','master_sha256':mh,'fast_sha256':fh,'qa_checks':sum(len(q['checks'])for q in qs.values()),'reports':names,'references':len(refs)},ensure_ascii=False,indent=2),'utf8')
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['V26_19_Manifest.json','V26_19_Package_QA.json']]
(R/'V26_19_Manifest.json').write_text(json.dumps({'version':'V26.19','files':manifest},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(manifest),flush=True)
