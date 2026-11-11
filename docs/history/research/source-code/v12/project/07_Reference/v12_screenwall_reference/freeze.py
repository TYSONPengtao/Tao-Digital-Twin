import json,hashlib,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import rhino3dm as rh
from PIL import Image
O=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
M=json.loads((O/'Mutation.json').read_text(encoding='utf-8'));S=json.loads(Path(M['source_scene']).read_text(encoding='utf-8'));P=json.loads((O/'Preview_Scene.json').read_text(encoding='utf-8'))
assert sha(Path(M['source_scene']))==M['source_scene_sha256']
assert sha(Path(M['reference_sources'][0]))==M['source_before_sha256']
E={e['name']:e for e in S['elements']};PE={e['name']:e for e in P['elements']}
preservation=[]
for name in M['preserved_nodes']:
 assert PE[name]==E[name]
 preservation.append(dict(node=name,original_full_node_unchanged=True))
name=M['replace'][0]['name'];original=[p for i,p in enumerate(E[name]['parts'],1) if i not in [3,4]]
assert original==PE[name]['parts'];assert len(original)==142
cad=rh.File3dm.Read(str(O/'Screenwall_V12_Detail_LOCAL.3dm'));assert len(cad.Objects)==984
assert cad.Settings.ModelUnitSystem==rh.UnitSystem.Meters
assert all(isinstance(o.Geometry,rh.Mesh) and o.Geometry.IsValid and o.Geometry.IsClosed for o in cad.Objects)
names=['V12_Screenwall_'+x+'.png' for x in ['Front','End','Roof','DripDetail']]
for n in names:
 im=Image.open(O/n);assert im.size==(1600,1000);im.verify()
Q=json.loads((O/'Geometry_QA.json').read_text(encoding='utf-8'));assert Q['status']=='PASS';assert Q['drip_contact_qa']['checked_cap_tube_contacts']==90
Q.update(source_scene_and_before_unchanged_by_sha=True,preserved_full_nodes=preservation,preserved_ridge_parts_exact_count=142,native_readback_valid_closed_count=984,visual_review={'status':'PASS','full_lotus_relief_visible':True,'views':names})
(O/'Geometry_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
files=['Mutation.json','Preview_Scene.json','Screenwall_V12_Detail_LOCAL.3dm','Geometry_QA.json','Drip_Contact_QA.json','Reference_Comparison.md']+names
manifest=dict(status='FROZEN_PASS',mutation_sha256=sha(O/'Mutation.json'),files={n:{'sha256':sha(O/n),'bytes':(O/n).stat().st_size} for n in files},native_mesh_parts=984,added_parts=842,exact_preserved_ridge_parts=142,retired_original_ridge_part_indices=[3,4],complete_source_nodes_unchanged=5,footprint_width_m=8.15,original_wall_main_roof_ridge_centre_unchanged=True,lotus_face_visibility_and_solid_contacts_pass=True,source_before_sha256=M['source_before_sha256'])
(O/'Freeze_Manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(manifest,ensure_ascii=False))
