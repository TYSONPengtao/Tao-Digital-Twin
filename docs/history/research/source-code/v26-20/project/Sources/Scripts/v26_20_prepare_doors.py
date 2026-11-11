"""Prepare bounded storage-leaf bottom cuts; native rigs and model stay untouched."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
import hashlib

D = W / 'v26_20'
P = D / 'Prepared'
P.mkdir(exist_ok=True)
C.D = P
source_index = json.loads((D / 'Input/Source_Index.json').read_text('utf8'))
index = {r['name']: r for r in source_index['objects']}
rows = []
proofs = []


def point_key(p):
    return tuple(np.asarray(p, np.float32).tolist())


for side in ['L', 'R']:
    name = 'DOOR_STORAGE_V20_' + side + '__LEAF_Geometry'
    row0 = index[name]
    path0 = D / 'Input' / row0['file']
    a = np.load(path0)
    v0, f0, uv0 = a['v'], a['f'], a['uv']
    old_bottom = float(v0[:, 2].min())
    old_top = float(v0[:, 2].max())
    clip_z = float(np.float32(old_bottom + .15))
    used_materials = sorted({row0['materials'][int(i)] for i in a['mi']})
    assert used_materials == ['M_V18_Aged_Storage_Timber'], used_materials
    wood = used_materials[0]
    # Native export has one vertex per triangle corner. Index exactly equal
    # coordinates before tracking so the helper never needs its rounded repair
    # and nearest-face UV transfer fallback.
    indexed_v, indexed_reverse = np.unique(v0, axis=0, return_inverse=True)
    indexed_f = indexed_reverse[f0]
    src = tracked(indexed_v, indexed_f, row0['materials'], a['mi'], uv0, name)
    source_relation = next(q for q in C.REL.values() if q['name'] == name)
    assert np.array_equal(source_relation['v'], indexed_v)
    assert np.array_equal(source_relation['f'], indexed_f)
    assert np.array_equal(source_relation['uv'], uv0)
    low, high = v0.min(0) - .1, v0.max(0) + .1
    high[2] = clip_z
    cutter = finish(cube(low, high), wood, name + ' bounded bottom cut')
    cut = src - cutter
    row, cut = export(name, cut,
                      'Trim only the lower150mm to preserve the original storage hinges, '
                      'leaf tops, fixed lintel and inward door animations above the raised floor')
    exported = np.load(P / row['file'])
    v = exported['v'].copy()
    f = exported['f'].astype(np.int64)
    mi = exported['mi'].copy()
    uv = exported['uv'].copy()

    # Export's native float32 preparation can perturb retained world coordinates
    # and barycentric endpoint UVs. Restore those exact source corner values.
    source_points = {}
    for p in v0:
        key = point_key(p)
        if key in source_points:
            assert np.array_equal(source_points[key], p), ('Ambiguous source point', key)
        source_points[key] = p
    restored_points = 0
    for i, p in enumerate(v):
        old = source_points.get(point_key(p))
        if old is not None and old[2] >= clip_z:
            v[i] = old
            restored_points += 1

    mesh = cut.to_mesh64()
    face_ids = np.asarray(mesh.face_id)
    restored_corners = 0
    source_faces = 0
    for run, rid in enumerate(mesh.run_original_id):
        relation = C.REL.get(int(rid))
        if relation is None or relation['name'] != name:
            continue
        lo, hi = int(mesh.run_index[run] // 3), int(mesh.run_index[run + 1] // 3)
        for ti in range(lo, hi):
            oi = int(face_ids[ti])
            old_tri = relation['v'][relation['f'][oi]]
            old_uv = relation['uv'][oi]
            source_faces += 1
            for k, p in enumerate(v[f[ti]]):
                matches = [j for j, old in enumerate(old_tri)
                           if point_key(p) == point_key(old)]
                if matches:
                    uv[ti, k] = old_uv[matches[0]]
                    restored_corners += 1

    # A source corner may occur on several UV seams. A corner is accepted only
    # if its original face's exact UV value was preserved, or that same original
    # coordinate/UV pair appears on a retained incident face after triangulation.
    expected_pairs = set()
    for fi, face in enumerate(f0):
        for corner, vi in enumerate(face):
            if v0[vi, 2] >= clip_z:
                expected_pairs.add((tuple(v0[vi]), tuple(uv0[fi, corner])))

    tri = v[f]
    cap = np.max(abs(tri[:, :, 2] - clip_z), axis=1) < 1e-9
    assert cap.any(), 'Missing solid bottom cap'
    uv[cap] = uv_project(v, f[cap])
    mi[cap] = row['materials'].index(wood)
    v, f, mi, uv, cleanup = repair_indexed(v, f, mi, uv)
    assert np.isfinite(uv).all(), 'Nonfinite retained or cap UV'
    result = solid(v, f, name + ' saved lower-edge cut')
    assert result.status() == mf.Error.NoError and result.volume() > 0
    components = result.decompose()
    assert len(components) == len(src.decompose()), (name, len(components), len(src.decompose()))
    assert float(v[:, 2].min()) == clip_z
    assert float(v[:, 2].max()) == old_top
    actual_pairs = {(tuple(v[vi]), tuple(uv[fi, corner]))
                    for fi, face in enumerate(f) for corner, vi in enumerate(face)}
    missing_pairs = expected_pairs - actual_pairs
    assert not missing_pairs, (name, 'Source corner UV was altered or discarded', len(missing_pairs))
    np.savez_compressed(P / row['file'], v=v, f=f, mi=mi, uv=uv)
    q = {'name': name, 'rig_root': name.removesuffix('_Geometry'),
         'source_file_sha256': hashlib.sha256(path0.read_bytes()).hexdigest(),
         'source_mesh_hash': row0.get('mesh_hash'),
         'old_bottom_z_m': old_bottom, 'new_bottom_z_m': clip_z,
         'trimmed_height_m': clip_z - old_bottom,
         'old_top_z_m': old_top, 'new_top_z_m': float(v[:, 2].max()),
         'floor_z_m': -.25, 'floor_clearance_m': clip_z + .25,
         'old_volume_m3': src.volume(), 'new_volume_m3': result.volume(),
         'closed_components': len(components), 'cap_triangles': int(cap.sum()),
         'cap_material': wood, 'native_cleanup': cleanup,
         'root_and_animation_changes': False, 'fixed_frame_changes': False,
         'uv_proof': {'retained_source_corner_uv_pairs': len(expected_pairs),
                      'exact_source_corner_uv_pairs_retained': len(expected_pairs) - len(missing_pairs),
                      'missing_source_corner_uv_pairs': len(missing_pairs),
                      'restored_original_world_points': restored_points,
                      'restored_source_face_corners': restored_corners,
                      'tracked_source_faces': source_faces,
                      'finite_uv': True, 'cap_uv': 'worldXY metric projection'}}
    row.update(triangles=len(f), volume_m3=result.volume(), closed_components=len(components),
               native_cleanup=cleanup, preserve_object_transform=True, proof=q)
    rows.append(row)
    proofs.append(q)
    print('DOOR_PREPARED', name, json.dumps(q, ensure_ascii=False), flush=True)

out = {'source_model': source_index['model'], 'source_sha256': source_index['sha256'],
       'objects': rows, 'archive': [], 'proof': {'doors': proofs,
       'scope': 'Two storage leaf bottom cuts only; native model, rigs, actions, '
                'fixed frames, walls and kitchen are not modified'}}
(D / 'Prepared_Doors.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), 'utf8')
print('STORAGE_DOORS_READY', len(rows), flush=True)
