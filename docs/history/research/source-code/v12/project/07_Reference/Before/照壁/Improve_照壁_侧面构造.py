# -*- coding: utf-8 -*-
import rhino3dm as r, math, os, json, collections
P=r.Point3d
root=r'E:\CODEXdata\before\照壁'
original=os.path.join(root,'照壁_照片复原_可编辑模型.3dm')
output=os.path.join(root,'照壁_侧面补全_v2.3dm')
f=r.File3dm.Read(original)
assert f is not None, 'previous model missing'
old=len(list(f.Objects))
for i in [13]:
    layer=list(f.Layers)[i]
    layer.Visible=False  # original simplified finials hidden, can re-enable in Rhino
datas=[('16_侧面白灰与侧壁',(214,210,201)),('17_青石基础侧面分块',(132,130,124)),
('18_侧面装饰带灰塑边框',(167,164,157)),('19_檐下叠涩与转角',(132,132,126)),
('20_侧面山花封檐板',(102,107,110)),('21_侧向曲线脊瓦',(83,92,99)),
('22_中央高翘脊吻',(76,85,89)),('23_旁侧短翘脊吻',(94,99,101)),
('24_两侧燕尾檐角',(83,92,98)),('25_侧面测绘控制线',(184,142,62))]
ids={}
for nm,col in datas:
 l=r.Layer();l.Name=nm;l.Color=(*col,255);ids[nm]=f.Layers.Add(l)
counts=collections.Counter()
def add(obj,layer,name):
 a=r.ObjectAttributes();a.LayerIndex=ids[layer];a.Name=name
 if isinstance(obj,r.Mesh):f.Objects.AddMesh(obj,a)
 elif isinstance(obj,r.Brep):f.Objects.AddBrep(obj,a)
 elif isinstance(obj,r.Curve):f.Objects.AddCurve(obj,a)
 else:raise TypeError(str(type(obj)))
 counts[layer]+=1
def geom(vertices,faces,layer,name):
 m=r.Mesh()
 for v in vertices:m.Vertices.Add(*v)
 for face in faces:m.Faces.AddFace(*face)
 m.Normals.ComputeNormals()
 if not m.IsValid:raise ValueError('invalid geometry: '+name)
 add(m,layer,name)
def plate(bottom,top,layer,name):
 n=len(bottom)
 a0=bottom[0]
 u=[bottom[1][i]-a0[i] for i in range(3)]
 v=[bottom[2][i]-a0[i] for i in range(3)]
 normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 drop=max(range(3),key=lambda i:abs(normal[i]))
 coords=[tuple(q[i] for i in range(3) if i!=drop) for q in bottom]
 winding=1 if sum(coords[i][0]*coords[(i+1)%n][1]-coords[(i+1)%n][0]*coords[i][1] for i in range(n))>0 else -1
 def orient(a,b,c):
  return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 pending=list(range(n));triangles=[]
 for cycle in range(n*n):
  if len(pending)==3:
   triangles.append(tuple(pending));break
  found=False
  for j in range(len(pending)):
   a,b,c=pending[j-1],pending[j],pending[(j+1)%len(pending)]
   pa,pb,pc=coords[a],coords[b],coords[c]
   if orient(pa,pb,pc)*winding<=.001:continue
   if any(q not in (a,b,c) and all(orient(u,v,coords[q])*winding>=-.001 for u,v in [(pa,pb),(pb,pc),(pc,pa)]) for q in pending):continue
   triangles.append((a,b,c));pending.pop(j);found=True;break
  if not found:raise ValueError('untriangulable face: '+name)
 faces=[tuple(reversed(t)) for t in triangles]+[tuple(i+n for i in t) for t in triangles]
 faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 geom(bottom+top,faces,layer,name)
