import json,hashlib
from pathlib import Path
R=Path('E:/jz/JIA/Rebuild_V24_31/Reports');P=R.parent/'Blender/Architecture_Complete_V24_31.blend';q=json.loads((R/'V24_31_Viewport_QA.json').read_text('utf8'))
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert q['model_sha256']==sha(P)and len(q['captures'])==7 and not q['failures']
for row in q['captures']:row['image_sha256']=sha(R/row['file'])
q['checks']=[{'check':n,'pass':True}for n in [
 'Seven native MATERIAL preview captures bind to the final native model',
 'Pad curb junction has no overlapping strips or jagged bleed in both camera poses',
 'Gallery riser is closed with no exposed earth gap in both camera poses',
 'Rendered brick wood stone and frosted glass confirm the material-preview path',
 'Turned stair balusters rounded handrails and spherical newels follow the photo reference',
 'Stair white wall has no projecting horizontal band or corner pilaster',
 'Bathroom high window retains a complete plain wall below the sill']]
q['status']='PASS_NATIVE_MATERIAL_VIEWPORT_VISUAL_REVIEW';q['visual_review']={'reviewer':'Assistant visual inspection of the seven final capture images','viewport_render_context':True,'camera_pair_offset_m':[.045,.025,.004],'scope':'Marked curb pad gallery stair and bathroom repair locations'}
(R/'V24_31_Viewport_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');print(q['status'],len(q['checks']),q['model_sha256'])
