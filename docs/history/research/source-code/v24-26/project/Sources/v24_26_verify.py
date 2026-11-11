import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_26';O=Path('E:/jz/JIA/Rebuild_V24_26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_26.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_26_Changes.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);return o,v,f
def tree(n):
 o,v,f=geo(n);return BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Unchanged original object fully retained / '+n,after['objects'].get(n)==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Original '+kind+' retained / '+n,after[kind].get(n)==a)
ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('No original objects removed',not(set(before['objects'])-set(after['objects'])))
ck('26 doors and all original animated poses retained',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
ck('Metric model units retained',bpy.context.scene.unit_settings.system=='METRIC'and bpy.context.scene.unit_settings.scale_length==1.)
exports=[]
for row in prep['objects']:
 o,v,f=geo(row['name']);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':o.name,'file':fn,'volume_m3':row['volume_m3']});expected=np.array(row['v']);err=float(np.max(np.linalg.norm(v-expected,axis=1)))if len(v)==len(expected)else 1.;ck('Saved geometry within 0.03mm / '+o.name,err<3e-5,maximum_vertex_error_m=err)
n=prep['recolor'][0]['name'];o,v,f=geo(n);a=np.load(D/idx[n]['file']);ck('Closure geometry and UV retained',np.array_equal(v,a['v'])and np.array_equal(f,a['f'])and len(o.data.uv_layers)>0);ck('Closure fully finished in matching blue brick',all(m.name=='M_V24_18_Continuous_Blue_Brick'for m in o.data.materials))
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';o,v,f=geo(n);a=np.load(D/idx[n]['file']);ck('Connected masonry geometry retained during return recolor',np.array_equal(v,a['v'])and np.array_equal(f,a['f']))
for face in o.data.polygons:
 c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
 if abs(c.x-9.43)<.00004 and -3.0<c.y<-2.5 and no.x<-.8:ck('Narrow return beside closure also blue brick / '+str(face.index),o.data.materials[face.material_index].name=='M_V24_18_Continuous_Blue_Brick')
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0','V24_25_Kitchen_East_Unified_Pan_Barrel_Field','V24_Kitchen_Curved_Gable_Coping']:
 _,v,_=geo(n);ck('South kitchen projection limited to 120mm / '+n,v[:,1].min()>-11.85003,minimum_y_m=float(v[:,1].min()))
for i in [1,2,3]:
 n=f'V24_19_Kitchen_South_Faceted_Head_Frame_{i}';_,v,_=geo(n);a=np.load(D/idx[n]['file']);d=v-a['v'];ck('South ear profile reseated without changing height / '+n,np.max(abs(d-np.array([0,.14,0])))<3e-5)
chain='SITE_COURTYARD_WEST_TILE_WALL';cap=tree(chain+'_TILE_COPING_Geometry')
wall=tree(chain+'_Geometry')
for x,y in [(0.,q)for q in [1.,-1.,-6.,-10.]]+[(q,-11.582)for q in [.7,2.,4.5]]:
 top=wall.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),2)[0];bottom=cap.ray_cast(Vector((x,y,1.5)),Vector((0,0,1)),2)[0];ck(f'Roof bedding actually seats on unchanged wall crown {x},{y}',top is not None and bottom is not None and bottom.z<top.z+.00003,wall_top_z=top.z if top else None,cap_bottom_z=bottom.z if bottom else None)
for y in [-10.,-6.,-1.,1.]:
 for x in [-.448,0.,.448]:
  hit=cap.ray_cast(Vector((x,y,4.)),Vector((0,0,-1)),3)[0];ck(f'Wide roof bed covers west wall and both eaves {x},{y}',hit is not None)
for x in [.7,2.,4.5]:
 for d in [-.448,0.,.448]:
  hit=cap.ray_cast(Vector((x,-11.582+d,4)),Vector((0,0,-1)),3)[0];ck(f'Wide roof bed covers return and both eaves {x},{d}',hit is not None)
flower=tree(chain+'_V10_OPEN_FLOWER_BRICKS_Geometry')
for i,r in enumerate(prep['proof']['courtyard_coping']['hole_probes'][::9]):
 p=Vector(r['point']);n=Vector(r['direction']);hit=flower.ray_cast(p-n*.20,n,.4)[0];ck('Real through aperture in floral ridge / '+str(i),hit is None)
for name in [r['name']for r in prep['objects']if r['name'].startswith(chain)]:
 _,v,_=geo(name);ck('Wall coping stops before carved gate pier / '+name,v[:,0].max()<4.90403)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:
 s=bpy.data.texts[txt].as_string();ck('Embedded runtime equals delivered runtime / '+fn,s==(O/'Roam'/fn).read_text('utf8'));ck('Tested V24.25 runtime retained exactly / '+fn,s==(Path('E:/jz/JIA/Rebuild_V24_25/Roam')/fn).read_text('utf8'))
ck('Navigation cache is hidden and updated',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_26_Architecture_Updated'))
ck('All image dependencies packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
for module,txt in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_measure','V24_25_测量工具.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[txt].as_string(),txt,'exec'),m.__dict__)
c=sys.modules['architecture_roam_controller'];c.register();ck('Roam and measurement operators register together',hasattr(bpy.types.Scene,'arch_roam')and hasattr(bpy.ops.arch_roam,'measure_mode'));c.unregister()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[c for c in checks if not c['pass']];(R/'V24_26_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_CORRECTIONS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V26_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
