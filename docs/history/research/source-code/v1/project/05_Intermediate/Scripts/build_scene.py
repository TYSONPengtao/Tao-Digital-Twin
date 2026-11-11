"""Source-grounded architectural reconstruction. All geometry in metres.
No source mesh is used as building geometry. See element Evidence attributes.
"""
# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,math,csv,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
import numpy as np
OUT=Path(r'E:\jz\JIA\Rebuild')
THETA=math.radians(19.65);ORIGIN=[-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002]
MATS={
 'M_Wall_Exterior':{'color':[232,231,218],'roughness':.75},'M_Wall_Interior':{'color':[241,239,234],'roughness':.8},'M_Concrete':{'color':[158,160,155],'roughness':.85},
 'M_Brick':{'color':[108,110,104],'roughness':.85},'M_Stone':{'color':[171,178,171],'roughness':.7},'M_Wood':{'color':[108,49,27],'roughness':.45},
 'M_Glass_Clear':{'color':[128,166,161],'roughness':.1,'alpha':.25,'ior':1.52},'M_Glass_Frosted':{'color':[186,207,201],'roughness':.45,'alpha':.7,'ior':1.52},
 'M_Metal_Black':{'color':[67,79,78],'roughness':.28,'metallic':.8},'M_Metal_Stainless':{'color':[188,194,195],'roughness':.2,'metallic':1},'MAT_DOOR_FRAME_RED':{'color':[114,35,29],'roughness':.35,'metallic':.5},
 'M_Roof':{'color':[96,103,100],'roughness':.82},'M_Tile':{'color':[184,185,171],'roughness':.4},'M_Floor':{'color':[168,174,169],'roughness':.4},
 'M_Ceiling':{'color':[245,243,238],'roughness':.8},'M_Asphalt':{'color':[123,128,120],'roughness':.9},'M_Soil':{'color':[123,106,75],'roughness':.98},
 'M_Grass':{'color':[96,113,71],'roughness':1},'M_Water':{'color':[88,132,145],'roughness':.1,'alpha':.45},'M_Uncertain':{'color':[230,156,63],'roughness':.7}}
ELEMENTS=[];DEFS={};OPENINGS=[]
def box(x,y,z,w,d,h):return {'type':'box','origin':[x,y,z],'size':[w,d,h]}
def prism(profile,vector):return {'type':'prism','profile':profile,'vector':vector}
def polyz(xy,z,h):return prism([[x,y,z] for x,y in xy],[0,0,h])
def cylinder(x,y,z,r,h,segments=24):return {'type':'cylinder','origin':[x,y,z],'radius':r,'height':h,'segments':segments}
def add(name,layer,parts,source,confidence='HIGH',family='ARCH_MODEL',**meta):
 e={'name':name,'layer':layer,'family':family,'parts':parts,'source':source,'confidence':confidence,**meta};ELEMENTS.append(e);return e
def part(g,mat):return {'geometry':g,'material':mat}
def instance(name,layer,key,origin,angle=0,source='D03,D04,D06',confidence='HIGH',family='ARCH_MODEL',**meta):
 e=add(name,layer,[],source,confidence,family,definition=key,origin=origin,angle=angle,**meta);return e
def transform_points(p,origin,angle):
 a=np.asarray(p,dtype=float);c=math.cos(angle);s=math.sin(angle);a[:,:2]=a[:,:2]@np.array([[c,s],[-s,c]]);return (a+np.array(origin)).tolist()
def wall(name,p0,p1,z,h,t,opens=(),ext=True,columns=()):
 p0=np.array(p0,float);p1=np.array(p1,float);L=np.linalg.norm(p1-p0);u=(p1-p0)/L;n=np.array([-u[1],u[0]]);breaks={0,L};cut=[]
 for s,w,b,hh in opens:breaks.update([s,s+w]);cut.append((s,s+w,b,b+hh))
 for s,w in columns:breaks.update([max(0,s-w/2),min(L,s+w/2)]);cut.append((s-w/2,s+w/2,0,h))
 intervals=sorted(max(0,min(L,x)) for x in breaks);parts=[]
 for s0,s1 in zip(intervals[:-1],intervals[1:]):
  if s1-s0<1e-6:continue
  mid=(s0+s1)/2;zz={0,h}
  for a,b,bz,tz in cut:
   if a-1e-6<=mid<=b+1e-6:zz.update([max(0,bz),min(h,tz)])
  zz=sorted(zz)
  for z0,z1 in zip(zz[:-1],zz[1:]):
   if z1-z0<1e-6 or any(a<mid<b and bz<(z0+z1)/2<tz for a,b,bz,tz in cut):continue
   q=[p0+u*s0-n*t/2,p0+u*s1-n*t/2,p0+u*s1+n*t/2,p0+u*s0+n*t/2]
   parts.append(part(polyz(q,z+z0,z1-z0),'M_Wall_Exterior' if ext else 'M_Wall_Interior'))
 e=add(name,'10_WALL_EXT' if ext else '11_WALL_INT',parts,'D02,D03,D04',status='PDF_DESIGN_FIELD_PARTIAL',thickness=t,core_thickness=.18,opening_data=list(opens))
 return e
