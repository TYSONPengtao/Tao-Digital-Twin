import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V19');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm'))
for n in ['DOOR_BED_F1_X3.9__LEAF','DOOR_FRONT_CENTER_F1','SITE_INNER_DARK_TIMBER_DOORS','SITE_SW_METAL_ENTRY_GATE_V11__LEAF_1']:
 oo=[ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')];print(n,[(type(o.Geometry).__name__,o.Attributes.Name) for o in oo])
e=next(e for e in S['elements'] if e['name']=='DOOR_FRONT_CENTER_F1')
for j,p in enumerate(ex.expand_parts(e)):
 v,f=ex.world_part(p,e);print(j,p['material'],v.min(0).tolist(),v.max(0).tolist(),p['geometry']['type'])
e=next(e for e in S['elements'] if e['name']=='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY');print('storage metadata',{k:v for k,v in e.items() if k!='parts'})
for j,p in enumerate(next(e for e in S['elements'] if e['name']=='SITE_INNER_DARK_TIMBER_DOORS')['parts']):
 v,f=ex.world_part(p,{'origin':[0,0,0]});print('INNER',j,p['material'],v.min(0).tolist(),v.max(0).tolist())
