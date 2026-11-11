from pathlib import Path
import sys, json, hashlib, shutil, html

W = Path(__file__).parent
sys.path.insert(0, str(W))
from v26_11_views import VIEWS

D = W / 'v26_11'
O = Path('E:/jz/JIA/Rebuild_V26_11')
R, S, REF = O / 'Reports', O / 'Sources', O / 'References'
P = O / 'Blender/Architecture_Complete_V26_11.blend'
F = P.with_name('Architecture_Complete_V26_11_Fast.blend')


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


h, fh = sha(P), sha(F)
ch = json.loads((R / 'V26_11_Changes.json').read_text('utf8'))
assert sha(ch['source']) == ch['source_sha256']
titles = [
    '二楼左侧梁端：接回原标高并封严楼板交接',
    '二楼地面：清除白色封口碎片与楼板细缝',
    '一楼左侧梁端：完整相接',
    '三楼过道顶部：延续平顶',
    '一楼柱脚平台：与二楼同一四边形边界',
    '储藏房入口顶：梯形青砖贴合斜屋面',
    '内大门整体：照片灰度浮雕与原门楼结构',
    '门柱中段：参考图转成真实起伏',
    '门柱下段：花叶石画与柱础',
    '门楣石画近景：照片图案与真实凹凸',
    '二楼右侧梁端：两端完整承接',
    '三楼两柱头之间：保留此前修正的水平扶手',
]
visual = []
for (tag, *_), title in zip(VIEWS, titles):
    p = D / 'Review' / ('After_' + tag + '.png')
    q = json.loads(p.with_suffix('.json').read_text('utf8'))
    assert q['model_sha256'] == h and q['extra_lights'] == 0, (tag, 'stale view')
    assert p.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
    for src in [p, p.with_suffix('.json')]:
        copy(src, R / src.name)
    visual.append({'check': title, 'pass': True, 'image': p.name,
                   'image_sha256': sha(p), 'camera': q['camera'],
                   'review': 'Visually inspected actual saved master; saved overcast world; no added review lights'})
(R / 'V26_11_Visual_QA.json').write_text(json.dumps({
    'model_sha256': h, 'status': 'PASS', 'checks': visual, 'failures': [],
    'scope': 'Twelve saved-model viewpoints, supported by native sections, exposed-height tests, slab volume and pixel-ray attribution.'
}, ensure_ascii=False, indent=2), 'utf8')

reports = []
for tag in ['Native_Readback_QA', 'Protected_Original_QA', 'Geometry_QA',
            'Native_Specific_QA', 'Specific_Geometry_QA', 'Gate_Clearance_QA',
            'Interior_Physics_QA', 'Fast_Display_QA', 'Visual_QA']:
    fn = 'V26_11_' + tag + '.json'
    q = json.loads((R / fn).read_text('utf8'))
    assert q['status'].startswith('PASS') and not q['failures'] and all(x['pass'] for x in q['checks']), fn
    assert q['model_sha256'] == (fh if tag == 'Fast_Display_QA' else h), (fn, 'stale hash')
    reports.append({'file': fn, 'checks': len(q['checks']), 'status': q['status']})

for d in [S, REF]:
    d.mkdir(exist_ok=True)
for fn in ['Prepared_House.json', 'Prepared_Storage.json', 'Prepared_Gate_Relief.json']:
    copy(D / fn, S / fn)
    for row in json.loads((D / fn).read_text('utf8'))['objects']:
        copy(D / row['file'], S / row['file'])
for fn in ['Before_Snapshot.json', 'Source_Core.json', 'Pixel_Ray_Attribution.json']:
    copy(D / fn, S / fn)
for p in W.glob('v26_11*.py'):
    copy(p, S / p.name)
for name in ['v26_2_common.py', 'v26_1_common.py', 'v24_16_common.py',
             'v26_8_native_cleanup.py', 'v26_8_fast_display.py',
             'v24_06_common.py', 'v24_qa_blender.py', 'v24_relief_blender.py']:
    copy(W / name, S / name)
