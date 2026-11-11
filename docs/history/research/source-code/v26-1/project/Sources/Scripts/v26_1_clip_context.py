from v26_1_common import *
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union,triangulate
X=json.loads((D/'Extra_Index.json').read_text('utf8'));out=[];proof=[]
segs=json.loads((W/'v16/Drain_Segments.json').read_text('utf8'));masks=[]
def mask(a,b,width,z0,z1,ground_exempt=False):
 a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);n=np.array([-u[1],u[0]]);lo=np.array([-.03,-width,z0]);hi=np.array([np.linalg.norm(b-a)+.03,width,z1]);corn=np.array([a+u*s+n*t for s in [lo[0],hi[0]]for t in[lo[1],hi[1]]]);return {'origin':np.r_[a,0.],'basis':np.array([[*u,0.],[*n,0.],[0,0,1.]]),'lo':lo,'hi':hi,'bbox':[np.r_[corn.min(0),z0],np.r_[corn.max(0),z1]],'ground_exempt':ground_exempt}
for r in segs:
 if r['ci']==0 and r['j']in [60,61]:continue
 a=np.array(r['a']);b=np.array(r['b']);masks.append(mask(a,b,.50,min(r['za'],r['zb'])-.7,4.90,True))
# Native buildings have priority in these occupied footprints. The original
# entrance-ramp mesh is a separate protected V26 object and is never selected.
for lo,hi in [([-.25,.94,-.69],[13.26,10.04,11.65]),([8.10,-11.94,-.86],[14.32,-2.53,5.12]),([13.02,-16.55,-.68],[18.76,-8.44,5.12])]:
 m=mask([lo[0],(lo[1]+hi[1])/2],[hi[0],(lo[1]+hi[1])/2],(hi[1]-lo[1])/2,lo[2],hi[2]);masks.append(m)
branch=mask([10.67,-16.8545],[13.46,-16.5811],.63,-4.5,3.80,True);masks.append(branch)
def clip_half(poly,axis,z,sign):
 ins=[];outs=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  di=sign*(p[0][axis]-z);dj=sign*(q[0][axis]-z);pi=di>=-1e-9;qi=dj>=-1e-9;(ins if pi else outs).append(p)
  if pi!=qi:
   t=di/(di-dj);r=(p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1]));ins.append(r);outs.append(r)
 return ins,outs
def subtract_box(t,uv,m):
 local=(t-m['origin'])@m['basis'].T
 if ((local.max(0)<m['lo'])|(local.min(0)>m['hi'])).any():return [(t,uv)],False
 if m['ground_exempt']:
  no=np.cross(t[1]-t[0],t[2]-t[0]);nl=np.linalg.norm(no)
  if nl>1e-15 and no[2]/nl>.45 and t[:,2].max()<-.90:return [(t,uv)],False
 poly=[(p,u)for p,u in zip(local,uv)];remain=[]
 for k in range(3):
  for z,sign in [(m['lo'][k],1),(m['hi'][k],-1)]:
   if not poly:break
   poly,side=clip_half(poly,k,z,sign)
   if len(side)>2:remain.append(side)
 if not poly:return [(t,uv)],False
 ans=[]
 for poly in remain:
  for j in range(1,len(poly)-1):
   qq=[poly[0],poly[j],poly[j+1]];a=np.array([r[0]for r in qq])@m['basis']+m['origin'];u=np.array([r[1]for r in qq])
   if np.linalg.norm(np.cross(a[1]-a[0],a[2]-a[0]))>1e-10:ans.append((a,u))
 return ans,True
