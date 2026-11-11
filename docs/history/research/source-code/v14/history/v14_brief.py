import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,export_v5 as ex
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V13\08_Editable_Source\Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S
for e in S['elements']:
 n=e['name']
 if n.startswith(('SITE_PERIMETER_JOINED','SITE_SOUTH_EAST_ANNEX','SITE_KITCHEN','STAIR_F2','STAIR_LANDING_F2','STAIR_V4_FLOOR_END_2','DOOR_LAUNDRY_F3','DOOR_STUDY_F3','DOOR_BATH_F3')) or n in ['PARTITIONS_JOINED_F3','SLAB_JOINED_F3']:
  parts=ex.expand_parts(e);vs=[ex.world_part(p,e)[0] for p in parts]
  v=np.concatenate(vs) if vs else np.zeros((0,3))
  print(n, 'bbox',np.round([v.min(0),v.max(0)],4).tolist() if len(v) else [],'parts',len(parts))
  if n.startswith(('DOOR_','STAIR_F2','STAIR_LANDING')):print(json.dumps(e,ensure_ascii=False)[:5000])
  if n in ['PARTITIONS_JOINED_F3']:print('wall planar z slices',[(g['geometry']['outer'],g['geometry']['z'],g['geometry']['height']) for g in parts if g['geometry']['z']>=9.6])
  if n.startswith(('SITE_PERIMETER_JOINED_RETAINING_WALL_','SITE_SOUTH_EAST_ANNEX')) and 'TILE' not in n:print('params',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));print('geotypes',[p['geometry']['type'] for p in parts])
