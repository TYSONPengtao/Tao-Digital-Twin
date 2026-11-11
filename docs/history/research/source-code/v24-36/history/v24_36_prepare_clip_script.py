from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape,mapping
D=W/'v24_36';pieces=[]
for r in json.loads((W/'v24_35/Envelope_Index.json').read_text()):
 a=np.load(W/'v24_35'/r['file']);t=a['v'][a['f'],:2];ar=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));pp=shapely.polygons(t)
 p=shapely.union_all(shapely.buffer(pp,.22))if r['wall']else shapely.union_all(pp[ar>1e-10]).buffer(.22);pieces.append(p)
native=shapely.union_all(pieces).buffer(0);(D/'Native_Complete_Envelope.geojson').write_text(json.dumps(mapping(native)))
parts=[native]+[shape(json.loads((W/'v24_34'/n).read_text()))for n in ['Existing_Coverage.geojson','Added_Coverage.geojson']];mask=shapely.union_all(parts).buffer(0);(D/'Existing_Coverage.geojson').write_text(json.dumps(mapping(mask)));print('CURRENT_PROTECTED',mask.area,'COMPLETE_NATIVE_ROOF_WALL',native.area,flush=True)
s=(W/'v24_34_clip.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_36'").replace('MB7_Registration.json','PTJIA6_Registration.json').replace('Decoded_L27_Index.json','Decoded_L99_Index.json').replace('1187','2117').replace('1186','2116').replace('3347669','6032331');(W/'v24_36_clip.py').write_text(s,encoding='utf8');compile(s,'v24_36_clip.py','exec')
