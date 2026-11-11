from pathlib import Path
import json,hashlib,shutil,html,re
W=Path(__file__).parent;D=W/'v26_15';O=Path('E:/jz/JIA/Rebuild_V26_15');R=O/'Reports';V=R/'Views';V.mkdir(exist_ok=True);S=O/'Sources';S.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
qa_names=['Native_QA','Geometry_QA','Fast_Display_QA','Interior_Physics_QA','Door_Clearance_QA','Runtime_Viewport_QA'];reports={n:json.loads((R/('V26_15_'+n+'.json')).read_text('utf8'))for n in qa_names};assert all(not q['failures']and q['status'].startswith('PASS')for q in reports.values()),[(n,q['status'],q['failures'])for n,q in reports.items()]
master=O/'Blender/Architecture_Complete_V26_15.blend';fast=O/'Blender/Architecture_Complete_V26_15_Fast.blend';mh,fh=sha(master),sha(fast)
for n,q in reports.items():assert q['model_sha256']==(fh if n in['Fast_Display_QA','Runtime_Viewport_QA']else mh),(n,q['model_sha256'])
tags=['01_Porch_Right_Z_Fighting','02_Porch_Left','06_Storage_Entry_Reverse','07_Gate_Rear_Floor_Recess','09_Stair_West_Front_Corner']
for ver in['V26_14','V26_15']:
 for tag in tags:
  for ext in['png','json']:shutil.copy2(D/'Review'/(ver+'_'+tag+'.'+ext),V)
for p in(D/'Review').glob('Viewport_*'):
 if p.suffix in['.png','.json']:shutil.copy2(p,V)
refs=[]
for time,label in [('013106','门廊柱脚重面'),('013138','楼梯墙角凸块'),('090317','储藏房悬浮细条'),('090417','门后地面凹槽')]:
 name='屏幕截图 2026-10-25 '+time+'.jpg';p=Path('D:/Desktop')/name;assert p.exists(),p;shutil.copy2(p,O/'References'/name);refs.append({'label':label,'file':'References/'+name,'sha256':sha(p)})
ch=json.loads((R/'V26_15_Changes.json').read_text('utf8'));si=json.loads((D/'Input/Source_Index.json').read_text('utf8'));(S/'Input').mkdir(exist_ok=True);(S/'Prepared').mkdir(exist_ok=True);(S/'Final').mkdir(exist_ok=True);(S/'Scripts').mkdir(exist_ok=True)
needed=ch['geometry_changed']+['V26_7_Inner_Gate_Rear_Return_Closure','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_01_Geometry'];sr=[r for r in si['objects']if r['name']in needed]
for r in sr:shutil.copy2(D/'Input'/r['file'],S/'Input')
(S/'Input/Source_Index.json').write_text(json.dumps(dict(si,objects=sr),ensure_ascii=False,indent=2),'utf8');shutil.copy2(D/'Before_Snapshot.json',S/'Input/Before_Snapshot.json')
for folder in['Prepared','Final']:
 for p in(D/folder).glob('*'):
  if p.is_file():shutil.copy2(p,S/folder)
for name in['Prepared.json','Diagnosis.json','Gate_Floor_Profile.json','Stair_Corner_Audit.json','Check_Run.json']:
 if(D/name).exists():shutil.copy2(D/name,S/name)
for name in['probe','focus','prepare','native_cleanup','build','build_fast','fast_display','native_qa','geometry_qa','physics_qa','door_clearance_qa','native_viewport_review','verify_fast','render','views','package','verify_package']:
 p=W/('v26_15_'+name+'.py')
 if p.exists():shutil.copy2(p,S/'Scripts')
shutil.copy2(W/'v26_15_perf/Fast_Build.json',R/'V26_15_Fast_Build.json')
for p in Path('E:/jz/JIA/Rebuild_V26_14/Textures').glob('*'):
 if p.is_file():shutil.copy2(p,O/'Textures')
