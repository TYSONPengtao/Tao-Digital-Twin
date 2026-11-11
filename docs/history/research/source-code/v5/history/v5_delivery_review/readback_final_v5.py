"""Inspect final ARCH/VIS FBX+GLB exports: actual origins, IDs, leaf rotations."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(r'E:\jz\JIA\Rebuild_V5')
S=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
E={e['name']:e for e in S['elements']}
R=[r for r in S['door_registry'] if r.get('leaf_element')]

def bounds(points):
    return [[min(p[k] for p in points) for k in range(3)],
            [max(p[k] for p in points) for k in range(3)]]

def expected_points(e):
    result=[];R=Matrix.Rotation(e['angle'],3,'Z');T=Vector(e['origin'])
    for part in S['definitions'][e['definition']]['parts']:
        g=part['geometry'];assert g['type']=='box'
        x,y,z=g['origin'];w,d,h=g['size']
        result.extend(R@Vector((xx,yy,zz))+T
                      for xx in [x,x+w] for yy in [y,y+d] for zz in [z,z+h])
    return result

report={'scope':'Actual final V5 ARCH/VIS FBX+GLB imported into Blender; real hierarchy origins, closed leaf bounds and 90deg world hinge rotation tested. Does not validate UE import settings or real-world swing handedness.',
        'scene_sha256':hashlib.sha256((OUT/'05_Intermediate/Architecture_Scene.json').read_bytes()).hexdigest(),
        'registered_hinged_doors':len(R),'formats':{},'failures':[]}
for mode in ['ARCH','VIS']:
    for ext in ['fbx','glb']:
        p=OUT/'08_Export'/f'Production_1QK_{mode}.{ext}'
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(p))
        else:bpy.ops.import_scene.gltf(filepath=str(p))
        bpy.context.view_layer.update();rows=[]
        for reg in R:
            e=E[reg['leaf_element']];g=bpy.data.objects.get(e['name'])
            assert g is not None,(mode,ext,e['name'],'missing_group')
            children=[o for o in g.children if o.type=='MESH']
            assert children,(mode,ext,e['name'],'missing_mesh')
            expected=Vector(reg['hinge_world_m'])
            pivot_error=(g.matrix_world.translation-expected).length
            mesh_error=max((o.matrix_world.translation-expected).length for o in children)
            assert max(pivot_error,mesh_error)<1e-5,(mode,ext,e['name'],'pivot',pivot_error,mesh_error)
            assert g.get('door_id')==reg['door_id'] and g.get('role')=='LEAF',(mode,ext,e['name'],'metadata')
            frame=bpy.data.objects.get(reg['frame_element'])
            assert frame is not None and frame.get('role')=='FRAME' and frame.get('door_id')==reg['door_id'],(mode,ext,e['name'],'frame_registration')
            actual_points=[o.matrix_world@v.co for o in children for v in o.data.vertices]
            actual_bounds=bounds(actual_points);expected_bounds=bounds(expected_points(e))
            bound_error=max(abs(actual_bounds[i][j]-expected_bounds[i][j]) for i in range(2) for j in range(3))
            assert bound_error<1e-5,(mode,ext,e['name'],'closed_bounds',bound_error)
            parameters=json.loads(g['Parameters'])
            assert parameters['door_id']==reg['door_id'] and parameters['pivot_local_m']==[0,0,0]
            original=g.matrix_world.copy();hinge_before=g.matrix_world.translation.copy()
            sign=1 if e['open_angle_degrees_provisional']>0 else -1
            T=Matrix.Translation(hinge_before)
            g.matrix_world=T@Matrix.Rotation(sign*math.pi/2,4,'Z')@T.inverted()@original
            bpy.context.view_layer.update()
            hinge_move=(g.matrix_world.translation-hinge_before).length
            after=[o.matrix_world@v.co for o in children for v in o.data.vertices]
            tip_move=max((a-b).length for a,b in zip(actual_points,after))
            assert hinge_move<3e-6 and tip_move>.8,(mode,ext,e['name'],'90deg_rotation',hinge_move,tip_move)
            g.matrix_world=original;bpy.context.view_layer.update()
            rows.append({'door_id':reg['door_id'],'frame':frame.name,'leaf':g.name,'leaf_mesh_parts':len(children),
                         'hinge_world_m':list(hinge_before),'origin_error_m':pivot_error,'mesh_origin_error_m':mesh_error,
                         'closed_bounds_error_m':bound_error,'hinge_moved_90deg_m':hinge_move,
                         'furthest_leaf_vertex_moved_90deg_m':tip_move,'door_id_and_role_preserved':True,
                         'swing_status':'Proposed model interaction, not field confirmed'})
        report['formats'][mode+'_'+ext]={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
           'doors_passed':len(rows),'max_origin_error_m':max(r['origin_error_m'] for r in rows),
           'max_closed_bounds_error_m':max(r['closed_bounds_error_m'] for r in rows),'results':rows}
        print('FINAL PIVOT READBACK',mode,ext,'13 doors PASS',flush=True)
report['pass']=len(report['formats'])==4 and not report['failures']
(OUT/'09_Report/Door_Pivot_Exchange_Readback_V5.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:{a:v for a,v in r.items() if a!='results'} for k,r in report['formats'].items()},indent=2))