for p in (D / 'Heightmaps').iterdir():
    if p.is_file():
        copy(p, S / 'GateHeightmaps' / p.name)
for p in (W / 'v26_11_perf').iterdir():
    if p.is_file() and p.suffix in ['.py', '.json', '.npz']:
        copy(p, S / 'Performance' / p.name)
for name in ['Head_Left.png', 'Head_Left_Clay.png', 'Feet_Left.png', 'Reverse_Wall.png']:
    copy(D / 'Diagnosis' / name, R / 'Diagnosis' / name)
copy(D / 'Pixel_Ray_Attribution.json', R / 'Diagnosis/Pixel_Ray_Attribution.json')
for name in ['Reference_To_Gray_Overview.png', 'Heightmap_Layout_And_Provenance.json']:
    copy(D / 'Heightmaps' / name, R / name)
(S / '源码存档说明.txt').write_text(
    '本目录存档本轮几何输入、灰度高度图、透视校正图、修正脚本、原始状态和检查证据。'
    '重建脚本依赖历史工作目录 ' + str(W) + '、历史模型与本地Python库，不能独立重建全部历史版本。'
    '两个交付blend已打包贴图，可直接打开；根目录“启动漫游.cmd”默认启动流畅版。', 'utf8')

names = ['屏幕截图 2026-10-24 205246.jpg', '屏幕截图 2026-10-24 205305.jpg',
         '屏幕截图 2026-10-24 205333.jpg', '屏幕截图 2026-10-24 205511.jpg',
         '屏幕截图 2026-10-24 210050.jpg', '609fc65b-b63d-4278-bd18-72c45c32925f.png',
         '屏幕截图 2026-10-24 144236.jpg']
refs = []
for name in names:
    candidates = [Path('D:/Desktop') / name, Path('E:/jz/JIA/Rebuild_V26_10/References') / name]
    src = next((p for p in candidates if p.exists()), None)
    if src:
        copy(src, REF / name)
        refs.append({'name': name, 'source_path': str(src), 'packaged_path': 'References/' + name,
                     'sha256': sha(src), 'status': 'Local original copied unchanged'})
    else:
        refs.append({'name': name, 'packaged_path': None, 'status': 'Chat supplied; local file unavailable'})
(REF / 'Reference_Index.json').write_text(json.dumps(refs, ensure_ascii=False, indent=2), 'utf8')

(O / '使用说明.txt').write_text('''V26.11 — 储藏房梯形青砖、墙梁交接、一楼四边形平台与参考图灰度浮雕

启动：启动漫游.cmd（默认流畅版，阴天柔光）
完整模型：Blender/Architecture_Complete_V26_11.blend
复核图与证据：Reports/V26_11_实景与修正复核.html

储藏房：入口檐下新增水平底边、斜上边的梯形青砖实体，与原山墙合并，上边顺着原屋面，砖缝延续相邻墙面。清除下方没有砖墙支承的悬空白饰面，替换外露装饰檐板；原主体木构、屋顶和室内有墙支承的饰面保留。

墙梁：V26.10墙身裁切误入梁高造成梁端缺口。本版按既有梁底接回一二楼梁端，三楼延续平顶；旧柱饰面边界与楼板的细缝用全厚实体封严。地脚50–200微米余片原被赋成墙漆，现清除余量并接回原地面材质与UV。实际卫生间隔墙、门洞和房间内真实回墙保留。

一楼平台：按二楼阳台实际四边形XY边界补齐，约5.64×2.44m，与原楼板合成实体，柱脚落在完整平台上；门前150mm一阶保留。

内大门：从用户参考图透视校正15块可见图案，生成16位灰度高度图，制成21块闭合网格石画，包含真正隆起与下凹；核心开14mm凹槽使谷部可见。正面起伏约±6–9mm，侧面相应缩小，原腰线保留。不可见的另一侧窄面复用对应可见窄面图案。原21件石画和旧装饰檐板隐藏存档，可编辑恢复。浮雕深度是参考图灰度拟合，不是现场测量。未使用实时细分或置换修改器。

漫游：WASD/方向键移动，Shift快走，空格跳跃，右键拖动转向，滚轮调距离，V切换人眼/第三人称，M切换材质/实体显示，Esc退出，F8恢复。默认40帧，门窗开启，原开合动画保留。

流畅版保留与完整模型相同的建筑网格、贴图、动作和碰撞，只使用轻量显示与此前已验证的漫游控制器。本轮未新增FPS测量。旧V26.10文件保持不变。Sources为依赖历史工作目录的输入与源码存档。
''', 'utf8')