for row in X:
 n=row['name'];a=np.load(D/row['file']);v=a['v'];f=a['f'];tt=v[f];uv=a['uv'];native=not any(k in n for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_']);ms=[dict(branch,ground_exempt=False)]if native else masks
 if native:ms[0]['lo']=ms[0]['lo'].copy();ms[0]['lo'][2]=2.15
 if n.startswith('V24_21_Exterior_'):
  ms=[branch,mask([13.53,-2.90],[13.53,10.40],2.55,-1.30,3.70)]
 active=[]
 for m in ms:
  if not ((v.max(0)<m['bbox'][0])|(v.min(0)>m['bbox'][1])).any():active.append(m)
 if not active:continue
 candidates=np.zeros(len(f),bool)
 for m in active:candidates|=np.all((tt.max(1)>=m['bbox'][0])&(tt.min(1)<=m['bbox'][1]),axis=1)
 keep=np.ones(len(f),bool);vv=v.tolist();ff=[];uu=[];mi=[];changed=0;removedarea=0.;cuts=0
 for k in np.flatnonzero(candidates):
  pieces=[(tt[k],uv[k])];hit=False
  for m in active:
   new=[]
   for t,u in pieces:
    pp,ch=subtract_box(t,u,m);new.extend(pp);hit|=ch
   pieces=new
   if not pieces:break
  if not hit:continue
  keep[k]=False;changed+=1;before=np.linalg.norm(np.cross(tt[k,1]-tt[k,0],tt[k,2]-tt[k,0]))/2;after=0.
  for t,u in pieces:
   after+=np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2;j=len(vv);vv.extend(t.tolist());ff.append([j,j+1,j+2]);uu.append(u);mi.append(int(a['mi'][k]));cuts+=1
  removedarea+=max(0,before-after)
 if changed:
  fv=np.vstack([f[keep],np.array(ff,np.int32).reshape(-1,3)]);tu=np.concatenate([uv[keep],np.array(uu).reshape(-1,3,2)]);mat=np.r_[a['mi'][keep],mi].astype(np.int32);vv=np.array(vv);used,ix=np.unique(fv.ravel(),return_inverse=True);vv=vv[used];fv=ix.reshape(-1,3);fn='TRIM_'+str(len(out))+'.npz';np.savez_compressed(D/fn,v=vv,f=fv,uv=tu,mi=mat);out.append({'name':n,'file':fn,'materials':row['materials'],'reason':'Only scanning fragments within already modeled building/wall volumes are clipped; original outside features and photo UVs retained'});proof.append({'name':n,'original_triangles':len(f),'touched_triangles':changed,'retained_untouched_triangles':int(keep.sum()),'new_boundary_triangles':cuts,'trimmed_surface_m2':removedarea,'unmodified_photo_materials':True,'source_files_overwritten':False});print('CLIPPED',n,changed,round(removedarea,3),flush=True)
# Remove old earth triangles only in the actual occupied plan of the finished
# paving. This handles thin soil wedges and strips at floor/wall junctions.
a=np.load(D/'V26_1_Continuous_Court_Road_And_Floor_Surfaces.npz');tr=a['v'][a['f']];no=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);region=unary_union([Polygon(t[:,:2])for t in tr[no[:,2]>1e-9]]).buffer(.0002)
n='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';a=arr(n);t=a['v'][a['f']];p=shapely.polygons(t[:,:,:2]);area=shapely.area(p);hit=shapely.intersects(region,p);full=shapely.covers(region,p);keep=~hit;vv=a['v'].tolist();ff=list(a['f'][keep]);uu=list(a['uv'][keep]);mm=list(a['mi'][keep]);clipped=0
for k in np.flatnonzero(hit&~full&(area>1e-12)):
 g=p[k].difference(region)
 for pp in [g]if g.geom_type=='Polygon'else getattr(g,'geoms',[]):
  if pp.geom_type!='Polygon' or pp.area<1e-9:continue
  for tri in triangulate(pp):
   if not pp.covers(tri.representative_point()):continue
   xy=np.array(tri.exterior.coords)[:3];old=t[k];A=np.c_[old[:,:2],np.ones(3)];bc=np.c_[xy,np.ones(3)]@np.linalg.inv(A);z=bc@old[:,2];uv=bc@a['uv'][k];j=len(vv);vv.extend(np.c_[xy,z]);ff.append([j,j+1,j+2]);uu.append(uv);mm.append(a['mi'][k]);clipped+=1
fn='TRIM_NATIVE_SOIL.npz';np.savez_compressed(D/fn,v=np.array(vv),f=np.array(ff,np.int32),uv=np.array(uu),mi=np.array(mm,np.int32));out.append({'name':n,'file':fn,'materials':I[n]['materials'],'reason':'Trim inherited earth only under the exact plan of the finished floor, retaining source heights and UV outside'});proof.append({'name':n,'removed_covered_triangles':int(full.sum()),'retained_untouched_triangles':int(keep.sum()),'new_boundary_triangles':clipped})
(D/'Prepared_Context_Trim.json').write_text(json.dumps({'objects':out,'proof':proof,'exterior_extension_added_again':False,'original_ramp_selected_for_trimming':False},ensure_ascii=False,indent=2),encoding='utf8');print('CONTEXT_TRIM_DONE',len(out),flush=True)
