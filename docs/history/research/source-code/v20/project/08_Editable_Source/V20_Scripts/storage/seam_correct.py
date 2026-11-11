"""Local V20 road/channel seam correction from saved native caches; no model writes."""
import sys,json,math,ast,copy
from pathlib import Path
W=Path(__file__).parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,mapbox_earcut,triangle,export_v5 as ex
from shapely.geometry import Polygon,LineString,Point,box as sb
from shapely.ops import unary_union,nearest_points
from shapely.geometry.polygon import orient
B=Path('E:/jz/JIA/Rebuild_V20');I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))}
proof={'source':'Saved V20 native readback; local original scan road grades','scope':'Only new storage south front gutter/road shoulder, scan within local new front footprint + 360 mm blend, and retained tie within that footprint','blend_width_m':.36,'reference':'Original INSV 710/715/720/725 and aligned stone guard user instruction','qa':[]};Q={'replace':[],'add':[],'remove':[]};cache={}
for file,ns in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ns],type_ignores=[]),'<helpers>','exec'))
def dat(n):
 if n not in cache:
  d=np.load(B/'02_Data'/I[n]['file']);cache[n]={k:d[k].copy() for k in d.files}
 return cache[n]
def native(n):
 d=dat(n);v=d['vertices'];f=d['faces'];vv,inv=np.unique(np.round(v,10),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)));assert a.status()==mf.Error.NoError,(n,a.status());return a
