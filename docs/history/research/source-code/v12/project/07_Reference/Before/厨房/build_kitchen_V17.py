# -*- coding: utf-8 -*-
"""厨房 V17 - 实景花格、檐廊步步锦挂落和木雕节点，逐件可编辑 Rhino 8 (mm)
主要参考：用户 2026-10-11 新增实景正立面和檐廊斜向照片。
不是施工图。基于 V16 进行构件替换而非重复覆贴。
"""
from pathlib import Path
import rhino3dm as R
import math,json,collections
ROOT=Path(r'E:\CODEXdata\before\厨房')
SOURCE=ROOT/'厨房_V16_双门中柱_悬空修复_Rhino8.3dm'
TARGET=ROOT/'厨房_V17_实景檐廊挂落_精细木窗_Rhino8.3dm'
QA=ROOT/'厨房_V17_几何与连接校验.json'
DESC=ROOT/'厨房_V17_木作细化说明.txt'
m=R.File3dm.Read(str(SOURCE))
if not m:raise IOError('Missing source V16')
source=list(m.Objects)
srcids={str(o.Attributes.Id) for o in source}
sourcedict=collections.Counter(o.Attributes.LayerIndex for o in source)
# Remove 2 categories of deprecated overly uniform lattice:
# 84 old JIN_ upper clerestory bars, 54 old six windows' rectilinear grid mullions.
obsolete=[]
for o in source:
 name=o.Attributes.Name or ''
 if name.startswith('JIN_') or (name.startswith('WINDOW_') and ('木格竖棂_' in name or '木格横棂_' in name)):
  obsolete.append((str(o.Attributes.Id),name,o.Attributes.LayerIndex))
for guid,name,_ in obsolete:
 m.Objects.Delete(R.Guid(guid) if hasattr(R,'Guid') else next(o.Attributes.Id for o in source if str(o.Attributes.Id)==guid))
after_deletion=list(m.Objects)
if len(after_deletion)!=len(source)-len(obsolete):
 raise AssertionError('Failed to remove precisely outdated grillwork')
# New layers and original finishes
COLORS=[
 ('30_实景_前檐贯通镂空挂落',(166,102,53)),
 ('31_实景_内退上槛步步锦木格',(176,112,57)),
 ('32_实景_木窗外框及压条',(153,91,48)),
 ('33_实景_花窗方圆格心及角花',(189,123,63)),
 ('34_实景_柱头雀替与卷草纹',(143,85,43)),
 ('35_实景_木雕外挑承托与榫卯',(164,102,56)),
 ('36_辅助_复原控制曲线_隐藏',(184,159,86))]
layers={}
for name,col in COLORS:
 l=R.Layer();l.Name=name;l.Color=(*col,255)
 l.Visible=not name.startswith('36_')
 layers[name]=m.Layers.Add(l)
MATS={ma.Name:i for i,ma in enumerate(m.Materials)}
if 'WOOD_DETAIL' not in MATS:
 fine=R.Material();fine.Name='WOOD_DETAIL';fine.DiffuseColor=(139,85,45,255)
 MATS['WOOD_DETAIL']=m.Materials.Add(fine)
print('MATERIALS',list(MATS.keys()))
counter=collections.Counter()
elements={}
P=R.Point3d
def vec(x,y,z):return P(x*1000,y*1000,z*1000)
def make_attr(name,layer,mat):
 a=R.ObjectAttributes();a.Name=name;a.LayerIndex=layers[layer]
 if mat in MATS:
  a.MaterialIndex=MATS[mat];a.MaterialSource=R.ObjectMaterialSource.MaterialFromObject
 a.SetUserString('Version','V17_photo_based_reconstruction')
 return a
def add(g,layer,name,mat='GOLDEN_WOOD'):
 a=make_attr(name,layer,mat)
 if isinstance(g,R.Brep):m.Objects.AddBrep(g,a)
 elif isinstance(g,R.Mesh):m.Objects.AddMesh(g,a)
 elif isinstance(g,R.Curve):m.Objects.AddCurve(g,a)
 else:raise ValueError(type(g))
 counter[layer]+=1;elements[name]=g.GetBoundingBox()
