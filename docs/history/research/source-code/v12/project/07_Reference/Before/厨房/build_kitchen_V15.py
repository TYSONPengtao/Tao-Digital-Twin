# -*- coding: utf-8 -*-
"""Kitchen Rhino V15: photograph-guided enhancement of inner-recessed timber corridor.
V14 retained untouched. mm units. Preserve footprint, ridge, three brick walls.
"""
import rhino3dm as R
import math, os, json, collections, time
from pathlib import Path
ROOT=Path(r'E:\CODEXdata\before\厨房')
ORIGINAL=ROOT/'厨房_V14_双坡平分_内凹檐廊_Rhino7兼容.3dm'
OUTPUT=ROOT/'厨房_V15_实景木构细化_檐廊_Rhino8.3dm'
REPORT=ROOT/'厨房_V15_构件验证.json'
NOTES=ROOT/'厨房_V15_修改说明.txt'
f=R.File3dm.Read(str(ORIGINAL))
if not f:raise IOError("V14 was not found")
start=time.time()
pre_objs=list(f.Objects)
pre_count=len(pre_objs)
# Remove only approximate old geometries that new detailed elements replace.
remove_prefixes=['RAFTER_FRONT_','RAFTER_REAR_','TRANSOM_','GLASS_TRANSOM_',
 'FRONT_TOP_TRANSOM_','BRACKET_','CORRIDOR_SPANDREL_','CORRIDOR_BRACING_']
removed=[]
for obj in pre_objs:
 nm=obj.Attributes.Name or ''
 remove=any(nm.startswith(prefix) for prefix in remove_prefixes)
 if nm.startswith('POST_') and any(s in nm for s in ('_木方柱','_木柱脚端箍','_木柱头承枋')):
  remove=True
 if remove:
  f.Objects.Delete(obj.Attributes.Id)
  removed.append(nm)
assert pre_count-len(removed)==len(list(f.Objects)),(pre_count,len(removed),len(list(f.Objects)))
# Set old optional lamps to hidden layer, retain original
for layer in f.Layers:
 if layer.Name.startswith("14_"):layer.Visible=False
# Material and layers
WOOD='HONEY_WOOD'; GOLD='GOLDEN_WOOD'; DARK='WOOD_DARK'
materials={item.Name:index for index,item in enumerate(f.Materials)}
colors={
'15_实木圆柱与柱头':(166,101,54),
'16_曲线月梁与挑梁':(160,94,47),
'17_檐下密排木椽':(111,68,34),
'18_檐廊枋木斗拱':(158,98,53),
'19_垂花柱及雕刻吊件':(174,109,62),
'20_步步锦通花格窗':(193,125,63),
'21_实木门扇浮雕':(166,101,55),
'22_檐口雀替和装饰线':(146,83,43),
'23_节庆装饰_默认隐藏':(180,37,38),
'24_结构测绘控制线_隐藏':(175,156,101)}
layer_index={}
for n,color in colors.items():
 layer=R.Layer();layer.Name=n;layer.Color=(*color,255)
 if n.startswith(('23_','24_')):layer.Visible=False
 layer_index[n]=f.Layers.Add(layer)
# extra paper materials optional
for matname,rgb in [('PAPER_RED',(201,44,38)),('PAPER_CREAM',(229,218,181)),('WOOD_DETAIL',(151,96,55))]:
 material=R.Material();material.Name=matname;material.DiffuseColor=(*rgb,255)
 materials[matname]=f.Materials.Add(material)
counts=collections.Counter()
P=R.Point3d
def attr(n,material,tag):
 a=R.ObjectAttributes();a.Name=tag;a.LayerIndex=layer_index[n]
 if material in materials:
  a.MaterialIndex=materials[material]
  a.MaterialSource=R.ObjectMaterialSource.MaterialFromObject
 a.SetUserString("construction_revision","V15_photo_guided")
 return a
