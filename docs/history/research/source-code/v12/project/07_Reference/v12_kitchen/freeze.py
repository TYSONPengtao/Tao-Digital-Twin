"""Run only after manually reviewing the final geometry's seven previews."""
import json,hashlib,datetime
from pathlib import Path
O=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
M=json.loads((O/'Mutation.json').read_bytes());Q=json.loads((O/'Geometry_QA.json').read_bytes())
assert Q['status']=='PASS' and (Q['added_nodes'],Q['closed_parts'],Q['old_nodes_retired'])==(33,629,22)
assert len(Q['checks'])==Q['checks_count']==6441 and all(x['passed'] for x in Q['checks'])
assert not Q['new_structure_disconnected']
S=Path(r'E:/jz/JIA/Rebuild_V11_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json');E={e['name']:e for e in json.loads(S.read_bytes())['elements']}
assert sha(S)==M['source_scene_sha256']
assert all(hashlib.sha256(json.dumps(E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest()==h for n,h in M['protected_node_sha256'].items())
native=['Changed_Kitchen_V12_LOCAL.3dm','Kitchen_Complete_V12_LOCAL.3dm','Kitchen_Complete_V12_ALIGNED_ENU.3dm']
images=['Kitchen_V12_Complete.png','Kitchen_V12_Exposed_Timber.png','Kitchen_V12_Double_Octagon_Window_Detail.png','Kitchen_V12_Door_Pair_Detail.png','Kitchen_V12_Two_Fret_Levels_Detail.png','Kitchen_V12_Interior_Facade_Relation.png','Kitchen_V12_Interior_Complete.png']
assert all((O/n).stat().st_mtime>=(O/'Mutation.json').stat().st_mtime for n in images)
files=['Mutation.json','Geometry_QA.json','Contact_Graph.json','Near_Photo_Comparison.md',*native,*images,'build_kitchen.py','extract_before.py','render.py','preview_data.py','Before_Donor.json']
refs=[Path(f'D:/Desktop/问题/屏幕截图 2026-10-11 {s}.jpg') for s in ['115520','115537','191926','191942']]
R=dict(status='PASS_FROZEN',created_local=datetime.datetime.now().isoformat(timespec='seconds'),added_nodes=33,closed_parts=629,retired_nodes=22,geometry_qa_checks=6441,solid_contact_edges=Q['contact_edges'],protected_v11_node_hashes_verified=True,source_v11_scene_sha256=sha(S),files={n:dict(absolute_path=str((O/n).resolve()),bytes=(O/n).stat().st_size,sha256=sha(O/n)) for n in files},actual_near_photos={str(p):sha(p) for p in refs},manual_visual_review=dict(octagon_and_return_coplanar_black_spots_removed=True,door_pair_moulding_rises_toward_middle=True,outer_columns_on_explicit_stone_bases=True,wide_upper_band_separate_from_narrow_transoms=True,no_complex_triangulated_reference_truss=True,diagnostic_fret_images_hide_roof_members_only_in_render=True,complete_interior_keeps_roof_members_and_photo_confirmed_services=True,images_reviewed=images),outer_column_direct_support=Q['outer_column_direct_support'],fan_blade_timber_clearance=Q['photo_confirmed_services']['fan_blade_timber_clearance'],door_interaction=Q['door_interaction'],dimensions_status='Reference fit to existing registered model and uncalibrated real photographs; not a field measurement or structural construction certification')
(O/'Final_Freeze_QA.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({n:R['files'][n]['sha256'] for n in ['Mutation.json',*native]},ensure_ascii=False,indent=2))
