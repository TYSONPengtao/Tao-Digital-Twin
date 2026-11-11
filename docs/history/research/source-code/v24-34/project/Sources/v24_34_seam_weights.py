from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_34';mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));boundary=mask.boundary
for r in json.loads((D/'Missing_Exterior_Index.json').read_text()):
 p=D/r['file'];a=dict(np.load(p));dist=shapely.distance(shapely.points(a['v'][:,:2]),boundary);a['seam_weight']=np.maximum(0,1-dist/.75)**2;np.savez_compressed(p,**a)
print('SEAM_WEIGHTS_DONE',flush=True)
