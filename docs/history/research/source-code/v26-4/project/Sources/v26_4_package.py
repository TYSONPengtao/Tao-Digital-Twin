from pathlib import Path
import json,hashlib,shutil,html
W=Path(__file__).parent;D=W/'v26_4';O=Path('E:/jz/JIA/Rebuild_V26_4');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_4.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);validation=[]
for fn in ['V26_4_Native_Readback_QA.json','V26_4_Geometry_QA.json','V26_4_Interior_Physics_QA.json','V26_4_Protected_Original_QA.json','V26_4_Scoped_Overlap_QA.json']:
 q=json.loads((R/fn).read_text('utf8'));assert q['model_sha256']==h,(fn,'stale result');assert not q.get('failures'),(fn,q.get('failures'));validation.append({'file':fn,'checks':len(q['checks']),'status':q['status']})
assert sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']
assert not list(O.rglob('*.3dm'))
refs=[('E:/jz/JIA/Rebuild_V24_20/References/09_downa77d.png','F1_User_Marked_Room_Relationships.png'),('E:/jz/JIA/Rebuild_V24_20/References/03_屏幕截图 2026-10-18 230016.jpg','F1_Actual_Right_WC_Entry.jpg')]
for name in ['Wide_L0_0160s_Y+40.jpg','Wide_L1_0212s_Y+00.jpg','Wide_L0_0218s_Y+00.jpg','Wide_L0_0235s_Y+40.jpg']:refs.append((str(W/'v5_video_plan'/name),'F3_Actual_'+name))
for src,name in refs:shutil.copy2(src,O/'References'/name)
review=[]
for meta in sorted((D/'Review').glob('*_Cycles.json')):
 q=json.loads(meta.read_text('utf8'))
 if q['model_sha256']!=h:continue
 image=meta.with_suffix('.png');assert image.exists();shutil.copy2(image,R/image.name);shutil.copy2(meta,R/meta.name);review.append(image.name)
assert len(review)>=7,('Final material previews not complete',len(review))
for fn in ['Wall_Thickness_Proof.json','Prepared_Geometry.json']:shutil.copy2(D/fn,O/'Sources'/fn)
for row in json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['objects']:shutil.copy2(D/row['file'],O/'Sources'/row['file'])
for fn in ['v26_4_house.py','v26_4_surface.py','v26_4_prepare.py','v26_4_orthogonal.py','v26_4_build.py','v26_4_readback.py','v26_4_geometry_qa.py','v26_4_physics_qa.py','v26_4_protection_qa.py','v26_4_overlap_after.py','v26_4_overlap_gate.py','v26_4_render.py','v26_4_views.py','v26_4_draw_plan.py','v26_4_package.py']:shutil.copy2(W/fn,O/'Sources'/fn)
(O/'Sources/来源与运行环境.txt').write_text('生产工作区：'+str(W.parent)+'\n脚本、几何中间件与证据留档供本机复核。完整生产依赖位于该工作区的 work/np1、work/geomlibs、work/libs 和前序版本输入文件中。\n主 Blender 文件已内嵌原有 230 张贴图，查看和编辑模型无需这些生产脚本。\n',encoding='utf8')
readme='''Rebuild_V26.4 — Blender 修正版

模型：Blender\\Architecture_Complete_V26_4.blend
漫游：启动漫游.cmd
普通墙段厚度上限 240 mm；转角及原梁柱节点单独处理。

本轮修正：
1. 一楼楼梯口卫生间与右侧卫生间保留两区、两个独立入口和 100 mm 中间隔墙；整理过厚墙面、门套和门头窄缝。
2. 二、三楼卫生间前墙连续收平，清除旧门洞封补留下的矩形凹凸轮廓，保留侧向入口及房间后窄段。
3. 三楼参考实景的白色平天花，保留梁的下挂轮廓并封合墙顶；平顶标高沿用原模型，未作为实测尺寸。
4. 楼梯与平台、滑动门固定框和上亮、外飘窗墙边及雨棚交接表面已整理。卧室门套内收到墙面以内 1 mm，保留原门洞尺寸。保留门扇动画、原踏步标高和木扶手。
5. 次照壁原构件、原位置及原照片映射保留；原入口坡和外景扫描保留。

模型重新打开后复核了墙厚、墙头和门头连续性、梁柱保留、门扇扫掠及实际漫游碰撞。具体点位和限制见 Reports 中的 JSON 检查记录。
一楼空间关系图：Reports\\V26_4_F1_Room_Relationships.png
实景依据：References
本目录只提供 Blender 模型，唯一命令入口是“启动漫游.cmd”。
'''
(O/'使用说明.txt').write_text(readme,encoding='utf8')
labels={'03_F1_Right_Room':'一楼右侧房间与卫生间门头','04_F1_Stair_Wall':'一楼楼梯墙面与平台交接','06_F3_Stair_Ceiling':'三楼楼梯间白色平顶','08_F3_Right_Ceiling':'三楼右侧房间天花及卫生间前墙','09_F3_Right_High_Window':'三楼高窗墙顶收口','11_F1_Sliding_Glass':'一楼滑动门及上亮玻璃','12_F2_Sliding_Glass':'二楼滑动门及上亮玻璃','13_Terrace_Frame':'露台栏板与雨棚边界','15_F1_Bay_Frame_Return':'外飘窗原窗框与墙边配合'}
figures=''.join('<figure><figcaption>'+html.escape(next((v for k,v in labels.items()if k in f),f))+'</figcaption><img loading="lazy" src="'+html.escape(f)+'"></figure>'for f in review)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V26.4 实际模型复核</title><style>body{font:17px/1.7 "Microsoft Yahei",sans-serif;color:#253e4e;max-width:1150px;margin:38px auto;padding:0 20px}img{max-width:100%;height:auto}figure{margin:28px 0}figcaption{font-weight:bold}code{word-break:break-all}</style><h1>V26.4 模型复核</h1><p>一楼空间关系、普通墙段 240 mm 厚度上限、三楼实景白色平顶和梁墙收口。</p><p>下图均来自重新打开的同一个保存文件。材质预览添加了 75 W 临时补光，补光未写入模型。</p><p>模型 SHA256：<code>'''+h+'''</code></p><figure><figcaption>一楼实际剖切空间关系</figcaption><img src="V26_4_F1_Room_Relationships.png"></figure>'''+figures+'<p>墙厚检查针对普通墙段，转角与梁柱节点单列；平顶绝对标高沿用原模型。详细样本在本目录的检查记录中。</p></html>'
(R/'V26_4_模型复核.html').write_text(page,encoding='utf8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='Manifest_SHA256.json':manifest.append({'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'source_model':'E:/jz/JIA/Rebuild_V26_3/Blender/Architecture_Complete_V26_3.blend','checks':validation,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGED',P,h,'FILES',len(manifest),'CHECKS',sum(q['checks']for q in validation),flush=True)
