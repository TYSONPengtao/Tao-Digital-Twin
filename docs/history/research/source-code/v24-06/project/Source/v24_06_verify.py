"""Fresh-read verification of the five V24.06 review requests and original assets."""
import bpy,json,sys,math,numpy as np,bmesh
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
base=json.loads((R/'V24_06_Before_Snapshot.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_06_Changes.json').read_text(encoding='utf8'));build=json.loads((R/'V24_06_Build.json').read_text(encoding='utf8'));pave=json.loads((R/'V24_06_Passage_Paving.json').read_text(encoding='utf8'));balance=delta['roof_balance'];timber=delta['timber'];checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
allowed=set(delta['declared_changes']);removed={'SITE_TREE_5_Geometry','SITE_TREE_6_Geometry','SITE_V15_EXISTING_TREE_ROOT_SOIL_Geometry'}
ck('Only declared changes',set(delta['changed_objects'])<=allowed,unexpected=sorted(set(delta['changed_objects'])-allowed));ck('Only selected trees and root soil removed',set(delta['removed_objects'])==removed)
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Original packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original action '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
transform_allowed=set(delta['roof_objects']+delta['attachments'])
for n,r in base['objects'].items():
 ob=bpy.data.objects.get(n);ck('Retained original object '+n,ob is not None or n in removed)
 if ob is None:continue
 ck('Original parent and animation '+n,(ob.parent.name if ob.parent else None)==r['parent']and q._animation(ob)==r['animation'])
 ck('Original visibility '+n,ob.hide_render==r['hide_render'])
 if n not in transform_allowed:ck('Original transform '+n,q._matrix(ob.matrix_world)==r['matrix'])
 if r['mesh_hash']and n not in allowed:ck('Original site mesh and UV '+n,q._mesh_hash(ob.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Saved mesh digest '+n,n in bpy.data.objects and q._mesh_hash(bpy.data.objects[n].data)==h)
newsolids=set(delta['roof_objects']+delta['supports']+timber['changed_objects']+timber['added_objects'])
deps=bpy.context.evaluated_depsgraph_get()
for n in sorted(newsolids):
 ob=bpy.data.objects[n];s=q._stats(ob.data);ck('Closed positive solid '+n,s['closed']and s['signed_volume_m3']>0 and s['finite'],**s)
 if ob.modifiers:
  ev=ob.evaluated_get(deps);me=ev.to_mesh();s=q._stats(me);ck('Evaluated closed solid '+n,s['closed']and s['signed_volume_m3']>0 and s['finite'],**s);ev.to_mesh_clear()
for n in delta['restored_kitchen']:
 if n in timber['changed_objects']:continue
 s=_closed_stats(bpy.data.objects[n]);ck('Kitchen contact has no open boundary '+n,s['boundary_edges']==0,**s)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,m in poses.items():ck('Original door pose '+n+' frame '+f,q._matrix(bpy.data.objects[n].matrix_world)==m)
sc.frame_set(40);bpy.context.view_layer.update();ck('26 moving door roots',len(base['doors'])==26);ck('15 original relief fields',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15);ck('Original materials enabled',all(v.material_override is None for v in sc.view_layers))
roof=[bpy.data.objects[n]for n in delta['roof_objects']];rb=[[min(_bounds(o)[0][i]for o in roof)for i in range(3)],[max(_bounds(o)[1][i]for o in roof)for i in range(3)]];pb=_bounds(bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry']);cy=sum(pb[i][1]for i in[0,1])/2;front=pb[0][1]-rb[0][1];rear=rb[1][1]-pb[1][1]
ck('Roof centered on gate piers',abs(sum(rb[i][1]for i in[0,1])/2-cy)<1e-5,center_y=cy)
ck('Equal front and rear roof projections',abs(front-rear)<.001,front_m=front,rear_m=rear)
ck('Front eave retracted at least 0.5m',rb[0][1]-balance['old_bounds'][0][1]>.5,retraction_m=rb[0][1]-balance['old_bounds'][0][1])
ck('Thin roof stack preserved',abs((rb[1][2]-rb[0][2])-(balance['old_bounds'][1][2]-balance['old_bounds'][0][2]))<1e-5)
def clip(poly,axis,bound,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=bound if greater else a[axis]<=bound;ib=b[axis]>=bound if greater else b[axis]<=bound
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((bound-a[axis])/(b[axis]-a[axis])))
 return out
heights=[];coll=[];roof_bvh=[(o,_bounds(o),_tree(o))for o in roof]
for r in balance['kitchen_clipped_height_proof']:
 ob=bpy.data.objects[r['name']];ob.data.calc_loop_triangles();z=[]
 for t in ob.data.loop_triangles:
  p=[ob.matrix_world@ob.data.vertices[i].co for i in t.vertices]
  for ax,b,g in[(0,rb[0][0],True),(0,rb[1][0],False),(1,rb[0][1],True),(1,rb[1][1],False)]:
   if p:p=clip(p,ax,b,g)
  if p:z.extend(v.z for v in p)
 ck('Adjacent kitchen height proof '+ob.name,bool(z)and abs(max(z)-r['max_z_in_gate_plan'])<1e-5)
 if z:heights.append(max(z))
 lo,hi=_bounds(ob);tr=None
 for ro,bb,rt in roof_bvh:
  if any(hi[i]<bb[0][i]or lo[i]>bb[1][i]for i in range(3)):continue
  if tr is None:tr=_tree(ob)
  hits=tr.overlap(rt)
  if hits:coll.append({'kitchen':ob.name,'gate':ro.name,'triangles':len(hits)})
gap=rb[0][2]-max(heights);ck('Lowest eave underside clears highest adjacent kitchen coping',gap>.10,gate_underside_z=rb[0][2],kitchen_coping_z=max(heights),clearance_m=gap);ck('No gate roof kitchen interpenetration',not coll,collisions=coll)
for n in delta['supports']:
 lo,hi=_bounds(bpy.data.objects[n]);ck('Plain bearing reaches raised underside '+n,hi[2]>=rb[0][2]+.015 and lo[2]<2.70,lower_z=lo[2],upper_z=hi[2])
ridge=bpy.data.objects['SITE_COURTYARD_WEST_TILE_WALL_V10_OPEN_FLOWER_BRICKS_Geometry'];v=[ridge.matrix_world@v.co for v in ridge.data.vertices];vs=[p for p in v if .5<p.x<4.5 and p.y<-11];wc=(min(p.y for p in vs)+max(p.y for p in vs))/2
ck('Courtyard wall centerline equals gate pier centerline',abs(wc-cy)<1e-5,wall_y=wc,pier_y=cy,inward_shift_m=delta['wall']['inward_shift_m'])
ck('Wall correction is inward and limited',.10<delta['wall']['inward_shift_m']<.15 and .98<delta['wall']['return_length_factor']<1)
for n in delta['wall']['changed_objects']:
 ob=bpy.data.objects[n];s=_closed_stats(ob);old=delta['wall']['source_topology'][n];ck('Wall original boundary topology retained '+n,s['boundary_edges']<=old['boundary_edges'],original_boundary_edges=old['boundary_edges'],new_boundary_edges=s['boundary_edges'])
for n in removed:ck('Selected tree removed '+n,n not in bpy.data.objects)
ref=bpy.data.objects[pave['reference_path']];soil=bpy.data.objects[pave['changed_objects'][0]];target=bpy.data.materials[pave['material']];slot=pave['material_slot'];fit=np.array(pave['uv_fit']);uv=soil.data.uv_layers.active;err=[];count=0
ck('Same neighboring passage material',soil.data.materials[slot]==ref.data.materials[0]==target and target.name=='M_V12_Road_Concrete')
for f in soil.data.polygons:
 if f.material_index!=slot:continue
 count+=1
 for li in f.loop_indices:
  p=soil.matrix_world@soil.data.vertices[soil.data.loops[li].vertex_index].co;expect=np.array([p.x,p.y,1.])@fit;err.append(float(np.max(np.abs(np.array(uv.data[li].uv)-expect))))
ck('Paving uses identical metric UV mapping',bool(err)and max(err)<1e-5,max_uv_error=max(err)if err else None,fit_rms=pave['uv_fit_rms']);ck('Selected earth strip paved',pave['paved_surface_area_m2']>30 and count==pave['paved_faces'],area_m2=pave['paved_surface_area_m2'],faces=count)
st=_tree(soil);grade=[]
for r in pave['height_samples']:
 if math.hypot(r['x']+4,r['y']+13.5)<1.3:continue
 h=st.ray_cast(Vector((r['x'],r['y'],4)),Vector((0,0,-1)),12)
 if h[0]is not None:grade.append(abs(h[0].z-r['old_ground_z']))
ck('Original terrain grade retained outside old tree pit',bool(grade)and max(grade)<1e-4,maximum_height_change_m=max(grade)if grade else None)
for x,y in [(0,-15.2),(3,-15.0)]:
 h=st.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),12);ck('Road finish at selected ground '+str((x,y)),h[0]is not None and soil.data.polygons[h[2]].material_index==slot)
root=pave['root_pit_repair'];hit=_tree(ref).ray_cast(Vector((-4,-13.5,4)),Vector((0,0,-1)),12);expected=float(np.array([-4,-13.5,1])@np.array(root['matching_road_plane']))
ck('Old tree pit filled to neighboring passage level',hit[0]is not None and abs(hit[0].z-expected)<1e-4,expected_z=expected,actual_z=hit[0].z if hit[0]else None)
rs=_closed_stats(ref);ck('Repaired original road is closed manifold',rs['boundary_edges']==0 and rs['nonmanifold_edges']==0,**rs)
column=bpy.data.objects.get('V24_03_Kitchen_Single_Veranda_Column');ck('One independent kitchen veranda column retained',column is not None and timber['independent_veranda_columns']==1 and 'SITE_KITCHEN_V12_BEFORE_WOOD_15_Geometry'not in bpy.data.objects and 'SITE_KITCHEN_GROUNDED_OUTER_COLUMN_STONE_BASES_Geometry'not in bpy.data.objects)
def components(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);remain=set(bm.verts);c=0
 while remain:
  c+=1;stack=[remain.pop()]
  while stack:
   for e in stack.pop().link_edges:
    for v in e.verts:
     if v in remain:remain.remove(v);stack.append(v)
 bm.free();return c
rc=components(bpy.data.objects['SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry']);ck('80 dense rafters in 40 pairs',rc==80,count=rc)
ck('Three ties and six curved facade brackets',timber['tie_bearing_stations_y_m']==[-11.2,-7.1,-2.98]and timber['curved_facade_brackets']==6)
for n in ['V24_06_Kitchen_Carved_Bracket_Heads','V24_06_Kitchen_Fluted_Melon_Pendants']:ck('Editable solid wood sculpture '+n,any(m.type=='MULTIRES'and m.total_levels>=1 for m in bpy.data.objects[n].modifiers))
returnwall=_tree(bpy.data.objects['V24_04_Kitchen_Perimeter_Upper_Return']);perimeter=_tree(bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry']);backwall=_tree(bpy.data.objects['V24_03_Kitchen_Rear_Gable_Wall']);ck('Full-height kitchen rear closure retained',bool(returnwall.overlap(perimeter))and bool(returnwall.overlap(backwall)))
ck('Saved model SHA matches build',sha(P)==build['sha256']);fail=[r for r in checks if not r['pass']]
report={'status':'PASS_V24_06_FRESH_BLEND_QA'if not fail else'FAIL_V24_06_FRESH_BLEND_QA','model_sha256':sha(P),'checks':checks,'failures':fail,'roof_balance':balance,'eave_bottom_clearance_m':gap,'retained_materials':len(base['materials']),'retained_images':len(base['images']),'moving_doors':len(base['doors']),'paved_area_m2':pave['paved_surface_area_m2'],'timber':timber};write('V24_06_Fresh_Blend_QA.json',report);print(report['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:20],ensure_ascii=False))
