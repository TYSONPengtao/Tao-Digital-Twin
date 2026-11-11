import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
for e in S['elements']:
 if e['name'].startswith(('ENTRANCE_STEP','SITE_PERIMETER_JOINED_RETAINING_WALL_0_BODY','SITE_PERIMETER_JOINED_RETAINING_WALL_1_BODY')):print(json.dumps(e,ensure_ascii=False)[:1500])
for p in Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\02_Data').glob('*Hole*'):
 print(p.name, p.read_text()[:2000])