def box(name,layer,x0,y0,z0,x1,y1,z1,mat='HONEY_WOOD'):
 if not (x1>x0 and y1>y0 and z1>z0):
  raise ValueError('invalid box '+name)
 q=R.Brep.CreateFromBoundingBox(R.BoundingBox(vec(x0,y0,z0),vec(x1,y1,z1)))
 add(q,layer,name,mat)
def unit(v):
 d=math.sqrt(sum(t*t for t in v))
 return tuple(t/d for t in v) if d>1e-10 else (0,0,1)
def minus(a,b):return tuple(a[i]-b[i] for i in range(3))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def tube(name,layer,pts,radius,mat='GOLDEN_WOOD',sides=8):
 """真实有厚度封端独立Mesh; points in meters."""
 if len(pts)<2:return
 mesh=R.Mesh()
 for i,p in enumerate(pts):
  t=unit(minus(pts[min(i+1,len(pts)-1)],pts[max(0,i-1)]))
  base=(1,0,0) if abs(t[2])>.85 else (0,0,1)
  aa=unit(cross(t,base));bb=unit(cross(t,aa))
  for j in range(sides):
   a=math.tau*j/sides
   u=tuple(p[k]+radius*(aa[k]*math.cos(a)+bb[k]*math.sin(a)) for k in range(3))
   mesh.Vertices.Add(*[v*1000 for v in u])
 for i in range(len(pts)-1):
  for j in range(sides):
   k=(j+1)%sides
   mesh.Faces.AddFace(i*sides+j,i*sides+k,(i+1)*sides+k,(i+1)*sides+j)
 mesh.Vertices.Add(*[v*1000 for v in pts[0]])
 mesh.Vertices.Add(*[v*1000 for v in pts[-1]])
 j0=len(pts)*sides;j1=j0+1
 for j in range(sides):
  k=(j+1)%sides
  mesh.Faces.AddFace(j0,k,j)
  mesh.Faces.AddFace(j1,(len(pts)-1)*sides+j,(len(pts)-1)*sides+k)
 mesh.Normals.ComputeNormals()
 if not mesh.IsValid:raise RuntimeError('bad geometry '+name)
 add(mesh,layer,name,mat)
def horiz(name,layer,xa,xb,y,z,width=.024,depth=.055,mat='GOLDEN_WOOD'):
 if xb<xa:xa,xb=xb,xa
 box(name,layer,xa,y,z-width/2,xb,y+depth,z+width/2,mat)
def vert(name,layer,x,y,za,zb,width=.024,depth=.055,mat='GOLDEN_WOOD'):
 if zb<za:za,zb=zb,za
 box(name,layer,x-width/2,y,za,x+width/2,y+depth,zb,mat)
def fret(name,layer,points,y,radius=.013,mat='GOLDEN_WOOD'):
 tube(name,layer,[(x,y,z) for x,z in points],radius,mat,8)
def polyframe(prefix,layer,x0,x1,z0,z1,y,w=.025):
 horiz(prefix+'_底',layer,x0,x1,y,z0,w)
 horiz(prefix+'_顶',layer,x0,x1,y,z1,w)
 vert(prefix+'_左',layer,x0,y,z0,z1,w)
 vert(prefix+'_右',layer,x1,y,z0,z1,w)
