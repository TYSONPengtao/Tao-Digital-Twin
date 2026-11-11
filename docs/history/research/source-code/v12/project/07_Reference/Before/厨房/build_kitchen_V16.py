# -*- coding: utf-8 -*-
import rhino3dm as R
from pathlib import Path
import json,collections
P=R.Point3d
root=Path(r'E:\CODEXdata\before\厨房')
src=root/'厨房_V15_实景木构细化_檐廊_Rhino8.3dm'
dest=root/'厨房_V16_双门中柱_悬空修复_Rhino8.3dm'
f=R.File3dm.Read(str(src))
assert f is not None,'找不到V15模型'
original=list(f.Objects)
original_guids=set(str(o.Attributes.Id) for o in original)
material={x.Name:i for i,x in enumerate(f.Materials)}
layer_names=[('25_落地圆木中柱',(177,105,56)),('26_石柱础及柱脚箍',(143,139,129)),
 ('27_门楣格窗交接横枋',(176,111,56)),('28_檐下上部梁枋檩条',(148,90,50)),
 ('29_悬空节点与吊件补接',(163,101,52))]
idx={}
for name,color in layer_names:
 l=R.Layer();l.Name=name;l.Color=(*color,255)
 idx[name]=f.Layers.Add(l)
count=collections.Counter();added={}
def pt(x,y,z):return P(x*1000,y*1000,z*1000)
def add(g,name,layer,mat='HONEY_WOOD'):
 a=R.ObjectAttributes();a.Name=name;a.LayerIndex=idx[layer]
 if mat in material:
  a.MaterialIndex=material[mat];a.MaterialSource=R.ObjectMaterialSource.MaterialFromObject
 a.SetUserString('revision','V16')
 if isinstance(g,R.Brep):f.Objects.AddBrep(g,a)
 else:raise TypeError(str(type(g)))
 count[layer]+=1;added[name]=g.GetBoundingBox()
def box(name,layer,a,b,mat='HONEY_WOOD'):
 assert all(a[i]<b[i] for i in range(3)),name
 g=R.Brep.CreateFromBoundingBox(R.BoundingBox(pt(*a),pt(*b)))
 add(g,name,layer,mat)
def cyl(name,layer,x,y,z0,z1,r,mat='HONEY_WOOD'):
 g=R.Cylinder(R.Circle(pt(x,y,z0),r*1000),(z1-z0)*1000).ToBrep(True,True)
 add(g,name,layer,mat)
POST='25_落地圆木中柱';STONE='26_石柱础及柱脚箍'
FAC='27_门楣格窗交接横枋';ROOF='28_檐下上部梁枋檩条';NODE='29_悬空节点与吊件补接'
# 两扇门的模型区间 X=3.659..4.619 和 4.939..5.899（m）。
# 中柱中心 X=4.779、内凹立面 Y=1.40。避免扩建整个前檐。
cx=4.779;cy=1.397
box('中柱_石质通长底座',STONE,(4.585,1.198,-.018),(4.974,1.594,.089),'STONE_FOUNDATION')
box('中柱_石础二层',STONE,(4.613,1.220,.077),(4.947,1.577,.182),'STONE_THRESHOLD')
cyl('中柱_青石束腰',STONE,cx,cy,.149,.291,.163,'STONE_FOUNDATION')
cyl('中柱_圆形木柱身',POST,cx,cy,.230,3.393,.151)
cyl('中柱_柱脚木箍',STONE,cx,cy,.237,.331,.165,'WOOD_DARK')
cyl('中柱_中部木箍',POST,cx,cy,2.742,2.848,.161,'GOLDEN_WOOD')
cyl('中柱_柱头圆盘',POST,cx,cy,3.312,3.467,.167,'GOLDEN_WOOD')
box('中柱_柱头承木方斗',POST,(4.548,1.211,3.379),(5.010,1.581,3.570))
# Replace the visually bare masonry strip between 2 door jambs with a wood backing mortise.
box('中柱_门框后置榫头',NODE,(4.628,1.311,.302),(4.932,1.352,2.592),'WOOD_DARK')
# Existing door frame top Z≈2.37; under-transom Z≈2.49 -> 120mm unsupprted strip.
box('门楣_贯通木枋',FAC,(.639,1.263,2.347),(8.919,1.455,2.511))
box('花格_下槛压木',FAC,(.639,1.244,2.487),(8.919,1.282,2.533),'GOLDEN_WOOD')
# Top of lattice 2.89; original full header bottom 2.91 -> tie with deliberate overlap.
box('花格_上槛承木',FAC,(.639,1.271,2.865),(8.919,1.461,2.965))
box('花格_上沿细压线',FAC,(.639,1.243,2.931),(8.919,1.277,2.954),'GOLDEN_WOOD')
# Upper facade structural frame: visible gap above top header is bridged by
# independent beam and short posts, with roof eave soffit ~Z3.86 at Y1.4m.
box('檐廊_内退立面连梁',ROOF,(.520,1.311,3.312),(9.03,1.552,3.565))
box('檐廊_内退连梁上沿',ROOF,(.520,1.280,3.536),(9.03,1.318,3.583),'GOLDEN_WOOD')
box('檐廊_椽下沿柱列长檩',ROOF,(.520,1.312,3.736),(9.03,1.543,3.902),'WOOD_DARK')
xs=(.639,3.619,4.779,5.939,8.919)
for i,x in enumerate(xs):
 box('檐廊_连梁立撑_%02d'%i,ROOF,
     (x-.108,1.302,3.518),(x+.108,1.540,3.782))
 box('檐廊_抱檩节点_%02d'%i,ROOF,
     (x-.124,1.289,3.740),(x+.124,1.551,3.861),'GOLDEN_WOOD')
