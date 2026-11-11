"""Bounded Blender-only sculpt pass on the compact V23 gate's wing ornaments.

No scene loading/saving, Rhino writes or GLB exports occur in this module.
The original ceramic material slots and the parent hierarchy are preserved.
"""
import json, math
from pathlib import Path


def apply_v24_sculpt(bpy, output_dir):
    import bmesh
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    node = 'SITE_V21_GATE_REFERENCE_LAYER_14'
    source = bpy.data.objects.get(node + '_Geometry')
    if source is None or source.type != 'MESH':
        raise RuntimeError('Missing compact V23 gate wing/ridge mesh: ' + node)
    if bpy.data.objects.get(node + '_V24_Sculpted_Wings'):
        raise RuntimeError('V24 wing sculpt is already applied; reload the V23 source before rerunning.')

    bm = bmesh.new(); bm.from_mesh(source.data)
    before_unwelded = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    bm.normal_update()
    mw = source.matrix_world.copy(); inv = mw.inverted()
    matrix = np.asarray(mw, dtype=float)
    invmatrix = np.asarray(inv, dtype=float)

    # Native readback stores disconnected closed solids in one mesh. Isolate
    # only the four front wing/ridge fin solids; the 34 ridge copings stay put.
    remaining = set(bm.verts); selected = set(); components = []
    while remaining:
        root = remaining.pop(); stack = [root]; component = {root}
        while stack:
            v = stack.pop()
            for edge in v.link_edges:
                other = edge.other_vert(v)
                if other in remaining:
                    remaining.remove(other); component.add(other); stack.append(other)
        pts = np.asarray([tuple(mw @ v.co) for v in component])
        centre = pts.mean(0)
        is_wing = centre[1] < -12.05 and abs(centre[0] - 6.6) > 1.8
        components.append({'vertices': len(component), 'selected_wing': bool(is_wing),
                           'bbox': [pts.min(0).tolist(), pts.max(0).tolist()]})
        if is_wing: selected.update(v.index for v in component)
    if not selected:
        bm.free(); raise RuntimeError('No registered compact wing components were found.')

    kept = bm.copy(); sculpt = bm.copy(); bm.free()
    for mesh in [kept, sculpt]:
        mesh.verts.ensure_lookup_table(); mesh.verts.index_update()
    bmesh.ops.delete(kept, geom=[v for v in kept.verts if v.index in selected], context='VERTS')
    bmesh.ops.delete(sculpt, geom=[v for v in sculpt.verts if v.index not in selected], context='VERTS')
    sculpt.verts.ensure_lookup_table(); sculpt.verts.index_update(); sculpt.normal_update()
    original = np.asarray([tuple(mw @ v.co) for v in sculpt.verts])
    original_faces = [[v.index for v in f.verts] for f in sculpt.faces]
    bvh = BVHTree.FromPolygons([Vector(p) for p in original], original_faces, all_triangles=False)
    lo, hi = original.min(0), original.max(0)
    original_volume = abs(sculpt.calc_volume(signed=True))

    def weight(world):
        # Protect the entire bearing skirt at the ceramic carrier. At X=4.3
        # and X=8.9 the shallow refitted eave is about Z=3.07 m. Everything
        # within 35 mm of this envelope remains an exact, unmoved anchor.
        x, y, z = world
        t = min(1., abs(x - 6.6) / (.87 * 2.6547619))
        carrier = 2.8093 + .37 * (.077 * t*t + .638 * t**7)
        inner = min(1., max(0., (abs(x - 6.6) - 1.86) / .30))
        upper = min(1., max(0., (z - carrier - .035) / .055))
        # The outer tips extend beyond the carrier and can be rounded safely.
        outer = min(1., max(0., (abs(x - 6.6) - 2.29) / .15))
        w = inner * max(upper, outer)
        return w*w*(3.-2.*w)

    eligible = []
    for edge in sculpt.edges:
        if not edge.is_manifold: continue
        if edge.calc_face_angle(0.) < .42: continue
        if min(weight(mw @ v.co) for v in edge.verts) > .08: eligible.append(edge)
    if eligible:
        bmesh.ops.bevel(sculpt, geom=eligible, offset=.0032, segments=3,
                        affect='EDGES', profile=.55, clamp_overlap=True)
    sculpt.verts.ensure_lookup_table(); sculpt.verts.index_update()
    # Actual topology, not an unapplied smooth modifier: each selected fin is
    # subdivided into a dense brush-editable surface before the sculpt kernel.
    if len(sculpt.verts) < 30000:
        bmesh.ops.subdivide_edges(sculpt, edges=list(sculpt.edges), cuts=1,
                                 use_grid_fill=True, smooth=0.)
    sculpt.verts.ensure_lookup_table(); sculpt.verts.index_update(); sculpt.normal_update()
    if len(sculpt.verts) > 70000:
        raise RuntimeError('Wing sculpt topology exceeded the local vertex budget.')
    positions = np.asarray([tuple(mw @ v.co) for v in sculpt.verts])
    initial = positions.copy()
    normals = np.asarray([tuple(v.normal) for v in sculpt.verts]) @ invmatrix[:3, :3]
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-12)
    weights = np.asarray([weight(p) for p in positions])
    edges = np.asarray([[e.verts[0].index, e.verts[1].index] for e in sculpt.edges], dtype=np.int64)
    counts = np.zeros(len(positions))
    np.add.at(counts, edges[:, 0], 1.); np.add.at(counts, edges[:, 1], 1.)
    counts = np.maximum(counts, 1.)

    # Smooth/relax followed by a very shallow, deterministic inflate pass.
    # Every moved vertex is bounded to 4.5 mm and the original compact envelope.
    for iteration in range(6):
        sums = np.zeros_like(positions)
        np.add.at(sums, edges[:, 0], positions[edges[:, 1]])
        np.add.at(sums, edges[:, 1], positions[edges[:, 0]])
        laplace = sums / counts[:, None] - positions
        positions += .24 * weights[:, None] * laplace
        delta = positions - initial
        lengths = np.linalg.norm(delta, axis=1)
        positions = initial + delta * np.minimum(1., .0045 / np.maximum(lengths, 1e-12))[:, None]
    phase = np.sin(initial[:, 0]*31. + initial[:, 2]*19.) * np.sin(initial[:, 1]*23. - initial[:, 2]*17.)
    positions += normals * (.00055 * weights * phase)[:, None]
    delta = positions-initial
    lengths = np.linalg.norm(delta, axis=1)
    positions = initial + delta * np.minimum(1., .0045 / np.maximum(lengths, 1e-12))[:, None]
    positions = np.minimum(np.maximum(positions, lo), hi)
    anchors = weights < 1e-12
    positions[anchors] = initial[anchors]
    local = positions @ invmatrix[:3, :3].T + invmatrix[:3, 3]
    for vert, co in zip(sculpt.verts, local): vert.co = co
    sculpt.normal_update()
    for face in sculpt.faces: face.smooth = True
    for edge in sculpt.edges:
        edge.smooth = not (edge.is_manifold and edge.calc_face_angle(0.) > .80)
    boundaries = sum(not e.is_manifold for e in sculpt.edges)
    volume = abs(sculpt.calc_volume(signed=True))
    if boundaries or volume <= 0:
        raise RuntimeError('Sculpted wing lost its closed solid topology.')

    # Keep all original material slots and loop UV where topology permits;
    # bevel/subdivision interpolate those coordinates onto the new faces.
    wing_mesh = source.data.copy(); wing_mesh.name = node + '_V24_Dense_Sculpt_Mesh'
    sculpt.to_mesh(wing_mesh); wing_mesh.update(); sculpt.free()
    kept.to_mesh(source.data); source.data.update(); kept.free()
    wing = bpy.data.objects.new(node + '_V24_Sculpted_Wings', wing_mesh)
    for collection in source.users_collection: collection.objects.link(wing)
    wing.parent = source.parent; wing.matrix_parent_inverse = source.matrix_parent_inverse.copy()
    wing.matrix_world = mw
    wing['Geometry_Provenance'] = 'Actual compact V23 Rhino readback wing solids; Blender-only bounded sculpt pass'
    wing['Protected_Carrier_Contact_Zone'] = 'Unmoved lower bearing skirt and inner roots; 4.5 mm smoothing cap'
    wing['Sculpt_Method'] = 'Local weld, eligible-edge bevel, actual subdivision, six smooth/relax iterations, shallow inflate'

    # A SIMPLE Multires level gives further sculpting resolution without
    # shrinking the bearing skirt or changing the compact silhouette.
    previous_active = bpy.context.view_layer.objects.active
    previous_selection = list(bpy.context.selected_objects)
    for ob in previous_selection: ob.select_set(False)
    wing.select_set(True); bpy.context.view_layer.objects.active = wing
    multi = wing.modifiers.new('V24_Editable_Sculpt_Multires', 'MULTIRES')
    multires_error = None
    try:
        if len(wing_mesh.vertices) < 45000:
            bpy.ops.object.multires_subdivide(modifier=multi.name, mode='SIMPLE')
            multi.levels = 1; multi.sculpt_levels = 1; multi.render_levels = 1
        else:
            multi.levels = 0; multi.sculpt_levels = 0; multi.render_levels = 0
    except Exception as err:
        multires_error = str(err)
    for ob in bpy.context.selected_objects: ob.select_set(False)
    for ob in previous_selection:
        if ob.name in bpy.data.objects: ob.select_set(True)
    bpy.context.view_layer.objects.active = previous_active

    movements = np.linalg.norm(positions-initial, axis=1)
    nearest = [bvh.find_nearest(Vector(p))[3] for p in positions]
    nearest = [d for d in nearest if d is not None]
    report = {
        'status': 'PASS_BLENDER_SCULPT_GEOMETRY', 'scope': [wing.name],
        'source_node': node, 'material_slots': [m.name if m else None for m in wing_mesh.materials],
        'original_unwelded_layer_vertices': before_unwelded,
        'selected_original_vertices': len(original), 'base_sculpt_vertices': len(wing_mesh.vertices),
        'base_sculpt_faces': len(wing_mesh.polygons), 'original_components': components,
        'eligible_edges_bevelled': len(eligible), 'moved_dense_vertices': int((movements>1e-7).sum()),
        'max_kernel_vertex_displacement_m': float(movements.max()),
        'max_surface_distance_from_original_m': float(max(nearest) if nearest else 0.),
        'protected_anchor_vertices': int(anchors.sum()),
        'max_anchor_displacement_m': float(movements[anchors].max()) if anchors.any() else 0.,
        'before_bbox': [lo.tolist(), hi.tolist()],
        'after_bbox': [positions.min(0).tolist(), positions.max(0).tolist()],
        'closed_manifold': boundaries == 0, 'before_volume_m3': original_volume,
        'after_volume_m3': volume, 'volume_ratio': volume/original_volume,
        'uv_layers': [uv.name for uv in wing_mesh.uv_layers],
        'multires_levels': int(multi.total_levels), 'multires_error': multires_error,
        'preserved': ['compact outer envelope', 'bearing skirt anchors', 'ridge coping pieces',
                      'original ceramic materials', 'parent hierarchy', 'all other gate/site objects'],
        'runtime_UE_tested': False,
    }
    if report['moved_dense_vertices'] < 10:
        raise RuntimeError('The sculpt kernel did not produce a meaningful geometric change.')
    (out/'V24_Wing_Sculpt_Report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    return report
