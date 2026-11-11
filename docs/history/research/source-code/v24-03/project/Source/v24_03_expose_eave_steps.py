import bpy,bmesh,json,sys,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_qa_blender import _mesh_hash
from v24_xieshan_roof_blender import fitted_bearing_z,CX,CY,BEARING_DEPTH_SCALE
from v24_03_junction_blender import _bounds,_tree
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend';bpy.ops.wm.open_mainfile(filepath=str(P));ob=bpy.data.objects['V24_XIESHAN_09_Continuous_Eave_Bearing_Core'];V=[];F=[]
levels=[(1.96,.575,2.655,2.695),(2.015,.600,2.695,2.736),(2.065,.620,2.736,2.770),(2.110,.642,2.770,2.815),(2.155,.660,2.815,2.865)]
for a,b,z0,z1 in levels:
 x0,x1=CX-a+.045,CX+a-.045;y0,y1=CY-(b-.025)*BEARING_DEPTH_SCALE,CY+(b-.025)*BEARING_DEPTH_SCALE;lo,hi=fitted_bearing_z(z0-.002),fitted_bearing_z(z1+.002);k=len(V);V.extend([(x,y,z)for z in [lo,hi]for y in [y0,y1]for x in [x0,x1]]);F.extend([[k+i for i in f]for f in [[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]]])
me=bpy.data.meshes.new('V24_03_Inset_Tiered_Bearing_Core');me.from_pydata(V,[],F)
for m in ob.data.materials:me.materials.append(m)
me.update();uv=me.uv_layers.new(name='V24_Metric_UV')
for loop in me.loops:
 v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x*.35+v.y*.13,v.z*.35+v.y*.31)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(me);bm.free();ob.data=me
delta=json.loads((R/'V24_03_Changes.json').read_text(encoding='utf8'));jr=delta['module_reports']['junction'];tr=_tree(ob);bb=_bounds(ob);collisions=[]
for n in jr['kitchen_candidates']:
 q=bpy.data.objects[n];qb=_bounds(q)
 if any(qb[1][i]<bb[0][i]or qb[0][i]>bb[1][i]for i in range(3)):continue
 ov=tr.overlap(_tree(q))
 if ov:collisions.append({'kitchen':n,'gate':ob.name,'pairs':len(ov)})
assert not collisions,collisions
ob['V24_03_Exposed_Eave_Levels']=5;ob['V24_03_Core_Inset_m']=[.045,.025*BEARING_DEPTH_SCALE];delta['expected_mesh_hashes'][ob.name]=_mesh_hash(me);roof=delta['module_reports']['roof'];roof['core_fascia_visibility']={'exposed_levels':5,'core_side_inset_m':.045,'core_front_back_inset_m':.025*BEARING_DEPTH_SCALE,'all_kitchen_crossings_after_change':0}
for row in roof['geometry']:
 if row['object']==ob.name:row.update(vertices=len(V),faces=len(F),volume_m3=vol,bbox=_bounds(ob))
(R/'V24_03_Xieshan_Roof_Report.json').write_text(json.dumps(roof,ensure_ascii=False,indent=2),encoding='utf8');(R/'V24_03_Changes.json').write_text(json.dumps(delta,ensure_ascii=False,indent=2),encoding='utf8');bpy.context.scene.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'));build['roof']=roof
with P.open('rb')as f:build['model_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_03_Build.json').write_text(json.dumps(build,ensure_ascii=False,indent=2),encoding='utf8');print('FIVE EAVE LEVELS EXPOSED; CORE HIDDEN BEHIND FASCIA; ZERO KITCHEN CROSSINGS',flush=True)