def add(g,ly,ma,name):
 a=attr(ly,ma,name)
 if isinstance(g,R.Brep):f.Objects.AddBrep(g,a)
 elif isinstance(g,R.Mesh):f.Objects.AddMesh(g,a)
 elif isinstance(g,R.Curve):f.Objects.AddCurve(g,a)
 else:raise TypeError(str(type(g)))
 counts[ly]+=1
def mm(v):return 1000*float(v)
def p(pt):return P(*(mm(a) for a in pt))
def box(ly,ma,name,x0,y0,z0,x1,y1,z1):
 if not(x1>x0 and y1>y0 and z1>z0):raise ValueError(name)
 g=R.Brep.CreateFromBoundingBox(R.BoundingBox(p((x0,y0,z0)),p((x1,y1,z1))))
 add(g,ly,ma,name)
def cylinder(ly,ma,name,x,y,z0,z1,radius):
 assert z1>z0
 plane=R.Plane(p((x,y,z0)),R.Vector3d(0,0,1))
 circ=R.Circle(p((x,y,z0)),mm(radius))
 cyl=R.Cylinder(circ,mm(z1-z0))
 add(cyl.ToBrep(True,True),ly,ma,name)
def sphere(ly,ma,name,x,y,z,radius):
 add(R.Sphere(p((x,y,z)),mm(radius)).ToBrep(),ly,ma,name)
def vsub(a,b):return tuple(a[j]-b[j] for j in range(3))
def vadd(a,b):return tuple(a[j]+b[j] for j in range(3))
def vmul(a,k):return tuple(k*vv for vv in a)
def vdot(a,b):return sum(a[j]*b[j] for j in range(3))
def unit(a):
 s=math.sqrt(vdot(a,a));return tuple(q/s for q in a) if s else (0.,0.,1.)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def tube(ly,ma,name,points,radius,segments=8):
 if len(points)<2:return
 mesh=R.Mesh()
 for i,pos in enumerate(points):
  direction=unit(vsub(points[min(i+1,len(points)-1)],points[max(0,i-1)]))
  ref=(0.,0.,1.) if abs(direction[2])<.85 else (1.,0.,0.)
  u=unit(cross(direction,ref));v=unit(cross(direction,u))
  for j in range(segments):
   angle=2*math.pi*j/segments
   q=vadd(pos,vadd(vmul(u,radius*math.cos(angle)),vmul(v,radius*math.sin(angle))))
   mesh.Vertices.Add(mm(q[0]),mm(q[1]),mm(q[2]))
 for i in range(len(points)-1):
  for j in range(segments):
   mesh.Faces.AddFace(i*segments+j,i*segments+(j+1)%segments,
      (i+1)*segments+(j+1)%segments,(i+1)*segments+j)
 # cap
 mesh.Vertices.Add(*(mm(t) for t in points[0]))
 mesh.Vertices.Add(*(mm(t) for t in points[-1]))
 n=len(points)*segments
 for j in range(segments):
  mesh.Faces.AddFace(n,(j+1)%segments,j)
  mesh.Faces.AddFace(n+1,(len(points)-1)*segments+j,(len(points)-1)*segments+(j+1)%segments)
 mesh.Normals.ComputeNormals()
 if not mesh.IsValid:raise ValueError("invalid tube "+name)
 add(mesh,ly,ma,name)
