"""Read-only, scene-driven verification of the V4 interface repairs.

Default input: E:/jz/JIA/Rebuild_V4/05_Intermediate/Architecture_Scene.json
Default output: E:/jz/JIA/Rebuild_V4/09_Report/Interface_Repair_Check.json
Use --scene and --output to inspect a copy. No model geometry is written.
"""
import argparse
import collections
import json
import math
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(W/x) for x in ['np1', 'geomlibs', 'libs']] + [str(W)]
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import v2_geometry


def solid_data(g):
    typ = g['type']
    if typ in v2_geometry.TYPES:
        v, f, _, _ = v2_geometry.data(g)
        return v, f
    if typ == 'box':
        x, y, z = g['origin']; w, d, h = g['size']
        p = np.array([[x, y, z], [x+w, y, z], [x+w, y+d, z], [x, y+d, z]])
        vec = np.array([0, 0, h])
    elif typ == 'cylinder':
        x, y, z = g['origin']; r = g['radius']
        p = np.array([[x+r*math.cos(a), y+r*math.sin(a), z]
                      for a in np.linspace(0, 2*math.pi, g['segments'], endpoint=False)])
        vec = np.array([0, 0, g['height']])
    elif typ == 'prism':
        p = np.array(g['profile']); vec = np.array(g['vector'])
    else:
        return None, None
    normal = np.sum(np.cross(p, np.roll(p, -1, axis=0)), axis=0)
    if np.dot(normal, vec) < 0:
        p = p[::-1]
    n = len(p); v = np.vstack([p, p+vec])
    f = [list(range(n-1, -1, -1)), list(range(n, 2*n))]
    f += [[i, (i+1) % n, (i+1) % n+n, i+n] for i in range(n)]
    return v, f


class SceneGeometry:
    def __init__(self, S):
        self.S = S
        self.E = {e['name']: e for e in S['elements']}
        self.cache = {}

    def parts(self, e):
        return self.S['definitions'][e['definition']]['parts'] if 'definition' in e else e['parts']

    def world_part(self, p, e):
        v, f = solid_data(p['geometry'])
        if v is None:
            return None, None
        a = e.get('angle', 0); c = math.cos(a); s = math.sin(a)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return v @ R.T + np.array(e.get('origin', [0, 0, 0])), f

    def triangles(self, name):
        if name not in self.cache:
            e = self.E[name]; result = []
            for p in self.parts(e):
                v, f = self.world_part(p, e)
                if v is None:
                    continue
                # Only triangles of positive projected area are used by ray_z.
                for face in f:
                    for i in range(1, len(face)-1):
                        result.append(v[[face[0], face[i], face[i+1]]])
            self.cache[name] = np.array(result)
        return self.cache[name]

    def ray(self, name, point, axis=2):
        point = np.array(point, float)
        projected = [i for i in range(3) if i != axis]
        hits = []
        for t in self.triangles(name):
            p = t[:, projected]; B = np.column_stack((p[1]-p[0], p[2]-p[0]))
            if abs(np.linalg.det(B)) < 1e-10:
                continue
            q = np.linalg.solve(B, point[projected]-p[0])
            if q.min() >= -1e-7 and q.sum() <= 1+1e-7:
                hits.append(float(t[0, axis]+q[0]*(t[1, axis]-t[0, axis])+q[1]*(t[2, axis]-t[0, axis])))
        return sorted(set(round(v, 8) for v in hits))

    def vertical(self, name, x, y):
        return self.ray(name, [x, y, 0], 2)

    def bbox(self, name):
        e = self.E[name]
        vv = [self.world_part(p, e)[0] for p in self.parts(e)]
        vv = np.vstack([v for v in vv if v is not None])
        return vv.min(0), vv.max(0)


