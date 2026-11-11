from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1')];import numpy as np
D=W/'v26_6';R=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['objects'][0];a=np.load(D/R['file']);T=a['v'][a['f']];N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);N/=np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-30);out=[]
for floor,bottom,top in [(1,1.3227050304412842,1.5),(2,5.086377143859863,5.25)]:
 sel=(np.max(abs(T[:,:,0]-5.2),axis=1)<.00001)&(N[:,0]>.99)&(T.max(1)[:,1]>=8.53999)&(T.min(1)[:,1]<=9.55001)&(T.max(1)[:,2]>=bottom-.00001)&(T.min(1)[:,2]<=top+.00001)
 rows=[]
 for i in np.flatnonzero(sel):rows.append({'index':int(i),'material':R['materials'][int(a['mi'][i])],'vertices':T[i].tolist(),'min_z':float(T[i,:,2].min()),'max_z':float(T[i,:,2].max()),'crosses_actual_tread_height':bool(T[i,:,2].min()<bottom<T[i,:,2].max())})
 print('FLOOR',floor,'selected',len(rows),'crossing',[r for r in rows if r['crosses_actual_tread_height']],flush=True);out.append({'floor':floor,'actual_lower':bottom,'top':top,'selected':rows})
(Path(__file__).parent/'Prepared_direct_riser_face_selection.json').write_text(json.dumps(out,indent=2),'utf8')
