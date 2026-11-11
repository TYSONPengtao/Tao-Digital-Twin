from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_16';O=Path('E:/jz/JIA/Rebuild_V26_16');R=O/'Reports';V=R/'Views';V.mkdir(exist_ok=True);S=O/'Sources';S.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa_names=['Native_QA','Geometry_QA','Fast_Display_QA','Interior_Physics_QA','Window_Motion_QA','Runtime_Viewport_QA']
reports={n:json.loads((R/('V26_16_'+n+'.json')).read_text('utf8'))for n in qa_names}
assert all(not q['failures']and q['status'].startswith('PASS')for q in reports.values()),[(n,q['status'],q['failures'])for n,q in reports.items()]
master=O/'Blender/Architecture_Complete_V26_16.blend';fast=O/'Blender/Architecture_Complete_V26_16_Fast.blend';mh,fh=sha(master),sha(fast)
for n,q in reports.items():assert q['model_sha256']==(fh if n in['Fast_Display_QA','Runtime_Viewport_QA']else mh),(n,q['model_sha256'])
views=[
 ('F1_L_Head_Joint','一楼左侧 · 窗顶与梁端','补齐窄墙、梁端和窗头交接；修正室内顶面与阳台边板的交叠，并统一收口面的材质。'),
 ('F1_R_Head_Joint','一楼右侧 · 窗顶与梁端','与左侧对应修整，裁除伸入室内完成顶面约2mm的阳台外饰面，清除灰色三角露面。'),
 ('F1_L_Full_Window_Jamb','一楼左侧 · 整段窗边','窗框与窄墙连续接合，移除横档、窗台端部伸出的白色方块。原低窗脚、下部固定玻璃和上部开启扇保持。'),
 ('F1_R_Full_Window_Jamb','一楼右侧 · 整段窗边','同类结构同步处理；窗框、玻璃、窗扇及开合动作保持，窗台高度不变。'),
 ('F2_L_Full_Window_Jamb','二楼左侧 · 整段窗边','整理窗顶、侧墙及窗台端部的接合。开启扇下方保持实体窗台墙。'),
 ('F2_R_Full_Window_Jamb','二楼右侧 · 整段窗边','清理窗框端部的白色凸片，保留现有实体窗台及窄墙尺度。'),
 ('F3_R_Full_Window_Jamb','三楼右侧 · 整段窗边','整理梁头、窄墙边与窗台收口；飘窗上方按原房间完成顶面补齐连续封顶，与原结构合并，消除屋面裁切留下的尖片。既有门窗与通道结构保持。')]
for ver in['V26_15','V26_16']:
 for tag,_,_ in views:
  for ext in['png','json']:shutil.copy2(D/'Review'/(ver+'_'+tag+'.'+ext),V)
runtime=reports['Runtime_Viewport_QA']
for row in runtime['captures']:
 for ext in['png','json']:shutil.copy2(D/'Review'/Path(row['image']).with_suffix('.'+ext),V)
refs=[]
for stamp,label in[('090838','窗顶梁角破缺'),('090818','窗顶、横档与窗台端部的多余白片')]:
 name='屏幕截图 2026-10-25 '+stamp+'.jpg';p=Path('D:/Desktop')/name;assert p.exists();shutil.copy2(p,O/'References'/name);refs.append({'label':label,'file':'References/'+name,'sha256':sha(p)})
ch=json.loads((R/'V26_16_Changes.json').read_text('utf8'));si=json.loads((D/'Input/Source_Index.json').read_text('utf8'));needed=ch['geometry_changed']+[n['frame']for n in ch['proof']['nodes']];sr=[r for r in si['objects']if r['name']in needed]
for folder in['Input','Prepared','Final','Scripts']:(S/folder).mkdir(exist_ok=True)
for r in sr:shutil.copy2(D/'Input'/r['file'],S/'Input')
(S/'Input/Source_Index.json').write_text(json.dumps(dict(si,objects=sr),ensure_ascii=False,indent=2),'utf8');shutil.copy2(D/'Before_Snapshot.json',S/'Input/Before_Snapshot.json')
for folder in['Prepared','Final']:
 for p in(D/folder).glob('*'):
  if p.is_file():shutil.copy2(p,S/folder)
for name in['Prepared.json','Check_Run.json']:
 if(D/name).exists():shutil.copy2(D/name,S/name)
for name in['probe','prepare','build','build_fast','fast_display','native_qa','geometry_qa','physics_qa','window_motion_qa','native_viewport_review','verify_fast','render','views','run_checks','package','verify_package']:
 p=W/('v26_16_'+name+'.py')
 if p.exists():shutil.copy2(p,S/'Scripts')
