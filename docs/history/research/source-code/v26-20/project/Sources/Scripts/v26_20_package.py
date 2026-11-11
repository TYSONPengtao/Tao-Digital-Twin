"""Package the verified V26.20 artifacts without opening or saving either model."""
from pathlib import Path
import json, hashlib, shutil, html
from v26_20_views import VIEWS

W = Path(__file__).parent
D = W / 'v26_20'
O = Path('E:/jz/JIA/Rebuild_V26_20')
R, S = O / 'Reports', O / 'Sources'
V = R / 'Views'
for folder in [R, S, V, O / 'References', O / 'Textures']:
    folder.mkdir(parents=True, exist_ok=True)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text('utf8'))


source_index = read(D / 'Input/Source_Index.json')
source = Path(source_index['model'])
source_hash = source_index['sha256']
assert sha(source) == source_hash, 'Current V26.19 source bytes changed'
master = O / 'Blender/Architecture_Complete_V26_20.blend'
fast = O / 'Blender/Architecture_Complete_V26_20_Fast.blend'
mh, fh = sha(master), sha(fast)
qa_names = ['Native_QA', 'Geometry_QA', 'Fast_Display_QA', 'Interior_Physics_QA',
            'Runtime_Viewport_QA', 'Door_Clearance_QA']
qs = {name: read(R / ('V26_20_' + name + '.json')) for name in qa_names}
for name, q in qs.items():
    assert q['status'].startswith('PASS') and not q.get('failures'), (name, 'Failed QA')
    expected = fh if name in ['Fast_Display_QA', 'Runtime_Viewport_QA'] else mh
    assert q['model_sha256'] == expected, (name, 'Stale QA')
changes = read(R / 'V26_20_Changes.json')
assert changes['source_sha256'] == source_hash

titles = {
    '01_Storage_West_Entry': '储藏房西侧入口：室内高于室外150毫米',
    '02_Entry_Step_Close': '窄入口近景：只有一道150毫米竖向台阶',
    '03_Storage_Door_Clearance': '储藏房双扇门：修短下沿，保留门顶与动作',
    '04_Storage_Outer_Foundation': '外侧基础：原基础留位，续接上部与材质',
    '05_Kitchen_Storage_Interface': '厨房与储藏房交接：保护原厨房范围',
    '06_Kitchen_Unchanged': '厨房原地面、木构与墙体保持',
}
cases = [(view[0], titles[view[0]]) for view in VIEWS]
assert len(cases) == 6 and len({tag for tag, _ in cases}) == 6
for version in ['V26_19', 'V26_20']:
    for tag, _ in cases:
        for ext in ['png', 'json']:
            shutil.copy2(D / 'Review' / (version + '_' + tag + '.' + ext), V)
runtime = qs['Runtime_Viewport_QA']
assert len(runtime['captures']) == 4
for row in runtime['captures']:
    image = Path(row['image']).name
    for ext in ['png', 'json']:
        shutil.copy2(D / 'Review' / Path(image).with_suffix('.' + ext), V)

