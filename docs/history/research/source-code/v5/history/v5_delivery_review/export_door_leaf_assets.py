"""Optional Blender helper: single door-leaf meshes with true origin at hinge.

Call only after production scene has been built and group metadata added.
Does not alter originals. Each asset is local and closed; placement is external.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector


def export_door_leaf_assets(asset_directory):
    folder = Path(asset_directory)
    folder.mkdir(parents=True, exist_ok=True)
    previous_active = bpy.context.view_layer.objects.active
    previous_selection = list(bpy.context.selected_objects)
    records = []
    leaves = [o for o in bpy.context.scene.objects
              if o.type == 'EMPTY' and (o.get('component_role') or o.get('role')) == 'LEAF']
    for group in leaves:
        source = [o for o in group.children if o.type == 'MESH']
        if not source:
            raise ValueError('Leaf group contains no mesh: ' + group.name)
        door_id = str(group['door_id'])
        if any(ch in door_id for ch in '/\\:*?"<>|'):
            raise ValueError('Door ID is not suitable for an asset filename: ' + door_id)
        duplicates = []
        for ob in source:
            dup = ob.copy()
            dup.data = ob.data.copy()
            # Parent-local geometry and transform stay; worldwide placement is removed.
            dup.parent = None
            dup.matrix_world = ob.matrix_local.copy()
            bpy.context.scene.collection.objects.link(dup)
            duplicates.append(dup)
        bpy.ops.object.select_all(action='DESELECT')
        for ob in duplicates:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = duplicates[0]
        bpy.ops.object.join()
        asset = bpy.context.view_layer.objects.active
        asset.name = door_id + '_LEAF_ASSET'
        # Source child transforms are required to have their origin at the hinge.
        if asset.location.length > 1e-6:
            raise ValueError('Source leaf mesh did not have a hinge local origin: ' + group.name)
        asset['door_id'] = door_id
        asset['component_role'] = 'LEAF'
        asset['pivot_local_m'] = '[0,0,0]'
        asset['interaction_axis_local'] = 'Z'
        fbx_path=folder/(door_id+'_LEAF.fbx');glb_path=folder/(door_id+'_LEAF.glb')
        bpy.ops.export_scene.fbx(filepath=str(fbx_path),use_selection=True,
            global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',
            object_types={'MESH'},bake_anim=False,add_leaf_bones=False,use_custom_props=True)
        bpy.ops.export_scene.gltf(filepath=str(glb_path),use_selection=True,
            export_format='GLB',export_extras=True)
        hinge = list(group.matrix_world.translation)
        xaxis = group.matrix_world.to_3x3() @ Vector((1,0,0))
        record = {'door_id':door_id,'source_element':group.name,
                  'asset_fbx':fbx_path.name,'asset_glb':glb_path.name,
                  'hinge_world_m':hinge,'closed_angle_rad':math.atan2(xaxis.y,xaxis.x),
                  'hinge_axis_world':[0,0,1],'hinge_status':str(group.get('hinge_status','UNCONFIRMED')),
                  'room_a':str(group.get('room_a','')),'room_b':str(group.get('room_b',''))}
        if 'Parameters' in group:
            params=json.loads(group['Parameters'])
            record['swing_status']=params.get('swing_status','Proposed; not field confirmed')
            record['proposed_open_angle_deg']=params.get('open_angle_degrees_provisional')
        records.append(record)
        mesh = asset.data
        bpy.data.objects.remove(asset,do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in previous_selection:
        if ob.name in bpy.data.objects:
            ob.select_set(True)
    bpy.context.view_layer.objects.active = previous_active
    (folder/'DoorPlacement.json').write_text(json.dumps({
        'units':'metres','axis':'right-handed Z-up project local',
        'leaf_assets':'mesh origin lies on hinge; place by hinge_world_m, rotate by closed_angle_rad',
        'doors':records},ensure_ascii=False,indent=2),encoding='utf-8')
    return records
