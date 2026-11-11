import sys,json,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['geomlibs','np1','libs']]
from wall_opening_patch import patch_door_opening
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));old=copy.deepcopy(next(e for e in s['elements'] if e['name']=='DOOR_BED_F1_X3.9'));target=copy.deepcopy(old);target['origin']=[3.9,5.3,0];target['video_evidence']='SYNTHETIC_TEST_ONLY_NOT_ACTUAL_TARGET';before=copy.deepcopy(s);r=patch_door_opening(s,'PARTITIONS_JOINED_F1',old,target)
changed=[a['name'] for a,b in zip(s['elements'],before['elements']) if a!=b];assert changed==['PARTITIONS_JOINED_F1'];assert abs(r['delta_wall_m3'])<1e-8
r['description']='In-memory synthetic move test only. No corrected scene file was written; target is not evidence-supported.';r['changed_elements']=changed;Path(__file__).with_name('Patch_Helper_Simulation_QA.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(r)
