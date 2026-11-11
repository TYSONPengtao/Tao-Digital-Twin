"""Read-only GLB gate hierarchy audit, augmenting the Rhino QA report."""
from pathlib import Path
import hashlib
import json
import math
import struct
import sys

W = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(W / 'np1'))
import numpy as np

O = Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
OUT = Path(__file__).parent
path = O / '05_Export/Reality_Hybrid_V11_LOCAL.glb'
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()
before = sha(path)
with path.open('rb') as f:
    magic, version, size = struct.unpack('<III', f.read(12))
    assert magic == 0x46546C67 and version == 2
    length, kind = struct.unpack('<II', f.read(8))
    assert kind == 0x4E4F534A
    G = json.loads(f.read(length))
R = json.loads((O / '02_Data/Interaction_Registry_V11.json').read_text(encoding='utf8'))
outer = R['V11_exterior_gate_additions']
nodes = G['nodes']
names = {n.get('name'): i for i, n in enumerate(nodes)}
parents = {child: i for i, n in enumerate(nodes) for child in n.get('children', [])}
checks = []

def ck(name, ok, detail=None):
    checks.append({'id': name, 'status': 'PASS' if bool(ok) else 'FAIL', 'detail': detail})

def matrix(n):
    if 'matrix' in n:
        return np.array(n['matrix']).reshape(4, 4).T
    x, y, z, w = n.get('rotation', [0, 0, 0, 1])
    q = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    m = np.eye(4)
    m[:3, :3] = q @ np.diag(n.get('scale', [1, 1, 1]))
    m[:3, 3] = n.get('translation', [0, 0, 0])
    return m

world_cache = {}
def world(i):
    if i not in world_cache:
        world_cache[i] = world(parents[i]) @ matrix(nodes[i]) if i in parents else matrix(nodes[i])
    return world_cache[i]

# Blender Z-up maps to glTF Y-up as x,z,-y.
basis = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], dtype=float)
rows = []
for d in outer:
    i = names[d['leaf_element']]
    node = nodes[i]
    parent_id = d.get('parent_door_id')
    parent_name = nodes[parents[i]].get('name') if i in parents else None
    expected_parent = next(x['leaf_element'] for x in outer if x['door_id'] == parent_id) if parent_id else None
    ck('glb_actual_parent_graph_' + d['door_id'], parent_name == expected_parent, {'actual_parent': parent_name, 'expected_parent': expected_parent})
    c, s = math.cos(d['angle']), math.sin(d['angle'])
    local = np.array([[c, -s, 0, d['hinge_world_m'][0]], [s, c, 0, d['hinge_world_m'][1]], [0, 0, 1, d['hinge_world_m'][2]], [0, 0, 0, 1]])
    expected = basis @ local @ basis.T
    actual = world(i)
    err = float(np.max(abs(actual - expected)))
    ck('glb_actual_hinge_world_matrix_' + d['door_id'], err < 2e-5, {'max_abs_error': err, 'actual_glTF_world_matrix': actual.tolist(), 'expected_glTF_world_matrix': expected.tolist()})
    extras = node.get('extras', {})
    ck('glb_parent_and_door_extras_' + d['door_id'], extras.get('door_id') == d['door_id'] and extras.get('role') == 'LEAF' and extras.get('parent_door_id') == str(parent_id))
    geometry_children = [nodes[j] for j in node.get('children', []) if nodes[j].get('name') == d['leaf_element'] + '_Geometry']
    ck('glb_actual_geometry_child_on_pivot_' + d['door_id'], len(geometry_children) == 1 and 'mesh' in geometry_children[0] and np.max(abs(matrix(geometry_children[0]) - np.eye(4))) < 1e-9)
    rows.append({'door_id': d['door_id'], 'node_index': i, 'actual_parent_name': parent_name, 'actual_glTF_world_matrix': actual.tolist(), 'world_matrix_max_abs_error': err})

after = sha(path)
ck('glb_stable_during_read_only_audit', before == after)
status = 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL'
report = {'status': status, 'path': str(path), 'sha256': after, 'checks': checks, 'actual_gate_nodes': rows, 'method': 'Read GLB JSON chunk; evaluate each actual node parent chain with TRS/quaternion transforms; compare actual world matrices after independent Blender-to-glTF coordinate conversion.'}
(OUT / 'GLB_QA.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
main_path = OUT / 'QA.json'
if main_path.exists():
    main = json.loads(main_path.read_text(encoding='utf8'))
    main['checks'] = [c for c in main['checks'] if not c['id'].startswith('glb_')] + checks
    main['glb_gate_hierarchy'] = {k: v for k, v in report.items() if k != 'checks'}
    main['input_sha256']['glb'] = after
    main['passed_checks'] = sum(c['status'] == 'PASS' for c in main['checks'])
    main['failed_checks'] = sum(c['status'] == 'FAIL' for c in main['checks'])
    main['status'] = 'PASS' if main['failed_checks'] == 0 else 'FAIL'
    main_path.write_text(json.dumps(main, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'status': status, 'checks': len(checks), 'actual_parent_links': [(r['door_id'], r['actual_parent_name']) for r in rows], 'maximum_matrix_error': max(r['world_matrix_max_abs_error'] for r in rows)}), flush=True)
if status != 'PASS':
    print(json.dumps([c for c in checks if c['status'] == 'FAIL']), flush=True)
    raise SystemExit(1)
