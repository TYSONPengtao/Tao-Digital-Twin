"""In-memory V4 interface repairs. No reads/writes of the delivery scene.

Call apply(S) with a mutable scene dictionary. Returned records explain all
changes and inferred dimensions. These geometry repairs are not structural
design, reinforcement design or a construction approval.
"""
import math
import numpy as np
import mapbox_earcut
from shapely.geometry import Polygon, box as rect, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import set_precision


def _polys(p):
    if p.is_empty:
        return []
    if p.geom_type == 'Polygon':
        return [p] if p.area > 1e-9 else []
    return [q for q in p.geoms if q.geom_type == 'Polygon' and q.area > 1e-9]


def _part(g, m):
    return {'geometry': g, 'material': m}


def _box(x, y, z, w, d, h):
    return {'type': 'box', 'origin': [float(x), float(y), float(z)],
            'size': [float(w), float(d), float(h)]}


def _prisms(p, z, h, material):
    if h < 1e-7:
        return []
    result = []
    for q in _polys(set_precision(p, 1e-7).buffer(0)):
        q = orient(q, 1)
        result.append(_part({'type': 'prism_holes',
                            'outer': [list(t) for t in list(q.exterior.coords)[:-1]],
                            'holes': [[list(t) for t in list(r.coords)[:-1]] for r in q.interiors],
                            'z': float(z), 'height': float(h)}, material))
    return result


