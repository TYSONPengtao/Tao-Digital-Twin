import json,sys
from pathlib import Path
W=Path.cwd()/'work';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V20');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S
I=json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))
for r in I:
 n=r['name'];e=next(t for t in S['elements'] if t['name']==n)
 if n.startswith(('FACADE','PARTITION','DOOR_')):
  print(n, r.get('actual_3dm_mesh_bbox_local'),len(e.get('parts',[])),e.get('role'),e.get('pivot_world_m'),e.get('open_angle_degrees'))
print('materials',[(k,v) for k,v in S['materials'].items() if any(t in k for t in ['Wall','Facade','Paint','Interior','Column','Plaster'])])