def win_def(W,H,panes=2,frosted=False,red=False):
 key=f'WINDOW_W{int(W*1000)}_H{int(H*1000)}_P{panes}'+('_FROSTED' if frosted else '')+('_RED' if red else '')
 if key in DEFS:return key
 b=.06;dep=.09;parts=[];frame='MAT_DOOR_FRAME_RED' if red else 'M_Metal_Black'
 for g in [box(0,-dep/2,0,W,dep,b),box(0,-dep/2,H-b,W,dep,b),box(0,-dep/2,b,b,dep,H-2*b),box(W-b,-dep/2,b,b,dep,H-2*b)]:parts.append(part(g,frame))
 cell=(W-2*b-(panes-1)*b)/panes
 for i in range(panes):
  x=b+i*(cell+b)
  if i:parts.append(part(box(x-b,-dep/2,b,b,dep,H-2*b),frame))
  transom=H*.72 if H>2 else H*.6
  parts.append(part(box(x,-dep/2,transom-.025,cell,dep,.05),frame))
  for zz,hh in [(b,transom-.025-b),(transom+.025,H-b-transom-.025)]:parts.append(part(box(x,-.003,zz,cell,.006,hh),'M_Glass_Frosted' if frosted else 'M_Glass_Clear'))
 # Separate stone sill with true thickness; sill remains below the opening.
 parts.append(part(box(-.04,-.16,-.04,W+.08,.28,.04),'M_Stone'))
 DEFS[key]={'parts':parts,'parameters':{'Width':W,'Height':H,'Frame_Depth':dep,'Frame_Width':b,'Glass_Thickness':.006,'Opening_Width':W,'Opening_Height':H},'source':'D06 schedule; profile 60x90mm and mullion scheme visually estimated','confidence':'MEDIUM'};return key
def door_def(W,H=2.1,sliding=False):
 key=f'DOOR_W{int(W*1000)}_H{int(H*1000)}'+('_SLIDING' if sliding else '_WOOD')
 if key in DEFS:return key
 if sliding:
  keywin=win_def(W,H,max(4,int(W/1.2)),False,True);DEFS[key]={'parts':DEFS[keywin]['parts'][:-1],'parameters':DEFS[keywin]['parameters'],'source':'D06 M4821; video L0 79s red frame','confidence':'MEDIUM'}
 else:
  b=.045;parts=[part(box(b,-.025,0,W-2*b,.05,H-b),'M_Wood'),part(box(0,-.07,0,b,.14,H),'M_Wood'),part(box(W-b,-.07,0,b,.14,H),'M_Wood'),part(box(b,-.07,H-b,W-2*b,.14,b),'M_Wood')]
  DEFS[key]={'parts':parts,'parameters':{'Width':W,'Height':H,'Frame_Depth':.14,'Opening_Width':W,'Opening_Height':H},'source':'D06 door schedule; frame thickness visually estimated','confidence':'MEDIUM'}
 return key
def opening_instance(name,typ,W,H,origin,angle=0,panes=2,frost=False,**meta):
 key=win_def(W,H,panes,frost) if typ=='window' else door_def(W,H,W>2)
 e=instance(name,'31_WINDOW' if typ=='window' else '30_DOOR',key,origin,angle,**meta);OPENINGS.append({'name':name,'type':typ,'W':W,'H':H,'origin':origin,'angle':angle,'definition':key});return e
