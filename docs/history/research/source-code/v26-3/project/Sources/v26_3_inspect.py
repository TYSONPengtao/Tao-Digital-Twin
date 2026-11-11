from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
D=W/'v26_3';rows=json.loads((D/'Components.json').read_text('utf8'));I={r['name']:r for r in rows}
for r in rows:
 if r['name'].startswith(('ROOF_','UTILITY_','HOUSE_V22_FRONT_TRANSOM','SLAB_JOINED','PARTITIONS_JOINED'))or'Secondary'in r['name']:
  print(r['name'],np.round(r['bounds'],3).tolist(),r['triangles'],'hidden',r['hide_render'],'mats',r['materials'])
r=I['V26_2_House_Flush_Continuous_Finished_Shell'];a=np.load(D/r['file']);v,f,mi=a['v'],a['f'],a['mi'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);areas=np.linalg.norm(n,axis=1);n/=np.maximum(areas[:,None],1e-30);cent=t.mean(1)
print('MATERIALS',r['materials'])
for k,mat in enumerate(r['materials']):
 ix=mi==k;down=ix&(n[:,2]<-.5);up=ix&(n[:,2]>.5);print(mat,int(ix.sum()),'area',round(areas[ix].sum()/2,2),'down',int(down.sum()),'downarea',round(areas[down].sum()/2,2),'zdown',np.round([cent[down,2].min(),cent[down,2].max()],3).tolist()if down.any()else[]) 
m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64),np.array(f,dtype=np.uint64)));print('NATIVE_MANIFOLD',m.status(),m.volume())
def ray(A,B):
 hits=m.ray_cast(A,B)
 return[{'p':np.round(h.position,5).tolist(),'tri':int(h.face_id),'normal':np.round(n[h.face_id],4).tolist(),'material':r['materials'][int(mi[h.face_id])]}for h in hits[:8]]
for x,y in [(1.1,8.5),(3,8.8),(6.5,5),(8.4,8),(8.4,9),(10,8.8),(11.5,8.5)]:
 for floor,ceiling in [(-.45,3.32),(3.45,6.92),(7.05,10.22)]:print('CEILING_RAY',x,y,floor,ray([x,y,floor+1.5],[x,y,13]))
for fl,z in [(1,2.5),(2,6.3)]:print('TRANSOM_RAY',fl,ray([6.5,1.5,z],[6.5,2.8,z]))
print('PROBE_DONE')
