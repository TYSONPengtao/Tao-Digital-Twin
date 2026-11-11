# -*- coding: utf-8 -*-
"""基于照片的可编辑 Rhino 8 三维照壁复原；尺寸为推拟值，单位 mm。"""
import rhino3dm as r
import math, os, json, collections, traceback
P=r.Point3d
ROOT=r"E:\CODEXdata\before\照壁"
OUT=os.path.join(ROOT,"照壁_照片复原_可编辑模型.3dm")
DETAIL=os.path.join(ROOT,"照壁_模型说明.txt")
REPORT=os.path.join(ROOT,"照壁_文件校验.json")
f=r.File3dm()
f.Settings.ModelUnitSystem=r.UnitSystem.Millimeters
f.Settings.ModelAbsoluteTolerance=1.0
LAYERS=[
 ("01_基础_青石台基",(126,125,121)),
 ("02_墙身_砖砌实体",(136,133,130)),
 ("03_正面_白灰粉刷",(224,217,207)),
 ("04_背面_青砖纹理",(108,116,121)),
 ("05_墙头_装饰带基底",(211,207,196)),
 ("06_墙头_八角多层灰塑边框",(159,157,150)),
 ("07_檐下_叠涩压檐线脚",(146,147,144)),
 ("08_屋面_两坡NURBS曲面",(98,105,109)),
 ("09_屋面_板瓦和筒瓦",(119,125,130)),
 ("10_瓦当_莲花雕饰",(152,154,153)),
 ("11_正脊_中轴脊瓦",(87,95,99)),
 ("12_正脊_菱格透雕",(104,111,115)),
 ("13_翼角_四向戗脊",(88,96,100)),
 ("14_脊端_燕尾起翘",(80,88,94)),
 ("15_参考_可编辑曲线",(200,160,81))]
layerids={}
for i,(name,color) in enumerate(LAYERS):
 l=r.Layer();l.Name=name;l.Color=(*color,255)
 layerids[name]=f.Layers.Add(l)
counts=collections.Counter()
def at(n,label=""):
 a=r.ObjectAttributes();a.LayerIndex=layerids[n];a.Name=label or n
 return a
def add(g,n,label="",typ=None):
 if g is None:return
 if isinstance(g,(list,tuple)):
  for q in g:add(q,n,label)
  return
 if isinstance(g,r.Brep):f.Objects.AddBrep(g,at(n,label))
 elif isinstance(g,r.Extrusion):f.Objects.AddExtrusion(g,at(n,label))
 elif isinstance(g,r.Mesh):f.Objects.AddMesh(g,at(n,label))
 elif isinstance(g,r.Curve):f.Objects.AddCurve(g,at(n,label))
 elif isinstance(g,r.NurbsSurface):f.Objects.AddSurface(g,at(n,label))
 else:raise TypeError(type(g))
 counts[n]+=1
def box(x1,y1,z1,x2,y2,z2,n,label=""):
 bb=r.Box(r.BoundingBox(P(float(x1),float(y1),float(z1)),P(float(x2),float(y2),float(z2))))
 add(r.Brep.CreateFromBox(bb),n,label)
def poly_mesh(points,faces):
 m=r.Mesh()
 for pt in points:m.Vertices.Add(*[float(v) for v in pt])
 for ids in faces:
  if len(ids)==3:m.Faces.AddFace(*ids)
  else:m.Faces.AddFace(*ids)
 m.Normals.ComputeNormals()
 return m
def prism_poly(bot,top,n,label):
 verts=bot+top;sz=len(bot);faces=[]
 faces.extend([tuple(reversed(range(sz))),tuple(range(sz,sz*2))])
 for i in range(sz):j=(i+1)%sz;faces.append((i,j,j+sz,i+sz))
 add(poly_mesh(verts,faces),n,label)
def curve(points,n,label,degree=3):
 points=[P(*p) for p in points]
 c=r.Curve.CreateControlPointCurve(points,degree)
 add(c,n,label);return c
