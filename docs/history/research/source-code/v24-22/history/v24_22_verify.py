import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_22';O=Path('E:/jz/JIA/Rebuild_V24_22');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_22.blend';before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_22_Changes.json').read_text());checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed'])|set(changes['removed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Unaffected object fully preserved / '+n,after['objects'].get(n)==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Original '+kind+' preserved / '+n,after[kind].get(n)==a)
ck('All changed objects declared',all(n in allow or after['objects'].get(n)==a for n,a in before['objects'].items()))
ck('All removals declared',set(before['objects'])-set(after['objects'])==set(changes['removed']))
ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('26 original door interactions and 3 poses retained',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
ck('Roof valley tiles and small ears retained exactly',all(after['objects'].get(n)==a for n,a in before['objects'].items()if any(k in n for k in ['Unified_Pan_Barrel','Faceted_Head','Curved_Gable_Coping','North_Gable_Coping'])))
exports=[]
for row in prep['objects']:
 o=bpy.data.objects[row['name']];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':o.name,'file':fn,'volume_m3':row['volume_m3']});expected=np.array(row['v']);ck('Geometry stored within 0.03mm / '+o.name,len(v)==len(expected)and np.max(np.linalg.norm(v-expected,axis=1))<3e-5)
wall=bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];me=wall.data;v=[wall.matrix_world@p.co for p in me.vertices];me.calc_loop_triangles();tris=list(me.loop_triangles);bvh=BVHTree.FromPolygons(v,[t.vertices[:]for t in tris],all_triangles=True)
for y,direction,expected in [(-4.,(0,1,0),-2.935),(-10.5,(0,-1,0),-11.62)]:
 for x in [9.8,10.5,11.5,12.5]:
  for z in [.5,1.8,2.5,3.15]:
   hit,no,i,dist=bvh.ray_cast(Vector((x,y,z)),Vector(direction),3.)
   good=hit is not None and abs(hit.y-expected)<.007
   ck(f'Continuous closed white end face {x},{y},{z}',good,hit=list(hit)if hit else None)
   if hit:
    name=me.materials[me.polygons[tris[i].polygon_index].material_index].name;ck(f'Actual white inner finish {x},{y},{z}','White_Limewash'in name,material=name)
ck('Shared gable received kitchen-only white finish',any(m and m.name.startswith('M_V24_22_Shared_Gable_Interior')for m in bpy.data.objects['V24_14_Storage_West_Sealed_Gable'].data.materials))
ck('All image dependencies packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
ck('Updated startup is embedded verbatim',bpy.data.texts['V24_21_启动漫游.py'].as_string()==(O/'Roam/start_roam.py').read_text(encoding='utf8'))
ck('Navigation cache hidden and rebuilt',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_22_Architecture_Updated'))
for module,txt in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[txt].as_string(),txt,'exec'),m.__dict__)
control=sys.modules['architecture_roam_controller'];control.register();ck('Controller registers',hasattr(bpy.types.Scene,'arch_roam'));control.unregister();ck('Controller unregisters',not hasattr(bpy.types.Scene,'arch_roam'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[c for c in checks if not c['pass']];(R/'V24_22_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_KITCHEN'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V22_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
