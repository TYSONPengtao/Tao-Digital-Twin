"""Read staged roof patch back, check preservation and shared joint coordinates."""
import sys, json, hashlib, math
from pathlib import Path
from collections import Counter
W = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(W / x) for x in ['np1', 'geomlibs', 'libs']] + [str(W)]
import numpy as np
import manifold3d as md
from shapely.geometry import Polygon, box
import export_v5 as ex
from roof_parameters import *

O = Path(__file__).parent
baseline = Path(r'E:\jz\JIA\Rebuild_V8_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S = json.loads(baseline.read_text(encoding='utf-8'))
E = {e['name']: e for e in S['elements']}
M = json.loads((O / 'Mutation.json').read_text(encoding='utf-8'))
L = json.loads((W / 'v9_eave_layers' / 'Mutation.json').read_text(encoding='utf-8'))
qa = json.loads((O / 'Geometry_QA.json').read_text(encoding='utf-8'))
checks = []

def check(name, ok, **data):
    checks.append(dict(name=name, passed=bool(ok), **data))
    if not ok:
        raise ValueError((name, data))

def sig(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def manifold(g):
    v, fs, _, _ = ex.solid_data(g)
    tri = np.asarray([[f[0], f[k], f[k + 1]] for f in fs for k in range(1, len(f) - 1)], dtype=np.uint64)
    a = md.Manifold(md.Mesh64(np.asarray(v, dtype=np.float64), tri))
    assert a.status() == md.Error.NoError, a.status()
    return a

check('staged_geometry_QA_pass', qa['status'] == 'PASS', checks_count=qa['checks_count'])
roof_names = set(e['name'] for e in M['replace'] + M['add'])
layer_names = set(e['name'] for e in L['replace'] + L['add'])
check('no_duplicate_names_between_patches', not roof_names & layer_names, intersection=sorted(roof_names & layer_names))
check('no_retired_or_changed_gate_roof', len(M['remove']) == 0 and all('GATEHOUSE_ROOF' not in n for n in roof_names))
check('replacement_names_are_existing', all(e['name'] in E for e in M['replace']))
check('additions_names_are_new', all(e['name'] not in E for e in M['add']))
check('only_west_roof_and_west_tiles_replaced', sorted(e['name'] for e in M['replace']) == ['SITE_KITCHEN_CHINESE_TILE_ROOF', 'SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0'])

tile = next(e for e in M['replace'] if e['name'].endswith('TILE_ROWS_0'))
orig_tiles = E[tile['name']]['parts']
old_sigs = Counter(sig(p) for p in orig_tiles)
new_sigs = Counter(sig(p) for p in tile['parts'])
unchanged_tiles = sum((old_sigs & new_sigs).values())
check('ordinary_cover_tile_modules_preserved', unchanged_tiles == 669, exact_whole_part_count=unchanged_tiles, original_parts=len(orig_tiles), new_parts=len(tile['parts']), cut_closed_parts=10, removed_parts=18)

old_shell = manifold(E['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts'][0]['geometry'])
new_shell = manifold(next(e for e in M['replace'] if e['name'] == 'SITE_KITCHEN_CHINESE_TILE_ROOF')['parts'][0]['geometry'])
new_added = new_shell - old_shell
cut_solid = old_shell - new_shell
check('new_shell_only_removes_corner_not_raises_or_adds_surface', new_added.volume() < 1e-9, added_volume_m3=new_added.volume(), removed_volume_m3=cut_solid.volume())
foot = Polygon(KITCHEN_FOOTPRINT)
cut_plan = box(*KITCHEN_BOUNDS).difference(foot)
cut_verts = cut_solid.to_mesh64().vert_properties[:, :3]
retained_mask = md.CrossSection([np.asarray(KITCHEN_FOOTPRINT, dtype=np.float64)]).extrude(8).translate([0, 0, -2])
outside_corner_removed_volume = (cut_solid ^ retained_mask).volume()
check('no_removed_shell_volume_outside_joint_corner', abs(outside_corner_removed_volume) < 1e-9, footprint_area_m2=cut_plan.area, removed_outside_corner_volume_m3=outside_corner_removed_volume, expected_removed_volume_m3=cut_plan.area * .075, interpretation='Boolean remeshing can retain coincident zero-volume boundary faces; volumetric difference measures actual removed solid.')

le = {e['name']: e for e in L['replace'] + L['add']}
south_wall = le['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts'][0]
wv = np.asarray(ex.solid_data(south_wall['geometry'])[0])
check('south_wall_follows_joint_cutline_and_is_inset', all(q[1] >= kitchen_ymin(q[0]) + .18 - 1e-8 for q in wv), minimum_offset_m=float(min(q[1] - kitchen_ymin(q[0]) for q in wv)))
columns = le['SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS']['parts']
candidates = [p['geometry'] for p in columns if p['geometry']['type'] == 'cylinder']
check('south_timber_columns_behind_tile_cutline', all(g['origin'][1] >= kitchen_ymin(g['origin'][0]) + .17 for g in candidates), southernmost_column_y=min(g['origin'][1] for g in candidates))
check('gate_core_plan_and_roof_end_disjoint', foot.intersection(box(4.9, -11.95, 8.3, -11.45)).area < 1e-10)
check('truncated_corner_covered_by_gate_roof_plan', cut_plan.difference(box(*GATE_BOUNDS)).area < 1e-10, uncovered_area_m2=cut_plan.difference(box(*GATE_BOUNDS)).area)

result = dict(status='PASS', ready_to_merge=True, checks=checks,
              geometry_checks_count=qa['checks_count'],
              replace=[e['name'] for e in M['replace']], add=[e['name'] for e in M['add']], removed=M['remove'],
              mutation_sha256=hashlib.sha256((O / 'Mutation.json').read_bytes()).hexdigest(),
              baseline_scene_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
              kitchen_normal_roof_height_unchanged=True, gate_normal_roof_unchanged=True,
              lower_roof_under_upper_roof_plan_area_m2=foot.intersection(box(*GATE_BOUNDS)).area,
              cut_corner_area_m2=cut_plan.area,
              limitations=['Joint plan cutline and concealed cap section are inferred from images, not a field survey.',
                           'Hidden tile battens or structural capacity are not established by this roof patch.',
                           'Layer intersections must also pass the independent combined-patch audit before delivery.'])
(O / 'Final_Review_QA.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(dict(status=result['status'], ready_to_merge=True, staged_checks=len(checks), geometry_checks=qa['checks_count'], mutation_sha256=result['mutation_sha256']), ensure_ascii=False, indent=2))
