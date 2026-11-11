from pathlib import Path
import json,hashlib,shutil,html,datetime
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=json.loads((R/'V26_1_Build.json').read_text('utf8'));assert h==build['sha256'];qa=[]
for name in ['V26_1_Native_Readback_QA.json','V26_1_Saved_Geometry_QA.json','V26_1_Interior_Physics_QA.json']:
 q=json.loads((R/name).read_text('utf8'));assert q['model_sha256']==h,(name,'stale model');assert not q['failures'],(name,q['failures']);qa+=q['checks']
assert all(q['pass']for q in qa);assert sha(build['source'])==build['source_sha256'];assert not list(O.rglob('*.3dm'))
views=json.loads((D/'Views.json').read_text('utf8'));render=[]
for tag,*_ in views:
 p=R/('V26_1_'+tag+'.png');s=json.loads(p.with_name(p.stem+'_State.json').read_text('utf8'));assert p.exists()and s['model_sha256']==h and not s['draft'],tag;render.append({'view':tag,'image':p.name,'sha256':sha(p)})
for src,dst in [('Before_Stair.png','Before_V26_Stair.png'),('Before_Terrace.png','Before_V26_Terrace.png'),('Before_Screen.png','Before_V26_Screenwall.png'),('Before_Gate_Floor.png','Before_V26_Gate_Floor.png')]:shutil.copy2(D/src,R/dst)
scripts=O/'Sources/Scripts';scripts.mkdir(parents=True,exist_ok=True)
for p in W.glob('v26_1_*.py'):shutil.copy2(p,scripts/p.name)
for fn in ['Base.json','Prepared_House.json','Prepared_Railing.json','Prepared_Site.json','Prepared_Context_Trim.json','Last_Joint.json','Views.json']:shutil.copy2(D/fn,O/'Sources'/fn)
audit=json.loads((D/'Final/Coplanar_Audit.json').read_text('utf8'));same=[q for q in audit if q['same_normal']];(R/'V26_1_Coplanar_Candidates.json').write_text(json.dumps({'model_sha256':h,'scope':'Axis-aligned planes of exported native visible meshes. Candidate pairs include interior mating contacts, frame edges and roof detail joints; a candidate is not itself a visible flicker. Dense photo scans and curved reliefs are excluded.','plane_separation_limit_m':.00051,'candidate_pairs':audit,'same_normal_candidates':len(same)},ensure_ascii=False,indent=2),encoding='utf8')
caption={
'01_Stair_Flush_Treads':'平台前的白色横条已从可见踏步中消除，灰色踏步标高保持。',
'02_Half_Landing_Wreath':'实拍样式的180°回弯与柱颈连接，握持面为连续椭圆扫掠。',
'03_Floor_Newel_Sockets':'上下梯段分别接入柱身颈口，球头、立柱和栏杆均有实体连接。',
'04_Stair_White_Corner':'楼梯墙、柱与梁的可见面统一收口，原结构构件保存在隐藏集合。',
'05_Terrace_Flush_Wall':'露台陶瓷饰面移至柱外连续收口，保留真实梁及屋面支承。',
'06_F3_Guard_Base':'三层临空边补足连续栏杆，立柱及车木杆落在实际楼板上。',
'07_Reference_Screenwall':'按实拍整理连续白色线脚、浅瓦压顶和毛石—灰石—青砖层次，清除旧山花、斜条及悬片。',
'08_Gate_Floor':'门口地面归并为连续可见面，保留原门槛高差；已测试双向通行。',
'09_White_Wall_Ground':'白墙脚与铺地交接清理，删除该区域遗留饰面及穿插土坡碎面。',
'10_West_Courtyard_Wall':'西院墙的白色内面、砖饰及框线归并并落实支承，减少重复表面。',
'11_House_Exterior':'完整模型与外景保留；扫描模型只在已有重建部分的覆盖范围裁切。',
'12_Original_Entrance_Ramp':'入口原场地坡面、照片和UV保持，邻接高处的冗余扫描片清理。',
'13_Stair_Flush_Glazing_Jamb':'从楼梯仰视复核连续墙面与楼层交接。'}
md=f'''# Rebuild V26.1 修正交付

模型：[Architecture_Complete_V26_1.blend](../Blender/Architecture_Complete_V26_1.blend)  
漫游：双击上一级目录的“启动漫游.cmd”。编辑：双击“打开修正版模型.cmd”。

基于 V26 另存，交付 Blender 模型。原文件 SHA-256 保持 `{build['source_sha256']}`。最终模型 SHA-256：`{h}`。

本次处理了标注的楼梯踏步白条、梁墙柱穿插、露台墙面凸条及楼面重叠。楼梯平台的支承梁只在露出踏步的位置局部避让；原踏步高度保留，支承关系保留。原构件放在“V26_1_原构件备份_隐藏不参与显示和碰撞”集合，可继续编辑。

深红木扶手保留实拍中的车木柱与球头样式，改为连续回弯和接柱颈口。新增栏杆共110根车木杆、7根主柱，均检查了与实际楼板或踏步的接触。水平护栏顶高约1.20米；杆件名义最大净间距92毫米。

南侧靠廊房的短墙取消错误端山花和低位装饰，改成连续白色线脚和浅瓦压顶。外墙按补图恢复毛石、灰石带及青砖层次；尺寸为照片比例与既有定位线拟合。裁掉进入已有建筑、墙体和地面范围的扫描碎片，范围外的外景保留。

保存后重新读取并检查，共{len(qa)}项自动检查通过；其中漫游与碰撞{sum(1 for q in json.loads((R/'V26_1_Interior_Physics_QA.json').read_text('utf8'))['checks'])}项，涵盖双向上下楼、院内通道、内门槛、原入口坡道，以及4处独立MB7外景可行走表面。80个踏步采样未发现凸条；110根栏杆与7根立柱均有支承接触。原入口坡面对象、照片字节及门窗动作保持。通过的是已列出的模型检查与路线，不构成现场测量或结构承载认证。

平面扫描还会列出内部接触面、门窗压边和瓦件拼接候选；这些不直接等于可见闪烁，完整候选记录随报告保存。标注处采用实体归并、表面归属与局部裁切处理，并从对应角度复查，未把原有构造接触面一律删除。

下图均由交付模型实际渲染。室内复核时临时加入面光源，交付模型未加入该灯；明暗不能作为修改前后材质颜色的直接对照。

'''
for tag,*_ in views:md+=f'## {tag}\n\n{caption[tag]}\n\n![{tag}]({(R/("V26_1_"+tag+".png")).as_posix()})\n\n'
md+='栏杆几何复核参考：[中国建筑科学研究院 GB55031-2022 6.6](https://gf.cabr-fire.com/article-41818.htm)。现有模型资料不能完成荷载、锚固、材料及全部规范适用性的认证。\n'
(R/'修正说明与预览.md').write_text(md,encoding='utf8')
cards=[]
for before,tag,title in [('Before_V26_Stair.png','01_Stair_Flush_Treads','踏步白条'),('Before_V26_Terrace.png','05_Terrace_Flush_Wall','露台墙柱交接'),('Before_V26_Screenwall.png','07_Reference_Screenwall','外院墙与悬片')]:cards.append(f'<section><h2>{title}</h2><div class="pair"><figure><img src="{before}"><figcaption>修改前 V26</figcaption></figure><figure><img src="V26_1_{tag}.png"><figcaption>修改后 V26.1</figcaption></figure></div></section>')
gallery=''.join(f'<figure><a href="V26_1_{tag}.png"><img loading="lazy" src="V26_1_{tag}.png"></a><figcaption>{html.escape(caption[tag])}</figcaption></figure>'for tag,*_ in views)
doc=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.1 修正核对</title><style>body{{font:16px/1.7 "Microsoft YaHei",sans-serif;margin:0;background:#f3f4f5;color:#26313b}}main{{max-width:1320px;margin:auto;padding:28px}}h1{{font-size:30px}}section{{background:white;padding:22px;margin:24px 0;border-radius:12px}}.pair,.gallery{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0}}img{{width:100%;display:block}}figcaption{{padding:9px 0;color:#52606a}}a{{color:#176a81}}small{{word-break:break-all}}@media(max-width:800px){{.pair,.gallery{{grid-template-columns:1fr}}}}</style><main><h1>Rebuild V26.1 · 修正核对</h1><p><a href="../Blender/Architecture_Complete_V26_1.blend">Blender 模型</a>　<a href="修正说明与预览.md">详细说明</a></p><p>{len(qa)}项保存后检查通过，含上下楼、门槛、原坡道与MB7外景表面行走。保留原V26、原照片、原坡面及门窗动作。室内图使用临时复核灯光，未添加到交付文件。</p>{''.join(cards)}<section><h2>实际模型复核图</h2><div class="gallery">{gallery}</div></section><small>交付模型 SHA-256：{h}</small></main></html>'''
(R/'V26_1_修正对比.html').write_text(doc,encoding='utf8')
(O/'README_先看这里.md').write_text(f'''Rebuild V26.1 · Blender

编辑模型：打开修正版模型.cmd
启动漫游：启动漫游.cmd
修正对比：Reports/V26_1_修正对比.html
逐项检查与实图：Reports/修正说明与预览.md

最终模型：Blender/Architecture_Complete_V26_1.blend
SHA-256：{h}

原V26保持。原构件保留在隐藏备份集合，当前可见模型和碰撞不重复使用它们。模型中的贴图为原始打包照片。Sources中的脚本是本次处理和检查的归档，依赖原工作区 {W.parent} 的几何库及缓存；Blender交付文件本身可直接编辑，不依赖这些脚本。
''',encoding='utf8')
result={'status':'PASS','model_sha256':h,'source_sha256_unchanged':sha(build['source']),'automated_checks':len(qa),'rendered_views':len(render),'checks':qa,'renders':render,'format':'Blender only','rhino_exports':0};(R/'V26_1_Delivery_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='Manifest_SHA256.json':manifest.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');print('V26_1_DELIVERY_PASS',len(qa),len(render),h,flush=True)