def polys(p):return [p] if p.geom_type=='Polygon' else [q for q in getattr(p,'geoms',[]) if q.geom_type=='Polygon' and q.area>1e-12]
def prm(p,z,h):
 p=orient(p,1);return {'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[list(q.coords)[:-1] for q in p.interiors],'z':z,'height':h}
def normals(v,f):
 t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ln=np.linalg.norm(n,axis=1);n[ln>0]/=ln[ln>0,None];out=np.zeros_like(v)
 for k in range(3):np.add.at(out,f[:,k],n)
 ll=np.linalg.norm(out,axis=1);out[ll>0]/=ll[ll>0,None];return out
def put(n,data,closed=True,**meta):
 fp=D/('SEAM_'+n+'.npz');np.savez_compressed(fp,**data);parts=[{'geometry':{'type':'polyhedron','vertices':data['vertices'].tolist(),'faces':data['faces'].tolist()},'material':I[n]['materials'][0]}] if closed else []
 e={**copy.deepcopy(I[n]['element']),'parts':parts,'v20_native_cache_override':str(fp),'v20_seam_correction':True,'open_expected':not closed,'closed_expected':closed,**meta}
 for key in ['origin','angle','angle_deg','definition']:e.pop(key,None)
 Q['replace'].append(e);return e

scan_names=[n for n in I if n.startswith('SITE_V14_ORIGINAL_EXTERIOR')];ground={}
for n in scan_names:
 d=dat(n);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nl=np.linalg.norm(no,axis=1);use=(abs(no[:,2])>.25*nl)&(t[:,:,2].max(1)>-4.85)&(t[:,:,2].min(1)<-3.0)&(t[:,:,0].max(1)>12.8)&(t[:,:,0].min(1)<23.4)&(t[:,:,1].max(1)>-19.7)&(t[:,:,1].min(1)<-14.1);ground[n]=t[use]
def ray_height(p):
 p=np.array(p);zs=[]
 for tt in ground.values():
  ids=((tt[:,:,:2].min(1)<=p+1e-8).all(1)&(tt[:,:,:2].max(1)>=p-1e-8).all(1));t=tt[ids]
  if not len(t):continue
  aa=t[:,0,:2];u=t[:,1,:2]-aa;v=t[:,2,:2]-aa;det=u[:,0]*v[:,1]-u[:,1]*v[:,0];q=p-aa;s=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/det;r=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/det;hit=(s>=-1e-7)&(r>=-1e-7)&(s+r<=1+1e-7);zz=t[:,0,2]+s*(t[:,1,2]-t[:,0,2])+r*(t[:,2,2]-t[:,0,2]);zs.extend(zz[hit& (zz>-4.85)&(zz<-3.0)].tolist())
 return float(np.median(zs)) if zs else None
route=np.array([[13.35,-17.04],[20.2,-17.04],[21.43,-15.48]],float);lengths=np.linalg.norm(np.diff(route,axis=0),axis=1);cum=np.r_[0,np.cumsum(lengths)];dd=np.diff(route,axis=0)/lengths[:,None];ns=np.c_[dd[:,1],-dd[:,0]];mids=np.array([ns[0],(ns[0]+ns[1])/(1+np.dot(ns[0],ns[1])),ns[1]])
stations=[];pts=[];offs=[]
for j in range(2):
 for t in np.linspace(0,1,int(math.ceil(lengths[j]/.12))+1):
  if j and t==0:continue
  stations.append(cum[j]+t*lengths[j]);pts.append(route[j]+t*(route[j+1]-route[j]));offs.append(mids[j]*(1-t)+mids[j+1]*t)
stations=np.array(stations);pts=np.array(pts);offs=np.array(offs)
raw=[]
for p,off in zip(pts,offs):raw.append([ray_height(p+off*d) for d in [.025,.43,1.05]])
raw=np.array([[np.nan if z is None else z for z in r] for r in raw]);fits=raw.copy()
for k in range(3):
 ok=np.isfinite(raw[:,k]);assert ok.sum()>10,(k,ok.sum());vals=np.interp(stations,stations[ok],raw[ok,k]);fits[:,k]=[float(np.median(vals[max(0,j-2):min(len(vals),j+3)])) for j in range(len(vals))]
proof['grade_stations']=[{'s':float(s),'point':p.tolist(),'miter_offset_vector':n.tolist(),'inner_road_z':float(z[0]),'outer_lip_z':float(z[1]),'shoulder_outer_z':float(z[2])} for s,p,n,z in zip(stations,pts,offs,fits)]
def station_of(p):
 p=np.array(p);best=None
 for j in range(2):
  t=float(np.clip(np.dot(p-route[j],dd[j])/lengths[j],0,1));q=route[j]+t*(route[j+1]-route[j]);di=np.linalg.norm(p-q)
  if best is None or di<best[0]:best=(di,cum[j]+t*lengths[j],float(np.dot(p-q,ns[j])))
 return best[1],best[2]
def grade(p):
 s,d=station_of(p);zi,zo,zs=[float(np.interp(s,stations,fits[:,k])) for k in range(3)]
 if d<=.43:
  if d<.09:return zi-.02
  if d<.34:return min(zi,zo)-.28
  return zo-.02
 t=np.clip((d-.43)/.62,0,1);return float(zo*(1-t)+zs*t)
def road_grade(p):
 s,d=station_of(p);zo,zs=[float(np.interp(s,stations,fits[:,k])) for k in [1,2]];t=np.clip((d-.43)/.62,0,1);return float(zo*(1-t)+zs*t)
# Coverage includes the gutter and shoulder. Slight inward overlap seals against the stone face.
lower=pts+offs*(-.025);upper=pts+offs*1.05;coverage=Polygon(np.vstack([lower,upper[::-1]])).buffer(0);blendmask=coverage.buffer(.36,join_style=2)
pathplan=Polygon(np.vstack([pts+offs*.089, (pts+offs*.341)[::-1]])).buffer(0)

# Build one closed gutter + shoulder using the measured cross slopes, shared miter points and densified stations.
strips=[]
for j in range(len(pts)-1):
 a,b=pts[j],pts[j+1];na,nb=offs[j],offs[j+1];zia,zoa,zsa=fits[j];zib,zob,zsb=fits[j+1];fa=min(zia,zoa)-.28;fb=min(zib,zob)-.28
 for lo,hi,ta0,ta1,tb0,tb1,ba0,ba1,bb0,bb1 in [
  (-.025,.09,zia-.02,zia-.02,zib-.02,zib-.02,fa-.18,fa-.18,fb-.18,fb-.18),
  (.09,.34,fa,fa,fb,fb,fa-.18,fa-.18,fb-.18,fb-.18),
  (.34,.43,zoa-.02,zoa-.02,zob-.02,zob-.02,fa-.18,fa-.18,fb-.18,fb-.18),
  (.43,1.05,zoa,zsa,zob,zsb,zoa-.10,zsa-.10,zob-.10,zsb-.10)]:
  vv=[[*(a+na*lo),ba0],[*(b+nb*lo),bb0],[*(b+nb*hi),bb1],[*(a+na*hi),ba1],[*(a+na*lo),ta0],[*(b+nb*lo),tb0],[*(b+nb*hi),tb1],[*(a+na*hi),ta1]];g=oriented({'type':'polyhedron','vertices':vv,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]});strips.append(manifold(g))
