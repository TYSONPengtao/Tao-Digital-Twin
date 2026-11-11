import sys,json,math,shutil,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v6_reality_inventory')]
import numpy as np,mapbox_earcut
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from shapely import covers,points
import export_v5 as ex
from nearest_photo_projection import PhotoProjector,closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');S=ex.SCENE
hp=json.loads((W/'v6_alignment_audit/Refined_Main_Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(hp['local']['outer'],hp['local']['holes'])
shutil.copy2(W/'v6_alignment_audit/Refined_Main_Hole_Polygon.json',O/'02_Data/Hole_Polygon.json')
coord=S['coordinate'];a=math.radians(coord['rotation_deg']);c=math.cos(a);ss=math.sin(a);T=np.eye(4);T[:3,:3]=[[c,-ss,0],[ss,c,0],[0,0,1]];T[:3,3]=coord['origin'];inv=np.linalg.inv(T)
origpaths=sorted(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj'))
print('Loading unchanged original photo donor...',flush=True);P=PhotoProjector.from_objs(origpaths,inv)
materials={k:dict(v) for k,v in S['materials'].items()};photo_names={}
for i,m in P.materials.items():
 tex=Path(m['texture']);dest=O/'03_Textures/Patch'/tex.name;shutil.copy2(tex,dest);name='PATCH_PHOTO_'+str(i);photo_names[i]=name;materials[name]={'color':[255,255,255],'roughness':.78,'texture':str(dest),'source_texture':str(tex),'role':'Original measured photo UV projected only onto new patch'}
def polys(p):
 if p.is_empty:return []
 if p.geom_type=='Polygon':return [p]
 return [q for q in getattr(p,'geoms',[]) if q.geom_type=='Polygon']
def polygon_tris(p):
 rings=[list(p.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in p.interiors];xy=np.array([q for r in rings for q in r],float);ends=np.cumsum([len(r) for r in rings]).astype(np.uint32);inds=mapbox_earcut.triangulate_float64(xy,ends).reshape(-1,3)
 return xy[inds]
def clip_half(v,n,lim,greater):
 out=[]
 for A,B in zip(v,np.roll(v,-1,axis=0)):
  qa=np.dot(A[:2],n)-lim;qb=np.dot(B[:2],n)-lim;ina=qa>=-1e-10 if greater else qa<=1e-10;inb=qb>=-1e-10 if greater else qb<=1e-10
  if ina:out.append(A)
  if ina!=inb:out.append(A+(B-A)*(qa/(qa-qb)))
 return np.array(out)
def clipped(t,mask):
 xy=t[:,:2];p=Polygon(xy)
 if p.area>1e-12:
  if mask.covers(p):return [t]
  inter=p.intersection(mask);n=np.cross(t[1]-t[0],t[2]-t[0]);d=np.dot(n,t[0]);result=[]
  for pp in polys(inter):
   for uv in polygon_tris(pp):
    vv=np.column_stack((uv,(d-uv@n[:2])/n[2]))
    if np.dot(np.cross(vv[1]-vv[0],vv[2]-vv[0]),n)<0:vv=vv[[0,2,1]]
    result.append(vv)
  return result
 # Preserve vertical model faces while clipping against the extruded XY mask.
 dd=np.linalg.norm(xy[:,None,:]-xy[None,:,:],axis=2);i,j=np.unravel_index(np.argmax(dd),dd.shape)
 if dd[i,j]<1e-10:return []
 p0=xy[i];u=(xy[j]-p0)/dd[i,j];line=LineString([xy[i],xy[j]]);q=line.intersection(mask);segs=[q] if q.geom_type=='LineString' else [r for r in getattr(q,'geoms',[]) if r.geom_type=='LineString'];result=[]
 for seg in segs:
  if seg.is_empty or len(seg.coords)<2:continue
  vals=np.array(seg.coords)@u;v=clip_half(t,u,vals.min(),True)
  if len(v)>2:v=clip_half(v,u,vals.max(),False)
  if len(v)>2:result += [v[[0,k,k+1]] for k in range(1,len(v)-1)]
 return result
def split(t,maxedge=.5):
 edge=np.linalg.norm(np.roll(t,-1,axis=0)-t,axis=1);i=int(np.argmax(edge))
 if edge[i]<=maxedge:return [t]
 j=(i+1)%3;k=(i+2)%3;m=(t[i]+t[j])/2
 return split(np.array([t[i],m,t[k]]),maxedge)+split(np.array([m,t[j],t[k]]),maxedge)
index=[];coverage=[];counts=collections.Counter();projectedcount=0;excluded=[]
def save(name,e,tri,uv,matnames,**extra):
 if not len(tri):return
 n=len(index);ms=list(dict.fromkeys(matnames));mid=np.array([ms.index(m) for m in matnames],np.int32);vv=np.array(tri).reshape(-1,3);faces=np.arange(len(vv),dtype=np.int32).reshape(-1,3);uv=np.array(uv).reshape(-1,2);fn=f'Patch_{n:03}.npz';np.savez_compressed(O/'02_Data'/fn,vertices=vv,faces=faces,uv=uv,material_ids=mid)
 info=dict(index=n,file=fn,name=name,element={k:v for k,v in e.items() if k!='parts'},materials=ms,triangles=len(tri),vertices=len(vv),**extra);index.append(info)
 for t in tri:
  p=Polygon(t[:,:2])
  if p.area>1e-10:coverage.append(p)
for e in S['elements']:
 if e['layer'] in ['01_GRID','02_LEVEL','99_HELPER','90_UNCERTAIN'] or e['confidence']=='LOW':continue
 # V6 is existing-photo integration. Keep unbuilt V4 additions in V5 for review.
 if e['name'].startswith('CONSTRUCTION_'):excluded.append(e['name']);continue
 tri=[];base=[];eligible=[]
 for part in ex.expand_parts(e):
  v,faces=ex.world_part(part,e)
  if v is None:continue
  photo=part['material'] not in ['M_Glass_Clear','M_Glass_Frosted'] and e['layer'] not in ['11_WALL_INT','30_DOOR','31_WINDOW','40_STAIR','70_EQUIPMENT']
  for face in faces:
   ids=ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]
   for ids0 in ids:
    t=v[[face[k] for k in ids0]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-10:continue
    for tt in clipped(t,H):
     if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-10:continue
     for ttt in (split(tt) if photo else [tt]):tri.append(ttt);base.append(part['material']);eligible.append(photo)
 if not tri:counts['outside_nodes_excluded']+=1;continue
 tri=np.array(tri);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];uv=np.zeros((len(tri),3,2));names=base[:]
 for j,t in enumerate(tri):
  axes=[k for k in range(3) if k!=int(np.argmax(abs(norm[j])))];uv[j]=t[:,axes]
 pp=np.flatnonzero(eligible)
 if len(pp):
  q=P.query(tri[pp].reshape(-1,3),np.repeat(norm[pp],3,axis=0),max_distance=.35,min_normal_dot=.65,k=16)
  match=q['matched'].reshape(-1,3).all(axis=1);mi=q['material_id'].reshape(-1,3);match &= (mi==mi[:,0:1]).all(axis=1);quv=q['uv'].reshape(-1,3,2);match &= np.ptp(np.nan_to_num(quv,nan=1e20),axis=1).max(axis=1)<.12
  for j in np.flatnonzero(match):idx=pp[j];uv[idx]=quv[j];names[idx]=photo_names[int(mi[j,0])]
  projectedcount+=int(match.sum());counts['photo_eligible_triangles']+=len(pp);counts['photo_projected_triangles']+=int(match.sum())
 save(e['name'],e,tri,uv,names,photo_triangles=sum(m.startswith('PATCH_PHOTO') for m in names),role='V5_REBUILT_GEOMETRY_ONLY_INSIDE_MISSING_AREA')
 if len(index)%30==0:print('patch nodes',len(index),'triangles',sum(x['triangles'] for x in index),flush=True)
print('Computing patch projection coverage...',flush=True);covered=unary_union(coverage);residual=H.difference(covered);counts['primary_void_area_m2']=H.area;counts['residual_before_photo_edge_m2']=residual.area
# Add original photo geometry only into narrow missing edge strips. It also
# supplies the original UVs where no clean donor geometry existed.
if residual.area>1e-6:
 donor=[];duv=[];dm=[];t=P.triangles;mins=t[:,:,:2].min(axis=1);maxs=t[:,:,:2].max(axis=1);b=residual.bounds;sel=np.flatnonzero((maxs[:,0]>=b[0])&(mins[:,0]<=b[2])&(maxs[:,1]>=b[1])&(mins[:,1]<=b[3]))
 for i in sel:
  poly=Polygon(t[i,:,:2])
  if poly.area<1e-12 or not poly.intersects(residual):continue
  for tt in clipped(t[i],residual):
   _,bw,_=closest_on_triangles(tt,np.repeat(t[i][None,:,:],3,axis=0));donor.append(tt);duv.append(bw@P.uv[i]);dm.append(photo_names[int(P.material_ids[i])])
 if donor:save('PHOTO_BOUNDARY_RECOVERY',{'name':'PHOTO_BOUNDARY_RECOVERY','layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','source':'Original JIA photo geometry clipped to residual missing strips, not into intact base'},donor,duv,dm,role='ORIGINAL_PHOTO_EDGE_STRIP_RECOVERY')
covered=unary_union(coverage);residual=H.difference(covered);outside=covered.difference(H)
counts.update(patch_nodes=len(index),patch_triangles=sum(x['triangles'] for x in index),residual_after_photo_edge_m2=residual.area,patch_outside_primary_void_m2=outside.area)
(O/'02_Data/Patch_Index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/Materials.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2),encoding='utf-8');(O/'06_Report/Patch_Clip_And_Photo_QA.json').write_text(json.dumps(dict(counts=counts,source_base_modified=False,excluded_unbuilt_proposal_nodes=excluded,photo_projection={'max_distance_m':.35,'min_normal_dot':.65,'cross_photo_triangles':'Kept provisional V5 material','unmatched':'Kept provisional V5 material'},residual_polygons=[{'outer':list(p.exterior.coords),'holes':[list(r.coords) for r in p.interiors]} for p in polys(residual)]),ensure_ascii=False,indent=2),encoding='utf-8')
assert outside.area<1e-7
print('Hybrid patch built',dict(counts),flush=True)
