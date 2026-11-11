import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_24';O=Path('E:/jz/JIA/Rebuild_V24_24');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_24.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_24_Changes.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw})
def tree(v,f):return BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
def objtree(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();return o,tree(np.array([o.matrix_world@v.co for v in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles]))
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed'])|set(changes['removed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Unaffected object fully preserved / '+n,after['objects'].get(n)==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Original '+kind+' preserved / '+n,after[kind].get(n)==a)
ck('All changed objects declared',all(n in allow or after['objects'].get(n)==a for n,a in before['objects'].items()))
ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('No objects removed',not changes['removed']and set(before['objects'])<=set(after['objects']))
ck('26 door interactions and original three poses retained',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
exports=[]
for row in prep['objects']:
 o=bpy.data.objects[row['name']];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':o.name,'file':fn,'volume_m3':row['volume_m3']});expected=np.array(row['v']);ck('Geometry stored within 0.03mm / '+o.name,len(v)==len(expected)and np.max(np.linalg.norm(v-expected,axis=1))<3e-5)
wallname='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';wall,wb=objtree(wallname);me=wall.data;old=np.load(D/idx[wallname]['file']);ob=tree(old['v'],old['f'])
for x in [8.45,8.8,9.5,10.5,11.8,12.6]:
 for z in [.1,1.5,2.3]:
  hit,no,j,dist=wb.ray_cast(Vector((x,-13,z)),Vector((0,1,0)),3)
  mat=me.materials[me.polygons[me.loop_triangles[j].polygon_index].material_index].name if hit else None
  ck(f'Front brick set back to white wall plane {x},{z}',hit is not None and abs(hit.y+11.73)<.00003 and mat=='M_V24_18_Continuous_Blue_Brick',hit=list(hit)if hit else None,material=mat)
for x in [8.45,8.8,9.5,10.5,11.8,12.6]:
 for z in [.1,1.5,2.3,2.9]:
  a=ob.ray_cast(Vector((x,-11.1,z)),Vector((0,-1,0)),1.2);b=wb.ray_cast(Vector((x,-11.1,z)),Vector((0,-1,0)),1.2)
  same=(a[0]is None and b[0]is None)or(a[0]is not None and b[0]is not None and(a[0]-b[0]).length<3e-5)
  ck(f'Courtyard-side gate wall surface unchanged {x},{z}',same,old=list(a[0])if a[0]else None,new=list(b[0])if b[0]else None)
closure,cb=objtree('V24_24_Kitchen_North_Veranda_White_Closure')
for x in [8.48,8.8,9.2,9.5]:
 top=2.57+(x-8.28)*(.465/1.32)-.095+.012
 for z in [0.,1.,2.3,top-.02]:
  hit,_,_,_=cb.ray_cast(Vector((x,-3.8,z)),Vector((0,1,0)),1.)
  ck(f'Red opening completely sealed {x},{z:.3f}',hit is not None and abs(hit.y+3.035)<2e-5)
_,pb=objtree('V24_24_House_Front_Matching_Stone_Paving');floor_trees=[]
for n in ['SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_V12_REBUILT_COURT_0_0_0_Geometry']:
 a=np.load(D/idx[n]['file']);floor_trees.append(tree(a['v'],a['f']))
for x in [.65,2.4,3.3,5.8,7.7,9.8,12.4]:
 for y in [-3.3,-2.3,-1.2,-.55,.4,1.4]:
  h=pb.ray_cast(Vector((x,y,1.)),Vector((0,0,-1)),3)[0];zs=[a.z for tr in floor_trees if(a:=tr.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),3)[0])is not None]
  iy=int(np.floor((y+10.9)/.62));ix=int(np.floor((x-(.4-(.56 if iy%2 else 0)))/1.12));xx=x-(.4-(.56 if iy%2 else 0))-ix*1.12;yy=y+10.9-iy*.62;rise=.002 if .003<xx<1.117 and .003<yy<.617 else .0005
  ck(f'Paving follows original grade {x},{y}',h is not None and zs and abs(h.z-max(zs)-rise)<4e-5,surface_z=h.z if h else None,source_z=max(zs)if zs else None,finish_rise_m=rise)
ck('All image dependencies packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
ck('Original proven startup retained verbatim',bpy.data.texts['V24_21_启动漫游.py'].as_string()==(O/'Roam/start_roam.py').read_text('utf8'))
ck('Navigation cache hidden and rebuilt',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_24_Architecture_Updated'))
for module,txt in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[txt].as_string(),txt,'exec'),m.__dict__)
control=sys.modules['architecture_roam_controller'];control.register();ck('Controller registers',hasattr(bpy.types.Scene,'arch_roam'));control.unregister();ck('Controller unregisters',not hasattr(bpy.types.Scene,'arch_roam'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[c for c in checks if not c['pass']];(R/'V24_24_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_CORRECTIONS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V24_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