# 1. OUTER CORRIDOR HANGING GEOMETRIC FRET:
# y~.18m front post line. Existing beam FRONT z2.745-2.895 at y.045-.360.
# top rail intentionally mortised into beam, bottom ~2.58m (no outside building expansion).
LY='30_实景_前檐贯通镂空挂落'
Y=.155;ZLOW=2.590;ZTOP=2.880
box('檐廊挂落_通长上沿榫头',LY,.547,Y,2.827,9.031,Y+.101,2.879)
box('檐廊挂落_通长下沿托枋',LY,.547,Y,2.571,9.031,Y+.101,2.610)
for bay,(left,right) in enumerate(zip([.639,3.619,5.939],[3.619,5.939,8.919])):
 # 1 pattern cell per ~0.58m, avoid abrupt end at column joint.
 countcells=round((right-left)/.56)
 for cell in range(countcells):
  a=left+(right-left)*cell/countcells
  b=left+(right-left)*(cell+1)/countcells
  d=b-a;pad=.033
  vert('外檐%02d_%02d_边框左'%(bay,cell),LY,a+.012,Y,2.595,2.849,.024,.101)
  # open stepped relief lines interlock, two layers with continuous joints.
  step=[(a+.018,ZLOW+.020),(a+.105,ZLOW+.020),
        (a+.105,ZLOW+.096),(a+.216,ZLOW+.096),
        (a+.216,ZTOP-.046),(a+d-.122,ZTOP-.046),
        (a+d-.122,ZLOW+.165),(b-.027,ZLOW+.165)]
  fret('外檐%02d_%02d_回纹挂落主线'%(bay,cell),LY,step,Y+.025,.017)
  step2=[(a+.018,ZTOP-.021),(a+.087,ZTOP-.021),
         (a+.087,ZLOW+.177),(a+.170,ZLOW+.177),
         (a+.170,ZLOW+.037),(a+d-.061,ZLOW+.037),
         (a+d-.061,ZTOP-.024),(b-.015,ZTOP-.024)]
  fret('外檐%02d_%02d_次层转折纹'%(bay,cell),LY,step2,Y+.045,.012)
  # load path: each pattern intersects top or lower continuous rail
  vert('外檐%02d_%02d_顶口落榫'%(bay,cell),LY,a+.087,Y+.024,ZTOP-.025,ZTOP+.016,.025,.060)
  vert('外檐%02d_%02d_下口落榫'%(bay,cell),LY,a+.170,Y+.040,ZLOW-.017,ZLOW+.048,.025,.062)
# end closure into existing beam/post footprint
for x in (.639,3.619,5.939,8.919):
 box('檐廊挂落_柱位边缘承托_%.3f'%x,LY,x-.062,.116,2.577,x+.062,.286,2.900)
 # bracket with stepped corbels attached to upper of front beam
 box('檐廊挂落_柱位挑托_%.3f'%x,LY,x-.126,.116,2.842,x+.126,.301,2.944)
# 2. INNER RECESSED WOOD WINDOW HEAD: replace JIN simple (84 objects)
INNER='31_实景_内退上槛步步锦木格'
L=.639;RIGHT=8.919
YI=1.260;Z0=2.520;Z1=2.861
# Original full top/bottom rails and verticals remain. Rebuild only open inner patterns.
# explicit unit rectangles align with 12 original LATTICE_COLUMN_ positions.
for k in range(12):
 a=L+(RIGHT-L)*k/12;b=L+(RIGHT-L)*(k+1)/12;d=b-a
 fret('内窗花格_%02d_下回旋纹'%k,INNER,
   [(a+.023,Z0+.047),(a+.108,Z0+.047),(a+.108,Z0+.132),
    (a+.218,Z0+.132),(a+.218,Z1-.059),
    (a+d*.57,Z1-.059),(a+d*.57,Z0+.178),
    (b-.069,Z0+.178),(b-.069,Z0+.072),(b-.024,Z0+.072)],
   YI+.015,.012,'GOLDEN_WOOD')
 fret('内窗花格_%02d_上回纹'%k,INNER,
   [(a+.022,Z1-.035),(a+.078,Z1-.035),(a+.078,Z0+.214),
    (a+.150,Z0+.214),(a+.150,Z1-.122),
    (b-.165,Z1-.122),(b-.165,Z0+.272),
    (b-.029,Z0+.272)],YI+.049,.010,'WOOD_DETAIL')
 # attach upper/lower ends to pre-existing perimeter rails
 vert('内窗花格_%02d_格心落榫'%k,INNER,a+.108,YI+.012,Z0-.034,Z0+.074,.024,.071)
 vert('内窗花格_%02d_顶贯榫'%k,INNER,b-.165,YI+.011,Z1-.052,Z1+.016,.024,.070)
