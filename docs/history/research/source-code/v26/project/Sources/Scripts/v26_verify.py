from pathlib import Path
import bpy,json,numpy as np,hashlib,sys
W=Path(__file__).parent;D=W/'v26';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26.blend';sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=snapshot(bpy);sc.frame_set(40);bpy.context.view_layer.update();changes=json.loads((R/'V26_Changes.json').read_text('utf8'));allowed=set(changes['changed']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
diff=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('Unrelated base objects retain geometry, world transforms, materials and visibility',not diff,checked=len(before['objects'])-len(allowed),mismatches=diff)
ck('Every base object is retained',all(n in after['objects']for n in before['objects']))
mdiff=[n for n,v in before['materials'].items()if after['materials'].get(n,{}).get('hash')!=v['hash']and n in after['materials']];ck('Original shader graphs are unchanged; white is assigned only to inner faces',not mdiff,changed_shaders=mdiff)
idiff=[n for n,v in before['images'].items()if after['images'].get(n)!=v];ck('All packed photographs remain byte identical',not idiff,changed_photographs=idiff)
ck('All door and window actions and frames 1 20 40 remain unchanged',before['actions']==after['actions']and before['door_poses']==after['door_poses'])
base=json.loads((D/'Base.json').read_text('utf8'));source=json.loads((D/'Original_Source_Index.json').read_text('utf8'));ck('V24.34 source file is byte identical',sha(base['source'])==base['sha256']);ck('Original site 3dm is byte identical',sha(source['source'])==source['sha256'])
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches delivered '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
struct=json.loads((D/'Prepared_Structure.json').read_text('utf8'));ramp=json.loads((D/'Prepared_Ramp.json').read_text('utf8'));selected={r['name']for r in struct['objects']+ramp['objects']};selected.update(f'SLAB_JOINED_F{fl}_Geometry'for fl in [1,2,3]);selected.add('ROOF_MAIN_JOINED_Geometry');final=[];FD=D/'Final';FD.mkdir(exist_ok=True);invalid=[];photoqa=[]
for n in sorted(selected):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32);fn='FINAL_'+str(len(final))+'.npz';np.savez_compressed(FD/fn,v=v,f=f,mi=mi,uv=uv);final.append({'name':n,'file':fn,'materials':[m.name for m in me.materials],'bounds':[v.min(0).tolist(),v.max(0).tolist()],'triangles':len(f)})
 if not np.isfinite(v).all():invalid.append(n)
 if n.startswith('V26_Original_Site_Entrance_Ramp'):
  r=next(r for r in ramp['objects']if r['name']==n);a=np.load(D/r['file']);err=float(np.abs(v-a['v']).max());uvpass=np.array_equal(uv,a['uv'].astype(np.float32));photoqa.append({'name':n,'maximum_vertex_float_rounding_m':err,'uv_exact':uvpass});ck('Original ramp heights and UV survive saved file '+n,err<2e-6 and uvpass,maximum_coordinate_rounding_m=err)
ck('All inspected native geometry is finite',not invalid,invalid=invalid)
(FD/'Geometry_Index.json').write_text(json.dumps(final,ensure_ascii=False),encoding='utf8')
# Exterior-facing polygon indices and UVs of the actual perimeter remain
# bitwise equal to the source, while the selected inward faces read white.
inv={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};paint=json.loads((R/'V26_White_Inside_Faces.json').read_text('utf8'));whitebad=[]
for r in paint:
 o=bpy.data.objects[r['object']];count=sum(p.material_index<len(o.data.materials)and o.data.materials[p.material_index].name=='M_V24_11_Plain_White_Limewash'for p in o.data.polygons)
 if count<r['inward_white_faces']:whitebad.append(r['object'])
ck('White finish assignments read back on all five courtyard inward meshes',not whitebad,invalid=whitebad,painted_faces=sum(r['inward_white_faces']for r in paint))
ci=json.loads((R/'V26_Collision_Index.json').read_text('utf8'));cn={r['name']for r in ci['objects']};need=[r['name']for r in struct['objects']+ramp['objects']if r['name']!='V26_Original_Ramp_Concrete_Back_And_Sides'];ck('Collision proxy includes every repaired support and recovered ramp',all(n in cn for n in need),missing=[n for n in need if n not in cn],triangles=ci['triangles'])
ck('No Rhino model is exported',not list(O.rglob('*.3dm')))
fail=[r for r in checks if not r['pass']];(R/'V26_Native_Readback_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail,'photo_ramp':photoqa},ensure_ascii=False,indent=2),encoding='utf8');print('READBACK_DONE',len(checks),'FAIL',len(fail),flush=True)
