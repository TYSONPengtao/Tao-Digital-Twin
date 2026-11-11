from v26_2_common import *
import hashlib,shutil,html,re,xml.etree.ElementTree as ET
D=W/'v26_3';O=Path('E:/jz/JIA/Rebuild_V26_3');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_3.blend';V=D/'Review'
def sha(p):
 with Path(p).open('rb')as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
h=sha(P);build=json.loads((R/'V26_3_Build.json').read_text('utf8'));assert h==build['sha256']
qa=[]
for name in ['V26_3_Native_Readback_QA.json','V26_3_Saved_Geometry_QA.json','V26_3_Interior_Physics_QA.json']:
 q=json.loads((R/name).read_text('utf8'));assert q['model_sha256']==h,(name,'stale model');assert q['status'].startswith('PASS'),(name,q.get('failures'));qa.append(q)
checks=sum(len(q['checks'])for q in qa)
for p in V.iterdir():
 if p.suffix not in ['.png','.json']:continue
 if not p.name.startswith(('Before_','After_','Original_')):continue
 if p.name.startswith('After_'):
  state=json.loads(p.with_suffix('.json').read_text('utf8'))if p.suffix=='.png'else json.loads(p.read_text('utf8'));assert state['model_sha256']==h,(p.name,'stale preview')
 shutil.copy2(p,R/p.name)