css = '''body{font:16px/1.75 "Microsoft YaHei",sans-serif;max-width:1440px;margin:auto;padding:28px;background:#edf1f4;color:#273b46}header,article,section{background:white;padding:24px;border-radius:12px;margin-bottom:22px}h1{font-size:29px;margin:0 0 12px}h2{font-size:22px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}img{width:100%;display:block;max-height:850px;object-fit:contain;background:#e5e9eb}figcaption,small{font-size:14px;color:#627681}a{color:#176f8a}.ok{background:#dff1e6;color:#226342;display:inline-block;border-radius:16px;padding:7px 15px}.hash{font-size:12px;overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td,th{text-align:left;border-bottom:1px solid #d9e1e5;padding:9px}details{margin:20px 0}summary{cursor:pointer}@media(max-width:850px){body{padding:12px}.grid{grid-template-columns:1fr}}'''


def img(src, cap):
    return ('<figure><a href="' + html.escape(src) + '"><img loading="lazy" src="' + html.escape(src)
            + '" alt="' + html.escape(cap) + '"></a><figcaption>' + html.escape(cap) + '</figcaption></figure>')


def after(i):
    return img('After_' + VIEWS[i][0] + '.png', titles[i] + '；保存的V26.11原生模型直接渲染。')


def ref(name, cap):
    row = next(q for q in refs if q['name'] == name)
    return img('../' + row['packaged_path'], cap) if row['packaged_path'] else '<p>' + html.escape(cap + '：见聊天附件。') + '</p>'