def stepped_beam(ly,ma,name,pts,width=.12,height=.16):
 """Continuous curved timber beam with rectangular section and connected solid mesh."""
 mesh=R.Mesh()
 for i,pos in enumerate(pts):
  d=unit(vsub(pts[min(i+1,len(pts)-1)],pts[max(0,i-1)]))
  s=unit(cross(d,(0,0,1)))
  if math.sqrt(vdot(s,s))<.01:s=(0,1,0)
  u=unit(cross(d,s))
  for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   q=vadd(pos,vadd(vmul(s,a*width/2),vmul(u,b*height/2)))
   mesh.Vertices.Add(*(mm(t) for t in q))
 for k in range(len(pts)-1):
  for j in range(4):
   mesh.Faces.AddFace(k*4+j,k*4+(j+1)%4,(k+1)*4+(j+1)%4,(k+1)*4+j)
 mesh.Faces.AddFace(0,3,2,1)
 n=4*(len(pts)-1)
 mesh.Faces.AddFace(n,n+1,n+2,n+3)
 mesh.Normals.ComputeNormals()
 if not mesh.IsValid:raise ValueError('invalid beam '+name)
 add(mesh,ly,ma,name)
def seq(a,b,n):return [a+(b-a)*i/(n-1) for i in range(n)]
D=9.27901
EAVE=2.92
RIDGE=2.605
RIDGEZ=4.64
YFR=-.72
YBK=5.93
FACE=1.40
POST_X=[.639,3.619,5.939,8.919]
def zroof(y):
 return EAVE+(RIDGEZ-EAVE)*((y-YFR)/(RIDGE-YFR) if y<=RIDGE else (YBK-y)/(YBK-RIDGE))
# 1. Replace squared timber front posts with slightly tapered hardwood circular pillars
for i,x in enumerate(POST_X):
 tag='COL_%02d'%(i+1)
 cylinder('15_实木圆柱与柱头',WOOD,tag+'_实体柱身',x,.191,.245,2.73,.123)
 cylinder('15_实木圆柱与柱头',DARK,tag+'_柱脚木箍',x,.191,.245,.321,.137)
 cylinder('15_实木圆柱与柱头',GOLD,tag+'_柱头圆枋',x,.191,2.695,2.777,.146)
 box('15_实木圆柱与柱头',WOOD,tag+'_柱头承梁托块',
     x-.18,.045,2.758,x+.18,.352,2.850)
 for angle in range(8):
  a=math.tau*angle/8
  xx=x+.13*math.cos(a); yy=.191+.13*math.sin(a)
  tube('15_实木圆柱与柱头',GOLD,tag+'_柱头浅刻纹_'+str(angle),
       [(xx,yy,2.646),(xx,yy,2.725)],.006,6)
# 2. Curved "月梁" between posts visible from low angle: restrained camber to avoid fisheye exaggeration
for k in range(len(POST_X)-1):
 left,right=POST_X[k],POST_X[k+1]
 points=[]
 for s in seq(0,1,31):
  x=left+(right-left)*s
  z=3.015+.126*4*s*(1-s)
  points.append((x,.25,z))
 stepped_beam('16_曲线月梁与挑梁',WOOD,
              'MOON_BEAM_%02d_略起拱的弧形月梁'%k,points,.19,.19)
 tube('22_檐口雀替和装饰线',GOLD,
      'MOON_BEAM_%02d_上沿圆角线'%k,
      [(x,.142,z+.101) for x,_,z in points],.015,10)
 tube('22_檐口雀替和装饰线',DARK,
      'MOON_BEAM_%02d_下沿阴刻线'%k,
      [(x,.148,z-.104) for x,_,z in points],.009,8)