def railing(name,p0,p1,z,H=1.1,stone=False,source='D04,D06; video L0 377s'):
 L=math.dist(p0,p1);ang=math.atan2(p1[1]-p0[1],p1[0]-p0[0]);parts=[]
 if stone:
  parts=[part(box(0,-.09,0,L,.18,.2),'M_Stone'),part(box(0,-.08,.22,L,.16,.68),'M_Stone'),part(box(-.025,-.12,H-.14,L+.05,.24,.14),'M_Stone')]
  for x in np.linspace(0,L,max(2,int(L/1.3)+1)):parts.append(part(box(x-.09,-.09,0,.18,.18,H),'M_Stone'))
 else:
  parts=[part(box(0,-.03,H-.06,L,.06,.06),'M_Wood')]
  for x in np.linspace(0,L,max(2,int(L/.12)+1)):parts.append(part(box(x-.015,-.015,.06,.03,.03,H-.12),'M_Wood'))
 add(name,'41_RAILING',parts,source,'MEDIUM',origin=[*p0,z],angle=ang,profile_assumption=True)
# Structural grid dimensions and elevations are read from formal dimensions.
X=[0,3.9,9.1,13];Y=[2.1,7.3,9.8];levels=[0,3.9,7.5,10.8]
for i,z0 in enumerate(levels[:-1]):
 ztop=levels[i+1]-.13
 for ix,x in enumerate(X):
  for iy,y in enumerate(Y):
   if i==2 and ix==0 and iy==0:continue
   key=f'COLUMN_400_400_H{round((ztop-z0)*1000)}'
   DEFS.setdefault(key,{'parts':[part(box(-.2,-.2,0,.4,.4,ztop-z0),'M_Concrete')],'parameters':{'Width':.4,'Depth':.4,'Height':ztop-z0},'source':'D12-D14 KZ schedule','confidence':'HIGH'})
   instance(f'KZ_{ix+1}_{iy+1}_F{i+1}','20_COLUMN',key,[x,y,z0],source=f'D{12+i:02d}')
 for y in Y:
  for xa,xb in zip(X[:-1],X[1:]):add(f'BEAM_X_F{i+1}_{y}_{xa}','21_BEAM',[part(box(xa+.2,y-.125,ztop-.27,xb-xa-.4,.25,.27),'M_Concrete')],f'D{16 if i==0 else 17 if i==1 else 18:02d}','MEDIUM',section_height=.4,slab_included_depth=.13,status='AS_DESIGNED_SECTION_LABEL_PARTIAL')
 for x in X:
  if i==2 and x==0:ys=[7.3,9.8]
  else:ys=Y
  for ya,yb in zip(ys[:-1],ys[1:]):add(f'BEAM_Y_F{i+1}_{x}_{ya}','21_BEAM',[part(box(x-.125,ya+.2,ztop-.27,.25,yb-ya-.4,.27),'M_Concrete')],f'D{16 if i==0 else 17 if i==1 else 18:02d}','MEDIUM',section_height=.4,section_width=.25,status='TYPE_KL_250x400_INTERPRETED')
# Floor slabs are divided into adjacent native profiles; the stair opening is empty.
for floor,z in enumerate([0,3.9,7.5]):
 h=.13 if floor else .15
 polygons=[[(0,2.1),(.7,1.1),(3.2,1.1),(3.9,2.1),(3.9,9.9),(-.1,9.9),(-.1,2.1)],[(9.1,2.1),(9.8,1.1),(12.3,1.1),(13,2.1),(13.1,2.1),(13.1,9.9),(9.1,9.9)],[(3.9,0),(9.1,0),(9.1,7.3),(3.9,7.3)],[(7.8,7.3),(9.1,7.3),(9.1,9.9),(7.8,9.9)]]
 if floor==0:polygons.append([(3.9,7.3),(7.8,7.3),(7.8,9.9),(3.9,9.9)])
 if floor==2:polygons[0]=[[-.1,1.1],[3.9,1.1],[3.9,9.9],[-.1,9.9]]
 for k,poly in enumerate(polygons):add(f'SLAB_F{floor+1}_{k+1}','22_SLAB',[part(polyz(poly,z-h,h),'M_Concrete')],'D03,D04,D19,D20','HIGH' if floor else 'MEDIUM',thickness=h)
