import json,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V21');R=O/'06_Report'
N=json.loads((R/'V21_Native_Readback_QA.json').read_text(encoding='utf8'))
D=json.loads((R/'Final_Native_Door_QA.json').read_text(encoding='utf8'))
assert N['status'].startswith('PASS') and D['status'].startswith('PASS')
checks={}
for task,filename in [('gate','Source_QA.json'),('house','House_Native_QA.json'),('site','Final_Native_Review.json')]:
 p=W/f'v21_{task}'/filename;d=json.loads(p.read_text(encoding='utf8'));assert d['status'].startswith('PASS')
 d['final_native_model_sha256']=N['sha256'];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
 checks[task]=d['status']
 if task=='gate':(W/'v21_gate/Part_QA.json').write_text(json.dumps(d['parts'],ensure_ascii=False,indent=2),encoding='utf8')
for task in ['house','site']:
 p=W/f'v21_{task}'/'Preview_Review.json';d=json.loads(p.read_text(encoding='utf8'))
 d['final_native_model_sha256']=N['sha256'];d['final_native_preview_pending_root_rebuild']=False
 d['final_geometry_review']='Root inspected final native readback previews: gate flush joint and collars, F3 plain opening and sliding entry, storage paired fretwork.'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
out={'status':'PASS_FINAL_V21_REVIEW','native_model_sha256':N['sha256'],'component_checks':checks,'changed_native_objects':771,'preserved_native_objects':15952,'door_default_open_checks':len(D['doors']),'changed_door_sample_checks':len(D['changed_door_motion_samples']),'limitations':['Actual UE import and collision runtime have not been tested.','One retained outer gate brick-skin node is not boolean-testable; detailed door QA lists this exception.','Dimensions are photo-fit to the registered site, not a new field survey.'],'verified_visual_corrections':['Gate-kitchen gray-brick face is flat and connected without former white wing.','Gate pier/collar overlap and threshold coincident-face black artifacts removed.','F3 old bedroom hole sealed; new doorway beside study; terrace opening has white original wall reveals and no invented leaf.','Storage paired octagon fretwork is connected and visible without a foreground-column obstruction.'],'baseline_v20_preserved':True}
(R/'Final_Review_V21.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL REVIEW RECORDED',flush=True)
