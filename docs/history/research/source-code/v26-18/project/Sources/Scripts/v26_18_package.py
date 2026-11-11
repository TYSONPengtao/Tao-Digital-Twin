from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_18';O=Path('E:/jz/JIA/Rebuild_V26_18');R=O/'Reports';V=R/'Views';V.mkdir(exist_ok=True);S=O/'Sources'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
names=['Native_QA','Geometry_QA','Fast_Display_QA','Interior_Physics_QA','Runtime_Viewport_QA'];qs={n:json.loads((R/('V26_18_'+n+'.json')).read_text('utf8'))for n in names};assert all(q['status'].startswith('PASS')and not q['failures']for q in qs.values())
master=O/'Blender/Architecture_Complete_V26_18.blend';fast=O/'Blender/Architecture_Complete_V26_18_Fast.blend';mh,fh=sha(master),sha(fast)
for n,q in qs.items():assert q['model_sha256']==(fh if n in['Fast_Display_QA','Runtime_Viewport_QA']else mh),(n,'stale QA')
cases=[('01_F1_Slab_Join_Underside','一楼楼梯与二楼楼板下表面'),('02_F1_Slab_Join_Close','一楼接缝近看'),('03_F1_Landing_White_Fascia','一楼平台侧面白色与踏步石材分界'),('04_F2_Slab_Join_Underside','上层同类连接片同步修整'),('05_F2_Landing_White_Fascia','上层半层平台侧面'),('06_Gate_Rear_Right','内大门后部多余红板移除'),('07_Gate_Rear_Whole','内大门后部整体'),('08_Gate_Front_Relief','正面雕刻石柱与门扇保留')]
for ver in['V26_17','V26_18']:
 for tag,_ in cases:
  for ext in['png','json']:shutil.copy2(D/'Review'/(ver+'_'+tag+'.'+ext),V)
runtime=qs['Runtime_Viewport_QA']
for row in runtime['captures']:
 for ext in['png','json']:shutil.copy2(D/'Review'/Path(row['image']).with_suffix('.'+ext),V)
refs=[]
for n in['屏幕截图 2026-10-25 180844.jpg','屏幕截图 2026-10-25 180928.jpg','屏幕截图 2026-10-25 181125.jpg']:
 p=Path('D:/Desktop')/n;shutil.copy2(p,O/'References'/n);refs.append({'path':'References/'+n,'sha256':sha(p)})
for folder in['Input','Prepared','Final','Scripts']:
 (S/folder).mkdir(exist_ok=True)
 if folder!='Scripts':
  for p in(D/folder).glob('*'):
   if p.is_file():shutil.copy2(p,S/folder)
for name in['Prepared.json','Before_Snapshot.json','Check_Run.json','Prepared_Geometry_QA.json']:
 shutil.copy2(D/name,S/name)
for p in W.glob('v26_18_*.py'):
 if p.stem not in['v26_18_pixel_probe','v26_18_stair_analyze']:shutil.copy2(p,S/'Scripts')
for name in['v26_15_native_cleanup.py']:shutil.copy2(W/name,S/'Scripts')
shutil.copy2(W/'v26_18_perf/Fast_Build.json',R/'V26_18_Fast_Build.json')
for p in Path('E:/jz/JIA/Rebuild_V26_17/Textures').glob('*'):
 if p.is_file():shutil.copy2(p,O/'Textures')