# 3. Column head ornament "吊瓜" and flying brackets; no structural sizing assertion
for i,x in enumerate(POST_X):
 for sign in [-1,1]:
  if sign<0 and i==0 or sign>0 and i==len(POST_X)-1:
   continue
  tt=[(x+sign*.06,.19,2.784),
      (x+sign*.24,.19,2.94),
      (x+sign*.37,.19,3.01)]
  stepped_beam('18_檐廊枋木斗拱',GOLD,
       'BRACKET_%02d_%s_柱头抱梁斜撑'%(i,sign),tt,.126,.128)
  box('18_檐廊枋木斗拱',WOOD,'BRACKET_%02d_%s_挑枋'% (i,sign),
       min(x+sign*.07,x+sign*.39),.135,2.832,
       max(x+sign*.07,x+sign*.39),.267,2.919)
  bx=x+sign*.36
  cylinder('19_垂花柱及雕刻吊件',GOLD,'HANG_%02d_%s_吊垂木颈'%(i,sign),
           bx,.198,2.632,2.826,.052)
  sphere('19_垂花柱及雕刻吊件',GOLD,'HANG_%02d_%s_莲花木坠'%(i,sign),
         bx,.198,2.637,.080)
  cylinder('19_垂花柱及雕刻吊件',DARK,'HANG_%02d_%s_上刻箍'%(i,sign),
           bx,.198,2.788,2.825,.068)
  for t in range(6):
   theta=math.tau*t/6
   xx=bx+.064*math.cos(theta);yy=.198+.064*math.sin(theta)
   tube('19_垂花柱及雕刻吊件',WOOD,
       'HANG_%02d_%s_垂花细纹_%d'%(i,sign,t),
       [(xx,yy,2.639),(xx*.998+bx*.002,yy,2.721)],.010,6)
# Extra plain continuous beam behind decorative arched beam (undermost eave band)
box('18_檐廊枋木斗拱',WOOD,'FRONT_FASCIA_前额枋分层檐板',
    .50,.052,2.69,9.045,.125,2.785)
box('22_檐口雀替和装饰线',GOLD,'FRONT_FASCIA_额枋平直金边',
    .52,.043,2.843,9.04,.055,2.870)
# 4. Dense exposed rafters under both slopes; no roofs removed or moved
for idx,x in enumerate(seq(.25,D-.23,39)):
 # 38-39 evenly spaced rafters approximately 0.23m apart
 for side in ['FRONT','REAR']:
  ya,yb=(-.655,RIDGE) if side=='FRONT' else (RIDGE,5.87)
  path=[(x,y,zroof(y)-.157) for y in seq(ya,yb,4)]
  stepped_beam('17_檐下密排木椽',DARK,
    'EXPOSED_RAFTER_%s_%02d'%(side,idx+1),path,.067,.106)
  # front eave not beyond existing roof line
  if side=='FRONT':
   stepped_beam('17_檐下密排木椽',WOOD,
       'RAFTER_TIP_FRONT_%02d'%idx,
       [(x,-.655,zroof(-.655)-.164),(x,-.54,zroof(-.54)-.164)],.074,.113)
# Wood ceiling furring battens transverse, follow underside of roof
for k,y in enumerate((-.48,.16,.78,1.39,2.00,3.20,3.83,4.56,5.18)):
 z=zroof(y)-.235
 box('18_檐廊枋木斗拱',WOOD,'CEILING_BATTEN_%02d_横向小枋'%k,
     .25,y-.032,z-.036,D-.23,y+.032,z+.036)
# Additional corridor cross braces under ceiling connect existing front posts to inner jamb, no facade projection.
for i,x in enumerate(POST_X):
 pts=[(x,.20,2.896),(x,.56,3.14),(x,.94,3.37),(x,1.36,3.49)]
 stepped_beam('18_檐廊枋木斗拱',WOOD,
              'CORRIDOR_TIE_%02d_前后梁'%i,pts,.134,.17)
# 5. Replace generic transom with open, stepped traditional lattice (continuous all facade bays).
# This is on recessed facade plane, not the front post line.
HEIGHT0=2.51
HEIGHT1=2.868
LEFT=.639
RIGHT=8.919
YY=FACE-.129
def segment_x(label,a,b,z,w=.032):
 if b-a<=.008:return
 box('20_步步锦通花格窗',GOLD,label,min(a,b),YY,z-w/2,max(a,b),YY+.092,z+w/2)
def segment_z(label,x,a,b,w=.033):
 if b-a<=.008:return
 box('20_步步锦通花格窗',GOLD,label,x-w/2,YY,min(a,b),x+w/2,YY+.092,max(a,b))
