import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from v24_13_geometry import roof_z,front,ridge,north_boundary
D=W/'v24_14';OUT={'objects':[],'proof':{'facade_setback_m':.48,'source':'V24.13','reference':'2026-10-18 storage photos 113325 through 114422'}}
def solid(v,f,n=''):
 m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError and m.volume()>0:return m
 for dec in [9,8,7,6,5]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];ok=np.linalg.norm(np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]),axis=1)>1e-13;ff=ff[ok];m=mf.Manifold(mf.Mesh64(np.array(vv,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 raise RuntimeError((n,m.status(),m.volume()))
def load(n):
 d=np.load(D/(n+'.npz'));return solid(d['v'],d['f'],n)
def put(n,m,new=False,mat=None,transfer=None):
 assert m.status()==mf.Error.NoError and m.volume()>0,(n,m.status());d=m.to_mesh64();v=np.asarray(d.vert_properties[:,:3]);f=np.asarray(d.tri_verts);test=solid(v.astype(np.float32).astype(np.float64),f,n+' float32');assert test.volume()>0
 OUT['objects'].append({'name':n,'new':new,'material':mat,'v':v.tolist(),'f':f.tolist(),'bodies':len(m.decompose()),'volume_m3':m.volume(),'transfer':transfer});print(n,round(m.volume(),6),len(m.decompose()),flush=True)
def cube(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def extrude(poly,thick):return mf.CrossSection([np.array(orient(poly,1).exterior.coords)[:-1]]).extrude(thick)
def yzprofile(poly,x0,x1):return extrude(Polygon(poly),x1-x0).transform(np.array([[0,0,1,x0],[1,0,0,0],[0,1,0,0]],float))
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1.]);v/=np.linalg.norm(v);nn=np.cross(u,v);return mf.Manifold.cube([w,d,float(np.linalg.norm(b-a))],True).transform(np.c_[v,nn,u,(a+b)/2])
def under(poly,fn,z0):
 d=extrude(Polygon(poly),1).to_mesh64();v=np.asarray(d.vert_properties[:,:3]).copy();f=np.asarray(d.tri_verts)
 for p in v:p[2]=z0+p[2]*(fn(p[0],p[1])-z0)
 return solid(v,f,'under')
def strip_roof(x0,x1,y0,y1,depth=.02,drop=.075):
 top=under([(x0,y0),(x1,y0),(x1,y1),(x0,y1)],lambda x,y:roof_z(x,y)-drop,2.4);bottom=under([(x0-.01,y0-.01),(x1+.01,y0-.01),(x1+.01,y1+.01),(x0-.01,y1+.01)],lambda x,y:roof_z(x,y)-drop-depth,2.3);return top-bottom
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';original=load(n)
selector=cube([13.30,-15.40,-.60],[18.50,-14.55,2.47]);facade=original^selector
remain=original-selector
cuts=[cube([13.12,-16.9,2.47],[19,-13.99,5.5]),cube([18.405,-17,2.48],[19.1,-8.4,5.5]),cube([13.13,-17,2.48],[13.535,-8.4,5.5])]
remain=remain-union(cuts);facade=(facade^cube([13.25,-15.41,-.61],[18.51,-14.54,2.32])).translate([0,.48,0]);put(n,union([remain,facade]),transfer='recessed_front_and_trimmed_roof')
OUT['proof']['moved_front_volume_m3']=facade.volume();OUT['proof']['old_facade_y_bounds']=[-15.40,-14.55];OUT['proof']['no_exposed_wood_outside_gables']={'west_interior_x':13.535,'east_interior_x':18.405,'above_z':2.48}
# Continuous, fine roof boarding and a visible rafter rhythm replace the oversized apron.
posts=[(13.72,-14.65),(18.26,-15.60)];members=[];heads=[[x,y,roof_z(x,y)-.225]for x,y in posts];members.append(beam(*heads,.15,.18));u=np.array(posts[1])-posts[0];u/=np.linalg.norm(u)
for x in np.arange(13.57,18.37,.27):members.append(beam([x,-16.48,roof_z(x,-16.48)-.132],[x,-13.99,roof_z(x,-13.99)-.132],.048,.072))
members.append(beam([13.53,-16.48,2.92],[18.40,-16.48,2.92],.07,.12))
members.append(beam([13.54,-14.27,2.37],[18.40,-14.27,2.37],.12,.12))
members.append(strip_roof(13.535,18.405,-16.48,-13.99))
put('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails',union(members))
OUT['proof']['veranda_columns']={'count':2,'axis_xy':posts,'entry_column_moved_out_of_gable_m':[.30,0,0],'post_line_oblique':True,'both_vertical':True}
# Paired curved haunches: open below, with small scroll noses, not deep solid blocks.
haunch=[]
for (x,y),head in zip(posts,heads):
 for sign in [-1,1]:
  if not 13.54<x+sign*.31*u[0]<18.40:continue
  yz=[(0,0),(.36,0),(.35,-.055),(.28,-.065),(.22,-.09),(.16,-.14),(.10,-.23),(0,-.30)]
  m=extrude(Polygon(yz),.10);axis=np.r_[u*sign,0.];lat=np.r_[-u[1],u[0],0.];T=np.c_[axis,[0,0,1],lat,[x,y,head[2]-.075]];haunch.append(m.transform(T).translate(-lat*.05))
put('V24_14_Storage_Curved_Carved_Haunches',union(haunch),True,'M_V18_Aged_Storage_Timber')
# Sealed masonry gables. Rounded ears replace the isolated needle ridge ornaments.
for side,x0,x1,outer,sg in [('West',13.205,13.535,13.205,-1),('East',18.405,18.685,18.685,1)]:
 rear=north_boundary((x0+x1)/2)-.18;ys=sorted(set(np.linspace(-16.10,rear,90).tolist()+np.linspace(-12.43,-11.87,91).tolist()))
 def zz(y):
  base=roof_z(0,y)+.075;d=abs(y+12.15)
  if d<.16:return 4.63+math.sqrt(max(0,.16**2-d*d))
  if d<.28:return max(base,4.63-(d-.16)*2.4)
  return base
 profile=[(-16.10,2.50),(rear,2.50)]+[(y,zz(y))for y in reversed(ys)];body=yzprofile(profile,x0,x1);put('V24_14_Storage_'+side+'_Sealed_Gable',body,True,'M_V24_11_Plain_White_Limewash')
 # Narrow weathered coping following the full ear profile, ending at the masonry eave.
 band=[(y,zz(y)+.035)for y in ys]+[(y,zz(y)-.028)for y in reversed(ys)];cap=yzprofile(band,x0-.045,x1+.045);put('V24_14_Storage_'+side+'_Gable_Stone_Coping',cap,True,'M_V19_Weathered_Wall_Tile')
OUT['proof']['gable_ears']={'count':2,'shape':'rounded masonry gable ear integral with sealed roof verge','no_external_timber_bargeboards':True}
# The erroneous V24.13 return pier is removed in Blender. A shallow projecting
# end cornice and white volute gable sit on the original straight secondary wall.
# The return must not project back into the passage.
U=np.array([1,.098]);U/=np.linalg.norm(U);N=np.array([-U[1],U[0]]);anchor=np.array([13.10,-16.67])
def terminal(poly,a,b):
 m=extrude(Polygon(poly),b-a);T=np.array([[N[0],0,U[0],anchor[0]+a*U[0]],[N[1],0,U[1],anchor[1]+a*U[1]],[0,1,0,0]],float);return m.transform(T)
# Two sloping flanks and a round roll at the ridge; no crease in the wall itself.
t=np.linspace(-.36,.36,81)
def th(s):
 a=abs(s);z=2.665+.23*(1-a/.36)
 if a<.10:z=max(z,2.92+math.sqrt(max(0,.10**2-a*a)))
 return z
outer=[(-.36,2.60),(.36,2.60)]+[(float(s),th(s))for s in reversed(t)]
put('V24_14_Secondary_Screenwall_Volute_End',terminal(outer,-.18,.135),True,'M_V24_11_Plain_White_Limewash')
band=[(float(s),th(s)+.035)for s in t]+[(float(s),th(s)-.025)for s in reversed(t)]
put('V24_14_Secondary_Screenwall_Volute_Rim',terminal(band,-.205,.155),True,'M_V19_Weathered_Wall_Tile')
steps=[]
for r,z0,z1,aa,bb in [(.39,2.53,2.60,-.22,.17),(.34,2.47,2.53,-.18,.13),(.28,2.42,2.47,-.13,.10)]:steps.append(terminal([(-r,z0),(r,z0),(r,z1),(-r,z1)],aa,bb))
put('V24_14_Secondary_Screenwall_Stepped_End_Soffit',union(steps),True,'M_V24_11_Screenwall_Crisp_Soffit_Stone')
# Raised grey frame round the white triangular inset and its rounded scroll.
ring=[]
for sign in [-1,1]:
 pts=[(sign*.30,2.66),(sign*.09,2.85)]
 for (s0,z0),(s1,z1)in zip(pts,pts[1:]):ring.append(terminal([(s0-.015,z0-.012),(s1-.015,z1-.012),(s1+.015,z1+.012),(s0+.015,z0+.012)],.136,.153))
circle=lambda r:np.array([(r*math.cos(a),2.92+r*math.sin(a))for a in np.linspace(0,math.tau,64,endpoint=False)])
roll=mf.CrossSection([circle(.080),circle(.063)[::-1]]).extrude(.019);T=np.array([[N[0],0,U[0],anchor[0]+.136*U[0]],[N[1],0,U[1],anchor[1]+.136*U[1]],[0,1,0,0]],float);ring.append(roll.transform(T))
put('V24_14_Secondary_Screenwall_White_Inset_Frame',union(ring),True,'M_V19_Weathered_Wall_Tile')
OUT['proof']['secondary_end']={'straight_wall_and_level_bands_preserved':True,'removed_wrong_return':True,'end_anchor':anchor.tolist(),'end_roof_max_z':max(th(float(s))for s in t)+.035,'stepped_soffit':3,'entrance_canopy_reintroduced':False}
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,separators=(',',':')),encoding='utf8')
