# -*- coding: utf-8 -*-
"""照壁三版融合v4。不是三个文件叠加：
从v3中追溯v1/v2/v3对象，淘汰旧缺陷层，重建无双层覆盖的中段NURBS屋面，
把端部横向误向瓦片替换为与原筒瓦方向一致的两端瓦作。
可编辑独立构件和清晰图层。 2026-10-11.
注意：尺寸均源于照片推拟，非现场测绘。
"""
import rhino3dm as R
import os, math, json, collections, hashlib
P=R.Point3d
ROOT=r'E:\CODEXdata\before\照壁'
inputs=[
 os.path.join(ROOT,'照壁_照片复原_可编辑模型.3dm'),
 os.path.join(ROOT,'照壁_侧面补全_v2.3dm'),
 os.path.join(ROOT,'照壁_实景侧面修正版_v3.3dm')]
OUT=os.path.join(ROOT,'照壁_三版融合_统一模型_v4.3dm')
QA=os.path.join(ROOT,'照壁_三版融合_v4_校验.json')
DOC=os.path.join(ROOT,'照壁_三版融合_v4_使用说明.txt')
src=[R.File3dm.Read(p) for p in inputs]
if any(s is None for s in src):raise IOError('Missing one or more source versions')
v1,v2,v3=src
ids1={str(o.Attributes.Id) for o in v1.Objects}
ids2={str(o.Attributes.Id) for o in v2.Objects}
ids3={str(o.Attributes.Id) for o in v3.Objects}
if not(ids1<=ids2 and ids2<=ids3):
 raise AssertionError("Models are not progressive versions: refusing to overlay sources blindly")
BASE="A_石台及主体墙身"
PANELS="B_墙头灰塑装饰"
ROOF="C_中段_双坡NURBS屋面"
ENDS="D_端部_延展起翘瓦面"
TILES="E_筒瓦板瓦_独立构件"
CAPS="F_莲花瓦当_独立构件"
MAINRIDGE="G_通长正脊与檐口压瓦"
OPENWORK="H_菱格透雕脊饰"
SIDEWALL="I_侧墙白灰与石块"
SIDEPANELS="J_侧面抱框与灰塑"
FASCIA="K_侧面封檐板与压边"
HIPS="L_侧向戗脊与双端飞檐"
HIGH="M_端部高立脊吻"
SHORT="N_端部短立脊饰"
CORNICE="O_檐下叠涩与出檐承托"
REFER="Z_隐藏_可编辑测绘控制线"
names=[
("01_青石台基",BASE,(126,125,121)),
("02_主体砖墙",BASE,(136,133,130)),
("03_正面白灰",BASE,(224,217,207)),
("04_背面青砖",BASE,(108,116,121)),
("05_灰塑花带底层",PANELS,(211,207,196)),
("06_长短交替八角灰塑",PANELS,(159,157,150)),
("07_侧墙抹灰",SIDEWALL,(214,210,201)),
("08_侧石基灰缝",SIDEWALL,(132,130,124)),
("09_侧面装饰框",SIDEPANELS,(167,164,157)),
("10_整合双坡屋面_NURBS",ROOF,(98,105,109)),
("11_屋面端部过渡网格",ENDS,(99,108,111)),
("12_青灰筒瓦与板瓦",TILES,(119,125,130)),
("13_莲花瓦当",CAPS,(152,154,153)),
("14_通长正脊与屋檐盖瓦",MAINRIDGE,(85,92,96)),
("15_中轴透雕菱格与四瓣花",OPENWORK,(104,111,115)),
("16_侧面封檐与滴水压边",FASCIA,(99,105,108)),
("17_曲线戗脊及檐角",HIPS,(85,94,99)),
("18_高立脊吻及立线",HIGH,(76,85,89)),
("19_旁侧小脊吻",SHORT,(87,91,96)),
("20_檐下连续叠涩与承托",CORNICE,(130,132,128)),
("21_侧面角部灰塑抱框",SIDEPANELS,(183,180,167)),
("22_控制线_隐藏",REFER,(190,145,70))]
nf=R.File3dm()
nf.Settings.ModelUnitSystem=R.UnitSystem.Millimeters
nf.Settings.ModelAbsoluteTolerance=1.0
layer_ids={}
provenance=collections.Counter()
totals=collections.Counter()
for label,category,color in names:
 layer=R.Layer()
 layer.Name=label;layer.Color=(*color,255)
 if label.startswith('22_'):layer.Visible=False
 layer_ids[label]=nf.Layers.Add(layer)