(S/'脚本说明.txt').write_text('本次输入、修改参数、最终读回网格、材质槽、UV及脚本均随包保留。重跑依赖原工作区v26_2_common.py、v24_16_common.py、geomlibs及原v26结构输入；日常编辑或漫游直接使用原生模型，无需执行脚本。修改前模型部件保存在V26.18_局部修正原件存档集合。','utf8')
(O/'使用说明.txt').write_text('''V26.18｜楼梯板底、平台侧面与内门后部修正

双击根目录“启动漫游.cmd”进入本版Fast漫游。F8开始/停止，WASD或方向键移动，Shift快走，右键拖动转向，V切换人眼/跟随，空格跳跃，M测量，Esc结束。
完整编辑模型：Blender/Architecture_Complete_V26_18.blend
流畅漫游模型：Blender/Architecture_Complete_V26_18_Fast.blend
对照报告：Reports/V26_18_楼梯板底与内门后部复核.html

修整原楼梯连接片低于楼板底的65mm错台，使原斜板底连续接至楼板底；同类上层节点同步修正。半层平台侧面改白，最后一级踏步立面仍保留石材。移除内大门后固定红色装饰板，保留活动门扇、正面雕刻石柱及门槛。
保留原楼层、踏步与窗台标高，以及V26.17窗边修正、阴天柔光和既有Fast显示设置。当前用户打开的V26.17窗口未替换，请从本版入口查看。
''','utf8')
cards=''.join(f'<section><p class="num">{i:02d}</p><h2>{title}</h2><div class="pair"><figure><img loading="lazy" src="Views/V26_17_{tag}.png"><figcaption>修改前 · V26.17</figcaption></figure><figure><img loading="lazy" src="Views/V26_18_{tag}.png"><figcaption>修改后 · V26.18</figcaption></figure></div></section>'for i,(tag,title)in enumerate(cases,1))
labels={'Native_QA':'保存后原生模型','Geometry_QA':'接缝、标高与材质边界','Fast_Display_QA':'Fast模型保真','Interior_Physics_QA':'漫游与碰撞','Runtime_Viewport_QA':'实际材质视口'};links=''.join(f'<a href="V26_18_{n}.json">{labels[n]} · 通过</a>'for n in names)
vp=''.join(f'<figure><img loading="lazy" src="Views/{c["image"]}"><figcaption>{"实际人眼漫游"if i==0 else "实际Blender材质视口"}</figcaption></figure>'for i,c in enumerate(runtime['captures']))
reference_html=''.join(f'<figure><img loading="lazy" src="../{html.escape(q["path"])}"></figure>'for q in refs)
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.18｜楼梯板底与内门后部复核</title><style>body{{margin:0;background:#f2f4f3;color:#203638;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1240px;margin:auto;padding:38px 28px}}header{{padding-bottom:28px;border-bottom:1px solid #cbd6d3}}h1{{font-size:33px;line-height:1.5}}h2{{font-size:23px;margin:5px 0 18px}}a{{color:#126c71;text-underline-offset:4px}}nav{{display:flex;gap:20px;flex-wrap:wrap}}section{{padding:30px 0;border-bottom:1px solid #cbd6d3}}.pair,.vp,.refs{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:white}}img{{width:100%;height:auto;display:block}}figcaption{{padding:10px 16px;color:#52706d;font-size:14px}}.num,.kicker{{font-size:13px;color:#65837b;letter-spacing:2px}}.num{{margin:0}}.qa{{display:flex;gap:12px;flex-wrap:wrap}}.qa a{{background:white;padding:14px}}.status{{display:inline-block;background:#deede2;color:#286146;padding:5px 14px;border-radius:5px}}summary{{cursor:pointer;color:#126c71}}footer{{font-size:13px;color:#627a70;padding:26px 0}}code{{font-size:12px;word-break:break-all}}@media(max-width:760px){{main{{padding:24px 15px}}h1{{font-size:27px}}.pair,.vp,.refs{{grid-template-columns:1fr}}}}</style><main><header><p class="kicker">建筑重建 / V26.18 / 2026.10.25</p><h1>楼梯板底顺接，平台侧面恢复白色</h1><p>修正一楼楼梯与二楼楼板接缝，并同步处理上层同类连接片；移除内大门后多余红色装饰板。</p><p class="status">保存后复核通过 · 原V26.17保留</p><nav><a href="../Blender/Architecture_Complete_V26_18.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_18_Fast.blend">Fast漫游模型</a><a href="../使用说明.txt">启动说明</a></nav></header><section><h2>查明的原因与修正</h2><p>旧楼梯连接片的底面比楼板底低约65毫米，连接处形成了下凸的矩形错台。此次修整该处实体下表面，让原斜板底连续接至楼板底；同类上层节点同步处理。</p><p>半层平台与连接梁的侧面被误分配为踏步石材。现在改为原白墙材质，并明确分出最后一级踏步的石材立面，平台顶面及其他踏步保持。</p><p>内大门后的固定红色装饰板已移除，背面露出原石柱。活动门扇、五金、正面雕刻、门槛及原有动作保留。V26.17窗边修正、楼板和踏步标高、窄楼梯井及阴天柔光保持。</p><details><summary>本次标注依据</summary><div class="refs">{reference_html}</div></details></section>{cards}<section><h2>保存后的实际检查</h2><div class="qa">{links}</div><p>检查原生网格的封闭性、接缝下表面标高、平台与踏步的材质边界、楼梯井和漫游碰撞。对照图片使用相同相机与光照，以下图片来自交付Fast模型的实际材质视口。</p><p>Fast版延续既有流畅显示设置；本次没有新增FPS测速。</p><div class="vp">{vp}</div></section><footer><p>模型标高与踏步保持；旧部件归档隐藏，可在模型内恢复。当前用户打开的V26.17窗口未被替换，请从V26.18入口查看。</p><p>主模型SHA256：<code>{mh}</code><br>Fast模型SHA256：<code>{fh}</code></p></footer></main></html>'''
(R/'V26_18_楼梯板底与内门后部复核.html').write_text(page,'utf8');(R/'V26_18_Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8');(R/'V26_18_Delivery_Summary.json').write_text(json.dumps({'status':'PASS','master_sha256':mh,'fast_sha256':fh,'qa_checks':sum(len(q['checks'])for q in qs.values()),'reports':names,'references':3},ensure_ascii=False,indent=2),'utf8')
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['V26_18_Manifest.json','V26_18_Package_QA.json']];(R/'V26_18_Manifest.json').write_text(json.dumps({'version':'V26.18','files':manifest},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(manifest),flush=True)
