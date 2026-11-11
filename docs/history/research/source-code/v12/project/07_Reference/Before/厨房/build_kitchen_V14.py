# -*- coding: utf-8 -*-
"""Rebuild editable Rhino kitchen model from previously measured Rhino geometry.
Source H: is not connected on this desktop. V14 is a parameterized reconstruction,
not a lossless copy of original V11 meshes. All distances below are METERS.
The .3dm file uses millimeters, so geometry is scaled by 1000 when added.
"""
from pathlib import Path
import math, json, time, collections
import numpy as np
import rhino3dm as R

TARGET=Path(r"E:\CODEXdata")
TARGET.mkdir(parents=True,exist_ok=True)
MODEL=TARGET/"厨房_V14_双坡平分_内凹檐廊_重建.3dm"
NOTES=TARGET/"厨房_V14_模型说明.txt"
PARAMS=TARGET/"厨房_V14_尺寸构件清单.json"
START=time.time()
DIMS={"building_length_m":9.27901,"building_depth_m":5.66357,
      "roof_front_eave_y_m":-.72,"roof_rear_eave_y_m":5.93,
      "roof_ridge_y_m":2.605,"roof_eaves_height_m":2.92,
      "roof_ridge_height_m":4.64,"recessed_facade_y_m":1.40,
      "facade_recess_m":1.40,"roof_left_x_m":-.18,"roof_right_x_m":9.73}
W=DIMS["building_length_m"]
DEPTH=DIMS["building_depth_m"]
YFR=DIMS["roof_front_eave_y_m"]
YBK=DIMS["roof_rear_eave_y_m"]
RIDGE=DIMS["roof_ridge_y_m"]
EAVEZ=DIMS["roof_eaves_height_m"]
RIDGEZ=DIMS["roof_ridge_height_m"]
FACEY=DIMS["recessed_facade_y_m"]
def zroof(y):
    return EAVEZ+(RIDGEZ-EAVEZ)*((y-YFR)/(RIDGE-YFR) if y<=RIDGE else (YBK-y)/(YBK-RIDGE))
m=R.File3dm()
m.Settings.ModelUnitSystem=R.UnitSystem.Millimeters
m.Settings.ModelAbsoluteTolerance=1.0
try:m.Settings.ModelAngleToleranceRadians=math.pi/180
except Exception:pass
layers={}
materials={}
stats=collections.Counter()
measurements={}
def layer(code,name,color):
    lyr=R.Layer()
    lyr.Name=f"{code}_{name}"
    lyr.Color=(*color,255)
    layers[code]=m.Layers.Add(lyr)
    return layers[code]
def material(name,color,transp=0):
    mat=R.Material()
    mat.Name=name
    mat.DiffuseColor=(*color,255)
    mat.Transparency=transp
    materials[name]=m.Materials.Add(mat)
layer("00","基座_室内外地坪",(159,157,148))
layer("01","三面砖墙_实体",(135,137,135))
layer("02","灰砖错缝细节",(95,98,98))
layer("03","檐廊木柱石柱础",(182,115,63))
layer("04","木构梁枋檩椽",(145,89,46))
layer("05","内退木门_实体与雕花",(172,102,49))
layer("06","内退花格窗_下裙板",(192,124,62))
layer("07","格窗玻璃_可隐藏",(157,185,193))
layer("08","檐廊石材铺地",(175,172,161))
layer("09","双坡灰瓦屋面基层",(91,96,98))
layer("10","双坡筒瓦_可编辑瓦列",(113,118,121))
layer("11","瓦当与屋脊",(72,76,78))
layer("12","檐口封板与金属收边",(107,111,114))
layer("13","木构雀替和节点",(178,114,58))
layer("14","廊下仿古吊灯_可隐藏",(92,85,78))
layer("99","辅助标注与轴线_可隐藏",(95,96,96))
for name,color,opacity in [
 ("STONE_FOUNDATION",(121,123,120),0),
 ("STONE_PAVING",(164,163,151),0),
 ("STONE_THRESHOLD",(108,108,105),0),
 ("GRAY_BRICK",(131,133,131),0),
 ("BRICK_MORTAR",(98,101,102),0),
 ("HONEY_WOOD",(181,115,60),0),
 ("GOLDEN_WOOD",(204,139,70),0),
 ("WOOD_DARK",(122,75,39),0),
 ("GLASS_PALE",(133,183,196),.67),
 ("GRAY_TILE_BASE",(82,87,88),0),
 ("GRAY_TILE_LIGHT",(118,123,124),0),
 ("GRAY_TILE_MID",(104,109,112),0),
 ("GRAY_TILE_DARK",(83,89,93),0),
 ("RIDGE",(69,74,77),0),
 ("METAL",(160,164,166),0),
 ("LAMP_GLOW",(240,222,173),.20),
 ("LAMP_FRAME",(47,45,40),0),
 ]:
    material(name,color,opacity)