def run(scene, output):
    S = json.loads(scene.read_text(encoding='utf-8'))
    G = SceneGeometry(S); E = G.E; failures = []; notes = []
    tolerance = .001
    R = {'source': str(scene), 'units': 'metres', 'tolerance_m': tolerance,
         'method': 'Analytic infill/box section intersections; scene face-triangle ray intersections; aperture occupancy; capital seat contact projection.',
         'scope': 'Geometry interfaces only. Finite contact is not bearing-capacity verification, structural approval or construction acceptance.',
         'wall_beam_overlaps': [], 'roof_support_chain': [], 'arch_end_bearing': [],
         'bathroom_openings': [], 'west_wall_finish': [], 'decorative_backing': [], 'failures': failures, 'notes': notes}

    def require(ok, detail):
        if not ok:
            failures.append(detail)

    # Core-wall overlap volume, respecting all opening loops in the infill.
    beams = []
    for e in S['elements']:
        if not e['name'].startswith('BEAM_'):
            continue
        for p in G.parts(e):
            require(p['geometry']['type'] == 'box', 'Unexpected beam type: '+e['name'])
            v, _ = G.world_part(p, e); lo = v.min(0); hi = v.max(0)
            beams.append((e['name'], box(lo[0], lo[1], hi[0], hi[1]), lo[2], hi[2]))
    volume = 0.
    for e in S['elements']:
        if not e['name'].startswith(('FACADE_CONTINUOUS', 'PARTITIONS_JOINED')):
            continue
        for j, p in enumerate(G.parts(e)):
            g = p['geometry']
            require(g['type'] == 'prism_holes', 'Unexpected wall type: '+e['name'])
            if g['type'] != 'prism_holes':
                continue
            P = Polygon(g['outer'], g['holes']); za = g['z']; zb = za+g['height']
            for bn, B, a, b in beams:
                h = min(zb, b)-max(za, a)
                if h < 1e-7:
                    continue
                overlap = P.intersection(B).area*h
                volume += overlap
                if overlap > 1e-8:
                    R['wall_beam_overlaps'].append({'wall': e['name'], 'part_1based': j+1, 'beam': bn, 'volume_m3': overlap})
    R['wall_beam_overlap_volume_m3'] = round(volume, 12)
    require(volume < 1e-8, 'Positive volume occupied by both infill and concrete beam core.')

    # 12 post-beam-roof interfaces. Verify at each support centre.
    for i in [1, 2, 3]:
        post = E[f'SITE_SHED_{i}_POSTS']; bn = f'SITE_SHED_{i}_CONTINUOUS_SUPPORT_BEAMS'; rn = f'SITE_SHED_{i}_ROOF'
        require(len(post['parts']) == 4, 'Unexpected post count: '+post['name'])
        for j, p in enumerate(post['parts']):
            v, _ = G.world_part(p, post); xy = (v.min(0)[:2]+v.max(0)[:2])/2
            pv = G.vertical(post['name'], *xy); bv = G.vertical(bn, *xy); rv = G.vertical(rn, *xy)
            if not (pv and bv and rv):
                require(False, f'Missing support ray: {post["name"]} part {j+1}'); continue
            a, b = float(bv[0]-pv[-1]), float(rv[0]-bv[-1])
            R['roof_support_chain'].append({'group': post['name'], 'part_1based': j+1, 'xy': xy.tolist(), 'post_to_beam_gap_m': round(a, 8), 'beam_to_roof_gap_m': round(b, 8)})
            require(abs(a) <= tolerance and abs(b) <= tolerance, f'Shed support discontinuity: {post["name"]} part {j+1}')

    # Curved masonry roof bases, multiple samples including near both ends.
    for ln, bn, rn, points in [
        ('SITE_INNER_STONE_GATEHOUSE', 'SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE', 'SITE_INNER_GATEHOUSE_ROOF_CURVED_TILE_SHELL', [(5.1, -11.7), (6.6, -11.7), (8.1, -11.7), (6.6, -11.85), (6.6, -11.55)]),
        ('SITE_SOUTH_SCREENWALL_RAISED_BODY', 'SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE', 'SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL', [(3.45, -16.9), (6.6, -16.9), (10.6, -16.9), (6.6, -17.05), (6.6, -16.77)])]:
        for xy in points:
            av = G.vertical(ln, *xy); bv = G.vertical(bn, *xy); cv = G.vertical(rn, *xy)
            if not (av and bv and cv):
                require(False, 'Missing masonry base ray: '+bn); continue
            a, b = float(bv[0]-av[-1]), float(cv[0]-bv[-1])
            R['roof_support_chain'].append({'group': ln, 'xy': xy, 'lower_to_base_gap_m': round(a, 8), 'base_to_roof_gap_m': round(b, 8)})
            require(abs(a) <= tolerance and abs(b) <= tolerance, 'Masonry roof support discontinuity: '+bn+' '+str(xy))

    # Complete capital top projection must be covered by an enlarged flat seat.
    for z in [0, 3.9]:
        for x in [3.9, 9.1]:
            cn = f'ROMAN_COLUMN_X{x}_Z{z}'; an = f'PORCH_ARCH_BEAM_Z{z}'
            col = E[cn]; definition = S['definitions'][col['definition']]
            cap_profile = definition['parts'][-1]['geometry']['profile']
            radius, h = cap_profile[-1]; cap_top = z+h
            cap = Point(x, 0).buffer(radius, resolution=64); seats = []
            for p in G.parts(E[an]):
                if p['geometry']['type'] != 'box':
                    continue
                v, _ = G.world_part(p, E[an]); lo = v.min(0); hi = v.max(0)
                if abs(lo[2]-cap_top) <= tolerance:
                    seats.append(box(lo[0], lo[1], hi[0], hi[1]))
            projected = unary_union(seats) if seats else Polygon()
            area = cap.intersection(projected).area; fraction = area/cap.area
            sample = G.vertical(an, x, .18)
            gap = sample[0]-cap_top if sample else None
            R['arch_end_bearing'].append({'column': cn, 'arch': an, 'capital_top_z': cap_top, 'capital_radius_m': radius, 'contact_area_m2': round(area, 8), 'covered_capital_fraction': round(fraction, 8), 'seat_gap_at_y_0_18_m': gap})
            require(fraction > .999 and gap is not None and abs(gap) <= tolerance, 'Incomplete flat capital bearing: '+cn)

    # Test occupancy in the old/new apertures, not only door transform metadata.
    def wall_occupied(name, x, y, z):
        for p in G.parts(E[name]):
            g = p['geometry']
            if g['type'] != 'prism_holes':
                continue
            if g['z']+1e-7 < z < g['z']+g['height']-1e-7 and Polygon(g['outer'], g['holes']).covers(Point(x, y)):
                return True
        return False
    for floor, z in [(2, 3.9), (3, 7.5)]:
        wall = f'PARTITIONS_JOINED_F{floor}'; dn = f'DOOR_BATH_F{floor}_R'; door = E[dn]
        old_closed = [wall_occupied(wall, 12.3, 7.3, z+v) for v in [.1, 1.0, 2.05]]
        new_open = [not wall_occupied(wall, 10.8, 8.05, z+v) for v in [.1, 1.0, 2.05]]
        head = wall_occupied(wall, 10.8, 8.05, z+2.15)
        origin_ok = np.linalg.norm(np.array(door['origin'])-np.array([10.8, 7.65, z])) <= tolerance
        angle_ok = abs(door['angle']-math.pi/2) < 1e-8
        row = {'floor': floor, 'old_aperture_closed_at_three_heights': old_closed, 'new_aperture_clear_at_three_heights': new_open,
               'new_wall_present_above_head': head, 'door_origin': door['origin'], 'door_angle_rad': door['angle'], 'position_confidence': door['confidence']}
        R['bathroom_openings'].append(row)
        require(all(old_closed) and all(new_open) and head and origin_ok and angle_ok and door['confidence'] == 'MEDIUM', 'Bathroom route repair mismatch: '+dn)
    f1 = E.get('DOOR_BACKROOM_F1_R')
    require(f1 is not None and np.linalg.norm(np.array(f1['origin'])-np.array([11.9, 7.3, 0])) <= tolerance, 'Ground floor right door moved unexpectedly.')

    # Optional finish audit is a separate section, not a structural inference.
    if 'SITE_COURTYARD_WEST_WHITE_INSIDE' in E:
        for y in [-10, -5, .5]:
            a = G.vertical('SITE_COURTYARD_WEST_TILE_WALL', 0, y)
            b = G.vertical('SITE_COURTYARD_WEST_WHITE_INSIDE', .133, y)
            if a and b:
                exceed = b[-1]-a[-1]
                R['west_wall_finish'].append({'sample_y': y, 'wall_crown_z': a[-1], 'white_finish_top_z': b[-1], 'finish_above_wall_m': round(exceed, 8)})
                require(exceed <= tolerance, 'West white finish projects above masonry crown: Y='+str(y))
            else:
                notes.append('West finish sample missing at Y='+str(y))

    # Measure rays from raised decorative strips backwards towards their body.
    # Count separately named backing pieces when their name contains the frame name.
    decor = [('SITE_GATEHOUSE_CARVED_PANEL_FRAME_4.95', 'SITE_INNER_STONE_GATEHOUSE'),
             ('SITE_GATEHOUSE_CARVED_PANEL_FRAME_7.95', 'SITE_INNER_STONE_GATEHOUSE')]
    decor += [(n, 'SITE_SOUTH_SCREENWALL_RAISED_BODY') for n in E if n.startswith('SITE_SCREENWALL_STEPPED_PANEL_') and 'BACK' not in n.upper()]
    decor += [(n, 'BALCONY_STONE_JOINED') for n in E if n.startswith('BALCONY_STONE_PANEL_MOULDING_') and 'BACK' not in n.upper()]
    for dn, body in decor:
        e = E[dn]; measured = []
        candidates = [body] + [n for n in E if n != dn and dn in n]
        # Below screenwall raised-body base, original perimeter body also supports plaster frames.
        if body.startswith('SITE_SOUTH_SCREENWALL'):
            candidates += [n for n in E if n.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_') and 'TILE' not in n]
        for p in G.parts(e):
            v, _ = G.world_part(p, e)
            if v is None:
                continue
            # All three frame classes are planar XZ, front -Y; use face centroid at back Y.
            lo, hi = v.min(0), v.max(0); x, z = v.mean(0)[[0, 2]]; back_y = float(hi[1])
            # A curved-wall relief has a planar but sloped rear triangle. Its
            # local rear centroid is not the maximum Y of all triangle vertices.
            if p['geometry']['type'] == 'prism' and p['geometry']['vector'][1] < 0:
                pg = p['geometry']; q = np.mean(np.array(pg['profile'], float), axis=0)
                a = e.get('angle', 0); c = math.cos(a); ss = math.sin(a)
                q = q @ np.array([[c, ss, 0], [-ss, c, 0], [0, 0, 1]]) + np.array(e.get('origin', [0, 0, 0]))
                x, back_y, z = map(float, q)
            hits = []
            for n in candidates:
                hits += [h for h in G.ray(n, [x, back_y, z], 1) if h >= back_y-tolerance]
            if hits:
                measured.append(max(0., min(hits)-back_y))
        max_gap = max(measured) if measured else None
        R['decorative_backing'].append({'frame': dn, 'body': body, 'backing_candidates': candidates, 'samples': len(measured), 'max_backing_air_gap_m': round(max_gap, 8) if max_gap is not None else None})
        if max_gap is None:
            notes.append('No supporting ray found for decorative frame: '+dn)
        else:
            require(max_gap <= tolerance, 'Decorative frame lacks immediate backing: '+dn)

    R['passed'] = not failures
    R['summary'] = {'failure_count': len(failures), 'shed_posts_checked': 12, 'masonry_roof_samples_checked': 10,
                    'capital_seats_checked': 4, 'bathrooms_checked': 2, 'decorative_frames_checked': len(decor)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'passed': R['passed'], 'report': str(output), 'summary': R['summary'], 'failures': failures}, ensure_ascii=False, indent=2))
    return R


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--scene', type=Path, default=Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json'))
    p.add_argument('--output', type=Path, default=Path(r'E:\jz\JIA\Rebuild_V4\09_Report\Interface_Repair_Check.json'))
    args = p.parse_args()
    if not args.scene.is_file():
        p.error('Scene is not available yet: '+str(args.scene))
    result = run(args.scene, args.output)
    sys.exit(0 if result['passed'] else 1)
