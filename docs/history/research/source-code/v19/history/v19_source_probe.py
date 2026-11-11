import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V18/08_Editable_Source/Architecture_Scene_V18.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};rows=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH','SITE_SOUTH_SCREENWALL_RAISED_BODY','SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE','SITE_SCREENWALL_HORIZONTAL_MOULDINGS']:
 e=E[n];print(n,len(e['parts']),flush=True)
 for j,p in enumerate(e['parts']):
  v,fs,_,_=ex.solid_data(p['geometry']);v=np.array(v);r={'node':n,'i':j,'material':p['material'],'type':p['geometry']['type'],'min':v.min(0).tolist(),'max':v.max(0).tolist()};rows.append(r)
  if j<6 or 'SCREENWALL' in n:print(r,flush=True)
  if j<3:print(json.dumps(p['geometry'])[:2500],flush=True)
Path('work/v19').mkdir(exist_ok=True);Path('work/v19/Wall_Part_Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
