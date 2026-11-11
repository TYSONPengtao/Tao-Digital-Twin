import sys,json,math
from pathlib import Path
W0=Path(__file__).parent;sys.path[:0]=[str(W0/'np1'),str(W0/'geomlibs'),str(W0/'libs'),str(W0)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from v24_12_geometry import *
D=W0/'v24_12';OUT={'objects':[],'proof':{}}
def solid(v,f,name=''):
 for dec in [8,7,6,5]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];ok=(ff[:,0]!=ff[:,1])&(ff[:,1]!=ff[:,2])&(ff[:,2]!=ff[:,0]);ff=ff[ok];ok=np.linalg.norm(np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]),axis=1)>1e-13;ff=ff[ok]
  m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(vv,dtype=np.float64),np.ascontiguousarray(ff,dtype=np.uint64)))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 raise RuntimeError((name,m.status(),m.volume()))
def put(n,m):
 assert m.status()==mf.Error.NoError and m.volume()>0;dd=m.to_mesh64();OUT['objects'].append({'name':n,'v':np.asarray(dd.vert_properties[:,:3]).tolist(),'f':np.asarray(dd.tri_verts).tolist(),'bodies':len(m.decompose()),'volume_m3':m.volume()});print('PREPARED',n,m.volume(),len(m.decompose()),flush=True)
def cube(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1.]);v=v/np.linalg.norm(v);nn=np.cross(u,v);return mf.Manifold.cube([w,d,float(np.linalg.norm(b-a))],True).transform(np.c_[v,nn,u,(a+b)/2])
def prism(poly,zfn,thick=.055):
 poly=orient(poly,1);dd=mf.CrossSection([np.array(poly.exterior.coords)[:-1]]).extrude(thick).to_mesh64();v=np.asarray(dd.vert_properties[:,:3]).copy();f=np.asarray(dd.tri_verts)
 for p in v:p[2]+=zfn(*p[:2])-thick
 return solid(v,f,'roof prism')
SOUTH=Polygon([(12.82,front(12.82)),(E,front(E)),(E,ridge(E)),(W,ridge(W))]);NORTH=Polygon([(W,ridge(W)),(E,ridge(E))]+[(x,rear(x))for x in np.linspace(E,H[0],80)])
ms=[prism(SOUTH,roof_z),prism(NORTH,roof_z)]
for tri,p in ADAPTERS:ms.append(prism(Polygon(np.array(tri)[:,:2]),lambda x,y,pp=p:float(np.dot([x,y,1],pp))))
roof=mf.Manifold.batch_boolean(ms,mf.OpType.Add);put('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry',roof)
OUT['proof']['roof_polygons']={'south':list(SOUTH.exterior.coords)[:-1],'north':list(NORTH.exterior.coords)[:-1],'adapters':[np.array(t).tolist()for t,p in ADAPTERS]};OUT['proof']['ridge_z']=RIDGE_Z;OUT['proof']['eave_z']=EAVE_Z;OUT['proof']['roof_axis_slope_xy']=AXIS
# Trim the obsolete coarse timber roof deck to the actual new soffit and
# footprint. Merely moving its corner vertices leaves a sloping wooden sheet
# poking through the planar tiles, especially on the curved rear edge.
def under(poly,zfn,z0=-2.0):
 poly=orient(poly,1);dd=mf.CrossSection([np.array(poly.exterior.coords)[:-1]]).extrude(1).to_mesh64();v=np.asarray(dd.vert_properties[:,:3]).copy();f=np.asarray(dd.tri_verts)
 for p in v:p[2]=z0+p[2]*(zfn(*p[:2])-z0)
 return solid(v,f,'timber envelope')
support=[under(SOUTH,lambda x,y:roof_z(x,y)-.067),under(NORTH,lambda x,y:roof_z(x,y)-.067)]
for tri,pp in ADAPTERS:support.append(under(Polygon(np.array(tri)[:,:2]),lambda x,y,p=pp:float(np.dot([x,y,1],p))-.067))
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';dd=np.load(D/(n+'.npz'));tv=np.array([timber(p)for p in dd['v']]);tm=solid(tv,dd['f'],n);bound=mf.Manifold.batch_boolean(support+[cube([10,-18,-2],[20,-7,2.55])],mf.OpType.Add);tm=tm^bound
# Keep actual manifold vertex identities. Global coordinate welding would
# merge distinct touching timber cells and destroy valid closed topology.
td=tm.to_mesh64();test=mf.Manifold(mf.Mesh64(np.array(td.vert_properties[:,:3],dtype=np.float32).astype(np.float64,order='C'),np.array(td.tri_verts,dtype=np.uint64,order='C')));assert test.status()==mf.Error.NoError and test.volume()>0
put(n,tm)
OUT['proof']['timber_deck_clipped_to_new_soffit']=True
# Roof-level edges move within the vertical gable planes. The foundation,
# curved rear plan and lower door openings remain on their accepted positions.
for n,fn in [('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry',masonry),('SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry',masonry),('V24_11_Storage_Curved_Rear_Interior_White_Finish',lambda p:np.array([p[0],p[1],roof_z(*p[:2])-.125])if p[2]>2 else p)]:
 dd=np.load(D/(n+'.npz'));v=np.array([fn(p)for p in dd['v']]);m=solid(v,dd['f'],n);put(n,m)
posts=[(13.42,-14.65),(18.26,-15.60)];heads=[];members=[]
for x,y in posts:heads.append([x,y,roof_z(x,y)-.245])
members.append(beam(heads[0],heads[1],.19,.23));u=np.array(posts[1])-posts[0];u/=np.linalg.norm(u)
for i,(x,y)in enumerate(posts):
 for sg in[-1,1]:
  p=np.array([x,y])+sg*.42*u
  if 13.2<p[0]<18.57:members.append(beam([x,y,roof_z(x,y)-.635],[*p,roof_z(*p)-.26],.075,.095))
 members.append(cube([x-.15,y-.16,heads[i][2]-.09],[x+.15,y+.16,heads[i][2]+.105]))
for x in np.arange(12.95,18.77,.24):members.append(beam([x,-14.9,roof_z(x,-14.9)-.12],[x,front(x),EAVE_Z-.12],.045,.06))
members.append(beam([12.82,front(12.82),EAVE_Z-.105],[E,front(E),EAVE_Z-.105],.09,.13))
members.append(beam([W,ridge(W),RIDGE_Z-.18],[E,ridge(E),RIDGE_Z-.18],.14,.18))
put('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails',mf.Manifold.batch_boolean(members,mf.OpType.Add))
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('DONE',flush=True)
