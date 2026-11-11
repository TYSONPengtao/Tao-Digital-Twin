import json,hashlib
from pathlib import Path
D=Path(__file__).parent
B=Path('E:/jz/JIA/Rebuild_V21')
cam=['V21_Storage_Front_Fretwork',[14.65,-16.65,1.0],[14.65,-14.855,1.10],84]
for name in ['Mutation.json','Design_Control.json']:
 p=D/name;q=json.loads(p.read_text(encoding='utf8'))
 q['cameras']=[cam if c[0]==cam[0] else c for c in q['cameras']]
 p.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
p=D/'design.py';s=p.read_text(encoding='utf8');s=s.replace("['V21_Storage_Front_Fretwork',[16.0,-16.35,.93],[16.15,-14.855,1.13],67]", "['V21_Storage_Front_Fretwork',[14.65,-16.65,1.00],[14.65,-14.855,1.10],84]");p.write_text(s,encoding='utf8')
native=B/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm'
report={'status':'PASS_SITE_GEOMETRY_AND_REVISED_CAMERA_TEST','native_sha256_reviewed':hashlib.sha256(native.read_bytes()).hexdigest(),'native_qa':'Final_Native_Review.json','native_checks_passed':132,'reviewed_images':[
 {'file':str(B/'06_Report/V21_Kitchen_Gallery_Paving.png'),'finding':'Gray-brown slab joints visible, original floor level and raised column feet continuous. View reveals the existing hall slider and inward kitchen opening. No visible new floor cracks.'},
 {'file':str(B/'06_Report/V21_Storage_Gallery_Detail.png'),'finding':'Matte cement walkway is continuous. End portal, column base, rail and roof remain in place. Stacked octagon windows and transom visible.'},
 {'file':str(D/'Front_Fretwork_Final_Camera.png'),'finding':'Camera moved clear of foreground column, showing both paired windows and connected head transom without hiding geometry.'}],
 'comparison_references':['Reference/INSV_1036s_L0_Y+00_P-10.jpg','Reference/INSV_0710s_L0_Y+00_P+00.jpg','Reference/INSV_0715s_L0_Y-25_P+05.jpg'],
 'camera_patch':cam,'required_final_step':'Root must use revised camera in final saved assembly and final readback preview. Gate refinement was still in progress during this independent review.',
 'geometry_changes_by_reviewer':False,
 'limitations':['No Unreal Engine runtime import test.','Photo-fitted motif proportions and surface colors are approximations, not surveyed reproduction.']}
(D/'Preview_Review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('CAMERA_PATCH_READY',cam)
