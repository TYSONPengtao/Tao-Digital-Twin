from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_3';FD=D/'Final';FD.mkdir(exist_ok=True);O=Path('E:/jz/JIA/Rebuild_V26_3');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_3.blend';sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=snapshot(bpy);sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((R/'V26_3_Changes.json').read_text('utf8'));allowed=set(ch['changed']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
diff=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('Unrelated source meshes transforms UVs materials and visibility retained',not diff,checked=len(before['objects'])-len(allowed),mismatches=diff)
ck('V26.2 source remains byte identical',sha(ch['source'])==ch['source_sha256']);ck('All original objects remain in the editable file',all(n in after['objects']for n in before['objects']))
md=[n for n,v in before['materials'].items()if after['materials'].get(n,{}).get('hash')!=v['hash']];ck('Original shared shader graphs unchanged',not md,changed=md)
im=[n for n,v in before['images'].items()if after['images'].get(n)!=v];ck('Original packed photo bytes unchanged',not im,changed=im);ck('All original animation curves unchanged',before['actions']==after['actions'])
posebad=[]
for fr,old in before['door_poses'].items():
 for n,m in old.items():
  want=np.array(m)
  got=np.array(after['door_poses'].get(fr,{}).get(n,[]))
  if got.shape!=(4,4)or np.max(abs(want-got))>3e-6:posebad.append([fr,n])
ck('All original evaluated door poses retained',not posebad,mismatches=posebad,frames=[1,20,40])
ck('Archived previous components excluded from rendering and viewport',all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get()for n in ch['archived']))
ci=json.loads((R/'V26_3_Collision_Index.json').read_text('utf8'));cn={r['name']for r in ci['objects']};ck('Archived sources excluded from collision',not(cn&set(ch['archived'])))
for n in ['V26_3_House_Connected_Walls_And_Stairs','V26_2_Continuous_Ground_And_Perimeter_Shell','V26_1_Photo_Referenced_Continuous_Wood_Railing','V26_Original_Site_Entrance_Ramp_0']:ck('Saved collision contains '+n,n in cn)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
rows=[];invalid=[]
for o in bpy.data.objects:
 if o.type!='MESH'or not len(o.data.polygons)or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 if any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','Navigation_Collision','Avatar_','Roam_Person','V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_']):continue
 if len(o.data.polygons)>100000 and not o.name.startswith('V26_'):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32);fn='FINAL_'+str(len(rows))+'.npz';np.savez_compressed(FD/fn,v=v,f=f,mi=mi,uv=uv);rows.append({'name':o.name,'file':fn,'materials':[m.name for m in me.materials],'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
 if not np.isfinite(v).all():invalid.append(o.name)
ck('Actual saved visible native geometry finite',not invalid,invalid=invalid);ck('Original photographed entrance ramp fully unchanged',before['objects']['V26_Original_Site_Entrance_Ramp_0']==after['objects']['V26_Original_Site_Entrance_Ramp_0']);ck('No Rhino model exported',not list(O.rglob('*.3dm')))

# The recovered screenwall is the original native mesh, transform and finish.
orig=json.loads((D/'Original_Secondary.json').read_text('utf8'));restorebad=[]
for r in orig['objects']:
 o=bpy.data.objects[r['name']];a=np.load(D/r['file']);me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
 ok=v.shape==a['v'].shape and np.array_equal(v,a['v'])and np.array_equal(f,a['f'])and np.array_equal(mi,a['mi'])and np.array_equal(uv,a['uv'])and[m.name for m in me.materials]==r['materials']and not o.hide_render and not o.hide_get()
 if not ok:restorebad.append(r['name'])
ck('All 11 original V24.34 secondary screenwall components restored exactly',not restorebad,invalid=restorebad,components=len(orig['objects']),original_sha256=orig['sha256'])
ck('All five unintended replacement screenwall components hidden and excluded from collision',all(bpy.data.objects[n].hide_render and n not in cn for n in ch['archived']if n.startswith('V26_1_Secondary_Wall_')))
gn='V26_2_Continuous_Ground_And_Perimeter_Shell';oldindex={r['name']:r for r in json.loads((W/'v26_2'/'Final'/'Geometry_Index.json').read_text('utf8'))};oa=np.load(W/'v26_2'/'Final'/oldindex[gn]['file']);go=bpy.data.objects[gn];gv=np.array([go.matrix_world@p.co for p in go.data.vertices]);go.data.calc_loop_triangles();gf=np.array([t.vertices[:]for t in go.data.loop_triangles],np.int32)
ck('Secondary finish restoration preserves every ground and perimeter vertex and face',np.array_equal(gv,oa['v'])and np.array_equal(gf,oa['f']))
field=np.load(D/'Secondary_Restored_Point_Field.npz');attribute=go.data.attributes.get('V24_20_Height_Above_Finish_Division');got=np.array([attribute.data[int(i)].value for i in field['ids']])if attribute else np.array([])
ck('Original secondary-wall shader height field is present with the restored source values',attribute is not None and np.array_equal(got,field['values']),points=len(field['ids']))
bad=[]
for r in ch['restored_secondary_ornaments']:
 oldrow=oldindex[r['name']];olddata=np.load(W/'v26_2'/'Final'/oldrow['file']);o=bpy.data.objects[r['name']];me=o.data;me.calc_loop_triangles();verts=np.array([o.matrix_world@p.co for p in me.vertices]);faces=np.array([t.vertices[:]for t in me.loop_triangles],np.int32)
 if not np.array_equal(verts[:len(olddata['v'])],olddata['v'])or not np.array_equal(faces[:len(olddata['f'])],olddata['f']):bad.append(r['name'])
ck('Restoring the original secondary frieze leaves every existing outside-branch triangle unchanged',not bad,invalid=bad)
mp=json.loads((R/'V26_3_Secondary_Original_Photo_Mapping.json').read_text('utf8'));mapbad=[]
for row in mp['triangles']:
 face=go.data.polygons[row['triangle']];v=np.array([go.matrix_world@go.data.vertices[j].co for j in face.vertices]);uv=np.array([go.data.uv_layers.active.data[j].uv[:]for j in face.loop_indices]);pred=v@np.array(row['gradients_world'])+np.array(row['offsets_m']);mat=go.data.materials[face.material_index]
 if np.max(abs(uv-pred))>3e-5 or not mat.name.startswith('M_V26_3_Secondary_Original_Photo_'):mapbad.append(row['triangle'])
ck('Recovered secondary photograph mapping matches the original source UV coordinates',not mapbad,triangles=len(mp['triangles']),invalid=mapbad)
# Export actual evaluated hinge matrices, including intermediate animated poses.
leaves=[o for o in bpy.data.objects if o.type=='MESH'and o.name.endswith('__LEAF_Geometry')and o.name.startswith(('DOOR_BATH_','DOOR_BED_','DOOR_KITCHEN_F1','DOOR_STUDY_'))];motion={}
for o in leaves:
 me=o.data;me.calc_loop_triangles();fn='LEAF_LOCAL_'+str(len(motion))+'.npz';np.savez_compressed(FD/fn,v=np.array([p.co[:]for p in me.vertices]),f=np.array([t.vertices[:]for t in me.loop_triangles]));motion[o.name]={'file':fn,'matrices':{}}
for fr in list(range(1,41,3))+[40]:
 sc.frame_set(fr);bpy.context.view_layer.update()
 for o in leaves:motion[o.name]['matrices'][str(fr)]=[list(r)for r in o.matrix_world]
(FD/'Door_Motion.json').write_text(json.dumps(motion),encoding='utf8');(FD/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');fail=[c for c in checks if not c['pass']];(R/'V26_3_Native_Readback_QA.json').write_text(json.dumps({'model_sha256':sha(P),'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('READBACK_DONE',len(checks),len(fail),flush=True)