def attr(name,l,mat=None):
    a=R.ObjectAttributes()
    a.Name=name
    a.LayerIndex=layers[l]
    if mat is not None:
        a.MaterialIndex=materials[mat]
        a.MaterialSource=R.ObjectMaterialSource.MaterialFromObject
    return a
def P(x,y,z):
    return R.Point3d(float(x)*1000,float(y)*1000,float(z)*1000)
def box(name,lyr,mat,x0,y0,z0,x1,y1,z1):
    if not(x1>x0 and y1>y0 and z1>z0):
        raise ValueError(("bad box",name,x0,y0,z0,x1,y1,z1))
    b=R.Brep.CreateFromBoundingBox(R.BoundingBox(P(x0,y0,z0),P(x1,y1,z1)))
    assert b is not None
    m.Objects.AddBrep(b,attr(name,lyr,mat))
    stats[lyr]+=1
def mesh(name,lyr,mat,vertices,faces):
    g=R.Mesh()
    for a,b,c in vertices:g.Vertices.Add(float(a)*1000,float(b)*1000,float(c)*1000)
    for face in faces:
        if len(face)==3:g.Faces.AddFace(*map(int,face))
        elif len(face)==4:g.Faces.AddFace(*map(int,face))
    if not len(g.Vertices) or not len(g.Faces):
        raise RuntimeError("mesh empty "+name)
    try:g.Normals.ComputeNormals()
    except Exception:pass
    m.Objects.AddMesh(g,attr(name,lyr,mat))
    stats[lyr]+=1