shutil.copy2(W/'v26_15_native_cleanup.py',S/'Scripts');shutil.copy2(W/'v26_16_perf/Fast_Build.json',R/'V26_16_Fast_Build.json')
for p in Path('E:/jz/JIA/Rebuild_V26_15/Textures').glob('*'):
 if p.is_file():shutil.copy2(p,O/'Textures')
(S/'脚本说明.txt').write_text('输入、准备及保存后读回的网格、材质槽、UV、边界参数与实际执行脚本均保存在此。脚本依赖原工作区 work/v26_2_common.py、v24_16_common.py、geomlibs 及 V26.15 源模型；不是从零生成整栋建筑的独立安装包。直接使用 Blender 原生文件或根目录“启动漫游.cmd”，无需运行复核脚本。修改前原件另存于模型内隐藏的“V26.16_局部修正原件存档”集合。','utf8')
(O/'使用说明.txt').write_text('''V26.16｜窗边与梁角收口修正

双击根目录“启动漫游.cmd”，打开本版 Fast 模型并开始漫游。F8 开始/停止，WASD/方向键移动，Shift 快走，右键拖动转向，V 切换人眼/跟随，空格跳跃，Home 回院落，M 测量，Esc 结束。
完整可编辑模型：Blender/Architecture_Complete_V26_16.blend
流畅显示模型：Blender/Architecture_Complete_V26_16_Fast.blend
图文前后对照：Reports/V26_16_窗边与梁角收口复核.html

本次修正一楼左右、二楼左右及三楼右侧，共五组前房间内侧窗边：连续接合窄墙、梁头与窗台；清除穿入窗框的白色方块、修正窗顶面和侧面材质；一楼两处阳台边板收回室内完成顶面，保留外侧阳台轮廓。三楼右侧飘窗按原房间完成顶面补齐连续封顶，与原结构合并，消除屋面裁切留下的尖片。
原窗框与玻璃、窗扇开合、窗台高度和上版其他修正保持。沿用阴天柔和均匀光照及既有 Fast 显示方案，没有新 FPS 测速。
V26.15 源文件未覆盖。本次从已保存的 V26.15 建立新版本，未操作用户原有未保存的 Blender 窗口。尺寸为既有模型与实景关系拟合，不是新增现场测量。
''','utf8')
cards=[]
for i,(tag,title,detail)in enumerate(views,1):
 cards.append(f'<section><p class="num">{i:02d}</p><h2>{title}</h2><p>{detail}</p><div class="pair"><figure><img loading="lazy" src="Views/V26_15_{tag}.png" alt="V26.15修改前"><figcaption>修改前 · V26.15</figcaption></figure><figure><img loading="lazy" src="Views/V26_16_{tag}.png" alt="V26.16修改后"><figcaption>修改后 · V26.16</figcaption></figure></div></section>')
