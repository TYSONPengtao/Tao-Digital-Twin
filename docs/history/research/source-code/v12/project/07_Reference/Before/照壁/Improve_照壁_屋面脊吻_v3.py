# -*- coding: utf-8 -*-
"""照壁侧檐照片复原v3：修正旧版悬空脊吻、断裂弧形瓦檐、檐下浮动线脚。
在既有v2文件基础上新增真实连接几何；旧错误层隐藏，原v2无改动。
单位mm，所有尺寸基于照片推拟，尚未测量。
"""
import rhino3dm as R
import math,os,json,collections
P=R.Point3d
ROOT=r'E:\CODEXdata\before\照壁'
SOURCE=os.path.join(ROOT,'照壁_侧面补全_v2.3dm')
OUT=os.path.join(ROOT,'照壁_实景侧面修正版_v3.3dm')
REPORT=os.path.join(ROOT,'照壁_实景侧面修正版_v3_校验.json')
f=R.File3dm.Read(SOURCE)
assert f,'Missing v2'
before=len(list(f.Objects))
hidden=[
6,  # 旧版断开的挑檐条和浮动线脚
12, # 旧版端部戗脊与新真实连接曲线交叉
13, # 旧版错误燕尾脊
14, # 旧参考曲线
18, # 侧面旧分离檐下叠涩
19, # 侧面老山花浮板
20, # 侧面老多重V字脊瓦
21, # 浮空高立脊饰
22, # 侧面错位短脊饰
23, # 侧檐两侧旧悬空尖角
24  # 控制曲线
]
for index in hidden:
 l=list(f.Layers)[index]
 l.Visible=False
CATS=[
('26_新屋面_端部弧面连接',(99,108,111)),
('27_新屋面_厚实封檐及封边',(96,101,104)),
('28_新瓦作_接续筒瓦与瓦当',(124,131,135)),
('29_新屋面_弯曲侧向戗脊',(82,91,96)),
('30_新脊吻_连体脊座',(87,90,93)),
('31_新脊吻_中部高立尖饰',(71,81,85)),
('32_新脊吻_一侧短饰',(87,91,96)),
('33_新灰塑_檐下连续叠涩',(146,148,143)),
('34_新灰塑_侧角装饰抱框',(183,180,167)),
('35_新屋面_出檐承托木石层',(108,110,108)),
('36_新测绘_尺寸说明参考曲线',(192,142,73))]
idx={}
for label,rgb in CATS:
 lay=R.Layer();lay.Name=label;lay.Color=(*rgb,255);idx[label]=f.Layers.Add(lay)
count=collections.Counter()
def add(obj,lyr,name):
 a=R.ObjectAttributes();a.Name=name;a.LayerIndex=idx[lyr]
 if isinstance(obj,R.Brep): f.Objects.AddBrep(obj,a)
 elif isinstance(obj,R.Mesh): f.Objects.AddMesh(obj,a)
 elif isinstance(obj,R.Curve): f.Objects.AddCurve(obj,a)
 elif isinstance(obj,R.NurbsSurface):f.Objects.AddSurface(obj,a)
 else:raise TypeError(type(obj))
 count[lyr]+=1
def box(xa,ya,za,xb,yb,zb,lyr,name):
 a=P(min(xa,xb),min(ya,yb),min(za,zb));b=P(max(xa,xb),max(ya,yb),max(za,zb))
 add(R.Brep.CreateFromBox(R.Box(R.BoundingBox(a,b))),lyr,name)
def mesh(v,faces,lyr,name):
 obj=R.Mesh()
 for p in v:obj.Vertices.Add(*p)
 for fac in faces:obj.Faces.AddFace(*fac)
 obj.Normals.ComputeNormals()
 if not obj.IsValid:raise ValueError("invalid mesh "+name)
 add(obj,lyr,name)
