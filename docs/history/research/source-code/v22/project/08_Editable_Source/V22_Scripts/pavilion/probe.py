import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V21');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));I={e['name']:e for e in json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
for e in S['elements']:
 n=e['name']
 if 'GAZEBO' not in n and 'PAVILION' not in n:continue
 a=np.load(B/'02_Data'/I[n]['file'])['vertices']
 print(n, 'parts',len(e.get('parts',[])), 'bbox',a.min(0).round(4),a.max(0).round(4), 'mats',set(p['material'] for p in e.get('parts',[])))
 if 'POSTS' in n or 'BEAMS' in n or 'ROOF' in n:print(str(e)[:600])