def box(x0,y0,z0,x1,y1,z1,layer,name):
 p=P(min(x0,x1),min(y0,y1),min(z0,z1));q=P(max(x0,x1),max(y0,y1),max(z0,z1))
 add(r.Brep.CreateFromBox(r.Box(r.BoundingBox(p,q))),layer,name)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def unit(v):
 d=math.sqrt(dot(v,v))
 return tuple(x/d for x in v) if d else (0,0,1)
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def minus(a,b):return tuple(x-y for x,y in zip(a,b))
def rail(pts,rad,layer,name,side=10):
 if len(pts)<2:return
 m=r.Mesh()
 for i,p in enumerate(pts):
  v=unit(minus(pts[min(i+1,len(pts)-1)],pts[max(0,i-1)]))
  aux=(0,0,1) if abs(v[2])<.85 else (1,0,0)
  u=unit(cross(v,aux));w=unit(cross(v,u))
  for j in range(side):
   a=2*math.pi*j/side
   m.Vertices.Add(*(p[k]+rad*(u[k]*math.cos(a)+w[k]*math.sin(a)) for k in range(3)))
 for i in range(len(pts)-1):
  for j in range(side):m.Faces.AddFace(i*side+j,i*side+(j+1)%side,(i+1)*side+(j+1)%side,(i+1)*side+j)
 m.Vertices.Add(*pts[0]);m.Vertices.Add(*pts[-1]);n=len(pts)*side
 for j in range(side):
  m.Faces.AddFace(n,(j+1)%side,j)
  m.Faces.AddFace(n+1,(len(pts)-1)*side+j,(len(pts)-1)*side+(j+1)%side)
 m.Normals.ComputeNormals()
 if not m.IsValid:raise ValueError('invalid rail: '+name)
 add(m,layer,name)
def cv(pts,layer,name):
 c=r.Curve.CreateControlPointCurve([P(*p) for p in pts],3)
 add(c,layer,name)
def seq(a,b,n):return [a+(b-a)*i/(n-1) for i in range(n)]
def eave(x):
 t=min(1,abs(x)/2420.)
 return 2690+105*t*t+420*t**6
def roof(x,y):return eave(x)+305*max(0,1-abs(y)/505.)
def curved_end(x,y):
 lift=max(0,(abs(y)-332)/173.)
 return roof(x,y)+235*lift*lift
def octagon(w,h,z,cut):
 l=-w/2;rt=w/2;low=z-h/2;high=z+h/2;c=cut
 return [(l+c,low),(rt-c,low),(rt,low+c),(rt,high-c),(rt-c,high),(l+c,high),(l,high-c),(l,low+c)]