for end in [0,1]:
 j=0 if end==0 else len(pts)-2;ta=0 if end==0 else 1-.035/(stations[j+1]-stations[j]);tb=.035/(stations[j+1]-stations[j]) if end==0 else 1
 a=pts[j]*(1-ta)+pts[j+1]*ta;b=pts[j]*(1-tb)+pts[j+1]*tb;na=offs[j]*(1-ta)+offs[j+1]*ta;nb=offs[j]*(1-tb)+offs[j+1]*tb;za=fits[j]*(1-ta)+fits[j+1]*ta;zb=fits[j]*(1-tb)+fits[j+1]*tb;fa=min(za[:2])-.46;fb=min(zb[:2])-.46
 for lo,hi,tla,tha,tlb,thb in [(-.025,.09,za[0]-.02,za[0]-.02,zb[0]-.02,zb[0]-.02),(.09,.34,za[0]-.02,za[1]-.02,zb[0]-.02,zb[1]-.02),(.34,.43,za[1]-.02,za[1],zb[1]-.02,zb[1]),(.43,1.05,za[1],za[2],zb[1],zb[2])]:
  vv=[[*(a+na*lo),fa],[*(b+nb*lo),fb],[*(b+nb*hi),fb],[*(a+na*hi),fa],[*(a+na*lo),tla],[*(b+nb*lo),tlb],[*(b+nb*hi),thb],[*(a+na*hi),tha]];g=oriented({'type':'polyhedron','vertices':vv,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]});strips.append(manifold(g))
channel=mf.Manifold.batch_boolean(strips,mf.OpType.Add);print('CHANNEL COMPONENTS',[(q.volume(),q.bounding_box()) for q in channel.decompose()],flush=True);g=fromman(channel);channel=manifold(g);assert len(channel.decompose())==1,len(channel.decompose());v=np.array(g['vertices']);f=np.array(g['faces'],np.int32);u=v[:,:2].copy();data={'vertices':v,'faces':f,'uv':u,'normals':normals(v,f),'material_ids':np.zeros(len(f),np.int32)}
put('SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER',data,v20_fit_to_local_scan=True,v20_grade_stations=proof['grade_stations'],v20_road_blend_width_m=.36,v20_closed_end_return_length_m=.035)
rt=v[f];rno=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);rt=rt[rno[:,2]>1e-10]
def actual_new_surface(p):
 p=np.array(p);mask=(rt[:,:,:2].min(1)<=p+1e-7).all(1)&(rt[:,:,:2].max(1)>=p-1e-7).all(1);ts=rt[mask];zs=[]
 for t in ts:
  U=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]]);s=np.linalg.solve(U,p-t[0,:2])
  if (s>=-1e-6).all() and s.sum()<=1+1e-6:zs.append(float(t[0,2]+np.dot(s,t[1:,2]-t[0,2])))
 return max(zs) if zs else None
def road_grade(p):
 z=actual_new_surface(p)
 if z is None:
  # Numerical vertex-to-edge tolerance only. Coverage boundary belongs to the real closed mesh.
  raise ValueError('New shoulder boundary has no actual surface at '+str(p))
 return z