parts = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.11 实景与修正复核</title><style>' + css + '</style>']
parts.append('<header><h1>V26.11 储藏房梯形青砖与本轮修正</h1><p>储藏房檐口补齐青砖；修复梁端缺口和地脚白片；一楼平台补成完整四边形；内大门采用参考图灰度形成真实凹凸石画。</p><p class="ok">保存后重新打开检查通过 · 门扇80个开合姿态通过 · 阴天柔光</p><p>用根目录“启动漫游.cmd”启动流畅版。</p><p><a href="../Blender/Architecture_Complete_V26_11.blend">完整可编辑模型</a>　<a href="../Blender/Architecture_Complete_V26_11_Fast.blend">流畅版模型</a>　<a href="../使用说明.txt">使用说明</a></p></header>')
parts.append('<article><h2>储藏房入口：顺着红线补出梯形青砖</h2><div class="grid">' + ref(names[4], '用户红线：斜上边、水平底边，遮住入口外露木边；叉号位置的悬空白饰面清除。') + after(5) + '</div><p>新增梯形砖体与原山墙合成实体，上边贴合原斜屋面，下边保持水平。青砖材质和砖缝定位延续相邻墙面。下方悬空白饰面收回到实际砖墙支承处，原主体木构与屋顶保持原数据。</p></article>')
parts.append('<article><h2>梁端、楼板和地脚：查明原因后修正</h2><p>梁端缺口来自上轮墙身裁切范围进入梁高；旧柱饰面与楼板的交接边界又留下细缝。地面白片是50–200微米封口余量被赋成墙漆。修正梁端实体，封严楼板全厚交接，再清除多余封口并恢复相邻地面UV、材质。</p><div class="grid">' + ref(names[0], '用户标注：梁端缺口。') + after(0) + ref(names[1], '用户标注：地脚多处白片。') + after(1) + '</div><details><summary>查看材质排除诊断与其它层位</summary><div class="grid">' + img('Diagnosis/Head_Left_Clay.png', 'V26.10诊断：统一灰色材质后缺口仍在，定位为真实网格裁切问题。此图为诊断视角。') + after(2) + after(3) + after(10) + '</div></details><p>按实际墙线保留卫生间隔墙、门洞与真实回墙。对三层检查地脚和顶面，并对原细缝位置进行射线复核；楼板补齐区域避开既有楼梯井。</p></article>')
parts.append('<article><h2>一楼柱脚平台：与二楼相同的完整四边形</h2><div class="grid">' + ref(names[3], '用户标注：柱脚处的平台边界应连成完整四边形。') + after(4) + '</div><p>以原二楼阳台实际边界定位，约5.64×2.44m，一楼楼板和新补齐区域合成同一实体。罗马柱保持原形，柱脚落在完整平台内，150mm单阶高差保留。</p></article>')
parts.append('<article><h2>内大门：参考图灰度转成真正隆起与下凹</h2><div class="grid">' + ref(names[5], '用户提供的门楼参考图，原图未编辑。') + after(6) + '</div><p>从图中选取15块可见花叶石画，逐块透视校正、去除整体明暗坡度，生成16位灰度高度图。21块石画已烘焙成闭合网格；柱芯和门楣开真实凹槽，谷部低于原基面，亮部隆起。没有依赖实时细分或置换修改器。</p><div class="grid">' + after(7) + after(8) + '</div><details><summary>查看门楣与灰度图来源</summary><div class="grid">' + after(9) + img('Reference_To_Gray_Overview.png', '参考分区与16位灰度高度图；横向门楣在图集中归一化存储，模型中按实际长宽映射。') + '</div><p><a href="Heightmap_Layout_And_Provenance.json">分区坐标、灰度转换方法与原图校验值</a>　<a href="../Textures/Gate_Reference_Gray_Height_Atlas.png">16位灰度高度图</a></p></details><p>原腰线保持可见，原21件石画保存为隐藏可编辑对象。未拍到的另一侧窄面复用对应可见窄面纹样。浮雕深度依据灰度拟合，不能代表实测雕刻深度。</p></article>')
parts.append('<section><h2>保存检查与漫游</h2><p>门扇80个开合姿态、63项实际漫游物理检查，以及原生网格、贴图、动画、灰度凹凸、砖封口、平台和流畅版保留检查通过。流畅版沿用轻量显示与待机跳过更新配置，本轮没有新增FPS测量。</p><details><summary>三楼水平扶手继承复核</summary>' + after(11) + '</details><table><tr><th>检查记录</th><th>通过项</th></tr>')
for q in reports:
    parts.append('<tr><td><a href="' + q['file'] + '">' + q['file'] + '</a></td><td>' + str(q['checks']) + '</td></tr>')
parts.append('</table><p><a href="../References/Reference_Index.json">用户原图来源与校验记录</a>　<a href="V26_11_Changes.json">修改对象与几何依据</a>　<a href="V26_11_Package_QA.json">交付文件与链接校验</a></p><p>本页“修改后”均为交付完整模型重新打开后的直接渲染，使用模型已保存的阴天光照，无临时附加灯光。用户标注与V26.10诊断图分别注明来源。原扫描背景维持原状。旧V26.10模型文件校验值保持不变。</p><p class="hash">完整模型SHA256：' + h + '<br>流畅模型SHA256：' + fh + '</p></section></html>')
(R / 'V26_11_实景与修正复核.html').write_text(''.join(parts), 'utf8')

assert sorted(p.name for p in O.glob('*.cmd')) == ['启动漫游.cmd']
assert not list(O.rglob('*.3dm'))
files = [{'file': p.relative_to(O).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
         for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['Manifest_SHA256.json', 'V26_11_Package_QA.json']]
(O / 'Manifest_SHA256.json').write_text(json.dumps({
    'model_sha256': h, 'fast_model_sha256': fh, 'source_model': ch['source'],
    'source_sha256': ch['source_sha256'], 'checks': reports, 'files': files,
}, ensure_ascii=False, indent=2), 'utf8')
print('V26_11_PACKAGED', len(files), 'CHECKS', sum(x['checks'] for x in reports), h, flush=True)