def attrs(layer,label,origin,previous_id=None):
 a=R.ObjectAttributes()
 a.LayerIndex=layer_ids[layer];a.Name=label
 a.SetUserString("建模组成来源",origin)
 if previous_id:a.SetUserString("原对象GUID",previous_id)
 return a
def add(g,layer,label,origin,id=None):
 a=attrs(layer,label,origin,id)
 if isinstance(g,R.Mesh):nf.Objects.AddMesh(g,a)
 elif isinstance(g,R.Brep):nf.Objects.AddBrep(g,a)
 elif isinstance(g,R.NurbsSurface):nf.Objects.AddSurface(g,a)
 elif isinstance(g,R.Curve):nf.Objects.AddCurve(g,a)
 elif isinstance(g,R.Extrusion):nf.Objects.AddExtrusion(g,a)
 else:raise TypeError(type(g))
 provenance[origin]+=1;totals[layer]+=1
def vname(o):return o.Attributes.Name or "未命名构件"
def bbx(o):
 b=o.Geometry.GetBoundingBox()
 return ((b.Min.X+b.Max.X)/2.0,(b.Min.Y+b.Max.Y)/2.0,(b.Min.Z+b.Max.Z)/2.0)
# Selection by provenance, with fixed layer replacement policies:
policy={
0:'01_青石台基',1:'02_主体砖墙',2:'03_正面白灰',
3:'04_背面青砖',4:'05_灰塑花带底层',5:'06_长短交替八角灰塑',
8:'12_青灰筒瓦与板瓦',9:'13_莲花瓦当',
11:'15_中轴透雕菱格与四瓣花',
15:'07_侧墙抹灰',16:'08_侧石基灰缝',17:'09_侧面装饰框',
25:'11_屋面端部过渡网格',26:'16_侧面封檐与滴水压边',
28:'17_曲线戗脊及檐角',
30:'18_高立脊吻及立线',31:'19_旁侧小脊吻',
32:'20_檐下连续叠涩与承托',33:'21_侧面角部灰塑抱框',
34:'20_檐下连续叠涩与承托',
35:'22_控制线_隐藏'}
allobjects=list(v3.Objects)
rejection=collections.Counter()
for o in allobjects:
 layer=o.Attributes.LayerIndex
 if layer not in policy:
  if layer==7:rejection["旧版屋面延伸到端部与v3相叠"]=rejection["旧版屋面延伸到端部与v3相叠"]+1
  elif layer==10:rejection["旧版重复正脊与檐口线"]=rejection["旧版重复正脊与檐口线"]+1
  elif layer==27:rejection["v3端部错误的横向续瓦"]=rejection["v3端部错误的横向续瓦"]+1
  elif layer==29:rejection["v3局部正脊重复线"]=rejection["v3局部正脊重复线"]+1
  else:rejection["旧侧檐_浮空脊吻_隐藏过时构件"]=rejection["旧侧檐_浮空脊吻_隐藏过时构件"]+1
  continue
 # to avoid double geometry at eaves, replace end tile rows by unified orientation
 if layer in (8,9) and abs(bbx(o)[0])>=2100:
  rejection["旧版端部瓦片_位置与新曲面不吻合"]+=1
  continue
 origin=("v1_主体" if str(o.Attributes.Id) in ids1 else
         ("v2_侧立面" if str(o.Attributes.Id) in ids2 else "v3_结构补全"))
 add(o.Geometry,policy[layer],vname(o),origin,str(o.Attributes.Id))
# geometry helpers
def plus(a,b):return tuple(a[i]+b[i] for i in range(3))
def sub(a,b):return tuple(a[i]-b[i] for i in range(3))
def mul(a,s):return tuple(v*s for v in a)
def dot(a,b):return sum(u*v for u,v in zip(a,b))
def unit(a):
 d=math.sqrt(dot(a,a));return tuple(v/d for v in a) if d else (0,0,1)
def cross(a,b):
 return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def lin(a,b,n):return [a+(b-a)*i/(n-1) for i in range(n)]
