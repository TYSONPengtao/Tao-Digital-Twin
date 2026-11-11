from pathlib import Path
import bpy,bmesh,numpy as np,json,time
W=Path(__file__).parent;D=W/'v26_2';p=json.loads((D/'Exact_House_Parts.json').read_text('utf8'));bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
names=['M_Wall_Interior','M_Floor','M_V24_31_White_Painted_Ceiling','M_V24_31_Stair_Gray_Marble','M_V21_House_Exterior_Grey_White']
for r in p['extras']:
 for n in r['materials']:
  if n not in names:names.append(n)
for n in names:bpy.data.materials.new(n)
col=bpy.data.collections.new('Exact_Operands');sc.collection.children.link(col);objs=[]
for r in p['layers']+p['extras']:
 a=np.load(D/r['file']);me=bpy.data.meshes.new(r['name']);me.from_pydata(a['v'],[],a['f'])
 for n in names:me.materials.append(bpy.data.materials[n])
 ids=np.array([names.index(r['materials'][j])for j in a['mi']],np.int32);me.polygons.foreach_set('material_index',ids);uv=me.uv_layers.new(name='Source_Photo_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o=bpy.data.objects.new(r['name'],me);(sc.collection if not objs else col).objects.link(o);objs.append(o)
o=objs[0];bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Exact_Registered_Wall_Core_Union','BOOLEAN');mod.operation='UNION';mod.operand_type='COLLECTION';mod.collection=col;mod.solver='EXACT';mod.use_hole_tolerant=True;t0=time.perf_counter();print('EXACT_BEGIN',len(objs),sum(len(x.data.polygons)for x in objs),flush=True);bpy.ops.object.modifier_apply(modifier=mod.name);print('EXACT_APPLIED',len(o.data.polygons),'seconds',time.perf_counter()-t0,flush=True)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad_edges=sum(not e.is_manifold for e in bm.edges);bad_faces=sum(f.calc_area()<1e-12 for f in bm.faces);volume=bm.calc_volume(signed=True);bm.to_mesh(o.data);bm.free();me=o.data;me.update();me.calc_loop_triangles();v=np.array([x.co[:]for x in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);tr=v[f];n=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(n,axis=1)/2;n/=np.maximum(2*area[:,None],1e-30);c=tr.mean(1)
mi[(n[:,2]<-.7)&(c[:,2]>-.4)]=names.index('M_V24_31_White_Painted_Ceiling')
for z in [-.45,3.45,7.05]:mi[(n[:,2]>.999)&(abs(c[:,2]-z)<.0002)]=names.index('M_Floor')
for z in [1.5,5.25]:mi[(n[:,2]>.999)&(abs(c[:,2]-z)<.0003)]=names.index('M_V24_31_Stair_Gray_Marble')
mask=((n[:,0]<-.99)&(c[:,0]<-.09)|(n[:,0]>.99)&(c[:,0]>13.09)|(n[:,1]>.99)&(c[:,1]>9.89))&(c[:,2]<10.221)&(c[:,2]>-.45);mi[mask]=names.index('M_V21_House_Exterior_Grey_White')
fn='V26_2_House_Flush_Continuous_Finished_Shell.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi.astype(np.int32),uv=uv)
proof={'solver':'Blender EXACT Boolean union of analytic height layers and original actual core profiles','elapsed_seconds':time.perf_counter()-t0,'nonmanifold_edges':bad_edges,'zero_area_polygon_faces':bad_faces,'zero_area_triangles':int((area<1e-12).sum()),'signed_volume_m3':volume,'triangles':len(f),'operands':len(objs),'canonical_grid_m':.0001,'maximum_internal_vertical_join_overlap_m':.00005};(D/'Exact_House_QA.json').write_text(json.dumps(proof,indent=2));row={'name':'V26_2_House_Flush_Continuous_Finished_Shell','file':fn,'materials':names,'triangles':len(f),'volume_m3':volume,'reason':'Continuous wall finishes and real registered apertures; clean topology from analytic plans and original beam column slab stair roof profiles using Blender exact union'}
out={'objects':[row]+p['frames'],'archive':['V26_1_House_Continuous_Opaque_Shell'],'proof':dict(p['proof'],exact_union=proof)};(D/'Prepared_House.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('EXACT_HOUSE_READY',json.dumps(proof),flush=True)