# Cut ONLY old tie inside the newly modeled surface footprint, preserving every other perimeter run.
n='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE';oldtie=native(n);cut=mf.Manifold.batch_boolean([manifold(prm(p,-8,12)) for p in polys(coverage.buffer(.002,join_style=2))],mf.OpType.Add);tie=oldtie-cut;assert tie.status()==mf.Error.NoError
g=fromman(tie);v=np.array(g['vertices']);f=np.array(g['faces'],np.int32)
# All tie material is original grey fine aggregate. Preserve old UV wherever new faces sit on old surfaces.
old=dat(n);ot=old['vertices'][old['faces']];ou=old['uv'][old['faces']];ovno=np.cross(ot[:,1]-ot[:,0],ot[:,2]-ot[:,0]);ovn=np.linalg.norm(ovno,axis=1);ovno[ovn>0]/=ovn[ovn>0,None]
dv=[];df=[];du=[]
for tri in v[f]:
 cen=tri.mean(0);no=np.cross(tri[1]-tri[0],tri[2]-tri[0]);no/=np.linalg.norm(no);cand=np.flatnonzero((abs(np.einsum('ij,ij->i',ot[:,0]-cen,ovno))<1e-5)&(abs(ovno@no)>.99));uv=None
 for j in cand:
  a0=ot[j,0];U=np.column_stack([ot[j,1]-a0,ot[j,2]-a0]);weights=np.linalg.lstsq(U,(tri-a0).T,rcond=None)[0].T;ww=np.c_[1-weights.sum(1),weights]
  wc=np.linalg.lstsq(U,cen-a0,rcond=None)[0]
  if (wc>=-1e-5).all() and wc.sum()<=1+1e-5:uv=ww@ou[j];break
 if uv is None:
  k=int(np.argmax(abs(no)));axes=[j for j in range(3) if j!=k];uv=tri[:,axes]
 off=len(dv);dv.extend(tri.tolist());du.extend(uv.tolist());df.append([off,off+1,off+2])
v=np.array(dv);f=np.array(df,np.int32);data={'vertices':v,'faces':f,'uv':np.array(du),'normals':normals(v,f),'material_ids':np.zeros(len(f),np.int32)};put(n,data,v20_local_new_front_footprint_cut=True,v20_unchanged_elsewhere=True,v20_original_retention_scope='All native surface outside 2 mm expanded new local gutter/shoulder footprint retained geometrically')
proof['qa'].append({'test':'old_tie_vs_new_cavity','remaining_volume_m3':(tie^manifold(prm(pathplan,-8,12))).volume(),'old_tie_removed_volume_m3':oldtie.volume()-tie.volume(),'new_tie_closed':str(tie.status())})

# Clip triangles, interpolate original texture UV, blend only the 360 mm local scan boundary.
# The construction road itself is replaced by the closed channel/shoulder. Outside the blend every face is kept exactly.
boundary=coverage.boundary;station_lines=[LineString([p-off*30,p+off*30]) for p,off in zip(pts,offs)]
mesh_border_points=np.unique(np.round(rt[:,:,:2].reshape(-1,2),10),axis=0);mesh_border_points=np.array([p for p in mesh_border_points if Point(p).distance(boundary)<1e-6])
seam_vertices=[];updated_scans=[]
def densify_ring(ring):
 out=[]
 for aa,bb in zip(ring,ring[1:]+ring[:1]):
  aa=np.array(aa);bb=np.array(bb);out.append(aa.tolist());ed=LineString([aa,bb]);critical=[]
  if ed.length<1e-10:continue
  if ed.distance(boundary)<1e-7:
   for pp in mesh_border_points:
    t=np.dot(pp-aa,bb-aa)/np.dot(bb-aa,bb-aa)
    if 1e-7<t<1-1e-7 and ed.distance(Point(pp))<1e-6:critical.append((t,pp))
   for line in station_lines:
    hit=ed.intersection(line)
    if hit.geom_type=='Point':
     t=np.dot(np.array(hit.coords[0])-aa,bb-aa)/np.dot(bb-aa,bb-aa)
     if 1e-7<t<1-1e-7:critical.append((t,np.array(hit.coords[0])))
  if ed.distance(coverage)<.36:
   for t in np.linspace(0,1,int(math.ceil(ed.length/.12))+1)[1:-1]:critical.append((float(t),aa+t*(bb-aa)))
  last=-1.
  for t,pp in sorted(critical,key=lambda x:x[0]):
   if abs(t-last)>1e-7:out.append(pp.tolist());last=t
 return out
