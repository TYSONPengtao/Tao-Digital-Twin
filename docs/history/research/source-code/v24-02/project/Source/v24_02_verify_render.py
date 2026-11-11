"""Fresh Blender readback, preservation checks, actual aperture rays, color renders."""
import bpy,json,sys,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
import v24_qa_blender as qa_module
O=Path('E:/jz/JIA/Rebuild_V24');P=O/'Blender/Architecture_Complete_V24_02.blend';R=O/'Reports'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
expected=json.loads((R/'V24_02_Expected_Mesh_Readback.json').read_text(encoding='utf8'))
qa_module.ALLOWED.update(expected['changed_old_objects'])
base=json.loads((R/'Baseline_V23_Snapshot.json').read_text(encoding='utf8'))
qa=qa_module.validate_v24(bpy,base,R)
checks=[]
def ck(label,passed,**kw):
 row={'check':label,'pass':bool(passed),**kw};checks.append(row)
 if not passed:print('EXTRA QA FAILURE',row,flush=True)
for n,h in expected['expected_meshes'].items():
 ob=bpy.data.objects.get(n);ck('Saved mesh/UV/material exact readback '+n,ob is not None and qa_module._mesh_hash(ob.data)==h)
for n in expected['new_objects']:
 ob=bpy.data.objects[n]
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free()
 ck('New detail closed solid '+n,closed and volume>1e-10,volume_m3=volume)
 ck('New detail has original material and UV '+n,bool(ob.data.uv_layers) and all(m and m.name in base['materials'] for m in ob.data.materials))
def tree(name):
 ob=bpy.data.objects[name];return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons])
roof=tree('SITE_V21_GATE_REFERENCE_LAYER_09_Geometry');lattice=tree('V24_GATE_PHOTO_OPEN_DIAMOND_RIDGE');clear=0
for j in range(45):
 x=4.385+(8.815-4.385)*j/44
 hit=roof.ray_cast(Vector((x,-11.486,10)),Vector((0,0,-1)),10)
 assert hit[0] is not None
 if lattice.ray_cast(Vector((x,-11.54,hit[0].z+.028)),Vector((0,1,0)),.108)[0] is None:clear+=1
ck('All 45 ridge apertures remain truly open',clear==45,clear_count=clear)
ck('Saved walkthrough default is frame 40',sc.frame_current==40)
qa['top_and_junction_checks']=checks;qa['failures']+= [c for c in checks if not c['pass']]
qa['status']='PASS_V24_02_FRESH_BLEND_QA' if not qa['failures'] else 'FAIL_V24_02_FRESH_BLEND_QA'
with P.open('rb') as f:qa['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
qa['model']=str(P);(R/'V24_02_Fresh_Blend_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
assert not qa['failures'],qa['failures'];print('V24.02 ALL QA PASS',len(qa['checks'])+len(checks),flush=True)
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
views=[('V24_02_Front_Real_Materials','V24_Inner_Gate_Real_Materials',20),('V24_02_Roof_Real_Materials','V23_Gate_Roof_Oblique',40),('V24_02_Carving_Closeup','V23_Gate_Carved_Corner',40)]
for name,pos,tar,lens in [('V24_02_Kitchen_Gate_Junction',[10.8,-16.8,4.4],[9.9,-11.7,3.35],42),('V24_02_Ridge_Top',[7.2,-14.4,5.6],[6.8,-11.53,2.95],40)]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;views.append((name,name,40))
for label,name,frame in views:
 sc.frame_set(frame);sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/(label+'.png'));bpy.ops.render.render(write_still=True);print('V24.02 COLOR RENDER',label,flush=True)
(R/'V24_02_Preview_States.json').write_text(json.dumps({'model_sha256':qa['model_sha256'],'views':[{'file':l+'.png','camera':n,'frame':f} for l,n,f in views],'real_materials':True,'material_override':None,'saved_default_frame':40,'runtime_UE_tested':False},ensure_ascii=False,indent=2),encoding='utf8')
print('V24.02 FRESH QA AND RENDERS COMPLETE',flush=True)
