import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S
for e in S['elements']:
 if any(t in e['name'] for t in ['BALCONY_PANEL','MOULDING']):print('mould',e['name'])
 if any(p['material']=='M_Grey_Brick' for p in ex.expand_parts(e)):
  print(e['name'],[(p['geometry']['type'],str(p['geometry'])[:210]) for p in ex.expand_parts(e) if p['material']=='M_Grey_Brick'][:8])
