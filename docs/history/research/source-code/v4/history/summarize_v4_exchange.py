import json
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V4');j=json.loads((O/'09_Report/Exchange_Readback_QA.json').read_text(encoding='utf-8'))
for m,ds in j.items():
 for fmt,r in ds.items():print(m,fmt,{k:r.get(k) for k in ['import_success','invalid_coordinates','degenerate_faces','uv_missing_objects','material_slot_missing_objects','known_door_width_m','complete_site_present','photo_corrected_site_present','obsolete_false_gate_absent']})
print('clean', (O/'09_Report/Exchange_Surface_Cleanup.json').read_text(encoding='utf-8'))
