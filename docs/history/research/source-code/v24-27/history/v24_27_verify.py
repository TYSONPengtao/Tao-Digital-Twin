import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_27';O=Path('E:/jz/JIA/Rebuild_V24_27');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_27.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_27_Changes.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);return o,v,f,mi,uv
def tree(n):
 o,v,f,_,_=geo(n);return BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
def height(tr,x,y):
 h=tr.ray_cast(Vector((x,y,2)),Vector((0,0,-1)),8)[0];return h.z if h else None
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
for row in prep['raw_objects']:
 o,v,f,mi,uv=geo(row['name']);a=np.load(D/row['file']);original=np.load(D/idx[o.name]['file']);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append({'name':o.name,'file':fn});err=float(np.max(np.linalg.norm(v-a['v'],axis=1)))if len(v)==len(a['v'])else 1.
 ck('Grade saved within 0.03mm / '+o.name,err<3e-5,maximum_vertex_error_m=err)
 ck('Original plan vertices retained and subdivisions saved / '+o.name,np.max(abs(v[:len(original['v']),:2]-original['v'][:,:2]))<3e-6 and np.array_equal(f,a['f']))
 ck('Affine source UVs and material indices saved / '+o.name,np.array_equal(mi,a['mi'])and np.max(abs(uv-a['uv']))<2e-6)
 soil='SOIL'in o.name;below=a['source_v'][:,2]<=a['source_v'][:,2].min()+1e-5
 if not o.name.startswith('V24_24_'):ck('Buried base retained / '+o.name,np.max(abs(v[below]-a['source_v'][below]))<3e-6)
soil=tree('SITE_V16_GRADED_INTERIOR_SOIL_Geometry');finish=tree('V24_24_House_Front_Matching_Stone_Paving');entry=tree('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry')
for y in [2.5,4.,6.,8.5,9.5]:
 for x in [-.25,-.65,-1.5,-3.,-5.5]:
  z=height(soil,x,y);target=-.15+(-.504+.15)*((-x-.125)/5.875);ck(f'West exterior follows the long planar grade {x},{y}',z is not None and abs(z-target)<.006,z_m=z,expected_m=target)
for x in [.5,2.5,6.5,10.,12.5]:
 for y in [-.45,.7,1.7]:
  z=height(finish,x,y);ck(f'Near-house court has consistent lower landing {x},{y}',z is not None and abs(z+.148)<.006,z_m=z)
z0=height(entry,6.5,-.15);z1=height(finish,6.5,-.35);ck('One exposed approximately 150mm entry riser',z0 is not None and z1 is not None and .143<z0-z1<.156,rise_m=z0-z1 if z0 is not None and z1 is not None else None)
# Matching top surfaces at the former court/soil seam are checked from the
# actual saved meshes, including the narrow strip behind the wall.
for y in [-.3,.5,1.5]:
 a=height(soil,-.15,y);cs=tree('SITE_V12_REBUILT_COURT_-20_0_0_Geometry'if y>=0 else'SITE_V12_REBUILT_COURT_-20_-20_0_Geometry');b=height(cs,-.06,y);ck(f'West court-to-soil edge closes without vertical crack {y}',a is not None and b is not None and abs(a-b)<.007,soil_z_m=a,court_z_m=b)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:
 s=bpy.data.texts[txt].as_string();ck('Embedded runtime equals delivered runtime / '+fn,s==(O/'Roam'/fn).read_text('utf8'));ck('Tested V24.26 runtime retained exactly / '+fn,s==(Path('E:/jz/JIA/Rebuild_V24_26/Roam')/fn).read_text('utf8'))
ck('Navigation cache is hidden and updated',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_27_Architecture_Updated'))
ck('All image dependencies packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
for module,txt in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_measure','V24_25_测量工具.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[txt].as_string(),txt,'exec'),m.__dict__)
c=sys.modules['architecture_roam_controller'];c.register();ck('Roam and measurement operators register together',hasattr(bpy.types.Scene,'arch_roam')and hasattr(bpy.ops.arch_roam,'measure_mode'));c.unregister()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[c for c in checks if not c['pass']];(R/'V24_27_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_GRADE'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V27_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
