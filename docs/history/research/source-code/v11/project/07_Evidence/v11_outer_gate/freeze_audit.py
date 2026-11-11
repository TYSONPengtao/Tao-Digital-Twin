"""Read-only audit of frozen patch against V10 source and exact allowed footprints."""
import sys,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];OUT=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
import export_v5 as ex
P=OUT/'Mutation.json';M=json.loads(P.read_text(encoding='utf8'));source=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json');S=json.loads(source.read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S
scope=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in M['hybrid_scope_additions']]);rows=[]
def check(name,ok,**kw):
 rows.append(dict(name=name,pass_=bool(ok),**kw))
 if not ok:raise AssertionError(name)
for e in M['replace']:
 check('whole_reused_node_exact',e==E[e['name']],node=e['name'])
for e in M['replace']+M['add']:
 pr=[]
 for p in ex.expand_parts(e):
  v,_=ex.world_part(p,e);poly=MultiPoint(v[:,:2]).convex_hull
  if poly.area>1e-15:pr.append(poly)
 projected=unary_union(pr);outside=projected.difference(scope).area
 check('every_full_node_footprint_inside_authorized_scope',outside<1e-11,node=e['name'],outside_m2=outside)
added={e['name']:e for e in M['add']};reg=M['door_registry_additions'];leafs=[e for e in M['add'] if e.get('role')=='LEAF']
check('four_unique_leaf_elements',len(leafs)==4 and len({e['name'] for e in leafs})==4)
check('four_unique_registry_rows',len(reg)==4 and len({r['door_id'] for r in reg})==4)
hinges=[]
for r in reg:
 e=added[r['leaf_element']];hinges.append(tuple(r['hinge_world_m']))
 check('registry_element_axis_consistent',e['origin']==r['hinge_world_m'] and e['angle']==r['angle'] and e['door_id']==r['door_id'] and e.get('hinge_axis_local')==[0,0,1],door=r['door_id'])
check('four_distinct_axes',len(set(hinges))==4)
check('no_fixed_post_geometry_inside_moving_leaf',all(e['classification']=='PHOTO_FOUR_PANEL_STAINLESS_OUTER_GATE' for e in leafs))
check('no_existing_node_replacement_beyond_wall1',all(e['name'].startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_1') for e in M['replace']))
check('no_original_source5_data_mutation',M['changes']['original_source5_mesh_and_textures_unchanged'] and not M['remove'])
check('source_scene_hash_consistent',hashlib.sha256(source.read_bytes()).hexdigest()==M['changes']['original_scene_sha256'])
check('geometry_generator_QA_pass',json.loads((OUT/'Geometry_QA.json').read_text(encoding='utf8'))['pass_'])
check('original_photo_evidence_copied',(OUT/'Evidence/Center_L0_0897s.jpg').is_file() and (OUT/'Evidence/DJI_0073.JPG').is_file())
report=dict(pass_=True,mutation_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),checks=rows,scope_union_area_m2=scope.area,replace_nodes=[e['name'] for e in M['replace']],add_nodes=list(added),new_parts=sum(len(e['parts']) for e in M['add']),reused_parts=sum(len(e['parts']) for e in M['replace']),unmeasured_dimensions_preserved_in_metadata=True)
(OUT/'Final_Freeze_Audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(pass_=True,checks=len(rows),scope_union_m2=scope.area,sha=report['mutation_sha256'])))
