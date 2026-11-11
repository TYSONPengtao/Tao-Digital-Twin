from pathlib import Path
import json, hashlib, shutil, html

W=Path(__file__).parent
D=W/'v26_6'
O=Path('E:/jz/JIA/Rebuild_V26_6')
R=O/'Reports'
P=O/'Blender/Architecture_Complete_V26_6.blend'

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

h=sha(P)
shutil.copy2(W/'v26_6_stair_audit/F2_Landing_Visual_QA.json',R/'V26_6_Stair_Visual_QA.json')
reports=[]
for suffix in ['Native_Readback_QA','Geometry_QA','Interior_Physics_QA','Protected_Original_QA','Scoped_Overlap_QA','Stair_Finish_Regression_QA','AsBuilt_Terrace_Regression_QA','Facade_Joint_Regression_QA','Neutral_White_Preview_QA','Stair_Visual_QA','AsBuilt_Terrace_Visual_QA']:
 name='V26_6_'+suffix+'.json'
 q=json.loads((R/name).read_text('utf8'))
 assert q['model_sha256']==h,(name,'stale hash')
 assert q['status'].startswith('PASS') and not q['failures'] and all(c['pass'] for c in q['checks']),(name,q['failures'])
 reports.append({'file':name,'checks':len(q['checks']),'status':q['status']})
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']
assert not list(O.rglob('*.3dm'))
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))
assert sha(prep['source'])==prep['source_sha256']

S=O/'Sources'
S.mkdir(exist_ok=True)
for f in [D/'Prepared_Geometry.json']+[D/r['file'] for r in prep['objects']]:shutil.copy2(f,S/f.name)
for name in ['v26_6_prepare.py','v26_6_build.py','v26_6_readback.py','v26_6_geometry_qa.py','v26_6_physics_qa.py','v26_6_protection_qa.py','v26_6_overlap_after.py','v26_6_overlap_gate.py','v26_6_render.py','v26_6_views.py','v26_6_package.py','v26_2_common.py','v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,S/name)
for folder,names in [
 ('v26_6_stair_audit',['regression_saved.py']),
 ('v26_6_asbuilt_audit',['saved_native_qa.py','saved_facade_band_qa.py','saved_capsule_qa.py','extract_terrace.py']),
 ('v26_6_ceiling_audit',['final_preview_qa.py','final_geometry_qa.py'])]:
 target=S/folder;target.mkdir(exist_ok=True)
 for name in names:shutil.copy2(W/folder/name,target/name)

REF=O/'References'
stairs=REF/'楼梯实景';stairs.mkdir(parents=True,exist_ok=True)
for f in (W/'v26_6_stair_audit/References').iterdir():
 if f.is_file():shutil.copy2(f,stairs/f.name)
terrace=REF/'三楼露台实景';terrace.mkdir(parents=True,exist_ok=True)
for f in (W/'v26_6_asbuilt_audit').glob('Actual_*.jpg'):shutil.copy2(f,terrace/f.name)
for name in ['Frame_Provenance.json','AsBuilt_F3_Terrace_Crosswall_Findings.json','Findings_实景依据.txt']:
 shutil.copy2(W/'v26_6_asbuilt_audit'/name,terrace/name)
for k in ['005126','005202','005316']:
 shutil.copy2(Path('D:/Desktop')/f'屏幕截图 2026-10-24 {k}.jpg',REF/f'问题截图_{k}.jpg')

views=[
 ('01_F1_Landing_Front','一楼中平台：灰色前立面连续，踏步高程保持'),
 ('02_F2_Landing_Front','二楼中平台：消除剩余窄白条'),
 ('03_F2_Arrival_Front','二楼楼层入口：灰色行走前缘'),
 ('04_F3_Arrival_Front','三楼楼层入口：灰色行走前缘'),
 ('05_F2_Stair_Hall_West','二楼楼梯厅西向：原白色顶面和梁柱'),
 ('06_F2_Stair_Hall_East','二楼楼梯厅东向：保留真实梁底收边'),
 ('07_F3_Terrace_Open_Alcove','三楼露台：按实景去除错误填充墙'),
 ('08_F3_Alcove_Window_Heads','三楼双窗角：平整窗头及白色连续平顶'),
 ('09_F3_Alcove_Reverse_Opening','三楼窗角反向：保留横梁、两侧柱及露台开口'),
 ('10_F3_Stair_Hall_Ceiling','三楼楼梯厅：白色天花核对'),
]
for tag,title in views:
 f=D/'Review'/('After_'+tag+'_Cycles.json')
 q=json.loads(f.read_text('utf8'));assert q['model_sha256']==h,(f,'stale render')
 assert q['temporary_review_fill_watts']==75 and q['saved_model_unmodified']
 shutil.copy2(f,R/f.name);shutil.copy2(f.with_suffix('.png'),R/f.with_suffix('.png').name)

readme='''Rebuild_V26.6 — 依据原实景视频继续修正的 Blender 模型

模型：Blender\\Architecture_Complete_V26_6.blend
漫游入口：启动漫游.cmd
实景与修正图核对：Reports\\V26_6_实景依据与修正复核.html

本轮修正：
1. 对照原 INSV 115、125、140、150 秒楼梯画面，两个中平台及两个楼层到达前缘改用原有灰色石纹材质，消除平台窄白条。仅更改原面的材质，踏步和平台实体、高程、木扶手保持原样；原白色梯底与梁底保留。
2. 对照原 INSV 170、175、180、200、205 秒三楼露台画面，去除误补的西侧窗角前填充墙，恢复露台与窗角空间的开口。原顶部横梁、两侧柱、窗框和玻璃保留，一二楼隔墙不按此开口改动。
3. 整理该三楼双窗窗头的旧错台与小凸片，裁掉穿到室内平顶下的旧檐板，接齐原白色平顶；室外檐口与主屋顶保留。
4. 白色天花材质本身未变。默认材质预览由 forest.exr 改为 studio.exr，减轻森林环境造成的棕色偏色。studio.exr 仍有色温，不能当作严格中性色参考。另在模型中内嵌灰度环境，仅供中性渲染核对。

实景依据位于 References，包含原视频抽帧时刻、镜头编号和文件哈希；没有生成或合成的“实景证据”。未经测量标定的视频用于判断开口、构件关系和饰面，不作为实测尺寸。灰色石纹的具体岩石种类未据图推断。

普通墙段厚度上限240mm，转角和原梁柱节点另计。次照壁、原入口坡、门窗玻璃与开启动画保留。V26.5 原文件未覆盖。只提供 Blender 文件和漫游入口，未生成两个被取消的打开脚本或 Rhino 文件。

复核图是从保存后的本文件原生材质渲染，临时加入75W相机补光以看清室内；补光未保存到模型，也不代表现场实测照明。几何、材质、门窗动画和人体漫游检查均绑定本模型 SHA256。报告列明覆盖范围，不表示全建筑所有部位均已完成实测还原。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf8')

parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.6 实景依据与修正复核</title><style>body{font:17px/1.65 "Microsoft YaHei",sans-serif;max-width:1380px;margin:30px auto;background:#f1f3f5;color:#20313d;padding:20px}article{background:white;border-radius:7px;padding:24px;margin:25px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%;max-height:850px;object-fit:contain;background:#e9edef}h1{font-size:29px}h2{font-size:22px}small{overflow-wrap:anywhere}a{color:#176284}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style><h1>V26.6 实景依据与修正复核</h1><p>本轮围绕平台前缘、三楼露台错误填充墙、双窗窗头和平顶修正。原梁柱、木扶手、玻璃、次照壁和入口坡保留。以下实景均取自用户原图或原 INSV 视频。</p><p>实景视频用于核对构件关系、开口和饰面，未经标定的画面不代表实测尺寸。修正图来自本页所列哈希的保存模型；临时75W复核补光未写入模型。</p>''']
evidence=[
 ('楼梯灰色前缘及白色梯底','../References/楼梯实景/Actual_INSV_0125s_L0.jpg','原 INSV 125 秒，镜头0','After_01_F1_Landing_Front_Cycles.png','一楼中平台修正后'),
 ('三楼露台与窗角原本连通','../References/三楼露台实景/Actual_F3Terrace_t175_Lens0_Yaw0_FOV110.jpg','原 INSV 175 秒，镜头0','After_09_F3_Alcove_Reverse_Opening_Cycles.png','窗角向露台反向复核'),
 ('三楼双窗角为白色平顶','../References/三楼露台实景/Actual_F3Terrace_t170_Lens0_Yaw0_FOV110.jpg','原 INSV 170 秒，镜头0','After_08_F3_Alcove_Window_Heads_Cycles.png','双窗窗头及平顶修正后'),
]
for title,ref,caption,after,aftercap in evidence:
 parts.append('<article><h2>'+title+'</h2><div class="grid"><div><p>'+caption+'</p><a href="'+ref+'"><img src="'+ref+'"></a></div><div><p>'+aftercap+'</p><a href="'+after+'"><img src="'+after+'"></a></div></div></article>')
