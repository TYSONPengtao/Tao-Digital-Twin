# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
from pyproj import Transformer
D=W/'v24_34';lat=np.deg2rad(TAO_PRIVATE_SITE_003);lon=np.deg2rad(TAO_PRIVATE_SITE_024);B=np.array([[-np.sin(lon),np.cos(lon),0],[-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)],[np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)]])
ecef=Transformer.from_crs(4979,4978,always_xy=True);origin=np.array(ecef.transform(np.rad2deg(lon),np.rad2deg(lat),0.));proj=Transformer.from_crs(32647,4978,always_xy=True);C=np.array(json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text('utf8'))['local_to_survey']);Ci=np.linalg.inv(C)
def local(p):
 v=np.array(proj.transform(TAO_PRIVATE_SITE_021+p[0],TAO_PRIVATE_SITE_006+p[1],p[2]));enu=B@(v-origin);return Ci[:3,:3]@enu+Ci[:3,3]
p=np.array([0.,0.,1370.]);base=local(p);A=np.column_stack([local(p+np.eye(3)[i])-base for i in range(3)]);T=np.eye(4);T[:3,:3]=A;T[:3,3]=base-A@p
rows=json.loads((D/'Decoded_L21_Index.json').read_text('utf8'));v=np.concatenate([np.load(D/r['file'])['v'] for r in rows]);q=v@T[:3,:3].T+T[:3,3];(D/'Coordinate_Seed.json').write_text(json.dumps({'source_srs':'EPSG:32647','source_origin_m':[TAO_PRIVATE_SITE_021,TAO_PRIVATE_SITE_006,0.],'target_srs':'Local architectural model based on ENU:TAO_PRIVATE_SITE_003,TAO_PRIVATE_SITE_024','seed_source_to_local':T.tolist(),'seed_bounds_local':[q.min(0).tolist(),q.max(0).tolist()],'requires_overlap_registration':True,'seed_only_does_not_assume_shared_vertical_datum':True},indent=2),encoding='utf8');print('SEED',T.tolist(),'BOUNDS',q.min(0).tolist(),q.max(0).tolist(),flush=True)
