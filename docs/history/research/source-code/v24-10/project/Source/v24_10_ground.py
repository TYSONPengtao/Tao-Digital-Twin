"""Closed, source-graded ground infill with original photograph UV projection."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import Polygon,Point,box
from shapely.geometry.polygon import orient
from shapely.ops import triangulate
from scipy.spatial import cKDTree
from scipy.interpolate import RBFInterpolator
from PIL import Image
D=W/'v24_10';prep=json.loads((D/'Prepared_Geometry.json').read_text());poly=Polygon(prep['plot']['outline']);outer=poly.buffer(2.55,join_style=2).intersection(box(12.5,-19.55,23.35,-7.0));mask=outer.difference(poly.buffer(.43,join_style=2)).difference(box(0,-11.9,13.03,10))
d=np.load(D/'AsBuilt_All_LOCAL.npz');sv=d['v'].astype(float);sf=d['f'];su=d['uv'];tt=sv[sf];p=tt.mean(1);nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1),1e-20)[:,None]
ok=(p[:,0]>11.5)&(p[:,0]<24.5)&(p[:,1]>-20.5)&(p[:,1]<-5.5)&(p[:,2]<-1.3)&(abs(nn[:,2])>.45);tri=tt[ok];uvtri=su[sf[ok]];gp=p[ok];tree=cKDTree(gp[:,:2])
# Smooth scan micro-noise while retaining the actual topographic gradient.
bins=np.round(gp[:,:2]/.30).astype(int);keys=np.unique(bins,axis=0);controls=[]
for key in keys:
 g=gp[np.all(bins==key,axis=1)];controls.append([*np.median(g[:,:2],axis=0),float(np.median(g[:,2]))])
controls=np.array(controls);source_height=RBFInterpolator(controls[:,:2],controls[:,2],neighbors=min(55,len(controls)),smoothing=.25,kernel='thin_plate_spline')
photo=np.asarray(Image.open('D:/AJAVIS01/ContextCapture/CASES/JIA/Productions/Production_OBJ/Data/Model/Model_0.jpg').convert('RGB'),float)/255;hh,ww=photo.shape[:2];tc=uvtri.mean(1);ix=np.clip((tc[:,0]*(ww-1)).astype(int),0,ww-1);iy=np.clip(((1-tc[:,1])*(hh-1)).astype(int),0,hh-1);source_colors=photo[iy,ix]
old=np.load(D/'Retained_Ground_Reference.npz');ot=old['v'][old['f']];op=ot.mean(1);otree=cKDTree(op[:,:2])
def height(q,pts,tr):
 dis,ii=tr.query(q,k=20);pp=pts[ii];w=1/np.maximum(.1,dis)**2;A=np.c_[pp[:,:2]-q,np.ones(len(pp))];c=np.linalg.lstsq(A*np.sqrt(w[:,None]),pp[:,2]*np.sqrt(w),rcond=None)[0]
 return float(c[2])if max(abs(c[:2]))<.9 else float(np.average(pp[:,2],weights=w))
V=[];F=[];LUV=[];COL=[];index={};deltas=[]
def vertex(q):
 key=tuple(np.round(q,7))
 if key in index:return index[key]
 src=float(source_height(np.array(q)[None,:])[0]);ret=height(np.array(q),op,otree);ret=src+np.clip(ret-src,-.18,.18);dist=outer.exterior.distance(Point(q));w=max(0,min(1,dist/.80));z=src*w+ret*(1-w)+.005*(1-w);index[key]=len(V);V.append([*q,z]);deltas.append(abs(z-src));dis,ii=tree.query(q,k=10);wc=np.exp(-dis**2/(2*.35**2));COL.append(np.average(source_colors[ii],axis=0,weights=np.maximum(wc,1e-20)));return index[key]
def bary(q,t):
 A=np.c_[t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]]
 if abs(np.linalg.det(A))<1e-10:return np.array([1.,0,0])
 b=np.linalg.solve(A,np.array(q)-t[0,:2]);return np.array([1-b.sum(),*b])
for x in np.arange(12.5,23.35,.24):
 for y in np.arange(-19.55,-7.0,.24):
  cut=mask.intersection(box(x,y,min(x+.24,23.35),min(y+.24,-7.0)))
  if cut.is_empty or cut.area<1e-8:continue
  for q in triangulate(cut):
   if not cut.covers(q.representative_point()):continue
   xy=np.array(orient(q,1).exterior.coords)[:3];f=[vertex(p)for p in xy]
   if len(set(f))<3:continue
   cc=xy.mean(0);dist,candidates=tree.query(cc,k=28);best=None
   for i in candidates:
    b=bary(cc,tri[i]);neg=float(np.maximum(0,-b).sum());score=neg+float(np.linalg.norm(cc-gp[i,:2]))*.03
    if best is None or score<best[0]:best=(score,i)
   i=best[1];uv=np.array([bary(p,tri[i])@uvtri[i]for p in xy]);F.append(f);LUV.append(uv)
np.savez_compressed(D/'Restored_Original_Ground.npz',v=np.array(V,np.float32),f=np.array(F,np.int32),loop_uv=np.array(LUV,np.float32),color=np.array(COL,np.float32))
prep['terrain'].update(mesh_faces=len(F),vertices=len(V),all_top_uv_unchanged=False,method='Closed native source-graded terrain with 0.30m control cells and smoothed source elevations; at most 185mm edge grade blend; original photo colors sampled into native vertex attributes (no bitmap editing), source UV projection retained',maximum_boundary_grade_blend_m=max(deltas),local_patch_bounds=list(mask.bounds),mask_outer=list(mask.exterior.coords))
(D/'Prepared_Geometry.json').write_text(json.dumps(prep,ensure_ascii=False),encoding='utf8');print(json.dumps({k:v for k,v in prep['terrain'].items()if k!='mask_outer'}),flush=True)
