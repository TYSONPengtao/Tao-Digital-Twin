import bpy,json,sys,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_03_junction_blender as j
from v24_qa_blender import _mesh_hash
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P))
target=bpy.data.objects['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry'];core=bpy.data.objects['V24_XIESHAN_09_Continuous_Eave_Bearing_Core'];lo,hi=j._bounds(core);lo=[v-.020 for v in lo];hi=[v+.020 for v in hi];col=bpy.context.scene.collection
cutter=j._box(bpy,col,'V24_03_TEMP_Core_Timber_Seat',lo,hi,bpy.data.materials['M_Roof']);row=j._difference(bpy,target,cutter);bpy.data.objects.remove(cutter,do_unlink=True);assert row['boundary_edges']==0,row
delta=json.loads((R/'V24_03_Changes.json').read_text(encoding='utf8'));jr=delta['module_reports']['junction'];roofobs=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];rd=[(o,j._bounds(o),j._tree(o))for o in roofobs];collisions=[]
for n in jr['kitchen_candidates']:
 ob=bpy.data.objects[n];lo,hi=j._bounds(ob);tr=j._tree(ob)
 for ro,rb,rt in rd:
  if any(hi[i]<rb[0][i]or lo[i]>rb[1][i]for i in range(3)):continue
  ov=tr.overlap(rt)
  if ov:collisions.append({'kitchen':n,'gate':ro.name,'triangle_pairs':len(ov)})
assert not collisions,collisions
for r in jr['geometry_changes']:
 if r['name']==target.name:r.update(row);r['final_core_seat']='Closed local timber bearing relief, 20 mm concealed margin'
for r in jr['checks']:
 if r.get('name')==target.name:r.update(row);r['pass']=row['boundary_edges']==0 and row['materials_preserved']and row['uv_preserved']
 if 'collisions'in r:r['collisions']=collisions;r['pass']=True
jr['status']='PASS_V24_03_JUNCTION';delta['expected_mesh_hashes'][target.name]=_mesh_hash(target.data)
(R/'V24_03_Changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2),encoding='utf8');(R/'V24_03_Junction_Report.json').write_text(json.dumps(jr,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'));build['junction']=jr
with P.open('rb') as f:build['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf8');print('ALL ROOF/KITCHEN TRIANGLE INTERSECTIONS ZERO',flush=True)
