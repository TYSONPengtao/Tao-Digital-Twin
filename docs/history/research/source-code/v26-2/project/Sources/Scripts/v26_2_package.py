from pathlib import Path
import json,hashlib,shutil,html,sys,struct
W=Path(__file__).parent;D=W/'v26_2';O=Path('E:/jz/JIA/Rebuild_V26_2');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_2.blend'
def sha(p):
 with Path(p).open('rb')as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
h=sha(P);base=json.loads((D/'Base.json').read_text('utf8'));assert sha(base['model'])==base['sha256']
qa=[]
for fn in ['V26_2_Native_Readback_QA.json','V26_2_Saved_Geometry_QA.json','V26_2_Interior_Physics_QA.json']:
 q=json.loads((R/fn).read_text('utf8'));assert q['model_sha256']==h,(fn,'stale model hash');assert not q['failures'],(fn,q['failures']);qa.append(q)
checks=sum(len(q['checks'])for q in qa)
pairs=[
 ('02_Left_Room_Corner','墙角和梁侧收平','对应 072826、073017：柱边与梁侧的长条凸面归入连续完成面，保留门洞。'),
 ('03_Rear_Window_Wall','一层窗下墙面','对应 072901、072943：按实际窗框边界补齐窗下、窗头，清除斜向补面形成的三角斑块。'),
 ('05_Ceiling_Head_Joints','楼梯相邻墙体和墙顶','对应 072718、073017：墙体接至梁板，清理旧三角面透出的斑块。'),
 ('09_F2_Rear_Window','二层窗下和窗头','同类问题沿各楼层检查，保留原窗框、玻璃和窗洞。'),
 ('10_F3_Head_Junction','三层门边和梁墙交接','保留原门位、开启方向与楼梯口，整理墙边凸条及门头收口。'),
 ('11_Corrected_Glazed_Door','一层右侧玻璃门：开启','对应 073142：门框补足墙厚；这组门原来比实际门洞高 450mm，已对齐现有楼面。卫生间隔墙沿用当前版本的位置。'),
 ('12_Closed_Glazed_Door','一层右侧玻璃门：关闭','使用相同原生动画的关闭姿态检查门扇、门框、楼面和洞口的配合。'),
 ('06_Gallery_Stone_Base','廊房下的石材基座','对应 073314：去除低位旧白色饰条及青砖错贴，毛石和条石沿基座连续衔接。'),
 ('07_Long_Outer_Wall','整段外院墙贴图','对应 073539：沿外墙连续配置毛石基座、灰石带、白灰腰线和青砖；内侧白墙保持。'),
]
singles=[('04_Glazed_Door','室内玻璃门与完整门框'),('08_House_Overview','整体建筑与保留的外景'),('13_Protected_Stair_Guard','保留的三层护栏和敞开楼梯口')]
images=[];rows=[]
for tag,title,desc in pairs:
 for phase,want in [('Before',base['sha256']),('After',h)]:
  fn=phase+'_'+tag+'.png';s=json.loads((R/(fn[:-4]+'_State.json')).read_text('utf8'));assert s['model_sha256']==want and not s['draft'],fn;assert(R/fn).stat().st_size>10000
  with(R/fn).open('rb')as fp:header=fp.read(24)
  size=struct.unpack('>II',header[16:24]);assert size==(1600,1200),(fn,size);images.append(dict(s,file=fn,sha256=sha(R/fn),width=size[0],height=size[1]))
 a=json.loads((R/('Before_'+tag+'_State.json')).read_text('utf8'));b=json.loads((R/('After_'+tag+'_State.json')).read_text('utf8'));assert all(a[k]==b[k]for k in ['position','aim','lens','frame','temporary_review_light']),tag
 before='Before_'+tag+'.png';after='After_'+tag+'.png';rows.append(f'<section><h2>{html.escape(title)}</h2><p>{html.escape(desc)}</p><div class="pair"><figure><figcaption>V26.1 · 修正前</figcaption><img loading="lazy" src="{before}" alt="修正前"></figure><figure><figcaption>V26.2 · 修正后</figcaption><img loading="lazy" src="{after}" alt="修正后"></figure></div></section>')
for tag,title in singles:
 fn='After_'+tag+'.png';s=json.loads((R/(fn[:-4]+'_State.json')).read_text('utf8'));assert s['model_sha256']==h and not s['draft'],fn;assert(R/fn).stat().st_size>10000;images.append(dict(s,file=fn,sha256=sha(R/fn)));rows.append(f'<section><h2>{title}</h2><img class="single" loading="lazy" src="{fn}" alt="{title}"></section>')
