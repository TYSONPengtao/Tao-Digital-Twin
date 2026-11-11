import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v3 as ex
rows=[]
for e in ex.SCENE['elements']:
 if e['family']=='VIS_MODEL':continue
 vs=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e)
  if v is not None:vs.append(v)
 if vs:
  v=np.vstack(vs);row={'name':e['name'],'family':e['family'],'layer':e['layer'],'bbox_min':v.min(0).round(5).tolist(),'bbox_max':v.max(0).round(5).tolist(),'part_count':len(vs)};rows.append(row)
  print(e['name'],row['bbox_min'],row['bbox_max'],row['part_count'])
(W/'v4_audit_junction/bboxes.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
