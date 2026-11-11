import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S
for e in S['elements']:
 if (e['layer']=='60_SITE' and (e['name'] in ['SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD','SITE_CURVED_PUBLIC_ROAD','SITE_CONTEXT_TERRAIN','SITE_EAST_GARDEN'] or any(i in e['name'] for i in ['SW_METAL_ENTRY_GATE','KITCHEN_PLINTH']))):
  vs=[]
  for p in ex.expand_parts(e):
   v,f=ex.world_part(p,e)
   if v is not None:vs.append(v)
  if vs:
   v=np.concatenate(vs);print(e['name'],v.min(0).round(4),v.max(0).round(4),'parts',len(vs))
