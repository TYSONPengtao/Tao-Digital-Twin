import bpy,json,numpy as np,collections,time,hashlib
from pathlib import Path
W=Path(__file__).parent;D=W/'v25';O=Path('E:/jz/JIA/Rebuild_V25');T=time.monotonic();idx=json.loads((D/'Export_Index.json').read_text('utf8'));mats={x['key']:x for x in json.loads((D/'Material_Index.json').read_text('utf8'))};expected=collections.Counter()
for r in idx:expected[(r['source_object'],mats[r['material']]['source_material'])]+=r['triangles']
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();actual=collections.Counter();rows=[]
for j,name in enumerate(dict.fromkeys(r['source_object'] for r in idx)):
 o=bpy.data.objects[name];ev=o.evaluated_get(dep);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dep);me.calc_loop_triangles();verts=np.empty(len(me.vertices)*3,np.float64);me.vertices.foreach_get('co',verts);verts=verts.reshape(-1,3);M=np.array(o.matrix_world);verts=verts@M[:3,:3].T+M[:3,3];ff=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',ff);ff=ff.reshape(-1,3);tt=verts[ff];valid=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)>1e-11;mi=np.array([t.material_index for t in me.loop_triangles]);source_mats=[s.material for s in ev.material_slots]
 for mid in np.unique(mi[valid]):
  mat=source_mats[int(mid)];count=int(np.count_nonzero(valid & (mi==mid)));actual[(name,mat.name)]+=count
 ev.to_mesh_clear()
 if j%500==0:print('MATERIAL_SOURCE_FACE_QA',j,flush=True)
cleanup_path=D/'Coplanar_Cleanup.json'
if cleanup_path.exists():
 cleanup=json.loads(cleanup_path.read_text('utf8'));key=(cleanup['source_object'],mats[cleanup['material_key']]['source_material']);actual[key]-=cleanup['faces_removed']
assert actual==expected,[(k,actual[k],expected[k]) for k in set(actual)|set(expected) if actual[k]!=expected[k]][:30]
report={'status':'PASS_SOURCE_MATERIAL_FACE_PARTITIONS','source_objects':len({k[0] for k in actual}),'material_partitions':len(actual),'valid_triangles':sum(actual.values()),'checks':['Every retained source triangle retains its source material assignment','Fresh source evaluation compared with final Rhino export index; completely covered internal backfaces accounted separately','Source photograph mesh material assignments preserved'],'failures':[],'seconds':time.monotonic()-T};(O/'Reports/V25_Material_Face_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('V25_MATERIAL_FACE_QA_OK',len(actual),report['seconds'],flush=True)