refs, missing_refs = [], []
desktop = Path('D:/Desktop')
tokens = ['205603', '205524', '205622', '205454', '225820', '2051454']
for token in tokens:
    original = desktop / ('屏幕截图 2026-10-25 ' + token + '.jpg')
    if not original.is_file():
        candidates = sorted(p for p in desktop.glob('*' + token + '.*')
                            if p.is_file() and p.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp'])
        original = candidates[0] if candidates else None
    if original is None:
        missing_refs.append(token)
        continue
    shutil.copy2(original, O / 'References' / original.name)
    refs.append({'token': token, 'path': 'References/' + original.name, 'sha256': sha(original)})

for folder in ['Input', 'Prepared', 'Final']:
    target = S / folder
    target.mkdir(exist_ok=True)
    assert (D / folder).is_dir(), ('Missing source evidence folder', folder)
    for path in (D / folder).rglob('*'):
        if path.is_file():
            dest = target / path.relative_to(D / folder)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
for path in D.iterdir():
    if path.is_file() and path.suffix.lower() in ['.json', '.txt']:
        shutil.copy2(path, S / path.name)
for filename in ['Before_Snapshot.json', 'Native_After_Snapshot.json',
                 'Native_Snapshot_Source_SHA256.txt', 'Protected_Object_State.json',
                 'Kitchen_Overlap_Audit.json', 'Prepared_Floor.json', 'Prepared_Doors.json',
                 'Prepared.json', 'Prepared_Geometry_QA.json', 'Check_Run.json']:
    assert (S / filename).is_file(), ('Missing audit artifact', filename)
(S / 'Scripts').mkdir(exist_ok=True)
for path in W.glob('v26_20_*.py'):
    if path.name != 'v26_20_make_helpers.py':
        shutil.copy2(path, S / 'Scripts' / path.name)
obsolete_generator = S / 'Scripts/v26_20_make_helpers.py'
if obsolete_generator.is_file():
    obsolete_generator.unlink()
for filename in ['v26_2_common.py', 'v26_15_native_cleanup.py', 'v24_06_common.py', 'v24_16_common.py']:
    shutil.copy2(W / filename, S / 'Scripts' / filename)
(S / 'Performance').mkdir(exist_ok=True)
for path in (W / 'v26_20_perf').glob('*'):
    if path.is_file():
        shutil.copy2(path, S / 'Performance' / path.name)
shutil.copy2(W / 'v26_20_perf/Fast_Build.json', R / 'V26_20_Fast_Build.json')
for path in source.parent.parent.joinpath('Textures').glob('*'):
    if path.is_file():
        shutil.copy2(path, O / 'Textures' / path.name)

(S / '脚本说明.txt').write_text(
    '本包保留现行V26.19原模型的输入索引与哈希、修改前及保存后快照、厨房范围与重叠审计、'
    '墙体和厨房保护状态、地面与门扇修改参数、输入/修改后/读回网格、原UV和材质分配、'
    '全部六类QA、同机位对照、实际Fast视口与性能配置脚本。Sources/Performance为继承的'
    '显示配置证据，本轮没有新增FPS测量。重跑脚本仍依赖原工作区的历史结构索引、'
    'geomlibs等库；日常编辑或漫游直接打开交付blend，无需运行重建脚本。'
    '本轮修改前的三件网格隐藏保存在V26.20_局部修正原件存档集合。', 'utf8')
(O / '使用说明.txt').write_text('''V26.20｜储藏房150毫米台阶与厨房关系复核

双击根目录“启动漫游.cmd”进入本版Fast漫游。
F8开始/停止；WASD或方向键移动；Shift快走；右键拖动转向；V切换人眼/跟随；空格跳跃；M测量；Esc结束。
完整编辑模型：Blender/Architecture_Complete_V26_20.blend
流畅漫游模型：Blender/Architecture_Complete_V26_20_Fast.blend
对照报告：Reports/V26_20_储藏房150mm台阶与厨房关系复核.html

1. 储藏房窄入口内的檐廊、后部室内及相连外廊铺地抬高150毫米，完成面Z=-0.25米；入口外院地面仍为Z=-0.40米，西侧窄入口只有一道150毫米台阶。
2. 墙体保持原位置、形状、可见状态和材质。厨房原地面、木构、墙体与原UV关系保持；抬高范围从X=13.421809米向储藏房一侧展开，避开原厨房。
3. 原基础Z=-0.4001米以下的区域保留，新增实体只位于原完成面以上150毫米范围；新顶面沿用原世界XY贴图尺度与起点，外侧新增竖面续接相邻基础材质及UV相位。仅新增的15厘米石材立面采用连续镜像取样，避免旧着色器在上沿拉伸最后一行；原照片、原材质节点及下部UV保持。
4. 两扇储藏房门只修短下沿150毫米并封底，门顶、合页轴、根对象和开合动画保留。门底与新地面约8.4毫米间隙，固定门框保持。
5. 以花盆已经移除的现行V26.19完整模型为源，继续保留该状态，以及既有梁端窗角、楼梯、门窗和内大门修正与阴天柔光。

Fast版延续既有显示配置，本轮没有新增FPS测试。QA、同机位前后对照和实际Fast材质视口均随包保存。原V26.19文件保持不变。
''', 'utf8')

cards = ''.join(
    f'<section><p class="num">{i:02d}</p><h2>{html.escape(title)}</h2><div class="pair">'
    f'<figure><img loading="lazy" src="Views/V26_19_{tag}.png"><figcaption>修改前 · 现行V26.19</figcaption></figure>'
    f'<figure><img loading="lazy" src="Views/V26_20_{tag}.png"><figcaption>修改后 · V26.20</figcaption></figure>'
    '</div></section>' for i, (tag, title) in enumerate(cases, 1))
labels = {'Native_QA': '保存后原生模型', 'Geometry_QA': '地面边界、厨房与UV',
          'Fast_Display_QA': 'Fast模型保真', 'Interior_Physics_QA': '实际漫游与碰撞',
          'Runtime_Viewport_QA': '实际Fast材质视口', 'Door_Clearance_QA': '双扇门全程净空'}
qa_links = ''.join(f'<a href="V26_20_{name}.json">{labels[name]} · 通过</a>' for name in qa_names)
vp_titles = ['入口外侧实际人眼漫游', '150毫米台阶实际材质视口',
             '储藏房门底净空实际材质视口', '储藏房外侧基础实际材质视口']
viewport_html = ''.join(
    f'<figure><img loading="lazy" src="Views/{html.escape(Path(row["image"]).name)}">'
    f'<figcaption>{vp_titles[i]}</figcaption></figure>' for i, row in enumerate(runtime['captures']))
reference_html = ''.join(f'<figure><img loading="lazy" src="../{html.escape(q["path"])}">'
                         f'<figcaption>用户标注 · {q["token"]}</figcaption></figure>' for q in refs)
reference_section = ('<details><summary>本次用户标注</summary><div class="refs">' +
                     reference_html + '</div></details>') if refs else ''
page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V26.20｜储藏房150mm台阶与厨房关系复核</title><style>
body{{margin:0;background:#f2f4f3;color:#203638;font:16px/1.8 "Microsoft YaHei",sans-serif}}main{{max-width:1240px;margin:auto;padding:38px 28px}}header{{padding-bottom:28px;border-bottom:1px solid #cbd6d3}}h1{{font-size:33px;line-height:1.5}}h2{{font-size:23px;margin:5px 0 18px}}a{{color:#126c71;text-underline-offset:4px}}nav{{display:flex;gap:20px;flex-wrap:wrap}}section{{padding:30px 0;border-bottom:1px solid #cbd6d3}}.pair,.vp,.refs{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}figure{{margin:0;background:white}}img{{width:100%;height:auto;display:block}}figcaption{{padding:10px 16px;color:#52706d;font-size:14px}}.num,.kicker{{font-size:13px;color:#65837b;letter-spacing:2px}}.num{{margin:0}}.qa{{display:flex;gap:12px;flex-wrap:wrap}}.qa a{{background:white;padding:14px}}.status{{display:inline-block;background:#deede2;color:#286146;padding:5px 14px;border-radius:5px}}summary{{cursor:pointer;color:#126c71}}footer{{font-size:13px;color:#627a70;padding:26px 0}}code{{font-size:12px;word-break:break-all}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{text-align:left;border-bottom:1px solid #dde5e2;padding:10px 14px}}@media(max-width:760px){{main{{padding:24px 15px}}h1{{font-size:27px}}.pair,.vp,.refs{{grid-template-columns:1fr}}}}</style><main>
<header><p class="kicker">建筑重建 / V26.20 / 2026.10.25</p><h1>储藏房室内抬高150毫米，窄入口形成一阶</h1><p>储藏房入口内的檐廊与后部室内地面连续抬高150毫米，西侧入口外院地面保留，入口处只有一道150毫米竖向台阶。墙体与厨房保持原位置和既有关系。</p><p class="status">保存后复核通过 · 原V26.19保留</p><nav><a href="../Blender/Architecture_Complete_V26_20.blend">完整编辑模型</a><a href="../Blender/Architecture_Complete_V26_20_Fast.blend">Fast漫游模型</a><a href="../使用说明.txt">启动说明</a></nav></header>
<section><h2>地面、墙体与厨房的边界</h2><table><tr><th>位置</th><th>本版关系</th></tr><tr><td>入口外院</td><td>原Z=-0.40米完成面保留</td></tr><tr><td>入口内檐廊、储藏房室内及相连外廊</td><td>Z=-0.25米，比外院高150毫米</td></tr><tr><td>西侧窄入口</td><td>X=13.421809米处形成单一竖向台阶；没有中间踏面</td></tr><tr><td>厨房与墙体</td><td>原位置、网格、材质、UV及可见状态按保护范围复核</td></tr></table><p>厨房与储藏房的旧地面、基础和场地已合成一个大网格，不能整体移动。此次按原配准储藏房范围限定新增的150毫米实体，以西侧X=13.421809米边界避开厨房，保留厨房原地面及其材质与UV关系。</p><p>原基础Z=-0.4001米以下的区域保持原位置，按区域取样核对原材质和UV。新顶面继续使用原世界XY贴图坐标，保持纹理尺度和起点；新增外侧竖面从相邻原基础面延续材质与UV相位，西侧台阶采用连续米制坐标。仅新增的15厘米石材立面采用连续镜像取样，避免旧着色器在上沿拉伸最后一行；原照片、原材质节点及下部UV保持。具体几何及UV误差记录见<a href="V26_20_Geometry_QA.json">保存后区域检查</a>。</p>{reference_section}</section>
<section><h2>门扇只修短下沿，门顶和合页保持</h2><p>地面抬高后，两扇储藏房门的原下沿会进入新地面。此次仅裁去下沿150毫米并补齐同木材封底，原门顶、固定上框、合页轴和门扇根对象位置保持；原开合动画继续使用。两扇门与新地面分别保留约8.3965和8.3991毫米间隙，原UV接缝与保留面纹理继续沿用。全程开合净空独立复核。</p><p>本版源于花盆已经移除的现行V26.19主模型，保留该状态和此前梁端窗角、楼梯、窗扇、内大门等修正，继承阴天柔光。</p></section>
{cards}<section><h2>保存后的实际检查</h2><div class="qa">{qa_links}</div><p>六组修改前后对照采用相同相机和光照。检查覆盖单阶尺寸、室内连续标高、原厨房范围、墙体保护状态、原基础区域、材质与UV、门扇开合及实时漫游。以下四张图片来自交付Fast模型的实际Blender材质视口，首张为入口外侧运行中的人眼漫游。</p><p>Fast版延续既有显示配置，本轮没有新增FPS测速。源网格、修改参数、保护状态、输入及读回数据、脚本与配置证据保留在Sources目录。</p><div class="vp">{viewport_html}</div></section>
<footer><p>模型中保留本轮修改前隐藏存档。原V26.19文件保持不变。</p><p>源V26.19 SHA256：<code>{source_hash}</code><br>主模型SHA256：<code>{mh}</code><br>Fast模型SHA256：<code>{fh}</code></p></footer></main></html>'''
(R / 'V26_20_储藏房150mm台阶与厨房关系复核.html').write_text(page, 'utf8')
(R / 'V26_20_Reference_Index.json').write_text(json.dumps(refs, ensure_ascii=False, indent=2), 'utf8')
summary = {'status': 'PASS', 'source': str(source), 'source_sha256': source_hash,
           'master_sha256': mh, 'fast_sha256': fh,
           'qa_checks': sum(len(q['checks']) for q in qs.values()), 'reports': qa_names,
           'references': len(refs), 'missing_reference_tokens': missing_refs,
           'before_after_pairs': 6, 'actual_viewport_captures': 4, 'png_count': 16,
           'cases': [tag for tag, _ in cases], 'new_fps_measurement': False}
(R / 'V26_20_Delivery_Summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), 'utf8')
assert sha(source) == source_hash and sha(master) == mh and sha(fast) == fh
manifest = [{'path': path.relative_to(O).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)}
            for path in sorted(O.rglob('*')) if path.is_file()
            and path.name not in ['V26_20_Manifest.json', 'V26_20_Package_QA.json']]
(R / 'V26_20_Manifest.json').write_text(json.dumps({'version': 'V26.20', 'files': manifest},
                                               ensure_ascii=False, indent=2), 'utf8')
print('PACKAGED', len(manifest), 'FILES', 'QA', len(qa_names), 'PAIRS', len(cases), flush=True)
