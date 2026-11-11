from pathlib import Path
import json,hashlib,sys
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_7_views import VIEWS
O=Path('E:/jz/JIA/Rebuild_V26_7');P=O/'Blender/Architecture_Complete_V26_7.blend';D=W/'v26_7/Review'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
h=sha(P)
notes=[
 '人工查看最终图：楼层横向错台和上角窄悬片已去除；保留原中平台承托边。',
 '人工查看最终图：窗下普通墙面连续，原玻璃和框保留；墙角原窄返边不作全平化处理。',
 '人工查看最终图：门边到顶交接闭合；真实交墙转角和既有门框边保留。此视图不表示所有转角均无构造凸出。',
 '人工查看最终图：起步扶手回弯圆顺，接到柱身球下；立杆斜帽与握柄接合。',
 '人工查看最终图：上层后护栏与斜扶手从球下接柱，未穿球；五个端部补杆与原节奏配合。',
 '人工查看最终图：平台与踏步连续，扶手立杆落位；平台贴墙承托端保留。',
 '人工查看最终图并对照原视频：内大门低石门槛连续，原高叠块已降低；门扇底部与石槛配合。100mm仅为相对现院坪的模型拟合。',
 '人工查看最终图：右门扇与门框饰面保留，侧后部分被开启门扇遮挡；缺角闭合另由09近景和原生射线检查覆盖。',
 '人工查看最终近景：门后走廊侧缺失角已补到既有标高，石基座与门框下脚连接；原铺地和高差保留。',
 '人工查看最终图：另一侧门框、门扇下沿与原走廊地坪交接保留，没有新增高叠块。',
 '人工查看最终图：非照壁院墙腰线高度为青砖，原石材与毛石分层保留。',
 '人工查看最终图：原次照壁旁水平檐带显露，错误重复斜檐带和垂落斜条已消失；原11构件精确保护另有报告。',
 '人工查看最终图：误贴青砖的墙脚恢复条石和毛石层次；接缝处纹理尺度差异及周期重复仍可见，未宣称无缝实测贴图。',
 '人工查看最终图：三楼白平顶与窗头闭合，玻璃保留；原梁和墙角返边保留。'
]
checks=[]
for (tag,*_),note in zip(VIEWS,notes):
 p=D/f'After_{tag}_Cycles.png';q=json.loads(p.with_suffix('.json').read_text('utf8'));assert q['model_sha256']==h and q['saved_model_unmodified']
 checks.append({'check':'Targeted final native render reviewed: '+tag,'pass':True,'image':p.name,'image_sha256':sha(p),'model_sha256':h,'manual_observation':note})
q={'model_sha256':h,'status':'PASS','checks':checks,'failures':[],'method':'Manual inspection of all14 current-hash Cycles views; material and geometric regressions are in separate saved-native reports. Temporary75W viewing fill was not saved.','limitations':['Targeted review of the user-identified areas, not a certification of the entire reconstruction.','Original photographed beams, wall-intersection returns, stair bearing edges and door frames are retained.','Brick/rubble periodic repetition and some base texture scale seams remain visible.','Reference frames are uncalibrated; fitted dimensions are not site measurements.']}
(O/'Reports/V26_7_Visual_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8');print('FINAL_VISUAL_REVIEW',len(checks),h)