(S/'脚本说明.txt').write_text('本目录保存本次修改的输入网格、最终网格、材质槽、UV和修正参数，以及实际执行的脚本。脚本使用原工作区 work/v26_2_common.py、v24_16_common.py、geomlibs 等既有依赖和 V26.14 源模型；不是从零生成整栋建筑的独立安装包。直接使用原生 Blender 主文件或根目录启动漫游.cmd，无需运行这些复核脚本。所有贴图已沿用并内嵌于模型。','utf8')
readme='''V26.15｜重面、楼梯墙角、储藏房残片与门后地面修正

双击根目录“启动漫游.cmd”，打开本版 Fast 模型并开始漫游。F8 开始/停止，WASD/方向键移动，Shift 快走，右键拖动转向，V 切换人眼/跟随，空格跳跃，Home 回院落，M 测量，Esc 结束。
完整可编辑模型：Blender/Architecture_Complete_V26_15.blend
流畅显示模型：Blender/Architecture_Complete_V26_15_Fast.blend
图文对照：Reports/V26_15_重面墙角与地面复核.html

本次：门廊重叠实体局部合并，四边平台使用连续原石面；楼梯两处越墙的楼板封补凸块裁回原墙线；删除储藏房门洞独立悬空细木片；门后补地延伸到真实墙根并与邻地面齐平。
继续沿用阴天柔和均匀显示、局部AO及既有流畅控制器；未作新FPS测试。门窗动作、浮雕和其他建筑构件保留。V26.14 源文件未覆盖，本次工作未替换用户原窗口。尺寸是既有模型/参考关系拟合，不是新现场测量。
'''
(O/'使用说明.txt').write_text(readme,'utf8')
cases=[('01','门廊柱脚与平台重面','01_Porch_Right_Z_Fighting','旧地面与后来补齐的四边平台实体重叠，原铺地与石面争夺同一平面；旧平台前沿还比四边平台多出约8cm窄唇边。','将局部旧地面并入平台实体，再从地面对象移除同一部分；只将旧前沿多出的部分收回到四边平台边界，保留原标高和单阶关系。顶面使用连续原石材及其UV，消除交错色块。',refs[0]),('02','楼梯附近墙角凸块','09_Stair_West_Front_Corner','先前楼板补缝体在两层交接处超出了原墙线，留下两块约190×190×130mm的方形凸起。','只裁去进入楼梯空间的两处凸块，保留墙内楼板连接；复核原踏步、平台、窄楼梯井及卫浴墙角。',refs[1]),('03','储藏房门洞悬浮细条','06_Storage_Entry_Reverse','门洞中残留5个顶点、6个三角面的独立旧木片，未随现有门扇开合，底端也未落地。','准确删除这条残片。两侧完整木框、玻璃格纹、实际门扇及开合动作保留。',refs[2]),('04','门后墙根地面下凹','07_Gate_Rear_Floor_Recess','旧补地止于Y=-11.382m，实际墙面在Y=-11.620m，留下约24cm宽低槽。','补地延伸到真实墙根，与相邻地面同标高并合并为实体支撑；避让原墙、石柱、门槛和门扇。',refs[3])]
cards=[]
for num,title,tag,cause,result,ref in cases:
 b='Views/V26_14_'+tag+'.png';a='Views/V26_15_'+tag+'.png';cards.append(f'''<section id="case{num}"><p class="num">{num}</p><h2>{title}</h2><div class="pair"><figure><img src="{b}" alt="V26.14修改前"><figcaption>修改前 · V26.14</figcaption></figure><figure><img src="{a}" alt="V26.15修改后"><figcaption>修改后 · V26.15</figcaption></figure></div><div class="words"><p><b>原因</b>{cause}</p><p><b>修正</b>{result}</p></div><details><summary>查看本次用户标注图</summary><img class="ref" src="../{html.escape(ref['file'])}" alt="用户提供的标注位置"></details></section>''')
