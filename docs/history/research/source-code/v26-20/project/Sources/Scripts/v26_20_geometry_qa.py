"""Independent offline QA for the V26.20 storage floor repair.

No bpy, scene changes, or preparation/build imports. --prepared reads the
prepared floor; the default reads the fresh saved Final geometry export.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

# The Blender Python runtime needs this workspace's matching 3.12 wheels;
# the workstation's 3.11 Python already has its own compatible dependencies.
W = Path(__file__).resolve().parent
if sys.version_info[:2] == (3, 12):
    sys.path[:0] = [str(W / x) for x in ['np1', 'geomlibs', 'libs']]
import numpy as np
import manifold3d as mf
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point, box, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

D = W / 'v26_20'
N = 'V26_2_Continuous_Ground_And_Perimeter_Shell'
XSTEP = 13.421809196472168
ZOLD = -.4000000059604645
ZNEW = ZOLD + .15
GEOM_TOL = .000006
UV_TOL = .00005
checks = []

def ck(name, yes, **data):
    row = {'check': name, 'pass': bool(yes), **data}
    checks.append(row)
    print('GEOMETRY_QA', name, bool(yes), data if not yes else '', flush=True)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()

def solid(v, f, name):
    obj = mf.Manifold(mf.Mesh64(np.asarray(v, dtype=np.float64, order='C'),
                               np.asarray(f, dtype=np.uint64, order='C')))
    if obj.status() != mf.Error.NoError or obj.volume() <= 0:
        raise AssertionError((name, str(obj.status()), obj.volume()))
    return obj

def prism(poly, z0, z1):
    rings = []
    parts = [poly] if poly.geom_type == 'Polygon' else list(poly.geoms)
    for part in parts:
        if part.geom_type != 'Polygon' or part.area < 1e-15:
            continue
        part = orient(part, 1)
        rings.append(np.asarray(part.exterior.coords)[:-1])
        rings.extend(np.asarray(ring.coords)[:-1] for ring in part.interiors)
    return mf.CrossSection(rings, mf.FillRule.NonZero).extrude(z1 - z0).translate([0, 0, z0])

def triangles(a):
    t = a['v'][a['f']]
    cr = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ar = np.linalg.norm(cr, axis=1) / 2
    return t, cr / np.maximum((2 * ar)[:, None], 1e-30), ar

def canonical(t):
    q = np.rint(t * 100000).astype(np.int64)
    order = np.lexsort((q[:, 2], q[:, 1], q[:, 0]))
    return tuple(q[order].ravel()), order

class Surface:
    """Exact triangle matching, then containment/UV sampling after subdivision."""
    def __init__(self, a, mats):
        self.a = a
        self.t, self.no, self.ar = triangles(a)
        self.names = np.asarray([mats[int(j)] for j in a['mi']], object)
        self.lo, self.hi = self.t.min(1), self.t.max(1)
        self.kd = cKDTree(self.t.mean(1))
        self.exact = {}
        for j, tri in enumerate(self.t):
            key, order = canonical(tri)
            self.exact.setdefault((self.names[j], key), []).append((j, order))

    def exact_triangle(self, tri, tex, mat):
        key, order = canonical(tri)
        for j, dest_order in self.exact.get((mat, key), []):
            dg = np.max(abs(tri[order] - self.t[j, dest_order]))
            du = np.max(abs(tex[order] - self.a['uv'][j, dest_order]))
            if dg <= GEOM_TOL and du <= UV_TOL:
                return True, float(dg), float(du)
        return False, None, None

    def sample(self, p, expected_uv, mat, normal):
        _, ids = self.kd.query(p, k=min(64, len(self.t)))
        ids = np.atleast_1d(ids)
        best = None
        for full in [False, True]:
            if full:
                ids = np.flatnonzero((self.names == mat) &
                    np.all(self.lo <= p + GEOM_TOL, axis=1) &
                    np.all(self.hi >= p - GEOM_TOL, axis=1))
            ids = ids[(self.names[ids] == mat) & (self.no[ids] @ normal > .9999)]
            if not len(ids):
                continue
            tr = self.t[ids]
            A, B, Q = tr[:, 1] - tr[:, 0], tr[:, 2] - tr[:, 0], p - tr[:, 0]
            aa, ab, bb = (np.einsum('ij,ij->i', x, y) for x, y in [(A, A), (A, B), (B, B)])
            aq, bq = np.einsum('ij,ij->i', A, Q), np.einsum('ij,ij->i', B, Q)
            det = aa * bb - ab * ab
            good = det > 1e-24
            s = np.zeros(len(ids)); u = np.zeros(len(ids))
            s[good] = (bb[good] * aq[good] - ab[good] * bq[good]) / det[good]
            u[good] = (aa[good] * bq[good] - ab[good] * aq[good]) / det[good]
            plane = abs(np.einsum('ij,ij->i', Q, self.no[ids]))
            good &= (s >= -1e-7) & (u >= -1e-7) & (s + u <= 1.0000001) & (plane <= GEOM_TOL)
            for k in np.flatnonzero(good):
                tex = self.a['uv'][ids[k]]
                got = tex[0] + s[k] * (tex[1] - tex[0]) + u[k] * (tex[2] - tex[0])
                du = float(np.max(abs(got - expected_uv)))
                candidate = (du, float(plane[k]), int(ids[k]))
                if best is None or candidate < best:
                    best = candidate
            if best is not None and best[0] <= UV_TOL:
                return True, best
        return False, best

def barycentric_xy(tri, xy):
    A = tri[1, :2] - tri[0, :2]
    B = tri[2, :2] - tri[0, :2]
    st = np.linalg.solve(np.column_stack([A, B]), np.asarray(xy) - tri[0, :2])
    return np.asarray([1 - st.sum(), *st])

def samples_of_clipped_top(tri, kitchen):
    cut = Polygon(tri[:, :2]).intersection(kitchen)
    parts = [cut] if cut.geom_type == 'Polygon' else [x for x in getattr(cut, 'geoms', []) if x.geom_type == 'Polygon']
    out = []
    for part in parts:
        if part.area < 1e-12:
            continue
        ref = np.asarray(part.representative_point().coords[0])
        out.append(barycentric_xy(tri, ref))
        for xy in list(part.exterior.coords)[:-1]:
            out.append(barycentric_xy(tri, .8 * np.asarray(xy) + .2 * ref))
    return out

def uv_regional_checks(old_a, old_row, after, kitchen, plan):
    t, no, ar = triangles(old_a)
    top = (no[:, 2] > .999) & (t[:, :, 2].min(1) > -.45) & (t[:, :, 2].max(1) < -.35)
    failed = []; samples = 0; max_uv = 0.; max_geom = 0.
    kitchen_faces = 0
    for j in np.flatnonzero(top):
        weights = samples_of_clipped_top(t[j], kitchen)
        if not weights:
            continue
        kitchen_faces += 1
        mat = old_row['materials'][int(old_a['mi'][j])]
        exact, dg, du = after.exact_triangle(t[j], old_a['uv'][j], mat)
        if exact:
            # Very narrow inherited triangles have an ill-conditioned
            # barycentric basis. Identical corner records are stronger
            # evidence than resampling such a triangle numerically.
            samples += len(weights)
            max_uv = max(max_uv, du); max_geom = max(max_geom, dg)
            continue
        for w in weights:
            p, tex = w @ t[j], w @ old_a['uv'][j]
            ok, detail = after.sample(p, tex, mat, no[j]); samples += 1
            if detail:
                max_uv = max(max_uv, detail[0]); max_geom = max(max_geom, detail[1])
            if not ok and len(failed) < 20:
                failed.append({'source_triangle': int(j), 'point': p.tolist(), 'material': mat, 'nearest': detail})
    ck('Kitchen floor geometry, material and regional UV remain unchanged after triangle subdivision',
       not failed and kitchen_faces >= 500, source_faces=kitchen_faces, samples=samples,
       maximum_uv_error_m=max_uv, maximum_plane_error_m=max_geom, invalid=failed)

    # Most source faces should be exact records. Only subdivided faces need
    # expensive sampling. Dense barycentric samples are filtered against the
    # independently derived floor-change volume; material names are compared.
    weights = np.asarray([[i / 6, j / 6, 1 - (i + j) / 6]
                          for i in range(1, 6) for j in range(1, 6 - i)])
    weights = np.vstack([[1/3, 1/3, 1/3], weights])
    failed = []; exact_count = 0; sample_count = 0; max_uv = 0.; max_geom = 0.
    foundation_faces = 0; foundation_samples = 0; foundation_failed = []
    exception = plan.buffer(.000002)
    for j, tri in enumerate(t):
        if ar[j] < 1e-15:
            continue
        mat = old_row['materials'][int(old_a['mi'][j])]
        exact, dg, du = after.exact_triangle(tri, old_a['uv'][j], mat)
        if exact:
            exact_count += 1
            max_uv = max(max_uv, du); max_geom = max(max_geom, dg)
            if tri[:, 2].min() < -.4001:
                foundation_faces += 1
            continue
        for w in weights:
            p, tex = w @ tri, w @ old_a['uv'][j]
            allowed = -.4001 <= p[2] <= ZNEW + .00001 and exception.covers(Point(p[:2]))
            if allowed:
                continue
            ok, detail = after.sample(p, tex, mat, no[j]); sample_count += 1
            if p[2] < -.4001:
                foundation_samples += 1
            if detail:
                max_uv = max(max_uv, detail[0]); max_geom = max(max_geom, detail[1])
            if not ok and len(failed) < 20:
                failed.append({'source_triangle': int(j), 'point': p.tolist(), 'material': mat, 'nearest': detail})
            if not ok and p[2] < -.4001 and len(foundation_failed) < 20:
                foundation_failed.append({'source_triangle': int(j), 'point': p.tolist(), 'material': mat, 'nearest': detail})
    ck('Original source surface geometry, materials and UV remain unchanged outside new top and risers',
       not failed, exact_source_triangles=exact_count, subdivided_surface_samples=sample_count,
       maximum_uv_error_m=max_uv, maximum_plane_error_m=max_geom, invalid=failed)
    ck('Original foundation faces below minus 400.1 mm retain regional geometry and UV',
       not foundation_failed, exact_foundation_triangles=foundation_faces,
       subdivided_foundation_samples=foundation_samples,
       invalid=foundation_failed)

def floor_hits(a, xy):
    t, no, ar = triangles(a)
    keep = (no[:, 2] > .7) & (t[:, :, 2].max(1) >= -.8) & (t[:, :, 2].min(1) <= -.1)
    ids = np.flatnonzero(keep); tr = t[ids]
    A, B = tr[:, 1, :2] - tr[:, 0, :2], tr[:, 2, :2] - tr[:, 0, :2]
    Q = np.asarray(xy) - tr[:, 0, :2]
    det = A[:, 0] * B[:, 1] - A[:, 1] * B[:, 0]
    good = abs(det) > 1e-14
    s = np.zeros(len(ids)); u = np.zeros(len(ids))
    s[good] = (Q[good, 0] * B[good, 1] - Q[good, 1] * B[good, 0]) / det[good]
    u[good] = (A[good, 0] * Q[good, 1] - A[good, 1] * Q[good, 0]) / det[good]
    good &= (s >= -1e-8) & (u >= -1e-8) & (s + u <= 1.00000001)
    z = tr[:, 0, 2] + s * (tr[:, 1, 2] - tr[:, 0, 2]) + u * (tr[:, 2, 2] - tr[:, 0, 2])
    return sorted(set(round(float(q), 9) for q in z[good] if -.8 <= q <= -.1), reverse=True)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--prepared', action='store_true')
    args = parser.parse_args(); started = time.perf_counter()
    source = json.loads((D / 'Input/Source_Index.json').read_text('utf8'))
    ix = {r['name']: r for r in source['objects']}
    prep_path = D / 'Prepared.json'
    if args.prepared and not prep_path.exists():
        prep_path = D / 'Prepared_Floor.json'
    prep = json.loads(prep_path.read_text('utf8')) if prep_path.exists() else {}
    folder = D / ('Prepared' if args.prepared else 'Final')
    rows = prep.get('objects', []) if args.prepared else json.loads((folder / 'Geometry_Index.json').read_text('utf8'))
    ri = {r['name']: r for r in rows}; row = ri[N]; before = ix[N]
    with np.load(folder / row['file']) as archive:
        a = {k: archive[k] for k in archive.files}
    with np.load(D / 'Input' / before['file']) as archive:
        old_a = {k: archive[k] for k in archive.files}
    obj, old = solid(a['v'], a['f'], N), solid(old_a['v'], old_a['f'], 'source ' + N)
    storage = Polygon(json.loads((W / 'v24_10/AsBuilt_Plan.json').read_text('utf8'))['outline'])
    plan = storage.intersection(box(XSTEP, -100, 100, 100))
    audit = json.loads((D / 'Kitchen_Overlap_Audit.json').read_text('utf8'))
    kitchen = shape(audit['registered_kitchen_exclusion_geometry'])
    scope = prism(plan.buffer(.000002, join_style=2), -.4001, ZNEW + .00001)
    added, removed = obj - old, old - obj
    delta = [float((added - scope).volume()), float((removed - scope).volume())]
    ck('Storage floor volume changes are confined to its registered plan and 150 mm top band',
       max(abs(x) for x in delta) < 1e-5, outside_scope_delta_m3=delta,
       added_m3=added.volume(), removed_m3=removed.volume(), independent_raise_plan_area_m2=plan.area)
    comps, old_comps = obj.decompose(), old.decompose()
    ck('Floor shell remains closed and positive with the original connected component count',
       obj.status() == mf.Error.NoError and obj.volume() > 0 and len(comps) == len(old_comps),
       before_components=len(old_comps), after_components=len(comps), positive_volume_m3=obj.volume())
    large_added = [p.volume() for p in added.decompose() if p.volume() > 1e-7]
    ck('The raised floor addition is one connected positive body', len(large_added) == 1,
       added_components_m3=large_added)
    kitchen_scope = prism(kitchen, -.851, ZNEW + .001)
    kd = [float((added ^ kitchen_scope).volume()), float((removed ^ kitchen_scope).volume())]
    ck('Kitchen floor solid volume is unchanged', max(abs(x) for x in kd) < 1e-7, delta_m3=kd)
    lower = mf.Manifold.cube([120, 120, 30]).translate([-60, -60, -30.4001])
    lower_delta = [float((added ^ lower).volume()), float((removed ^ lower).volume())]
    ck('Existing foundation volume below minus 400.1 mm remains unchanged',
       max(abs(x) for x in lower_delta) < 1e-5, delta_m3=lower_delta,
       boolean_volume_tolerance_m3=1e-5)

    t, normal, area = triangles(a)
    f = a['f']; edges = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    ck('Saved indexed floor mesh has closed edges, positive faces and finite coordinates and UVs',
       bool(np.all(counts == 2) and area.min() > 1e-18 and np.isfinite(a['v']).all() and np.isfinite(a['uv']).all()),
       minimum_triangle_area_m2=float(area.min()), invalid_edges=int(np.sum(counts != 2)))
    samples = []
    for xy in [(13.8,-15.7),(14.5,-15),(16,-15),(18,-15),(20,-15),
               (14,-13),(16,-13),(18,-13),(20,-13),(14,-11),(16,-11),(18,-11),(14,-9.5),(15,-9.5)]:
        if plan.buffer(-.01).covers(Point(xy)):
            hits = floor_hits(a, xy)
            samples.append({'xy': list(xy), 'floor_hits_m': hits,
                            'pass': bool(hits and abs(hits[0] - ZNEW) < GEOM_TOL and
                                         not any(abs(z - ZOLD) < GEOM_TOL for z in hits))})
    ck('Storage gallery and interior grid is exactly 150 mm higher with no hidden old floor plane',
       bool(samples) and all(p['pass'] for p in samples), samples=samples)
    west, east = floor_hits(a, (13.1,-15.7)), floor_hits(a, (13.8,-15.7))
    ck('Paired southwest portal levels differ by exactly 150 mm',
       bool(west and east and abs(west[0]-ZOLD)<GEOM_TOL and abs(east[0]-ZNEW)<GEOM_TOL and abs(east[0]-west[0]-.15)<GEOM_TOL),
       west_m=west, inside_m=east, step_x_m=XSTEP)
    transect = []
    for x in np.linspace(13.05, 13.85, 161):
        if abs(x-XSTEP) < .00001:
            continue
        hits = floor_hits(a, (float(x),-15.7)); target = ZOLD if x<XSTEP else ZNEW
        transect.append({'x': float(x), 'z': hits[0] if hits else None,
                         'pass': bool(hits and abs(hits[0]-target)<GEOM_TOL)})
    ck('The narrow west portal contains exactly one riser and no intermediate tread',
       all(p['pass'] for p in transect), failed=[p for p in transect if not p['pass']], sampled_points=len(transect))
    is_top = (normal[:,2]>.9999) & (abs(t[:,:,2]-ZNEW).max(1)<GEOM_TOL)
    top_uv = float(np.max(abs(a['uv'][is_top]-t[is_top,:,:2]))) if is_top.any() else None
    ck('Raised top retains world XY metre texture scale and phase',
       is_top.any() and top_uv<UV_TOL, new_top_triangles=int(is_top.sum()), maximum_uv_error_m=top_uv)
    side = (abs(normal[:,2])<.01) & (abs(t[:,:,2].max(1)-ZNEW)<GEOM_TOL)
    uv_t = a['uv'][side]
    uv_area = abs((uv_t[:,1,0]-uv_t[:,0,0])*(uv_t[:,2,1]-uv_t[:,0,1])-
                  (uv_t[:,1,1]-uv_t[:,0,1])*(uv_t[:,2,0]-uv_t[:,0,0]))/2
    ck('New step and perimeter risers have finite nondegenerate UVs',
       side.any() and np.isfinite(uv_t).all() and np.all(uv_area>1e-14),
       riser_triangles=int(side.sum()), minimum_uv_area=float(uv_area.min()) if len(uv_area) else None)
    uv_regional_checks(old_a, before, Surface(a, row['materials']), kitchen, plan)
    ck('Source V26.19 Blender file remains byte-identical', sha(source['model']) == source['sha256'])
    failures = [p for p in checks if not p['pass']]
    out = {'status': 'PASS' if not failures else 'FAIL', 'prepared': args.prepared,
           'source_sha256': source['sha256'], 'checks': checks, 'failures': failures,
           'geometry_source': str(folder / row['file']), 'test_seconds': time.perf_counter()-started,
           'uv_tolerance_m': UV_TOL, 'geometry_tolerance_m': GEOM_TOL}
    if args.prepared:
        path = D / 'Prepared_Geometry_QA.json'
    else:
        path = Path('E:/jz/JIA/Rebuild_V26_20/Reports/V26_20_Geometry_QA.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        model = path.parent.parent / 'Blender/Architecture_Complete_V26_20.blend'
        if model.exists():
            out['model_sha256'] = sha(model)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), 'utf8')
    print('GEOMETRY_QA_DONE', len(checks), len(failures), path, flush=True)
    if failures:
        raise AssertionError([p['check'] for p in failures])

if __name__ == '__main__':
    main()
