# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from pyproj import Transformer
D=W/'v24_36';layer=json.loads((D/'Scene_Metadata.json').read_text())['layers'][0];slat,slon=map(float,layer['SRS'].split(':')[1].split(','));tlat,tlon=TAO_PRIVATE_SITE_003,TAO_PRIVATE_SITE_024
def basis(lat,lon):
 lat,lon=np.deg2rad([lat,lon]);return np.array([[-np.sin(lon),np.cos(lon),0],[-np.sin(lat)*np.cos(lon),-np.sin(lat)*np.sin(lon),np.cos(lat)],[np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)]])
ecef=Transformer.from_crs(4979,4978,always_xy=True);so=np.array(ecef.transform(slon,slat,0));to=np.array(ecef.transform(tlon,tlat,0));Bs=basis(slat,slon);Bt=basis(tlat,tlon);C=np.array(json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text())['local_to_survey']);Ci=np.linalg.inv(C);T=np.eye(4);T[:3,:3]=Ci[:3,:3]@Bt@Bs.T;T[:3,3]=Ci[:3,:3]@Bt@(so-to+Bs.T@np.array(layer['SRSOrigin']))+Ci[:3,3]
rows=json.loads((D/'Decoded_L21_Index.json').read_text());v=np.concatenate([np.load(D/r['file'])['v']for r in rows]);p=v@T[:3,:3].T+T[:3,3];(D/'Coordinate_Seed.json').write_text(json.dumps({'source_srs':layer['SRS'],'source_origin_m':layer['SRSOrigin'],'seed_source_to_local':T.tolist(),'seed_bounds_local':[p.min(0).tolist(),p.max(0).tolist()],'requires_overlap_registration':True,'method':'exact ENU to ECEF to existing model ENU affine transform; no guessed XY offsets'},indent=2));print('PTJIA6_SEED_BOUNDS',p.min(0).tolist(),p.max(0).tolist(),flush=True)
