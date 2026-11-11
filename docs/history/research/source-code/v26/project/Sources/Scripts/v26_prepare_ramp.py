from pathlib import Path
import sys,json,collections
W=Path(__file__).parent;D=W/'v26';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,manifold3d as mf
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union,nearest_points
from scipy.spatial import cKDTree
from v24_16_common import solid,union,section
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};SI=json.loads((D/'Original_Source_Index.json').read_text('utf8'));OUT={'objects':[],'proof':{}}
def polys(p):return [p]if p.geom_type=='Polygon'else[q for q in getattr(p,'geoms',[])if q.geom_type=='Polygon' and q.area>1e-11]
def prism(p,z0,z1):
 ms=[]
 for q in polys(p):
  m=section(list(q.exterior.coords)[:-1],z1-z0).translate([0,0,z0])
  for h in q.interiors:m-=section(list(h.coords)[:-1],z1-z0+.02).translate([0,0,z0-.01])
  ms.append(m)
 return union(ms)
def top(t,threshold=.55):
 no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return no[:,2]>threshold*np.linalg.norm(no,axis=1)
def sample(t,xy):
 xy=np.array(xy);A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];Q=xy-t[:,0,:2];det=np.cross(A,B);safe=np.where(abs(det)>1e-12,det,1);u=np.cross(Q,B)/safe;w=np.cross(A,Q)/safe;ok=(abs(det)>1e-12)&(u>=-3e-5)&(w>=-3e-5)&(u+w<=1.00003)
 if ok.any():
  ix=np.flatnonzero(ok);z=t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]);k=ix[np.argmax(z[ix])];return float(z[k])
 # Boundary evaluation can lie a few ulps outside a source face. Use nearest
 # triangle, with clamped barycentric coordinates, only for seam interpolation.
 p=shapely.points(float(xy[0]),float(xy[1]));ps=shapely.polygons(t[:,:,:2]);dist=shapely.distance(ps,p);k=int(np.argmin(dist));q=nearest_points(Polygon(t[k,:,:2]),Point(xy))[0];Q=np.array(q.coords[0])-t[k,0,:2];u=np.cross(Q,B[k])/safe[k];w=np.cross(A[k],Q)/safe[k];return float(t[k,0,2]+u*(t[k,1,2]-t[k,0,2])+w*(t[k,2,2]-t[k,0,2]))
def clip(a,region,inside):
 t=a['v'][a['f']];uv=a['uv'];fpolys=shapely.polygons(t[:,:,:2]);area=shapely.area(fpolys);whole=shapely.covers(region,fpolys);hit=shapely.intersects(region,fpolys);keep=whole if inside else ~hit
 keep[area<1e-11]=False if inside else ~shapely.contains_xy(region,t[area<1e-11].mean(1)[:,0],t[area<1e-11].mean(1)[:,1])
 vv=list(t[keep]);uu=list(uv[keep]);changed=0
 for j in np.flatnonzero(hit&~whole&(area>1e-11)):
  g=fpolys[j].intersection(region)if inside else fpolys[j].difference(region)
  A=t[j,1,:2]-t[j,0,:2];B=t[j,2,:2]-t[j,0,:2];det=np.cross(A,B)
  for p in polys(g):
   for tr in shapely.constrained_delaunay_triangles(p).geoms:
    xy=np.array(tr.exterior.coords)[:3];Q=xy-t[j,0,:2];s=np.cross(Q,B)/det;w=np.cross(A,Q)/det;v=t[j,0]+s[:,None]*(t[j,1]-t[j,0])+w[:,None]*(t[j,2]-t[j,0]);quv=uv[j,0]+s[:,None]*(uv[j,1]-uv[j,0])+w[:,None]*(uv[j,2]-uv[j,0]);
    if np.dot(np.cross(v[1]-v[0],v[2]-v[0]),np.cross(t[j,1]-t[j,0],t[j,2]-t[j,0]))<0:v=v[::-1];quv=quv[::-1]
    if np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))>1e-11:vv.append(v);uu.append(quv);changed+=1
 v=np.array(vv).reshape(-1,3);return v,np.arange(len(v),dtype=np.int32).reshape(-1,3),np.array(uu),int(keep.sum()),changed

P0=np.array([-14.8813,-8.4793]);P1=np.array([-12.5895,-12.7096]);L=np.linalg.norm(P1-P0);u=(P1-P0)/L;inn=np.array([-u[1],u[0]])
zone=Polygon([P0+u*s+inn*d for s,d in [(-.12,-3.2),(L+.12,-3.2),(L+.12,-.08),(-.12,-.08)]])
n='V24_31_Continuous_Gray_Road_And_Storage_Approach';a=np.load(D/I[n]['file']);native=solid(a['v'],a['f'],n);nt=a['v'][a['f']];nt=nt[top(nt)];nplan=unary_union([Polygon(p[:,:2])for p in nt]).buffer(0)
raw=[];sr=[]
for r in SI['rows']:
 a=np.load(D/r['file']);t=a['v'][a['f']];ok=top(t)&(t[:,:,0].max(1)>-19)&(t[:,:,0].min(1)<-11)&(t[:,:,1].max(1)>-16)&(t[:,:,1].min(1)<-7)&(t[:,:,2].max(1)<.1)&(t[:,:,2].min(1)>-2)
 if not ok.any():continue
 b={'v':t[ok].reshape(-1,3),'f':np.arange(ok.sum()*3).reshape(-1,3),'uv':a['uv'][ok]};sr.append((r,b));raw.extend(t[ok])
