from pathlib import Path
import sys,json,hashlib
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_36.blend';mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));native=shape(json.loads((D/'Native_Complete_Envelope.geojson').read_text()));shapely.prepare(mask);shapely.prepare(native);checks=[];overlap=0.;bodyoverlap=0.;total=0;rows=json.loads((D/'Final_Exterior_Index.json').read_text())
for i,r in enumerate(rows):
 a=np.load(D/r['file']);v=a['v'].astype(np.float32).astype(float);t=v[a['f'],:2];ar=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));p=shapely.polygons(t[ar>1e-9]);hit=shapely.intersects(mask,p)
 if hit.any():overlap+=float(shapely.area(shapely.intersection(p[hit],mask)).sum())
 hit=shapely.intersects(native,p)
 if hit.any():bodyoverlap+=float(shapely.area(shapely.intersection(p[hit],native)).sum())
 total+=len(a['f'])
 if i%600==0:print('SURFACE',i,len(rows),flush=True)
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
ck('New PTJIA6 faces do not overlay existing model or MB7 coverage',overlap<1e-5,overlap_area_m2=overlap)
ck('Complete native kitchen storage roof and curved wall envelope excludes new scan ghosts',bodyoverlap<1e-5,overlap_area_m2=bodyoverlap)
inventory=json.loads((D/'3MX_Inventory.json').read_text());idx={r['name']:r for r in inventory['files']};names={r['source_node']for r in rows};bad=[n for n in names if idx[n]['links']];ck('All imported 3MXB source nodes are terminal leaves without parent child LOD duplicates',not bad,nonterminal_nodes=bad)
ck('Only a subset of the supplied PTJIA6 exterior is added',total<6032331 and len(rows)<2116,imported_triangles=total,source_triangles=6032331,imported_parts=len(rows))
reg=json.loads((D/'PTJIA6_Registration.json').read_text());ck('Shared feature and geometric registration remain within declared local context tolerance',reg['landmark_inliers']>=15 and reg['inlier_rms_m']<.35,inliers=reg['landmark_inliers'],rms_m=reg['inlier_rms_m'],p95_m=reg['inlier_p95_m'],scale=reg['feature_scale'],basis='Photogrammetric overlap; no new independent survey control.')
source=Path(inventory['source']);decoded=json.loads((D/'Decoded_L99_Index.json').read_text());seen=set();bad=[]
for r in decoded:
 if r['node']in seen:continue
 seen.add(r['node'])
 if hashlib.sha256((source/r['node']).read_bytes()).hexdigest()!=r['source_sha256']:bad.append(r['node'])
ck('Every used source 3MXB file remains byte-identical',not bad,checked_files=len(seen),changed=bad)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V24_36_Surface_QA.json').write_text(json.dumps({'status':'PASS_MISSING_PTJIA6_ONLY_AND_COMPLETE_NATIVE_ENVELOPE'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},indent=2));print('SURFACE_QA',len(checks),'FAIL',len(fail),flush=True)
