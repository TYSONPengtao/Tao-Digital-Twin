import json,sys
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_31';sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from shapely.geometry import Polygon,shape,box
from shapely.ops import unary_union
idx={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
def foot(n):
 a=np.load(D/idx[n]['file']);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return unary_union([Polygon(p[:,:2]) for p in t[abs(no[:,2])>1e-9]]).buffer(0)
rows=[]
for n in ['SLAB_JOINED_F1_Geometry','SITE_KITCHEN_STONE_FLOOR_Geometry','SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V14_OUTER_STORAGE_FLOOR_Geometry','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry','SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP_Geometry','SITE_V15_ENTRY_PAVEMENT_SUPPORTED_SUBGRADE_Geometry','V24_30_Outer_Gate_Swing_Clearance_Graded_Apron','V24_30_Outer_Yard_White_Building_Pad','V24_30_Low_Main_Court_Joint_Base','V24_30_High_North_Lane_And_Rear_Joint_Base','V24_30_Individual_Roadside_Curb_Stones','SITE_V16_GRADED_INTERIOR_SOIL_Geometry','V24_25_Storage_Entrance_Continuous_Light_Gray_Finish','V24_23_Storage_Flush_Alley_Floor']:
 if n in idx:
  p=foot(n);rows.append({'name':n,'outline':p.__geo_interface__,'area':p.area});print(n,'area',p.area,'bounds',p.bounds,flush=True)
old=W/'v24_30';ix={r['name']:r for r in json.loads((old/'Geometry_Index.json').read_text('utf8'))}
for n,r in ix.items():
 if n.startswith('SITE_V12_REBUILT_COURT_'):
  a=np.load(old/r['file']);v=a['v'];f=a['f'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);p=unary_union([Polygon(p[:,:2]) for p in t[abs(no[:,2])>1e-9]]).buffer(0);rows.append({'name':'OLD_'+n,'outline':p.__geo_interface__,'area':p.area});print('OLD',n,p.bounds,'Z',np.unique(np.round(v[:,2],4)).tolist(),flush=True)
(D/'Plan_Outlines.json').write_text(json.dumps(rows),encoding='utf8')
