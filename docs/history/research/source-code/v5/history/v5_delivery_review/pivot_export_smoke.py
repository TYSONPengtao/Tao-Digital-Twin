"""Readback experiment for real Blender FBX/GLB leaf origins, outside production."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from door_pivot_helper import split_hinged_door, validate_registration

src = json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
scene = {'definitions': src['definitions'], 'elements': []}
originals = [next(e for e in src['elements'] if e['name'] == 'DOOR_BED_F1_X3.9'),
             next(e for e in src['elements'] if e['name'] == 'DOOR_BED_F3_X9.1')]
for i, (e, local_hinge) in enumerate(zip(originals, ([.045, 0, 0], [.855, 0, 0])), 1):
    scene['elements'].extend(split_hinged_door(scene, e, 'PIVOT_TEST_D' + str(i), local_hinge))
assert validate_registration(scene) == 2

def box(g):
    x,y,z = g['origin'];w,d,h = g['size']
    v = [Vector(p) for p in [(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z),
                              (x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h)]]
    f = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return v,f

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1
expected = {}
equivalence = []
for e in scene['elements']:
    group = bpy.data.objects.new(e['name'], None)
    bpy.context.scene.collection.objects.link(group)
    group.location = e['origin'];group.rotation_euler[2] = e['angle']
    for k in ['door_id','component_role','assembly_id','hinge_status']:
        group[k] = e[k]
    for j,p in enumerate(scene['definitions'][e['definition']]['parts']):
        v,f = box(p['geometry']);data = bpy.data.meshes.new(e['name'] + str(j));data.from_pydata(v, [], f)
        ob = bpy.data.objects.new(e['name'] + '_PART' + str(j), data)
        bpy.context.scene.collection.objects.link(ob);ob.parent = group
        ob['door_id'] = e['door_id'];ob['component_role'] = e['component_role']
    if e['component_role'] == 'LEAF':expected[e['name']] = e['origin']
bpy.context.view_layer.update()
for old in originals:
    oldverts = []
    R=Matrix.Rotation(old['angle'],3,'Z');T=Vector(old['origin'])
    for p in src['definitions'][old['definition']]['parts']:
        v,f=box(p['geometry']);oldverts.extend(R@q+T for q in v)
    newverts = [ob.matrix_world@v.co for ob in bpy.context.scene.objects
                if ob.type == 'MESH' and ob.name.startswith(old['name']) for v in ob.data.vertices]
    err=max(min((p-q).length for q in newverts) for p in oldverts)
    assert err < 1e-6, err
    equivalence.append({'door':old['name'],'closed_world_geometry_max_error_m':err})

bpy.ops.object.select_all(action='SELECT')
fbx=HERE/'pivot_smoke.fbx';glb=HERE/'pivot_smoke.glb'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,global_scale=1,apply_unit_scale=True,
                        axis_forward='-Y',axis_up='Z',object_types={'MESH','EMPTY'},
                        bake_anim=False,add_leaf_bones=False,use_custom_props=True)
bpy.ops.export_scene.gltf(filepath=str(glb),use_selection=True,export_format='GLB',export_extras=True)
report = {'scope':'Two-door synthetic export/readback using unchanged V4 closed geometry; not a production model validation',
          'closed_equivalence':equivalence,'formats':{}}
for ext,p in [('fbx',fbx),('glb',glb)]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(p))
    else:bpy.ops.import_scene.gltf(filepath=str(p))
    bpy.context.view_layer.update();results=[]
    for name,hinge in expected.items():
        group=bpy.data.objects.get(name);assert group is not None,name
        leafs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.parent==group]
        assert leafs,name
        group_err=(group.matrix_world.translation-Vector(hinge)).length
        mesh_err=max((o.matrix_world.translation-Vector(hinge)).length for o in leafs)
        assert max(group_err,mesh_err)<1e-5,(ext,name,group_err,mesh_err)
        assert group['component_role']=='LEAF' and 'door_id' in group,(ext,name,'metadata')
        before=[o.matrix_world@v.co for o in leafs for v in o.data.vertices]
        fixed_before=group.matrix_world@Vector((0,0,0))
        # glTF is Y-up; after roundtrip local node axes may retain that encoding.
        # Rotate the node in the preserved world Z hinge axis, not Euler.z.
        T=Matrix.Translation(fixed_before)
        group.matrix_world=T@Matrix.Rotation(math.pi/2,4,'Z')@T.inverted()@group.matrix_world
        bpy.context.view_layer.update()
        fixed_after=group.matrix_world@Vector((0,0,0))
        after=[o.matrix_world@v.co for o in leafs for v in o.data.vertices]
        hinge_move=(fixed_after-fixed_before).length
        tip_move=max((a-b).length for a,b in zip(after,before))
        assert hinge_move<1e-6 and tip_move>.8,(ext,name,'rotation')
        world_axis=(group.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        results.append({'leaf':name,'DoorId':group['door_id'],'group_origin_error_m':group_err,
                        'mesh_origin_error_m':mesh_err,'hinge_moved_after_90deg_m':hinge_move,
                        'furthest_leaf_vertex_moved_m':tip_move,
                        'imported_local_z_axis_world':list(world_axis)})
    report['formats'][ext]=results
(HERE/'Pivot_Export_Readback.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
