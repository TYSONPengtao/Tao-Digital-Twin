import sys,json,collections
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import Polygon
from scipy.spatial import cKDTree
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');out=W/'v8_terrain_clear';meta=json.loads((out/'Redline_Calibration.json').read_text());R=Polygon(meta['raw_local_polygon']);I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
for row in I:
 d=np.load(O/'02_Data'/row['file']);t=d['vertices'][d['faces']];c=t.mean(1);hit=shapely.contains_xy(R,c[:,0],c[:,1]);
 if not hit.sum():continue
 if row['name'].startswith(('PHOTO_','SITE_')) and ('KITCHEN' not in row['name'] and 'SOUTH_SCREEN' not in row['name'] and 'SOUTH_EAST' not in row['name']):
  n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];print(row['name'],int(hit.sum()),'z',np.round(np.percentile(c[hit,2],[0,10,25,50,75,90,100]),3).tolist(),'up>',int((hit&(abs(n[:,2])>.65)).sum()))
row=next(x for x in I if x['name']=='PHOTO_BOUNDARY_GROUND_RECOVERY');d=np.load(O/'02_Data'/row['file']);t=d['vertices'][d['faces']];c=t.mean(1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];hit=shapely.contains_xy(R,c[:,0],c[:,1])&(abs(n[:,2])>.65);c=c[hit];g=np.floor(c[:,:2]).astype(int);z={}
for ky in set(map(tuple,g)):q=c[(g==ky).all(1),2];z[str(ky)]=list(np.round(np.percentile(q,[10,50,90]),3))
(out/'Ground_Cell_Heights.json').write_text(json.dumps(z,indent=2));print('cells',len(z))
