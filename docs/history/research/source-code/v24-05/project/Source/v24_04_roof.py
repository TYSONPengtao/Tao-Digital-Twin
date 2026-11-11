"""V24.03 native six-surface xieshan roof replacement, with closed stepped eaves.
Coordinates use the established LOCAL scene metres. No file load/save or shaders changed.
"""
import math,json
from pathlib import Path

CX,CY=6.6,-11.90
A,B=2.22,1.30
IA,IB=1.62,.55
EAVE,SHOULDER,RIDGE=2.94,3.12,3.38
BEARING_DEPTH_SCALE=1.30/.69
def fitted_bearing_z(z):
 """Retain pier/ceiling bearing while deepening the measured layered eave."""
 if z<2.538:return z
 if z<=2.88:return 2.538+(z-2.538)*(EAVE-2.538)/(2.88-2.538)
 return EAVE+(z-2.88)

def apply_v24_xieshan_roof(bpy,report_dir):
 import bmesh
 from mathutils import Vector,Matrix
 out=Path(report_dir);out.mkdir(parents=True,exist_ok=True)
 if any(o.name.startswith('V24_XIESHAN_') for o in bpy.data.objects):raise RuntimeError('Xieshan already applied')
 old=[]
 for ob in list(bpy.data.objects):
  if ob.type!='MESH':continue
  n=ob.name
  exact=n in ['SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT_Geometry','GATE_V22_EMBOSSED_TILE_END_CAPS_Geometry']
  layer=any(n.startswith('SITE_V21_GATE_REFERENCE_LAYER_%02d_'%i) for i in range(9,16))
  extra=n.startswith('V24_GATE_')
  if exact or layer or extra:old.append(n)
 mats={n:bpy.data.materials[n] for n in ['M_V21_GATE_REF_09','M_V21_GATE_REF_11','M_V21_GATE_REF_12','M_V21_GATE_REF_13','M_V21_GATE_REF_14','M_V21_GATE_CLOSED_PALE_SOFFIT']}
 tiles=[bpy.data.materials['M_V23_Gate_Tile_%02d'%i] for i in range(5)]
 for n in old:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 collection=bpy.data.collections.new('V24_04_歇山屋顶_轻薄分层');bpy.context.scene.collection.children.link(collection)
 parent=bpy.data.objects.get('SITE_V21_GATE_REFERENCE_LAYER_09')
 report=[];groups={}
 def group(n,material):
  groups[n]=[[],[],material];return groups[n]
 def append(g,vs,fs):
  V,F,M=g;k=len(V);V.extend(vs);F.extend([[k+i for i in f]for f in fs])
 def box(g,x0,x1,y0,y1,z0,z1):
  append(g,[(x,y,z)for z in [z0,z1]for y in [y0,y1]for x in [x0,x1]],[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]])
 def solidgrid(g,nu,nv,point,thickness):
  vs=[]
  for k in [0,1]:
   for j in range(nv+1):
    for i in range(nu+1):
     q=point(i/nu,j/nv);vs.append((q[0],q[1],q[2]-(1-k)*thickness))
  nn=(nu+1)*(nv+1);fs=[]
  for j in range(nv):
   for i in range(nu):
    a=j*(nu+1)+i;b=a+1;c=b+nu+1;d=a+nu+1
    fs.extend([[a,d,c,b],[a+nn,b+nn,c+nn,d+nn]])
  bd=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+i for i in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
  fs.extend([[a,b,b+nn,a+nn]for a,b in zip(bd,bd[1:]+bd[:1])]);append(g,vs,fs)
 def prism(g,poly,axis,lo,hi):
  vs=[]
  for t in [lo,hi]:
   for a,b in poly:
    vs.append((t,a,b)if axis==0 else(a,t,b)if axis==1 else(a,b,t))
  n=len(poly);fs=[list(range(n-1,-1,-1)),list(range(n,n*2))]
  fs.extend([[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]);append(g,vs,fs)
 def tube(g,path,radius,sides=10):
  vs=[]
  for j,p in enumerate(path):
   p=Vector(p);t=Vector(path[min(j+1,len(path)-1)])-Vector(path[max(0,j-1)])
   t.normalize();h=t.cross(Vector((0,0,1)))
   if h.length<.01:h=t.cross(Vector((0,1,0)))
   h.normalize();k=t.cross(h).normalized();r=radius(j/(len(path)-1))if callable(radius)else radius
   for i in range(sides):vs.append(tuple(p+r*(h*math.cos(i*math.tau/sides)+k*math.sin(i*math.tau/sides))))
  fs=[list(range(sides-1,-1,-1)),list(range((len(path)-1)*sides,len(path)*sides))]
  for j in range(len(path)-1):
   for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;fs.append([a,b,b+sides,a+sides])
  append(g,vs,fs)
 def beam(g,p,q,w,d):
  p,q=Vector(p),Vector(q);t=(q-p).normalized();u=t.cross(Vector((0,0,1)))
  if u.length<.01:u=t.cross(Vector((0,1,0)))
  u.normalize();v=t.cross(u).normalized();vs=[]
  for a in [p,q]:
   for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]:vs.append(tuple(a+u*w*.5*su+v*d*.5*sv))
  append(g,vs,[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
 def lower(side,u,t):
  # Inner shoulder to the swept four-sided lower hip eave. Four corner lines coincide.
  s=u*2-1;rise=.15*abs(s)**5
  z=SHOULDER+(EAVE-SHOULDER)*t+.055*(t*t-t)+rise*t**3
  if side in [0,1]:
   y=CY+(-1 if side==0 else 1)*(IB+(B-IB)*t);x=CX+s*(IA+(A-IA)*t)
  else:
   x=CX+(-1 if side==2 else 1)*(IA+(A-IA)*t);y=CY+s*(IB+(B-IB)*t)
  return x,y,z
 def upper(side,u,t):
  return CX+(u*2-1)*IA,CY+(-1 if side==0 else 1)*IB*t,RIDGE-(RIDGE-SHOULDER)*(t**.90)
 roof=group('01_Upper_Two_Main_Slopes',mats['M_V21_GATE_REF_09'])
 for side in [0,1]:solidgrid(roof,64,12,lambda u,t,s=side:upper(s,u,t),.047)
 lowerg=group('02_Four_Lower_Hipped_Eaves',mats['M_V21_GATE_REF_09'])
 for side in range(4):solidgrid(lowerg,64 if side<2 else 16,14,lambda u,t,s=side:lower(s,u,t),.055)
 # The two vertical triangular gables are the defining xieshan upper/end transition.
 gables=group('03_Two_Upper_Gable_Tympana',mats['M_V21_GATE_CLOSED_PALE_SOFFIT'])
 for s in [-1,1]:
  x=CX+s*IA;prism(gables,[(CY-IB,SHOULDER-.035),(CY+IB,SHOULDER-.035),(CY,RIDGE-.025)],0,x-.035,x+.035)
 # Actual overlapping ceramic pan and cover units, not an unbroken corrugated plane.
 ceramic=[group('04_Ceramic_%02d'%i,tiles[i])for i in range(5)]
 count=0
 def tileunit(surf,u0,u1,t0,t1,kind,matid):
  nonlocal count
  def point(u,t):
   uu=u0+(u1-u0)*u;tt=t0+(t1-t0)*t;x,y,z=surf(uu,tt)
   profile=.030*math.sin(math.pi*u) if kind=='cover' else .010*(2*u-1)**2
   return x,y,z+.009+profile+.002*(1-t)
  solidgrid(ceramic[matid%5],10 if kind=='cover'else 6,5,point,.011);count+=1
 for side in range(4):
  lanes=36 if side<2 else 12;surf=lambda u,t,s=side:lower(s,u,t)
  for lane in range(lanes):
   for course in range(3):
    t0=max(0,course/3-.018);t1=min(1,(course+1)/3+.018)
    tileunit(surf,(lane+.06)/lanes,(lane+.94)/lanes,t0,t1,'pan',lane+course+side)
   if lane<lanes-1:
    for course in range(3):
     tileunit(surf,(lane+.72)/lanes,(lane+1.28)/lanes,max(0,course/3-.022),min(1,(course+1)/3+.022),'cover',lane+course+side+2)
 for side in [0,1]:
  surf=lambda u,t,s=side:upper(s,u,t)
  for lane in range(36):
   for course in range(2):tileunit(surf,(lane+.06)/36,(lane+.94)/36,max(0,course/2-.018),min(1,(course+1)/2+.018),'pan',lane+course+side)
   if lane<35:
    for course in range(2):tileunit(surf,(lane+.72)/36,(lane+1.28)/36,max(0,course/2-.02),min(1,(course+1)/2+.02),'cover',lane+course+side+2)
 # Nine-ridge roof: one main ridge, four upper gable verges, four diagonal hips.
 ridge=group('05_One_Main_Ridge_Four_Verges_Four_Hips',mats['M_V21_GATE_REF_14'])
 for k in range(25):
  x0=CX-IA+k*(IA*2/25)-.004;x1=x0+IA*2/25+.008
  tube(ridge,[(x0+(x1-x0)*j/4,CY,RIDGE+.098)for j in range(5)],.036,12)
 lattice=group('05B_True_Open_Diamond_Ridge_Band',mats['M_V21_GATE_REF_14'])
 box(lattice,CX-IA,CX+IA,CY-.020,CY+.020,RIDGE+.027,RIDGE+.039)
 box(lattice,CX-IA,CX+IA,CY-.020,CY+.020,RIDGE+.076,RIDGE+.086)
 for k in range(36):
  x=CX-IA+(k+.5)*IA*2/36
  p=[(x-.042,CY,RIDGE+.057),(x,CY,RIDGE+.080),(x+.042,CY,RIDGE+.057),(x,CY,RIDGE+.034)]
  for a,b in zip(p,p[1:]+p[:1]):beam(lattice,a,b,.026,.006)
 for s in [-1,1]:
  for sy in [-1,1]:
   path=[]
   for k in range(18):
    t=k/17;path.append((CX+s*IA,CY+sy*IB*t,RIDGE-(RIDGE-SHOULDER)*t**.9+.055))
   tube(ridge,path,.036,10)
   path=[]
   for k in range(25):
    t=k/24;q=lower(0 if sy<0 else 1,0 if s<0 else 1,t);path.append((q[0],q[1],q[2]+.048))
   tube(ridge,path,.040,12)
 # Four modest swept corner finials, sculpt-ready dense closed geometry.
 wings=group('06_Four_Sculpted_Corner_Finials',mats['M_V21_GATE_REF_14'])
 for sx in [-1,1]:
  for sy in [-1,1]:
   vv=[];ff=[];rings=33;sectors=12
   for k in range(rings):
    t=k/(rings-1);x=CX+sx*(A-.24+.39*t);y=CY+sy*(B-.11+.17*t)
    z=EAVE+.105+.020*t+.460*t*t;halfwidth=.043*(1-.65*t);halfheight=.045+.030*math.sin(math.pi*t)
    for j in range(sectors):
     a=math.tau*j/sectors;vv.append((x-sy*.4*halfwidth*math.cos(a),y+sx*.92*halfwidth*math.cos(a),z+halfheight*math.sin(a)))
   ff=[list(range(sectors-1,-1,-1)),list(range((rings-1)*sectors,rings*sectors))]
   for k in range(rings-1):
    for j in range(sectors):a=k*sectors+j;b=k*sectors+(j+1)%sectors;ff.append([a,b,b+sectors,a+sectors])
   append(wings,vv,ff)
 # A sealed pale ceiling and stepped continuous load-bearing mouldings.
 ceil=group('07_Closed_Pale_Ceiling',mats['M_V21_GATE_CLOSED_PALE_SOFFIT'])
 box(ceil,CX-1.95,CX+1.95,CY-.57,CY+.57,2.538,2.665)
 mould=group('08_Five_Continuous_Stepped_Eave_Bands',mats['M_V21_GATE_REF_12'])
 # Ring profiles increase their reach towards the roof, visually readable from below.
 levels=[(1.96,.575,2.655,2.695),(2.015,.600,2.695,2.736),(2.065,.620,2.736,2.770),(2.110,.642,2.770,2.815),(2.155,.660,2.815,2.865)]
 for a,b,z0,z1 in levels:
  box(mould,CX-a,CX+a,CY-b,CY-b+.075,z0,z1)
  box(mould,CX-a,CX+a,CY+b-.075,CY+b,z0,z1)
  box(mould,CX-a,CX-a+.075,CY-b+.075,CY+b-.075,z0,z1)
  box(mould,CX+a-.075,CX+a,CY-b+.075,CY+b-.075,z0,z1)
 # Continuous backing connects every step and eave corner: no open underside.
 back=group('09_Continuous_Eave_Bearing_Core',mats['M_V21_GATE_REF_09'])
 # A continuous bearing core must sit BEHIND each exposed stepped fascia.
 # A single oversized cuboid here would conceal the middle moulding levels.
 for a,b,z0,z1 in levels:
  box(back,CX-a+.045,CX+a-.045,CY-b+.025,CY+b-.025,z0-.002,z1+.002)
 rafters=group('10_Exposed_Rafter_Tails_and_Corner_Braces',mats['M_V21_GATE_REF_11'])
 for side in range(4):
  num=29 if side<2 else 8
  for i in range(num):
   u=(i+.5)/num;p=lower(side,u,.36);q=lower(side,u,.985)
   beam(rafters,(p[0],p[1],p[2]-.085),(q[0],q[1],q[2]-.077),.050,.063)
 # Shallow hanging floral slabs, all volumetric, with restrained profiles from photographs.
 frieze=group('11_Hanging_Floral_Frieze_and_Returns',mats['M_V21_GATE_REF_13'])
 ornament=group('12_Frieze_Shallow_Raised_Petals',mats['M_V21_GATE_REF_13'])
 for side in range(4):
  n=24 if side<2 else 7;span=3.96 if side<2 else 1.16
  for i in range(n):
   c=-span/2+(i+.5)*span/n;w=span/n-.004
   poly=[(c-w*.5,2.70),(c+w*.5,2.70),(c+w*.5,2.61),(c+w*.38,2.60),(c+w*.25,2.62),(c,2.582),(c-w*.25,2.62),(c-w*.38,2.60),(c-w*.5,2.61)]
   if side<2:
    poly=[(x+CX,z)for x,z in poly];yy=CY+(-.588 if side==0 else .588);prism(frieze,poly,1,yy-.014,yy+.014)
   else:
    poly=[(y+CY,z)for y,z in poly];xx=CX+(-1.982 if side==2 else 1.982);prism(frieze,poly,0,xx-.014,xx+.014)
   # Each compact petal is a closed low-relief oval tube, 2 mm proud of the panel.
   for petal in range(4):
    ang=math.tau*petal/4;path=[]
    for j in range(17):
     t=math.tau*j/16;du=.030*math.cos(t);dz=.011*math.sin(t)
     a=c+math.cos(ang)*(du+.021)-math.sin(ang)*dz;z=2.645+math.sin(ang)*(du+.021)+math.cos(ang)*dz
     path.append((CX+a,CY+(-.607 if side==0 else .607),z)if side<2 else(CX+(-2.001 if side==2 else 2.001),CY+a,z))
    tube(ornament,path,.0028,6)
 # Thin triangular course above the hanging frieze. It is carried on a real continuous band.
 teeth=group('13_Triangular_Eave_Course',mats['M_V21_GATE_REF_12'])
 for side in [0,1]:
  y=CY+(-.636 if side==0 else .636)
  for i in range(30):
   x=CX-2.035+(i+.5)*4.07/30;prism(teeth,[(x-.064,2.775),(x,2.822),(x+.064,2.775)],1,y-.010,y+.010)
 # Round embossed endcaps at outer courses, aligned with actual tile surfaces.
 caps=group('14_Round_Tile_Ends',tiles[2]);caprelief=group('15_Tile_End_Rosettes',mats['M_V21_GATE_REF_14'])
 for side in range(4):
  num=35 if side<2 else 11
  for i in range(num):
   u=(i+1)/(num+1);x,y,z=lower(side,u,1);z+=.027
   d=Vector((0,-1 if side==0 else 1,0))if side<2 else Vector((-1 if side==2 else 1,0,0));p=Vector((x,y,z));tube(caps,[tuple(p),tuple(p+d*.018)],.032,16)
   for k in range(6):
    a=math.tau*k/6;h=Vector((1,0,0))if side<2 else Vector((0,1,0));q=p+d*.020+h*.016*math.cos(a)+Vector((0,0,.016*math.sin(a)));tube(caprelief,[tuple(q),tuple(q+d*.003)],.0045,7)
 # Editable real meshes, inherited shader datablocks, metric UVs, closed manifold checks.
 for label,(V,F,mat) in groups.items():
  if label[:2]in ['07','08','09','11','12','13']:
   V=[(x,CY+(y-CY)*BEARING_DEPTH_SCALE,fitted_bearing_z(z))for x,y,z in V]
  name='V24_XIESHAN_'+label;me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(V,[],F);me.update();me.materials.append(mat)
  uv=me.uv_layers.new(name='V24_Metric_UV')
  for loop in me.loops:
   p=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x*.35+p.y*.13,p.z*.35+p.y*.31)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);volume=abs(bm.calc_volume(signed=True));boundary=sum(not e.is_manifold for e in bm.edges);bm.free()
  if boundary or volume<=1e-10:raise RuntimeError(('Invalid xieshan solid',name,boundary,volume))
  ob=bpy.data.objects.new(name,me);collection.objects.link(ob)
  if parent:ob.parent=parent;ob.matrix_world=Matrix.Identity(4)
  ob['V24_Xieshan_Roof']=True;ob['Reference']='DJI_0101.JPG, DJI_0103.JPG, 124258.jpg; photo fitted LOCAL coordinates'
  if label.startswith(('04','05','06','12','14','15')):
   for p in me.polygons:p.use_smooth=True
  if label.startswith('06'):
   bpy.context.view_layer.objects.active=ob;ob.select_set(True);mod=ob.modifiers.new('V24_Editable_Corner_Sculpt','MULTIRES');bpy.ops.object.multires_subdivide(modifier=mod.name,mode='SIMPLE');mod.levels=1;mod.sculpt_levels=1;mod.render_levels=1;ob.select_set(False)
  lo=[min(v[i]for v in V)for i in range(3)];hi=[max(v[i]for v in V)for i in range(3)]
  report.append({'object':name,'vertices':len(V),'faces':len(F),'closed_manifold':True,'volume_m3':volume,'bbox':[lo,hi],'material':mat.name})
 bpy.context.view_layer.update()
 result={'status':'PASS_XIESHAN_REAL_GEOMETRY','coordinate_system':'Existing scene LOCAL metres; photograph fit, not direct surveyed registration','removed_objects':old,'changed_old_objects':[],'added_objects':[r['object']for r in report],'new_objects':[r['object']for r in report],'roof_type':'single-eave xieshan: two upper main slopes + two gable tympana + four lower hip slopes; 1 main ridge + 4 upper verges + 4 hip ridges','roof_patch_counts':{'upper_main_slopes':2,'upper_gables':2,'lower_hip_slopes':4,'main_ridges':1,'upper_verges':4,'hip_ridges':4,'corner_finials':4},'ceramic_closed_units':count,'open_main_ridge_diamonds':36,'continuous_moulding_levels':5,'front_eave_y':CY-B,'back_eave_y':CY+B,'outer_eave_x':[CX-A,CX+A],'shoulder_rectangle':[CX-IA,CX+IA,CY-IB,CY+IB],'elevations':{'eave_mid':EAVE,'hip_shoulder':SHOULDER,'upper_ridge':RIDGE,'top_coping':RIDGE+.134},'geometry':report,'material_shaders_modified':False,'doors_or_relief_modified':False}
 (out/'V24_04_Xieshan_Roof_Report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print('V24 XIESHAN COMPLETE',len(report),'groups',count,'ceramic units',flush=True);return result

def xieshan_clearance_mesh_data(padding=.006):
 """Closed LOCAL metre envelope for adjoining-wall/roof termination, not a coarse AABB.
 Returns vertices and faces only. Caller can build and delete its own Boolean cutter.
 Includes the five stepped bearing tiers, four lower hips, and two upper gables.
 """
 N=32;V=[];F=[]
 def ring(a,b,zfunc):
  ids=[]
  for side in range(4):
   for i in range(N):
    u=i/N
    if side==0:s=-1+2*u;x,y=CX+s*a,CY-b
    elif side==1:s=-1+2*u;x,y=CX+a,CY+s*b
    elif side==2:s=1-2*u;x,y=CX+s*a,CY+b
    else:s=1-2*u;x,y=CX-a,CY+s*b
    z=zfunc(side,s)if callable(zfunc)else zfunc
    ids.append(len(V));V.append((x,y,z))
  return ids
 steps=[(1.950,.570,2.538-padding),(1.950,.570,2.577),(2.005,.611,2.577),(2.005,.611,2.710),(2.015,.611,2.736),(2.065,.620,2.770),(2.110,.646,2.815),(2.155,.666,2.865)]
 rings=[]
 for a,b,z in steps:rings.append(ring(a+padding,(b+padding)*BEARING_DEPTH_SCALE,fitted_bearing_z(z)))
 rings.append(ring(A+padding,B+padding,lambda side,s:EAVE+.15*abs(s)**5+.053+padding))
 rings.append(ring(IA+padding,IB+padding,SHOULDER+.053+padding))
 F.append(list(reversed(rings[0])))
 for r0,r1 in zip(rings,rings[1:]):
  for i in range(N*4):j=(i+1)%(N*4);F.append([r0[i],r0[j],r1[j],r1[i]])
 inner=rings[-1];left=len(V);V.append((CX-IA-padding,CY,RIDGE+.134+padding));right=len(V);V.append((CX+IA+padding,CY,RIDGE+.134+padding))
 F.append([*inner[:N+1],right,left])
 F.append([*inner[2*N:3*N+1],left,right])
 F.append([*inner[N:2*N+1],right])
 F.append([*inner[3*N:],inner[0],left])
 return V,F
