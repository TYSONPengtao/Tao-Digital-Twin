"""Read-only construction geometry audit. Not a statutory compliance certificate.

Usage: python check_construction_v4.py --scene PATH --register OPTIONAL_CSV --out DIR
Geometry is expanded directly from the scene. Attribute dimensions are not used
as measured dimensions. Optional node metadata improves correspondence:
host, finished_surface_role, outward_xy/drain_xy, stair_usage, opening_state.
"""
import argparse
import collections
import csv
import json
import math
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(WORK / x) for x in ['np1', 'geomlibs', 'libs']]
import numpy as np

TOL = 1e-6


def geom_data(g):
    typ = g['type']
    if typ == 'box':
        x, y, z = g['origin']; w, d, h = g['size']
        p = np.array([[x, y, z], [x+w, y, z], [x+w, y+d, z], [x, y+d, z]])
        vec = np.array([0., 0., h])
    elif typ == 'prism':
        p = np.array(g['profile'], float); vec = np.array(g['vector'], float)
    elif typ == 'cylinder':
        x, y, z = g['origin']; r = g['radius']; n = g.get('segments', 32)
        p = np.array([[x+r*math.cos(a), y+r*math.sin(a), z] for a in np.linspace(0, 2*math.pi, n, endpoint=False)])
        vec = np.array([0., 0., g['height']])
    elif typ == 'prism_holes':
        # Holes are retained separately for vertical point queries. Cap triangles
        # are unnecessary for a planar height/gradient audit.
        p = np.c_[np.array(g['outer'], float), np.full(len(g['outer']), g['z'])]
        vec = np.array([0., 0., g['height']])
    elif typ in ('polyhedron', 'terrain', 'mesh'):
        return np.array(g['vertices'], float), g['faces']
    elif typ in ('surface_polygon', 'nurbs_patch'):
        p = np.array(g['points'], float)
        return p, [list(range(len(p)))]
    elif typ == 'lathe':
        n = g.get('segments', 64)
        v = np.array([[r*math.cos(a), r*math.sin(a), z] for r, z in g['profile'] for a in np.linspace(0, 2*math.pi, n, endpoint=False)])
        faces = [[j*n+i, j*n+(i+1)%n, (j+1)*n+(i+1)%n, (j+1)*n+i] for j in range(len(g['profile'])-1) for i in range(n)]
        faces += [list(range(n-1, -1, -1)), list(range((len(g['profile'])-1)*n, len(v)))]
        return v, faces
    else:
        return None, []
    nn = np.sum(np.cross(p, np.roll(p, -1, axis=0)), axis=0)
    if np.dot(nn, vec) < 0:
        p = p[::-1]
    n = len(p); v = np.vstack([p, p+vec])
    f = [list(range(n-1, -1, -1)), list(range(n, 2*n))]
    f += [[i, (i+1)%n, (i+1)%n+n, i+n] for i in range(n)]
    return v, f


def transformed(points, e):
    a = float(e.get('angle', 0)); c, s = math.cos(a), math.sin(a)
    r = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return np.asarray(points) @ r.T + np.array(e.get('origin', [0, 0, 0]), float)


def inside_ring(xy, poly):
    x, y = xy; inside = False
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        ab = b-a; ap = np.array(xy)-a
        if abs(np.cross(ab, ap)) < 1e-7 and np.dot(ap, ab) >= -TOL and np.dot(ap, ab) <= np.dot(ab, ab)+TOL:
            return True
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside = not inside
    return inside


def top_faces(rec):
    for ids in rec['faces']:
        p = rec['vertices'][ids]
        if len(p) < 3:
            continue
        nn = np.sum(np.cross(p, np.roll(p, -1, axis=0)), axis=0)
        ll = np.linalg.norm(nn)
        if ll < 1e-12 or nn[2] / ll < .70:
            continue
        n = nn / ll
        grad = -n[:2]/n[2]
        residual = np.max(np.abs((p-p[0]) @ n))
        yield {'points': p, 'gradient': grad, 'intercept': float(p[0, 2]-np.dot(grad, p[0, :2])), 'area_xy': abs(nn[2])/2, 'planarity_m': float(residual)}