raw=np.array(raw);coverage=unary_union([Polygon(p[:,:2])for p in raw]);region=zone.intersection(nplan).intersection(coverage).buffer(0)
parts=sorted(polys(region),key=lambda p:p.area,reverse=True);region=parts[0];assert region.area>6,(region.area,'ramp patch too small')
assert all(p.area<.01 for p in parts[1:]),[p.area for p in parts]
photo=[];kept_vertices=0
for r,a in sr:
 v,f,uv,keep,cut=clip(a,region,True)
 if not len(f):continue
 fn=f'RAMP_PHOTO_{len(photo)}.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv,mi=np.zeros(len(f),np.int32));row={'name':f'V26_Original_Site_Entrance_Ramp_{len(photo)}','file':fn,'materials':[f'M_V14_ORIGINAL_EXTERIOR_{SI["rows"].index(r)}'],'new':True,'source_id':r['source_id'],'source_texture_sha256':r['texture_sha256'],'whole_source_triangles':keep,'clipped_boundary_triangles':cut,'photo_geometry':'original survey-to-local transform only; no height deformation'};photo.append(row);OUT['objects'].append(row);kept_vertices+=keep*3
# One displayed owner at every original-photo overlap. All source outside the
# recovered ramp footprint retains its vertex positions and UV interpolation.
for r in I.values():
 if 'SITE_V14_ORIGINAL_EXTERIOR_'not in r['name']:continue
 a=np.load(D/r['file']);v,f,uv,keep,cut=clip(a,region,False)
 if len(f)==len(a['f'])and cut==0:continue
 fn='RAMP_TRIM_'+r['name']+'.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv,mi=np.zeros(len(f),np.int32));OUT['objects'].append({'name':r['name'],'file':fn,'materials':r['materials'],'new':False,'reason':'Remove duplicate photographic coverage inside recovered ramp only'})
# Remove the synthetic wedge exactly beneath the recovered source patch.
# Refine only the 0.85m transition strip, leaving the remaining road untouched.
belt=region.buffer(.85,join_style=2).difference(region);far=native-prism(region.buffer(.85,join_style=2),-5.1,1.1);near=(native^prism(belt,-5.1,1.1)).refine_to_length(.18)
mm=near.to_mesh64();v=np.array(mm.vert_properties[:,:3]);f=np.array(mm.tri_verts);bound=region.boundary
# Insert every original photo boundary node into the adjacent synthetic edge.
# Uniform refinement alone leaves T junctions at abrupt scan height changes.
# The edge split is shared by both incident faces, preserving a closed solid.
pv=[];pf=[];po=0
for r in photo:
 aa=np.load(D/r['file']);pv.extend(aa['v']);pf.extend(aa['f']+po);po+=len(aa['v'])
pv,pi=np.unique(np.round(np.array(pv),7),axis=0,return_inverse=True);pf=pi[np.array(pf)];pe=collections.Counter(tuple(sorted((int(a),int(b))))for tri in pf for a,b in zip(tri,np.roll(tri,-1)));shore=np.array([pv[k,:2]for e,c in pe.items()if c==1 for k in e]);shore=np.unique(shore,axis=0);splits={};vv=v.tolist()
for face in f:
 for a,b in zip(face,np.roll(face,-1)):
  key=tuple(sorted((int(a),int(b))))
  if key in splits:continue
  A=v[key[0]];B=v[key[1]];ab=B[:2]-A[:2];ll=float(ab@ab)
  if ll<1e-12:continue
  if max(bound.distance(Point(A[:2])),bound.distance(Point(B[:2])),bound.distance(Point((A[:2]+B[:2])/2)))>2e-6:continue
  if abs(sample(nt,A[:2])-A[2])>.015 or abs(sample(nt,B[:2])-B[2])>.015:continue
  ts=((shore-A[:2])@ab)/ll;qq=A[:2]+ts[:,None]*ab;ok=(ts>1e-6)&(ts<1-1e-6)&(np.linalg.norm(qq-shore,axis=1)<2e-6);ids=[]
  for t in np.sort(np.unique(np.round(ts[ok],9))):
   ids.append(len(vv));vv.append((A+t*(B-A)).tolist())
  if ids:splits[key]=ids
ff=[]
for face in f:
 ring=[]
 for a,b in zip(face,np.roll(face,-1)):
  ring.append(int(a));key=tuple(sorted((int(a),int(b))));seq=splits.get(key,[]);ring.extend(seq if a<b else seq[::-1])
 if len(ring)==3:ff.append(list(face));continue
 centre=len(vv);vv.append(v[face].mean(0).tolist())
 for a,b in zip(ring,np.roll(ring,-1)):ff.append([int(a),int(b),centre])
