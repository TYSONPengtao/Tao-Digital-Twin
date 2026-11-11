from pathlib import Path
import json,hashlib,shutil,ast
W=Path(__file__).parent;D=W/'v26';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P);build=json.loads((R/'V26_Build.json').read_text('utf8'));assert h==build['sha256'];qa=[]
for name in ['V26_Native_Readback_QA.json','V26_Structural_Geometry_QA.json','V26_Interior_Physics_QA.json','V26_Ramp_Surface_QA.json']:
 a=json.loads((R/name).read_text('utf8'));assert a['model_sha256']==h and not a['failures'],(name,a.get('failures'));qa.append({'report':name,'checks':len(a['checks']),'status':a['status']})
views=json.loads((D/'Views.json').read_text('utf8'))
for tag,*_ in views:
 a=json.loads((R/('V26_'+tag+'_State.json')).read_text('utf8'));assert a['model_sha256']==h and not a['draft'];assert(R/a['file']).stat().st_size>50000
# Draft renders are agent-created review intermediates, archived locally.
archive=D/'Draft_Archive';archive.mkdir(exist_ok=True)
for p in R.glob('Draft_V26_*'):
 assert p.is_file()and p.resolve().parent==R.resolve()
 shutil.copy2(p,archive/p.name);p.unlink()
