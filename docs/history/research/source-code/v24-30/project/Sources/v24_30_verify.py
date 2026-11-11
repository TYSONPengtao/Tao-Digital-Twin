import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_30';O=Path('E:/jz/JIA/Rebuild_V24_30');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_30.blend';before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));c=json.loads((R/'V24_30_Changes.json').read_text('utf8'));prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw})
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(c['changed'])|set(c['removed'])
for n,row in before['objects'].items():
 if n not in allow:ck('Unrelated native object retained / '+n,after['objects'].get(n)==row)
for k in ['materials','actions','images']:
 for n,row in before[k].items():ck('Original '+k+' retained / '+n,after[k].get(n)==row)
ck('All retirements explicitly scoped to superseded ground',set(before['objects'])-set(after['objects'])==set(c['removed']))
ck('All new objects declared',set(after['objects'])-set(before['objects'])==set(c['added']))
ck('All 26 door rigs and keyed poses unchanged',len(after['doors'])==len(before['doors'])==26 and after['door_poses']==before['door_poses'])
house=json.loads(Path('E:/jz/JIA/Rebuild_V24_29/Reports/V24_29_Changes.json').read_text('utf8'))['house']
ground_fixture={'CONSTRUCTION_RAINWATER_RECEIVER_WING_SW_Geometry','CONSTRUCTION_RAINWATER_RECEIVER_NW_Geometry'}
ck('House floors and architectural objects retained without further deformation',all(before['objects'][n]==after['objects'][n]for n in house if n not in ground_fixture),objects=len(set(house)-ground_fixture))
for row in c['offsets']:
 n=row['name'];a=before['objects'][n];b=after['objects'][n];m=np.array(a['matrix']);m[:3,3]+=row['offset'];ck('Ground attachment rigidly follows the new court / '+n,a['mesh_hash']==b['mesh_hash']and a['animation']==b['animation']and np.max(abs(m-np.array(b['matrix'])))<.00004)
trees={}
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();return o,np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles])
def tree(n):
 if n not in trees:
  _,v,f=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True,epsilon=1e-6)
 return trees[n]
def hit(n,x,y,z=1.):
 p=tree(n).ray_cast(Vector((x,y,z)),Vector((0,0,-1)),8.)[0];return float(p.z)if p else None
for row in prep['raw_objects']:
 o,v,f=geo(row['name']);a=np.load(D/row['file']);ck('Saved prepared geometry / '+o.name,len(v)==len(a['v'])and len(f)==len(a['f'])and np.max(abs(v-a['v']))<4e-5 and np.array_equal(f,a['f']))
 me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);ck('Material and affine UV / '+o.name,np.array_equal(mi,a['mi'])and np.max(abs(uv-a['uv']))<4e-5)
 if row['name'].startswith('V24_30_'):
  edges={}
  for face in f:
   for i,j in zip(face,np.roll(face,-1)):key=(int(min(i,j)),int(max(i,j)));edges[key]=edges.get(key,0)+1
  ck('New native floor or curb mesh is closed / '+o.name,all(x==2 for x in edges.values()),non_manifold_edges=sum(x!=2 for x in edges.values()))
pad='V24_30_Outer_Yard_White_Building_Pad';nav='V24_21_Navigation_Collision';low='V24_30_Low_Main_Court_Running_Bond_Stone';hi='V24_30_High_North_Lane_And_Rear_Running_Bond_Stone'
o,v,f=geo(pad);t=v[f];norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=t[norm[:,2]>1e-7];ck('Outer building pad top is one exact horizontal plane',np.max(abs(up[:,:,2]+.60))<.000002,area_m2=float(norm[norm[:,2]>1e-7,2].sum()/2),z_m=-.60)
ck('Outer pad uses only plain white material',[m.name for m in o.data.materials]==['M_V24_30_White_Building_Pad'])
for x,y in [(-4,0),(-4,5),(-4,9),(-10,5),(-10,0),(-10,-5),(-15,3),(-15,-3),(-19,1)]:
 z=hit(nav,x,y,-.20);ck('Outer yard flat and unobstructed '+str((x,y)),z is not None and abs(z+.60)<.002,z_m=z)
for x,y in [(5,-9),(5.5,-7),(6.2,-5),(4.9,-3),(6.5,-.7),(1.6,-9),(1.5,-2),(7.9,-2)]:
 z=hit(nav,x,y,-.2);ck('Low court continuously paved '+str((x,y)),z is not None and abs(z+.60)<.002,z_m=z)
for x,y in [(8.7,-1.5),(10.5,-1),(12.5,-1),(13.8,2),(14.2,6),(.5,10.7),(6,10.6),(12,10.3)]:
 z=hit(nav,x,y,-.2);ck('High inner lane and rear strip share a horizontal floor '+str((x,y)),z is not None and abs(z+.45)<.002,z_m=z)
