from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent
D=W/'v26_8_perf'
O=Path('E:/jz/JIA/Rebuild_V26_8')
R=O/'Reports'
S=O/'Sources/Performance'


def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()


qa=json.loads((R/'V26_8_Performance_QA.json').read_text('utf8'))
assert not qa['failures']and all(c['pass']for c in qa['checks'])
assert sha(qa['model'])==qa['model_sha256']
assert sha(qa['source_model'])==qa['source_sha256']
launcher=O/'启动漫游.cmd'
previous=launcher.read_text('utf8')
backup=S/'Original_Launcher.txt'
if not backup.exists():backup.write_text(previous,'utf8')
new=backup.read_text('utf8').replace('Architecture_Complete_V26_8.blend','Architecture_Complete_V26_8_Fast.blend').replace('start_roam.py','start_roam_fast.py')
launcher.write_text(new,'utf8')
imdir=R/'流畅模式对比'
imdir.mkdir(exist_ok=True)
for name in ['baseline_court.png','fast_court.png','baseline_stairs.png','fast_stairs.png']:
    shutil.copy2(D/name,imdir/name)
for name in ['Audit_Before.json','Viewport_Benchmark.json','Fast_Build.json']:
    shutil.copy2(D/name,R/('V26_8_'+name))
for name in ['v26_8_verify_fast.py','v26_8_package_fast.py','v26_8_verify_package.py']:
    shutil.copy2(W/name,S/name)
bench=qa['viewport_benchmark']
rows=[]
for v,label in [('court','院落'),('stairs','楼梯')]:
    entries={r['profile']:r for r in bench['measurements']if r['view']==v}
    rows.append(f"<tr><td>{label}</td><td>{entries['baseline']['effective_fps']:.1f}</td><td>{entries['fast']['effective_fps']:.1f}</td></tr>")
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.8 流畅漫游</title><style>body{font:17px/1.7 "Microsoft YaHei",sans-serif;max-width:1100px;margin:25px auto;padding:20px;background:#eef1f3;color:#26333b}article{background:#fff;padding:24px;margin:24px 0;border-radius:8px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ccd3d8;text-align:left}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}img{width:100%;height:auto}a{color:#176482}small{overflow-wrap:anywhere}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>V26.8 流畅漫游</h1><p>原来的“启动漫游.cmd”现在默认进入流畅版。当前已打开的窗口仍使用旧设置，需要重新启动漫游后生效。</p><p><a href="../启动漫游.cmd">启动漫游.cmd</a> · <a href="../Blender/Architecture_Complete_V26_8_Fast.blend">流畅版模型</a> · <a href="V26_8_实景与修正复核.html">实景与结构复核</a></p><article><h2>本机视口对比</h2><table><tr><th>视角</th><th>原设置 FPS</th><th>流畅设置 FPS</th></tr>'''+''.join(rows)+'''</table><p>测试视口1920×1010，排除着色器预热后每项16帧，使用 Blender 原生窗口重绘计时；测试时原漫游窗口与其他程序仍在运行。这是本机该窗口尺寸下的对比值。</p></article><article><h2>保存的内容</h2><p>原始建筑网格、楼梯井和扶手结构、UV、贴图原件、材质图、门窗动画与碰撞网格均完整保留。仅降低实时显示负担：采用Eevee预览，减少实时阴影，限制视口贴图为2K，并以二像素步长显示实时预览；阴天环境与柔光保留。按M可临时在纹理和极速显示间切换。</p><p>漫游静止或窗口失焦时停止重复更新人物与相机；再次移动即可恢复。原修正主模型保留在原路径。</p></article><article><h2>院落：原设置 / 流畅设置</h2><div class="grid"><img loading="lazy" src="流畅模式对比/baseline_court.png"><img loading="lazy" src="流畅模式对比/fast_court.png"></div></article><article><h2>楼梯：原设置 / 流畅设置</h2><div class="grid"><img loading="lazy" src="流畅模式对比/baseline_stairs.png"><img loading="lazy" src="流畅模式对比/fast_stairs.png"></div></article><p><a href="V26_8_Performance_QA.json">重新读取模型与原生漫游检查</a> · <a href="V26_8_Viewport_Benchmark.json">原始计时记录</a></p><small>流畅版SHA256：'''+qa['model_sha256']+'''</small></html>'''
(R/'V26_8_流畅模式说明.html').write_text(page,'utf8')
main=R/'V26_8_实景与修正复核.html'
text=main.read_text('utf8')
banner='<p><a href="V26_8_流畅模式说明.html">已增加流畅漫游：查看性能对比和启动说明</a></p>'
if banner not in text:text=text.replace('<h1>',banner+'<h1>',1)
main.write_text(text,'utf8')
readme=O/'使用说明.txt'
old=readme.read_text('utf8')
prefix='''流畅模式更新

仍只使用“启动漫游.cmd”，默认已指向 Blender/Architecture_Complete_V26_8_Fast.blend。
已打开的旧漫游窗口需要重新启动后生效；当前未保存的窗口没有被关闭或覆盖。
阴天柔光、玻璃、建筑结构、原图与门窗动画保留。实时预览改用Eevee、2K视口贴图、二像素预览和更少实时阴影；不改贴图原件或建筑网格。按M切换纹理/极速显示。
人物静止或窗口失焦时不再重复更新。性能对比：Reports/V26_8_流畅模式说明.html。
原修正主模型Architecture_Complete_V26_8.blend保持原样，流畅版是单独保存的显示副本。

'''
if not old.startswith('流畅模式更新'):readme.write_text(prefix+old,'utf8')
manifest_path=O/'Manifest_SHA256.json'
manifest=json.loads(manifest_path.read_text('utf8'))
manifest['fast_model']=qa['model']
manifest['fast_model_sha256']=qa['model_sha256']
manifest['performance_checks']={'file':'V26_8_Performance_QA.json','checks':len(qa['checks']),'status':qa['status']}
manifest['default_launcher']='启动漫游.cmd -> Architecture_Complete_V26_8_Fast.blend'
manifest['files']=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}
                   for p in sorted(O.rglob('*'))if p.is_file()and p!=manifest_path]
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print('FAST_PACKAGE_READY',len(manifest['files']),len(qa['checks']),qa['model_sha256'])