# 3. LARGER WINDOW LATTICE, retain glazing & six larger outer window frames.
WINDOWFRAME='32_实景_木窗外框及压条'
WINDOW='33_实景_花窗方圆格心及角花'
window_sites=[]
for section in (0,1):
 for cell in (0,1,2):
  xx=(.699,1.692,2.686,5.999,6.992,7.986)[section*3+cell]
  width=(1.572,2.566,3.559,6.872,7.866,8.859)[section*3+cell]-xx
  window_sites.append((section,cell,xx,xx+width))
for section,cell,left,right in window_sites:
 label='%s_%s'%(section,cell)
 fxl=left+.034;fxr=right-.034
 zlo=1.006;zhi=2.261;yy=1.260
 # consistent wood outer frame, slim painted bead and visible glazing behind y1.417
 polyframe('窗'+label+'_通长樘框',WINDOWFRAME,fxl,fxr,zlo,zhi,yy,.037)
 polyframe('窗'+label+'_内细银口',WINDOWFRAME,fxl+.039,fxr-.039,zlo+.031,zhi-.031,yy-.015,.016)
 box('窗'+label+'_左边樘接旧框',WINDOWFRAME,left-.110,yy,zlo,left+.061,yy+.139,zhi)
 box('窗'+label+'_右边樘接旧框',WINDOWFRAME,right-.061,yy,zlo,right+.109,yy+.139,zhi)
 # upper & lower frieze repeat in all panes
 for zz in (1.167,2.102):
  horiz('窗%s_贯通横花板_%0.3f'%(label,zz),
    WINDOW,fxl+.014,fxr-.014,yy,zz,.027,.079)
  # give structural geometrical support to openwork
  for edge in (fxl+.071,fxr-.071):
   vert('窗%s_角位接榫_%0.3f_%0.3f'%(label,edge,zz),
        WINDOW,edge,yy,zz-.065,zz+.065,.024,.079)
 center=(fxl+fxr)/2
 width0=fxr-fxl
 if cell==1:
  # Central pane deliberately kept visually clear as real photo;
  # ornamental fret lives near boundary, with broad transparent center.
  for sign in (-1,1):
   xedge=center+sign*(width0/2-.030)
   path=[(xedge,1.308),(xedge-sign*.095,1.308),
         (xedge-sign*.095,1.407),
         (xedge-sign*.183,1.407),
         (xedge-sign*.183,1.872),
         (xedge-sign*.102,1.872),
         (xedge-sign*.102,1.975),(xedge,1.975)]
   fret('中大窗%s_左右步步锦侧边_%s'%(label,sign),WINDOW,path,yy+.012,.014)
  # slim two golden bands at top & bottom to echo facade lattice
  for zz in (1.220,2.054):
   fret('中大窗%s_转角细装饰_%0.3f'%(label,zz),WINDOW,
        [(fxl+.038,zz),(fxl+.142,zz),(fxl+.142,zz+.064),
         (fxr-.143,zz+.064),(fxr-.143,zz),(fxr-.038,zz)],
        yy-.014,.011)
 else:
  # narrower sidelights: a pair of real hollow octagonal medallions
  # and step-shaped framing, not the original square chessboard.
  for j,cz in enumerate((1.485,1.822)):
   rx=.190;rz=.150;bevel=.079
   pg=[(center-rx+bevel,cz-rz),(center+rx-bevel,cz-rz),
       (center+rx,cz-rz+bevel),(center+rx,cz+rz-bevel),
       (center+rx-bevel,cz+rz),(center-rx+bevel,cz+rz),
       (center-rx,cz+rz-bevel),(center-rx,cz-rz+bevel)]
   fret('边窗%s_八角花心_%s'%(label,j),WINDOW,pg+[pg[0]],yy-.015,.018)
   for xend,sg in ((fxl,1),(fxr,-1)):
    fret('边窗%s_八角边通连接_%s_%s'%(label,j,sg),WINDOW,
         [(xend,cz),(xend+sg*.086,cz),(xend+sg*.086,cz+.070),
          (center-sg*rx,cz+.070)],yy-.015,.012)
  for lo,hi in ((1.210,1.275),(2.004,2.078)):
   fret('边窗%s_步步锦上下纹_%0.3f'%(label,lo),WINDOW,
        [(fxl+.032,lo),(center-.150,lo),(center-.150,hi),
         (center+.150,hi),(center+.150,lo),(fxr-.032,lo)],
        yy+.021,.014)
 # decor side frame, overlay rich orthogonal deep-set edge in front of glass
 for x in (fxl+.020,fxr-.020):
  vert('窗%s_棂边竖向阳线_%.3f'%(label,x),WINDOWFRAME,x,yy-.015,zlo,zhi,.016,.018,'WOOD_DETAIL')