def tube(path,radius,layer,name,faces=12,origin="v4_屋瓦无缝融合"):
 g=R.Mesh()
 for i,pt in enumerate(path):
  direct=unit(sub(path[min(i+1,len(path)-1)],path[max(0,i-1)]))
  axis=(1,0,0) if abs(direct[2])>.85 else (0,0,1)
  u=unit(cross(direct,axis));v=unit(cross(direct,u))
  for j in range(faces):
   theta=math.tau*j/faces
   p=plus(pt,plus(mul(u,radius*math.cos(theta)),mul(v,radius*math.sin(theta))))
   g.Vertices.Add(*p)
 for i in range(len(path)-1):
  for j in range(faces):
   j2=(j+1)%faces
   g.Faces.AddFace(i*faces+j,i*faces+j2,(i+1)*faces+j2,(i+1)*faces+j)
 g.Vertices.Add(*path[0]);g.Vertices.Add(*path[-1])
 aa=len(path)*faces;bb=aa+1
 for j in range(faces):
  j2=(j+1)%faces
  g.Faces.AddFace(aa,j2,j)
  g.Faces.AddFace(bb,(len(path)-1)*faces+j,(len(path)-1)*faces+j2)
 g.Normals.ComputeNormals()
 if not g.IsValid:raise ValueError("invalid tube "+name)
 add(g,layer,name,origin)
def eave(x):
 a=min(1.0,abs(x)/2420.)
 return 2690.+105*a*a+420*a**6
def roof(x,y):
 return eave(x)+305*max(0.,1.-abs(y)/505.)
def ext(x,y):
 xx=max(0.,min(1.,(abs(x)-2140.)/330.))
 yy=max(0.,min(1.,(abs(y)-295.)/238.))
 return 185*(xx*xx*(3-2*xx))*(yy*yy*(3-2*yy))
def rz(x,y):return roof(x,y)+ext(x,y)
# A seamless two-way NURBS roof in the midspan. At x2100 znew=zold.
for sg in (-1,1):
 for delta in (0,-56):
  a=R.Curve.CreateControlPointCurve([P(x,0,roof(x,0)+delta) for x in lin(-2100,2100,89)],3)
  b=R.Curve.CreateControlPointCurve([P(x,sg*520,roof(x,sg*520)+delta) for x in lin(-2100,2100,89)],3)
  sf=R.NurbsSurface.CreateRuledSurface(a,b)
  if sf is None or not sf.IsValid:raise ValueError('failed create central NURBS')
  add(sf,'10_整合双坡屋面_NURBS','统一中段屋面_双坡_'+str(sg)+'_'+str(delta),'v4_中段NURBS续接')
# Near-end tiles each face has same orientation as original, across y (not across x).
# old inner area 39 positions -2280 ... +2280, truncate at ±2040.
for sx in (-1,1):
 for xx in (2160,2280,2400):
  x=sx*xx
  for sy in (-1,1):
   for row in range(4):
    a=sy*(10+row*127);b=sy*min(505,10+(row+1)*127+13)
    ys=lin(a,b,8)
    pts=[(x,y,rz(x,y)+23+5*math.sin(math.pi*j/7)) for j,y in enumerate(ys)]
    tube(pts,39,'12_青灰筒瓦与板瓦','端瓦与中央同向_筒瓦_'+str(x)+'_'+str(sy)+'_'+str(row),12)
   for row in range(3):
    a=sy*(15+row*140);b=sy*(15+(row+1)*140)
    tube([(x+sx*58,y,rz(x+sx*58,y)-8) for y in lin(a,b,7)],12,
         '12_青灰筒瓦与板瓦','端部板瓦搭接_'+str(x)+'_'+str(sy)+'_'+str(row),8)
   yy=sy*510;zz=rz(x,yy)+27
   tube([(x,yy,zz),(x,yy+sy*28,zz)],43,
        '13_莲花瓦当','端部花瓦当_'+str(x)+'_'+str(sy),16)
   for petal in range(8):
    theta=2*math.pi*petal/8
    px=x+21*math.cos(theta)
    pz=zz+21*math.sin(theta)
    tube([(px,yy+sy*26,pz),(px,yy+sy*30,pz)],8,
         '13_莲花瓦当','瓦当莲瓣_'+str(x)+'_'+str(sy)+'_'+str(petal),6)
# Connected long ridge and front-back eave upper/lower cornice.
tube([(x,0,rz(x,0)+34) for x in lin(-2470,2470,101)],38,
     '14_通长正脊与屋檐盖瓦','主脊底部连续_贯通两端',14)
tube([(x,0,rz(x,0)+160) for x in lin(-2140,2140,95)],26,
     '14_通长正脊与屋檐盖瓦','透雕脊饰上缘盖瓦',14)
