"""Map screenwall relief rear faces onto existing external masonry faces.

In-memory only; no wall is thickened. Splits reliefs at support-face boundaries
so each new triangular rear face remains planar and exactly supported.
"""
import copy
import numpy as np
import mapbox_earcut
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from check_final_v4 import SceneGeometry


def _polys(p):
    if p.is_empty:
        return []
    if p.geom_type == 'Polygon':
        return [p] if p.area > 1e-10 else []
    return [q for q in getattr(p, 'geoms', []) if q.geom_type == 'Polygon' and q.area > 1e-10]


def fix_screen_relief_backing(S):
    G = SceneGeometry(S); E = G.E; faces = []
    candidates = [n for n in E if n.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_') and 'TILE' not in n]
    candidates += ['SITE_SOUTH_SCREENWALL_RAISED_BODY', 'SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE']
    for n in candidates:
        if n not in E:
            continue
        for t in G.triangles(n):
            normal = np.cross(t[1]-t[0], t[2]-t[0])
            # South/front outward faces only; exclude opposite/internal walls.
            if normal[1] >= -1e-10 or t[:, 1].min() > -15.5 or t[:, 1].max() < -18.5:
                continue
            xz = t[:, [0, 2]]; p = Polygon(xz)
            if p.area < 1e-10:
                continue
            coef = np.linalg.solve(np.column_stack([xz, np.ones(3)]), t[:, 1])
            faces.append((p, coef, n))
    if not faces:
        raise ValueError('No screenwall outward support faces found')
    register = []
    for name in [f'SITE_SCREENWALL_STEPPED_PANEL_{i}' for i in range(3)]:
        e = E[name]; result = []; shift = []; support_counts = {}
        original_area = 0.; mapped_area = 0.
        for part in e['parts']:
            g = part['geometry']
            if g['type'] != 'prism' or len(g['profile']) != 3:
                raise ValueError('Relief must have triangular planar prism profile: '+name)
            v = np.array(g['profile'], float); orig = Polygon(v[:, [0, 2]])
            original_area += orig.area; remaining = orig
            cent = np.array([orig.centroid.x, orig.centroid.y, 1.])
            # On overlapping domains choose the most exterior surface first.
            available = [(p, c, n) for p, c, n in faces if p.intersects(orig)]
            available.sort(key=lambda item: float(cent @ item[1]))
            for face, coef, n in available:
                for piece in _polys(remaining.intersection(face)):
                    piece = orient(piece, 1)
                    xy = np.array(list(piece.exterior.coords)[:-1], float)
                    tri = mapbox_earcut.triangulate_float64(xy, np.array([len(xy)], np.uint32)).reshape(-1, 3)
                    for ids in tri:
                        txy = xy[ids]
                        if abs(np.cross(txy[1]-txy[0], txy[2]-txy[0])) < 2e-10:
                            continue
                        vv = []
                        for i in ids:
                            x, z = xy[i]; y = float(coef @ [x, z, 1.])
                            vv.append([float(x), y, float(z)])
                            shift.append(y-float(v[:, 1].mean()))
                        # A negative-Y extrusion stays outside the existing body.
                        pp = copy.deepcopy(part)
                        pp['geometry'] = {'type': 'prism', 'profile': vv,
                                          'vector': [0, -abs(float(g['vector'][1])), 0]}
                        pp['support_body'] = n
                        pp['interface_v4'] = 'Rear triangle lies in actual existing outward face plane; no backing wall added.'
                        result.append(pp)
                        support_counts[n] = support_counts.get(n, 0)+1
                    mapped_area += piece.area
                remaining = remaining.difference(face)
                if remaining.area < 1e-9:
                    break
            if remaining.area > 1e-8:
                raise ValueError(f'Unbacked relief area {name}: {remaining.area:.9f} m2')
        if abs(mapped_area-original_area) > 1e-7:
            raise ValueError('Relief area changed unexpectedly: '+name)
        old_count = len(e['parts']); e['parts'] = result
        e['installation_interface'] = 'Each rear triangle mapped to the current south perimeter / raised screenwall outward face. Relief follows existing curve and crown step.'
        e['interface_method'] = 'XZ clipping at support face boundaries; exact plane interpolation of rear Y; 25mm outward relief depth retained.'
        register.append({'id': 'SCREEN_RELIEF_BACKING_'+name[-1], 'element': name,
                         'old_parts': old_count, 'new_parts': len(result),
                         'existing_support_faces': support_counts,
                         'mapped_projected_area_m2': round(mapped_area, 9),
                         'original_projected_area_m2': round(original_area, 9),
                         'rear_y_shift_range_m': [round(min(shift), 8), round(max(shift), 8)],
                         'backing_wall_added': False,
                         'status': 'GEOMETRY_INTERFACE_REPAIR; NOT_CARVING_OR_FIXING_DESIGN'})
    return register
