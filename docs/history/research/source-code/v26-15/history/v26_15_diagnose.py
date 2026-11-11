from v26_2_common import *
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
D=W/'v26_15';I=D/'Input';J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};cache={}
def get(n):
 if n not in cache:
  r=ix[n];a=np.load(I/r['file']);cache[n]=(r,a,solid(a['v'],a['f'],n))
 return cache[n]
HN='V26_3_House_Connected_Walls_And_Stairs';GN='V26_2_Continuous_Ground_And_Perimeter_Shell';_,ha,h=get(HN);_,ga,g=get(GN);roi=cube([3.4,-.5,-.70],[9.6,2.35,-.30]);overlap=h^g^roi
print('PORCH_OVERLAP',overlap.volume(),flush=True)
for name,a in[(HN,ha),(GN,ga)]:
 t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);c=t.mean(1);mask=(c[:,0]>8.75)&(c[:,0]<9.5)&(c[:,1]>-.4)&(c[:,1]<2.3)&(c[:,2]>-.65)&(c[:,2]<-.30);mats=ix[name]['materials'];rows=[]
 for k in np.flatnonzero(mask):
  if np.linalg.norm(t[k].ptp(0))<.005:continue
  rows.append({'normal':n[k].round(5).tolist(),'bounds':np.array([t[k].min(0),t[k].max(0)]).round(6).tolist(),'material':mats[int(a['mi'][k])]})
 print('PORCH_FACES',name,json.dumps(rows)[:14000],flush=True)
cores=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
print('STAIR_CORES',[(r['name'],r['bounds_m'])for r in cores if any(k in r['name']for k in['Stair','KZ','BEAM'])and np.array(r['bounds_m'])[1,1]>7.4],flush=True)
components={}
for name in ['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','V24_16_Storage_Entrance_White_Wall_Return','V26_7_Inner_Gate_Rear_Return_Closure']:
 r,a,m=get(name);f=a['f'];nv=len(a['v']);ed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);graph=coo_matrix((np.ones(len(ed)),(ed[:,0],ed[:,1])),shape=(nv,nv));count,labels=connected_components(graph,directed=False);rows=[]
 for k in np.unique(labels[f].ravel()):
  ids=np.flatnonzero(labels==k);mask=np.any(np.isin(f,ids),1);v=a['v'][ids];rows.append({'vertices':len(ids),'triangles':int(mask.sum()),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'materials':sorted({r['materials'][j]for j in np.unique(a['mi'][mask])})})
 components[name]=rows;print('COMPONENTS',name,json.dumps(rows),flush=True)
stations=[]
for x in [7.7,7.9,8.0,8.15,8.35,8.5,8.75,9.0,9.25,9.45]:
 for y in[-11.6,-11.45,-11.35,-11.2,-11.05,-10.9]:
  hh=g.ray_cast([x,y,.10],[x,y,-1.0]);up=[q for q in hh if q.normal[2]>.7];stations.append({'x':x,'y':y,'ground_top':max((q.position[2]for q in up),default=None)})
(D/'Diagnosis.json').write_text(json.dumps({'porch_overlap_m3':overlap.volume(),'components':components,'gate_ground':stations},ensure_ascii=False,indent=2),'utf8')
print('GATE_FLOOR',json.dumps(stations),flush=True)
