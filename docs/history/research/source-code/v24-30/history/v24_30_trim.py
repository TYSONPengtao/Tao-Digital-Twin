import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from shapely.geometry import shape,Polygon,Point
from shapely.ops import triangulate
D=W/'v24_30';out=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));idx={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};n='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';a=np.load(D/idx[n]['file']);v=a['v'];f=a['f'];uv=a['uv'];mi=a['mi'];trim=shape(out['trim_footprint']);lo=np.array(trim.bounds[:2]);hi=np.array(trim.bounds[2:]);vv=v.tolist();ff=[];mm=[];uu=[];kept=[];cache={tuple(np.round(p,8)):i for i,p in enumerate(v)}
def add(p3,tex,mat):
 ids=[]
 for p in p3:
  key=tuple(np.round(p,8))
  if key not in cache:cache[key]=len(vv);vv.append(p.tolist())
  ids.append(cache[key])
 if len(set(ids))==3:ff.append(ids);mm.append(mat);uu.append(tex)
for k,(face,mat,tex)in enumerate(zip(f,mi,uv)):
 t=v[face];xy=t[:,:2]
 if ((xy.max(0)<lo)|(xy.min(0)>hi)).any():ff.append(face);mm.append(mat);uu.append(tex);kept.append(k);continue
 A=xy[1]-xy[0];B=xy[2]-xy[0];det=A[0]*B[1]-A[1]*B[0]
 if abs(det)<1e-12:
  if all(trim.covers(Point(p))for p in xy):continue
  ff.append(face);mm.append(mat);uu.append(tex);kept.append(k);continue
 poly=Polygon(xy)
 if not trim.intersects(poly):ff.append(face);mm.append(mat);uu.append(tex);kept.append(k);continue
 diff=poly.difference(trim)
 if diff.is_empty:continue
 ps=[diff]if diff.geom_type=='Polygon'else [p for p in diff.geoms if p.geom_type=='Polygon']
 for part in ps:
  for tri in triangulate(part):
   if tri.area<1e-12 or not part.covers(tri.representative_point()):continue
   q=np.array(tri.exterior.coords)[:3];Q=q-xy[0];u=(Q[:,0]*B[1]-Q[:,1]*B[0])/det;w=(A[0]*Q[:,1]-A[1]*Q[:,0])/det;p3=t[0]+u[:,None]*(t[1]-t[0])+w[:,None]*(t[2]-t[0]);tuv=tex[0]+u[:,None]*(tex[1]-tex[0])+w[:,None]*(tex[2]-tex[0])
   if det<0:p3=p3[::-1];tuv=tuv[::-1]
   add(p3,tuv,mat)
fn='TRIMMED_SOIL.npz';np.savez_compressed(D/fn,v=np.array(vv),f=np.array(ff),mi=np.array(mm),uv=np.array(uu),untouched_source_faces=np.array(kept),source_f=f)
out['raw_objects'].append({'name':n,'file':fn,'materials':idx[n]['materials'],'vertices':len(vv),'triangles':len(ff),'unchanged_original_triangles':len(kept)})
out['proof']['soil']={'source_file':idx[n]['file'],'trimmed_only_below_new_closed_floor_solids':True,'untouched_original_triangles':len(kept),'saved_triangles':len(ff)}
(D/'Prepared_Geometry.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8');print('TRIM_COMPLETE',len(vv),len(ff),'kept_exact',len(kept),flush=True)
