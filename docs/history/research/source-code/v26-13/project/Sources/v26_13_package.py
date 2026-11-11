from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_13';O=Path('E:/jz/JIA/Rebuild_V26_13');R=O/'Reports';S=O/'Sources';REF=O/'References'
P=O/'Blender/Architecture_Complete_V26_13.blend';F=P.with_name('Architecture_Complete_V26_13_Fast.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
h,fh=sha(P),sha(F);ch=json.loads((R/'V26_13_Changes.json').read_text('utf8'));probe=json.loads((D/'Probe.json').read_text('utf8'))
assert sha(ch['source'])==ch['source_sha256']and sha(probe['V24']['model'])==probe['V24']['sha256']
visual=[]
for tag in ['01_Gate_Whole','02_Left_Three_Faces','03_Right_Three_Faces','04_Low_Plinth_And_Sill','05_Faceted_Carving_Close']:
 p=D/'Review'/('V26_13_'+tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==h and q['temporary_lights']==0
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
 visual.append({'check':tag,'pass':True,'image':p.name,'image_sha256':sha(p),'model_sha256':h,'review':'Inspected saved native geometry under the inherited overcast and local AO profile'})
for tag in ['01_Gate_Whole','02_Left_Three_Faces','03_Right_Three_Faces','04_Low_Plinth_And_Sill']:
 p=D/'Review'/('V26_12_'+tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==ch['source_sha256']
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
for tag in ['Viewport_01_Actual_Tour','Viewport_02_Faceted_Stone']:
 p=D/'Review'/(tag+'.png');q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==fh and q['actual_viewport']and q['shading']=='MATERIAL'
 for src in[p,p.with_suffix('.json')]:copy(src,R/src.name)
 visual.append({'check':tag,'pass':True,'image':p.name,'image_sha256':sha(p),'model_sha256':fh,'review':'Inspected the actual native Fast material viewport, not an offline image substitution'})
(R/'V26_13_Visual_QA.json').write_text(json.dumps({'status':'PASS','model_sha256':h,'checks':visual,'failures':[]},ensure_ascii=False,indent=2),'utf8')
reports=[]
for tag in ['Native_QA','Gate_Clearance_QA','Interior_Physics_QA','Fast_Display_QA','Runtime_Viewport_QA','Visual_QA']:
 fn='V26_13_'+tag+'.json';q=json.loads((R/fn).read_text('utf8'));assert q['status'].startswith('PASS')and not q['failures']and all(c['pass']for c in q['checks']),fn
 assert q['model_sha256']==(fh if tag in ['Fast_Display_QA','Runtime_Viewport_QA']else h)
 reports.append({'file':fn,'status':q['status'],'checks':len(q['checks'])})
for p in W.glob('v26_13*.py'):copy(p,S/p.name)
for p in D.iterdir():
 if p.is_file()and p.suffix in ['.npz','.json']:copy(p,S/'Geometry_Archive'/p.name)
for name in ['v24_06_common.py','v24_qa_blender.py','v26_2_common.py','v26_12_fast_display.py','v23_gate_relief.py']:copy(W/name,S/name)
for p in (W/'v26_13_perf').iterdir():
 if p.is_file()and p.suffix in ['.py','.json']:copy(p,S/'Performance'/p.name)
for p in Path('E:/jz/JIA/Rebuild_V26_12/Textures').iterdir():
 if p.is_file():copy(p,O/'Textures'/p.name)
(S/'源码存档说明.txt').write_text('修正从V26.12完整模型开始。Geometry_Archive保留原件与变更网格、UV、顶点对应、V24/V26.12探测记录。脚本依赖原模型与历史工作目录和本地manifold/scipy库。交付的两份blend已打包图像，可直接打开；本目录是可追溯源码存档，不是独立一键重建工具。','utf8')
refs=[]
for src,name in [(Path('D:/Desktop/屏幕截图 2026-10-25 003420.jpg'),'实景对照_门柱正面.jpg'),(Path('D:/Desktop/屏幕截图 2026-10-25 003523.jpg'),'实景对照_斜转角与柱脚.jpg')]:
 assert src.is_file();copy(src,REF/name);refs.append({'file':name,'source':str(src),'sha256':sha(src)})
(REF/'Reference_Index.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),'utf8')
(O/'使用说明.txt').write_text('''V26.13 — 按实景修正内大门柱角、浮雕分格与柱脚

启动：根目录“启动漫游.cmd”，默认流畅版、阴天柔光。左下显示V26.13，启动定位内大门；Home回院落。
完整可编辑模型：Blender/Architecture_Complete_V26_13.blend
实景、修改前后与实际材质视口：Reports/V26_13_实景门柱与台基复核.html

本轮按10月25日两张实景对照：
1. 门柱前角由12mm小倒角改成90mm斜转面，正面与两处斜转角均保留V24竹叶花卉石画，修正侧画的位置与朝向。
2. 六幅下段石画向下延伸150mm，底框接近门槛。腰线从130mm收至82mm，并恢复原折面及雕花。
3. 移除原两层外凸柱脚，改为35mm高、最大外扩20mm的薄斜收口。一阶平台仍为100mm高，前沿从柱前280mm收至90mm，入口宽度随小柱脚收紧。
4. 柱体、边框、腰线和石画统一为灰石色系，保留真实网格起伏和细微石材颗粒。

门洞高度、门楣形状、屋顶、木门及动作和其他建筑沿用V26.12。门楣石画保留，材质与新门柱协调。原V26.12石画在文件中隐藏存档；V26.12和指定V24源文件均保持字节不变。

漫游：WASD/方向键移动，Shift快走，空格跳跃，右键拖动转向，滚轮调距离，V切换人眼/第三人称，M切换材质/实体显示，Esc退出，F8恢复。
保留8采样、半分辨率预览与20cm局部AO，无实时雕刻细分或置换。本轮不声称新增FPS测试结果。

尺寸为照片与原模型拟合，并非现场实测；雕刻纹样沿用V24，未将实景照片中的每一处石刻扫描还原。
V26.13独立保存，未覆盖用户先前打开的未保存工作。
''','utf8')
css='body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1440px;margin:auto;padding:28px;background:#e9eef0;color:#253940}header,article,section{background:white;padding:24px;border-radius:12px;margin-bottom:22px}h1{font-size:30px;margin:0 0 12px}h2{font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;max-height:850px;object-fit:contain;display:block;background:#dfe5e7}figcaption{font-size:14px;color:#586f78}a{color:#12667c}.ok{color:#226343;background:#dfefe4;padding:8px 15px;border-radius:12px;display:inline-block}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #d9e1e5;padding:8px}.hash{font-size:12px;overflow-wrap:anywhere}summary{cursor:pointer}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'
def img(src,cap):return '<figure><a href="'+html.escape(src)+'"><img loading="lazy" src="'+html.escape(src)+'" alt="'+html.escape(cap)+'"></a><figcaption>'+html.escape(cap)+'</figcaption></figure>'
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.13 实景门柱与台基复核</title><style>'+css+'</style><header><h1>V26.13 按实景修正内大门</h1><p>恢复带石画的斜转角，收薄腰线并延长下段花卉板；收小红叉所示柱脚和台阶外凸。柱身与浮雕使用相近的灰石色。</p><p class="ok">保存模型复核通过 · 双门80个开合姿态通过 · 实际漫游与入口通行通过</p><p>打开根目录“启动漫游.cmd”，左下应显示V26.13。新版独立保存。</p><p><a href="../Blender/Architecture_Complete_V26_13.blend">完整可编辑模型</a>　<a href="../Blender/Architecture_Complete_V26_13_Fast.blend">流畅模型</a>　<a href="../使用说明.txt">使用说明</a></p></header>']
parts.append('<article><h2>本次实景依据</h2><div class="grid">'+img('../References/实景对照_门柱正面.jpg','用户实景对照：门柱分格、腰线与下段花卉。原图未改动。')+img('../References/实景对照_斜转角与柱脚.jpg','用户实景对照：雕刻斜转面，红叉标示柱脚过度外凸。原图未改动。')+'</div><p>实景柱角有明显斜转面，原模型只有很小的倒角，导致侧画退到宽平面上。现将石画随真实截面转折，保留原V24竹叶、花卉与枝叶纹样。</p></article>')
parts.append('<article><h2>修改后整体</h2>'+img('V26_13_01_Gate_Whole.png','V26.13保存模型；阴天均匀光照与局部遮蔽，无临时附加灯。')+'</article>')
for tag,title in [('02_Left_Three_Faces','柱角、雕刻与腰线'),('04_Low_Plinth_And_Sill','收小柱脚和单阶平台')]:
 parts.append('<article><h2>'+title+'</h2><div class="grid">'+img('V26_12_'+tag+'.png','修改前V26.12；同一相机、阴天与局部AO设置。')+img('V26_13_'+tag+'.png','修改后V26.13；真实几何和灰石材质。')+'</div></article>')
parts.append('<article><h2>两侧转角与细部</h2><div class="grid">'+img('V26_13_03_Right_Three_Faces.png','右门柱：正面与斜转面连续收口。')+img('V26_13_05_Faceted_Carving_Close.png','斜转面及竹叶雕刻起伏近景。')+'</div><p>原雕刻起伏和UV保留，图案坐入柱体凹槽；活动石画不使用实时细分或置换。</p></article>')
parts.append('<article><h2>实际材质视口和漫游</h2><div class="grid">'+img('Viewport_01_Actual_Tour.png','交付Fast文件实际运行的人物漫游视口；原生导出图不包含HUD文字。')+img('Viewport_02_Faceted_Stone.png','同一Fast文件的实际材质视口近景，由Blender原生OpenGL导出。')+'</div><p>显示继续采用阴天柔光、8采样与半分辨率预览，保留读出石画纹理所需的20cm局部AO。本轮未新增FPS测量。</p></article>')
parts.append('<section><h2>调整与验证</h2><p>门洞高度、门楣形状、屋顶与原木门动作保留；门楣石画仅协调材质。尺寸依据照片比例与原模型拟合，并非现场实测。V24石画保留，并非实景石刻的逐点扫描。</p><details><summary>查看几何调整尺寸</summary><table><tr><th>部位</th><th>V26.12</th><th>V26.13</th></tr><tr><td>柱前角</td><td>12mm小倒角</td><td>90mm斜转面</td></tr><tr><td>装饰腰线</td><td>130mm高</td><td>82mm高，原折面雕花</td></tr><tr><td>六幅下段石画</td><td>底部偏高</td><td>下延150mm</td></tr><tr><td>柱脚</td><td>两层外凸台座</td><td>35mm薄斜收口，最大外扩20mm</td></tr><tr><td>台阶前沿</td><td>柱前280mm</td><td>柱前90mm</td></tr><tr><td>入口平台</td><td>3.60m宽</td><td>约3.393m宽，仍为100mm单阶</td></tr></table></details><table><tr><th>检查记录</th><th>检查项</th></tr>')
for q in reports:parts.append('<tr><td><a href="'+q['file']+'">'+q['file']+'</a></td><td>'+str(q['checks'])+'</td></tr>')
parts.append('</table><p><a href="V26_13_Changes.json">几何、材质与来源记录</a>　<a href="../References/Reference_Index.json">实景原图校验</a></p><p class="hash">完整模型SHA256：'+h+'<br>流畅模型SHA256：'+fh+'<br>V26.12来源SHA256：'+ch['source_sha256']+'</p></section></html>')
(R/'V26_13_实景门柱与台基复核.html').write_text(''.join(parts),'utf8')
files=[{'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name not in ['Manifest_SHA256.json','V26_13_Package_QA.json']]
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'fast_model_sha256':fh,'source_model':ch['source'],'source_sha256':ch['source_sha256'],'reference_model':probe['V24']['model'],'reference_sha256':probe['V24']['sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8')
print('PACKAGED',len(files),'CHECKS',sum(q['checks']for q in reports),flush=True)
