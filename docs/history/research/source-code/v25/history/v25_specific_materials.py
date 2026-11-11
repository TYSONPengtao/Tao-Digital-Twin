from pathlib import Path
import json,collections
W=Path(__file__).parent;b=json.loads((W/'v24_37/Before_Snapshot.json').read_text());p=json.loads((W/'v25/Blender_Probe.json').read_text())
for name in ['M_V24_20_Unified_Weathered_Gray_Clay','M_V24_18_Continuous_Rubble','M_V24_18_Continuous_Blue_Brick','M_V24_20_Continuous_AsBuilt_Perimeter','M_V24_31_Stair_Gray_Marble','M_V24_10_Original_AsBuilt_Ground_Photo']:
 print(name,json.dumps(b['materials'][name]['shader'],ensure_ascii=False),flush=True)
print('LARGEST',[(r['name'],r['triangles'],r['modifiers'])for r in sorted(p['rows'],key=lambda r:r['triangles'],reverse=True)[:12]])
print('COMPLEX_TOTAL',sum(r['triangles']for r in p['rows']if r['name']in p['complex_objects']))
