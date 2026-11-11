import sys,json,math
from pathlib import Path
W=Path(__file__).parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,Point,LineString
B=Path('E:/jz/JIA/Rebuild_V20');I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))};Q=json.loads((D/'Seam_Correction.json').read_text(encoding='utf8'));P=json.loads((D/'Seam_Correction_QA.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']};cache={};trcache={}
def dat(n):
 if n not in cache:
  fp=E[n]['v20_native_cache_override'] if n in E else str(B/'02_Data'/I[n]['file']);d=np.load(fp);cache[n]={k:d[k] for k in d.files}
 return cache[n]
def solid(n):
 d=dat(n);v=d['vertices'];f=d['faces'];vv,ii=np.unique(np.round(v,10),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,ii[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,(n,m.status());return m
def ray(n,p):
 if n not in trcache:
  d=dat(n);tt=d['vertices'][d['faces']];use=(tt[:,:,0].max(1)>13.0)&(tt[:,:,0].min(1)<23.2)&(tt[:,:,1].max(1)>-19.2)&(tt[:,:,1].min(1)<-14.2);trcache[n]=tt[use]
 ts=trcache[n];p=np.array(p);mask=(ts[:,:,:2].min(1)<=p+1e-8).all(1)&(ts[:,:,:2].max(1)>=p-1e-8).all(1);ts=ts[mask];zs=[]
 for t in ts:
  a=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]])
  if abs(np.linalg.det(a))<1e-12:continue
  s=np.linalg.solve(a,p-t[0,:2])
  if (s>=-1e-7).all() and s.sum()<=1+1e-7:zs.append(float(t[0,2]+s@(t[1:,2]-t[0,2])))
 return zs
new='SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER';old='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE';base='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE';extension='SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION';scan_names=[n for n in I if n.startswith('SITE_V14_ORIGINAL_EXTERIOR')]
gutter=solid(new);tie=solid(old);rows=[];cu=[]
for j,(a0,b0) in enumerate(zip(P['grade_stations'][:-1],P['grade_stations'][1:])):
 a=dict(a0);b=dict(b0)
 if j==0:
  t=.045/(b0['s']-a0['s']);a={key:np.asarray(a0[key])*(1-t)+np.asarray(b0[key])*t if key not in ['s'] else a0[key]*(1-t)+b0[key]*t for key in a0}
 if j==len(P['grade_stations'])-2:
  t=1-.045/(b0['s']-a0['s']);b={key:np.asarray(a0[key])*(1-t)+np.asarray(b0[key])*t if key not in ['s'] else a0[key]*(1-t)+b0[key]*t for key in a0}
 aa=np.array(a['point']);bb=np.array(b['point']);na=np.array(a['miter_offset_vector']);nb=np.array(b['miter_offset_vector']);fa=min(a['inner_road_z'],a['outer_lip_z'])-.28;fb=min(b['inner_road_z'],b['outer_lip_z'])-.28;ta=min(a['inner_road_z'],a['outer_lip_z'])-.03;tb=min(b['inner_road_z'],b['outer_lip_z'])-.03
 v=np.array([[*(aa+na*.092),fa+.006],[*(bb+nb*.092),fb+.006],[*(bb+nb*.338),fb+.006],[*(aa+na*.338),fa+.006],[*(aa+na*.092),ta],[*(bb+nb*.092),tb],[*(bb+nb*.338),tb],[*(aa+na*.338),ta]])
 f=np.array([[3,2,1],[3,1,0],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]],np.uint64);m=mf.Manifold(mf.Mesh64(v,f))
 if m.volume()<0:m=mf.Manifold(mf.Mesh64(v,f[:,::-1].copy()))
 assert m.status()==mf.Error.NoError and m.volume()>0;cu.append(m)
cavity=mf.Manifold.batch_boolean(cu,mf.OpType.Add);tvol=(cavity^tie).volume();gvol=(cavity^gutter).volume()
for a in P['grade_stations'][1:-1]:
 p=np.array(a['point']);off=np.array(a['miter_offset_vector']);fl=min(a['inner_road_z'],a['outer_lip_z'])-.28
 for d in [.12,.22,.32]:
  xy=p+off*d;hits={n:[z for z in ray(n,xy) if z>fl+.015 and z<max(a['inner_road_z'],a['outer_lip_z'])+.1] for n in scan_names};hits={n:z for n,z in hits.items() if z};
  if hits:rows.append({'xy':xy.tolist(),'floor':fl,'obstructions':hits})
coverage=Polygon(P['coverage_polygon']);edge=coverage.boundary;seam=[];outer=[]
for n in P['updated_scan_nodes']:
 datn=dat(n);t=datn['vertices'][datn['faces']]
 for tr in t:
  if tr[:,0].max()<13.0 or tr[:,0].min()>23.0 or tr[:,1].max()<-19.0 or tr[:,1].min()>-14.0:continue
  for a,b in zip(tr,np.roll(tr,-1,axis=0)):
   if Point(a[:2]).distance(edge)>1e-7 or Point(b[:2]).distance(edge)>1e-7:continue
   mid=(a+b)/2
   if Point(mid[:2]).distance(edge)>1e-7:continue
   for s in [.25,.5,.75]:
    p=a+(b-a)*s;zz=ray(new,p[:2]);zz=[z for z in zz if -5<z<-2.7]
    if not zz:seam.append({'xyz':p.tolist(),'gap':'NO_NEW_SURFACE'});continue
    err=abs(max(zz)-p[2]);seam.append({'xyz':p.tolist(),'gap':err})
    # Exterior shoulder seam excludes the intended vertical channel end section.
    if p[1]<-18.02 or p[0]>21.7:outer.append(err)
checks=[]
for n in E:
 d=dat(n);area=np.linalg.norm(np.cross(d['vertices'][d['faces']][:,1]-d['vertices'][d['faces']][:,0],d['vertices'][d['faces']][:,2]-d['vertices'][d['faces']][:,0]),axis=1)/2;checks.append({'node':n,'triangles':len(d['faces']),'minimum_triangle_area_m2':float(area.min()),'uv_min':d['uv'].min(0).tolist(),'uv_max':d['uv'].max(0).tolist(),'full_uv':len(d['uv'])==len(d['vertices']),'normals_count':len(d['normals'])})
report={'status':'PASS_LOCAL_SEAM_CORRECTION','cavity_volume_m3':cavity.volume(),'old_tie_intrusion_volume_m3':tvol,'new_gutter_intrusion_volume_m3':gvol,'scan_cavity_obstructions':rows,'outer_shoulder_seam_samples':len(outer),'maximum_outer_shoulder_z_gap_m':max(outer,default=None),'all_boundary_samples':len(seam),'maximum_all_boundary_z_gap_m':max([r['gap'] for r in seam if isinstance(r['gap'],float)],default=None),'missing_new_surface_boundary_samples':[r for r in seam if not isinstance(r['gap'],float)],'cache_checks':checks,'boundary_gap_samples_over_1mm':[r for r in seam if isinstance(r['gap'],float) and r['gap']>.001]}
if tvol>1e-7 or gvol>1e-7 or rows or max(outer,default=0)>.001:report['status']='FAIL_LOCAL_SEAM_CORRECTION'
(D/'Seam_Independent_Validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(report['status'], 'tie',tvol,'gutter',gvol,'scan_hits',len(rows),'outer_gap',max(outer,default=None),'all_gap',report['maximum_all_boundary_z_gap_m'],'no_surface',len(report['missing_new_surface_boundary_samples']),flush=True)