ref_html=''.join(f'<figure><img loading="lazy" src="../{html.escape(r["file"])}" alt="用户标注图"><figcaption>{r["label"]}</figcaption></figure>'for r in refs)
labels={'Native_QA':'保存后原生网格','Geometry_QA':'局部实体与窗框接合','Fast_Display_QA':'Fast模型保真','Interior_Physics_QA':'漫游碰撞','Window_Motion_QA':'窗扇40帧采样','Runtime_Viewport_QA':'实际材质视口'}
qa_html=''.join(f'<a href="V26_16_{n}.json">{labels[n]} · {len(reports[n]["checks"])}项通过</a>'for n in qa_names)
vp_html=''.join(f'<figure><img loading="lazy" src="Views/{r["image"]}" alt="实际Blender材质视口"><figcaption>{"实际人眼漫游"if i==0 else "实际材质视口 · 窗边检查"}</figcaption></figure>'for i,r in enumerate(runtime['captures']))
count=sum(len(q['checks'])for q in reports.values());filename='V26_16_窗边与梁角收口复核.html'
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.16｜窗边与梁角收口复核</title><style>
body{{margin:0;background:#f3f4f1;color:#1c3031;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1240px;padding:45px 28px;margin:auto}}header{{padding-bottom:32px;border-bottom:1px solid #cbd5d0}}h1{{font-size:34px;line-height:1.4}}h2{{font-size:23px;margin:4px 0 14px}}p{{margin:12px 0}}a{{color:#16625d;text-underline-offset:4px}}nav{{display:flex;gap:22px;flex-wrap:wrap}}.num,.kicker{{font-size:13px;color:#597b71;letter-spacing:2px}}.num{{margin:0}}section{{padding:32px 0;border-bottom:1px solid #cbd5d0}}.pair,.vp,.refs{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:#fff}}img{{display:block;width:100%;height:auto}}figcaption{{padding:10px 16px;font-size:14px;color:#46655b}}.status{{display:inline-block;background:#deecdf;color:#265b3e;padding:5px 14px;border-radius:5px}}.qa{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:20px 0}}.qa a{{display:block;background:#fff;padding:15px}}code{{font-size:12px;word-break:break-all}}footer{{font-size:13px;color:#60736d;padding:28px 0}}details{{margin-top:22px}}summary{{cursor:pointer;color:#16625d}}@media(max-width:760px){{main{{padding:25px 15px}}.pair,.vp,.refs,.qa{{grid-template-columns:1fr}}h1{{font-size:27px}}}}
</style><main><header><p class="kicker">建筑重建 / V26.16 / 2026.10.25</p><h1>窗边破缺与多余结构修正</h1><p>五组前房间内侧窗边已整理为连续接合的墙、梁、窗台与窗框收口。下方对照使用相同相机及阴天光照设置。</p><p class="status">{count}项检查通过 · 800个窗扇组件姿态采样</p><nav><a href="../Blender/Architecture_Complete_V26_16.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_16_Fast.blend">Fast漫游模型</a><a href="../使用说明.txt">启动与操作说明</a></nav></header>
<section><h2>原因与处理</h2><p>之前窄墙和窗框切口停在窗顶附近，梁端接合被割碎；后来补入的窗台方块也越过了窗框端面，形成白色凸片。此次替换各处局部接头，将梁头、窄墙边和窗台连接成闭合实体，按原窗框端面整理收口。</p><p>另外，一楼阳台边板底面比室内顶面低约2mm，局部露出了灰色外饰面；部分平整窗顶面还混用了墙面材质。此次处理了两处边板接合及顶面、侧面的材质映射，清除三角暗斑和拼接色块。三楼右侧飘窗原封顶不连续，露出屋面裁切留下的尖片；现按原房间完成顶面补齐并合并为连续实体。</p><p>一楼保留下部固定玻璃与原低窗脚，二楼开启扇下保留实体窗台墙。原窗台高度、窗框、玻璃、开启动作、阴天显示和V26.15其他已修部位保持。</p><details><summary>本次用户标注图</summary><div class="refs">{ref_html}</div></details></section>
{''.join(cards)}<section><h2>保存后复核</h2><div class="qa">{qa_html}</div><p>直接从保存后的原生模型读回网格，检查五组窄墙、窗台和梁头的连续接合，以及窗框无实体穿插。45处墙面探测点与25个窗高截面通过；十扇前窗的框和玻璃在40个动作帧中采样，共800个组件姿态，无与主体墙面的相交记录。</p><p>原材料、贴图、动作及其他构件逐项比对，未改的对象保持原值；Fast模型的网格、UV、材质及碰撞与主模型核对。继续使用既有阴天柔光、局部AO及流畅显示控制器，本版没有新的FPS测速。</p></section>
<section><h2>实际 Blender 视口</h2><p>以下来自交付Fast模型的原生材质视口。首图运行实际人眼漫游，其余临时隐藏人物以便检查；没有额外补灯，复核没有写回模型。</p><div class="vp">{vp_html}</div></section><footer><p>源模型：Architecture_Complete_V26_15.blend<br>新模型：Architecture_Complete_V26_16.blend</p><p>主模型 SHA256：<code>{mh}</code><br>Fast模型 SHA256：<code>{fh}</code></p><p>已保存V26.15保留。此次未替换用户原有未保存的Blender窗口。尺寸为模型边界与实景关系拟合，不是新增现场测量。</p></footer></main></html>'''
(R/filename).write_text(page,'utf8');(R/'V26_16_Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(R/'V26_16_Delivery_Summary.json').write_text(json.dumps({'status':'PASS','master_sha256':mh,'fast_sha256':fh,'qa_checks':count,'reports':qa_names,'reference_count':len(refs),'html':str(R/filename)},ensure_ascii=False,indent=2),'utf8')
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['V26_16_Manifest.json','V26_16_Package_QA.json']]
(R/'V26_16_Manifest.json').write_text(json.dumps({'version':'V26.16','files':manifest},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(manifest),count,str(R/filename),flush=True)
