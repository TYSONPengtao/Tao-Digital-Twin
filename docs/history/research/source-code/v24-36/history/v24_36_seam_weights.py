from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape,box
D=W/'v24_36';mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));near=mask.buffer(1.5);boundary=mask.boundary;rows=json.loads((D/'Missing_Exterior_Index.json').read_text());selected=0
for r in rows:
 lo,hi=np.array(r['bounds']);r['seam_weight_file']=None
 if not near.intersects(box(lo[0],lo[1],hi[0],hi[1])):continue
 a=np.load(D/r['file']);v=a['v'];sel=shapely.contains_xy(near,v[:,0],v[:,1]);w=np.zeros(len(v));dist=shapely.distance(shapely.points(v[sel,:2]),boundary);w[sel]=np.maximum(0,1-dist/1.5)**2;fn='SEAM_'+Path(r['node']).stem+'.npz';np.savez_compressed(D/fn,w=w);r['seam_weight_file']=fn;selected+=1
(D/'Missing_Exterior_Index.json').write_text(json.dumps(rows,indent=2));report=json.loads((D/'Clip_Report.json').read_text());report['method']='3MXB finest non-overlapping leaf frontier; exact projected subtraction outside current native and MB7 exterior plus full roof and wall protective envelope; original CTM coordinates and JPEG bytes';report['seam_width_m']=1.5;report['seam_tiles']=selected;(D/'Clip_Report.json').write_text(json.dumps(report,indent=2));print('SEAM_TILES',selected,flush=True)
