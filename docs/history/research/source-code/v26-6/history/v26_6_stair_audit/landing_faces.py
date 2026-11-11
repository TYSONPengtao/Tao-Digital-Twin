from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
D=W/'v26_5/Final';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};n='V26_3_House_Connected_Walls_And_Stairs';r=I[n];a=np.load(D/r['file']);T=a['v'][a['f']];N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-30)
def clip(P,lo,hi):
 for ax in range(3):
  for edge,sgn in [(lo[ax],1),(hi[ax],-1)]:
   O=[]
   if not len(P):return P
   for p,q in zip(P,np.roll(P,-1,axis=0)):
    pin=(p[ax]-edge)*sgn>=-1e-9;qin=(q[ax]-edge)*sgn>=-1e-9
    if pin:O.append(p)
    if pin!=qin:
     t=(edge-p[ax])/(q[ax]-p[ax]);O.append(p+t*(q-p))
   P=np.array(O)
 return P
rows=[]
for fl,off in [(1,0.),(2,3.75)]:
 lo=np.array([5.19,8.54,1.34+off]);hi=np.array([5.31,9.68,1.51+off]);sel=(T.max(1)>=lo-1e-8).all(1)&(T.min(1)<=hi+1e-8).all(1);faces=[]
 for i in np.flatnonzero(sel):
  p=clip(T[i],lo,hi)
  if len(p)<3:continue
  ar=.5*np.linalg.norm(sum((np.cross(p[j]-p[0],p[j+1]-p[0])for j in range(1,len(p)-1)),np.zeros(3)))
  if ar<1e-10:continue
  cn=p.mean(0);normal=N[i];role='other'
  if normal[2]>.99 and abs(cn[2]-(1.3950585+off))<.0002:role='bearing beam 35 mm raised ledge top'
  elif normal[0]>.99 and abs(cn[0]-5.3)<.0002:role='bearing beam exposed nose riser'
  elif normal[0]>.99 and abs(cn[0]-5.2)<.0002:role='landing front riser above beam ledge'
  elif normal[2]>.99 and abs(cn[2]-(1.499951+off))<.0002:role='landing gray stone top'
  elif normal[2]>.99 and abs(cn[2]-(1.3600585+off))<.0002:role='last gray tread top'
  faces.append({'triangle_index':int(i),'material':r['materials'][int(a['mi'][i])],'normal':normal.tolist(),'clipped_area_m2':float(ar),'clipped_polygon':p.tolist(),'role':role})
 summary={}
 for q in faces:
  k=q['role']+' / '+q['material'];summary[k]=summary.get(k,0)+q['clipped_area_m2']
 result={'floor':fl,'region_bounds':[lo.tolist(),hi.tolist()],'summary_area_m2':summary,'faces':faces};rows.append(result);print('FLOOR',fl,json.dumps(summary,indent=2),flush=True)
P=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend');(Path(__file__).parent/'native_landing_stripe_faces.json').write_text(json.dumps({'model':str(P),'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'house_object':n,'findings':rows},indent=2),'utf8')
