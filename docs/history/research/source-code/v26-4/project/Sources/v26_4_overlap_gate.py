from pathlib import Path
import json,hashlib
W=Path(__file__).parent;D=W/'v26_4';O=Path('E:/jz/JIA/Rebuild_V26_4');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_4.blend'
data=json.loads((D/'Overlap_Audit_After.json').read_text('utf8'));pairs=data['same_facing_coplanar_overlap_candidates'];hn='V26_3_House_Connected_Walls_And_Stairs'
keys=[f'{hn} | {hn}',f'CANOPY_CENTER_0_Geometry | {hn}','CANOPY_CENTER_0_Geometry | CANOPY_CENTER_0_Geometry']
keys += [f'BAY_WINDOW_F{f}_{side}_1_Geometry | {hn}'for f,side in [(1,'L'),(1,'R'),(2,'L'),(2,'R'),(3,'R')]]
keys += [f'DOOR_FRONT_CENTER_F{f}__FIXED_Geometry | DOOR_FRONT_CENTER_F{f}__FIXED_Geometry'for f in [1,2]]
checks=[]
for k in keys:
 area=pairs.get(k,{}).get('projected_area_m2',0.);checks.append({'check':'No competing coplanar surface: '+k,'pass':area<.00001,'area_m2':area})
with P.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
native=json.loads((R/'V26_4_Native_Readback_QA.json').read_text('utf8'));assert native['model_sha256']==h
fail=[q for q in checks if not q['pass']];(R/'V26_4_Scoped_Overlap_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'method':'Independent same-facing coplanar triangle intersection on freshly exported saved geometry, 0.12 mm plane and 0.00001 m2 area tolerances','retained_original_detail_candidates':'Unmodified tile laps, decorative junctions and embedded structural contacts elsewhere are not asserted to be absent.'},ensure_ascii=False,indent=2),encoding='utf8');print('SCOPED_OVERLAP_GATE',len(checks),'FAIL',len(fail),flush=True)
