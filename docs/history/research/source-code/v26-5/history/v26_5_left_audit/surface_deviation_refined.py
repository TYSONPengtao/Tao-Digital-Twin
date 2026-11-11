exec((__import__('pathlib').Path(__file__).parent/'regression_saved.py').read_text('utf8').split("ck('Saved model hash")[0])
from scipy.spatial import cKDTree

def sample(m):
 a=m.to_mesh64();v=np.asarray(a.vert_properties)[:,:3];f=np.asarray(a.tri_verts);return np.vstack([v,v[f].mean(1)])
def distances(points,m,exact=False):
 a=m.to_mesh64();v=np.asarray(a.vert_properties)[:,:3];f=np.asarray(a.tri_verts);t=v[f];tree=cKDTree(t.mean(1));out=[]
 for start in range(0,len(points),8 if exact else 256):
  p=points[start:start+(8 if exact else 256)];ids=np.tile(np.arange(len(t)),(len(p),1)) if exact else tree.query(p,k=min(96,len(t)))[1];T=t[ids];Q=p[:,None,:];A=T[:,:,1]-T[:,:,0];B=T[:,:,2]-T[:,:,0];V=Q-T[:,:,0];aa=np.sum(A*A,-1);bb=np.sum(B*B,-1);ab=np.sum(A*B,-1);aq=np.sum(A*V,-1);bq=np.sum(B*V,-1);det=np.maximum(aa*bb-ab*ab,1e-30);s=(bb*aq-ab*bq)/det;u=(aa*bq-ab*aq)/det;N=np.cross(A,B);dd=np.sum(V*N,-1)**2/np.maximum(np.sum(N*N,-1),1e-30);inside=(s>=-1e-10)&(u>=-1e-10)&(s+u<=1+1e-10);dd=np.where(inside,dd,np.inf)
  for j in range(3):
   P=T[:,:,j];E=T[:,:,(j+1)%3]-P;fac=np.clip(np.sum((Q-P)*E,-1)/np.maximum(np.sum(E*E,-1),1e-30),0,1);d=np.sum((Q-P-fac[:,:,None]*E)**2,-1);dd=np.minimum(dd,d)
  out.extend(np.sqrt(np.maximum(0,dd.min(1))).tolist())
 out=np.array(out)
 if not exact:
  bad=out>1e-5
  if bad.any():out[bad]=distances(points[bad],m,True)
 return out
norm=np.array([.8111365302967483,.5848568450639461]);limit=1.1723606549172076;poly=[[(limit-norm[1]*y)/norm[0],y]for y in [.7,2.3]]+[[1.,2.3],[1.,.7]];cut=section(poly,3.5).translate([0,0,-.7]);rows=[]
for n in ['SITE_COURTYARD_WEST_TILE_WALL_'+s+'_Geometry'for s in['TILE_COPING','V10_COVER_TILES','V10_LOTUS_DRIP_ENDS','V10_OPEN_FLOWER_BRICKS','V10_PAN_TILES','V10_RIDGE_SEAT_AND_CAP']]+['V26_1_Courtyard_West_Wall_Single_Surface']:
 o=load(OLD,OI,n)-cut;m=load(NEW,NI,n);s=sample(o);t=sample(m);d1=distances(s,m);d2=distances(t,o);r={'name':n,'expected_to_native_sample_count':len(s),'native_to_expected_sample_count':len(t),'expected_to_native_max_m':float(d1.max(initial=0)),'native_to_expected_max_m':float(d2.max(initial=0)),'expected_to_native_p999_m':float(np.quantile(d1,.999)),'native_to_expected_p999_m':float(np.quantile(d2,.999))};rows.append(r);print(r,flush=True)
(Path(__file__).parent/'saved_surface_deviation_refined.json').write_text(json.dumps(rows,indent=2),'utf8')