for sy in (-1,1):
 for delta,rad in ((10,24),(-25,17)):
  tube([(x,sy*505,rz(x,sy*505)+delta) for x in lin(-2470,2470,105)],rad,
      '14_通长正脊与屋檐盖瓦','两端连贯檐口瓦_'+str(sy)+'_'+str(delta),12)
# Finish + QA
if not nf.Write(OUT,8):raise IOError('Failed to write unified 3dm')
opened=R.File3dm.Read(OUT)
if opened is None:raise IOError('Write success but cannot read 3dm')
items=list(opened.Objects)
bad=[i for i,o in enumerate(items) if not o.Geometry.IsValid]
if bad:raise RuntimeError('invalid geometry count='+str(len(bad)))
bounds=[o.Geometry.GetBoundingBox() for o in items]
cube=[min(b.Min.X for b in bounds),min(b.Min.Y for b in bounds),min(b.Min.Z for b in bounds),
      max(b.Max.X for b in bounds),max(b.Max.Y for b in bounds),max(b.Max.Z for b in bounds)]
n=collections.Counter(type(o.Geometry).__name__ for o in items)
new_ids=[str(o.Attributes.Id) for o in items]
if len(new_ids)!=len(set(new_ids)):raise ValueError('duplicate object guids')
summary={
 "model":"照壁_三版融合_统一模型_v4.3dm",
 "source_versions":[{"file":os.path.basename(p),"objects":len(list(s.Objects)),"bytes":os.path.getsize(p)} for p,s in zip(inputs,src)],
 "source_lineage_proved":"all v1 GUIDs in v2, all v2 GUIDs in v3",
 "fusion_process":"select latest valid construction per component, remove hidden previous geometry, replace central roof overlap with shortened NURBS midspan, unify curved end tile directions, unify continuous roof ridge lines",
 "deleted_obsolete_or_duplicates":dict(rejection),
 "new_count_by_origin":dict(provenance),
 "result_file":OUT,"result_bytes":os.path.getsize(OUT),"result_layers":len(list(opened.Layers)),
 "result_objects":len(items),"geometry_types":dict(n),"valid_objects":len(items)-len(bad),
 "invalid_objects":len(bad),
 "bounds_mm":[round(x,2) for x in cube],
 "measured_dimensions":False,
 "original_versions_unchanged":True,
 "note":"Photo-derived geometric reconstruction, not measured construction drawings"}
with open(QA,'w',encoding='utf-8') as fp:json.dump(summary,fp,ensure_ascii=False,indent=2)
doc="""照壁三版融合总模型 v4
===================
文件：照壁_三版融合_统一模型_v4.3dm
源文件：最初版、侧面补全v2、实景侧面修正版v3。

整合方式：三个文件是累积版本，不是三个不同建筑。
本次逐个追踪原对象GUID后，按用途保留不同版本的最佳组件：
一版的青石基础、墙体、砖纹和墙头灰塑；
二版的侧墙抹灰、石基侧缝与侧面八角装饰框；
三版的准确接续的侧檐、鱼尾高脊饰、小脊饰、承托构造。

消除冗余：
- 删除旧版已隐藏的V字形檐、悬空立脊、错误悬挑构件和旧参考线
- 中段NURBS屋面仅保留到接续坐标x约±2100，之后以新端部上翘曲面接续，
  不再把从x2100到2420的整张旧屋面重复盖在新屋面下
- 把三版端部误用横向铺法的瓦片改成沿原屋面坡向(y方向)顺排，
  并修正起翘区瓦片相对屋面的高度
- 正脊与两侧檐口压瓦通长连续，不再重复叠放局部正脊
- 瓦片、瓦当、石基、砖墙、装饰仍保持独立对象，Rhino可分层编辑

本文件共22层，分别命名；“22_控制线_隐藏”默认隐藏。
使用 Rhino 8 直接打开，在图层面板单独开关以方便编辑。
NURBS 屋面与分件 Mesh 瓦件均保留，需细部拉伸、造型时请分别选取。

几何尺寸：单位毫米。全部尺寸来自照片比例推定，
不代表现场实测；古建筑构造、尺寸与材料必须实测后才可供施工。

检验报告：照壁_三版融合_v4_校验.json
源码：Fusion_照壁_三个版本_v4.py
三个源 .3dm 一律未覆盖。
"""
with open(DOC,'w',encoding='utf-8') as fp:fp.write(doc)
print(json.dumps(summary,ensure_ascii=True,indent=2))
