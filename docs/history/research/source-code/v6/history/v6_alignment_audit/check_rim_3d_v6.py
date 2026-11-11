"""Independent 3D check of actual source mesh rim, not unrelated XY surfaces."""
import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,shapely
from shapely.geometry import Polygon
from nearest_photo_projection import PhotoProjector,closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid')
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(C['origin'])
h=json.loads((O/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(h['local']['outer'],h['local']['holes'])
q=[];stats=[]
for path in sorted((O/'02_Data').glob('Base_*.npz')):
 d=np.load(path);v=(d['vertices']-origin)@R;f=d['faces']
 edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[f[:,2]==f[:,3]][:,[2,0]],f[f[:,2]!=f[:,3]][:,[2,3]],f[f[:,2]!=f[:,3]][:,[3,0]]])
 edges=np.sort(edges,axis=1);ue,counts=np.unique(edges,axis=0,return_counts=True);boundary=ue[counts==1]
 p=v[boundary];dist=shapely.distance(shapely.points(p[:,:,:2].mean(axis=1)),H.exterior)
 selected=p[dist<=.025]
 pts=[]
 for edge in selected:
  length=np.linalg.norm(edge[1]-edge[0]);number=max(2,int(math.ceil(length/.1))+1)
  if number>100:continue
  pts.extend(edge[0]+np.linspace(0,1,number)[:,None]*(edge[1]-edge[0]))
 if pts:
  pts=np.array(pts);dd=shapely.distance(shapely.points(pts[:,:2]),H.exterior);pts=pts[dd<=.00001];q.extend(pts)
 stats.append({'file':path.name,'all_naked_edges':len(boundary),'near_main_hole_edges':len(selected),'sample_points':len(pts)})
tri=[];transition=[]
for row in json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8')):
 if row['name'].startswith('PHOTO_BOUNDARY_') or row['name']=='PHOTO_RIM_TRANSITION':
  d=np.load(O/'02_Data'/row['file']);tri.append(d['vertices'][d['faces']])
  if row['name']=='PHOTO_RIM_TRANSITION':transition.append(tri[-1])
tri=np.concatenate(tri);q=np.unique(np.array(q),axis=0)
# UV is irrelevant to geometry distance. Give each donor triangle an admissible
# dummy UV triangle, then exact closest-point distance among centroid candidates.
uv=np.tile(np.array([[0,0],[1,0],[0,1]])[None,:,:],(len(tri),1,1));P=PhotoProjector(tri,uv,np.zeros(len(tri),np.int32),{})
res=P.query(q,max_distance=10,k=128,batch_size=512);dist=res['distance']
if transition:
 transition=np.concatenate(transition)
 # Thin long transition faces have distant centroids. Test every transition
 # explicitly instead of relying on the local centroid shortlist.
 for start in range(0,len(q),64):
  qq=q[start:start+64];_,_,dd=closest_on_triangles(np.repeat(qq,len(transition),axis=0),np.tile(transition,(len(qq),1,1)))
  dist[start:start+len(qq)]=np.minimum(dist[start:start+len(qq)],dd.reshape(len(qq),len(transition)).min(axis=1))
worst=np.argsort(dist)[-30:][::-1]
report={'source':'Actual naked edges of unchanged five base meshes whose sample XY lies on main void ring within 0.00001m; nearby lower ground / backsides outside the permitted patch are excluded','sample_step_m':.1,'photo_patch_triangles':len(tri),'source_objects':stats,'samples':len(q),'distance_m':dict(zip(['p50','p95','p99','max'],np.quantile(dist,[.5,.95,.99,1]).tolist())),'count_over_0p005m':int((dist>.005).sum()),'count_over_0p02m':int((dist>.02).sum()),'count_over_0p05m':int((dist>.05).sum()),'worst_samples':[{'xyz_local_m':q[i].tolist(),'closest_patch_distance_m':float(dist[i])} for i in worst],'status':'PASS' if np.quantile(dist,.95)<.02 and dist.max()<.05 else 'NEEDS_REVIEW','scope':'Source rim proximity to added measured photo surfaces. Does not claim all meshes are welded watertight.'}
(O/'06_Report/Actual_Source_Rim_3D_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
