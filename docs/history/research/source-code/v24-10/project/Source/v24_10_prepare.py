"""Closed replacement storage plot geometry, derived from the original 3dm section."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf,shapely
from shapely.geometry import Polygon,LineString,Point,box
from shapely.geometry.polygon import orient
from scipy.spatial import cKDTree
D=W/'v24_10';plan=json.loads((D/'AsBuilt_Plan.json').read_text());poly=orient(Polygon(plan['outline']),1)
out={'objects':[],'plot':plan,'guard_bays':[],'drain_stations':[]}
def prism(p,z,h):
 p=orient(p,1)
 return mf.CrossSection([np.array(p.exterior.coords)[:-1]]).extrude(h).translate([0,0,z])
def cube(lo,sz):return mf.Manifold.cube(sz).translate(lo)
def native(n):
 d=np.load(D/('BASE_'+n+'.npz'));v,inv=np.unique(np.round(d['v'],7),axis=0,return_inverse=True);f=inv[d['f']]
 m=mf.Manifold(mf.Mesh64(v,f.astype(np.uint64)));assert m.status()==mf.Error.NoError,(n,m.status());return m
def data(m):
 assert m.status()==mf.Error.NoError and m.volume()>0,(m.status(),m.volume())
 d=m.to_mesh64();return {'v':np.asarray(d.vert_properties[:,:3]).tolist(),'f':np.asarray(d.tri_verts).tolist()}
def put(n,parts,new=False,uv='metric'):
 out['objects'].append({'name':n,'new':new,'uv':uv,'parts':[{'material':ma,**data(m)}for m,ma in parts]})
def beam(a,b,w,h):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);vv=np.cross(u,[0,0,1.])
 if np.linalg.norm(vv)<1e-8:vv=np.array([1.,0,0])
 vv/=np.linalg.norm(vv);nn=np.cross(u,vv);R=np.eye(4);R[:3,:3]=np.c_[vv,nn,u];R[:3,3]=(a+b)/2
 return mf.Manifold.cube([w,h,float(np.linalg.norm(b-a))],True).transform(R[:3])
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
base=native('SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry')-cube([12.7,-21,-7],[11,11.70,9])
newbase=prism(poly,-4.65,4.242);base=base+newbase
lower=base^cube([5,-22,-8],[20,25,6.95]);upper=base-lower
put('SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry',[(base,'M_V18_Storage_Rubble')],uv='base_band')
out['base']={'closed_volume_m3':base.volume(),'connected_bodies':len(base.decompose()),'bounds':poly.bounds}
room=orient(poly.intersection(box(13.3,-14.85,18.65,-8.7)),1);gallery=orient(poly.intersection(box(13.3,-18,18.65,-14.85)),1);outer=orient(poly.intersection(box(18.65,-18,22,-8.7)),1)
for n,p,z,h in [('SITE_V14_INNER_STORAGE_FLOOR_Geometry',room,-.52,.12),('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry',gallery,-.425,.031),('SITE_V14_OUTER_STORAGE_FLOOR_Geometry',outer,-.55,.15)]:put(n,[(prism(p,z,h),'M_V21_Storage_Worn_Cement')])
out['floor_polygons']={k:list(p.exterior.coords)[:-1]for k,p in [('room',room),('gallery',gallery),('outer',outer)]}
# Traverse the actual exterior from the south-west entry to the north-east canopy return.
pts=np.array(poly.exterior.coords)[:-1];start=int(np.argmin(pts[:,1]));pts=np.roll(pts,-start,axis=0);route=[pts[0]]
for p in pts[1:]:
 if p[0]<18.65:
  a=route[-1];p=a+(p-a)*(18.65-a[0])/(p[0]-a[0]);route.append(p);break
 route.append(p)
path=LineString(route)
fy=lambda x:float(route[0][1]+(route[1][1]-route[0][1])*(x-route[0][0])/(route[1][0]-route[0][0]))
front=LineString([[13.55,fy(13.55)],[18.65,fy(18.65)]])
outerpath=LineString([[18.65,fy(18.65)]]+[list(p)for p in route[1:]])
ends=[front.interpolate(front.length*i/3).coords[0]for i in range(4)]+[outerpath.interpolate(outerpath.length*i/4).coords[0]for i in range(1,5)]
parts=[];postxy=[]
for aa,bb in zip(ends[:-1],ends[1:]):
 aa=np.array(aa);bb=np.array(bb);u=(bb-aa)/np.linalg.norm(bb-aa);no=np.array([-u[1],u[0]]);aa+=no*.075;bb+=no*.075;postxy.extend([aa,bb]);a=aa+u*.08;b=bb-u*.08;L=float(np.linalg.norm(b-a));mat='M_V18_Storage_Stone_Guard'
 for z,w,h in [(-.345,.105,.155),(-.03,.077,.52),(.51,.105,.145)]:parts.append(beam([*a,z],[*b,z],w,h))
 # Upper stone band has two actual six-sided openings, as in the real photograph.
 band=beam([*a,.337],[*b,.337],.078,.294)
 for ss in [.27,.73]:
  cc=a+(b-a)*ss;hw=min(.32,L*.17);zlo=.276;zhi=.431;be=.043
  pr=np.array([[-hw+be,zlo],[hw-be,zlo],[hw,zlo+be],[hw,zhi-be],[hw-be,zhi],[-hw+be,zhi],[-hw,zhi-be],[-hw,zlo+be]])
  hole=mf.CrossSection([pr]).extrude(.30);R=np.array([[u[0],0,no[0],cc[0]-no[0]*.15],[u[1],0,no[1],cc[1]-no[1]*.15],[0,1,0,0]])
  band=band-hole.transform(R)
 parts.append(band)
 for s in [-1,1]:
  oo=no*s*.043
  for z in [-.253,.194]:parts.append(beam([*(a+oo),z],[*(b+oo),z],.018,.020))
  for k in [.04,.96]:
   cc=a+(b-a)*k+oo;parts.append(beam([*cc,-.25],[*cc,.193],.018,.018))
 out['guard_bays'].append({'a':a.tolist(),'b':b.tolist(),'normal':no.tolist(),'length':L,'openings':2})
for x,y in {tuple(np.round(p,7))for p in postxy}:
 for z,w,h in [(-.410,.198,.112),(-.322,.154,.913),(.57,.188,.07)]:parts.append(cube([x-w/2,y-w/2,z],[w,w,h]))
put('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry',[(union(parts),'M_V18_Storage_Stone_Guard')],uv='guard_atlas')
# Outer metal lean-to follows the registered curved plinth, with thin attached edge beams.
co=np.array([-.0292431454,-.00117201994,2.58988663]);hm=lambda p:float(np.dot([*p,1],co));pv=np.array(outer.exterior.coords)[:-1]
roofverts=np.c_[pv,np.array([hm(p)-.025 for p in pv])];cross=mf.CrossSection([pv]).extrude(.025).translate([0,0,0]);md=cross.to_mesh64();vs=np.asarray(md.vert_properties[:,:3]).copy();vs[:,2]+=np.c_[vs[:,:2],np.ones(len(vs))]@co-.025
sheet=mf.Manifold(mf.Mesh64(np.array(vs,dtype=np.float64,order='C',copy=True),np.array(md.tri_verts,dtype=np.uint64,order='C',copy=True)));metal=[sheet]
for a,b in zip(pv,np.roll(pv,-1,axis=0)):metal.append(beam([*a,hm(a)-.041],[*b,hm(b)-.041],.045,.058))
for y in np.arange(outer.bounds[1]+.10,outer.bounds[3]-.10,.48):
 seg=outer.intersection(LineString([[18.60,y],[22,y]]))
 if seg.is_empty or seg.geom_type!='LineString':continue
 a,b=np.array(seg.coords[0]),np.array(seg.coords[-1]);metal.append(beam([*a,hm(a)-.045],[*b,hm(b)-.045],.034,.05))
 for dy in [0,.16,.32]:
  s=outer.intersection(LineString([[18.60,y+dy],[22,y+dy]]))
  if s.is_empty or s.geom_type!='LineString':continue
  c,d=np.array(s.coords[0]),np.array(s.coords[-1]);metal.append(beam([*c,hm(c)+.004],[*d,hm(d)+.004],.018,.008))
for p in [route[1],route[3],route[5],route[-1]]:metal.append(beam([*p,-.404],[*p,hm(p)-.025],.055,.055))
put('SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY_Geometry',[(union(metal),'M_V18_Metal_Weathered')])
# Source terrain evidence for the vacated over-sized plinth and the road foot junction.
d=np.load(D/'AsBuilt_All_LOCAL.npz');v=d['v'].astype(float);f=d['f'];t=v[f];cp=t.mean(1);nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1),1e-20)[:,None]
ma=(cp[:,0]>12.95)&(cp[:,0]<23.4)&(cp[:,1]>-19.6)&(cp[:,1]<-8.4)&(cp[:,2]<-1.0)&(abs(nn[:,2])>.18)
patchmask=poly.buffer(2.55,join_style=2).difference(poly.buffer(.43,join_style=2)).intersection(box(12.97,-19.55,23.35,-8.50))
sel=ma&shapely.contains_xy(patchmask,cp[:,0],cp[:,1]);ff=f[sel];ids,inv=np.unique(ff,return_inverse=True)
np.savez_compressed(D/'Restored_Original_Ground.npz',v=d['v'][ids],f=inv.reshape(-1,3),uv=d['uv'][ids])
out['terrain']={'source_faces':int(sel.sum()),'all_top_uv_unchanged':True,'local_patch_bounds':list(patchmask.bounds),'mask_outer':list(patchmask.exterior.coords)if patchmask.geom_type=='Polygon'else None}
# A continuous closed gutter at source ground grades replaces the displaced old strips.
ground=(cp[:,2]<-1.8)&(abs(nn[:,2])>.45)&(cp[:,0]>12)&(cp[:,0]<24)&(cp[:,1]>-20)&(cp[:,1]<-7.8)
gp=cp[ground];tree=cKDTree(gp[:,:2])
def grade(p):
 dist,ii=tree.query(p,k=20);qq=gp[ii];A=np.c_[qq[:,:2]-p,np.ones(len(qq))];weights=1/np.maximum(.10,dist)**2
 c=np.linalg.lstsq(A*np.sqrt(weights[:,None]),qq[:,2]*np.sqrt(weights),rcond=None)[0]
 if abs(c[0])>.8 or abs(c[1])>.8:return float(np.average(qq[:,2],weights=weights))
 return float(c[2])
norms=[]
for a,b in zip(route[:-1],route[1:]):u=(b-a)/np.linalg.norm(b-a);norms.append(np.array([u[1],-u[0]]))
ns=[norms[0]]+[(norms[i-1]+norms[i])/(1+float(norms[i-1]@norms[i]))for i in range(1,len(norms))]+[norms[-1]]
zs=[grade(p+no*.52)for p,no in zip(route,ns)];gut=[]
for i,(a,b)in enumerate(zip(route[:-1],route[1:])):
 for lo,hi,top,bottom in [(-.025,.08,-.015,-.36),(.08,.33,-.245,-.36),(.33,.43,-.015,-.36),(.43,.62,0,-.10)]:
  vv=np.array([[*(a+ns[i]*lo),zs[i]+bottom],[*(b+ns[i+1]*lo),zs[i+1]+bottom],[*(b+ns[i+1]*hi),zs[i+1]+bottom],[*(a+ns[i]*hi),zs[i]+bottom],[*(a+ns[i]*lo),zs[i]+top],[*(b+ns[i+1]*lo),zs[i+1]+top],[*(b+ns[i+1]*hi),zs[i+1]+top],[*(a+ns[i]*hi),zs[i]+top]])
  fs=np.array([[0,3,2],[0,2,1],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64)[:,::-1].copy();gut.append(mf.Manifold(mf.Mesh64(vv,fs)))
 out['drain_stations'].append({'a':a.tolist(),'b':b.tolist(),'grade_a':zs[i],'grade_b':zs[i+1],'clear_width_m':.25,'depth_m':.23})
put('SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER_Geometry',[(union(gut),'M_V19_Perimeter_Road_Shoulder')])
out['removed']=['SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_CONTINUATION_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TILE_COURSES_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TIMBER_CONTINUATION_Geometry']
(D/'Prepared_Geometry.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8');print(json.dumps({'objects':len(out['objects']),'plot_area_m2':poly.area,'base':out['base'],'terrain':{k:val for k,val in out['terrain'].items()if k!='mask_outer'},'guard_bays':len(out['guard_bays']),'route':len(route)}),flush=True)
