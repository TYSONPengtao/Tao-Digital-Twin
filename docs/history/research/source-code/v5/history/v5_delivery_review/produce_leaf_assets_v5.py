import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from export_door_leaf_assets import export_door_leaf_assets
OUT=Path(r'E:\jz\JIA\Rebuild_V5');FOLDER=OUT/'08_Export/Door_Leaf_Assets'
scene=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(OUT/'08_Export/Production_1QK_ARCH.blend'))
records=export_door_leaf_assets(FOLDER)
assert len(records)==13
registry={r['door_id']:r for r in scene['door_registry']}
for r in records:
    r['connected_rooms']=registry[r['door_id']]['connected_rooms']
    r['dimensions_status']=registry[r['door_id']]['dimensions_status']
(FOLDER/'DoorPlacement.json').write_text(json.dumps({'units':'metres','axis':'right-handed Z-up project local',
  'source_scene':'../../05_Intermediate/Architecture_Scene.json',
  'placement':'Each asset is local with actual hinge origin [0,0,0]. Place at hinge_world_m and rotate by closed_angle_rad.',
  'handedness_status':'Provisional model interaction; requires field confirmation. Defaults closed.',
  'doors':records},indent=2,ensure_ascii=False),encoding='utf-8')
report=[]
for r in records:
    for ext in ['fbx','glb']:
        bpy.ops.wm.read_factory_settings(use_empty=True);p=FOLDER/r['asset_'+ext]
        if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(p))
        else:bpy.ops.import_scene.gltf(filepath=str(p))
        bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        assert len(meshes)==1,(p,'joined_mesh_count',len(meshes))
        ob=meshes[0];origin_error=ob.matrix_world.translation.length
        assert origin_error<1e-6 and ob.get('door_id')==r['door_id']
        points=[ob.matrix_world@v.co for v in ob.data.vertices]
        bb=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]]
        # A vertical meter-scaled leaf should be ~2.035m high and near pivot X=0.
        assert abs((bb[1][2]-bb[0][2])-2.035)<1e-5,(p,'height',bb)
        original=ob.matrix_world.copy();before=ob.matrix_world.translation.copy()
        ob.matrix_world=Matrix.Rotation(math.pi/2,4,'Z')@original;bpy.context.view_layer.update()
        hinge_move=(ob.matrix_world.translation-before).length
        rotated=[ob.matrix_world@v.co for v in ob.data.vertices]
        tip_move=max((a-b).length for a,b in zip(points,rotated))
        assert hinge_move<1e-6 and tip_move>.8
        assert ob.data.uv_layers and ob.data.materials
        report.append({'door_id':r['door_id'],'format':ext,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'mesh_count':1,'local_hinge_origin_error_m':origin_error,'height_m':bb[1][2]-bb[0][2],
          'hinge_movement_90deg_m':hinge_move,'furthest_vertex_movement_90deg_m':tip_move,
          'uv_and_materials_preserved':True,'door_id_preserved':True})
(OUT/'09_Report/Door_Leaf_Asset_Readback_V5.json').write_text(json.dumps({'pass':True,'doors':13,
  'asset_files':26,'readback':report,'scope':'Native FBX/GLB readback into Blender, hinge mesh origins and real 90deg movement; not UE application testing'},indent=2),encoding='utf-8')
print('V5 LOCAL HINGE ASSETS: 13 doors, 26 final files all PASS')
