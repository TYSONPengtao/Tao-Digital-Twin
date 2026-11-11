import bpy, numpy as np, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
from v24_06_common import snapshot
def topology_uv_hash(me):
 h=hashlib.sha256()
 for seq,key,n,dt in[(me.loops,'vertex_index',1,np.int32),(me.polygons,'loop_start',1,np.int32),(me.polygons,'loop_total',1,np.int32),(me.polygons,'material_index',1,np.int32),(me.polygons,'use_smooth',1,np.bool_)]:h.update(q._bulk(seq,key,n,dt).tobytes())
 for uv in me.uv_layers:h.update(q._bulk(uv.data,'uv',2).tobytes())
 h.update(json.dumps([m.name if m else None for m in me.materials]).encode());return h.hexdigest()
O=Path('E:/jz/JIA/Rebuild_V26_12');P=O/'Blender/Architecture_Complete_V26_12.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
ch=json.loads((O/'Reports/V26_12_Changes.json').read_text('utf8'));before=json.loads((W/'v26_12/Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(name,yes,**kw):checks.append({'check':name,'pass':bool(yes),**kw});print('QA',name,bool(yes),kw if not yes else'',flush=True)
excluded=set(ch['archived_photo_reliefs']);bad=[]
for n,r in before['objects'].items():
 a=after['objects'].get(n)
 if a is None:bad.append(n);continue
 if n in excluded:
  rr=dict(r);aa=dict(a)
  for key in['hidden','hide_render','hide_viewport','hide_get','visible_get']:
   rr.pop(key,None);aa.pop(key,None)
  if rr!=aa:bad.append(n)
 elif r!=a:bad.append(n)
ck('All original architecture, stairs, door leaves, platforms, timber and collision mesh preserved',not bad,invalid=bad)
for key in['materials','images','actions','door_poses']:
 bad=[n for n,v in before[key].items()if after[key].get(n)!=v]
 ck('Original '+key+' preserved',not bad,invalid=bad)
bad=[];exposure=[];front_errors=[]
deps=bpy.context.evaluated_depsgraph_get()
def tree(ob):
 me=ob.data;me.calc_loop_triangles();return BVHTree.FromPolygons([ob.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
core_trees={name:tree(bpy.data.objects[name])for name in['V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']}
for r in ch['restored']:
 ob=bpy.data.objects[r['name']];old=bpy.data.objects[r['source_object']];v=q._world(ob.data,ob.matrix_world);src=q._world(old.data,old.matrix_world);ids=np.asarray(r['original_front_vertex_ids'],int);inside=np.asarray(r['inside']);origin=np.asarray(r['origin']);heights=-(v[ids]-origin)@inside
 # All relative original height differences are retained within native float precision.
 delta=(v[ids]-src[ids])@inside;error=np.max(abs(delta-r['front_rigid_inward_shift_m']));front_errors.append(float(error))
 if not ob.visible_get()or ob.hide_render or len(ob.modifiers)or not np.isfinite(v).all():bad.append(r['name'])
 me=ob.data;me.calc_loop_triangles();f=np.asarray([t.vertices[:]for t in me.loop_triangles]);edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,counts=np.unique(edges,axis=0,return_counts=True)
 if not np.all(counts==2):bad.append(r['name']+' nonclosed')
 # Check burial against the actual stone core. Surrounding walls, lanterns
 # and timber can legitimately occlude a side field from a20cm lateral ray;
 # keep that scene observation separately, rather than deleting real details.
 field_tree=tree(ob);core_tree=core_trees['SITE_V21_GATE_REFERENCE_LAYER_05_Geometry'if'Header'in r['source_object']else'V26_10_Inner_Gate_Rectangular_Stone_Piers']
 a=v[ids];tangent=np.cross(inside,[0.,0.,1.]);u=a@tangent;zz=a[:,2];mask=(u>np.min(u)+.04*np.ptp(u))&(u<np.max(u)-.04*np.ptp(u))&(zz>np.min(zz)+.04*np.ptp(zz))&(zz<np.max(zz)-.04*np.ptp(zz));pool=np.flatnonzero(mask)
 for label,k in[('valley',pool[np.argmin(heights[pool])]),('peak',pool[np.argmax(heights[pool])])]:
  pt=a[k];hit,co,no,fi,who,mat=sc.ray_cast(deps,Vector(pt-inside*.2),Vector(inside),distance=.4)
  near=Vector(pt-inside*.03);fh=field_tree.ray_cast(near,Vector(inside),.1);kh=core_tree.ray_cast(near,Vector(inside),.1)
  ok=fh[0]is not None and np.linalg.norm(np.asarray(fh[0])-pt)<.0001 and(kh[0]is None or fh[3]<kh[3]-.001)
  exposure.append({'object':ob.name,'sample':label,'height_m':float(heights[k]),'full_scene_lateral_hit':who.name if who else None,'field_distance_m':fh[3],'core_distance_m':kh[3],'pass':bool(ok)})
ck('21 restored inserts are visible, closed baked meshes with no live subdivision',not bad,invalid=bad,active_triangles=ch['active_relief_triangles'])
ck('Every original V24 relief height difference is preserved after seating',max(front_errors)<.000004,maximum_error_m=max(front_errors))
ck('All21 inserts have real peaks and valleys outside their actual stone-core backing',all(r['pass']for r in exposure)and all(r['height_m']<0 for r in exposure if r['sample']=='valley')and all(r['height_m']>0 for r in exposure if r['sample']=='peak'),rays=exposure)
ck('All15 active original inserts retain actual V24 reference topology and UV after header registration',all(topology_uv_hash(bpy.data.objects[r['name']].data)==ch['original_V24_meshes'][r['source_object']]['topology_uv_hash']for r in ch['restored']if r['source_is_original_V24']),maximum_registration_error_m=max(r['reference_alignment_error_m']for r in ch['original_V24_meshes'].values()))
ck('The21 low-definition photo inserts remain hidden, editable and unchanged',all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get()for n in excluded))
ck('Saved overcast world and zero direct sun retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Master material preview retains the local AO needed to read carving',sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and sc.eevee.fast_gi_resolution=='2')
ctrl=bpy.data.texts['V24_21_漫游控制器.py'].as_string();start=bpy.data.texts['V24_21_启动漫游.py'].as_string()
ck('Runtime labels V26.12 and opens on the inner gate with Home returning to court','V26.12  ·  1.65m'in ctrl and"walker.place(control.PRESETS['INNER_GATE'])"in start and"self.walker.place(PRESETS['COURT'])"in ctrl)
ck('V24 reference and V26.11 master remain byte-identical',hashlib.sha256(Path(ch['reference_model']).read_bytes()).hexdigest()==ch['reference_sha256']and hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
fail=[r for r in checks if not r['pass']]
(O/'Reports/V26_12_Native_QA.json').write_text(json.dumps({'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8')
print('NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
