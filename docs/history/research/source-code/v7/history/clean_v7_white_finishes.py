"""Remove unsupported photo contamination from new plain white finishes only."""
import json,sys
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));M['M_V7_White_Plain_Finish']={'color':[221,219,210],'roughness':.88,'source':'DJI 0002 0038/0429/0478/0623: plain white painted/rendered cement and pale stone; uniform appearance, not a fabricated photograph'}
changed=[]
for r in I:
 name=r['name']
 plain=name.startswith(('FACADE_CONTINUOUS_','FLOOR_FASCIA_CONTINUOUS_','GZY_','ROMAN_COLUMN_','KZ_','PORCH_ARCH_BEAM_')) or name in ['BALCONY_F2_PHOTO_OPEN_STONE_RAIL','TERRACE_STONE_PARAPET','TERRACE_PHOTO_PIERCED_CROWN','CANOPY_CENTER_RIDGE_CAP']
 if not plain:continue
 d=np.load(O/'02_Data'/r['file']);mid=np.zeros(len(d['faces']),np.int32)
 np.savez_compressed(O/'02_Data'/r['file'],vertices=d['vertices'],faces=d['faces'],uv=d['uv'],material_ids=mid)
 changed.append(dict(name=name,faces=len(mid),prior_photo_faces=r.get('photo_triangles',0)));r['materials']=['M_V7_White_Plain_Finish'];r['photo_triangles']=0;r['finish_revision']='Reference-supported plain white finish; rejected nearest-photo red-door/shadow contamination'
(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/Materials.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'06_Report/Plain_White_Finish_Revision.json').write_text(json.dumps(dict(nodes=changed,scope='Only rebuilt surfaces inside missing area; original source five meshes/materials untouched',material='Source-supported uniform white render/stone; no image editing',reason='Nearest measured scan photo projected red panels/shadows onto differently placed clean structural surfaces'),ensure_ascii=False,indent=2),encoding='utf-8');print('Plain finish corrected',len(changed),'nodes',flush=True)
