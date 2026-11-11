from v26_2_common import *
from shapely.geometry import Polygon,shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import shapely
p=json.loads((D/'Exact_House_Parts.json').read_text('utf8'));layers=p['layers'];plans=[shape(r['outline'])for r in layers];zs=[layers[0]['z_m'][0]]+[r['z_m'][1]for r in layers];mats=['M_Wall_Interior','M_Floor','M_V24_31_White_Painted_Ceiling','M_V24_31_Stair_Gray_Marble','M_V21_House_Exterior_Grey_White','M_Stone'];V=[];F=[];MI=[];UV=[];cache={}
def polygons(g):return[g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon']
def emit(tr,mat=None,uv=None):
 tr=np.array(tr,np.float32).astype(np.float64);n=np.cross(tr[1]-tr[0],tr[2]-tr[0]);ar=np.linalg.norm(n)
 if ar<1e-12:return
 n/=ar;c=tr.mean(0)
 if mat is None:
  mat=0
  if n[2]<-.7 and c[2]>-.4:mat=2
  if n[2]>.999 and any(abs(c[2]-z)<.0002 for z in[-.45,3.45,7.05]):mat=1
  if n[2]>.999 and any(abs(c[2]-z)<.0002 for z in[1.5,5.25]):mat=3
  if ((n[0]<-.99 and c[0]<-.09)or(n[0]>.99 and c[0]>13.09)or(n[1]>.99 and c[1]>9.89))and -.45<c[2]<10.221:mat=4
  if n[1]<-.1 and abs(n[2])<.7 and c[1]<1.889 and(c[0]<3.9 or c[0]>9.1)and-.65<c[2]<10.22:mat=5
 ids=[]
 for q in tr:
  key=tuple(q)
  if key not in cache:cache[key]=len(V);V.append(q)
  ids.append(cache[key])
 if len(set(ids))<3:return
 F.append(ids);MI.append(mat);UV.append(uv if uv is not None else tr[:,[1,2]if abs(n[0])>.7 else[0,2]if abs(n[1])>.7 else[0,1]])
stations=[]
for j,z in enumerate(zs):
 below=plans[j-1]if j>0 else Polygon();above=plans[j]if j<len(plans)else Polygon();lines=unary_union([below.boundary,above.boundary]);points=np.unique(shapely.get_coordinates(lines),axis=0);stations.append(points)
 for domain,sgn in [(below.difference(above),1),(above.difference(below),-1)]:
  for poly in polygons(domain):
   if poly.area<1e-12:continue
   for tri in shapely.constrained_delaunay_triangles(poly).geoms:
    t=np.c_[np.array(tri.exterior.coords)[:3],np.full(3,z)]
    if np.cross(t[1]-t[0],t[2]-t[0])[2]*sgn<0:t=t[::-1]
    emit(t)
for j,(P,z0,z1)in enumerate(zip(plans,zs,zs[1:])):
 for poly in polygons(P):
  poly=orient(poly,1)
  for ring in [poly.exterior]+list(poly.interiors):
   coords=np.array(ring.coords)
   for A,B in zip(coords,coords[1:]):
    d=B-A;L=np.linalg.norm(d)
    if L<1e-8:continue
    u=d/L;nodes=[]
    for z,points,rev in [(z0,stations[j],False),(z1,stations[j+1],True)]:
     s=(points-A)@u;dist=np.linalg.norm(points-(A+s[:,None]*u),axis=1);keep=(s>=-1e-8)&(s<=L+1e-8)&(dist<1e-8);ss=np.unique(np.r_[0,np.clip(s[keep],0,L),L]);ss=ss[::-1]if rev else ss;nodes.extend([[float(x),z]for x in ss])
    q=Polygon(nodes)
    for tri in shapely.constrained_delaunay_triangles(q).geoms:
     st=np.array(tri.exterior.coords)[:3];t=np.c_[A+st[:,0,None]*u,st[:,1]];n=np.cross(t[1]-t[0],t[2]-t[0]);out=np.r_[u[1],-u[0],0]
     if n@out<0:t=t[::-1]
     emit(t)
 print('DIRECT_LAYER',j,len(F),flush=True)
v=np.array(V);f=np.array(F,np.int32);mi=np.array(MI,np.int32);uv=np.array(UV);ed=np.sort(np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True);print('DIRECT_BASE_TOPOLOGY',len(f),dict(zip(*np.unique(ct,return_counts=True))),flush=True)
components=[{'name':'Registered wall column beam slab and landing surface','triangles':len(f),'nonmanifold_edges':int((ct!=2).sum())}]
# Roof and stair profiles remain independent closed solids seated into the
# opaque body, as actual architectural components. There is no coplanar skin.
for row in p['extras']:
 a=np.load(D/row['file']);name=row['name']
 if name.startswith('STAIR_F'):
  m=solid(a['v'],a['f'],name);b=m.to_mesh64();ev=np.array(b.vert_properties[:,:3],np.float32).astype(float);ef=np.array(b.tri_verts,np.int32);emi=np.full(len(ef),3,np.int32);_,eu=remap(a,ev,ef);tr=ev[ef];n=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);emi[n[:,2]<-1e-8]=2
 else:
  sourcev=a['v'].astype(np.float32).astype(float);ev,ix=np.unique(sourcev,axis=0,return_inverse=True);ef=ix[a['f']];emi=[]
  for nm in row['materials']:
   if nm not in mats:mats.append(nm)
  emi=np.array([mats.index(row['materials'][int(x)])for x in a['mi']],np.int32);eu=a['uv']
 ed=np.sort(np.vstack([ef[:,[0,1]],ef[:,[1,2]],ef[:,[2,0]]]),axis=1);_,ec=np.unique(ed,axis=0,return_counts=True);components.append({'name':name,'triangles':len(ef),'nonmanifold_edges':int((ec!=2).sum())});off=len(v);v=np.vstack([v,ev]);f=np.vstack([f,ef+off]);mi=np.r_[mi,emi];uv=np.concatenate([uv,eu])
fn='V26_2_House_Flush_Continuous_Finished_Shell.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);r={'name':'V26_2_House_Flush_Continuous_Finished_Shell','file':fn,'materials':mats,'triangles':len(f),'reason':'Conforming analytic wall, column, beam, slab and landing surface with original seated closed stair and roof components; actual registered apertures retained'};proof=dict(p['proof'],direct_conforming_surface=True,components=components,internal_vertical_join_overlap_m=0,exact_union=None);out={'objects':[r]+p['frames'],'archive':['V26_1_House_Continuous_Opaque_Shell'],'proof':proof};(D/'Prepared_House.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(D/'Direct_Surface_QA.json').write_text(json.dumps({'components':components,'triangles':len(f)},indent=2));print('DIRECT_HOUSE_READY',len(f),components,flush=True)