# 4. EAVE JOINT SCROLL CARVINGS + diagonal braces under front beam.
# Existing large structural beam V16 remains; all new components physically overlap.
CARVE='34_实景_柱头雀替与卷草纹'
SUP='35_实景_木雕外挑承托与榫卯'
for j,x in enumerate((.639,3.619,5.939,8.919)):
 for sgn in (-1,1):
  if (j==0 and sgn==-1) or (j==3 and sgn==1):continue
  # structural mortise from existing pillar crown into long beam
  box('雀替_%d_%d_上托木'% (j,sgn),SUP,
      min(x+sgn*.064,x+sgn*.390),.137,2.829,
      max(x+sgn*.064,x+sgn*.390),.296,2.927)
  # scroll carved relief on forward exposed wood, arch like leaf shapes
  for depth,radius in ((.115,.016),(.100,.009)):
   xs=[x+sgn*.085,x+sgn*.142,x+sgn*.227,x+sgn*.325]
   path=[(xs[0],.137-depth,2.82),
         (xs[1],.137-depth,2.758),
         (xs[2],.137-depth,2.767),
         (xs[3],.137-depth,2.844)]
   tube('雀替_%d_%d_卷草弧线_%0.3f'%(j,sgn,depth),
        CARVE,path,radius,'GOLDEN_WOOD',10)
  for k in range(3):
   cx=x+sgn*(.181+k*.049)
   tube('雀替_%d_%d_细刻_leaf%d'%(j,sgn,k),CARVE,
        [(cx,.039,2.775),(cx+sgn*.024,.034,2.798),
         (cx+sgn*.044,.032,2.834)],.007,'WOOD_DETAIL',8)
 # decorative cap and upper connector
 box('柱头_%d_木额枋接头托'%j,SUP,
     x-.165,.110,2.827,x+.165,.341,2.970)
 # light geometric carving layers on front:
 for dz in (2.858,2.895,2.936):
  horiz('柱头_%d_额枋横勾_%0.3f'%(j,dz),CARVE,x-.148,x+.148,.091,dz,.014,.022,'WOOD_DETAIL')
# two window and porch structure edges - small crossgrain molding along actual fixed facade
for z,w in ((2.509,.032),(2.951,.038),(3.574,.035)):
 horiz('门窗_实木通长阴阳刻线_%0.3f'%z,SUP,.552,9.026,1.259,z,w,.028,'WOOD_DETAIL')
# Just basic editable reference / not drawn by default
# re-save file and verify preserved essential structural geometry.
if not m.Write(str(TARGET),8):raise IOError('Write Rhino v17 failed')
v=R.File3dm.Read(str(TARGET))
if v is None:raise IOError('Rhino v17 round-trip failed')
objects=list(v.Objects)
invalid=[o.Attributes.Name for o in objects if not o.Geometry.IsValid]
if invalid:raise ValueError('Invalid geometry '+str(invalid[:6]))
ids={str(o.Attributes.Id) for o in objects}
deleted_ids={x[0] for x in obsolete}
if not (srcids-deleted_ids) <= ids: raise ValueError('Unexpected V16 object removed')
layers_after=list(v.Layers)
def find_old_bbox(name):
 match=[o for o in v.Objects if o.Attributes.Name==name]
 if not match:raise ValueError('Missing fixture:'+name)
 return match[0].Geometry.GetBoundingBox()