def _polyhedron(p, lower, upper):
    """Closed body from a polygon with holes, lower/upper z functions."""
    p = orient(p, 1)
    rings = [list(p.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in p.interiors]
    xy = np.array([pt for ring in rings for pt in ring], float)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    tri = mapbox_earcut.triangulate_float64(xy, ends).reshape(-1, 3)
    n = len(xy)
    vv = [[float(x), float(y), float(lower(x, y))] for x, y in xy]
    vv += [[float(x), float(y), float(upper(x, y))] for x, y in xy]
    ff = [t[::-1].tolist() for t in tri] + [(t + n).tolist() for t in tri]
    k = 0
    for ring in rings:
        m = len(ring)
        ff += [[k+i, k+(i+1) % m, k+(i+1) % m+n, k+i+n] for i in range(m)]
        k += m
    return {'type': 'polyhedron', 'vertices': vv, 'faces': ff}


def _triangles(g):
    if g['type'] == 'polyhedron':
        import v2_geometry
        v, faces, _, _ = v2_geometry.data(g)
    elif g['type'] == 'prism':
        p = np.array(g['profile'], float); vec = np.array(g['vector'], float)
        normal = np.sum(np.cross(p, np.roll(p, -1, axis=0)), axis=0)
        if np.dot(normal, vec) < 0:
            p = p[::-1]
        n = len(p); v = np.vstack([p, p+vec])
        faces = [list(range(n-1, -1, -1)), list(range(n, 2*n))]
        faces += [[i, (i+1) % n, (i+1) % n+n, i+n] for i in range(n)]
    else:
        raise ValueError('Roof geometry unsupported: '+g['type'])
    return [v[[f[0], f[i], f[i+1]]] for f in faces for i in range(1, len(f)-1)]


def _lower_roof_faces(g):
    result = []
    for t in _triangles(g):
        n = np.cross(t[1]-t[0], t[2]-t[0])
        if n[2] < -1e-10:
            result.append(t)
    return result


def _support_parts(roof_g, foot, bottom, material):
    parts = []
    for t in _lower_roof_faces(roof_g):
        A = np.column_stack((t[:, :2], np.ones(3)))
        coef = np.linalg.solve(A, t[:, 2])
        def top(x, y, c=coef):
            return float(c[0]*x+c[1]*y+c[2])
        for p in _polys(Polygon(t[:, :2]).intersection(foot)):
            pts = list(p.exterior.coords)[:-1]
            if min(top(x, y)-bottom for x, y in pts) < 1e-7:
                continue
            parts.append(_part(_polyhedron(p, lambda x, y: bottom, top), material))
    return parts


def _world_box(e, p):
    g = p['geometry']; x, y, z = g['origin']; w, d, h = g['size']
    q = np.array([[x, y], [x+w, y], [x+w, y+d], [x, y+d]])
    a = e.get('angle', 0); c = math.cos(a); s = math.sin(a)
    q = q @ np.array([[c, s], [-s, c]]) + np.array(e.get('origin', [0, 0, 0]))[:2]
    z += e.get('origin', [0, 0, 0])[2]
    return Polygon(q), z, z+h


def apply(S):
    """Mutate supplied scene only; return a detailed change register."""
    elements = S['elements']; E = {e['name']: e for e in elements}; changes = []
    def record(id, names, details, dimensions=None):
        r = {'id': id, 'elements': names, 'change': details,
             'status': 'GEOMETRY_INTERFACE_REPAIRED; NOT_STRUCTURALLY_CALCULATED'}
        if dimensions is not None:
            r['inferred_parameters'] = dimensions
        changes.append(r)
    def add(name, parts, source, classification, **attrs):
        e = {'name': name, 'parts': parts, 'layer': '60_SITE', 'family': 'SITE_MODEL',
             'source': source, 'confidence': 'MEDIUM', 'classification': classification,
             'construction_status': 'INTERFACE_INFERRED_REQUIRES_FIELD_VERIFICATION', **attrs}
        elements.append(e); E[name] = e
        return e

    # Fix the upper-right bathroom route before trimming partitions to beams.
    for floor, z in [(2, 3.9), (3, 7.5)]:
        wall = E[f'PARTITIONS_JOINED_F{floor}']; oldparts = wall['parts']
        close = rect(11.9, 7.21, 12.7, 7.39)
        opening = rect(10.71, 7.65, 10.89, 8.45)
        levels = {z, z+2.1}
        for p in oldparts:
            g = p['geometry']; levels.update([g['z'], g['z']+g['height']])
        rebuilt = []
        levels = sorted(levels)
        for a, b in zip(levels[:-1], levels[1:]):
            if b-a < 1e-7:
                continue
            mid = (a+b)/2
            polys = [Polygon(g['outer'], g['holes']) for p in oldparts
                     if (g := p['geometry'])['z']-1e-8 < mid < g['z']+g['height']+1e-8]
            if not polys:
                continue
            footprint = unary_union(polys)
            if z-1e-8 < mid < z+2.1-1e-8:
                footprint = footprint.union(close).difference(opening)
            rebuilt += _prisms(footprint, a, b-a, 'M_Wall_Interior')
        wall['parts'] = rebuilt
        name = f'DOOR_BACKROOM_F{floor}_R'; door = E[name]
        door['name'] = f'DOOR_BATH_F{floor}_R'; door['origin'] = [10.8, 7.65, z]
        door['angle'] = math.pi/2; door['confidence'] = 'MEDIUM'
        door['dimension_confidence'] = 'MEDIUM'
        door['source'] = 'D03/D04 functional layout correction; M0821 route mirrored from left bath. Exact position to field-verify.'
        door['status'] = 'CORRECTED_BATHROOM_ACCESS_ROUTE; LOCATION_ESTIMATED_NOT_SURVEYED'
        E[door['name']] = door; E.pop(name)
        record(f'J12_F{floor}', [wall['name'], door['name']],
               'Closed the erroneous transverse-wall door; moved M0821 to longitudinal x10.8 wall. Ground-floor door retained.',
               {'opening_width': .8, 'opening_height': 2.1, 'Y_range': [7.65, 8.45], 'position_confidence': 'MEDIUM'})

    # Core concrete gets precedence over infill. Divide wall bands at beam levels.
    beams = []
    for e in elements:
        if e['name'].startswith('BEAM_'):
            for p in e['parts']:
                if p['geometry']['type'] != 'box':
                    raise ValueError('Unexpected framework beam geometry')
                beams.append(_world_box(e, p))
    altered = []
    for e in elements:
        if not e['name'].startswith(('FACADE_CONTINUOUS', 'PARTITIONS_JOINED')):
            continue
        result = []; trimmed = 0.
        for p in e['parts']:
            g = p['geometry']; footprint = Polygon(g['outer'], g['holes'])
            za = g['z']; zb = za+g['height']
            levels = sorted({round(v, 9) for v in ({za, zb} | {v for _, lo, hi in beams for v in [lo, hi] if za < v < zb})})
            for lo, hi in zip(levels[:-1], levels[1:]):
                if hi-lo < 1e-7:
                    continue
                mid = (lo+hi)/2
                cutters = [P for P, a, b in beams if a-1e-8 < mid < b+1e-8]
                target = footprint.difference(unary_union(cutters)) if cutters else footprint
                trimmed += (footprint.area-target.area)*(hi-lo)
                result += _prisms(target, lo, hi-lo, p['material'])
        e['parts'] = result; e['junctions_v4'] = 'Beam core excluded from infill at exact band elevations; concrete core unchanged.'
        if trimmed > 1e-8:
            altered.append(e['name'])
    record('J01', altered, 'Subtract framework beam occupied volume from wall infill; preserve official beam/column/slab sizes.')

    # Full capital bearing through explicit enlarged arch-end seats.
    for z, H, rise in [(0, 2.65, .65), (3.9, 2.90, .40)]:
        e = E[f'PORCH_ARCH_BEAM_Z{z}']; top = 3.77 if z == 0 else 7.37
        half = .218; seat_h = .055; seat_top = z+H+seat_h
        a, b = 3.9+half, 9.1-half
        xs = [3.9-half, a] + np.linspace(a, b, 49)[1:-1].tolist() + [b, 9.1+half]
        def under(x):
            return seat_top if x <= a or x >= b else seat_top+rise*math.sin(math.pi*(x-a)/(b-a))
        profile = [[xs[0], -.12, top], [xs[-1], -.12, top]] + [[float(x), -.12, under(x)] for x in xs[::-1]]
        e['parts'] = [_part({'type': 'prism', 'profile': profile, 'vector': [0, .24, 0]}, 'M_Wall_Exterior')]
        e['parts'] += [_part(_box(x-half, -half, z+H, 2*half, 2*half, seat_h), 'M_Wall_Exterior') for x in [3.9, 9.1]]
        e['junction_v4'] = 'Flat enlarged end bearing heads; arch spring starts at capital inner edge.'
        e['bearing_seat_parameters'] = {'width': .436, 'depth': .436, 'height': seat_h, 'confidence': 'INTERFACE_ESTIMATED'}
        record('J02_'+str(z), [e['name']], 'Added enlarged horizontal end seats covering full flat capital; no column-height or beam-top change.', e['bearing_seat_parameters'])

    # A continuous beam ring follows the metal-sheet underside; posts meet it.
    for i in [1, 2, 3]:
        post = E[f'SITE_SHED_{i}_POSTS']; roof = E[f'SITE_SHED_{i}_ROOF']
        pg = roof['parts'][0]['geometry']; profile = np.array(pg['profile'])
        coef = np.linalg.lstsq(np.column_stack([profile[:, :2], np.ones(len(profile))]), profile[:, 2]+pg['vector'][2], rcond=None)[0]
        def underside(x, y, c=coef):
            return float(c[0]*x+c[1]*y+c[2])
        beam_h = .18; points = []
        for p in post['parts']:
            g = p['geometry']; x, y, zz = g['origin']; w, d, _ = g['size']
            points.append([x+w/2, y+d/2])
            foot = rect(x, y, x+w, y+d)
            p['geometry'] = _polyhedron(foot, lambda x, y, zz=zz: zz,
                                         lambda x, y: underside(x, y)-beam_h)
        path = LineString(points+[points[0]])
        ring = path.buffer(.07, cap_style=2, join_style=2)
        support = [_part(_polyhedron(q, lambda x, y: underside(x, y)-beam_h, underside), 'M_Wood') for q in _polys(ring)]
        add(f'SITE_SHED_{i}_CONTINUOUS_SUPPORT_BEAMS', support,
            'Visible farm shed posts/roof from DJI; beam interface inferred to eliminate model suspension.', 'SHED_CONTINUOUS_ROOF_SUPPORT',
            estimated_section=[.14, beam_h], field_measurement_required=True)
        record('J03_'+str(i), [post['name'], f'SITE_SHED_{i}_CONTINUOUS_SUPPORT_BEAMS'],
               'Post tops and continuous beam ring follow the exact roof underside; base and roof kept.',
               {'beam_width': .14, 'beam_depth': beam_h, 'confidence': 'INTERFACE_ESTIMATED'})

    # Closed underside-following roof bases, within the existing wall thickness.
    for id, roofname, foot, bottom, material, name in [
        ('J04', 'SITE_INNER_GATEHOUSE_ROOF_CURVED_TILE_SHELL', rect(4.9, -11.95, 8.3, -11.45), 2.45, 'M_Stone_Frame', 'SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE'),
        ('J05', 'SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL', rect(3.25, -17.10, 10.8, -16.72), 2.60, 'M_Wall_Exterior', 'SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE')]:
        parts = _support_parts(E[roofname]['parts'][0]['geometry'], foot, bottom, material)
        if not parts:
            raise ValueError('Empty curved roof support '+name)
        add(name, parts, 'DJI masonry/tiled roof classification; underside closure interface inferred.', 'MASONRY_ROOF_SUPPORT_BASE', field_measurement_required=True)
        record(id, [name, roofname], 'Added roof-following masonry/roof base. Door/screen wall openings unchanged.')

    # Kitchen gables use the SAME roof bottom function, within end-wall thickness.
    kg = E['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts'][0]['geometry']
    rv = np.array(kg['vertices']); x0, x1 = 7.7, 13.35; cx = 10.29
    xlo, xhi = float(rv[:, 0].min()), float(rv[:, 0].max())
    zlow, zridge = 2.85, 4.55
    def kitchen_bottom(x):
        return zlow+(zridge-zlow)*((x-xlo)/(cx-xlo) if x <= cx else (xhi-x)/(xhi-cx))
    for name, yy in [('SITE_KITCHEN_GABLE_INFILL_-11.49', -11.6), ('SITE_KITCHEN_GABLE_INFILL_-2.71', -2.82)]:
        profile = [[x0, yy, 2.95], [x1, yy, 2.95], [x1, yy, kitchen_bottom(x1)], [cx, yy, kitchen_bottom(cx)], [x0, yy, kitchen_bottom(x0)]]
        E[name]['parts'] = [_part({'type': 'prism', 'profile': profile, 'vector': [0, .22, 0]}, 'M_Grey_Brick')]
        E[name]['junction_v4'] = 'Gable follows exact tile-shell underside; 220mm end-wall thickness, field verification required.'
    record('J06', ['SITE_KITCHEN_GABLE_INFILL_-11.49', 'SITE_KITCHEN_GABLE_INFILL_-2.71'],
           'Closed both gable top air gaps using the roofing underside plane; placed inside masonry end-wall thickness.')

    # Complete the wood frame. Retain small operable door leaf head clearance.
    seal = []
    for j in [1, 2]:
        g = E[f'SITE_KITCHEN_TIMBER_DOOR_{j}']['parts'][0]['geometry']
        x, y, zz = g['origin']; w, d, h = g['size']
        seal.append(_part(_box(x, y, zz+h+.003, w, d, 1.92-(zz+h+.003)), 'M_Timber_Honey'))
    seal += [_part(_box(7.645, -11.24, z, .11, 8.28, h), 'M_Timber_Honey') for z, h in [(2.08, .02), (2.48, .07)]]
    # Avoid duplicating solid wood in the round end/centre posts.
    column_footprints = []
    for p in E['SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS']['parts']:
        g = p['geometry']
        if g['type'] == 'cylinder':
            x, y, _ = g['origin']; from shapely.geometry import Point
            column_footprints.append(Point(x, y).buffer(g['radius'], resolution=32))
    out = []
    for p in seal:
        g = p['geometry']; x, y, z = g['origin']; w, d, h = g['size']
        out += _prisms(rect(x, y, x+w, y+d).difference(unary_union(column_footprints)), z, h, p['material'])
    add('SITE_KITCHEN_TIMBER_FRAME_CLOSURES', out, 'DJI_0156/0867 visible timber frame; seam closure geometry estimated.', 'TIMBER_FRAME_HEAD_AND_TRANSOM_CLOSURES', operable_leaf_head_gap=.003)
    record('J09', ['SITE_KITCHEN_TIMBER_FRAME_CLOSURES'], 'Closed upper transom air bands with timber framing; door leaf retains estimated 3mm top installation gap.', {'door_head_gap': .003, 'confidence': 'INTERFACE_ESTIMATED'})

    # Preserve external retaining base, independently set inside crown datum.
    e = E['SITE_GATE_EAST_FLANK']; old = e['parts'][0]['geometry']; v = np.array(old['vertices'])
    base0, base1 = float(v[0, 2]), float(v[1, 2]); xa, xb = 8.3, 13.3
    def base(x, y):
        return min(-.45, base0+(base1-base0)*(x-xa)/(xb-xa))
    footprint = rect(xa, -11.825, xb, -11.575); white_bottom = 1.55; crown = 2.20
    e['parts'] = [_part(_polyhedron(footprint, base, lambda x, y: white_bottom), 'M_Grey_Brick'),
                  _part(_polyhedron(footprint, lambda x, y: white_bottom, lambda x, y: crown), 'M_Wall_Exterior')]
    e['datum_v4'] = {'inside_floor': -.45, 'inside_wall_height': 2.65, 'crown': crown, 'external_retaining_base': 'existing varying base retained'}
    cap = E['SITE_GATE_EAST_FLANK_TILE_COPING']; g = cap['parts'][0]['geometry']
    for i, pt in enumerate(g['vertices']):
        pt[2] = crown + (.17 if i in [2, 5] else 0)
    record('J07', [e['name'], cap['name']], 'Separated crown datum from external low terrain; continuous interior crown at z2.20, external retaining base retained.', e['datum_v4'])
    return changes
