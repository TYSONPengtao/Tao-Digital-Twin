import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_25';O=Path('E:/jz/JIA/Rebuild_V24_25');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_25.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_25_Changes.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def objtree(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();return o,BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed'])|set(changes['removed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Unchanged object fully retained / '+n,after['objects'].get(n)==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Original '+kind+' retained / '+n,after[kind].get(n)==a)
ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('All removals declared',set(before['objects'])-set(after['objects'])==set(changes['removed']))
ck('26 doors and all original action poses retained',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
ck('Metric model units',bpy.context.scene.unit_settings.system=='METRIC'and bpy.context.scene.unit_settings.scale_length==1.)
exports=[]
for row in prep['objects']:
 o=bpy.data.objects[row['name']];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':o.name,'file':fn,'volume_m3':row['volume_m3']});expected=np.array(row['v']);ck('Geometry saved within 0.03mm / '+o.name,len(v)==len(expected)and np.max(np.linalg.norm(v-expected,axis=1))<3e-5)
for fl,floor,sides in [(1,0.,['LEFT','RIGHT']),(2,3.9000244140625,['LEFT','RIGHT']),(3,7.5,['RIGHT'])]:
 _,wall=objtree(f'FACADE_CONTINUOUS_F{fl}_Geometry')
 for side in sides:
  x=0. if side=='LEFT'else 13.
  n=f'WINDOW_{side}_C1212_F{fl}_Geometry';o,tr=objtree(n);zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
  ck('High privacy sill and 0.8m window / '+n,abs(min(zs)-floor-1.8)<3e-5 and abs(max(zs)-floor-2.6)<3e-5)
  start=x+(1. if side=='LEFT'else-1.);direction=Vector((-1,0,0))if side=='LEFT'else Vector((1,0,0))
  for y in [8.18,8.40,8.75,8.94]:
   hit,_,i,_=tr.ray_cast(Vector((start,y,floor+2.2)),direction,2.);ma=o.data.materials[o.data.polygons[o.data.loop_triangles[i].polygon_index].material_index].name if hit else None
   ck('No middle horizontal bar / '+n+'/'+str(y),ma=='M_Glass_Frosted',hit_material=ma)
  hit=wall.ray_cast(Vector((start,8.2,floor+1.3)),direction,2)[0];ck('Old low window hole filled / '+n,hit is not None)
  hit=wall.ray_cast(Vector((start,8.2,floor+2.2)),direction,2)[0];ck('Raised window opening really cut / '+n,hit is None)
  clad=f'HOUSE_V21_{"WEST"if side=="LEFT"else"EAST"}_GREY_WHITE_F{fl}_Geometry';_,ct=objtree(clad)
  ck('Exterior cladding follows new high opening / '+n,ct.ray_cast(Vector((start,8.2,floor+1.3)),direction,2)[0]is not None and ct.ray_cast(Vector((start,8.2,floor+2.2)),direction,2)[0]is None)
_,wall=objtree('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry')
for x in [8.28,8.31,8.335,8.38]:
 for z in [.0,1.2,2.5,3.08]:
  h=wall.ray_cast(Vector((x,-12.3,z)),Vector((0,1,0)),1.)[0];ck(f'Gate pier-to-wall joint has no air gap {x},{z}',h is not None)
roofco=prep['proof']['kitchen_roof'];_,deck=objtree('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry')
for side,co,xs in [('west',roofco['west_plane'],[7.7,8.8,10.,11.4]),('east',roofco['east_plane'],[12.0,12.7,13.5])]:
 for x in xs:
  for y in [-9.5,-7.,-3.5]:
   h=deck.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),5)[0]
   if side=='east'and h is None:continue
   target=float(np.array(co)@np.array([x,y,1.]));ck(f'Continuous straight {side} roof surface {x},{y}',h is not None and abs(h.z-target)<4e-5,surface_z=h.z if h else None,plane_z=target)
for row in roofco['tiles']:
 o=bpy.data.objects[row['name']];v=np.array([o.matrix_world@v.co for v in o.data.vertices]);co=np.array(row['plane']);height=v[:,2]-np.c_[v[:,:2],np.ones(len(v))]@co
 ck('Tile bodies follow one pitch without diagonal height jumps / '+o.name,height.min()>-.001 and height.max()<.13,min_offset_m=float(height.min()),max_offset_m=float(height.max()))
for n in prep['proof']['storage_entrance']['recolored_existing_floors']+['V24_25_Storage_Entrance_Continuous_Light_Gray_Finish']:
 o=bpy.data.objects[n];ck('Same light grey entrance finish / '+n,all(m.name=='M_V12_Road_Concrete'for m in o.data.materials))
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py')]:ck('Embedded runtime equals delivered runtime / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
ck('Navigation cache updated and hidden',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_25_Architecture_Updated'))
ck('All image dependencies packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
for module,txt in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_measure','V24_25_测量工具.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[txt].as_string(),txt,'exec'),m.__dict__)
c=sys.modules['architecture_roam_controller'];c.register();ck('Roam and measure operators register together',hasattr(bpy.types.Scene,'arch_roam')and hasattr(bpy.ops.arch_roam,'measure_mode'));c.unregister();ck('Runtime unregisters cleanly',not hasattr(bpy.types.Scene,'arch_roam'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[c for c in checks if not c['pass']];(R/'V24_25_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_CORRECTIONS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V25_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)