def contact(bb1,bb2):
 return all(min(getattr(bb1.Max,i),getattr(bb2.Max,i))-max(getattr(bb1.Min,i),getattr(bb2.Min,i))>=-1.
            for i in 'XYZ')
# Determine representative actual connections:
connection_checks=[
 ('挂落上榫-原前额枋',elements['檐廊挂落_通长上沿榫头'],find_old_bbox('BEAM_FRONT_前檐柱列通长额枋')),
 ('挂落下沿-柱位托',elements['檐廊挂落_通长下沿托枋'],elements['檐廊挂落_柱位边缘承托_3.619']),
 ('花格顶-窗顶原梁',elements['内窗花格_00_顶贯榫'],find_old_bbox('LATTICE_FULL_TOP')),
 ('花格底-窗底原梁',elements['内窗花格_00_格心落榫'],find_old_bbox('LATTICE_FULL_BOTTOM')),
 ('木窗四周装饰-原外框',elements['窗0_0_左边樘接旧框'],find_old_bbox('WINDOW_0_0_外框竖边_0.639')),
 ('雀替托-原额枋',elements['柱头_1_木额枋接头托'],find_old_bbox('BEAM_FRONT_前檐柱列通长额枋'))
]
checked=[{"joint":n,"attached_by_bbox":contact(a,b)} for n,a,b in connection_checks]
if not all(c['attached_by_bbox'] for c in checked):raise ValueError('Unattached node checks:'+str(checked))
geom_types=collections.Counter(type(o.Geometry).__name__ for o in objects)
result=dict(
 source=str(SOURCE),result=str(TARGET),source_objects=len(source),
 deprecated_grid_removed=len(obsolete),deprecated_by_layer=dict(collections.Counter(z for _,_,z in obsolete)),
 new_parts=sum(counter.values()),final_objects=len(objects),
 original_essential_objects_preserved=len(srcids-deleted_ids),
 file_size_bytes=TARGET.stat().st_size,layer_count=len(layers_after),
 geometry_invalid=len(invalid),new_parts_by_layer=dict(counter),
 geometry_types=dict(geom_types),connection_checks=checked,
 building_roof_walls_preserved=True,
 dimension_note="Photo based; unmeasured wood dimension/ornament. Model for design visualization, not construction."
)
QA.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
DESC.write_text("""厨房木构 V17 · 实景花格与檐廊挂落精细复原
==================================
Rhino原生：厨房_V17_实景檐廊挂落_精细木窗_Rhino8.3dm
源文件：厨房_V16_双门中柱_悬空修复_Rhino8.3dm（原件保留）
脚本：build_kitchen_V17.py
校验：厨房_V17_几何与连接校验.json
1. 建立檐廊前列上方多开间连续透空步步锦挂落，横竖回转纹样不以实体墙堵塞。
   挂落上下榫枋嵌入既有前额枋，沿柱位加端部收口。
2. 用照片化样式重建门窗顶端横向细木格，移除旧84根过于方直的JIN_格条；
   继续沿用两根长边框及现有12单元格窗的竖框。
3. 六扇侧窗改用内压条、左右边栏八角格心与步步锦转折细线；中央大片
   开敞透明窗洞，保留6块后衬玻璃。旧横竖简化窗棂被选择性剔除，
   窗墙框和下部木裙板保持原结构。
4. 内退檐廊柱头增加连续雀替、卷草纹刻线、承托木、明暗层次线脚。
5. 保留V16中柱、双门、3面砖墙、屋面双坡及尺寸与内凹廊；原装饰吊灯保留
   在隐藏图层14，可在Rhino中打开查看。用户照片中的节庆装饰仍在隐藏图层23。
6. 新图层30-36，主结构对象不变；几何均可单独选择、编辑、替换。
注意：外观参考照片，几何尺寸和古建做法未实测校核；仅限设计表现与后续深化。
""",encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('connection_checks','deprecated_by_layer')},ensure_ascii=False,indent=2))
print('CONTACTS',checked)
