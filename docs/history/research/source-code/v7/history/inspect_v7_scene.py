import json
from pathlib import Path
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
for e in S['elements']:
 n=e['name']
 if e['layer']=='30_DOOR' or any(t in n for t in ['WALL_EXT','CANOPY','TERRACE','BALCONY','GZY','PARTITIONS_JOINED','WALLS_JOINED','SLAB_JOINED']):
  print(n,'origin',e.get('origin'),'angle',e.get('angle'),'definition',e.get('definition'),'layer',e['layer'])
  if e['parts']:
   for p in e['parts'][:3]:print(' ',str(p)[:1300])
print('Tile row sample')
e=next(e for e in S['elements'] if e['name']=='ROOF_MAIN_JOINED_TILE_ROWS_0');print(e['parts'][:2],len(e['parts']))