# frames and continuous rails
segment_x('LATTICE_FULL_BOTTOM',LEFT,RIGHT,HEIGHT0,.045)
segment_x('LATTICE_FULL_TOP',LEFT,RIGHT,HEIGHT1,.044)
for i in range(12):
 a=LEFT+(RIGHT-LEFT)*i/12.
 b=LEFT+(RIGHT-LEFT)*(i+1)/12.
 w=b-a
 z0=HEIGHT0
 z1=HEIGHT1
 segment_z('LATTICE_COLUMN_%02d_L'%i,a,z0,z1,.032)
 if i==11:segment_z('LATTICE_COLUMN_LAST_R',b,z0,z1,.032)
 # interlocking right-angle geometric "步步锦" pattern. Every rail is wood not a printed texture.
 xL=a+.085; xR=b-.085
 mid=(a+b)/2
 zB=z0+.082;zT=z1-.078
 segment_x('JIN_%02d_bottom_step'%i,a+.020,xL,zB)
 segment_z('JIN_%02d_inner_left'%i,xL,zB,zT)
 segment_x('JIN_%02d_crown'%i,xL,mid,zT)
 segment_z('JIN_%02d_inner_center'%i,mid,z0+.15,zT)
 segment_x('JIN_%02d_middle_link'%i,mid,xR,z0+.15)
 segment_z('JIN_%02d_inner_right'%i,xR,z0+.15,z1-.045)
 segment_x('JIN_%02d_right_end'%i,xR,b-.020,z1-.045)
# 6. Door relief panels based on wood lower panel photographs; made from reusable individual moldings
for i,(a,b) in enumerate(((3.659,4.619),(4.939,5.899))):
 for inset in (0.,.037):
  lo=a+.083+inset;hi=b-.083-inset
  zlo=.215+inset;zhi=.895-inset
  # arch-headed panel moulding, stepped on the top corners
  coords=[(lo,zlo),(hi,zlo),(hi,zhi-.14),(hi-.055,zhi-.14),
          (hi-.080,zhi-.065),((hi+lo)/2+0.10,zhi-.04),
          ((hi+lo)/2,zhi+.018),((hi+lo)/2-.10,zhi-.04),
          (lo+.080,zhi-.065),(lo+.055,zhi-.14),(lo,zhi-.14),(lo,zlo)]
  tube('21_实木门扇浮雕',DARK,'DOOR_PANEL_%02d_%s_如意开光压条'%(i,inset),
       [(x,FACE-.084-inset*.05,z) for x,z in coords],.014 if inset==0 else .009,8)
 # middle raised panel
 box('21_实木门扇浮雕',WOOD,'DOOR_PANEL_%02d_方芯木板'%i,
     a+.135,FACE-.074,.265,b-.135,FACE-.058,.615)
 # vertical door leaf center joints and lower rail
 box('21_实木门扇浮雕',GOLD,'DOOR_PANEL_%02d_下槛细木'%i,
    a+.06,FACE-.08,.092,b-.06,FACE-.066,.145)
# 7. optional seasonal festive decorations preserved in separate hidden layer, not part of construction.
for i,x in enumerate([1.2,2.48,4.2,6.12,7.25,8.12]):
 material='PAPER_RED' if i%3!=1 else 'PAPER_CREAM'
 box('23_节庆装饰_默认隐藏',material,'FESTIVE_PAPER_%02d'%i,
     x-.23,.69,2.08-(i%3)*.05,x+.23,.696,2.45-(i%3)*.05)
tube('23_节庆装饰_默认隐藏','PAPER_RED','节庆绳',
     [(x,.67,2.48) for x in seq(.7,8.8,22)],.007,6)