def dot(a,b):return sum(u*v for u,v in zip(a,b))
def unit(a):
 mag=math.sqrt(dot(a,a));return tuple(v/mag for v in a) if mag else (0,0,1)
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def rail(path,radius,lyr,name,faces=12,cap=True):
 obj=R.Mesh()
 for i,p in enumerate(path):
  dr=unit(minus(path[min(i+1,len(path)-1)],path[max(i-1,0)]))
  alt=(1,0,0) if abs(dr[2])>.83 else (0,0,1)
  u=unit(cross(dr,alt));v=unit(cross(dr,u))
  for j in range(faces):
   t=math.tau*j/faces
   obj.Vertices.Add(*(p[k]+radius*(u[k]*math.cos(t)+v[k]*math.sin(t)) for k in range(3)))
 for k in range(len(path)-1):
  for j in range(faces):
   obj.Faces.AddFace(k*faces+j,k*faces+(j+1)%faces,(k+1)*faces+(j+1)%faces,(k+1)*faces+j)
 if cap:
  obj.Vertices.Add(*path[0]);obj.Vertices.Add(*path[-1])
  l=faces*len(path)
  for j in range(faces):
   obj.Faces.AddFace(l,(j+1)%faces,j)
   obj.Faces.AddFace(l+1,(len(path)-1)*faces+j,(len(path)-1)*faces+(j+1)%faces)
 obj.Normals.ComputeNormals()
 if not obj.IsValid:raise ValueError('invalid rail '+name)
 add(obj,lyr,name)
def line(path,lyr,name):
 c=R.Curve.CreateControlPointCurve([P(*x) for x in path],3)
 add(c,lyr,name)
def axis(a,b,n):return [a+(b-a)*i/(n-1) for i in range(n)]
def eave(x):
 a=min(1.,abs(x)/2420.)
 return 2690+105*a*a+420*a**6
def roof(x,y):
 return eave(x)+305*max(0,1-abs(y)/505.)
def extension(x,y):
 # 与原屋顶重叠接续; 越靠近端部曲面，端角抬升越高
 s=max(0.,min(1.,(abs(x)-2140.)/330.))
 sy=max(0.,min(1.,(abs(y)-295.)/238.))
 smoothx=s*s*(3-2*s);smoothy=sy*sy*(3-2*sy)
 return 185.*smoothx*smoothy
def zroof(x,y):return roof(x,y)+extension(x,y)
def cap_up(y):
 # 侧立面轮廓从主脊下降进入凹曲，再在两个端部平滑起翘
 return zroof(2460,y)
def crown_mesh(sx,z0,ring_defs,lyr,name):
 # 实体渐变截面脊吻，由四边圆角方形剖面逐层过渡组成，底部穿入瓦面
 verts=[]
 for height,xctr,yctr,dx,dy in ring_defs:
  xx=sx*xctr
  # 8 sided pseudo-elliptic bevelled quadrilateral sections
  for u,v in [(-.7,-1),(.7,-1),(1,-.7),(1,.7),(.7,1),(-.7,1),(-1,.7),(-1,-.7)]:
   verts.append((xx+u*dx,yctr+v*dy,z0+height))
 n=len(ring_defs);faces=[]
 for row in range(n-1):
  for k in range(8):
   kk=(k+1)%8
   faces.append((row*8+k,row*8+kk,(row+1)*8+kk,(row+1)*8+k))
 faces.extend([(0,i+1,i) for i in range(1,7)])
 last=(n-1)*8
 faces.extend([(last,last+i,last+i+1) for i in range(1,7)])
 mesh(verts,faces,lyr,name)
def strip_mesh(sx,spec,lyr,name):
 # 通过二维网格连续展开布，支持侧向两个坡面形变
 nx=len(spec);ny=len(spec[0])
 verts=[]
 for row in spec:
  for x,y,z in row:verts.append((sx*x,y,z))
 faces=[]
 for i in range(nx-1):
  for j in range(ny-1):
   a=i*ny+j;b=(i+1)*ny+j
   faces.append((a,b,b+1,a+1))
 mesh(verts,faces,lyr,name)
def convex_plate(sx,ys,dx,zfunc,depth,lyr,name):
 # 侧面瓦檐下曲面板，厚度由上沿向下延伸
 aa=[(sx*dx,y,zfunc(y)) for y in ys]
 ab=[(sx*dx,y,zfunc(y)-depth) for y in ys]
 ba=[(sx*(dx+38),y,zfunc(y)) for y in ys]
 bb=[(sx*(dx+38),y,zfunc(y)-depth) for y in ys]
 n=len(ys);v=aa+ab+ba+bb;faces=[]
 for j in range(n-1):
  faces.extend([(j,j+1,n+j+1,n+j),
                (2*n+j,3*n+j,3*n+j+1,2*n+j+1),
                (j,2*n+j,2*n+j+1,j+1),
                (n+j,n+j+1,3*n+j+1,3*n+j)])
 faces.extend([(0,n,3*n,2*n),(n-1,2*n-1,4*n-1,3*n-1)])
 mesh(v,faces,lyr,name)
