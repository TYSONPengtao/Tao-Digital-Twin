import json,sys
from pathlib import Path
W=Path(__file__).parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V19')
I=json.loads((B/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'))
rows=[]
for r in I:
 n=r['name']
 if n.startswith(('DOOR','PARTITIONS','STAIR','SLAB','PORCH','TERRACE','BALCONY','SITE_MAIN','WALL','FACADE','EXT_WALL')) or any(q in n for q in ['ENTRY_STEP','HOUSE_STEPS','MAIN_BUILDING','ENTRANCE_STEP']):
  b=r.get('actual_3dm_mesh_bbox_local')
  if b is None:
   v=np.load(B/'02_Data'/r['file'])['vertices'];b=[v.min(0),v.max(0)]
  row={'name':n,'bounds':np.round(b,4).tolist(),'materials':r['materials'],'triangles':r['triangles'],'element':r['element']};rows.append(row)
  print(n,'BOUNDS',row['bounds'],'MAT',r['materials'])
  if n.startswith(('DOOR','PARTITIONS','STAIR','SLAB','PORCH')):print(json.dumps(r['element'],ensure_ascii=False)[:7500])
(Path(__file__).parent/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('ALLNAMES', [r['name'] for r in I if 'STEP' in r['name'] or 'PORCH' in r['name'] or 'STAIR' in r['name']])
