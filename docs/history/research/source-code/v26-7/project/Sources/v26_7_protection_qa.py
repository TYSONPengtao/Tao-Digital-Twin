from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_7');P=O/'Blender/Architecture_Complete_V26_7.blend';checks=[]
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('PROTECTED',n,bool(yes),flush=True)
src=json.loads((W/'v26_3/Original_Secondary.json').read_text('utf8'));bad=[]
for r in src['objects']:
 o=bpy.data.objects[r['name']];a=np.load(W/'v26_3'/r['file']);me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);yes=np.array_equal(v,a['v'])and np.array_equal(f,a['f'])and np.array_equal(uv,a['uv'])and np.array_equal(mi,a['mi'])and[m.name for m in me.materials]==r['materials']and not o.hide_render and not o.hide_get()
 if not yes:bad.append(o.name)
ck('All 11 original secondary screenwall components remain exact',not bad,invalid=bad)
gn=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];field=np.load(W/'v26_3/Secondary_Restored_Point_Field.npz');attr=gn.data.attributes.get('V24_20_Height_Above_Finish_Division');values=np.array([attr.data[int(i)].value for i in field['ids']])if attr else[];ck('Original secondary source-photo height field preserved',attr is not None and np.array_equal(values,field['values']))
mp=json.loads(Path('E:/jz/JIA/Rebuild_V26_3/Reports/V26_3_Secondary_Original_Photo_Mapping.json').read_text('utf8'));bad=[]
for r in mp['triangles']:
 p=gn.data.polygons[r['triangle']];v=np.array([gn.matrix_world@gn.data.vertices[i].co for i in p.vertices]);uv=np.array([gn.data.uv_layers.active.data[i].uv[:]for i in p.loop_indices]);pred=v@np.array(r['gradients_world'])+np.array(r['offsets_m']);mat=gn.data.materials[p.material_index]
 if abs(uv-pred).max()>3e-5 or not (mat.name.startswith('M_V26_3_Secondary_Original_Photo_') or str(mat.get('V26_7_Source_Affine_Material','')).startswith('M_V26_3_Secondary_Original_Photo_')):bad.append(r['triangle'])
ck('Exact restored secondary photograph interpolation retained',not bad,invalid=bad)
ck('Only requested roam launcher exists',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd'])
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(O/'Reports/V26_7_Protected_Original_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8')
