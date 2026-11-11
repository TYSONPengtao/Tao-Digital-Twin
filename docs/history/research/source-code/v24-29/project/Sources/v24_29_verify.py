import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_29';O=Path('E:/jz/JIA/Rebuild_V24_29');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_29.blend'
changes=json.loads((R/'V24_29_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));house=set(changes['house']);roots=set(changes['house_roots']);allow=set(changes['changed'])|set(changes['removed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Original object preserved / '+n,after['objects'].get(n)==a)
 if n in house:
  b=after['objects'][n];m=np.array(a['matrix']);expected=m.copy();expected[2,3]-=.45
  ck('Rigid house translation with native mesh and animation preserved / '+n,b['mesh_hash']==a['mesh_hash'] and b['animation']==a['animation']and np.max(abs(np.array(b['matrix'])-expected))<4e-5 and b['parent']==('V24_29_Three_Storey_House_Datum'if n in roots else a['parent']))
for k in ['materials','actions','images']:
 for n,a in before[k].items():ck('Original '+k+' retained / '+n,after[k].get(n)==a)
ck('Only the superseded court dividing step removed',set(before['objects'])-set(after['objects'])==set(changes['removed'])=={'V24_28_Continuous_Kitchen_To_House_Step'})
ck('Every added object declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('Door count remains 26',len(after['doors'])==len(before['doors'])==26)
for frame,poses in before['door_poses'].items():
 for n,m in poses.items():
  expected=np.array(m)
  if n in house:expected[2,3]-=.45
  ck('Door pose preserved relative to its own building / '+frame+'/'+n,np.max(abs(np.array(after['door_poses'][frame][n])-expected))<4e-5)
trees={}
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@q.co for q in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles],int)
 return o,v,f
def tree(n):
 if n not in trees:
  _,v,f=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
 return trees[n]
def height(n,x,y,start=1.):
 p=tree(n).ray_cast(Vector((x,y,start)),Vector((0,0,-1)),8.)[0];return float(p.z)if p else None
for row in changes['ground']:
 o,v,f=geo(row['name']);a=np.load(D/row['file']);ck('Saved ground geometry matches correction / '+o.name,len(v)==len(a['v'])and np.max(abs(v-a['v']))<4e-5)
 if row.get('terrain_cavity'):
  ck('Soil outside outline retained while excavating only the house foundation',np.max(abs(v[:,:2].min(0)-a['source_v'][:,:2].min(0)))<3e-6 and np.max(abs(v[:,:2].max(0)-a['source_v'][:,:2].max(0)))<3e-6)
 elif row.get('kind')=='trimmed_slab':ck('Old gallery band ends at new paving boundary / '+o.name,np.max(abs(v[:,0]-a['source_v'][:,0]))<3e-6 and np.max(abs(v[:,1]-np.minimum(a['source_v'][:,1],row['trimmed_at_y_m'])))<3e-6 and np.array_equal(f,a['f']))
 else:ck('Ground plan footprint and topology unchanged / '+o.name,np.array_equal(f,a['f'])and np.max(abs(v[:,:2]-a['source_v'][:,:2]))<3e-6)
 me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])
 ck('Ground material assignments and UV retained / '+o.name,np.array_equal(mi,a['mi'])and np.max(abs(uv-a['uv']))<3e-6)
 ck('Finite corrected mesh / '+o.name,np.isfinite(v).all())
soil='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';finish='V24_24_House_Front_Matching_Stone_Paving';nav='V24_21_Navigation_Collision'
for x in [-.3,-.7,-1.8,-3.5,-6.5,-9.]:
 for y in [-7.,-3.,.5,3.,6.,9.5]:
  h=height(soil,x,y);ck('West exterior has no raised transverse strip '+str((x,y)),h is not None and abs(h+.452)<.003,z_m=h)
for y in [-3.3,-2.8,-2.0,-1.0,-.32]:
 hs=[]
 for x in [1.5,3.,6.5,8.04,8.27,10.,12.5]:
  h=height(finish,x,y);hs.append(h);ck('Forecourt paving shares original level '+str((x,y)),h is not None and abs(h+.45)<.002,z_m=h)
  if y>-3.0 and not(y<=-2.55 and x>=8.15):
   actual=height(nav,x,y,start=-.30);ck('No buried terrain crosses the forecourt '+str((x,y)),actual is not None and -.454<actual<-.448,z_m=actual)
 ck('Both sides of old dividing step are flush at '+str(y),all(h is not None for h in hs)and max(hs)-min(hs)<.002,spread_m=max(hs)-min(hs)if all(h is not None for h in hs)else None)
for x in [4.1,6.5,8.9]:
 porch=height('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry',x,-.2);court=height(finish,x,-.32)
 ck('Lowered house porch meets the court '+str(x),porch is not None and court is not None and abs(porch-court)<.002,porch_z_m=porch,court_z_m=court)
for fl,z in [(1,-.45),(2,3.45),(3,7.05)]:
 n=f'SLAB_JOINED_F{fl}_Geometry';ck('F'+str(fl)+' slab mesh retained without bending',before['objects'][n]['mesh_hash']==after['objects'][n]['mesh_hash'])
 for x,y in ([(6.5,4.),(10.5,4.5),(11.5,5.5)]if fl==3 else[(1.5,4.),(6.5,3.),(10.5,4.5)]):
  h=height(n,x,y,start=z+1);ck('F'+str(fl)+' room floor is horizontal '+str((x,y)),h is not None and abs(h-z)<.00005,z_m=h)
  actual=height(nav,x,y,start=z+.10);ck('F'+str(fl)+' interior has no raised outdoor paving '+str((x,y)),actual is not None and abs(actual-z)<.012,z_m=actual)
ck('Story heights retained',abs(height('SLAB_JOINED_F2_Geometry',6.5,3.,5)-height('SLAB_JOINED_F1_Geometry',6.5,3.,1)-3.9)<.00005 and abs(height('SLAB_JOINED_F3_Geometry',6.5,3.,8)-height('SLAB_JOINED_F2_Geometry',6.5,3.,5)-3.6)<.00005)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:
 ck('Runtime retained / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8')==(Path('E:/jz/JIA/Rebuild_V24_28/Roam')/fn).read_text('utf8'))
ck('All file images packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
src=json.loads((D/'Source.json').read_text());ck('Prior V24.28 file unchanged',sha(src['model'])==src['sha256'])
fail=[c for c in checks if not c['pass']];(R/'V24_29_Native_QA.json').write_text(json.dumps({'status':'PASS_RIGID_HOUSE_LOWERING_LEVEL_YARD_AND_FLUSH_COURT'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V29_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
