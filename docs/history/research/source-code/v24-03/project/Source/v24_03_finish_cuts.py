import bpy,bmesh,json,sys,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_qa_blender import _mesh_hash
from v24_03_junction_blender import _closed_stats
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P));repairs=[]
for n in ['SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);tiny=[f for f in bm.faces if f.calc_area()<1e-7 and any(e.is_boundary for e in f.edges)];count=len(tiny)
 bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY');wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 isolated=[v for v in bm.verts if not v.link_edges]
 if isolated:bmesh.ops.delete(bm,geom=isolated,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();s=_closed_stats(ob);assert s['boundary_edges']==0,(n,s);repairs.append({'name':n,'removed_zero_area_cut_slivers':count,**s});print('CUT REPAIRED',repairs[-1],flush=True)
delta=json.loads((R/'V24_03_Changes.json').read_text(encoding='utf8'));jr=delta['module_reports']['junction']
for r in repairs:
 for row in jr['geometry_changes']:
  if row['name']==r['name']:row.update(r)
 for row in jr['checks']:
  if row.get('name')==r['name']:row.update(r);row['pass']=r['boundary_edges']==0 and row['materials_preserved']and row['uv_preserved']
 delta['expected_mesh_hashes'][r['name']]=_mesh_hash(bpy.data.objects[r['name']].data)
jr['status']='PASS_V24_03_JUNCTION' if all(c['pass']for c in jr['checks']) else 'FAIL_V24_03_JUNCTION';jr['zero_area_cut_fragment_repair']=repairs;assert jr['status'].startswith('PASS')
(R/'V24_03_Junction_Report.json').write_text(json.dumps(jr,ensure_ascii=False,indent=2),encoding='utf8');(R/'V24_03_Changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2),encoding='utf8')
bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'));build['junction']=jr
with P.open('rb') as f:build['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf8');print('CUT REPAIR SAVED',flush=True)