for n in scan_names:
 old=dat(n);v=old['vertices'];f=old['faces'];uv=old['uv'];nv=[];nf=[];nu=[];nmi=[];removed=0;clipped=0;changed=0;retained=0;discardzero=0
 for fi,face in enumerate(f):
  t=v[face];uu=uv[face];lo=t[:,:2].min(0);hi=t[:,:2].max(0);mins=blendmask.bounds[:2];maxs=blendmask.bounds[2:]
  def emit(tv,tu,edit=False):
   nonlocal_dummy=0
   off=len(nv);nv.extend(np.asarray(tv).tolist());nu.extend(np.asarray(tu).tolist());nf.append([off,off+1,off+2]);nmi.append(int(old['material_ids'][fi]))
  if hi[0]<mins[0] or lo[0]>maxs[0] or hi[1]<mins[1] or lo[1]>maxs[1]:emit(t,uu);retained+=1;continue
  po=Polygon(t[:,:2])
  if po.area<1e-12:
   if coverage.covers(Point(t[:,:2].mean(0))):removed+=1;continue
   emit(t,uu);retained+=1;continue
  if not po.is_valid:po=po.buffer(0)
  if not po.intersects(blendmask):emit(t,uu);retained+=1;continue
  rem=po.difference(coverage)
  if rem.is_empty:removed+=1;continue
  if not rem.equals(po):clipped+=1
  else:changed+=1
  A=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]]);Ai=np.linalg.inv(A)
  for pp in polys(rem):
   pp=orient(pp,1);rings=[densify_ring(list(pp.exterior.coords)[:-1])]+[densify_ring(list(r.coords)[:-1]) for r in pp.interiors];pv=np.array([q for r in rings for q in r]);segments=[];off=0
   for rr in rings:
    segments.extend([[off+k,off+(k+1)%len(rr)] for k in range(len(rr))]);off+=len(rr)
   inp={'vertices':pv,'segments':np.array(segments,np.int32)}
   if len(rings)>1:inp['holes']=np.array([[Polygon(rr).representative_point().x,Polygon(rr).representative_point().y] for rr in rings[1:]])
   out=triangle.triangulate(inp,'pQ');pv=out['vertices'];inds=out['triangles'];ab=(pv-t[0,:2])@Ai.T;wei=np.c_[1-ab.sum(1),ab];wei=np.maximum(wei,0);wei/=wei.sum(1)[:,None];vs=wei@t;us=np.clip(wei@uu,uu.min(0),uu.max(0))
   for j,xy in enumerate(pv):
    pt=Point(xy);di=pt.distance(coverage)
    if di<.36000001:
     near=nearest_points(pt,coverage)[1];target=road_grade([near.x,near.y]);w=1-3*(di/.36)**2+2*(di/.36)**3;w=float(np.clip(w,0,1));vs[j,2]=vs[j,2]*(1-w)+target*w
     if di<1e-7:seam_vertices.append([*xy,vs[j,2],target])
   oldnormal=np.cross(t[1]-t[0],t[2]-t[0])
   for ids in inds:
    q=vs[ids];no=np.cross(q[1]-q[0],q[2]-q[0])
    if np.linalg.norm(no)<1e-11:discardzero+=1;continue
    if np.dot(no,oldnormal)<0:ids=ids[::-1]
    emit(vs[ids],us[ids],True)
 if removed or clipped or changed:
  vv=np.array(nv);ff=np.array(nf,np.int32);data={'vertices':vv,'faces':ff,'uv':np.array(nu),'normals':normals(vv,ff),'material_ids':np.array(nmi,np.int32)};put(n,data,False,v20_scan_texture_uv_barycentric_preserved=True,v20_local_crop_footprint=list(coverage.exterior.coords),v20_boundary_blend_width_m=.36,v20_unchanged_triangles=retained,v20_cropped_triangles=removed+clipped)
  updated_scans.append(n);proof['qa'].append({'node':n,'old_triangles':len(f),'new_triangles':len(ff),'exact_retained_outside_local_patch':retained,'fully_removed_triangles':removed,'clipped_triangles':clipped,'blended_triangles':changed,'zero_area_removed':discardzero})
print('SCAN PATCH',updated_scans,flush=True)
# Use 2 mm overlap cap to old unchanged geometry, but the visible surface seam is exact shared grade.
seam=np.array(seam_vertices);proof['qa'].append({'test':'scan_to_new_shoulder_boundary','shared_seam_vertex_occurrences':len(seam),'maximum_z_gap_m':float(abs(seam[:,2]-seam[:,3]).max()) if len(seam) else None})
proof['coverage_polygon']=list(coverage.exterior.coords);proof['status']='PASS_LOCAL_SEAM_PATCH_GEOMETRY';proof['updated_scan_nodes']=updated_scans
(D/'Seam_Correction.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Seam_Correction_QA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');print('READY SEAM',len(Q['replace']),len(seam),flush=True)