# Finished walls and actual clear openings are created without mesh booleans.
for floor,(z,zt) in enumerate(zip(levels[:-1],levels[1:])):
 h=zt-z-.13
 # Two outer side walls, with the front-left terrace absent on floor 3.
 for side,x in [('LEFT',0),('RIGHT',13)]:
  start=7.5 if floor==2 and side=='LEFT' else 2.3
  ends=[(start,7.1),(7.5,9.6)] if start<7.1 else [(start,9.6)]
  for j,(ya,yb) in enumerate(ends):
   oo=[]
   if ya>=7.5:oo=[(0 if floor==2 and side=='LEFT' else .45,2.1 if floor==2 and side=='LEFT' else 1.2,.9,1.95 if floor==2 and side=='LEFT' else 1.2)]
   wall(f'WALL_{side}_F{floor+1}_{j}',(x,ya),(x,yb),z,h,.2,oo)
   if oo:opening_instance(f'WINDOW_{side}_'+('C2120' if floor==2 and side=='LEFT' else 'C1212')+f'_F{floor+1}','window',oo[0][1],oo[0][3],[x,ya+oo[0][0],z+.9],math.pi/2,frost=not(floor==2 and side=='LEFT'))
 # Back wall, interrupted at each 400mm column.
 heights=[2.55,2.25,1.95];H=heights[floor]
 backops=[(2.29,1.41,.9,H),(7.7,1.2,.9,H),(9.3,1.41,.9,H)]
 if floor==0:backops[2]=(9.3,1.41,.9,2.25)
 if floor==2:backops[0]=(.2,3.5,.9,1.95)
 wall(f'WALL_BACK_F{floor+1}',(0,9.8),(13,9.8),z,h,.2,backops,columns=[(xx,.4) for xx in X])
 for k,(s,w,sz,hh) in enumerate(backops):opening_instance(f'WINDOW_BACK_F{floor+1}_{k+1}','window',w,hh,[s,9.8,z+sz],panes=5 if w==3.5 else 2)
 # Bed/hall separation: door opening at the rear end.
 for x in [3.9,9.1]:
  oo=[(3.8,.9,0,2.1)]
  if floor==2 and x==3.9:oo=[]
  wall(f'PARTITION_BED_F{floor+1}_X{x}',(x,2.3),(x,7.1),z,h,.2,oo,ext=(floor==2 and x==3.9))
  if oo:opening_instance(f'DOOR_BED_F{floor+1}_X{x}','door',.9,2.1,[x,2.3+oo[0][0],z],math.pi/2)
 # Back rooms. The laundry niche below F3 is open to the bedroom.
 for side,x0 in [('L',0),('R',9.1)]:
  if side=='L':
   wall(f'PARTITION_BACK_F{floor+1}_{side}',(.2,7.3),(3.7 if floor==2 else 2.2,7.3),z,h,.2,[(2.6,.9,0,2.1)] if floor==2 else (),False)
   wall(f'PARTITION_BACKROOM_EAST_F{floor+1}',(3.9,7.5),(3.9,9.6),z,h,.2,(),False)
   if floor==2:opening_instance('DOOR_LAUNDRY_F3','door',.9,2.1,[2.8,7.3,z])
  else:
   wall(f'PARTITION_BACK_F{floor+1}_{side}',(x0+.2,7.3),(x0+3.7,7.3),z,h,.2,[(2.6,.8,0,2.1)],False)
   opening_instance(f'DOOR_BACKROOM_F{floor+1}_{side}','door',.8,2.1,[x0+2.8,7.3,z])
  if not(floor==2 and side=='L'):
   xx=2.2 if side=='L' else 10.8
   wall(f'PARTITION_BATH_F{floor+1}_{side}',(xx,7.4),(xx,9.6),z,h,.18,[(.25,.8,0,2.1)] if side=='L' else (),False)
   if side=='L':opening_instance(f'DOOR_BATH_F{floor+1}_{side}','door',.8,2.1,[xx,7.65,z],math.pi/2)
 if floor==0:
  wall('PARTITION_KITCHEN_F1',(7.8,7.5),(7.8,9.6),z,h,.18,[(1.1,.8,0,2.1)],False)
  opening_instance('DOOR_KITCHEN_F1','door',.8,2.1,[7.8,8.6,z],math.pi/2)
 if floor==2:
  wall('PARTITION_STUDY_F3',(3.9,7.3),(9.1,7.3),z,h,.2,[(.2,3.6,.9,1.95),(4.1,.9,0,2.1)],False,columns=[(0,.4),(5.2,.4)])
  opening_instance('WINDOW_STUDY_C3620_F3','window',3.6,1.95,[4.1,7.3,z+.9],panes=5)
  opening_instance('DOOR_STUDY_F3','door',.9,2.1,[8.0,7.3,z])
 # Front entrance / balcony door / upper study window.
 if floor<2:
  W=4.8;HH=2.1;s=.2;oo=[(s,W,0,HH)];typ='door'
 else:W=4.8;HH=1.95;s=.2;oo=[(s,W,.9,HH)];typ='window'
 wall(f'WALL_FRONT_CENTER_F{floor+1}',(3.9,2.1),(9.1,2.1),z,h,.2,oo,columns=[(0,.4),(5.2,.4)])
 opening_instance(f'{typ.upper()}_FRONT_CENTER_F{floor+1}',typ,W,HH,[3.9+s,2.1,z+(0 if floor<2 else .9)],panes=8)
 # Polygonal bay windows: formally dimensioned 700 + 2500 + 700.
 for x0,side in [(0,'L'),(9.1,'R')]:
  if floor==2 and side=='L':continue
  baypaths=[((x0,2.1),(x0+.7,1.1)),((x0+.7,1.1),(x0+3.2,1.1)),((x0+3.2,1.1),(x0+3.9,2.1))]
  for k,(p0,p1) in enumerate(baypaths):
   ll=math.dist(p0,p1);bw=ll-.12;bh=[3.0,2.7,2.4][floor];sill=.6
   wall(f'BAY_WALL_F{floor+1}_{side}_{k}',p0,p1,z,h,.2,[(.06,bw,sill,bh)])
   ori=np.array(p0)+.06*(np.array(p1)-p0)/ll
   opening_instance(f'BAY_WINDOW_F{floor+1}_{side}_{k}','window',bw,bh,[*ori,z+sill],math.atan2(p1[1]-p0[1],p1[0]-p0[0]),panes=3 if k==1 else 1,source='D04 bay width; D05 elevation; video 79s/377s',confidence='MEDIUM',bay_clear_height_estimated=True)