# The plan is a horizontal section of the reopened native mesh, not a sketch.
FD=D/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};a=np.load(FD/J['V26_3_House_Connected_Walls_And_Stairs']['file']);house=solid(a['v'],a['f'],'saved native house');contours=house.slice(.8).to_polygons();paths=[]
def xy(q):return(75+(q[0]-8.6)*205,840-(q[1]-6.4)*205)
for poly in contours:
 pp=[xy(q)for q in poly];paths.append('M'+'L'.join(f'{x:.3f},{y:.3f}'for x,y in pp)+'Z')
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="900" viewBox="0 0 1120 900"><defs><clipPath id="plan"><rect x="65" y="110" width="980" height="650"/></clipPath></defs><rect width="1120" height="900" fill="#f6f7f9"/><style>text{font-family:Microsoft YaHei,Arial;fill:#1d2939}.label{font-size:20px}.note{font-size:17px}</style><text x="55" y="52" font-size="28">一楼右侧隔墙与卫生间 · 模型实剖</text><text x="55" y="84" class="note">剖切标高 Z = 0.80 m；门扇处于保存的开启状态</text><g clip-path="url(#plan)">',f'<path d="{" ".join(paths)}" fill="#bfc5cd" stroke="#414b57" stroke-width="1.3" fill-rule="nonzero"/>']
for name in ['DOOR_BATH_F1_R__FRAME_Geometry','DOOR_BATH_F1_R__LEAF_Geometry','DOOR_KITCHEN_F1__FRAME_Geometry','DOOR_KITCHEN_F1__LEAF_Geometry']:
 r=J[name];a=np.load(FD/r['file']);m=solid(a['v'],a['f'],name)
 for poly in m.slice(.8).to_polygons():
  pp=[xy(q)for q in poly];path='M'+'L'.join(f'{x:.3f},{y:.3f}'for x,y in pp)+'Z';svg.append(f'<path d="{path}" fill="#955140" stroke="#6d352c" stroke-width="1"/>')
svg.append('</g>')
def label(x,y,text,size=20):
 p=xy((x,y));svg.append(f'<text x="{p[0]:.2f}" y="{p[1]:.2f}" font-size="{size}" text-anchor="middle">{html.escape(text)}</text>')
label(9.9,8.2,'楼梯间对面卫生间',18);label(11.8,8.7,'右侧卫生间',21);label(11.5,6.72,'一楼右侧房间',23);label(10.,7.08,'补回隔墙',18);label(11.6,9.35,'内隔墙保留 100 mm',17)
svg.extend(['<text x="55" y="811" class="label">红棕色为原门框与门扇；灰色为实际保存的墙体截面。</text>','<text x="55" y="847" class="note">两个卫生间门框深度为 220 mm；其余门扇动画与开启方向保留。</text>','</svg>']);(R/'F1_WC_Native_Section.svg').write_text(''.join(svg),encoding='utf8')
from PIL import Image,ImageDraw,ImageFont
root=ET.fromstring(''.join(svg));ns={'s':'http://www.w3.org/2000/svg'};scale=2;im=Image.new('RGB',(1120*scale,900*scale),'#f6f7f9');geom=im.copy();draw=ImageDraw.Draw(geom)
for path in root.findall('.//s:path',ns):
 rings=[]
 for part in path.attrib['d'].split('M')[1:]:
  points=np.array([float(q)for q in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',part)]).reshape(-1,2);area=np.sum(points[:,0]*np.roll(points[:,1],-1)-np.roll(points[:,0],-1)*points[:,1])/2;rings.append((area,points))
 for area,points in sorted(rings,key=lambda q:-abs(q[0])):
  coords=[tuple(p*scale)for p in points];draw.polygon(coords,fill=path.attrib['fill']if area<0 else'#f6f7f9');draw.line(coords+[coords[0]],fill=path.attrib['stroke'],width=2)
im.paste(geom.crop((65*scale,110*scale,1045*scale,760*scale)),(65*scale,110*scale));draw=ImageDraw.Draw(im)
for elem in root.findall('.//s:text',ns):
 size=int(elem.attrib.get('font-size',17 if elem.attrib.get('class')=='note'else 20));font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size*scale);anchor='ms'if elem.attrib.get('text-anchor')=='middle'else'ls';draw.text((float(elem.attrib['x'])*scale,float(elem.attrib['y'])*scale),elem.text,font=font,fill='#1d2939',anchor=anchor)
im.resize((1120,900),Image.Resampling.LANCZOS).save(R/'F1_WC_Native_Section.png')
proof={'model':str(P),'model_sha256':h,'status':'PASS','native_readback_checks':len(qa[0]['checks']),'saved_geometry_checks':len(qa[1]['checks']),'roam_checks':len(qa[2]['checks']),'total_checks':checks,'reports':['V26_3_Native_Readback_QA.json','V26_3_Saved_Geometry_QA.json','V26_3_Interior_Physics_QA.json'],'original_v26_2_byte_identical':sha(build['source'])==build['source_sha256'],'blender_only':not list(O.rglob('*.3dm')),'proof_view_modes':['Workbench material colors with original geometry','Cycles material preview; indoor temporary review fill 75 W, not saved to model']}
(R/'V26_3_Delivery_QA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
cards=[]
pairs=[('01_F1_Right_WC_Separation','一楼右侧房间与卫生间','补回与楼梯间对面卫生间之间的隔墙。内部隔墙为 100 mm，门框深度为 220 mm。隔墙后端接到窗侧墙；后窗右端按隔墙位置收回 110 mm，左端与高程保留。此数值为模型调整量。'),('04_F1_Transom','一楼滑动门上亮玻璃','移除挡住玻璃的实体墙段，玻璃上框接到原结构梁底。'),('07_F2_Transom','二楼滑动门上亮玻璃','恢复原玻璃材质与红色边框，上方保留原结构梁。'),('09_F1_High_Window','一楼高窗墙头','墙头接到楼板底，原梁的下挂轮廓保留。'),('02_F3_High_Window_Head','三楼高窗与斜屋顶','补足墙顶缺口，按现有斜屋顶底面封合；内侧顶面为中性白色。'),('08_Secondary_Screenwall','次照壁恢复原版','撤回加高、改平等误改，恢复 V24.34 的原构件、原阶梯装饰线、原坐标及墙身材质属性。')]
for tag,title,note in pairs:
 before='Before_'+tag+'_Solid.png';after='After_'+tag+'_Solid.png';assert(R/before).exists()and(R/after).exists();cards.append(f'<section><h2>{title}</h2><p>{note}</p><div class="pair"><figure><figcaption>V26.2</figcaption><img loading="lazy" src="{before}"/></figure><figure><figcaption>V26.3</figcaption><img loading="lazy" src="{after}"/></figure></div></section>')
materials=''.join(f'<figure><figcaption>{title}</figcaption><img loading="lazy" src="{name}"/></figure>'for name,title in [('After_02_F3_High_Window_Head_Cycles.png','三楼白色顶面与完整高窗墙头'),('After_08_Secondary_Screenwall_Cycles.png','恢复的次照壁原形制与贴图'),('After_11_F1_Door_Threshold_Cycles.png','一楼门口平整衔接'),('After_12_F1_WC_Rear_Jamb_Cycles.png','卫生间薄隔墙与后窗右端收口')])
page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rebuild V26.3 修正对照</title><style>body{{margin:0;background:#eef1f5;color:#202b39;font:16px/1.7 "Microsoft YaHei",Arial}}main{{max-width:1180px;margin:auto;padding:36px 24px}}h1{{font-size:32px;margin:0}}h2{{font-size:23px;margin:0 0 10px}}p{{margin:8px 0 20px}}section{{background:white;border-radius:14px;padding:24px;margin:24px 0;box-shadow:0 5px 18px #2331440c}}.pill{{display:inline-block;padding:4px 12px;border-radius:20px;background:#d8eee3;color:#1e6042}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}figure{{margin:0}}img{{width:100%;height:auto;display:block;background:#e5e7eb}}figcaption{{padding:7px 0;font-size:14px;color:#546172}}.muted{{font-size:14px;color:#607082}}code{{overflow-wrap:anywhere;font-size:12px}}@media(max-width:650px){{.pair{{grid-template-columns:1fr}}main{{padding:20px 12px}}}}</style><main><h1>Rebuild V26.3</h1><p>隔墙 · 上亮玻璃 · 高窗与墙顶收口 · 次照壁原版恢复</p><span class="pill">仅 Blender · 已重新打开检查</span><section><h2>交付文件</h2><p>模型：<b>Blender/Architecture_Complete_V26_3.blend</b><br>漫游：<b>启动漫游.cmd</b><br>V26.2 原文件保留。</p><p>检查覆盖原有 56 个梁柱核心、80 处楼梯踏面、12 扇室内门的 168 个动画姿态、门上亮与墙顶的定点检查，以及上下楼、门洞、实景入口坡和外景的漫游路线。共 {checks} 项检查通过。</p><p class="muted">检查针对保存文件中的几何、材质数据与所列路线。原楼梯扶手、实景入口坡及外景模型保留。该复核不代替现场实测或结构承载验算。</p></section><section><h2>一楼隔墙与卫生间</h2><img src="F1_WC_Native_Section.png"/></section>{''.join(cards)}<section><h2>材质与门口复查</h2><div class="pair">{materials}</div><p class="muted">材质图由实际模型生成。室内图使用临时 75 W 补光，补光未写入模型；上方成对图使用同一套实体材质色设置，便于辨认接缝和轮廓。</p></section><section><h2>验证记录</h2><p>原版次照壁 11 个构件的几何、位置、材质和 UV 已逐一比对；另外恢复了原有阶梯装饰线在次照壁范围内的表面及专用贴图高度属性。地面和围墙的全部顶点、三角面保留，其他区域的装饰面保持原有数据。</p><p><a href="V26_3_Delivery_QA.json">交付检查</a> · <a href="V26_3_Native_Readback_QA.json">保存后重新打开核查</a> · <a href="V26_3_Saved_Geometry_QA.json">几何核查</a> · <a href="V26_3_Interior_Physics_QA.json">漫游复测</a></p><p class="muted">模型 SHA-256<br><code>{h}</code></p></section></main></html>'''
(R/'V26_3_修正对比.html').write_text(page,encoding='utf8')
(O/'使用说明.txt').write_text('Rebuild V26.3，仅 Blender。\n用 Blender 直接打开 Blender/Architecture_Complete_V26_3.blend 编辑模型；双击“启动漫游.cmd”进入人物漫游。\n方向键/WASD移动，空格跳跃，Shift快走，鼠标右键转向，V切换视角，M切换材质显示，Esc退出。\n直接打开 Reports/V26_3_修正对比.html 查看本次修改及验证范围。\n次照壁按V24.34恢复，保留原位置与形制。\n原V26.2文件保留。\n',encoding='utf8')
sd=O/'Sources';sd.mkdir(exist_ok=True);pd=sd/'Prepared_Geometry';pd.mkdir(exist_ok=True)
for file in W.glob('v26_3_*.py'):shutil.copy2(file,sd/file.name)
for name in ['Prepared_House.json','Prepared_Fixtures.json','Prepared_Secondary_Deco.json','Original_Secondary.json','Original_Secondary_Surfaces.json','Exact_House_Parts.json','Secondary_Restored_Point_Field.npz']:
 shutil.copy2(D/name,sd/name)
for name in ['Prepared_House.json','Prepared_Fixtures.json','Prepared_Secondary_Deco.json','Original_Secondary.json','Original_Secondary_Surfaces.json']:
 data=json.loads((D/name).read_text('utf8'))
 for r in data.get('objects',[]):
  if r.get('file'):shutil.copy2(D/r['file'],pd/r['file'])
files=[]
for p in O.rglob('*'):
 if p.is_file()and p.name!='Manifest_SHA256.json':files.append({'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'Manifest_SHA256.json').write_text(json.dumps({'model_sha256':h,'files':files},ensure_ascii=False,indent=2),encoding='utf8');print('V26_3_DELIVERABLE_READY',checks,h,len(files),flush=True)