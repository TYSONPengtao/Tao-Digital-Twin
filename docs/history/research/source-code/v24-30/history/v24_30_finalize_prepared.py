import json
from pathlib import Path
D=Path(__file__).parent/'v24_30';p=D/'Prepared_Geometry.json';out=json.loads(p.read_text('utf8'));n='CONSTRUCTION_RAINWATER_RECEIVER_NW_Geometry'
if not any(r['name']==n for r in out['offsets']):out['offsets'].append({'name':n,'offset':[0,0,-.192]})
out['proof']['outer_ground_fixtures']={'buried_below_white_pad':['CONSTRUCTION_RAINWATER_RECEIVER_WING_SW_Geometry',n],'offset_m':-.192,'maximum_top_after_m':-.6020341796875,'indoor_slabs_unchanged':True}
p.write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