checks_count=sum(len(q['checks'])for q in reports.values());qa='<div class="qa">'+''.join(f'<a href="V26_15_{n}.json">{label} · {len(reports[n]["checks"])}项通过</a>'for n,label in[('Native_QA','保存后原生网格'),('Geometry_QA','局部结构'),('Interior_Physics_QA','实际漫游碰撞'),('Door_Clearance_QA','门扇开合'),('Fast_Display_QA','Fast模型保真'),('Runtime_Viewport_QA','实际视口')])+'</div>'
viewport=reports['Runtime_Viewport_QA']['captures'];vp=''.join(f'<figure><img src="Views/{q["image"]}" alt="实际Blender材质视口"><figcaption>实际 Blender 材质视口 · {i+1}</figcaption></figure>'for i,q in enumerate(viewport))
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.15｜重面墙角与地面复核</title><style>body{{margin:0;background:#f3f4f1;color:#172b2c;font-family:"Microsoft YaHei",sans-serif;line-height:1.75}}main{{max-width:1260px;margin:auto;padding:45px 30px}}header{{border-bottom:1px solid #cbd5d0;padding:0 0 35px}}.kicker,.num{{letter-spacing:2px;color:#50776c;font-size:14px}}h1{{font-size:35px;line-height:1.45;margin:12px 0}}h2{{font-size:24px;margin:3px 0 20px}}p{{margin:12px 0}}a{{color:#165e59;text-underline-offset:3px}}nav{{display:flex;gap:20px;flex-wrap:wrap}}.status{{display:inline-block;background:#dcece0;color:#215c40;padding:5px 14px;border-radius:5px}}section{{padding:35px 0;border-bottom:1px solid #cbd5d0}}.num{{margin:0}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:#fff}}img{{display:block;width:100%;height:auto}}figcaption{{font-size:14px;padding:10px 15px;color:#425a54}}.words{{display:grid;grid-template-columns:1fr 1fr;gap:25px}}b{{display:block;font-weight:600;color:#215c4d}}details{{margin:15px 0}}summary{{cursor:pointer;color:#326b5b}}.ref{{max-height:650px;object-fit:contain;background:#e9ece6;width:auto;max-width:100%;margin:20px auto}}.qa{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0}}.qa a{{background:#fff;padding:15px}}.vp{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}code{{word-break:break-all;color:#5e6b64;font-size:12px}}footer{{color:#67776e;font-size:13px;padding:30px 0}}@media(max-width:750px){{main{{padding:25px 15px}}.pair,.words,.qa,.vp{{grid-template-columns:1fr}}h1{{font-size:27px}}}}</style><main><header><p class="kicker">建筑重建 / V26.15 / 2026.10.25</p><h1>重面、墙角与地面接合复核</h1><p>四处问题均已落实到原生几何。相同相机、阴天环境与光照设置的前后对照如下。</p><p class="status">{checks_count}项检查通过 · 160个门扇姿态 · 原V26.14保留</p><nav><a href="../Blender/Architecture_Complete_V26_15.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_15_Fast.blend">Fast漫游模型</a><a href="../使用说明.txt">启动与操作说明</a></nav></header>{''.join(cards)}<section><h2>保存后检查</h2>{qa}<p>原门窗动作、浮雕、贴图、其他构件和上版卫浴墙角保持。漫游验证直接使用本次碰撞网格、人物胶囊和重力控制器，包含上下楼、门洞、内大门、储藏房和补平地面。Fast模型与主模型的网格、UV、材质及动作逐项核对。</p><p>保留阴天柔光、局部AO与既有流畅控制器。本版没有新的FPS测速。</p></section><section><h2>实际 Blender 视口</h2><p>下列图来自已交付Fast模型的原生材质视口，首图为实际人眼漫游；其余图临时隐藏人物便于检查。没有额外补灯，复核未写回模型。</p><div class="vp">{vp}</div></section><footer><p>源模型：Architecture_Complete_V26_14.blend<br>新模型：Architecture_Complete_V26_15.blend</p><p>主模型SHA256：<code>{mh}</code><br>Fast模型SHA256：<code>{fh}</code></p><p>尺寸为既有模型边界与实景关系拟合，不是新现场测量。此次未覆盖V26.14，也未替换用户原Blender窗口。</p></footer></main></html>'''
report=R/'V26_15_重面墙角与地面复核.html';report.write_text(page,'utf8');(R/'V26_15_Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8');(R/'V26_15_Delivery_Summary.json').write_text(json.dumps({'status':'PASS','master_sha256':mh,'fast_sha256':fh,'qa_checks':checks_count,'reports':qa_names,'reference_count':len(refs),'html':str(report)},ensure_ascii=False,indent=2),'utf8')
manifest=[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in['V26_15_Manifest.json','V26_15_Package_QA.json']];(R/'V26_15_Manifest.json').write_text(json.dumps({'version':'V26.15','files':manifest},ensure_ascii=False,indent=2),'utf8');print('PACKAGED',len(manifest),checks_count,str(report),flush=True)
