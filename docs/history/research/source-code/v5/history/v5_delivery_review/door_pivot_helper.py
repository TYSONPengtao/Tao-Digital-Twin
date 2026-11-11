"""Split a definition-based hinged door into real frame/hinge-rooted leaf instances.

Does not change the closed geometry, does not infer hinge side from a photograph,
and does not edit any source scene. Caller supplies the observed/proposed hinge.
"""
from copy import deepcopy
from math import cos, sin


def _subtract_pivot(geometry, pivot):
    g = deepcopy(geometry)
    typ = g['type']
    if typ in ('box', 'cylinder', 'lathe'):
        g['origin'] = [float(x) - p for x, p in zip(g['origin'], pivot)]
    elif typ == 'prism':
        g['profile'] = [[float(x) - p for x, p in zip(point, pivot)]
                        for point in g['profile']]
    elif typ == 'polyhedron' or typ == 'mesh':
        g['vertices'] = [[float(x) - p for x, p in zip(point, pivot)]
                         for point in g['vertices']]
    else:
        raise ValueError('Door pivot helper does not support ' + typ)
    return g


def split_hinged_door(scene, element, door_id, hinge_local, *,
                      leaf_indices=None, hinge_status='PROVISIONAL_NOT_FIELD_VERIFIED',
                      open_angle_deg=None, room_a=None, room_b=None):
    """Return [frame, leaf]; register two definitions, preserving closed geometry.

    `hinge_local` is in the original door definition coordinates (metres).
    `leaf_indices` can identify a composite glazed leaf; if omitted, the helper
    requires explicit `role=LEAF` parts or accepts only the legacy wood door's
    first part. Never call this for sliding doors.
    """
    original_key = element['definition']
    original = scene['definitions'][original_key]
    parts = original['parts']
    if 'SLID' in original_key.upper():
        raise ValueError('Sliding doors require translational leaf origins/travel')
    if leaf_indices is None:
        leaf_indices = [i for i, p in enumerate(parts) if p.get('role') == 'LEAF']
        if not leaf_indices and original_key in ('DOOR_W900_H2100_WOOD', 'DOOR_W800_H2100_WOOD'):
            leaf_indices = [0]
    leaf_indices = set(leaf_indices or [])
    if not leaf_indices or len(leaf_indices) == len(parts):
        raise ValueError('Explicit leaf and frame parts are both required')
    hinge = list(map(float, hinge_local))
    if len(hinge) != 3:
        raise ValueError('hinge_local must contain three metre coordinates')
    base = element.get('origin', [0, 0, 0])
    angle = element.get('angle', 0)
    c, s = cos(angle), sin(angle)
    hinge_world = [base[0] + c * hinge[0] - s * hinge[1],
                   base[1] + s * hinge[0] + c * hinge[1], base[2] + hinge[2]]
    assembly_id = element['name']
    common = {k: deepcopy(v) for k, v in element.items() if k not in ('parts', 'definition')}
    common.update(door_id=door_id, assembly_id=assembly_id,
                  hinge_status=hinge_status, room_a=room_a, room_b=room_b,
                  leaf_closed_angle_rad=angle, hinge_world_m=hinge_world,
                  hinge_axis_world=[0, 0, 1])
    frame, leaf = deepcopy(common), deepcopy(common)
    frame.update(name=assembly_id + '_FRAME', component_role='FRAME',
                 definition=assembly_id + '_FRAME_DEF', interaction='STATIC_FRAME')
    leaf.update(name=assembly_id + '_LEAF', component_role='LEAF',
                definition=assembly_id + '_LEAF_DEF', origin=hinge_world,
                interaction='ROTATE_ABOUT_LOCAL_Z', pivot_local_m=[0, 0, 0])
    if open_angle_deg is not None:
        leaf['open_angle_deg'] = float(open_angle_deg)
    else:
        leaf['open_angle_deg'] = None
    params = deepcopy(original.get('parameters', {}))
    for role, inst in [('FRAME', frame), ('LEAF', leaf)]:
        selected = []
        for i, part in enumerate(parts):
            if (i in leaf_indices) != (role == 'LEAF'):
                continue
            p = deepcopy(part)
            p['role'] = role
            if role == 'LEAF':
                p['geometry'] = _subtract_pivot(p['geometry'], hinge)
            selected.append(p)
        scene['definitions'][inst['definition']] = {
            'parts': selected,
            'parameters': {**params, 'DoorId': door_id, 'PartRole': role,
                           'PivotLocal': [0, 0, 0], 'HingeWorld': hinge_world},
            'source': original.get('source', element.get('source', '')),
            'confidence': original.get('confidence', element.get('confidence', 'MEDIUM'))}
    return [frame, leaf]


def validate_registration(scene):
    """Ensure each registered hinged door has exactly one frame and one leaf."""
    by_id = {}
    for element in scene['elements']:
        if element.get('component_role') in ('FRAME', 'LEAF'):
            by_id.setdefault(element['door_id'], []).append(element)
    for door_id, elements in by_id.items():
        assert len(elements) == 2 and {e['component_role'] for e in elements} == {'FRAME', 'LEAF'}, door_id
        leaf = next(e for e in elements if e['component_role'] == 'LEAF')
        assert leaf['origin'] == leaf['hinge_world_m'], door_id
        assert leaf['pivot_local_m'] == [0, 0, 0], door_id
        assert scene['definitions'][leaf['definition']]['parameters']['DoorId'] == door_id, door_id
    return len(by_id)