v=np.array(vv);f=np.array(ff,np.int32);print('PHOTO_EDGE_NODES_INSERTED',len(v)-len(mm.vert_properties),len(splits),flush=True)
# Densely cache seam coordinates and exact heights once; nearest seam
# interpolation uses the source's actual top triangle, never a flat plane.
edges=[]
for ring in [region.exterior]+list(region.interiors):
 coords=np.array(ring.coords)
 for A,B in zip(coords,coords[1:]):
  dist=np.linalg.norm(B-A);edges.extend(A+(B-A)*t for t in np.linspace(0,1,max(2,int(np.ceil(dist/.025))+1)))
edges=np.array(edges);delta=np.array([sample(raw,p)-sample(nt,p)for p in edges]);kd=cKDTree(edges);changes=[]
for j,p in enumerate(v):
 dist,ii=kd.query(p[:2]);
 if dist>.851:continue
 h=sample(nt,p[:2]);depth=h-p[2]
 if depth>.30:continue
 dd=float(delta[ii])
 if dist<.03:
  q=np.array(nearest_points(bound,Point(p[:2]))[0].coords[0]);dist=float(np.linalg.norm(p[:2]-q));dd=sample(raw,q)-sample(nt,q)
 t=np.clip(1-dist/.85,0,1);w=t*t*(3-2*t);vertical=np.clip(1-depth/.3,0,1);dz=float(dd*w*vertical);v[j,2]+=dz
 if abs(dz)>1e-6:changes.append(dz)
near=solid(v,f,'ramp transition');road=far+near
zero_parts=[p for p in road.decompose()if abs(p.volume())<1e-8];road=union([p for p in road.decompose()if p.volume()>1e-8])
print('ROAD_PARTS',len(native.decompose()),len(road.decompose()),'zero volume Boolean interface sheets removed',len(zero_parts),flush=True)
mm=road.to_mesh64();v=np.array(mm.vert_properties[:,:3]);f=np.array(mm.tri_verts);fn='RAMP_NEW_APPROACH.npz';np.savez_compressed(D/fn,v=v,f=f)
OUT['objects'].append({'name':n,'file':fn,'materials':I[n]['materials'],'new':False,'reason':'Cut only recovered source footprint; smooth 0.85m seam belt to original road heights'})
# The photographic ground is a surface, backed by a separate visible concrete
# body formed from the same top heights, 0.18m lower, with side closure.
v=np.vstack([np.load(D/r['file'])['v']for r in photo]);f=[];offset=0
for r in photo:
 a=np.load(D/r['file']);f.extend((a['f']+offset).tolist());offset+=len(a['v'])
v,ix=np.unique(np.round(v,7),axis=0,return_inverse=True);f=ix[np.array(f)];edges0=collections.Counter(tuple(sorted((int(x),int(y))))for tri in f for x,y in zip(tri,np.roll(tri,-1)));oriented={tuple(sorted((int(x),int(y)))):(int(x),int(y))for tri in f for x,y in zip(tri,np.roll(tri,-1))}
N=len(v);vv=np.vstack([v,v+[0,0,-.18]]);ff=f.tolist()+(f[:,::-1]+N).tolist()
for e,c in edges0.items():
 if c==1:
  a,b=oriented[e];ff.extend([[b,a,a+N],[b,a+N,b+N]])
back=solid(vv,ff,'original ramp backing');a=back.to_mesh64();vb=np.array(a.vert_properties[:,:3]);fb=np.array(a.tri_verts);tb=vb[fb];no=np.cross(tb[:,1]-tb[:,0],tb[:,2]-tb[:,0]);keep=no[:,2]<.55*np.linalg.norm(no,axis=1)
fn='RAMP_BACKING.npz';np.savez_compressed(D/fn,v=vb,f=fb[keep]);OUT['objects'].append({'name':'V26_Original_Ramp_Concrete_Back_And_Sides','file':fn,'materials':['M_V12_Road_Concrete'],'new':True,'reason':'18cm backing follows original source relief; top owned by photographic surface','collision_solid_file':'RAMP_BACKING_CLOSED.npz'})
np.savez_compressed(D/'RAMP_BACKING_CLOSED.npz',v=vb,f=fb)
OUT['proof']={'original_source':SI['source'],'original_source_sha256':SI['sha256'],'region':region.__geo_interface__,'recovered_area_m2':region.area,'original_whole_triangle_vertices_unchanged':kept_vertices,'source_photo_uv_interpolation_only_at_clip_boundary':True,'source_heights_unchanged':True,'synthetic_approach_overlap_after_m2':0.0,'seam_transition_width_m':.85,'maximum_transition_height_change_m':max(map(abs,changes),default=0),'boundary_delta_range_m':[float(delta.min()),float(delta.max())],'backing_closed_components':len(back.decompose()),'backing_closed_volume_m3':back.volume(),'note':'Existing photo ramp only. Source boundary flaps behind the gate excluded at 8cm outside the gate datum; seam adjusts synthetic road, not original ramp.'}
(D/'Prepared_Ramp.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2),encoding='utf8');print('RAMP_DONE',region.area,len(OUT['objects']),max(map(abs,changes),default=0),flush=True)
