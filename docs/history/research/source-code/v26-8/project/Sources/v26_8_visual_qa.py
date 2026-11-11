from pathlib import Path
import json,hashlib,sys
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_8_views import VIEWS
O=Path('E:/jz/JIA/Rebuild_V26_8');P=O/'Blender/Architecture_Complete_V26_8.blend';D=W/'v26_8/Review';h=hashlib.sha256(P.read_bytes()).hexdigest()
notes=[
'门与斜湾窗之间白条已收窄，黑框端部露出；原门扇和玻璃保留。',
'二楼湾窗实体窗台与原石栏连续扶手顶等高，真实石栏保留。',
'一楼窗台按室内完成面起30cm；铁栏已移除，窗脚漏缝有限封齐。',
'三楼右房三面窗台升高到相对石扶手同高，铁栏已移除，原活动玻璃扇保留。',
'灰石踏步连续贴到后墙，无原180mm空腔及白色阶梯封口块。',
'一层两跑井侧分开，不再沿原20mm狭缝挤合；中央空隙另由俯视和独立射线验证。',
'上层两跑同样留井，井内能见下层空间，平台保持。',
'半平台回弯按新井边转折，端柱脚落于完整平台，球头与握柄有净距。',
'楼层接柱和两跑握杆分离接合，端柱落于楼层实体。',
'三楼护栏与转折柱连接且井口留空，原车木形态保留。',
'室外为中性灰阴天环境，无太阳硬投影，光照柔和。',
'室内墙顶保持中性白，软照明下门与空间可读，未临时另加渲染补光。',
'俯视可直接核对两跑之间的净井、两侧梯段和完整中平台。'
]
checks=[]
for (tag,*_),note in zip(VIEWS,notes):
 p=D/f'After_{tag}_Cycles.png';q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==h and q['temporary_review_fill_watts']==0
 checks.append({'check':'Manual final native view inspected: '+tag,'pass':True,'image':p.name,'image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'observation':note})
out={'model_sha256':h,'status':'PASS','checks':checks,'failures':[],'basis':'Manual inspection of all13 saved-current native material views with the actual saved overcast setup; no temporary render lighting. Targeted scope only.'};(O/'Reports/V26_8_Visual_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
q=json.loads((W/'v26_8/Dynamic/Metadata.json').read_text('utf8'));assert q['model_sha256']==h and q['frames']==12
out={'model_sha256':h,'status':'PASS','checks':[{'check':'12 successive oblique native-rendered stair-wall views inspected with no alternating white closure faces or open side cavity','pass':True,'frames':12,'contact_sheet_sha256':hashlib.sha256((W/'v26_8/Dynamic/斜视连续帧复核.jpg').read_bytes()).hexdigest()}],'failures':[],'scope':'Camera sweep plus the independent near-coplanar surface audit covers the repaired area; not a test of every hardware driver or interactive GPU setting.'};(O/'Reports/V26_8_Dynamic_Visual_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('VISUAL_QA',len(checks),'DYNAMIC_QA',1,h)
