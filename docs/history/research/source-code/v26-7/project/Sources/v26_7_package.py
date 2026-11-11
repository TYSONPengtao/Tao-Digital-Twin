from pathlib import Path
import json,hashlib,shutil,sys
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_7_views import VIEWS
D=W/'v26_7';O=Path('E:/jz/JIA/Rebuild_V26_7');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_7.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);reports=[]
for tag in ['Native_Readback_QA','Geometry_QA','Interior_Physics_QA','Protected_Original_QA','Scoped_Overlap_QA','Column_Projection_QA','Railing_Regression_QA','Site_Material_QA','Gate_Regression_QA','Visual_QA']:
 name='V26_7_'+tag+'.json';q=json.loads((R/name).read_text('utf8'));assert q['model_sha256']==h,(name,'stale model hash');assert not q['failures']and all(c['pass']for c in q['checks']),(name,q['failures']);reports.append({'file':name,'checks':len(q['checks']),'status':q['status']})
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));assert sha(prep['source'])==prep['source_sha256']
assert [p.name for p in O.glob('*.cmd')]==['启动漫游.cmd'];assert not list(O.rglob('*.3dm'))
S=O/'Sources';S.mkdir(exist_ok=True)
for p in[D/'Prepared_Geometry.json']+[D/r['file']for r in prep['objects']]:shutil.copy2(p,S/p.name)
for name in ['v26_7_build.py','v26_7_collect.py','v26_7_finalize_house.py','v26_7_gate_prepare.py','v26_7_readback.py','v26_7_protection_qa.py','v26_7_geometry_qa.py','v26_7_physics_qa.py','v26_7_gate_qa.py','v26_7_overlap_after.py','v26_7_overlap_gate.py','v26_7_render.py','v26_7_views.py','v26_7_make_checks.py','v26_7_extra_checks.py','v26_7_package.py','v26_2_common.py','v24_16_common.py','v24_06_common.py','v24_qa_blender.py']:
 shutil.copy2(W/name,S/name)
shutil.copy2(W/'v26_7_visual_qa.py',S/'v26_7_visual_qa.py')
(S/'源码存档说明.txt').write_text('本目录是此次修正的输入几何、脚本和依据存档，不是可独立移动运行的复建程序包。\n构建与QA脚本依赖原工作目录 '+str(W)+' 及其中的历史版本几何缓存、Python依赖、V26.6源模型。\n交付模型和启动漫游.cmd可直接按使用说明打开。请勿在Sources目录直接运行构建脚本覆盖模型。\n','utf8')
for folder,names in[
 ('v26_7_site_audit',['apply_site_materials.py','Lower_Strata_Continuous_Arc_Mapping.json','Build_Material_Recipe.json','Prepared_Site_Decoration.json','saved_material_qa.py','README.md']),
 ('v26_7_railing_audit',['build_candidate.py','Prepared_Railing.json','saved_native_qa.py','Railing_Candidate_QA.json']),
 ('v26_7_column_audit',['prepare_candidate.py','saved_native_qa.py','Column_Projection_Findings.json'])]:
 target=S/folder;target.mkdir(exist_ok=True)
 for name in names:shutil.copy2(W/folder/name,target/name)
REF=O/'References';REF.mkdir(exist_ok=True)
for k in ['022453','022541','022618','022421','022909','023100','023323','023700']:
 shutil.copy2(Path('D:/Desktop')/f'屏幕截图 2026-10-24 {k}.jpg',REF/f'问题截图_{k}.jpg')
for folder,src in [('楼梯扶手实景',Path('E:/jz/JIA/Rebuild_V26_6/References/楼梯实景')),('楼梯墙面实景',W/'v26_7_stair_audit/References'),('院墙实景',W/'v26_7_site_audit/References')]:
 target=REF/folder;target.mkdir(exist_ok=True)
 if src.exists():
  for f in src.iterdir():
   if f.is_file():shutil.copy2(f,target/f.name)