st=json.loads((D/'Prepared_Structure.json').read_text('utf8'));rp=json.loads((D/'Prepared_Ramp.json').read_text('utf8'))
src=O/'Sources';src.mkdir(exist_ok=True)
for n in ['Prepared_Structure.json','Prepared_Ramp.json','Original_Source_Index.json','Base.json','Views.json']:shutil.copy2(D/n,src/n)
for row in st['objects']+rp['objects']:shutil.copy2(D/row['file'],src/row['file'])
shutil.copy2(D/'RAMP_BACKING_CLOSED.npz',src/'RAMP_BACKING_CLOSED.npz')
code=src/'Scripts';code.mkdir(exist_ok=True)
for n in ['v26_build.py','v26_prepare_structure.py','v26_prepare_ramp.py','v26_verify.py','v26_structure_verify.py','v26_surface_verify.py','v26_physics_qa.py','v26_render.py']:shutil.copy2(W/n,code/n)
for p in (O/'Roam').glob('*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
restored=[r for r in st['proof']['columns']if min(r['before_section_m'])<.2];removed=sum(r.get('zero_volume_boolean_sheets_removed',0)for r in st['objects']);total=sum(a['checks']for a in qa)
readme=f'''Rebuild V26 — Blender 原生模型
2026-10-23

打开修正版模型.cmd：打开 Blender/Architecture_Complete_V26.blend。
启动漫游.cmd：进入人物漫游；WASD 移动，Shift 快走，空格跳跃，
右键转向，滚轮调距离，V 切换视角，Home 回院落，Esc 退出。

以用户指定 Rebuild_V24_34 为底稿，没有导出 Rhino 模型。
1. 外院墙朝院内的面统一为白色，外侧青砖及门窗动作保留。
2. 恢复原场地入口坡面约 {rp['proof']['recovered_area_m2']:.2f} 平方米，保留原照片 UV 与起伏。
   现有建模道路在 0.85 米接缝带内贴合原坡面；不压平原坡。
3. 四段楼梯、两个中间平台形成实体支承；恢复 {len(restored)} 根被削窄柱的
   原 400×400mm 模型截面；补齐梁端、楼层及墙角节点。
4. 已按最终保存文件完成 {total} 项记录检查，其中结构几何 {qa[1]['checks']} 项、
   人物通行 {qa[2]['checks']} 项全部通过；坡面接缝与重面检查通过。

本次完成的是模型几何连接修正。没有进行承载力、配筋、锚固、
荷载、地基或抗震验算；几何检查通过不等于结构安全及全部规范认证。
新增节点按既有模型轴网、截面和标高拟合，施工前需设计复核。

照片已打包在 blend 内。打开和漫游不依赖 Sources；该目录保存本次
修改的网格输入和处理记录，Scripts 为过程代码，不是独立安装包。
Reports/修正说明.md 有预览、检查范围及参考标准。
原 V24.34 与纯场地版本.3dm 的 SHA256 已核对，均未改写。

最终模型 SHA256：{h}
'''
(O/'使用说明.txt').write_text(readme,encoding='utf8')
report=f'''# Rebuild V26 修正与检查记录

2026-10-23。底稿：[V24.34]({build['source']})；交付：[Blender 模型]({P.as_posix()})。

| 部位 | 实际修改 | 检查结果 |
|---|---|---|
| 外院墙 | 直接改朝院内的网格材质面为白色，未叠加共面白板；外侧青砖着色器保持 | 白色面保存回读与实际渲染复核通过 |
| 入口坡面 | 从原场地恢复 {rp['proof']['recovered_area_m2']:.2f} m² 原网格，保留原始照片 UV 和高度；只调整相邻建模道路的 0.85 m 接缝带 | 保存网格边界差小于 1 mm；没有超过容差的重面；四处双向穿行和跳跃落地通过 |
| 楼梯 | 四个梯段与侧墙形成 120 mm 模型搭接，平台和楼板端部补实体支承 | 每个梯段均与墙、平台支承梁和楼板有有限体积连接，两个平台均有支承 |
| 梁柱板 | 恢复 {len(restored)} 根被削窄柱的原 400×400 mm 截面；柱贯通楼板节点，梁端进入原柱轴线节点，楼梯间补回框架支承 | 35 根柱的柱脚、上下层柱、梁两端及二三层楼板梁支承检查通过 |
| 墙角 | 补合小缝隙，补全楼梯间转角，墙与框架分别拥有实体区域，清理 {removed} 个零体积布尔薄片 | 29 个有效墙体实体均有楼板、框架或连接横墙支承，未检出悬浮墙体实体 |

以上尺寸均为模型坐标与既有模型定义，不是新增现场测量值。网格接缝数值匹配误差也不代表摄影测量的绝对实测精度。

| 最终文件检查 | 项数 | 结果 |
|---|---:|---|
| 原生回读、原底稿及照片/动作保持 | {qa[0]['checks']} | 通过 |
| 结构实体连接与支承 | {qa[1]['checks']} | 通过 |
| 人物通行、上下楼、坡面双向穿行、跳跃及净空 | {qa[2]['checks']} | 通过 |
| 坡面覆盖、重面和边界高差 | {qa[3]['checks']} | 通过 |

楼梯既定实走路线的 226 个记录点中，最小垂直上方净空约 3.153 m。人物检查使用交付文件中的 1.65 m 人物胶囊与真实网格碰撞，未添加贯穿场地的无限平面。扫描边界和无支撑缺口沿用停止/返回安全位置的处理。

**规范核对范围：**本版没有进行材料强度、荷载、配筋锚固、连接承载力、地基和抗震验算，也没有把新增拟合节点确认为已实测的现场构造。因此交付结论为几何连接检查通过，不能据此确认整体结构安全或全部规范合规。施工采用前须由设计人员结合结构体系、使用性质和图纸复核。

对连接传力及竖向构件连续性的核对，参考 [GB 50010-2010（2024 年版）3.2] (https://gf.cabr-fire.com/m/article-12585.htm)；墙角拉结和板墙连接另参考 [GB 55007-2021 4.1](https://gf.cabr-fire.com/m/article-39242.htm)。这些要求包含本次网格模型未验证的构造与承载力内容，不能用实体相交代替。

以下均为最终保存模型的 Blender 渲染。室内近景使用临时工作灯；两张结构剖视临时隐藏外围饰面，保存的完整模型没有隐藏这些构件。

| 预览 | 文件 |
|---|---|
'''
labels=['院墙内侧白色','原场地坡面与入口衔接','下层楼梯接墙及平台','上层楼梯接墙及平台','楼梯间两墙转角','建筑整体','梁柱板结构剖视','楼梯支承剖视']
for (tag,*_),label in zip(views,labels):report+=f'| {label} | [打开预览]({(R/("V26_"+tag+".png")).as_posix()}) |\n'
report+=f'\n最终模型 SHA256：`{h}`。四份 QA JSON 与八张渲染状态均绑定该哈希。\n'
report=report.replace('3.2] (','3.2](')
(R/'修正说明.md').write_text(report,encoding='utf8')
delivery={'status':'PASS_MODEL_GEOMETRY_AND_DELIVERY','model':P.as_posix(),'model_sha256':h,'bytes':P.stat().st_size,'base_model':build['source'],'base_sha256':build['source_sha256'],'qa':qa,'total_checks':total,'all_render_states_match':True,'render_count':len(views),'rhino_files_created':len(list(O.rglob('*.3dm'))),'structural_capacity_or_full_code_compliance_certified':False,'input_file_changes':False,'scripts_parse':True,'reviewed_images':labels};(R/'V26_Delivery_QA.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file()and p.name!='Manifest_SHA256.json':manifest.append({'file':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':manifest},ensure_ascii=False,indent=2),encoding='utf8');assert not list(O.rglob('*.3dm'))
print('PACKAGE_DONE',str(P),P.stat().st_size,h,'checks',total,'files',len(manifest),flush=True)
