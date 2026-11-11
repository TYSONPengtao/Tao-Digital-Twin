from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import box,mapping
D=W/'v24_35';pieces=[];ZLOW=-.3;ZHIGH=5.2;scope=box(7.,-12.2,19.3,1.2)
for r in json.loads((D/'Envelope_Index.json').read_text()):
 a=np.load(D/r['file']);t=a['v'][a['f'],:2];area=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));pp=shapely.polygons(t)
 if r['wall']:p=shapely.union_all(shapely.buffer(pp,.22))
 else:p=shapely.union_all(pp[area>1e-10]).buffer(.18)
 pieces.append(p)
mask=shapely.union_all(pieces).intersection(scope).buffer(0);(D/'Repair_Envelope.geojson').write_text(json.dumps(mapping(mask)));shapely.prepare(mask)
def polys(g):return[g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon']
def zclip(p,z,above):
 out=[]
 for a,b in zip(p,np.roll(p,-1,axis=0)):
  ia=a[2]>=z if above else a[2]<=z;ib=b[2]>=z if above else b[2]<=z
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
 return np.array(out).reshape(-1,5)
rows=[];remove=[];proof=[]
for r in json.loads((D/'Region_Index.json').read_text()):
 if not r['photo']:continue
 a=np.load(D/r['file']);v=a['v'];f=a['f'];uv=a['uv'];mi=a['mi'];t=v[f];lo=t.min(1);hi=t.max(1);possible=(hi[:,2]>ZLOW)&(lo[:,2]<ZHIGH)&(hi[:,0]>7)&(lo[:,0]<19.3)&(hi[:,1]>-12.2)&(lo[:,1]<1.2);pp=shapely.polygons(t[:,:,:2]);hits=np.zeros(len(f),bool);hits[possible]=shapely.intersects(mask,pp[possible]);candidates=np.flatnonzero(hits)
 if not len(candidates):continue
 out=[t[~hits].reshape(-1,3)];tex=[uv[~hits].reshape(-1,2)];mats=[mi[~hits]];removed_area=0.;vertical=0
 def add(poly,mat):
  if len(poly)<3:return
  for i in range(1,len(poly)-1):
   tri=poly[[0,i,i+1]];out.append(tri[:,:3]);tex.append(tri[:,3:]);mats.append(np.array([mat],np.int32))
 for i in candidates:
  p=np.c_[t[i],uv[i]];add(zclip(p,ZLOW,False),mi[i]);add(zclip(p,ZHIGH,True),mi[i]);band=zclip(zclip(p,ZLOW,True),ZHIGH,False)
  if len(band)<3:continue
  xy=band[:,:2];g=shapely.Polygon(xy)
  if g.area<1e-12:
   vertical+=1
   if not shapely.contains_xy(mask,*xy.mean(0)):add(band,mi[i])
   continue
  keep=g.difference(mask);orig=t[i];inv=np.linalg.inv(np.vstack([orig[:,:2].T,np.ones(3)]))
  for p2 in polys(keep):
   if p2.area<1e-12:continue
   for tri in shapely.constrained_delaunay_triangles(p2).geoms:
    q=np.array(tri.exterior.coords[:-1]);bc=np.c_[q,np.ones(3)]@inv.T;xyz=bc@orig;quv=bc@uv[i]
    if np.dot(np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]),np.cross(orig[1]-orig[0],orig[2]-orig[0]))<0:xyz=xyz[::-1];quv=quv[::-1]
    add(np.c_[xyz,quv],mi[i])
 vv=np.concatenate(out);uu=np.concatenate(tex);mm=np.concatenate(mats);ff=np.arange(len(vv)).reshape(-1,3);tri=vv[ff];valid=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>1e-9;vv=tri[valid].reshape(-1,3);uu=uu.reshape(-1,3,2)[valid];mm=mm[valid]
 if not len(mm):remove.append(r['name']);result=0
 else:
  vv,iv=np.unique(vv,axis=0,return_inverse=True);ff=iv.reshape(-1,3).astype(np.int32);fn='CLEAN_'+Path(r['file']).stem+'.npz';np.savez_compressed(D/fn,v=vv,f=ff,uv=uu,mi=mm);rows.append({**r,'file':fn,'vertices':len(vv),'triangles':len(ff)});result=len(ff)
 proof.append({'name':r['name'],'source_triangles':len(f),'intersecting_triangles':len(candidates),'output_triangles':result,'vertical_degenerate_xy_cases':vertical});print('CLEAN',r['name'],len(f),'->',result,'tested',len(candidates),flush=True)
(D/'Prepared_Geometry.json').write_text(json.dumps({'changed':rows,'remove':remove,'proof':proof,'envelope':{'plan_area_m2':mask.area,'scope_xy':[7,-12.2,19.3,1.2],'z_min':ZLOW,'z_max':ZHIGH,'roof_clearance_m':.18,'wall_clearance_m':.22,'source':'Complete native kitchen/storage eaves and curved courtyard wall, limited to annotated local region'},'native_masonry_roof_pipes_preserved':True},indent=2));print('PREP_DONE',len(rows),'modified',len(remove),'removed',flush=True)