# high-end finial centerline absolute height alignment samples
contact={}
for sx in (-1,1):
 name='右端' if sx>0 else '左端'
 ys=axis(-520,520,51)
 # thick roof eave extension meshes connect to original ruled surfaces at x=2140
 xs=axis(2100,2470,15)
 upper=[[(x,y,zroof(sx*x,y)) for y in ys] for x in xs]
 lower=[[(x,y,zroof(sx*x,y)-56) for y in ys] for x in xs]
 strip_mesh(sx,upper,'26_新屋面_端部弧面连接',name+'延续双坡上覆瓦面')
 strip_mesh(sx,lower,'26_新屋面_端部弧面连接',name+'下承实板曲面')
 # new closed side fascia integrated with eave, roof edge x2470
 sidey=axis(-520,520,65)
 def facez(y):return cap_up(y)
 convex_plate(sx,sidey,2462,lambda y:facez(y)-55,185,
              '27_新屋面_厚实封檐及封边',name+'整段弧形侧挡板')
 # curved clay upper caps and molded edge matching underlying surface
 for offset,rad in [(10,24),(-52,22),(-124,17),(-218,14)]:
  rail([(sx*2502,y,facez(y)+offset) for y in sidey],
       rad,'27_新屋面_厚实封檐及封边',name+'曲线滴水与瓦脊第'+str(offset))
 # Special end tile band across the x end cap, not extruded loose quads under roof
 for j in range(10):
  y0=-466+j*105
  # short boundary ridge strips follow curvature and actually land on roof extension
  xx0=2185.; xx1=2455.
  t=axis(xx0,xx1,9)
  pts=[(sx*x,y0,zroof(sx*x,y0)+28) for x in t]
  rail(pts,31,'28_新瓦作_接续筒瓦与瓦当',name+'端部续瓦'+str(j),12)
  a=pts[-1]
  rail([a,(a[0]+sx*22,a[1],a[2])],33,
       '28_新瓦作_接续筒瓦与瓦当',name+'端部瓦当'+str(j),14)
 # smooth four lateral descending / rising corner hip ridges conform to sloped surface
 for sy in (-1,1):
  hip=[]
  for k in range(25):
   u=k/24
   x=1880+600*u
   y=sy*(45+485*u)
   zz=zroof(sx*x,y)+56
   # curved upwards only at final tip, reducing V-like thin line spikiness
   zz+=50*max(0,(u-.83)/.17)**2
   hip.append((sx*x,y,zz))
  rail(hip,35,'29_新屋面_弯曲侧向戗脊',name+'端部鱼尾翘角'+str(sy),14)
  tip=hip[-1]
  rail([tip,(tip[0]+sx*26,tip[1]+sy*31,tip[2]+36)],
       21,'29_新屋面_弯曲侧向戗脊',name+'翼角收头'+str(sy),12)
 # continuous main ridge transition to carved upright ornament
 ridgex=axis(2140,2478,31)
 rail([(sx*x,0,zroof(sx*x,0)+43) for x in ridgex],37,
      '30_新脊吻_连体脊座',name+'脊线主体贴合原屋脊',14)
 # integrated broad base: skirt from roof ridge through high-flying vertical shaft
 xx=2385
 roof_bottom=zroof(sx*xx,0)
 z0=roof_bottom-125
 # base inside roofing thickness; extends above as flared pedestal,
 # top tip higher than roof, with narrow shoulder and curved slanted ridge
 rings=[
   (0.,2385.,0,85.,127.),
   (96.,2387.,0,76.,111.),
   (205.,2394.,0,65.,81.),
   (310.,2403.,0,51.,61.),
   (425.,2411.,0,37.,43.),
   (560.,2423.,0,30.,31.),
   (705.,2434.,0,20.,21.),
   (785.,2442.,0,17.,20.),
   (822.,2440.,0,23.,23.)]
 crown_mesh(sx,z0,rings,'31_新脊吻_中部高立尖饰',
      name+'连体高脊吻_下插入瓦面')
 # slight round stacked top hat / ceramic finial
 topheight=z0+822
 rail([(sx*2434,0,topheight),(sx*2449,0,topheight+10)],
      22,'31_新脊吻_中部高立尖饰',name+'脊吻顶端圆头',12)
 # parallel flutes visible on upright high finial
 for sg in (-1,1):
  rail([(sx*(2412+27*t),sg*(48-30*t),
         z0+420+t*320) for t in axis(0,1,19)],5.5,
        '31_新脊吻_中部高立尖饰',name+'高脊吻竖向阴线',8)
 for h,rady in [(130,108),(310,64),(500,39),(695,23)]:
  rail([(sx*(2410+(h/820)*30),-rady,z0+h),
        (sx*(2410+(h/820)*30),rady,z0+h)],7,
       '31_新脊吻_中部高立尖饰',name+'高吻分层束箍'+str(h),8)
 # short spike at side of main, physically starts inside roof (not suspended)
 shortx=2270.;shorty=160.
 shortbase=zroof(sx*shortx,shorty)-93
 short_rings=[(0.,2265,shorty,55.,56.),
              (110.,2285,shorty+6,49.,45.),
              (205.,2310,shorty+20,33.,27.),
              (297.,2326,shorty+24,18.,18.),
              (358.,2344,shorty+29,17.,18.)]
 crown_mesh(sx,shortbase,short_rings,'32_新脊吻_一侧短饰',
           name+'短脊吻已锚固屋脊')
 rail([(sx*2330,shorty+22,shortbase+355),
       (sx*2350,shorty+29,shortbase+366)],17,
       '32_新脊吻_一侧短饰',name+'小脊吻翘端')
 # new continuous stepped corbels (support underside of the new extended roof)
 # wall top is x~1970, start all these supports above it, not hovering in the air
 for j in range(7):
  x=1960+40*j
  # thicken radial moldings in y and follow roof eave shape as the span grows
  ymax=320+24*j
  zz=2546+40*j
  box(sx*x,-ymax,zz,sx*(x+71),ymax,zz+37,
      '35_新屋面_出檐承托木石层',name+'出檐砖石承托叠出第'+str(j))
  # curved soffit molding y direction, abutting from the same support slab
  rail([(sx*(x+73),y,zz+24+40*(abs(y)/ymax)**4)
        for y in axis(-ymax,ymax,27)],9,
       '33_新灰塑_檐下连续叠涩',name+'逐层曲形收口线'+str(j),8)
 # outboard eave bracket/web ties roof to upper supporting corbels.
 # triangular support mesh running parallel to the side walls (last wood/stone cantilever)
 n=21
 ys2=axis(-470,470,n)
 xcs=[2220,2330,2410]
 vertices=[];faces=[]
 for x in xcs:
  for y in ys2:vertices.append((sx*x,y,zroof(sx*x,y)-91))
 for k in range(len(xcs)-1):
  for j in range(n-1):
   a=k*n+j
   faces.append((a,a+1,a+1+n,a+n))
 mesh(vertices,faces,'35_新屋面_出檐承托木石层',name+'曲面滴水板下承托')
 # new smaller continuous cornice on octagonal side panel
 panelx=2010
 for yy in (-256,256):
  for z in (2200,2437,2479):
   rail([(sx*(panelx-57),yy,z),(sx*(panelx+30),yy,z)],10,
        '34_新灰塑_侧角装饰抱框',name+'墙侧抱框转角收边',8)
 # translucent control curve objects on a hidden layer for later onsite adjustment
 line([(sx*2470,y,facez(y)+14) for y in axis(-520,520,51)],
       '36_新测绘_尺寸说明参考曲线',name+'贴合屋面侧向轮廓控制线')
 contact[name]={
  'roof_at_high_finial_base_center':round(roof_bottom,2),
  'finial_base_low':round(z0,2),
  'inserted_into_roof_mm':round(roof_bottom-z0,2),
  'short_spike_inserted_into_roof_mm':93}
# hide reference curves to keep clean viewport but retain as editable
list(f.Layers)[idx['36_新测绘_尺寸说明参考曲线']].Visible=False
if not f.Write(OUT,8):raise IOError("Could not save Rhino v3 3dm")
check=R.File3dm.Read(OUT)
assert check,'Failed to reopen saved Rhino v3'
items=list(check.Objects)
invalid=[i for i,o in enumerate(items) if not o.Geometry.IsValid]
if invalid:raise ValueError('Invalid objects: '+repr(invalid[:8]))
report=dict(
 file=OUT,original_model=SOURCE,old_objects=before,new_objects=sum(count.values()),
 total_objects=len(items),layers=len(list(check.Layers)),invalid_objects=len(invalid),
 bytes=os.path.getsize(OUT),hidden_old_problem_layers=hidden,
 layers_added=dict(count),finial_roof_contact=contact,
 note='Image-based reconstruction; no actual dimensions supplied. Roof pierces finial pedestal by 125mm for continuous physical contact.')
with open(REPORT,'w',encoding='utf-8') as fh:
 json.dump(report,fh,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=True,indent=2))