box('中柱_上部穿插榫',ROOF,(4.685,1.318,3.427),(4.871,1.488,3.768),'WOOD_DARK')
box('中柱_椽底托梁',ROOF,(4.626,1.259,3.803),(4.932,1.549,3.921),'GOLDEN_WOOD')
for i,x in enumerate((.639,3.619,5.939,8.919)):
 box('旧柱头_连接补垫_%02d'%i,NODE,
     (x-.114,1.310,3.328),(x+.114,1.540,3.565))
# Decorative hanging pendant: top bracket and hanging melon had 7mm visual gap.
for i,x in enumerate((.639,3.619,5.939,8.919)):
 for sign in (-1,1):
  if (i==0 and sign==-1) or (i==3 and sign==1):continue
  cyl('吊瓜_%d_%d_上颈补接'%(i,sign),NODE,
      x+sign*.36,.198,2.811,2.855,.068,'GOLDEN_WOOD')
# The originally optional lamps were hidden and their chains ended midair;
# extend rods in SAME old hidden 14 layer so both remain optional.
lamplayer=next((i for i,l in enumerate(f.Layers) if l.Name.startswith('14_')),None)
if lamplayer is not None:
 for i,x in enumerate((1.13,7.94),1):
  a=R.ObjectAttributes();a.Name='灯具_%d_续接吊链'%i;a.LayerIndex=lamplayer
  a.MaterialSource=R.ObjectMaterialSource.MaterialFromObject
  a.MaterialIndex=material.get('LAMP_FRAME',0)
  geometry=R.Cylinder(R.Circle(pt(x,.33,2.767),13),(3.46-2.767)*1000).ToBrep(True,True)
  f.Objects.AddBrep(geometry,a)
  box('灯具_%d_上部木托'%i,NODE,
      (x-.085,.270,3.428),(x+.085,.408,3.513),'WOOD_DARK')
# Strict, scoped overlap checks: visual attachment indicators, not structural engineering proof.
def lookup(n):
 if n in added:return added[n]
 os=[o for o in f.Objects if o.Attributes.Name==n]
 assert os,n
 return os[0].Geometry.GetBoundingBox()
checks=[]
def joint(n,a,b):
 aa,bb=lookup(a),lookup(b)
 ok=all(min(getattr(aa.Max,j),getattr(bb.Max,j))>=max(getattr(aa.Min,j),getattr(bb.Min,j))-1 for j in ("X","Y","Z"))
 checks.append({'node':n,'connected_by_bbox':ok,'objects':[a,b]})
 if not ok:raise ValueError('脱离: '+n)
joint('石础接圆柱','中柱_青石束腰','中柱_圆形木柱身')
joint('木柱接柱头','中柱_圆形木柱身','中柱_柱头圆盘')
joint('柱头接斗','中柱_柱头圆盘','中柱_柱头承木方斗')
joint('斗接长梁','中柱_柱头承木方斗','檐廊_内退立面连梁')
joint('长梁接立撑','檐廊_内退立面连梁','檐廊_连梁立撑_02')
joint('立撑接檩','檐廊_连梁立撑_02','檐廊_椽下沿柱列长檩')
joint('门顶接门楣','DOOR_1_框顶枋','门楣_贯通木枋')
joint('门楣接上槛','门楣_贯通木枋','LATTICE_FULL_BOTTOM')
joint('格窗顶接木压','LATTICE_FULL_TOP','花格_上槛承木')
joint('上槛接原额枋','花格_上槛承木','INNER_HEADER_内退门窗上部结构横梁')
joint('圆柱接原额枋','中柱_圆形木柱身','INNER_HEADER_内退门窗上部结构横梁')
assert f.Write(str(dest),8),'cannot write 3dm'
verify=R.File3dm.Read(str(dest))
assert verify is not None,'cannot re-read 3dm'
objs=list(verify.Objects)
bad=[o.Attributes.Name for o in objs if not o.Geometry.IsValid]
assert not bad,'invalid geometries '+str(bad[:10])
assert original_guids<={str(o.Attributes.Id) for o in objs},'old objects missing'
assert verify.Settings.ModelUnitSystem==R.UnitSystem.Millimeters
qa={'model':str(dest),'bytes':dest.stat().st_size,
    'old_objects':len(original),'new_objects':len(objs)-len(original),
    'total_objects':len(objs),'layers':len(list(verify.Layers)),
    'invalid_geometries':len(bad),
    'new_parts_per_layer':dict(count),'selected_contact_checks':checks,
    'caveat':'照片尺寸推定。接触为AABB检查，非结构计算或布尔融合。'}
(root/'厨房_V16_连接校验.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'厨房_V16_说明.txt').write_text(
 '厨房 V16：两门中间增设落地圆木承柱及青石柱础，门顶和格窗下沿补120mm连续木枋，'
 '顶部格窗接入原额枋，新增檐下长梁、短撑及椽下檩条，补接吊瓜及可隐藏的灯具吊链。'
 '原 V15 全部构件保留；没有改变三面砖墙、原坡屋面、基础建筑轮廓或Y=1400mm的檐廊内退。'
 '尺寸源于实景推定，需实测，不能当作结构施工图。'
 ,encoding='utf-8')
print(json.dumps({k:v for k,v in qa.items() if k!='selected_contact_checks'},ensure_ascii=False,indent=2))
print('selected_contact_checks',len(checks),'pass',all(c['connected_by_bbox'] for c in checks))
