from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / 'demo-house.blend'
GLB_PATH = ROOT / 'demo-house-from-blender.glb'

# Reset
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)

# Helpers

def mat(name, color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.65
    return m

def add_box(name, size, center, material):
    bpy.ops.mesh.primitive_cube_add(size=2, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

def add_cylinder(name, radius, height, center, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=height, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def add_sphere(name, radius, center, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# Colors
M_WALL = mat('MAT_Wall', (0.68, 0.74, 0.80))
M_LIVING = mat('MAT_LivingFloor', (0.42, 0.53, 0.64))
M_BED = mat('MAT_BedFloor', (0.62, 0.51, 0.39))
M_KITCHEN = mat('MAT_KitchenFloor', (0.45, 0.58, 0.42))
M_BALCONY = mat('MAT_BalconyFloor', (0.42, 0.52, 0.40))
M_DARK = mat('MAT_Dark', (0.05, 0.08, 0.12))
M_MID = mat('MAT_Mid', (0.20, 0.31, 0.42))
M_WOOD = mat('MAT_Wood', (0.48, 0.30, 0.18))
M_SOFA = mat('MAT_Sofa', (0.18, 0.30, 0.40))
M_BEDC = mat('MAT_Bed', (0.32, 0.42, 0.55))
M_GREEN = mat('MAT_Green', (0.12, 0.50, 0.24))
M_YELLOW = mat('MAT_DeviceLight', (1.00, 0.72, 0.16))
M_BLUE = mat('MAT_DeviceBlue', (0.12, 0.42, 0.90))
M_RED = mat('MAT_DeviceRed', (0.78, 0.18, 0.18))
M_WHITE = mat('MAT_White', (0.88, 0.92, 0.95))

W, D = 12.0, 8.0
wall_t, wall_h, floor_t = 0.16, 2.8, 0.10

# Room floors
add_box('ROOM_LivingRoom_Floor', (5.92, 4.92, floor_t), (-3.0, 1.5, floor_t/2), M_LIVING)
add_box('ROOM_Bedroom_Floor',    (5.92, 2.92, floor_t), (-3.0, -2.5, floor_t/2), M_BED)
add_box('ROOM_Kitchen_Floor',    (5.92, 4.92, floor_t), ( 3.0, -1.5, floor_t/2), M_KITCHEN)
add_box('ROOM_Balcony_Floor',    (5.92, 2.92, floor_t), ( 3.0,  2.5, floor_t/2), M_BALCONY)

# Exterior walls
add_box('WALL_North', (W, wall_t, wall_h), (0,  D/2-wall_t/2, wall_h/2), M_WALL)
add_box('WALL_South', (W, wall_t, wall_h), (0, -D/2+wall_t/2, wall_h/2), M_WALL)
add_box('WALL_West',  (wall_t, D, wall_h), (-W/2+wall_t/2, 0, wall_h/2), M_WALL)
add_box('WALL_East',  (wall_t, D, wall_h), ( W/2-wall_t/2, 0, wall_h/2), M_WALL)

# Interior walls with gaps
add_box('WALL_Center_Upper', (wall_t, 2.7, wall_h), (0, 2.55, wall_h/2), M_WALL)
add_box('WALL_Center_Mid',   (wall_t, 1.8, wall_h), (0, 0.1, wall_h/2), M_WALL)
add_box('WALL_Center_Lower', (wall_t, 1.8, wall_h), (0,-2.95, wall_h/2), M_WALL)
add_box('WALL_Left_H_A', (2.25, wall_t, wall_h), (-4.80, -1.0, wall_h/2), M_WALL)
add_box('WALL_Left_H_B', (2.55, wall_t, wall_h), (-1.28, -1.0, wall_h/2), M_WALL)
add_box('WALL_Right_H_A', (2.10, wall_t, wall_h), (1.15, 1.0, wall_h/2), M_WALL)
add_box('WALL_Right_H_B', (2.70, wall_t, wall_h), (4.65, 1.0, wall_h/2), M_WALL)

# Furniture
add_box('FURN_Sofa_Living', (2.4, 0.85, 0.72), (-3.8, 1.1, 0.36), M_SOFA)
add_box('FURN_CoffeeTable_Living', (1.2, 0.7, 0.38), (-3.7, 2.2, 0.19), M_WOOD)
add_box('FURN_TVStand_Living', (1.8, 0.45, 0.45), (-0.95, 2.6, 0.225), M_DARK)
add_box('FURN_Bed_Bedroom', (2.1, 1.6, 0.55), (-3.7, -2.6, 0.275), M_BEDC)
add_box('FURN_BedHead_Bedroom', (0.15, 1.6, 1.0), (-4.75, -2.6, 0.5), M_MID)
add_box('FURN_Nightstand_Bedroom', (0.55, 0.55, 0.55), (-2.35, -3.25, 0.275), M_WOOD)
add_box('FURN_Counter_Kitchen_A', (3.4, 0.65, 0.90), (2.9, -3.35, 0.45), M_WOOD)
add_box('FURN_Counter_Kitchen_B', (0.65, 2.0, 0.90), (5.25, -2.45, 0.45), M_WOOD)
add_box('FURN_Table_Kitchen', (1.4, 0.85, 0.75), (2.0, -1.3, 0.375), M_MID)
add_box('FURN_Planter_Balcony_A', (1.7, 0.55, 0.45), (2.0, 3.35, 0.225), M_WOOD)
add_box('FURN_Planter_Balcony_B', (1.7, 0.55, 0.45), (4.2, 3.35, 0.225), M_WOOD)
for i, x in enumerate([1.5, 2.0, 2.5, 3.7, 4.2, 4.7], start=1):
    add_cylinder(f'PLANT_{i:02d}', 0.12, 0.55, (x, 3.35, 0.73), M_GREEN, 16)

# Interactive devices
add_cylinder('DEV_Light_Living_Main', 0.35, 0.12, (-3.0, 1.5, 2.55), M_YELLOW)
add_box('DEV_TV_Living', (1.45, 0.10, 0.82), (-0.95, 2.78, 1.15), M_DARK)
add_box('DEV_Curtain_Living', (0.10, 2.0, 1.75), (-5.78, 1.55, 1.25), M_BLUE)
add_cylinder('DEV_Light_Bedroom', 0.30, 0.12, (-3.0, -2.4, 2.55), M_YELLOW)
add_box('DEV_AC_Bedroom', (1.15, 0.30, 0.38), (-3.0, -3.70, 2.15), M_WHITE)
add_cylinder('DEV_Light_Kitchen', 0.30, 0.12, (3.0, -1.4, 2.55), M_YELLOW)
add_cylinder('DEV_SmokeSensor_Kitchen', 0.18, 0.08, (4.25, -1.0, 2.62), M_RED, 24)
add_cylinder('DEV_Irrigation_Balcony', 0.18, 0.55, (3.1, 3.25, 0.40), M_BLUE, 24)
add_sphere('DEV_Irrigation_Balcony_Nozzle', 0.14, (3.1, 3.25, 0.76), M_BLUE)

# Organize into collections by prefixes
collections = {}
for cname in ['ROOMS', 'WALLS', 'FURNITURE', 'DEVICES', 'PLANTS']:
    col = bpy.data.collections.get(cname) or bpy.data.collections.new(cname)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    collections[cname] = col

for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('ROOM_'): target='ROOMS'
    elif obj.name.startswith('WALL_'): target='WALLS'
    elif obj.name.startswith('FURN_'): target='FURNITURE'
    elif obj.name.startswith('DEV_'): target='DEVICES'
    elif obj.name.startswith('PLANT_'): target='PLANTS'
    else: continue
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collections[target].objects.link(obj)

# Save source and export runtime model
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format='GLB',
    export_apply=True,
    export_yup=True,
)
print('Saved:', BLEND_PATH)
print('Exported:', GLB_PATH)
