"""Offline, read-only geometry audit; writes only this audit's JSON output.

Run with the workstation Python containing NumPy and Shapely. No bpy import.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union

W = Path(__file__).resolve().parent
D = W / 'v26_20'
J = json.loads((D / 'Input/Source_Index.json').read_text('utf8'))
I = {r['name']: r for r in J['objects']}
N = 'V26_2_Continuous_Ground_And_Perimeter_Shell'
r = I[N]
a = np.load(D / 'Input' / r['file'])
v, f, uv, mi = (a[k] for k in ['v', 'f', 'uv', 'mi'])
t = v[f]
cross = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
areas = np.linalg.norm(cross, axis=1) / 2
norm = cross / np.maximum((2 * areas)[:, None], 1e-30)

# This is the registered kitchen slab immediately before its V26.1 union.
# The fresh visible shell has the same plan, but some of the native slab's
# top triangles now carry gallery/road materials after the old unions.
old_dir = W / 'v26_1'
old_index = {r['name']: r for r in json.loads((old_dir / 'Geometry_Index.json').read_text('utf8'))}
old_row = old_index['SITE_KITCHEN_STONE_FLOOR_Geometry']
old = np.load(old_dir / old_row['file'])
ot = old['v'][old['f']]
on = np.cross(ot[:, 1] - ot[:, 0], ot[:, 2] - ot[:, 0])
kitchen = unary_union([Polygon(p[:, :2]) for p in ot[on[:, 2] > 1e-10]])
storage = Polygon(json.loads((W / 'v24_10/AsBuilt_Plan.json').read_text('utf8'))['outline'])
overlap = storage.intersection(kitchen)
raise_plan = storage.difference(kitchen)

def simple(poly):
    """Remove only collinear source vertices, without moving any boundary."""
    return poly.simplify(1e-12, preserve_topology=True)

def record_digest(ids):
    rows = []
    for j in ids:
        rows.append({'source_triangle': int(j), 'world_vertices': t[j].tolist(),
                     'material': r['materials'][int(mi[j])], 'uv': uv[j].tolist()})
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return digest, rows

top = (norm[:, 2] > .999) & (t[:, :, 2].min(1) > -.45) & (t[:, :, 2].max(1) < -.35)
top_ids = np.flatnonzero(top)
top_in = []
for j in top_ids:
    if Polygon(t[j, :, :2]).intersection(kitchen).area > 1e-12:
        top_in.append(int(j))

# All top triangles that reach the kitchen must remain exact records. They
# are not identified by material alone: ROAD_CONCRETE also owns small strips
# in the kitchen/storage footprint overlap.
top_hash, records = record_digest(top_in)
whole_face_protection = kitchen.union(unary_union([Polygon(t[j, :, :2]) for j in top_in]))
strict_raise_plan = storage.difference(whole_face_protection)
straddlers = []
for j in top_in:
    area_in_raise = Polygon(t[j, :, :2]).intersection(raise_plan).area
    if area_in_raise > 1e-10:
        straddlers.append({'source_triangle': j, 'area_outside_kitchen_inside_raise_plan_m2': area_in_raise,
                           'material': r['materials'][int(mi[j])]})
by_material = {}
for j in top_in:
    name = r['materials'][int(mi[j])]
    by_material.setdefault(name, []).append(j)
material_summary = []
for name, ids in by_material.items():
    footprint = unary_union([Polygon(t[j, :, :2]) for j in ids])
    material_summary.append({'material': name, 'triangles': len(ids),
                             'area_inside_registered_kitchen_m2': footprint.intersection(kitchen).area,
                             'ids': ids})

# Any current shell face touching the kitchen below the raised target can
# be compared geometrically after the boolean, even if triangulation at a
# non-kitchen interface changes. Existing walls live in separate objects.
affected_band = (t[:, :, 2].max(1) >= -.851) & (t[:, :, 2].min(1) <= -.249)
other_ids = []
for j in np.flatnonzero(affected_band):
    tri_plan = Polygon(t[j, :, :2])
    if tri_plan.area > 1e-14:
        touch = tri_plan.intersection(kitchen).area > 1e-12
    else:
        from shapely.geometry import LineString
        touch = LineString(t[j, :, :2]).intersection(kitchen).length > 1e-9
    if touch:
        other_ids.append(int(j))

concrete_ids = [j for j in top_in if r['materials'][int(mi[j])] == 'M_Concrete']
concrete_plan = unary_union([Polygon(t[j, :, :2]) for j in concrete_ids])
road_ids = [j for j in top_in if r['materials'][int(mi[j])] == 'M_V12_Road_Concrete']
road_plan = unary_union([Polygon(t[j, :, :2]) for j in road_ids])

out = {
    'source_model': J['model'], 'source_sha256': J['sha256'],
    'fresh_shell_mesh_hash': r['mesh_hash'], 'fresh_shell_triangles': len(f),
    'registered_kitchen_source': str(old_dir / old_row['file']),
    'registered_kitchen_area_m2': kitchen.area,
    'registered_kitchen_bounds_xy_m': list(kitchen.bounds),
    'registered_kitchen_exclusion_geometry': mapping(simple(kitchen)),
    'registered_storage_area_m2': storage.area,
    'kitchen_storage_overlap_area_m2': overlap.area,
    'exact_overlap_exclusion_geometry': mapping(simple(overlap)),
    'recommended_raise_plan_area_m2': raise_plan.area,
    'recommended_raise_plan_geometry': mapping(simple(raise_plan)),
    'whole_triangle_exactness_exclusion_geometry': mapping(simple(whole_face_protection)),
    'whole_triangle_exactness_raise_plan_geometry': mapping(simple(strict_raise_plan)),
    'whole_triangle_exactness_raise_plan_area_m2': strict_raise_plan.area,
    'source_kitchen_triangles_straddling_minimal_raise_boundary': straddlers,
    'fresh_kitchen_top_triangle_count': len(top_in),
    'fresh_kitchen_top_records_sha256': top_hash,
    'fresh_kitchen_top_records': records,
    'fresh_kitchen_top_materials': material_summary,
    'fresh_concrete_top_area_inside_kitchen_m2': concrete_plan.intersection(kitchen).area,
    'current_road_material_inside_kitchen_m2': road_plan.intersection(kitchen).area,
    'source_faces_touching_kitchen_band_ids': other_ids,
    'recommended_z_m': {'exterior': -.4000000059604645, 'raised_storage': -.2500000059604645,
                        'nominal_kitchen_top': -.4000244140625},
    'recommendations': [
        'Subtract registered kitchen exclusion geometry before any storage-floor raise.',
        'Material-only protection is incomplete: current kitchen includes ROAD_CONCRETE strips.',
        'For whole original triangle byte-exactness, use whole_triangle_exactness_raise_plan_geometry; minimal raise plan instead requires clipping nine straddling road triangles and barycentric regional UV invariance.',
        'Keep unchanged vertical foundation vertices and UVs fixed; extend the floor/top up 150 mm rather than translating the foundation.',
        'Continue new vertical foundation/riser UV in existing world-height or arc-length coordinates, without a new origin or uniform UV rescale.',
        'The narrow southwest gallery is part of the raised storage scope; old room/gallery y=-14.85 split is not the desired step location.',
    ],
}
P = D / 'Kitchen_Overlap_Audit.json'
P.write_text(json.dumps(out, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({k: out[k] for k in ['source_sha256', 'fresh_shell_mesh_hash',
    'kitchen_storage_overlap_area_m2', 'recommended_raise_plan_area_m2',
    'fresh_kitchen_top_triangle_count', 'current_road_material_inside_kitchen_m2']}, indent=2))
print('WROTE', P)