parts.append('<article><h2>用户标注问题</h2><p>三张原始截图仅作问题定位，几何调整依据上列真实照片及视频。</p><div class="grid">')
for k in ['005126','005202','005316']:
 ref='../References/问题截图_'+k+'.jpg';parts.append('<div><p>'+k+'</p><a href="'+ref+'"><img src="'+ref+'"></a></div>')
parts.append('</div></article>')
for tag,title in views:
 fn='After_'+tag+'_Cycles.png';parts.append('<article><h2>'+title+'</h2><a href="'+fn+'"><img src="'+fn+'"></a></article>')
parts.append('<article><h2>保存文件复核</h2><p>原白色材质未改。默认工作室材质预览有轻微色温；中性渲染核对使用单独内嵌灰度环境，不宣称还原现场照明。</p><ul>')
for r in reports:parts.append('<li><a href="'+r['file']+'">'+r['file']+'</a>：PASS（'+str(r['checks'])+' 项）</li>')
parts.append('</ul><p>普通墙段上限240mm，转角及原梁柱节点保留。原文件V26.5未覆盖。</p><small>模型 SHA256：'+h+'</small></article></html>')
(R/'V26_6_实景依据与修正复核.html').write_text(''.join(parts),encoding='utf8')

files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='Manifest_SHA256.json':files.append({'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'source_model':prep['source'],'source_sha256':prep['source_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGED',str(P),h,'FILES',len(files),'CHECKS',sum(x['checks'] for x in reports),flush=True)
