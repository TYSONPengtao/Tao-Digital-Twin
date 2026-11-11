from pathlib import Path
W=Path(__file__).parent
s=(W/'v20_package.py').read_text(encoding='utf8')
s=s.replace('V20','V21').replace('v19_preserved_sha256','v20_preserved_sha256')
s=s.replace("independent_inward_door_leaves':len(DM['doors'])","independent_door_leaves':len(DM['doors']),'sliding_leaves':sum(r.get('operation')=='SLIDING' for r in DM['doors'])")
# Keep binary parity, counts, atlas checks and actual readback checks; this
# delivery has its own comparison rows, copy rules and prose below.
s=s.split("comparison('V21_AsBuilt_Comparison.png'")[0]
s=s.replace("for name in V['view_names']:assert", "for name in V['view_names']:assert")
s += '''
comparison('V21_House_Comparison.png',[
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 150915.jpg'),'批注：三层卧室门位置错误'),(O/'06_Report/V21_F3_Corrected_Door_Landing.png','V21：旧洞封实，门移至柱子另一侧')],
 [(Path('D:/Desktop/问题/download.jfif'),'实景：三层晾晒檐廊入口与墙面'),(O/'06_Report/V21_F3_Doorless_Terrace.png','V21：白色无门扇入口、矩形饰面砖')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 150622.jpg'),'实景扫描：灰白色楼房外墙'),(O/'06_Report/V21_House_Rear_Facade.png','V21：按原洞口范围修正背面与侧面外墙')]])
comparison('V21_Gate_Comparison.png',[
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-12 002727.jpg'),'实景：内大门比例、门柱与屋檐'),(O/'06_Report/V21_Inner_Gate_Reference_Front.png','V21：采用指定分层模型重整内大门')],
 [(Path('D:/Desktop/问题/屏幕截图 2026-10-13 151254.jpg'),'批注：内门与厨房间多余饰墙'),(O/'06_Report/V21_Inner_Gate_Kitchen_Flush_Junction.png','V21：去掉多余饰墙，接缝平齐')],
 [(O/'07_Reference/V20_AsBuilt/gate_pavilion/INSV_0657s_L0_Y+00_P+25.jpg','实景抽帧：连续封闭檐底'),(O/'06_Report/V21_Inner_Gate_Reference_Underside.png','V21：修复模型薄片，补连续檐底')]])
readme="""V21 实景继续校正（2026-10-13）

主模型：04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm。Rhino 8，米，原 ENU 坐标。
漫游资产：05_Export/Complete_Site_V21_LOCAL.glb。可编辑检视场景：Actual_Rhino_V21_Readback_LOCAL.blend。两者 LOCAL 米，变换见02_Data/Coordinate.json。V20 原文件保留。

本轮修改依据：原始 VID_20260507_152114_00_001.insv 的新抽帧、用户10月13日15时批注及指定内大门原生模型。新抽帧和来源记录位于07_Reference/V21_AsBuilt；各部位设计判断、参考时间、拟合尺寸及未测量项记录于06_Report及08_Editable_Source/V21_Scripts。

内大门：按指定“内大门_实景复原_分层可编辑_Rhino8.3dm”的分层构件重新安置，统一毫米到米。保存来源对象对应关系；薄片构件加厚，檐底封闭。清理厨房侧多余饰墙、花砖和旧门楼重叠构件，校核门柱与厨房山墙接面。尺寸为既有场地与实景拟合，不是实测施工尺寸。
三层楼房：三层卧室门移到柱子南侧、靠书房门处，原错误洞口填实；移除通往晾晒檐廊的虚构木门和木门套，按实景保留白色通行洞口、矩形灰白砖墙。背面及侧面外墙修正为灰白色，保留实际窗洞及室内墙面。已补的首层红框缺墙和实心一阶入口保留并检查。
檐廊：按视频修正储藏房回字形窗棂及旧木色；厨房灰褐石板与储藏房灰米色水泥廊面分别处理。保留照壁齐排石栏、檐廊端部正确开口、亭子回收位置与木板底50mm净空，并复核相关支撑与接缝。
门：进入楼房的前玻璃门恢复两侧平移推拉，门框及固定侧玻璃不动；其余有门扇的通行口保留向内开。取消实景没有门扇的檐廊洞口虚构门。独立节点、铰链/平移量、开启方向与父子关系见02_Data/Door_Manifest_V21.json，GLB默认开启且含平移/内开动画。

请先打开06_Report中的实景对照图和对应命名视图。所有预览由最终保存3DM的回读网格生成，保留模型几何可见；室内检视灯只用于看清构件，不代表现场灯具。3DM及缓存、GLB的数值复核报告同时交付。
UE：保留节点层级和独立活动门，长度米转厘米100倍。02_Data/UE_Walkthrough_Settings.json提供胶囊/碰撞建议；实际UE项目导入、碰撞烘焙与交互逻辑尚未测试，不能将本地网格检查等同于引擎运行通过。
"""
(O/'README_V21_请先阅读.txt').write_text(readme,encoding='utf-8-sig')
settings=json.loads((Path('E:/jz/JIA/Rebuild_V20')/'02_Data/UE_Walkthrough_Settings.json').read_text(encoding='utf8'))
settings.update(asset='05_Export/Complete_Site_V21_LOCAL.glb',default_door_pose='OPEN; main-house front glazing SLIDING, other moving leaves HINGED_INWARD',door_manifest='02_Data/Door_Manifest_V21.json')
(O/'02_Data/UE_Walkthrough_Settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2),encoding='utf8')
for a in ['house','gate','site']:
 td=O/'08_Editable_Source/V21_Scripts'/a;td.mkdir(parents=True,exist_ok=True)
 for p in (W/f'v21_{a}').iterdir():
  if p.is_file() and p.suffix in ['.py','.json','.npz','.md'] and 'Inventory' not in p.name:
   if p.suffix=='.json':
    data=json.loads(p.read_text(encoding='utf8'));state=data.get('status','') if isinstance(data,dict) else ''
    if state.startswith(('FAIL','MAJOR','NEEDS','DESIGN_WRITTEN')):continue
   shutil.copy2(p,td/p.name)
 for name in ['Design_Control.json','QA.json','Final_Native_QA.json','Preview_Review.json']:
  p=W/f'v21_{a}'/name
  if p.exists():shutil.copy2(p,O/'06_Report'/f'{a}_{name}')
for p in W.glob('v21_*.py'):
 if 'prepare_' in p.name:continue
 shutil.copy2(p,O/'08_Editable_Source/V21_Scripts'/p.name)
src=Path('E:/CODEXdata/before/内大门/内大门_实景复原_分层可编辑_Rhino8.3dm');dst=O/'07_Reference/V21_AsBuilt/Inner_Gate_Source';dst.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst/src.name)
active={Path(r['file']).as_posix() for r in I};files=[]
for p in sorted(O.rglob('*')):
 if not p.is_file() or p.name in ['File_Manifest_SHA256.json','Bundle_QA.json'] or p.suffix in ['.blend1','.bak','.3dmbak']:continue
 if p.relative_to(O).as_posix().startswith('02_Data/') and p.suffix=='.npz' and p.relative_to(O/'02_Data').as_posix() not in active:continue
 files.append(p)
manifest={'version':'V21','model':P.relative_to(O).as_posix(),'file_count':len(files),'files':[{'path':p.relative_to(O).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]}
mp=O/'File_Manifest_SHA256.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');files.append(mp)
out=W.parent/'outputs';zp=out/'Production_1QK_Rhino_V21_AsBuilt_Refinement.zip'
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
 for i,p in enumerate(files):
  z.write(p,'Rebuild_V21/'+p.relative_to(O).as_posix())
  if i%100==0:print('PACKED',i,len(files),flush=True)
with zipfile.ZipFile(zp) as z:assert z.testzip() is None
bundle={'status':'PASS_ZIP_CRC','zip':str(zp),'bytes':zp.stat().st_size,'sha256':sha(zp),'files':len(files)}
(O/'06_Report/Bundle_QA.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bundle),flush=True)
'''
s=s.replace('门内开方向按本次要求设置。','楼房入口为推拉，其余活动门内开。')
(W/'v21_package.py').write_text(s,encoding='utf8')
print('Prepared V21 package validator')