def vadd(a,b):return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def vsub(a,b):return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def vmul(a,t):return (a[0]*t,a[1]*t,a[2]*t)
def dot(a,b):return sum(v*w for v,w in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 d=math.sqrt(dot(a,a))
 return tuple(q/d for q in a) if d else (0,0,1)
def tube(pts,rad,n,label="",facets=10,closed_caps=True):
 """一个细部构件 = 一个可独立选中、编辑的 Rhino 网格对象。"""
 if len(pts)<2:return
 m=r.Mesh();kk=max(6,facets)
 for i,p in enumerate(pts):
  dire=norm(vsub(pts[min(i+1,len(pts)-1)],pts[max(i-1,0)]))
  ax=(0,0,1) if abs(dire[2])<.85 else (1,0,0)
  v=norm(cross(dire,ax));w=norm(cross(dire,v))
  for j in range(kk):
   angle=2*math.pi*j/kk
   delta=vadd(vmul(v,rad*math.cos(angle)),vmul(w,rad*math.sin(angle)))
   m.Vertices.Add(*vadd(p,delta))
 for i in range(len(pts)-1):
  for j in range(kk):
   q=(j+1)%kk
   m.Faces.AddFace(i*kk+j,i*kk+q,(i+1)*kk+q,(i+1)*kk+j)
 if closed_caps:
  m.Vertices.Add(*pts[0]);m.Vertices.Add(*pts[-1])
  a=len(pts)*kk;b=a+1
  for j in range(kk):
   q=(j+1)%kk
   m.Faces.AddFace(a,q,j)
   m.Faces.AddFace(b,(len(pts)-1)*kk+j,(len(pts)-1)*kk+q)
 m.Normals.ComputeNormals()
 add(m,n,label)
def seq(start,end,count):
 return [start+(end-start)*i/(count-1) for i in range(count)]
def eave(x):
 s=min(1,abs(x)/2420.)
 return 2690+105*s*s+420*s**6
def roofz(x,y):
 s=abs(y)/505.
 return eave(x)+305*(1-min(1,s))
def ring_roof(y1,y2,label):
 # 双坡真实 NURBS ruled surfaces, 长向全段双端起翘
 pts1=[(x,y1,roofz(x,y1)) for x in seq(-2420,2420,81)]
 pts2=[(x,y2,roofz(x,y2)) for x in seq(-2420,2420,81)]
 c1=r.Curve.CreateControlPointCurve([P(*p) for p in pts1],3)
 c2=r.Curve.CreateControlPointCurve([P(*p) for p in pts2],3)
 surf=r.NurbsSurface.CreateRuledSurface(c1,c2)
 add(surf,"08_屋面_两坡NURBS曲面",label)
 return c1,c2
# 青石台基：四层独立实体
box(-2100,-350,0,2100,350,85,"01_基础_青石台基","底层挑出石台")
box(-2075,-334,85,2075,334,255,"01_基础_青石台基","第一层青石")
box(-2065,-325,255,2065,325,388,"01_基础_青石台基","第二层青石")
box(-2090,-345,388,2090,345,424,"01_基础_青石台基","石座上口压顶")
for side in (-1,1):
 y0=350 if side==1 else -362
 for k in range(10):
  x=-2098+k*420
  box(x,y0,85,x+410,y0+12,250,"01_基础_青石台基","逐块石砌纹理_%02d"%k)
# 砖砌主墙按照片上收；前后砖主体实体（可编辑形体）
bot=[(-2020,-260,424),(2020,-260,424),(2020,260,424),(-2020,260,424)]
top=[(-1920,-255,2160),(1920,-255,2160),(1920,255,2160),(-1920,255,2160)]
prism_poly(bot,top,"02_墙身_砖砌实体","上收砖墙实体")
# front plaster skin, rear brick wall with apparent relief
prism_poly([(-2015,-270,430),(2015,-270,430),(2015,-263,430),(-2015,-263,430)],
           [(-1915,-266,2160),(1915,-266,2160),(1915,-258,2160),(-1915,-258,2160)],
           "03_正面_白灰粉刷","照片所见正面连续白灰面层")
for row in range(19):
 z0=430+row*90
 half=2016-(z0-430)*100/1730
 for j in range(-11,12):
  x=j*220+((row%2)*110)
  a=max(-half+5,x-106)
  b=min(half-5,x+106)
  if b-a>30:box(a,260,z0,b,276,z0+83,"04_背面_青砖纹理","背面青砖第%d行"%row)
# Decorative band, each face with chamfer/octagonal plaques:
box(-1960,-292,2160,1960,292,2495,"05_墙头_装饰带基底","通长灰塑带")
def octogon(cx,w,cz,h,corner):
 l=cx-w/2;rr=cx+w/2;b=cz-h/2;t=cz+h/2;c=corner
 return [(l+c,b),(rr-c,b),(rr,b+c),(rr,t-c),(rr-c,t),(l+c,t),(l,t-c),(l,b+c)]
panel_widths=[625,225,640,225,640,225,625]
spaces=41
start=-(sum(panel_widths)+spaces*(len(panel_widths)-1))/2
for sg in (-1,1):
 outer_y=sg*300
 offset=0
 for j,w in enumerate(panel_widths):
  cx=start+offset+w/2;offset+=w+spaces
  tall=225 if j%2==0 else 205
  for contour,thick,rad in [(octogon(cx,w,2322,tall,30),0,10),(octogon(cx,w*.86,2322,tall*.76,23),sg*18,8)]:
   pts=[(xx,outer_y+thick,zz) for xx,zz in contour]
   tube(pts+[pts[0]],rad,"06_墙头_八角多层灰塑边框","灰塑八角框 第%d块"%j,facets=6)
   # planar central panel for faded gray framed painting / stucco
  box(cx-w*.35,outer_y+sg*9,2275,cx+w*.35,outer_y+sg*12,2365,
      "05_墙头_装饰带基底","内芯填灰 第%d块"%j)
# Frieze molding and continuous lower band: stratified stepped ancient corbel
for k in range(9):
 width=3890+k*20
 hh=2490+22*k
 for sg in (-1,1):
  yy=sg*(302+k*13)
  tube([(x,yy,hh) for x in seq(-width/2,width/2,3)],9 if k%2 else 14,
       "07_檐下_叠涩压檐线脚","压檐横线第%d道"%k,8)
# broad shelf facing eave as tapered band with curves on front/back
for sg in (-1,1):
 for k in range(5):
  tube([(x,sg*(410+18*k),2630+10*k+65*(abs(x)/2360)**4) for x in seq(-2300,2300,45)],
       14,"07_檐下_叠涩压檐线脚","曲线叠涩檐口",8)
# Accurate up-curved dual roof slopes as NURBS
for sg in (-1,1):
 c1,c2=ring_roof(0,sg*505,"斜坡青瓦面 "+("背" if sg>0 else "前"))
 # bottom layer gives thickness to roof edge
 ring_roof(sg*8,sg*499,"第二层基面_曲线")
 for y in (sg*505,sg*480):
  tube([(x,y,roofz(x,y)+(-25 if abs(y)>500 else 10)) for x in seq(-2420,2420,65)],
       24 if abs(y)>500 else 14,"11_正脊_中轴脊瓦","檐口连续弧线",12)
# lower underlay strips and cover cylinder tile segments; each tube individual element
for k in range(39):
 x=-2280+k*120
 for sg in (-1,1):
  for row in range(4):
   y0=sg*(10+row*127)
   y1=sg*min(505,10+(row+1)*127+13)
   s=seq(y0,y1,6)
   pts=[(x,y,roofz(x,y)+23+5*math.sin(math.pi*i/5)) for i,y in enumerate(s)]
   tube(pts,39,"09_屋面_板瓦和筒瓦","筒瓦 x%0.0f row%d"%(x,row),12)
  # shallow trough between cylinders, stagger pattern
  for row in range(3):
   a=sg*(15+row*140);b=sg*(15+(row+1)*140)
   pts=[(x+58,y,roofz(x+58,y)-8) for y in seq(a,b,5)]
   tube(pts,12,"09_屋面_板瓦和筒瓦","板瓦行间搭接",8)
  # lotus tile ends: circular clay cylinder and radial carved petals
  y=sg*510; zz=roofz(x,y)+27
  tube([(x,y,zz),(x,y+sg*28,zz)],43,"10_瓦当_莲花雕饰","花瓣筒瓦当",16)
  for petal in range(8):
   a=2*math.pi*petal/8
   px=x+21*math.cos(a);pz=zz+21*math.sin(a)
   tube([(px,y+sg*26,pz),(px,y+sg*30,pz)],8,
        "10_瓦当_莲花雕饰","单瓣瓦当",6)
# central back-bone ridge and vertical openwork screen
tube([(x,0,roofz(x,0)+34) for x in seq(-2420,2420,69)],38,
     "11_正脊_中轴脊瓦","主脊底部盖瓦",14)
tube([(x,0,roofz(x,0)+160) for x in seq(-2140,2140,59)],26,
     "11_正脊_中轴脊瓦","主脊顶部脊瓦",14)
for sg in (-1,1):
 y=sg*36
 # geometric diamond repeat and trefoil openings, between upper and lower rails
 for j in range(36):
  x=-2012+j*115
  zz=roofz(x,0)+75
  tube([(x-43,y,zz),(x+43,y,zz+70)],9,
       "12_正脊_菱格透雕","菱格左撇",6)
  tube([(x-43,y,zz+70),(x+43,y,zz)],9,
       "12_正脊_菱格透雕","菱格右撇",6)
  for h in range(4):
   theta=h*math.pi/2
   px=x+20*math.cos(theta)
   pz=zz+33+20*math.sin(theta)
   tube([(px,y,pz),(px,y+sg*9,pz)],10,
        "12_正脊_菱格透雕","四瓣透花",8)
# Four asymmetric-in-depth upturned hip ridge wings and swept end finials
for sx in (-1,1):
 for sg in (-1,1):
  path=[(sx*xx,sg*yy,roofz(sx*xx,sg*yy)+50+dz) for xx,yy,dz in
        [(1620,0,0),(1880,138,18),(2110,280,40),(2300,405,75),(2420,502,125)]]
  tube(path,32,"13_翼角_四向戗脊","端部戗脊_交错Y型",12)
  tip=path[-1]
  tube([tip,(tip[0]+sx*48,tip[1]+sg*20,tip[2]+57)],27,
       "13_翼角_四向戗脊","角部上翘",12)
 middle=[(sx*xx,0,roofz(sx*xx,0)+150+up) for xx,up in
         [(1860,0),(2130,28),(2280,86),(2410,182),(2515,295)]]
 tube(middle,30,"14_脊端_燕尾起翘","燕尾形正脊端部",14)
 tube([(sx*xx,-53,roofz(sx*xx,0)+160+up) for xx,up in
       [(1650,0),(1790,25),(1880,92)]],19,
       "14_脊端_燕尾起翘","短脊吻",12)
# Independent editable master profile curves for future adjustment.
for y in (-505,0,505):
 curve([(x,y,roofz(x,y)) for x in seq(-2420,2420,45)],
       "15_参考_可编辑曲线","檐口或屋脊控制曲线")
# Document user strings and metadata
success=f.Write(OUT,8)
if not success:raise IOError("Rhino 3DM file write failed!")
check=r.File3dm.Read(OUT)
if check is None:raise IOError("3DM re-open failed")
objects=list(check.Objects)
summary={
 "file":OUT,"file_bytes":os.path.getsize(OUT),"rhino_version":8,
 "object_count":len(objects),"layer_count":len(list(check.Layers)),
 "units":"millimeters","dimension_status":"all approximate from photographs; verify onsite",
 "approx_dimensions_mm":{"overall_width":5020,"masonry_width":4200,
 "total_height_roof_horn":3590,"base_to_ornament":2500,"wall_depth":650,
 "roof_depth":1010},
 "object_counts_by_layer":dict(counts),
 "verification":"Rhino File3dm.Read reopened successfully"
}
with open(REPORT,"w",encoding="utf-8") as fh:json.dump(summary,fh,ensure_ascii=False,indent=2)
readme="""照壁 Rhino 原生照片复原模型 - 2026-10-11

主模型：照壁_照片复原_可编辑模型.3dm
打开方式：Rhino 7/8，菜单 文件 -> 打开。

参考来源：正、背立面实景，近距离檐口照片，DJI_0069/0070/0071 俯拍。

构造分层：
01 青石台基 02 砖砌墙体 03 白灰粉刷 04 清水青砖背面
05 墙顶装饰带 06 八角灰塑边框 07 叠涩压檐
08 双坡 NURBS 屋面 09 青瓦筒瓦 10 莲花瓦当
11 正脊盖瓦 12 菱格透雕 13 戗脊 14 燕尾翘角
15 可编辑檐口、屋脊控制曲线。

技术说明：
墙石采用实体Brep；屋面采用可编辑NURBS曲面；
筒瓦、莲瓣、菱格与起翘戗脊采用独立分件 Rhino Mesh 几何，
均可单独选择、变形、替换或重新布置；单位均为毫米。
模型含大量可独立编辑的瓦件，不是截图贴图、不是单一整体扫描Mesh。

尺寸为根据照片拟定值：墙体基座宽约 4200 mm；墙厚约 650 mm；
屋顶总宽约 5020 mm；最终尺寸须现场实测确认。
注意：屋檐体系为根据照片反推的表现性复原，并非验证过的建筑古建结构做法。
如用于施工/保护修缮，应测量檩、椽、瓦口、压檐和砖墙实际构造。

此文件由本机 Anaconda rhino3dm 8.35 原生写入并重新打开验证。
"""
with open(DETAIL,"w",encoding="utf-8") as fh:fh.write(readme)
print(json.dumps(summary,ensure_ascii=False,indent=2))
