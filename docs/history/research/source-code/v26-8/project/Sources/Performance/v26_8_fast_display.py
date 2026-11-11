"""Session-local interactive display budget. Original meshes and textures stay intact."""
import bpy


def assign_enum(obj, name, preferred):
    if not hasattr(obj, name):
        return None
    prop = obj.bl_rna.properties.get(name)
    if prop is None:
        return None
    choices = [i.identifier for i in prop.enum_items]
    chosen = next((v for v in preferred if v in choices), None)
    if chosen is not None:
        setattr(obj, name, chosen)
    return chosen


def apply(scene=None):
    sc = scene or bpy.context.scene
    changes = {}
    # This preference is process-local: never save the user's global preferences.
    changes['viewport_texture_limit'] = assign_enum(
        bpy.context.preferences.system, 'gl_texture_limit', ['CLAMP_2048', '2048'])
    changes['preview_pixel_size'] = assign_enum(sc.render, 'preview_pixel_size', ['2'])
    if hasattr(bpy.context.preferences.view, 'show_splash'):
        bpy.context.preferences.view.show_splash = False
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        pass
    if hasattr(sc, 'eevee'):
        ev = sc.eevee
        for n, v in [('taa_samples', 8), ('use_raytracing', False),
                     ('use_shadow_jitter_viewport', False), ('use_fast_gi', False),
                     ('shadow_resolution_scale', .5), ('volumetric_samples', 16)]:
            if hasattr(ev, n):
                setattr(ev, n, v)
        assign_enum(ev, 'shadow_pool_size', ['128', '256'])
    # Fill lights approximate overcast ambient light; they do not need 23 shadow maps.
    # Retain the entrance area light's shadow for grounding the image.
    shadow_lights = []
    for ob in sc.objects:
        if ob.type != 'LIGHT':
            continue
        ob.data.use_shadow = ob.name == 'V20_INSPECTION_Gate_Soffit'
        if ob.data.use_shadow and ob.data.energy > 0:
            shadow_lights.append(ob.name)
    changes['shadow_lights'] = shadow_lights
    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type != 'VIEW_3D':
                    continue
                shade = space.shading
                shade.type = 'MATERIAL'
                shade.use_scene_lights = True
                shade.use_scene_world = True
                shade.use_dof = False
                space.overlay.show_overlays = False
                if hasattr(space, 'show_gizmo'):
                    space.show_gizmo = False
                space.clip_end = 180.
    changes['engine'] = sc.render.engine
    changes['geometry_modified'] = False
    changes['texture_pixels_modified'] = False
    return changes


if __name__ == '__main__':
    print('FAST_DISPLAY', apply(), flush=True)