def top_at(rec, xy):
    if any(inside_ring(xy, h) for h in rec['holes']):
        return None
    vals = [float(np.dot(t['gradient'], xy)+t['intercept']) for t in top_faces(rec) if inside_ring(xy, t['points'][:, :2])]
    return max(vals) if vals else None


class Audit:
    def __init__(self, scene, register=None, proposed_width=1.1, proposed_gap=.02):
        self.s = scene; self.result = []; self.rec = []; self.by_name = collections.defaultdict(list)
        self.proposed_width = proposed_width; self.proposed_gap = proposed_gap
        attrs = {}
        if register:
            with Path(register).open(encoding='utf-8-sig', newline='') as f:
                for row in csv.DictReader(f):
                    name = row.get('Element') or row.get('name') or row.get('Name')
                    if name: attrs[name] = row
        self.elements = []
        for raw in scene['elements']:
            e = dict(raw)
            for k, v in attrs.get(e['name'], {}).items():
                if k.lower() in ('host', 'finished_surface_role', 'stair_usage', 'opening_state') and k not in e: e[k.lower()] = v
            self.elements.append(e)
            pp = scene['definitions'][e['definition']]['parts'] if 'definition' in e else e.get('parts', [])
            for j, p in enumerate(pp):
                v, fs = geom_data(p['geometry'])
                if v is None: continue
                holes = [transformed(np.c_[h, np.zeros(len(h))], e)[:, :2] for h in p['geometry'].get('holes', [])]
                rec = {'element': e, 'part_index': j+1, 'geometry': p['geometry'], 'material': p.get('material'), 'vertices': transformed(v, e), 'local_vertices': v, 'faces': fs, 'holes': holes,
                       'finished_surface': p.get('finished_surface'), 'has_finished_surface_flag': 'finished_surface' in p}
                rec['lo'] = rec['vertices'].min(0); rec['hi'] = rec['vertices'].max(0)
                self.rec.append(rec); self.by_name[e['name']].append(rec)

    def add(self, check, names, status, measured, rule, note=''):
        self.result.append({'check': check, 'elements': names, 'status': status, 'measured': measured, 'rule': rule, 'note': note})

    def bounds(self, name):
        rr = self.by_name.get(name, [])
        return (np.min([x['lo'] for x in rr], axis=0), np.max([x['hi'] for x in rr], axis=0)) if rr else (None, None)

    def finishes(self, role):
        answer = []
        for r in self.rec:
            e = r['element']; name = e['name'].upper(); er = str(e.get('finished_surface_role', e.get('role', ''))).lower()
            named = name.startswith('CONSTRUCTION_') and role.upper() in name and any(x in name for x in ('FINISH', 'SLOPE', 'SCREED', 'SURFACE', 'PAVING'))
            if er != role and not named: continue
            # A finish assembly can include its flat waterproof backing,
            # underside stone and a window-head drip. Only explicitly tagged
            # finished surfaces drain. Unmarked V3 assemblies retain the
            # original baseline audit behaviour.
            marked = any(x['has_finished_surface_flag'] for x in self.by_name[e['name']])
            if not marked or r['finished_surface'] is True: answer.append(r)
        return answer

    def guards(self):
        groups = [('BALCONY_STONE_JOINED', 'balcony', 3.9), ('TERRACE_STONE_PARAPET', 'terrace', 7.5)]
        for name, role, datum in groups:
            members = [e['name'] for e in self.elements if e.get('layer', '').startswith('41_') and not e.get('finished_surface_role') and (e['name'] == name or e.get('host') == name or (name == 'BALCONY_STONE_JOINED' and e['name'] == 'BALCONY_STONE_COPING_JOINED'))]
            rr = [r for n in members for r in self.by_name[n]]
            rr = [r for r in rr if r['finished_surface'] is not True]
            ff = self.finishes(role)
            if not rr:
                self.add('guard_height', [name], 'needs-design', {}, 'GB 55038-2025 4.1.15 / 4.2.8', '未找到对应栏杆实体')
                continue
            guardtops = []
            for r in rr:
                for t in top_faces(r):
                    if t['area_xy'] > .003: guardtops.append(float(t['points'][:, 2].min()))
            # Body and continuous coping are separate solids. The continuous
            # coping's maximum elevation is legitimate only when it covers the
            # full body path. Mark coverage unresolved unless all caps are flat.
            top = max(guardtops) if guardtops else float(max(r['hi'][2] for r in rr))
            heights = [float(t['points'][:, 2].max()) for r in ff for t in top_faces(r)]
            floor = max(heights) if heights else datum+.05
            net = top-floor
            state = ('pass' if net >= 1.2-TOL else 'fail') if heights else 'needs-design'
            self.add('guard_height', members, state, {'geometry_guard_top_m': top, 'finished_surface_highest_m': floor, 'net_height_conservative_m': net, 'finish_elements': sorted(set(r['element']['name'] for r in ff)), 'finish_is_assumed': not bool(heights)}, '净高>=1.20 m；GB 55038-2025 4.1.15 / 4.2.8', '按实际完成面最高点保守起算；须另查连续防护覆盖、可登踏台面及栏杆承载。无完成面实体时50 mm仅为审查假设。')
            self.add('guard_nonclimb_and_load', members, 'needs-design', {}, 'GB 55038-2025 4.1.15 / 4.2.8', '净高通过不证明防攀登、栏杆强度及连接锚固通过')

    def slopes(self):
        for role, threshold, clause in [('window_sill', .05, 'GB 55030-2022 4.5.3'), ('balcony', .01, 'GB 55030-2022 4.5.4'), ('terrace', .01, 'GB 55030-2022 4.5.4'), ('site_paving', .002, 'GB 55038-2025 3.2.5')]:
            ff = self.finishes(role)
            # Original window sills are in component definitions; audit these
            # too, so missing a new CONSTRUCTION node cannot yield a false pass.
            if role == 'window_sill':
                hosts = {r['element'].get('host') for r in ff}
                for r in self.rec:
                    if r['element'].get('layer') == '31_WINDOW' and 'definition' in r['element'] and not r['element']['name'].startswith('WINDOW_STUDY') and r['material'] == 'M_Stone' and r['element']['name'] not in hosts: ff.append(r)
            if not ff:
                self.add(role+'_slope', [], 'needs-design', {}, clause, '缺可识别的完成坡面实体')
                continue
            for r in ff:
                e = r['element']; tops = [t for t in top_faces(r) if t['area_xy'] > 1e-4]
                if not tops:
                    self.add(role+'_slope', [e['name']], 'needs-design', {'part_index': r['part_index']}, clause, '无法从实体顶面求排水坡')
                    continue
                slopes = [float(np.linalg.norm(t['gradient'])) for t in tops]
                all_min = min(slopes); all_max = max(slopes)
                state = 'pass' if all_min >= threshold-TOL else 'fail'
                direction = e.get('outward_xy')
                direction_label = 'outward_xy'
                if direction is None and e.get('drain_xy') is not None:
                    center = (r['lo'][:2]+r['hi'][:2])/2
                    direction = np.array(e['drain_xy'])[:2]-center; direction_label = 'drain_xy'
                if direction is None:
                    direction_state = 'needs-design'; directional = None
                else:
                    direct = np.asarray(direction, float)[:2]; ll = np.linalg.norm(direct)
                    directional = [float(-np.dot(t['gradient'], direct/ll)) for t in tops] if ll > 1e-9 else []
                    direction_state = 'pass' if directional and min(directional) > TOL else 'fail'
                self.add(role+'_slope', [e['name']], state, {'part_index': r['part_index'], 'geometry_min_slope': all_min, 'geometry_max_slope': all_max, 'minimum_required_slope': threshold, 'top_faces': len(tops), 'maximum_planarity_error_m': max(t['planarity_m'] for t in tops)}, clause, '坡值由几何顶面法向计算；不使用对象标注坡度')
                self.add(role+'_drain_direction', [e['name']], direction_state, {'direction_basis': direction_label if direction is not None else None, 'geometry_slope_in_required_direction': directional}, clause, '缺排水方向/出口配对时不能把坡度通过当作排水系统通过')

    def low_window_guards(self):
        sill_by_host = collections.defaultdict(list)
        for r in self.finishes('window_sill'):
            if r['element'].get('host'): sill_by_host[r['element']['host']].append(r)
        for e in self.elements:
            if not e['name'].startswith('CONSTRUCTION_LOW_SILL_GUARD_'): continue
            host = e.get('host'); host_parts = self.by_name.get(host, [])
            rr = [r for r in self.by_name[e['name']] if r['finished_surface'] is not True]
            if not host_parts or not rr:
                self.add('low_window_guard_height', [e['name'], host] if host else [e['name']], 'needs-design', {}, 'GB 55038-2025 4.1.16', '缺宿主窗口或防护实体')
                continue
            sill_tops = [float(t['points'][:, 2].max()) for r in sill_by_host[host] for t in top_faces(r)]
            if sill_tops:
                sill = max(sill_tops); basis = 'finished_exterior_sill_geometry'
            else:
                sill = min(float(r['lo'][2]) for r in host_parts); basis = 'host_window_geometry_lower_bound'
            guard_top = max(float(r['hi'][2]) for r in rr)
            bay = 'BAY' in str(host).upper()
            fm = re.search(r'_F(\d+)(?:_|$)', str(host))
            structural_floor = self.stair_surface_z('SLAB_JOINED_F'+fm.group(1)) if fm else None
            sill_above_structure = sill-structural_floor if structural_floor is not None else None
            # The 450 mm classification is provisional until the actual
            # internal finished floor and climbable sill/bench are surveyed.
            need = (.6 if sill_above_structure is not None and sill_above_structure > .45 else .9) if bay else None
            net = guard_top-sill if bay else guard_top-structural_floor if structural_floor is not None else None
            if not bay: need = .9
            state = 'needs-design' if net is None else 'pass' if net >= need-TOL else 'fail'
            self.add('low_window_guard_height', [e['name'], host], state,
                     {'geometry_guard_top_m': guard_top, 'geometry_sill_m': sill, 'sill_basis': basis,
                      'structural_floor_reference_m': structural_floor, 'sill_above_structural_floor_m': sill_above_structure,
                      'guard_above_geometric_reference_m': net, 'conditional_required_height_m': need, 'bay_window': bay},
                     '凸窗台<=450 mm时距窗台>=900 mm，>450 mm时>=600 mm；普通低窗防护距楼地面/可登踏面>=900 mm；GB 55038-2025 4.1.16',
                     '本行仅核几何窗台和护栏的限定关系；外侧坡窗台不证明室内可登踏面高度。凸窗台分类暂用结构楼板参照。')
            self.add('low_window_climbable_sill_and_anchorage', [e['name'], host], 'needs-design',
                     {'geometric_sill_basis': basis, 'internal_finished_floor_confirmed': False, 'internal_climbable_surface_confirmed': False},
                     'GB 55038-2025 4.1.16', '须复核室内完成面、窗台/坐凳可登踏面、窗框边近贴安装及防护连接；现有外侧窗台实体不能替代这些证据。')
            angle = float(e.get('angle', 0)); u = np.array([math.cos(angle), math.sin(angle), 0.])
            posts = []
            for r in rr:
                q = r['vertices'] @ u; w = float(q.max()-q.min()); h = float(r['hi'][2]-r['lo'][2])
                if h > .3 and w < .15: posts.append((float(q.min()), float(q.max()), r['part_index']))
            posts.sort(); gaps = [posts[j+1][0]-posts[j][1] for j in range(len(posts)-1)]
            largest = max(gaps) if gaps else None
            self.add('low_window_guard_post_clear_gaps', [e['name']], 'needs-design' if largest is None else 'pass' if largest <= .11+TOL else 'fail',
                     {'vertical_post_count': len(posts), 'geometric_clear_gaps_m': gaps, 'maximum_clear_gap_m': largest},
                     '竖杆净距<=110 mm；GB 55038-2025 4.1.16', '净距直接由竖杆左右几何面计算；不使用标称间距。')

    def doors(self):
        for e in self.elements:
            if e.get('layer') != '30_DOOR': continue
            rr = self.by_name[e['name']]
            if not rr: continue
            a = e.get('angle', 0); u = np.array([math.cos(a), math.sin(a), 0.])
            dd = [(r, r['vertices'] @ u) for r in rr]
            width = max(float(q.max()) for _, q in dd)-min(float(q.min()) for _, q in dd)
            height = max(r['hi'][2] for r in rr)-min(r['lo'][2] for r in rr)
            jambs = [(r, float(q.min()), float(q.max())) for r, q in dd if float(q.max()-q.min()) < width*.20 and r['hi'][2]-r['lo'][2] > height*.70]
            jambs.sort(key=lambda x: x[1])
            if len(jambs) < 2 or width > 2:
                self.add('door_frame_clear_width', [e['name']], 'needs-design', {'overall_geometric_width_m': width, 'jamb_candidates': len(jambs)}, 'GB 55038-2025 4.1.14', '滑门有效开启、门扇数量和五金行程未确定')
                continue
            clear = jambs[-1][1]-jambs[0][2]
            name = e['name'].upper()
            usage = e.get('door_usage')
            usage = usage or ('bedroom' if 'BED' in name else 'wetroom' if any(x in name for x in ('BATH', 'KITCHEN', 'BACKROOM')) else None)
            need = .8 if usage == 'bedroom' else .7 if usage in ('wetroom', 'bathroom', 'kitchen') else .9 if usage in ('entry', 'new_entry') else .8 if usage == 'existing_entry' else None
            state = 'needs-design' if need is None else 'pass' if clear >= need-TOL else 'fail'
            self.add('door_frame_clear_width', [e['name']], state, {'overall_geometric_width_m': width, 'between_jambs_m': clear, 'deducted_frame_total_m': width-clear, 'threshold_m': need, 'door_usage': usage, 'jamb_part_indices': [jambs[0][0]['part_index'], jambs[-1][0]['part_index']]}, 'GB 55038-2025 4.1.14', '门框之间几何净距；名义洞口/门扇宽度不作为通行净宽')
            self.add('door_opened_passage', [e['name']], 'needs-design', {'frame_clear_upper_bound_m': clear, 'opening_state': e.get('opening_state', 'closed-or-unknown')}, 'GB 55038-2025 4.1.14', '实际门扇开启角、门厚、把手和限位仍须核查；框内净距仅是最大通行净宽上界')

    def stair_surface_z(self, name):
        rr = self.by_name.get(name, [])
        vals = [float(t['points'][:, 2].max()) for r in rr for t in top_faces(r)]
        return max(vals) if vals else None

    def stairs(self):
        flights = []
        for e in self.elements:
            m = re.fullmatch(r'STAIR_F(\d+)_FLIGHT(\d+)', e['name'])
            if not m: continue
            floor, flight = map(int, m.groups()); rr = self.by_name[e['name']]
            stair = next((r for r in rr if r['geometry']['type'] == 'prism'), None)
            if not stair:
                self.add('stair_rise_uniformity', [e['name']], 'needs-design', {}, 'GB 55031-2022 5.3.10', '缺单一梯段截面实体')
                continue
            g = stair['geometry']; p = transformed(np.array(g['profile']), e)
            vec = np.array(g['vector'], float)
            a = e.get('angle', 0); c, s = math.cos(a), math.sin(a)
            lat = np.array([c*vec[0]-s*vec[1], s*vec[0]+c*vec[1], 0.]); body_width = np.linalg.norm(lat)
            lat /= body_width
            zstart = self.stair_surface_z(f'SLAB_JOINED_F{floor}' if flight == 1 else f'STAIR_LANDING_F{floor}')
            zend = self.stair_surface_z(f'STAIR_LANDING_F{floor}' if flight == 1 else f'SLAB_JOINED_F{floor+1}')
            missing_level = zstart is None or zend is None
            if zstart is None: zstart = float(e.get('z_from', p[1, 2]))
            if zend is None: zend = float(e.get('z_to', p[:, 2].max()))
            treads = []
            receiving_names = [f'STAIR_LANDING_F{floor}'] if flight == 1 else [f'SLAB_JOINED_F{floor+1}']
            for aa, bb in zip(p[:-1], p[1:]):
                # Ordered profile ascends from the first riser to the final
                # landing. The terminal bearing tongue and waist underside
                # appear afterwards and are not walking treads.
                if zstart+TOL < aa[2] < zend-TOL and abs(aa[2]-bb[2]) < 1e-7 and np.linalg.norm(aa[:2]-bb[:2]) > .05:
                    sample=(aa[:2]+bb[:2])/2+lat[:2]*body_width/2
                    cover=[top_at(r,sample) for n in receiving_names for r in self.by_name[n]]
                    if any(v is not None and v>aa[2]+TOL for v in cover):continue
                    treads.append((float(aa[2]), float(np.linalg.norm(aa[:2]-bb[:2]))))
            treads = sorted(treads)
            levels = [zstart]+sorted(set(round(z, 10) for z, _ in treads))+[zend]
            rises = np.diff(levels)
            spread = float(np.ptp(rises)) if len(rises) else None
            state = 'needs-design' if missing_level or not len(rises) else 'pass' if spread < 1e-6 else 'fail'
            self.add('stair_rise_uniformity', [e['name']], state, {'start_geometry_level_m': zstart, 'end_geometry_level_m': zend, 'riser_count': len(rises), 'riser_heights_m': rises.tolist(), 'riser_spread_m': spread, 'tread_depths_m': [d for _, d in treads], 'level_geometry_missing': missing_level}, '同一梯段踏步高宽一致；GB 55031-2022 5.3.10', '边界踢面以真实平台/楼板几何标高计算；缺几何标高才退用属性并标needs-design')
            body_interval = [float((stair['vertices'] @ lat).min()), float((stair['vertices'] @ lat).max())]
            lo, hi = stair['lo'], stair['hi']; occupied = []; rail_names = []
            for r in self.rec:
                ne = r['element']['name']
                if ne.startswith('STAIR_V4_RAIL_'):
                    if ne != f'STAIR_V4_RAIL_F{floor}_{flight}': continue
                elif not ne.startswith(('STAIR_HANDRAIL', 'STAIR_BALUSTER', 'CONSTRUCTION_STAIR')): continue
                if r['hi'][0] < lo[0]-.01 or r['lo'][0] > hi[0]+.01 or r['hi'][2] < lo[2] or r['lo'][2] > hi[2]+1.5: continue
                q = r['vertices'] @ lat; aa = max(body_interval[0], float(q.min())); bb = min(body_interval[1], float(q.max()))
                if bb-aa > TOL:
                    occupied.append([aa, bb]); rail_names.append(ne)
            occupied.sort(); merged = []
            for aa, bb in occupied:
                if merged and aa <= merged[-1][1]+TOL: merged[-1][1] = max(bb, merged[-1][1])
                else: merged.append([aa, bb])
            gaps = []; cursor = body_interval[0]
            for aa, bb in merged:
                if aa > cursor+TOL: gaps.append(aa-cursor)
                cursor = max(cursor, bb)
            if cursor < body_interval[1]-TOL: gaps.append(body_interval[1]-cursor)
            net = max(gaps) if gaps else 0.
            usage = e.get('stair_usage', 'private-house-interior-unconfirmed')
            self.add('stair_geometric_width_and_rail_occupancy', [e['name']], 'needs-design', {'body_width_geometry_m': float(body_width), 'proposed_body_width_m': self.proposed_width, 'body_matches_proposal': abs(body_width-self.proposed_width) < 1e-6, 'conservative_clear_width_m': net, 'rail_intrusion_m': float(body_width-net), 'occupying_elements': sorted(set(rail_names)), 'usage': usage}, '拟议本体宽1100 mm；通行净宽需扣除扶手/栏杆占用', '这是按整个梯段扶手占用包络计算的保守净宽，不是名义构件width。户内梯不直接套公共梯1.00/1.10 m规范下限，净宽及起止平台使用条件待设计确认。')
            flights.append((floor, flight, e, stair, lat))
        for floor in sorted(set(x[0] for x in flights)):
            pair = [x for x in flights if x[0] == floor]
            if len(pair) != 2: continue
            lat = pair[0][4]
            ints = sorted([[float((x[3]['vertices']@lat).min()), float((x[3]['vertices']@lat).max())] for x in pair])
            gap = ints[1][0]-ints[0][1]
            self.add('stair_pair_gap', [x[2]['name'] for x in pair], 'pass' if abs(gap-self.proposed_gap) < 1e-6 else 'fail', {'geometry_between_flights_m': gap, 'proposed_gap_m': self.proposed_gap}, '拟议1100/20布局参数核对；不是法规验收值', '两跑之间本体净距，不代替扶手间距、梯井防坠或人体净通行')

    def run(self):
        self.guards(); self.slopes(); self.low_window_guards(); self.doors(); self.stairs()
        return {'title': 'V4施工几何参数核查', 'scope': '直接展开源场景实体几何；未作结构验算、法定图审、现场测量或材料验收', 'status_meaning': {'pass': '本行限定几何值满足所列条件，不能推广成整个构件/工程合规', 'fail': '本行几何值不足或与拟议参数不符', 'needs-design': '缺对应几何/用途/开启状态/连接细部，或必须由设计核定'}, 'counts': dict(collections.Counter(x['status'] for x in self.result)), 'checks': self.result}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scene', required=True)
    ap.add_argument('--register')
    ap.add_argument('--out', default=str(Path(__file__).parent/'geometry_audit'))
    ap.add_argument('--proposed-stair-width', type=float, default=1.1)
    ap.add_argument('--proposed-stair-gap', type=float, default=.02)
    ns = ap.parse_args()
    scene = json.loads(Path(ns.scene).read_text(encoding='utf-8-sig'))
    report = Audit(scene, ns.register, ns.proposed_stair_width, ns.proposed_stair_gap).run()
    report['scene'] = str(Path(ns.scene).resolve()); report['register'] = ns.register
    out = Path(ns.out); out.mkdir(parents=True, exist_ok=True)
    # NumPy reductions may produce scalars even where a Python float is usually
    # expected. Normalize them once at the serialization boundary.
    report = json.loads(json.dumps(report, ensure_ascii=False, default=lambda x: x.item() if isinstance(x, np.generic) else x.tolist()))
    (out/'Construction_Geometry_QA_V4.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    with (out/'Construction_Geometry_Checks_V4.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['check', 'elements', 'status', 'measured', 'rule', 'note']); writer.writeheader()
        for row in report['checks']: writer.writerow({**row, 'elements': ' | '.join(row['elements']), 'measured': json.dumps(row['measured'], ensure_ascii=False)})
    print(json.dumps({'out': str(out.resolve()), 'counts': report['counts']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