# Front decorative round columns (GZY D=250) are independent repeated components.
for z,h in [(0,3.77),(3.9,3.47)]:
 key=f'GZY_D250_H{int(h*1000)}';DEFS[key]={'parts':[part(cylinder(0,0,0,.125,h),'M_Stone')],'parameters':{'Diameter':.25,'Height':h},'source':'D22 GZY D250; video entrance column','confidence':'HIGH'}
 for x in [3.9,9.1]:instance(f'GZY_X{x}_Z{z}','20_COLUMN',key,[x,0,z],source='D22; video L0 79s,377s')
railing('BALCONY_STONE_FRONT',(4.1,0),(8.9,0),3.85,1.1,True)
for x in [3.9,9.1]:railing(f'BALCONY_STONE_SIDE_X{x}',(x,0),(x,1.9),3.85,1.1,True)
railing('TERRACE_WEST',(0,1.1),(0,7.1),7.45,1.1,False,'D04,D06; 3F terrace not visited')
railing('TERRACE_FRONT',(0,1.1),(3.7,1.1),7.45,1.1,False,'D04,D06; 3F terrace not visited')
ELEMENTS[-1]['parts'].pop(1) # shared corner baluster is owned by TERRACE_WEST
# Exact two-flight stairs: 11 rises / 10 treads per flight.
for storey,(z,mid,top,rises) in enumerate([(0,1.95,3.9,[.178]*3+[.177]*8),(3.9,5.7,7.5,[.164]*7+[.163]*4)]):
 for flight in [0,1]:
  bz=z if flight==0 else mid;direction=-1 if flight==0 else 1;xstart=7.8 if flight==0 else 5.2;ystart=7.4 if flight==0 else 8.665
  profile=[];zz=bz
  profile.append([xstart,ystart,bz-.14])
  profile.append([xstart,ystart,bz+rises[0]])
  for k in range(10):
   xx=xstart+direction*(k+1)*.26;profile.append([xx,ystart,bz+sum(rises[:k+1])])
   if k<9:profile.append([xx,ystart,bz+sum(rises[:k+2])])
  # The landing or upper floor forms the final (11th) riser. Avoid a doubled end edge.
  xend=xstart+direction*2.6;profile.append([xend,ystart,bz+sum(rises[:10])-.14]);
  add(f'STAIR_F{storey+1}_FLIGHT{flight+1}','40_STAIR',[part(prism(profile,[0,1.175,0]),'M_Concrete')],'D10,D11',rises=rises,tread=.26,width=1.175,slab=.14,z_from=bz,z_to=bz+sum(rises))
  # Handrail and posts; dimensions from D02/D06; wood appearance from video.
  x0=xstart;xe=xend;z0=bz+.9;ze=bz+sum(rises)+.9;uu=np.array([xe-x0,0,ze-z0]);norm=np.array([-uu[2],0,uu[0]]);norm=norm/np.linalg.norm(norm)*.025
  pp=[np.array([x0,ystart+1.15,z0])+norm,np.array([xe,ystart+1.15,ze])+norm,np.array([xe,ystart+1.15,ze])-norm,np.array([x0,ystart+1.15,z0])-norm]
  add(f'STAIR_HANDRAIL_F{storey+1}_{flight+1}','41_RAILING',[part(prism([x.tolist() for x in pp],[0,.05,0]),'M_Wood')],'D02,D06; video 153s','MEDIUM')
  key='STAIR_BALUSTER_30_30_H850';DEFS.setdefault(key,{'parts':[part(box(-.015,-.015,0,.03,.03,.85),'M_Wood')],'parameters':{'Width':.03,'Height':.85},'source':'video wooden baluster; unmeasured profile','confidence':'MEDIUM'})
  for k in range(11):instance(f'STAIR_BALUSTER_{storey}_{flight}_{k}','41_RAILING',key,[xstart+direction*k*.26,ystart+1.175,bz+sum(rises[:k+1])],source='video153s; D02 railing900mm',confidence='MEDIUM')
 add(f'STAIR_LANDING_F{storey+1}','40_STAIR',[part(box(3.9,7.4,mid-.14,1.3,2.44,.14),'M_Concrete')],'D10,D11')