target=REF/'内大门实景';target.mkdir(exist_ok=True)
for t,l in[(650,0),(650,1),(655,0),(655,1),(660,1)]:
 p=W/'v26_7_gate_audit/Fine'/f'Actual_t{t:04d}_L{l}_Yaw0_Pitch-35.jpg';shutil.copy2(p,target/p.name)
q=json.loads((W/'v26_7_gate_audit/Fine/Frame_Provenance.json').read_text('utf8'));q['rows']=[r for r in q['rows']if(target/r['file']).exists()];(target/'Frame_Provenance.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
for tag,*_ in VIEWS:
 f=D/'Review'/('After_'+tag+'_Cycles.json');q=json.loads(f.read_text('utf8'));assert q['model_sha256']==h,(tag,'stale render');shutil.copy2(f,R/f.name);shutil.copy2(f.with_suffix('.png'),R/f.with_suffix('.png').name)
for tag in['07_Gate_Threshold_Front','09_Gate_Inner_Low_Return']:
 for ext in['.png','.json']:
  p=D/'Review'/('Before_'+tag+'_Cycles'+ext);shutil.copy2(p,R/p.name)
readme='''Rebuild_V26.7 — 依据实景继续修正的 Blender 模型

模型：Blender\\Architecture_Complete_V26_7.blend
漫游：启动漫游.cmd
截图、实景依据与修正图：Reports\\V26_7_实景与修正复核.html

1. 墙柱与窗下：检查35个旧合成柱节点，裁去室内侧不符合相邻墙面的旧柱芯、光晕状收口和窗下凸块；整理各层后窗窗台、窗头。楼梯井西、南、北侧错误的92.2mm楼层凸带收齐墙面。普通墙段不超过240mm，一楼既有卫生间100mm隔墙和200mm侧墙关系保留；原梁下挂、四个梯段、两个中平台和东侧到达层可行走楼板保留。普通墙与真实梁柱转角不能等同于所有实景构件均无凸出。

2. 木扶手：按原实景车木形态整理起步U形回弯、球下接头、上端斜接柱帽和细倒棱，消除三楼后护栏穿球；五个端部空档补杆，原110根立杆座位和七个起止/转角柱位保留。新增间距与截面细节是实景关系拟合，不作为现场测量或构件设计数据。

3. 内大门：旧门槛仍沿用院坪降低前的高程，形成约250mm高的叠块；本轮按实景低石门槛关系与当前院坪配合，顶面拟合至Z=-0.50m，比院坪约高100mm；门扇、门框下沿同步配合，原门扇平面、合页、上部雕刻和贴图不改。侧后方缺失的走廊地坪/基座转角补齐到原走廊标高，原地面和入口坡未覆盖。这些尺寸继承现模型坐标并按画面关系拟合，未经现场标定测量。

4. 院墙：白色腰线只保留照壁范围，其他外墙对应位置恢复连续青砖。次照壁旁重复添加的斜檐带和斜向装饰共5228面清除，显露原水平装饰；原次照壁11构件保持。次照壁下方误用青砖的区域恢复相邻条石、毛石层次，上部原照片映射和原源高度属性保留。

本轮从V26.6另存，原文件未覆盖。实景来自用户原图与原INSV视频，References保留时刻、镜头和哈希，没有生成的实景图。14张修正图来自本保存模型的原生渲染；为看清室内，复核进程临时加75W相机补光，补光没有写入模型，也不代表现场实测照明。检查报告列明覆盖范围。仅保留一个漫游入口，没有生成两个被取消的打开脚本或Rhino文件。

当前边界：本轮针对标注问题复核。原照片纹理仍有周期重复，次照壁墙脚接缝处可见局部纹理尺度切换；没有宣称全场无缝贴图或现场实测还原。Sources为源码与输入存档，依赖原工作目录，不作为独立可移植复建包。
'''
(O/'使用说明.txt').write_text(readme,'utf8')
titles=['楼梯间错误横向凸带收齐墙面','二楼后窗下凸块与柱边整理','楼梯厅门边墙柱收口','扶手起步U形回弯','三楼球下接头与后护栏','平台与连续木扶手','内大门低石门槛','内大门侧后方转角','门后侧地坪与基座补齐','门后另一侧收口','非照壁院墙恢复青砖腰线','次照壁旁恢复原水平檐带','次照壁墙脚恢复条石与毛石层次','三楼白平顶与窗角回归复核']
parts=['''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.7 实景与修正复核</title><style>body{font:17px/1.7 "Microsoft YaHei",sans-serif;max-width:1380px;margin:30px auto;padding:20px;background:#f2f4f5;color:#20313d}article{background:white;padding:24px;margin:25px 0;border-radius:7px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%;max-height:860px;object-fit:contain;background:#e7ecef}h1{font-size:30px}h2{font-size:22px}small{overflow-wrap:anywhere}a{color:#145f84}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style><h1>V26.7 实景与修正复核</h1><p>本轮修正墙柱错台、扶手节点、内大门与院墙分层。实景用于核对可见构件关系和饰面，未经标定的视频不等同于实测尺寸。原次照壁11构件、门窗玻璃、踏步和入口坡保留。</p><p>所有修正图来自本文件原生材质渲染，临时75W复核补光未写入模型。</p>''']
for title,ref,after in[
 ('楼梯墙面实景依据：原INSV125秒镜头0','../References/楼梯墙面实景/Actual_INSV_0125s_L0.jpg','After_01_F2_Stair_Wall_Bands_Cycles.png'),
 ('扶手实景依据','../References/楼梯扶手实景/屏幕截图 2026-10-23 015914.jpg','After_04_F1_Railing_Start_Cycles.png'),
 ('院墙实景依据','../References/院墙实景/屏幕截图 2026-10-23 020742.jpg','After_13_Secondary_Stone_Base_Cycles.png'),
 ('门槛实景依据：原INSV655秒镜头1','../References/内大门实景/Actual_t0655_L1_Yaw0_Pitch-35.jpg','After_07_Gate_Threshold_Front_Cycles.png')]:
 parts.append('<article><h2>'+title+'</h2><div class="grid"><img src="'+ref+'"><img src="'+after+'"></div></article>')
issues=[('022453','01_F2_Stair_Wall_Bands'),('022541','02_F2_Rear_Window_Underpanel'),('022618','03_F2_Stair_Door_Corner'),('022909','09_Gate_Inner_Low_Return'),('023100','07_Gate_Threshold_Front'),('023323','11_Exterior_NonScreen_Brick_Band'),('023700','12_Secondary_Level_Flank')]
for k,tag in issues:
 parts.append('<article><h2>问题截图 '+k+'</h2><div class="grid"><div><p>用户标注</p><img src="../References/问题截图_'+k+'.jpg"></div><div><p>对应部位保存模型复核</p><img src="After_'+tag+'_Cycles.png"></div></div></article>')
for (tag,*_),title in zip(VIEWS,titles):
 fn='After_'+tag+'_Cycles.png';parts.append('<article><h2>'+title+'</h2><a href="'+fn+'"><img src="'+fn+'"></a></article>')
parts.append('<article><h2>保存模型检查</h2><p>门槛100mm为相对现院坪的模型拟合值；立杆间距和造型细节为照片关系拟合。报告不表示建筑所有部位均已完成实测还原。原纹理仍有周期重复，墙脚接缝局部仍可见尺度切换。Sources是依赖原工作目录的源码存档。</p><ul>')
for r in reports:parts.append('<li><a href="'+r['file']+'">'+r['file']+'</a>：'+r['status']+'，'+str(r['checks'])+'项</li>')
parts.append('</ul><small>模型 SHA256：'+h+'</small></article></html>');(R/'V26_7_实景与修正复核.html').write_text(''.join(parts),'utf8')
files=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.rglob('*'))if p.is_file()and p.name!='Manifest_SHA256.json']
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'source_model':prep['source'],'source_sha256':prep['source_sha256'],'checks':reports,'files':files},ensure_ascii=False,indent=2),'utf8')
print('PACKAGED',str(P),h,'FILES',len(files),'CHECKS',sum(r['checks']for r in reports),flush=True)