def axisbeam(name,lyr,mat,start,end,width,height):
    a=np.array(start,float);b=np.array(end,float)
    v=b-a
    mag=np.linalg.norm(v)
    if mag<1e-8:return
    along=v/mag
    side=np.cross(along,[0,0,1])
    if np.linalg.norm(side)<1e-6:side=np.cross(along,[0,1,0])
    side/=np.linalg.norm(side)
    up=np.cross(along,side);up/=np.linalg.norm(up)
    verts=[]
    for endpt in (a,b):
        for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            verts.append(endpt+side*(width*s*.5)+up*(height*t*.5))
    tris=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),
          (0,1,5),(0,5,4),(1,2,6),(1,6,5),
          (2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    mesh(name,lyr,mat,verts,tris)
def prism_yz(name,lyr,mat,x0,x1,polygon):
    n=len(polygon)
    verts=[(x,y,z) for x in [x0,x1] for y,z in polygon]
    faces=[]
    for j in range(1,n-1):
        faces.append((0,j+1,j))
        faces.append((n,n+j,n+j+1))
    for j in range(n):
        k=(j+1)%n
        faces.extend([(j,k,n+k),(j,n+k,n+j)])
    mesh(name,lyr,mat,verts,faces)
def profile_prism_x(name,lyr,mat,x0,x1,polygon):
    prism_yz(name,lyr,mat,x0,x1,polygon)
def line(name,lyr,mat,aa,bb):
    m.Objects.AddLine(P(*aa),P(*bb),attr(name,lyr,mat))
    stats[lyr]+=1
def column(name,lyr,mat,x,y,z0,z1,r=.115,n=16):
    vertices=[]
    for z in [z0,z1]:
        for k in range(n):
            t=2*math.pi*k/n
            vertices.append((x+r*math.cos(t),y+r*math.sin(t),z))
    vertices.extend([(x,y,z0),(x,y,z1)])
    triangles=[]
    for k in range(n):
        nxt=(k+1)%n
        triangles.extend([(k,n+k,n+nxt),(k,n+nxt,nxt),
                          (2*n,k,nxt),(2*n+1,n+nxt,n+k)])
    mesh(name,lyr,mat,vertices,triangles)
def tile_row(name,lyr,mat,x,ya,yb,pieces=9,radius=.084):
    # Eight curved longitudinal strips in one independently editable Rhino mesh.
    num_u=11
    per_piece=4
    verts=[];faces=[]
    for pc in range(pieces):
        A=ya+(yb-ya)*pc/pieces
        B=ya+(yb-ya)*(pc+1)/pieces
        for j in range(per_piece+1):
            y=A+(B-A)*j/per_piece
            for k in range(num_u+1):
                theta=math.pi*k/num_u
                dx=radius*math.cos(theta)
                dz=radius*.75*math.sin(theta)
                verts.append((x+dx,y,zroof(y)+.035+dz+pc*.001))
        off=pc*(per_piece+1)*(num_u+1)
        for j in range(per_piece):
            for k in range(num_u):
                v=off+j*(num_u+1)+k
                faces.extend([(v,v+num_u+1,v+num_u+2),(v,v+num_u+2,v+1)])
    mesh(name,lyr,mat,verts,faces)
def half_tile_medallions(name,lyr,mat,coords,r=.066):
    verts=[];faces=[];steps=14
    for (x,y,z) in coords:
        st=len(verts)
        verts.append((x,y-.015,z))
        for rr in [r,.64*r,.24*r]:
            for k in range(steps):
                a=2*math.pi*k/steps
                verts.append((x+rr*math.cos(a),y,z+rr*math.sin(a)))
        for k in range(steps):
            j=(k+1)%steps
            faces.extend([(st+1+k,st+1+j,st+1+steps+j),(st+1+k,st+1+steps+j,st+1+steps+k)])
            faces.extend([(st+1+steps+k,st+1+steps+j,st+1+2*steps+j),(st+1+steps+k,st+1+2*steps+j,st+1+2*steps+k)])
            faces.append((st,st+1+2*steps+j,st+1+2*steps+k))
    mesh(name,lyr,mat,verts,faces)

# A) EXISTING FOOTPRINT, original whole-house floor unaffected by corridor recession.
box("BASE_01_地基整板_9279x5664mm","00","STONE_FOUNDATION",0,0,-.25,W,DEPTH,-.025)
box("BASE_02_室内地坪", "00","STONE_PAVING",.24,1.40,-.025,W-.24,DEPTH-.24,0)
box("BASE_03_檐下廊道石地坪","08","STONE_PAVING",.24,.02,-.02,W-.24,1.40,.013)
box("BASE_04_内退门窗门槛石", "08","STONE_THRESHOLD",.58,1.347,.013,8.98,1.485,.070)
# parallel paving stone joints on corridor
for i in range(13):
    x=.29+i*(W-.6)/12
    line(f"CORRIDOR_PAVING_JOINT_{i:02d}","08","STONE_THRESHOLD",(x,.035,.018),(x,1.34,.018))
for i,y in enumerate([.48,.91,1.29]):
    line(f"CORRIDOR_TRANSVERSE_JOINT_{i}","08","STONE_THRESHOLD",(.30,y,.018),(W-.30,y,.018))
# Raised edge remains within original footprint; no exterior patio additions.
box("BASE_05_原前沿地坪压边","08","STONE_THRESHOLD",.08,.01,-.025,W-.08,.105,.022)

# B) Three gray masonry walls: LEFT, RIGHT gable sides; REAR back wall.
# Solid base masonry bodies are fully selectable and editable Breps.
for title,x0,x1 in [("LEFT",.02,.26),("RIGHT",W-.26,W-.02)]:
    box(f"WALL_{title}_低段灰砖实体","01","GRAY_BRICK",x0,.025,.001,x1,DEPTH-.02,2.72)
    gable=[
        (.025,2.72),(.025,zroof(.025)-.18),
        (RIDGE,RIDGEZ-.18),(DEPTH-.03,zroof(DEPTH-.03)-.18),
        (DEPTH-.03,2.72)
    ]
    profile_prism_x(f"WALL_{title}_顶部双坡灰砖山墙","01","GRAY_BRICK",x0,x1,gable)
box("WALL_REAR_后墙实体","01","GRAY_BRICK",.26,DEPTH-.255,0,W-.26,DEPTH-.025,2.95)
# Visible courses on two side walls and rear wall, not just a grey color sheet.
for ci in range(1,23):
    z=.125*ci
    for x in [.014,.269,W-.268,W-.014]:
        line(f"MORTAR_SIDE_z{ci:02d}_x{round(x,3)}","02","BRICK_MORTAR",
             (x,.04,z),(x,DEPTH-.04,z))
    line(f"MORTAR_REAR_z{ci:02d}","02","BRICK_MORTAR",
         (.29,DEPTH-.267,z),(W-.29,DEPTH-.267,z))
for i in range(13):
    x=.28+i*.68
    if x>=W-.29:break
    for zlo in [.0,.25,.5,.75,1.0,1.25,1.5,1.75,2.0,2.25,2.5]:
        sx=x+(.34 if int(zlo/.25)%2 else 0)
        if sx<W-.3:
            line(f"BRICK_VJOINT_{i}_{round(zlo,2)}","02","BRICK_MORTAR",
                 (sx,DEPTH-.268,zlo+.009),(sx,DEPTH-.268,zlo+.114))

# C) Front post-line stays fixed at existing exterior wooden front plane y~0.
post_x=[.639,3.619,5.939,8.919]
for i,x in enumerate(post_x):
    box(f"POST_{i+1:02d}_石柱础","03","STONE_FOUNDATION",x-.183,.015,.015,x+.183,.38,.24)
    box(f"POST_{i+1:02d}_木方柱","03","HONEY_WOOD",x-.112,.075,.24,x+.112,.31,2.75)
    box(f"POST_{i+1:02d}_木柱脚端箍","03","WOOD_DARK",x-.135,.053,.235,x+.135,.335,.310)
    box(f"POST_{i+1:02d}_木柱头承枋","03","GOLDEN_WOOD",x-.18,.034,2.69,x+.18,.355,2.805)
    for side in [-1,1]:
        axisbeam(f"BRACKET_{i+1:02d}_{side:+d}_雀替","13","GOLDEN_WOOD",
            (x,.18,2.49),(x+side*.42,.18,2.72),.095,.115)
# Long front and recessed facade lintel beams; two interfaces make corridor real.
box("BEAM_FRONT_前檐柱列通长额枋","04","HONEY_WOOD",.51,.045,2.745,9.045,.36,2.895)
box("BEAM_FRONT_上压枋","04","WOOD_DARK",.52,.04,2.883,9.045,.345,2.955)

# D) 1.4m-INWARD timber frontage; all doors/windows are physically at y=1.4.
# Carefully retained 2 banks of 3 lattice windows and 2 wooden doors.
def facade_beam(name,x0,x1,z0,z1,depth=.115,mat="HONEY_WOOD"):
    box(name,"06" if 'WINDOW' in name or 'SKIRT' in name else "05",mat,
        x0,FACEY-depth/2,z0,x1,FACEY+depth/2,z1)
for i,x in enumerate([.639,3.619,4.939,5.939,8.919]):
    if i!=2:
        box(f"FRONT_FACADE_FRAME_VERTICAL_{i:02d}","06","HONEY_WOOD",
            x-.038,FACEY-.085,0,x+.038,FACEY+.085,2.90)
# Two skirts under 6 windows
for i,(x0,x1) in enumerate([(.639,3.619),(5.939,8.919)]):
    box(f"SKIRT_{i+1:02d}_窗下整幅木裙板","06","HONEY_WOOD",x0,FACEY-.083,0,x1,FACEY+.07,.945)
    for c in range(7):
        xx=x0+(x1-x0)*(c+.5)/7
        box(f"SKIRT_{i+1:02d}_装饰竖槽_{c:02d}","06","WOOD_DARK",
            xx-.008,FACEY-.095,.12,xx+.008,FACEY-.084,.88)
    facade_beam(f"WINDOW_{i+1:02d}_窗下槛",x0,x1,.925,.985,.15)
    facade_beam(f"WINDOW_{i+1:02d}_窗上槛",x0,x1,2.27,2.34,.15)
    for j in range(3):
        a=x0+(x1-x0)*j/3
        b=x0+(x1-x0)*(j+1)/3
        box(f"GLASS_{i}_{j}_后衬玻璃","07","GLASS_PALE",a+.06,FACEY+.017,1.03,b-.06,FACEY+.032,2.24)
        for k in range(5):
            xx=a+.09+(b-a-.18)*k/4
            box(f"WINDOW_{i}_{j}_木格竖棂_{k}","06","GOLDEN_WOOD",
                xx-.017,FACEY-.114,1.0,xx+.017,FACEY-.035,2.31)
        for k in range(4):
            zz=1.06+k*.39
            box(f"WINDOW_{i}_{j}_木格横棂_{k}","06","GOLDEN_WOOD",
                a+.05,FACEY-.121,zz-.016,b-.05,FACEY-.025,zz+.016)
        for xx in [a,b]:
            box(f"WINDOW_{i}_{j}_外框竖边_{xx:.3f}","06","HONEY_WOOD",
                xx-.033,FACEY-.12,.96,xx+.033,FACEY+.07,2.34)

# Two actual wooden hinged leaf door groups (base panels + windows + stiles + hardware).
doors=[(3.659,4.619),(4.939,5.899)]
for i,(a,b) in enumerate(doors):
    box(f"DOOR_{i+1}_框左挺","05","HONEY_WOOD",a-.042,FACEY-.11,0,a+.043,FACEY+.092,2.36)
    box(f"DOOR_{i+1}_框右挺","05","HONEY_WOOD",b-.043,FACEY-.11,0,b+.042,FACEY+.092,2.36)
    box(f"DOOR_{i+1}_框顶枋","05","HONEY_WOOD",a,FACEY-.11,2.28,b,FACEY+.09,2.37)
    box(f"DOOR_{i+1}_下部实木门板","05","GOLDEN_WOOD",a+.05,FACEY-.044,.028,b-.05,FACEY+.033,.99)
    box(f"DOOR_{i+1}_上部木芯板","05","HONEY_WOOD",a+.054,FACEY-.038,1.03,b-.054,FACEY+.033,2.285)
    for k in range(4):
        xx=a+.095+(b-a-.19)*k/3
        box(f"DOOR_{i+1}_上部格棂竖_{k}","05","WOOD_DARK",
            xx-.017,FACEY-.052,1.03,xx+.017,FACEY-.043,2.27)
    for k in range(3):
        z=1.29+.33*k
        box(f"DOOR_{i+1}_上部格棂横_{k}","05","WOOD_DARK",
            a+.070,FACEY-.055,z-.017,b-.07,FACEY-.042,z+.017)
    box(f"DOOR_{i+1}_腰枋","05","HONEY_WOOD",a+.04,FACEY-.073,.96,b-.04,FACEY+.062,1.043)
    box(f"DOOR_{i+1}_青铜拉手","05","WOOD_DARK",
        b-.12 if i==0 else a+.09,FACEY-.115,1.19,
        b-.09 if i==0 else a+.12,FACEY-.075,1.35)
# Fixed upper transom: 8 wooden lattice bays.
box("FRONT_TOP_TRANSOM_通长下横枋","06","HONEY_WOOD",.639,FACEY-.10,2.47,8.919,FACEY+.095,2.54)
box("FRONT_TOP_TRANSOM_通长上横枋","06","HONEY_WOOD",.639,FACEY-.10,2.83,8.919,FACEY+.095,2.925)
for k in range(8):
    a=.639+(8.919-.639)*k/8
    b=.639+(8.919-.639)*(k+1)/8
    box(f"GLASS_TRANSOM_{k:02d}","07","GLASS_PALE",a+.041,FACEY+.03,2.555,b-.041,FACEY+.047,2.815)
    for s in range(1,5):
        xx=a+(b-a)*s/5
        box(f"TRANSOM_{k:02d}_竖格_{s}","06","HONEY_WOOD",
            xx-.015,FACEY-.107,2.515,xx+.015,FACEY+.018,2.867)
    box(f"TRANSOM_{k:02d}_中横棂","06","HONEY_WOOD",
        a+.045,FACEY-.111,2.70,b-.045,FACEY+.02,2.727)
    box(f"TRANSOM_{k:02d}_立边","06","HONEY_WOOD",
        a-.026,FACEY-.11,2.49,a+.026,FACEY+.092,2.89)
box("INNER_HEADER_内退门窗上部结构横梁","04","HONEY_WOOD",
    .52,FACEY-.16,2.91,9.03,FACEY+.17,3.055)
# Notice front beam and facade remain two independent layers, with empty corridor between.
for i,x in enumerate(post_x):
    # Eave-passage purlin runs from front row to recessed interior frame
    axisbeam(f"CORRIDOR_BRACING_{i+1:02d}_前后连接梁","04","HONEY_WOOD",
        (x,.20,2.88),(x,FACEY,3.55),.14,.17)
    axisbeam(f"CORRIDOR_SPANDREL_{i+1:02d}_柱头斜撑","13","GOLDEN_WOOD",
        (x,.25,2.61),(x,.63,3.10),.105,.125)
# A line of backing timber posts immediately at recessed facade, no wall partitions inside kitchen
for i,x in enumerate([.639,3.619,5.939,8.919]):
    box(f"INNER_POST_{i+1:02d}_内退立面承梁柱","04","HONEY_WOOD",
        x-.085,FACEY-.09,2.45,x+.085,FACEY+.115,3.35)

# E) A single near-perfectly equal double-pitch roof. No added patio or eave projection.
left=-.18;right=9.73
def roof_solid(name,ya,yb,mat):
    za=zroof(ya);zb=zroof(yb)
    poly=[(ya,za-.09),(yb,zb-.09),(yb,zb),(ya,za)]
    prism_yz(name,"09",mat,left,right,poly)
roof_solid("ROOF_FRONT_前坡屋面基层_3325mm",YFR,RIDGE,"GRAY_TILE_BASE")
roof_solid("ROOF_REAR_后坡屋面基层_3325mm",RIDGE,YBK,"GRAY_TILE_BASE")
# Roof tiles follow the SAME two slopes; rows parallel to Y, not independent uneven roofs.
tilecoords=[]
xvals=np.arange(-.07,9.70,.268)
for k,x in enumerate(xvals):
    x=float(x)
    frontmat="GRAY_TILE_LIGHT" if k%4==0 else "GRAY_TILE_MID"
    rearmat="GRAY_TILE_LIGHT" if k%5==0 else "GRAY_TILE_MID"
    tile_row(f"TILE_FRONT_COLUMN_{k+1:02d}","10",frontmat,x,YFR+.012,RIDGE-.045,pieces=8)
    tile_row(f"TILE_REAR_COLUMN_{k+1:02d}","10",rearmat,x,YBK-.012,RIDGE+.045,pieces=8)
    tilecoords.append((x,YFR-.018,EAVEZ+.035))
    tilecoords.append((x,YBK+.015,EAVEZ+.035))
half_tile_medallions("ROOF_FRONT_AND_REAR_瓦当端部圆饰","11","RIDGE",tilecoords)
# Ridge caps separate tiny cylindrical tiles, similarly editable per unit
for k,x in enumerate(np.arange(left+.15,right-.15,.32)):
    xa=float(x);xb=min(xa+.30,right-.05)
    box(f"RIDGE_CROWN_{k+1:02d}_灰瓦屋脊盖瓦","11","RIDGE",
        xa,RIDGE-.112,RIDGEZ+.012,xb,RIDGE+.112,RIDGEZ+.105)
box("RIDGE_通长屋脊贯通木托","11","WOOD_DARK",
    left+.06,RIDGE-.12,RIDGEZ-.10,right-.06,RIDGE+.12,RIDGEZ+.008)
# End decorative ridge disks at both gables (simple proxy for traditional ornate caps)
for i,x in enumerate([left+.16,right-.16]):
    column(f"RIDGE_END_{i+1:02d}_装饰脊兽简化","11","RIDGE",
        x,RIDGE,RIDGEZ+.03,RIDGEZ+.31,.12,20)

# F) Exposed sloping timber framing under BOTH roof pitches, plus front/rear fascia and gutters.
for i,x in enumerate(np.arange(.24,W-.14,.55)):
    axisbeam(f"RAFTER_FRONT_{i+1:02d}_前坡椽","04","WOOD_DARK",
        (x,YFR+.085,zroof(YFR+.085)-.16),
        (x,RIDGE,zroof(RIDGE)-.16),.092,.13)
    axisbeam(f"RAFTER_REAR_{i+1:02d}_后坡椽","04","WOOD_DARK",
        (x,RIDGE,zroof(RIDGE)-.16),
        (x,YBK-.10,zroof(YBK-.10)-.16),.092,.13)
for i,y in enumerate([-.25,.95,RIDGE,4.08,5.46]):
    z=zroof(y)-.21
    box(f"PURLIN_{i+1:02d}_木檩条","04","HONEY_WOOD",
        .06,y-.09,z-.10,W-.06,y+.09,z+.105)
box("EAVE_FRONT_木檐口封板","12","WOOD_DARK",
    left,YFR-.013,EAVEZ-.16,right,YFR+.075,EAVEZ+.035)
box("EAVE_REAR_木檐口封板","12","WOOD_DARK",
    left,YBK-.080,EAVEZ-.16,right,YBK+.011,EAVEZ+.035)
for side,y in [("FRONT",YFR-.055),("REAR",YBK+.055)]:
    box(f"METAL_{side}_檐口通长金属滴水","12","METAL",
        left-.015,y-.015,EAVEZ-.092,right+.015,y+.012,EAVEZ-.055)
for side,x in [("LEFT",left),("RIGHT",right)]:
    axisbeam(f"GABLE_{side}_山墙前坡封山木","12","WOOD_DARK",
        (x,YFR,EAVEZ-.055),(x,RIDGE,RIDGEZ-.085),.115,.20)
    axisbeam(f"GABLE_{side}_山墙后坡封山木","12","WOOD_DARK",
        (x,RIDGE,RIDGEZ-.085),(x,YBK,EAVEZ-.055),.115,.20)

# G) Optional pendant lanterns hanging within the EXISTING eave corridor.
for i,x in enumerate([1.13,7.94]):
    y=.33
    column(f"LANTERN_{i+1}_吊链","14","LAMP_FRAME",x,y,2.22,2.78,.013,10)
    box(f"LANTERN_{i+1}_暖光灯罩","14","LAMP_GLOW",
        x-.11,y-.10,1.78,x+.11,y+.10,2.20)
    for dx in [-.13,.13]:
        for dy in [-.11,.11]:
            box(f"LANTERN_{i+1}_黑色灯罩框架_{dx:.2f}_{dy:.2f}",
                "14","LAMP_FRAME",x+dx-.012,y+dy-.012,1.76,
                x+dx+.012,y+dy+.012,2.23)
    box(f"LANTERN_{i+1}_灯顶","14","LAMP_FRAME",
        x-.15,y-.13,2.20,x+.15,y+.13,2.25)

# H) Nonrendering model information and accurate layout references in the file.
for label,xyz in [
    ("模型重建版：源H盘当前不可访问，部分细部按照片推定",(-.9,-1.18,1.1)),
    ("厨房室外尺寸 9279×5664 mm；双坡投影 3325+3325 mm",(-.9,-1.18,.83)),
    ("檐廊内凹 1400 mm；屋檐未外扩",(-.9,-1.18,.58))]:
    dot=R.TextDot(label,P(*xyz))
    m.Objects.AddTextDot(label,P(*xyz),attr("NOTE_"+label[:8],"99",None))
    stats["99"]+=1

ok=m.Write(str(MODEL),8)
if not ok:raise RuntimeError("Rhino .3dm file write failed")
elapsed=round(time.time()-START,2)
params={
    "model_name":MODEL.name,
    "model_kind":"尺寸约束的建筑重建模型；非 Rhino 原文件的无损修改版",
    "units":"millimeters",
    "source_of_major_dimensions":"从 H:\\处理\\Reality_Hybrid_V11.3dm 曾提取并在此前对话确认的尺寸",
    "measurements_m":DIMS,
    "roof_front_horizontal_run_m":RIDGE-YFR,
    "roof_rear_horizontal_run_m":YBK-RIDGE,
    "roof_pitch_degrees":round(math.degrees(math.atan((RIDGEZ-EAVEZ)/(RIDGE-YFR))),3),
    "corridor": {"front_post_row_y_m":.2,"recessed_facade_y_m":FACEY,"is_exterior_extension":False},
    "construction": {"three_side_brick_walls":True,"no_interior_partitions":True,
                     "original_footprint_preserved":True,"original_3dm_not_available":True,
                     "doors_recessed":True,"balanced_gabled_roof":True},
    "objects_by_layer":dict(stats),
    "object_count":sum(stats.values()),
    "generated_on":time.strftime("%Y-%m-%d %H:%M:%S"),
    "build_elapsed_sec":elapsed,
    "caveat":"屋架、墙厚、门窗雕花、铺地及装饰灯仅参考图片建模；不得作为施工放样或结构设计依据。"
}
PARAMS.write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding="utf-8")
NOTES.write_text(
    "厨房 Rhino V14 | 双坡平分 + 内凹檐廊（可编辑3dm）\n\n"
    "文件："+str(MODEL)+"\n"
    "几何单位：mm。外部地坪平面尺寸：9279.01 mm × 5663.57 mm。\n"
    "屋面前檐 Y=-720mm，后檐 Y=5930mm，屋脊 Y=2605mm。前后坡水平投影均为 3325mm。\n"
    "屋顶屋檐标高 2920mm，屋脊标高 4640mm（装饰瓦可更高），屋顶两坡倾角近似相同。\n"
    "内凹门窗立面 Y=1400mm；木柱列在 Y≈200mm，保留原建筑屋檐和基础轮廓。\n"
    "三面砖墙围合，不设内隔墙；内外两道木构界面之间是真实通行廊道。\n"
    "墙体、木裙板、门扇、格棂、木枋等为可独立选择的实体，坡屋面、筒瓦、檩椽包含可编辑网格。\n"
    "屋面两坡、门窗与檐廊、砖墙、木构节点、玻璃、灯笼均分别归入带有中文名称的图层。\n"
    "注意：由于当前计算机无法访问源 H 盘，此文件是依据先前取得的尺寸和你提供的照片重建，"
    "不是源 Rhino 几何的完整逐构件复制；未进行现场测绘或结构校核。\n"
    "要进一步提高准确性，建议将源 3dm/SKP 与新的重建模型在 Rhino 中重合检查。\n",
    encoding="utf-8"
)
# Immediate read-back validation
rr=R.File3dm.Read(str(MODEL))
if rr is None:raise RuntimeError("Re-read returned None")
all_objects=list(rr.Objects)
all_layers=list(rr.Layers)
types=collections.Counter(str(o.Geometry.ObjectType) for o in all_objects)
if len(all_objects)!=sum(stats.values()):raise RuntimeError("Mismatch in object counts")
if len(all_layers)!=len(layers):raise RuntimeError("Mismatch in layers")
if rr.Settings.ModelUnitSystem!=R.UnitSystem.Millimeters:raise RuntimeError("Wrong units")
print("FILE",MODEL,flush=True)
print("BYTES",MODEL.stat().st_size,"LAYERS",len(all_layers),"OBJECTS",len(all_objects),flush=True)
print("TYPES",dict(types),"ROOF_RUNS",RIDGE-YFR,YBK-RIDGE,flush=True)
print("OUTPUT",NOTES,PARAMS,"ELAPSED",elapsed,flush=True)