# Roof L profile, eaves 10.800, ridge 12.000. Facet arrangement from D04.
def panel(name,pts,th=.10,layer='50_ROOF',source='D04,D05,D06',confidence='MEDIUM',family='ARCH_MODEL'):
 pp=np.array(pts,float);normal=np.cross(pp[1]-pp[0],pp[2]-pp[0]);normal/=np.linalg.norm(normal)
 if normal[2]<0:pp=pp[::-1];normal=-normal
 add(name,layer,[part(prism(pp.tolist(),(-normal*th).tolist()),'M_Roof')],source,confidence,family,thickness=th)
E=10.6;Z=12.0
# 10.800 is the PDF bearing/eave datum. The overhanging edge is lower,
# approximately 10.600 in the registered OBJ. Front roof does not span the porch.
A=[-.8,6.5,E];B=[3.1,6.5,E];C=[3.1,.6,E];D=[13.8,.6,E];EE=[13.8,10.6,E];F=[-.8,10.6,E]
P=[1.25,8.55,Z];Q=[8.45,8.55,Z];T=[8.45,3.0,Z]
for name,pts in [('WEST_HIP',[A,F,P]),('WING_SOUTH',[A,P,Q,B]),('MAIN_WEST',[B,Q,T,C]),('SOUTH_HIP',[C,T,D]),('MAIN_EAST',[D,T,Q,EE]),('NORTH_HIP',[EE,Q,F]),('WING_NORTH',[F,Q,P])]:
 # Nonplanar quads are split into separate planar triangular native prisms.
 if len(pts)==4 and abs(np.dot(np.cross(np.array(pts[1])-pts[0],np.array(pts[2])-pts[0]),np.array(pts[3])-pts[0]))>1e-6:
  panel('ROOF_'+name+'_a',pts[:3]);panel('ROOF_'+name+'_b',[pts[0],pts[2],pts[3]])
 else:panel('ROOF_'+name,pts)
for e in ELEMENTS:
 if e['layer']=='50_ROOF':e['source']='D04,D05,D06 bearing 10.8/ridge12 + OBJ2 approximate overhang edge and ridge endpoints';e['status']='ROOF_DESIGN_DATUM_REALITY_FORM_INTERPRETED';e['confidence']='MEDIUM'
# Lower front canopy, dimensions and levels from D04 and D22.
for k,pts in enumerate([[[2.975,-.8,7.5],[6.5,-.8,8.4],[6.5,2.1,8.4],[2.975,2.1,7.5]],[[6.5,-.8,8.4],[10.025,-.8,7.5],[10.025,2.1,7.5],[6.5,2.1,8.4]]]):panel(f'CANOPY_CENTER_{k}',pts,.1,'51_CANOPY','D04,D22')
panel('CANOPY_LEFT_TERRACE',[[-.8,.1,7.5],[3.7,.1,7.5],[3.7,1.1,7.7],[-.8,1.1,7.7]],.1,'51_CANOPY','D04/D05 roof strip','MEDIUM')
# Entrance steps: three 150mm risers to 0.000 from -0.450.
for k in range(3):add(f'ENTRANCE_STEP_{k+1}','40_STAIR',[part(box(3.75,-.9+k*.3,-.45,5.5,.3,(k+1)*.15),'M_Stone')],'D03 outdoor -0.450, video79s','MEDIUM',tread_estimated=.3)
# Render details are additions to the same source model.
for z in [3.9,7.5]:
 for x0 in [0,9.1]:add(f'FRONT_BAND_X{x0}_Z{z}','51_CANOPY',[part(box(x0-.1,1.0,z-.16,4.1,.18,.16),'M_Stone')],'D05; video entrance fascia','MEDIUM','VIS_MODEL')
