from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_5';O=Path('E:/jz/JIA/Rebuild_V26_5');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_5.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);reports=[]
for suffix in ['Native_Readback_QA','Geometry_QA','Interior_Physics_QA','Protected_Original_QA','Scoped_Overlap_QA','WC_Window_Regression_QA','Bay_Clearance_Regression_QA','Facade_Joint_Regression_QA']:
 fn='V26_5_'+suffix+'.json';q=json.loads((R/fn).read_text('utf8'));assert q['model_sha256']==h,(fn,'stale model hash');assert not q['failures'],(fn,q['failures']);reports.append({'file':fn,'status':q['status'],'checks':len(q['checks'])})
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd'];assert not list(O.rglob('*.3dm'))
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));assert sha(prep['source'])==prep['source_sha256'];S=O/'Sources';S.mkdir(exist_ok=True)
for f in [D/'Prepared_Geometry.json']+[D/r['file']for r in prep['objects']]:shutil.copy2(f,S/f.name)
for name in ['v26_5_prepare.py','v26_5_facade_recipe.py','v26_5_build.py','v26_5_readback.py','v26_5_geometry_qa.py','v26_5_physics_qa.py','v26_5_protection_qa.py','v26_5_overlap_after.py','v26_5_overlap_gate.py','v26_5_render.py','v26_5_views.py','v26_5_package.py','v26_2_common.py','v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,S/name)
for folder,name,new in [('v26_5_left_audit','regression_saved.py','bay_regression_saved.py'),('v26_5_wc_audit','saved_native_qa.py','wc_regression_saved.py'),('v26_5_facade_audit','saved_native_qa.py','facade_regression_saved.py'),('v26_5_facade_audit','precision_review.py','triangle_precision_review.py')]:
 src=W/folder/name
 if src.exists():shutil.copy2(src,S/new)
names=['001202','001324','001426','001913','001940']
for k in names:shutil.copy2(Path('D:/Desktop')/f'屏幕截图 2026-10-24 {k}.jpg',O/'References'/f'问题截图_{k}.jpg')
previews=[]
for m in sorted((D/'Review').glob('After_*_Cycles.json')):
 q=json.loads(m.read_text('utf8'));assert q['model_sha256']==h,(m,'stale render');shutil.copy2(m,R/m.name);shutil.copy2(m.with_suffix('.png'),R/m.with_suffix('.png').name);previews.append(m.with_suffix('.png').name)
assert len(previews)==7
for tag in ['04_F1_Left_Room_Tile','09_F1_Right_WC_Rear_Corner','10_F1_Left_Rear_Window_Head','12_Exterior_Right_Bay_Joints','13_Exterior_Floor_Band']:
 for ext in ['.png','.json']:
  f=D/'Review'/('Before_'+tag+'_Solid'+ext);shutil.copy2(f,R/f.name)
readme='''Rebuild_V26.5 — 对应 2026-10-24 五张问题截图的 Blender 修正版

模型：Blender\\Architecture_Complete_V26_5.blend
漫游：启动漫游.cmd
复核图：Reports\\V26_5_截图问题复核.html

本轮修正：
1. 首层右卫生间后墙和100mm隔墙收口；窗台、窗头不再穿过隔墙形成小悬块。
2. 首层三个后高窗的旧错台和窗头缺口整理，原窗框与玻璃保留。
3. 西院墙瓦顶接飘窗端局部裁切，消除穿入一楼左房斜玻璃的瓦片；裁切之外保留原表面。
4. 一二楼东、西、后侧外墙与楼板边缘连续连接，楼梯井保持原有开口。
5. 五组飘窗正斜面转角的多余白色竖片清除，原黑色窗框、玻璃和开启关系保留。

普通墙段厚度上限240mm；本轮整理的后墙220.2mm，卫生间内隔墙100mm。转角和原梁柱节点单独保留。
一楼既有房间和两个卫生间入口关系、次照壁、原入口坡、三楼白色天花保持。
V26.4 原文件未覆盖。本目录只提供 Blender 模型，未生成 Rhino 文件及两个被取消的打开脚本。
检查基于重新打开的保存模型；专项报告列明点位、精度和覆盖范围。7张修正后预览均为本文件的原生材质渲染。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf8')
pairs=[('001202','09_F1_Right_WC_Rear_Corner','卫生间后角：清除旧凸条及穿过隔墙的小悬块'),('001324','04_F1_Left_Room_Tile','左房：西院墙瓦顶不再穿入斜玻璃'),('001426','10_F1_Left_Rear_Window_Head','后高窗：窗头收口连续，保留原梁柱'),('001913','13_Exterior_Floor_Band','外立面：补齐一二楼外墙与楼板边缘'),('001940','12_Exterior_Right_Bay_Joints','飘窗：清理正斜面转角多余白色竖片')]
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.5 截图问题复核</title><style>body{font:17px/1.65 "Microsoft YaHei",sans-serif;max-width:1400px;margin:35px auto;background:#f2f4f6;color:#182c3b;padding:20px}article{background:white;border-radius:8px;padding:24px;margin:26px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%;max-height:870px;object-fit:contain;background:#e9edef}h1{font-size:30px}h2{font-size:23px}small{overflow-wrap:anywhere}a{color:#125f85}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style><h1>V26.5 五处截图问题复核</h1><p>左列为用户原始问题截图，右列为修正后保存模型的原生材质渲染。相机点位与模型哈希见对应 JSON。</p><p>普通墙段上限 240 mm，转角及原梁柱节点保留。原模型 V26.4 未覆盖。</p>']
for k,tag,title in pairs:parts.append('<article><h2>'+title+'</h2><div class="grid"><div><p>用户问题截图</p><img src="../References/问题截图_'+k+'.jpg"></div><div><p>V26.5 保存模型材质预览</p><a href="After_'+tag+'_Cycles.png"><img src="After_'+tag+'_Cycles.png"></a></div></div></article>')
parts.append('<article><h2>保存模型复核</h2><p>原窗框、玻璃、门窗动画、次照壁、入口坡与原梁柱保留；重新打开后完成几何和漫游检查。检查覆盖范围及数值精度以各专项记录为准。</p><ul>')
for r in reports:parts.append('<li><a href="'+r['file']+'">'+r['file']+'</a>：'+r['status']+'（'+str(r['checks'])+' 项）</li>')
parts.append('</ul><small>模型 SHA256：'+h+'</small></article></html>');(R/'V26_5_截图问题复核.html').write_text(''.join(parts),encoding='utf8')
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='Manifest_SHA256.json':files.append({'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'source_model':prep['source'],'source_sha256':prep['source_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGED',str(P),h,'FILES',len(files),'CHECKS',sum(x['checks']for x in reports),flush=True)
