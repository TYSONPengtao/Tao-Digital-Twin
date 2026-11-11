"""Independent, read-only V11 delivery audit. Writes only beside this script."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import math
import struct
import sys

W = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(W / 'np1'), str(W / 'libs')]
import numpy as np
import rhino3dm as rh

O = Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
OUT = Path(__file__).parent
checks = []

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def ck(name, ok, detail=None):
    checks.append({'id': name, 'status': 'PASS' if bool(ok) else 'FAIL', 'detail': detail})

def matrix(angle, origin):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0, origin[0]], [s, c, 0, origin[1]],
                     [0, 0, 1, origin[2]], [0, 0, 0, 1]], dtype=float)

def rh_matrix(m):
    t = rh.Transform.Identity()
    for i in range(4):
        for j in range(4):
            setattr(t, f'M{i}{j}', float(m[i, j]))
    return t

def as_matrix(t):
    return np.array([[getattr(t, f'M{i}{j}') for j in range(4)] for i in range(4)])

def point(p):
    return [p.X, p.Y, p.Z]

def bbox(g):
    # openNURBS rhino3dm includes the unused fourth surface control corner
    # of some planar, triangular trimmed Brep faces in both bbox methods.
    # A planar trimmed face has extrema on its actual boundary edges.
    brep = g.ToBrep(True) if isinstance(g, rh.Extrusion) else g
    if isinstance(brep, rh.Brep) and all(f.IsPlanar() for f in brep.Faces):
        boxes = [e.GetTightBoundingBox() for e in brep.Edges]
        assert boxes
        return (np.min(np.array([point(b.Min) for b in boxes]), axis=0),
                np.max(np.array([point(b.Max) for b in boxes]), axis=0))
    b = g.GetBoundingBox()
    return np.array(point(b.Min)), np.array(point(b.Max))

def copy_at(g, t):
    duplicate = g.Duplicate()
    assert duplicate is not None and duplicate.Transform(t)
    return duplicate

def is_closed(g):
    if isinstance(g, rh.Mesh):
        return g.IsClosed
    if isinstance(g, (rh.Brep, rh.Extrusion)):
        return g.IsSolid
    return False

def solid_vertices(g):
    """Independent extraction for the three source types used by gate leaves."""
    typ = g['type']
    if typ == 'prism':
        p = np.array(g['profile'], dtype=float)
        return np.vstack([p, p + np.array(g['vector'])])
    if typ == 'polyhedron':
        return np.array(g['vertices'], dtype=float)
    if typ == 'cylinder':
        n = g['segments']
        t = np.arange(n) * (2 * math.pi / n)
        p = np.column_stack([g['radius'] * np.cos(t), g['radius'] * np.sin(t), np.zeros(n)])
        p += np.array(g['origin'])
        return np.vstack([p, p + [0, 0, g['height']]])
    raise ValueError(f'Unexpected gate source geometry type {typ}')

def max_match_error(actual, expected):
    return max(float(np.linalg.norm(actual - p, axis=1).min()) for p in expected)

def mesh_vertices(mesh):
    # Iteration exposes Point3f even for a double-precision mesh.
    return np.array([point(mesh.Vertices.Point3dAt(i)) for i in range(len(mesh.Vertices))], dtype=float)

paths = {
    'scene': O / '08_Editable_Source/05_Intermediate/Architecture_Scene.json',
    'coordinate': O / '02_Data/Coordinate.json',
    'registry': O / '02_Data/Interaction_Registry_V11.json',
    'editable': O / '04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm',
    'hybrid': O / '04_Rhino/Reality_Hybrid_V11.3dm',
}
architecture_only = '--architecture-only' in sys.argv
if architecture_only:
    paths.pop('hybrid')
hashes_before = {k: sha(p) for k, p in paths.items()}
C = read(paths['coordinate'])
T = matrix(math.radians(C['rotation_deg']), C['origin'])
ck('coordinate_full_matrix_consistent', np.max(np.abs(T - C['local_to_survey'])) < 1e-12)
Ti = rh_matrix(np.linalg.inv(T))
S = read(paths['scene'])
E = {e['name']: e for e in S['elements']}
R = read(paths['registry'])
outer = R['V11_exterior_gate_additions']
ck('registry_scene_sha256', R['source_scene_sha256'] == hashes_before['scene'])
ck('four_unique_registry_and_leaf_records', len(outer) == 4 and len({d['door_id'] for d in outer}) == 4 and len({d['leaf_element'] for d in outer}) == 4)
ck('registry_full_coordinate_matrix', np.max(np.abs(np.array(R['local_to_survey']) - T)) < 1e-12)
registry_by_id = {d['door_id']: d for d in outer}
scene_registry_by_id = {d['door_id']: d for d in S['door_registry']}
main_registry_by_id = {d['door_id']: d for d in R['door_registry']}
ck('four_gate_records_exact_in_scene_and_main_registry', all(d == scene_registry_by_id.get(d['door_id']) == main_registry_by_id.get(d['door_id']) for d in outer))

# Derive pavilion limits from duplicated file geometry, never from Scene bbox.
F = rh.File3dm.Read(str(paths['editable']))
ck('editable_file_read_and_metres', F is not None and F.Settings.ModelUnitSystem == rh.UnitSystem.Meters)
pavilion = []
editable_doors = {d['door_id']: [] for d in outer}
node_boxes = {}
groups = {g.Index: g.Name for g in F.Groups}
for ob in F.Objects:
    at = ob.Attributes
    node = at.GetUserString('V11_Element') or ''
    if node.startswith('SITE_GAZEBO') or at.Name.startswith('SITE_GAZEBO'):
        local = copy_at(ob.Geometry, Ti)
        lo, hi = bbox(local)
        row = {'name': at.Name, 'element': node, 'part_index': at.GetUserString('V11_Part_Index'),
               'type': type(ob.Geometry).__name__, 'valid': bool(ob.Geometry.IsValid),
               'closed': bool(is_closed(ob.Geometry)), 'min': lo.tolist(), 'max': hi.tolist()}
        pavilion.append(row)
        if node not in node_boxes:
            node_boxes[node] = [lo.copy(), hi.copy(), 0, []]
        b = node_boxes[node]
        b[0] = np.minimum(b[0], lo)
        b[1] = np.maximum(b[1], hi)
        b[2] += 1
        b[3].append(int(row['part_index']) if row['part_index'] is not None else -1)
    did = at.GetUserString('door_id')
    if did in editable_doors and not at.IsInstanceDefinitionObject:
        editable_doors[did].append(ob)

lo = np.min(np.array([r['min'] for r in pavilion]), axis=0)
hi = np.max(np.array([r['max'] for r in pavilion]), axis=0)
expected_nodes = {n: e for n, e in E.items() if n.startswith('SITE_GAZEBO')}
ck('actual_pavilion_908_independent_closed_valid_solids', len(pavilion) == 908 and all(r['valid'] and r['closed'] for r in pavilion), {'actual_count': len(pavilion), 'expected_count': 908, 'invalid_or_open': [r['name'] for r in pavilion if not r['valid'] or not r['closed']]})
ck('actual_pavilion_inside_west_and_south_boundaries', lo[0] > .22 and lo[1] > -11.48, {'actual_local_min_m': lo.tolist(), 'actual_local_max_m': hi.tolist(), 'west_boundary_x_m': .22, 'south_boundary_y_m': -11.48, 'west_clearance_m': float(lo[0] - .22), 'south_clearance_m': float(lo[1] + 11.48)})
ck('all_pavilion_elements_part_indices_exact', set(node_boxes) == set(expected_nodes) and all(b[2] == len(expected_nodes[n]['parts']) and sorted(b[3]) == list(range(len(expected_nodes[n]['parts']))) for n, b in node_boxes.items()), {n: b[2] for n, b in node_boxes.items()})
pavilion_nodes = [{'element': n, 'count': b[2], 'actual_local_min_m': b[0].tolist(), 'actual_local_max_m': b[1].tolist()} for n, b in node_boxes.items()]

# Independent registration, group membership and the actual native knuckle centers.
editable_rows = []
for d in outer:
    e = E[d['leaf_element']]
    origin = np.array(e['origin'])
    hinge = np.array(d['hinge_world_m'])
    expected_world = T @ matrix(e['angle'], origin)
    ck('registry_scene_consistent_' + d['door_id'], e['role'] == 'LEAF' and e['door_id'] == d['door_id'] and np.max(np.abs(origin - hinge)) < 1e-12 and np.max(np.abs(origin - np.array(d['origin']))) < 1e-12 and np.max(np.abs(origin - np.array(e['hinge_world_m']))) < 1e-12 and e['hinge_local_m'] == [0, 0, 0] and abs(e['angle'] - d['angle']) < 1e-12 and e.get('parent_door_id') == d.get('parent_door_id') and e['hinge_axis_local'] == d['hinge_axis_local'] == [0, 0, 1])
    obs = editable_doors[d['door_id']]
    part_ids = sorted(int(ob.Attributes.GetUserString('V11_Part_Index')) for ob in obs)
    common_groups = set.intersection(*(set(ob.Attributes.GetGroupList()) for ob in obs)) if obs else set()
    ck('editable_actual_group_and_exact_parts_' + d['door_id'], len(obs) == len(e['parts']) and part_ids == list(range(len(e['parts']))) and any(groups[g] == e['name'] for g in common_groups), {'actual_parts': len(obs), 'expected_parts': len(e['parts']), 'common_groups': [groups[g] for g in common_groups]})
    ck('editable_hinge_and_parent_attributes_' + d['door_id'], all(np.max(np.abs(np.array(json.loads(ob.Attributes.GetUserString('Hinge_ENU_m'))) - expected_world[:3, 3])) < 1e-9 and ob.Attributes.GetUserString('parent_door_id') == str(d.get('parent_door_id')) for ob in obs))
    back_to_leaf = rh_matrix(np.linalg.inv(expected_world))
    actual_by_index = {int(ob.Attributes.GetUserString('V11_Part_Index')): ob for ob in obs}
    knuckles = []
    for j, p in enumerate(e['parts']):
        g = p['geometry']
        if g['type'] != 'cylinder':
            continue
        ob = actual_by_index[j]
        native = copy_at(ob.Geometry, back_to_leaf)
        blo, bhi = bbox(native)
        expected_lo = np.array(g['origin']) + [-g['radius'], -g['radius'], 0]
        expected_hi = np.array(g['origin']) + [g['radius'], g['radius'], g['height']]
        err = float(max(np.max(abs(blo - expected_lo)), np.max(abs(bhi - expected_hi))))
        knuckles.append({'part_index': j, 'axis_xy_m': ((blo + bhi)[:2] / 2).tolist(), 'bbox_error_m': err})
    ck('editable_actual_hinge_knuckles_on_pivot_' + d['door_id'], len(knuckles) == 3 and all(k['bbox_error_m'] < 1e-8 and max(abs(x) for x in k['axis_xy_m']) < 1e-8 for k in knuckles), knuckles)
    editable_rows.append({'door_id': d['door_id'], 'parts': len(obs), 'actual_knuckles': knuckles})
del F

if architecture_only:
    report = {'status': 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL',
              'scope': 'Architecture actual geometry and actual editable gate hinges',
              'input_sha256': hashes_before,
              'pavilion': {'actual_closed_parts': len(pavilion), 'actual_local_min_m': lo.tolist(), 'actual_local_max_m': hi.tolist(), 'west_wall_cap_clearance_m': float(lo[0] - .22), 'south_boundary_clearance_m': float(lo[1] + 11.48), 'nodes': pavilion_nodes},
              'editable_gate_leaves': editable_rows, 'checks': checks,
              'passed_checks': sum(c['status'] == 'PASS' for c in checks),
              'failed_checks': sum(c['status'] == 'FAIL' for c in checks)}
    (OUT / 'Architecture_QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['checks', 'editable_gate_leaves', 'pavilion', 'input_sha256']}), flush=True)
    print(json.dumps(report['pavilion'], ensure_ascii=False), flush=True)
    if report['failed_checks']:
        print(json.dumps([c for c in checks if c['status'] == 'FAIL'], ensure_ascii=False), flush=True)
        raise SystemExit(1)
    raise SystemExit(0)

H = rh.File3dm.Read(str(paths['hybrid']))
ck('hybrid_file_read_and_metres', H is not None and H.Settings.ModelUnitSystem == rh.UnitSystem.Meters)
objects = {str(ob.Attributes.Id): ob for ob in H.Objects}
top = [ob for ob in H.Objects if not ob.Attributes.IsInstanceDefinitionObject]
defs = {str(d.Id): d for d in H.InstanceDefinitions}
gate_rows = []
definition_ids = []
actual_pivots = []
for d in outer:
    e = E[d['leaf_element']]
    matches = [ob for ob in top if ob.Attributes.Name == e['name']]
    ck('one_actual_leaf_instance_' + d['door_id'], len(matches) == 1 and isinstance(matches[0].Geometry, rh.InstanceReference))
    ob = matches[0]
    actual = as_matrix(ob.Geometry.Xform)
    expected_local = matrix(e['angle'], e['origin'])
    expected_enu = T @ expected_local
    error = float(np.max(np.abs(actual - expected_enu)))
    ck('actual_complete_4x4_instance_matrix_' + d['door_id'], error < 1e-9, {'max_abs_error': error, 'actual_matrix': actual.tolist(), 'expected_matrix': expected_enu.tolist()})
    ck('instance_rigid_unit_scale_' + d['door_id'], abs(np.linalg.det(actual[:3, :3]) - 1) < 1e-12 and np.max(np.abs(actual[:3, :3].T @ actual[:3, :3] - np.eye(3))) < 1e-12 and np.max(abs(actual[3] - [0, 0, 0, 1])) < 1e-12)
    ck('actual_block_parent_and_role_' + d['door_id'], ob.Attributes.GetUserString('door_id') == d['door_id'] and ob.Attributes.GetUserString('role') == 'LEAF' and ob.Attributes.GetUserString('parent_door_id') == str(d.get('parent_door_id')))
    def_id = str(ob.Geometry.ParentIdefId)
    definition_ids.append(def_id)
    ids = defs[def_id].GetObjectIds()
    defobs = [objects[str(i)] for i in ids]
    ck('actual_block_definition_contents_' + d['door_id'], len(defobs) > 0 and all(isinstance(x.Geometry, rh.Mesh) and x.Geometry.IsValid for x in defobs))
    av = np.vstack([mesh_vertices(x.Geometry) for x in defobs])
    ev = np.vstack([solid_vertices(p['geometry']) for p in e['parts']])
    bbox_error = float(max(np.max(abs(av.min(axis=0) - ev.min(axis=0))), np.max(abs(av.max(axis=0) - ev.max(axis=0)))))
    vertex_error = max_match_error(av, ev)
    ck('actual_block_geometry_relative_to_independent_pivot_' + d['door_id'], bbox_error < 1e-9 and vertex_error < 1e-9, {'bbox_error_m': bbox_error, 'all_expected_vertex_max_match_error_m': vertex_error, 'actual_definition_vertices': len(av), 'expected_source_vertices': len(ev)})
    knuckle_errors = []
    for p in e['parts']:
        if p['geometry']['type'] == 'cylinder':
            knuckle_errors.append(max_match_error(av, solid_vertices(p['geometry'])))
    ck('actual_block_knuckles_on_vertical_origin_axis_' + d['door_id'], len(knuckle_errors) == 3 and max(knuckle_errors) < 1e-9, knuckle_errors)
    pivot_local = (np.linalg.inv(T) @ actual)[:3, 3]
    actual_pivots.append(pivot_local)
    gate_rows.append({'door_id': d['door_id'], 'leaf_element': e['name'], 'parent_door_id': d.get('parent_door_id'), 'definition_id': def_id, 'actual_pivot_local_m': pivot_local.tolist(), 'actual_pivot_enu_m': actual[:3, 3].tolist(), 'actual_matrix': actual.tolist(), 'matrix_max_abs_error': error, 'definition_vertex_max_match_error_m': vertex_error})
ck('four_actual_independent_definitions_and_pivots', len(set(definition_ids)) == 4 and min(np.linalg.norm(a - b) for i, a in enumerate(actual_pivots) for b in actual_pivots[i + 1:]) > 1)

# The child axes must sit beyond the parent panel's actual far edge, with
# the frozen nominal 18 mm folding seam; the vertical offsets follow terrain.
parents_expected = {'SITE_SW_OUTER_GATE_PANEL_1': None, 'SITE_SW_OUTER_GATE_PANEL_2': 'SITE_SW_OUTER_GATE_PANEL_1', 'SITE_SW_OUTER_GATE_PANEL_3': 'SITE_SW_OUTER_GATE_PANEL_4', 'SITE_SW_OUTER_GATE_PANEL_4': None}
ck('registry_actual_parent_mapping', {d['door_id']: d.get('parent_door_id') for d in outer} == parents_expected)
seams = []
actual_matrices = {r['door_id']: np.array(r['actual_matrix']) for r in gate_rows}
for did, parent in parents_expected.items():
    if parent is None:
        continue
    pe = E[registry_by_id[parent]['leaf_element']]
    relative = np.linalg.inv(actual_matrices[parent]) @ actual_matrices[did]
    seam_gap = float(relative[0, 3] - pe['panel_width_m'])
    ck('parent_child_actual_hinge_seam_' + did, abs(seam_gap - .018) < 1e-9 and abs(relative[1, 3]) < 1e-9 and np.max(np.abs(relative[:3, :3] - np.eye(3))) < 1e-9, {'parent_door_id': parent, 'actual_parent_frame_child_pivot_m': relative[:3, 3].tolist(), 'actual_fold_seam_gap_m': seam_gap})
    seams.append({'door_id': did, 'parent_door_id': parent, 'actual_fold_seam_gap_m': seam_gap, 'parent_relative_matrix': relative.tolist()})
del H

hashes_after = {k: sha(p) for k, p in paths.items()}
ck('source_files_stable_during_read_only_audit', hashes_before == hashes_after)
report = {
    'status': 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL',
    'reviewed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'independent': True,
    'method': 'Only input JSON and 3dm reads. All actual geometry is duplicated before inverse ENU transforms. Planar trimmed Brep bounds are the union of actual boundary-edge tight boxes, avoiding unused fourth control corners of triangular face support surfaces; curved-solid and mesh bounds use the geometry bbox. Coordinate and hinge matrices independently constructed from scalar rotation/origin. No exporter transformation or final-site-QA helper imported.',
    'input_sha256': hashes_after,
    'script_review': {
        'final_v11_site_qa.py': 'Pavilion bbox there is Scene-based, actual 3dm checks closure/count; hinge check is translation plus M00/M10. This report independently checks actual inverse-transformed geometry bounds and all 16 matrix entries.',
        'export_v11_native.py': 'Meshes are inverse transformed into true leaf coordinates; independent ENU InstanceReference rotation/translation applied. Parent IDs copied as block attributes.',
        'merge_v11_cad.py': 'Full source geometry receives rigid LOCAL-to-ENU transform; editable hinge position encoded in ENU and leaf groups retained.',
        'blender_v11_hybrid.py': 'Actual leaf EMPTY pivots use origin/angle, geometry is inverse transformed; folding EMPTY children are parented while preserving world transforms. Runtime folding motion and operating sweep are not field verified.'
    },
    'pavilion': {'actual_closed_parts': len(pavilion), 'actual_local_min_m': lo.tolist(), 'actual_local_max_m': hi.tolist(), 'west_wall_cap_clearance_m': float(lo[0] - .22), 'south_boundary_clearance_m': float(lo[1] + 11.48), 'nodes': pavilion_nodes},
    'editable_gate_leaves': editable_rows,
    'hybrid_gate_leaves': gate_rows,
    'parent_child_actual_seams': seams,
    'limits': ['Folding parent relations are modeled provisional links, not a field-confirmed mechanism. Actual door sweep, animation and UE5 interaction are outside this audit.'],
    'checks': checks,
    'passed_checks': sum(c['status'] == 'PASS' for c in checks),
    'failed_checks': sum(c['status'] == 'FAIL' for c in checks)
}
(OUT / 'QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'status': report['status'], 'passed_checks': report['passed_checks'], 'failed_checks': report['failed_checks'], 'pavilion_parts': len(pavilion), 'actual_local_min_m': lo.tolist(), 'actual_local_max_m': hi.tolist(), 'gate_instances': len(gate_rows), 'report': str(OUT / 'QA.json')}), flush=True)
if report['failed_checks']:
    print(json.dumps([c for c in checks if c['status'] == 'FAIL'], ensure_ascii=False), flush=True)
    raise SystemExit(1)