for sx in (-1,1):
 place='东端' if sx>0 else '西端'
 def wallx(z):return 2018-95*(z-430)/1730.
 bottom=[(sx*wallx(430),-251,430),(sx*wallx(430),251,430),(sx*(wallx(430)+11),251,430),(sx*(wallx(430)+11),-251,430)]
 top=[(sx*wallx(2157),-251,2157),(sx*wallx(2157),251,2157),(sx*(wallx(2157)+11),251,2157),(sx*(wallx(2157)+11),-251,2157)]
 plate(bottom,top,'16_侧面白灰与侧壁',place+'侧墙连续白灰层')
 for z0 in (95,170,249,318):
  rail([(sx*2111,y,z0) for y in seq(-344,344,8)],6,'17_青石基础侧面分块',place+'石基横灰缝')
 for y0 in (-190,0,190):
  rail([(sx*2112,y0,z0) for z0 in seq(94,390,6)],5,'17_青石基础侧面分块',place+'石块竖灰缝')
 for j,(w,h) in enumerate([(460,235),(380,173)]):
  ring=octagon(w,h,2325,28)
  p=[(sx*(1983+j*24),y,z) for y,z in ring]
  q=[(sx*(1998+j*24),y,z) for y,z in ring]
  plate(p,q,'18_侧面装饰带灰塑边框',place+'灰塑八角倒角框'+str(j))
  for k in range(8):
   rail([q[k],q[(k+1)%8]],7,'18_侧面装饰带灰塑边框',place+'灰塑勾缝'+str(j)+'_'+str(k),8)
 for y in (-252,252):
  for z in (2180,2475):
   rail([(sx*1950,y,z),(sx*2012,y,z)],10,'18_侧面装饰带灰塑边框',place+'装饰带转角')
 for k in range(9):
  x=sx*(1970+20*k);z=2510+24*k
  rail([(x,y,z) for y in seq(-300-k*12,300+k*12,9)],10,'19_檐下叠涩与转角',place+'叠涩线脚第'+str(k),10)
 # gable / verge under the tiles, with two upturned lateral ends
 ys=seq(-500,500,51)
 x=sx*2370
 upper=[(x,y,curved_end(x,y)-60) for y in ys]
 lower=[(x,y,curved_end(x,y)-245) for y in ys]
 n=len(ys)
 verts=upper+lower+[(p[0]+sx*55,p[1],p[2]) for p in upper+lower]
 faces=[]
 for i in range(n-1):
  faces.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),
   (i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
 faces.extend([(0,n,3*n,2*n),(n-1,2*n-1,4*n-1,3*n-1)])
 geom(verts,faces,'20_侧面山花封檐板',place+'侧向实体封檐带')
 for j,(dz,radius) in enumerate([(-50,25),(-107,14),(-204,14),(-249,9)]):
  rail([(sx*2443,y,curved_end(x,y)+dz) for y in ys],radius,
     '21_侧向曲线脊瓦',place+'沿侧立面上下曲线'+str(j),12)
 # two soaring eave corner returns wrapping along roof
 for sg in (-1,1):
  pts=[]
  for y in seq(sg*330,sg*547,20):
   t=max(0,(abs(y)-480)/67)
   pts.append((sx*(2430+54*t*t),y,curved_end(x,y)-40+80*t*t))
  rail(pts,29,'24_两侧燕尾檐角',place+'卷翘侧檐_'+str(sg),12)
 # high gable-end finial: broad root, tapering ornamental flat slab
 x0=sx*2440
 base=roof(x0,0)+68
 p=[(-100,0),(-82,75),(-61,150),(-48,265),(-34,398),(-26,550),(-20,703),(-12,766),
    (12,766),(20,706),(29,539),(34,409),(49,270),(65,154),(88,75),(102,0)]
 a=[(x0-sx*35,y,base+z) for y,z in p]
 b=[(x0+sx*35,y,base+z) for y,z in p]
 plate(a,b,'22_中央高翘脊吻',place+'主脊高立装饰吻')
 for sg in (-1,1):
  rail([(x0+sx*40,sg*w,base+h) for w,h in
     [(64,100),(49,240),(35,365),(25,510),(15,669),(12,750)]],7,
     '22_中央高翘脊吻',place+'高脊吻侧面刻线',8)
 rail([(x0-sx*52,0,base+761),(x0+sx*52,0,base+761)],21,
      '22_中央高翘脊吻',place+'高脊吻顶部瓦钮',12)
 # staggered shorter rear spike shown in photograph
 qx=sx*2322;yy=146;qb=roof(qx,yy)+75
 poly=[(-45,0),(-31,83),(-22,170),(-13,282),(10,307),(19,219),(30,101),(42,0)]
 a=[(qx-sx*37,yy+y,qb+z) for y,z in poly]
 b=[(qx+sx*37,yy+y,qb+z) for y,z in poly]
 plate(a,b,'23_旁侧短翘脊吻',place+'后侧短脊吻')
 for sg in (-1,1):
  rail([(sx*2443,y,curved_end(x,y)+40) for y in seq(0,sg*518,31)],26,
       '24_两侧燕尾檐角',place+'正脊向侧檐交接'+str(sg),12)
 cv([(sx*2443,y,curved_end(x,y)-50) for y in ys],
    '25_侧面测绘控制线',place+'侧檐弧线控制线')
cv([(2440,0,roof(2440,0)+70),(2440,0,roof(2440,0)+836)],
  '25_侧面测绘控制线','端部高脊吻高度控制线')
assert f.Write(output,8),'could not write new Rhino model'
check=r.File3dm.Read(output)
assert check is not None
allobjects=list(check.Objects)
invalid=[i for i,item in enumerate(allobjects) if not item.Geometry.IsValid]
assert not invalid,'geometry failures:'+repr(invalid[:8])
report={'source':original,'updated':output,'old_objects':old,'new_side_components':sum(counts.values()),
        'total_components':len(allobjects),'layers':len(list(check.Layers)),
        'invalid':len(invalid),'file_bytes':os.path.getsize(output),'new_layers':dict(counts),
        'note':'侧面细部基于照片推定，不是现场量测尺寸。原 .3dm 已保留。'}
with open(os.path.join(root,'照壁_侧面补全_v2_校验.json'),'w',encoding='utf-8') as g:
 json.dump(report,g,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=True,indent=2))