styles='''body{margin:0;background:#eef1f3;color:#202a31;font:16px/1.7 "Microsoft YaHei",sans-serif}main{max-width:1500px;margin:auto;padding:32px}h1{font-size:30px;margin:0}h2{font-size:21px;margin:0 0 8px}p{margin:8px 0 18px}section{background:white;border-radius:12px;padding:22px;margin:22px 0;border:1px solid #dce2e6}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption{color:#52606c;padding-bottom:8px}img{width:100%;height:auto;border-radius:6px;display:block}.single{max-width:1200px;margin:auto}.meta{font-size:13px;overflow-wrap:anywhere;color:#53616e}.pass{padding:12px 18px;background:#e1f2e9;border-left:4px solid #238353}a{color:#175e8a}@media(max-width:800px){main{padding:16px}.pair{grid-template-columns:1fr}section{padding:14px}}'''
doc=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Rebuild V26.2 · 结构与贴图修正</title><style>{styles}</style><main><h1>Rebuild V26.2 · 结构与贴图修正</h1><p>以 V26.1 的 Blender 文件为底稿另存，按 2026-10-23 07:27—07:35 的八张圈注图继续修正。仅输出 Blender 模型。</p><p class="pass">保存文件复核通过：{checks} 项自动检查。含 480 个窗下/窗头采样点、80 个窗洞采样点、80 个踏步高度采样点、12 扇门的 168 个动画姿态，以及 62 项实际人物碰撞与行走检查。</p><p><a href="../Blender/Architecture_Complete_V26_2.blend">Blender 模型</a>　<a href="../启动漫游.cmd">启动漫游</a>　<a href="V26_2_Delivery_QA.json">检查记录</a></p><p>以下为原生 Blender 场景直接渲染，前后使用相同相机、分辨率及复核光照；关闭门使用第 1 帧，其余为第 40 帧。未生成或修绘验证图。</p>{''.join(rows)}<section><h2>保留与核查范围</h2><p>原 V26.1 文件、外景网格、原入口实景坡、门窗原生动画与打包照片保留。上一版墙地面主构件在模型的隐藏备份集合中保留，排除显示及碰撞。墙体使用共用边界；屋顶和楼梯保留为闭合且有实际接触的独立构件，避免把相接的构件当作重复外露面。</p><p>本次核查针对模型几何接合、材质和所列漫游路线。照片拟合与模型检查不能代替现场测量或结构承载验算；外景检查包含四处相互分开的实际可行走表面。</p><p class="meta">文件：{html.escape(str(P))}<br>SHA-256：{h}<br>源文件 SHA-256：{base['sha256']}</p></section></main></html>'''
(R/'V26_2_修正对比.html').write_text(doc,encoding='utf8')
out={'status':'PASS','model':str(P),'model_sha256':h,'bytes':P.stat().st_size,'source':base['model'],'source_sha256':base['sha256'],'source_preserved':True,'automated_checks':checks,'native_readback_checks':len(qa[0]['checks']),'geometry_checks':len(qa[1]['checks']),'physics_checks':len(qa[2]['checks']),'actual_final_renders':len(pairs)+len(singles),'actual_before_renders':len(pairs),'all_render_states_match_model_hashes':True,'no_rhino_model':not list(O.rglob('*.3dm')),'scope':'Geometric fit, material continuity and the documented real capsule routes; not structural capacity certification.'}
(R/'V26_2_Delivery_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(R/'V26_2_Render_Manifest.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf8')
Sdir=O/'Sources';(Sdir/'Scripts').mkdir(exist_ok=True);(Sdir/'Prepared_Geometry').mkdir(exist_ok=True)
for fn in ['v26_2_layered.py','v26_2_direct_surface.py','v26_2_frames.py','v26_2_site.py','v26_2_common.py','v26_2_build.py','v26_2_readback.py','v26_2_geometry_qa.py','v26_2_physics_qa.py','v26_2_render.py','v26_2_views.py','v26_2_package.py']:shutil.copy2(W/fn,Sdir/'Scripts'/fn)
for tag in ['House','Site']:
 prep=json.loads((D/f'Prepared_{tag}.json').read_text('utf8'));(Sdir/f'{tag}_修正参数.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),encoding='utf8')
 for r in prep['objects']:shutil.copy2(D/r['file'],Sdir/'Prepared_Geometry'/r['file'])
shutil.copy2(D/'Exact_House_Parts.json',Sdir/'分层墙体参数.json');shutil.copy2(D/'Direct_Surface_QA.json',R/'V26_2_Closed_Components_QA.json')
(Sdir/'说明.txt').write_text('Blender 主模型为可直接打开的交付物，材质照片及原构件备份保留在文件内。这里的参数和网格用于复核与后续编辑。Scripts 是本机过程记录，引用原项目及当前工作区缓存，不是独立构建包。墙面计算网格 0.1mm；二维接合容差 0.2mm；不代替现场测量。',encoding='utf8')
(O/'打开修正对比.cmd').write_text('@echo off\r\nstart "" "%~dp0Reports\\V26_2_修正对比.html"\r\n',encoding='utf8')
(O/'使用说明.md').write_text(f'''# Rebuild V26.2

双击“打开修正版模型.cmd”编辑模型；双击“启动漫游.cmd”进行人物漫游；“打开修正对比.cmd”查看逐项对比。

模型：Blender/Architecture_Complete_V26_2.blend（{P.stat().st_size/1024/1024:.1f} MiB）。原 V26.1 文件保留。

本次修正墙角和梁墙收口、窗下/窗头斜补面及空缺、门框厚度与一层右玻璃门标高、廊下错误青砖和低位旧饰条、整段院墙毛石/灰石/白灰腰线。所有门窗原生动画保留，三层护栏及楼梯口保留。原入口坡和外景保持。

保存后 {checks} 项检查通过，附 {len(pairs)+len(singles)} 张最终模型复核图。检测数据和相机/模型哈希位于 Reports。模型几何检查不等于现场测量或结构承载验算。

漫游：方向键/WASD 移动，空格跳跃，Shift 快走，鼠标右键转向，V 切换视角，Home 回院落，M 切换材质/流畅模式，Esc 结束。
''',encoding='utf8')
# Remove only this task's stale draft previews after final originals exist.
root=R.resolve()
for fn in R.glob('Draft_*'):
 assert fn.resolve().parent==root
 if fn.is_file():fn.unlink()
manifest=[]
for f in sorted(O.rglob('*')):
 if f.is_file()and f.name!='Manifest_SHA256.json':manifest.append({'file':f.relative_to(O).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');assert sha(P)==h;print('V26_2_DELIVERY_READY',json.dumps(out,ensure_ascii=False),flush=True)