for x in [4.1,6.5,7.8]:
 entry=hit('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry',x,-.2);court=hit(nav,x,-.7,-.2);ck('House entrance has exactly one 15cm riser '+str(x),entry is not None and court is not None and abs(entry-court-.15)<.002,entry_z_m=entry,low_court_z_m=court)
for fl,z in [(1,-.45),(2,3.45),(3,7.05)]:
 for x,y in [(1.5,4),(6.5,3),(10.5,4.5)]:
  zz=hit('SLAB_JOINED_F'+str(fl)+'_Geometry',x,y,z+1);ck('Indoor floor stays flat F'+str(fl)+' '+str((x,y)),zz is not None and abs(zz-z)<.00006,z_m=zz)
ck('Kitchen floor and original small rise unchanged',before['objects']['SITE_KITCHEN_STONE_FLOOR_Geometry']==after['objects']['SITE_KITCHEN_STONE_FLOOR_Geometry'])
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_TILE_COPING_Geometry']:
 ck('Original outer retaining masonry or unrelated coping retained exactly / '+n,after['objects'][n]==before['objects'][n])
walltree=tree('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry');facetre=tree('V24_28_Continuous_White_Courtyard_Wall_Face')
for row in prep['proof']['wall']['stations'][2:-2]:
 p=np.array(row['centre']);no=np.array(row['outward_mitre']);nn=no/np.linalg.norm(no);origin=Vector((*tuple(p+nn*.6),1.));direction=Vector((*tuple(-nn),0.));out=walltree.ray_cast(origin,direction,2.)[0];inside=walltree.ray_cast(Vector((*tuple(p-nn*.6),1.)),Vector((*tuple(nn),0.)),2.)[0]
 thick=(out-inside).length if out and inside else None;ck('Retained masonry has a vertical constant section at y='+str(round(row['y'],3)),thick is not None and abs(thick-.32)<.006,thickness_m=thick)
 face=facetre.ray_cast(Vector((*tuple(p-nn*.7),1.)),Vector((*tuple(nn),0.)),2.)[0];d=(out-face).length if out and face else None;ck('Thin inside finish follows the outside reference without a wedge at y='+str(round(row['y'],3)),d is not None and abs(d-.336)<.007,total_thickness_m=d)
o,v,f=geo('V24_28_Level_White_Wall_Tile_Coping');a=np.load(D/'V24_28_Level_White_Wall_Tile_Coping.npz');ck('Coping retains all original horizontal eave and tile Z levels',np.max(abs(v[:,2]-a['v'][:,2]))<.000003 and np.array_equal(f,a['f']))
ck('Coping has constant width from exterior reference',prep['proof']['wall']['tile_coping_nominal_width_m']==.47 and prep['proof']['wall']['outer_reference'].startswith('Original'))
curb=prep['proof']['curb'];ss=curb['stations'];ck('Curb is continuous along the full marked gate approach',14.5<curb['length_m']<16. and len(ss)>=19,length_m=curb['length_m'],stone_count=len(ss))
ck('Curb stands higher at the outer gate and gradually reaches inner landing',ss[0]['exposed_height_m']>.20 and ss[-1]['exposed_height_m']<.065 and ss[-1]['exposed_height_m']<ss[0]['exposed_height_m']/3,first_height_m=ss[0]['exposed_height_m'],last_height_m=ss[-1]['exposed_height_m'])
sep=prep['proof']['rear_separator'];ck('Rear partition connects house to perimeter and separates high/low zones',sep['outline']['coordinates'][0]and sep['width_m']==.20 and sep['internal_high_finish_m']==-.45 and sep['outer_pad_finish_m']==-.60)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:
 ck('Runtime retained / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8')==(Path('E:/jz/JIA/Rebuild_V24_29/Roam')/fn).read_text('utf8'))
ck('All external image resources packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
for frame in [1,20,40]:
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
 for i in [1,2,3,4]:
  n=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{i}_Geometry';o,v,f=geo(n);points=v[v[:,2]<-.61];clearances=[]
  for x,y,z in points:
   floors=[hit(k,float(x),float(y),-.20)for k in [pad,'V24_30_Outer_Gate_Swing_Clearance_Graded_Apron','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry','SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP_Geometry']]
   floors=[q for q in floors if q is not None]
   if floors:clearances.append(float(z)-max(floors))
  ck('Outer gate leaf has ground clearance at frame '+str(frame)+' / '+str(i),bool(clearances)and min(clearances)>-.003,minimum_clearance_m=min(clearances)if clearances else None)
bpy.context.scene.frame_set(40)
src=json.loads((D/'Source.json').read_text('utf8'));ck('Previous V24.29 file untouched',sha(src['model'])==src['sha256'])
fail=[r for r in checks if not r['pass']];(R/'V24_30_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_LEVELS_PAVING_WHITE_PAD_CURB_AND_ANCHORED_WALL'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V30_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