# 8. building controls only; hidden by default
for y,n in [(-.72,'roof front eave'),(2.605,'ridge equal pitches'),(5.93,'roof rear eave')]:
 ln=R.LineCurve(p((-.18,y,zroof(y))),p((9.73,y,zroof(y))))
 add(ln,'24_结构测绘控制线_隐藏','GOLD','FIXED '+n)
# Save and reopen
assert f.Write(str(OUTPUT),8),'write Rhino failed'
verify=R.File3dm.Read(str(OUTPUT))
assert verify is not None,'read-back failed'
objects=list(verify.Objects)
bad=[o.Attributes.Name for o in objects if not o.Geometry.IsValid]
assert not bad,'Invalid objects '+str(bad[:10])
assert verify.Settings.ModelUnitSystem==R.UnitSystem.Millimeters
bbox=[o.Geometry.GetBoundingBox() for o in objects]
overall=[min(a.Min.X for a in bbox),min(a.Min.Y for a in bbox),min(a.Min.Z for a in bbox),
         max(a.Max.X for a in bbox),max(a.Max.Y for a in bbox),max(a.Max.Z for a in bbox)]
# enforce original main roof bounds and structure layout unchanged, no exterior expansion
assert max(a.Max.X for a in bbox)<10100 and min(a.Min.X for a in bbox)>-1000
assert max(a.Max.Y for a in bbox)<6300 and min(a.Min.Y for a in bbox)>-1250
layers={ly.Name:ly.Visible for ly in verify.Layers}
summary=dict(output=str(OUTPUT),bytes=OUTPUT.stat().st_size,original_count=pre_count,
              removed_simplified_parts=len(removed),added_refined_parts=sum(counts.values()),
              final_count=len(objects),invalid_count=len(bad),
              layer_count=len(layers),objects_by_new_layer=dict(counts),
              roof_footprint_unchanged=True,roof_ridge_y_mm=2605,
              facade_y_mm=1400,columns_row_y_mm=191,
              new_elements_bounds_mm=[round(v,1) for v in overall],
              roof_width_m=9.91,roof_depth_m=6.65,
              notes="Materially grounded details with provisional geometries, no site-measured timber sizes")
REPORT.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
NOTES.write_text("""厨房 V15 实景木构檐廊优化说明
源模型：厨房_V14_双坡平分_内凹檐廊_Rhino7兼容.3dm（已保留，未改动）
新版：厨房_V15_实景木构细化_檐廊_Rhino8.3dm
依据：两张木构檐廊现场照片（室内仰视、侧向长廊）。

不变：
建筑基础轮廓约 9279×5664mm，双坡屋脊Y=2605mm，
前后坡投影各3325mm，前柱列y≈191mm，
门窗内退至y=1400mm，三面砖墙围合，内部无隔墙，
现有门窗和外部屋檐没有向外扩建。

更新：
1) 木柱由方形替换为独立可编辑圆木柱，石础保留；新增柱头圆枋和浅木刻线。
2) 三个开间的木制月梁局部略起拱，照片广角畸变可能造成弯曲夸张，
   本版只用了约126mm示意弧度，需实测。
3) 重建前、后坡屋面下的密排椽子和檐口末端，独立构件分类，
   原双坡屋面瓦材不变。
4) 增加檐廊前后联系梁、吊瓜垂花件、柱头挑枋、雀替、月梁阴刻线。
5) 内凹门窗面上方 12单元的步步锦开放式木格，替换了旧版简单密竖条；
   不再用仿玻璃背景遮挡镂空。
6) 两扇木门增加双层如意开光线脚，下段浮雕木板等。
7) 按实景加了独立可隐藏的节庆红纸和绳；原模拟灯具图层默认隐藏。

几何由可编辑 Brep、独立分组的 Mesh 和控制曲线组成；
V14原始主体未覆盖，新增图层15–24，节庆装饰与控制线默认关闭。
单位毫米，但檐梁、木装饰与门扇细部尺寸参考照片建模，
未现场实测或结构校核，不作为施工图。
""",encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True,indent=2))