for z,h in [(0,3.77),(3.9,3.47)]:
 for x in [3.9,9.1]:
  for zz,r,hh in [(z,.2,.10),(z+.1,.17,.06),(z+h-.10,.18,.10)]:add(f'COLUMN_MOULD_{x}_{zz}','20_COLUMN',[part(cylinder(x,0,zz,r,hh),'M_Stone')],'video79s/377s','MEDIUM','VIS_MODEL')
# Sun/true north marker is documentary geometry, separately switchable.
north=[math.sin(THETA),math.cos(THETA)]
add('TRUE_NORTH','99_HELPER',[{'geometry':{'type':'line','points':[[15,12,0],[15+2*north[0],12+2*north[1],0]]},'material':'M_Metal_Black'}],'ContextCapture ENU','MEDIUM',TrueNorthVector=[*north,0])
for k,x in enumerate(X):add(f'GRID_X_{k+1}','01_GRID',[{'geometry':{'type':'line','points':[[x,-1,-.2],[x,11,-.2]]},'material':'M_Metal_Black'}],'D03')
for k,y in enumerate([0,2.1,7.3,9.8]):add(f'GRID_Y_{chr(65+k)}','01_GRID',[{'geometry':{'type':'line','points':[[-1,y,-.2],[14,y,-.2]]},'material':'M_Metal_Black'}],'D03')
for z in levels+[12]:add(f'LEVEL_{z:.3f}','02_LEVEL',[{'geometry':{'type':'line','points':[[14,0,z],[14,10,z]]},'material':'M_Metal_Black'}],'D03,D04,D05,D06')
# Site surfaces use measured samples; no designed house dimensions are taken from image pixels.
data=np.load(OUT/'05_Intermediate/Reality_Geometry.npz');sp=data['points'];sn=data['normals'];sa=data['areas'];R=np.array([[math.cos(THETA),-math.sin(THETA)],[math.sin(THETA),math.cos(THETA)]]);lp=sp.copy();lp[:,:2]=(sp[:,:2]-np.array(ORIGIN[:2]))@R;lp[:,2]-=ORIGIN[2]
def sitez(x,y,default=-.45):
 sel=(abs(lp[:,0]-x)<1)&(abs(lp[:,1]-y)<1)&(abs(sn[:,2])>.5)&(lp[:,2]<3)
 return float(np.quantile(lp[sel,2],.2)) if sel.sum()>5 else default
def sitepoly(name,xy,material,layer='60_SITE',confidence='MEDIUM'):
 pts=[[x,y,sitez(x,y)] for x,y in xy];add(name,layer,[part({'type':'surface_polygon','points':pts},material)],'OBJ2 measured ground samples',confidence,site_reconstructed=True)
sitepoly('COURTYARD_PAVING',[[-18,-14],[13,-14],[13,-1],[9.1,-1],[9.1,0],[3.9,0],[3.9,1.1],[0,1.1],[0,-1],[-18,-1]],'M_Stone')
sitepoly('BACK_ROAD',[[-22,10.8],[20,10.8],[20,17],[-22,17]],'M_Asphalt')
sitepoly('EAST_LANE',[[14,-15],[18,-15],[18,10.8],[14,10.8]],'M_Asphalt')
sitepoly('SOUTH_LANE',[[-21,-18],[18,-18],[18,-15],[-21,-15]],'M_Asphalt')
# Courtyard wall centreline traced in the measured plan; size estimates remain separate.
def sitewall(name,p0,p1):
 z0=min(sitez(*p0),sitez(*p1));z1=z0;d=np.array(p1)-p0;L=np.linalg.norm(d);u=d/L;perp=np.array([-u[1],u[0]])*.12
 pts=[[*((np.array(p0)-perp).tolist()),z0],[*((np.array(p1)-perp).tolist()),z1],[*((np.array(p1)+perp).tolist()),z1],[*((np.array(p0)+perp).tolist()),z0]]
 add(name,'90_UNCERTAIN',[part(prism(pts,[0,0,2]),'M_Uncertain')],'OBJ2 courtyard wall trace; video674s/823s','LOW',status='MEASURED_PLAN_APPROX_HEIGHT',width=.24,height=2)
sitewall('COURTYARD_WALL_WEST',(-18,-14),(-18,0));sitewall('COURTYARD_WALL_SOUTH',(-18,-14),(10,-14));sitewall('COURTYARD_WALL_EAST',(13,-14),(13,-2))
# Independent terrain surface with building, roads and paving masked out.
vs=[];fs=[];grid={}
for y in range(-24,29,2):
 for x in range(-28,31,2):
  grid[x,y]=len(vs);vs.append([x,y,sitez(x,y,-.45)])
for (x,y),i in grid.items():
 if (x+2,y) not in grid or (x,y+2) not in grid:continue
 cx=x+1;cy=y+1
 if (-19<cx<18 and -19<cy<18):continue
 j=grid[x+2,y];k=grid[x+2,y+2];l=grid[x,y+2];fs.extend([[i,j,k],[i,k,l]])
add('SITE_TERRAIN_SIMPLIFIED','90_UNCERTAIN',[part({'type':'mesh','vertices':vs,'faces':fs},'M_Uncertain')],'OBJ2 lower envelope sampling at 2m; gaps approximated','LOW',site_surface=True,analysis_ready=False,status='COARSE_INTERPOLATED_TERRAIN_NOT_SURVEY')
CAMERAS=[{'name':'CAM_01_Entrance','position':[6.5,-14,6],'target':[6.5,3,5],'fov':50,'status':'MODEL_REVIEW_CAMERA_NOT_PHOTOGRAMMETRIC'},{'name':'CAM_02_Front','position':[26,-25,18],'target':[6.5,4,5.5],'fov':45,'status':'MODEL_REVIEW_CAMERA_NOT_PHOTOGRAMMETRIC'},{'name':'CAM_03_Back','position':[25,27,16],'target':[6.5,5,5.5],'fov':45,'status':'MODEL_REVIEW_CAMERA_NOT_PHOTOGRAMMETRIC'},{'name':'CAM_04_Courtyard','position':[-18,-20,12],'target':[5,3,5],'fov':50,'status':'MODEL_REVIEW_CAMERA_NOT_PHOTOGRAMMETRIC'},{'name':'CAM_05_Aerial','position':[30,-38,35],'target':[0,0,0],'fov':45,'status':'MODEL_REVIEW_CAMERA_NOT_PHOTOGRAMMETRIC'}]
scene={'name':'Production_1QK_Rebuild','units':'metres','coordinate':{'srs':'ENU:TAO_PRIVATE_SITE_003,TAO_PRIVATE_SITE_024','origin':ORIGIN,'rotation_deg':19.65,'local_to_survey':[[math.cos(THETA),-math.sin(THETA),0,ORIGIN[0]],[math.sin(THETA),math.cos(THETA),0,ORIGIN[1]],[0,0,1,ORIGIN[2]],[0,0,0,1]],'confidence':'MEDIUM','vertical_datum':'not independently controlled'},'materials':MATS,'definitions':DEFS,'elements':ELEMENTS,'openings':OPENINGS,'cameras':CAMERAS,'levels':levels+[12],'grid_x':X,'grid_y':[0,2.1,7.3,9.8],'status':'SOURCE_GROUNDED_REVIEW_MODEL; NOT CERTIFIED_AS_BUILT_LOD300'}
for e in ELEMENTS:
 if e['name'] in ['TERRACE_WEST','TERRACE_FRONT']:
  e['layer']='90_UNCERTAIN';e['confidence']='LOW';e['status']='PDF_RAILING_PROXY_MATERIAL_AND_PROFILE_UNVERIFIED'
 if 'definition' in e:
  e['dimension_confidence']=e['confidence']
  if DEFS[e['definition']]['confidence']=='MEDIUM' and e['confidence']=='HIGH':e['confidence']='MEDIUM'
 if e['name'].startswith('PARTITION_') or e['name'].startswith('DOOR_BED') or e['name'].startswith('DOOR_BACKROOM') or e['name'].startswith('DOOR_BATH'):
  e['confidence']='MEDIUM';e['status']='PDF_PLAN_INTERPRETED_NOT_FIELD_VERIFIED'
(OUT/'05_Intermediate/Architecture_Scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'09_Report/Element_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Element','Layer','Family','Source','Confidence','Status','Definition']);w.writerows([[e['name'],e['layer'],e['family'],e['source'],e['confidence'],e.get('status','SOURCE_GROUNDED'),e.get('definition','')] for e in ELEMENTS])
print('Scene elements',len(ELEMENTS),'definitions',len(DEFS),'openings',len(OPENINGS));print(collections.Counter(e['layer'] for e in ELEMENTS))
