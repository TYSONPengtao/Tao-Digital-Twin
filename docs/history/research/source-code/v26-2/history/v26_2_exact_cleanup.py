from pathlib import Path
import bpy,bmesh,numpy as np,json
W=Path(__file__).parent;D=W/'v26_2';p=json.loads((D/'Prepared_House.json').read_text('utf8'));r=p['objects'][0];a=np.load(D/r['file']);bpy.ops.wm.read_factory_settings(use_empty=True);me=bpy.data.meshes.new('Final_House_Surface_Cleanup');me.from_pydata(a['v'],[],a['f'])
for n in r['materials']:me.materials.append(bpy.data.materials.new(n))
me.polygons.foreach_set('material_index',a['mi']);uv=me.uv_layers.new();uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());bm=bmesh.new();bm.from_mesh(me)
for i in range(6):
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);deg=[f for f in bm.faces if f.calc_area()<1e-12]
 if deg:bmesh.ops.delete(bm,geom=deg,context='FACES_ONLY')
 loose=[e for e in bm.edges if not e.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
 # Collapsed coplanar slivers are T-junctions: one side has A--C while the
 # other has A--B--C. Split the long edge at B, rather than filling a zero-area
 # triangle, so the two sides share the same true topological edge.
 boundary=[e for e in bm.edges if e.is_boundary];verts=list({v for e in boundary for v in e.verts});points=np.array([v.co[:]for v in verts]);splits=0
 for edge in list(boundary):
  if not edge.is_valid:continue
  va,vb=edge.verts[:];a0=np.array(va.co);b0=np.array(vb.co);d=b0-a0;length=np.linalg.norm(d)
  if length<1e-6:continue
  u=((points-a0)@d)/(length*length);near=np.linalg.norm(points-(a0+u[:,None]*d),axis=1);ids=np.where((u>2e-6/length)&(u<1-2e-6/length)&(near<2e-6))[0]
  current=edge;start=va
  for j in sorted(ids,key=lambda j:u[j]):
   if not current.is_valid or not start.is_valid:break
   target=points[j];s=np.array(start.co);end=np.array(vb.co);frac=np.dot(target-s,end-s)/max(np.dot(end-s,end-s),1e-30)
   if not 1e-6<frac<1-1e-6:continue
   ne,nv=bmesh.utils.edge_split(current,start,float(frac));nv.co=target;rest=next((e for e in nv.link_edges if vb in e.verts),None);splits+=1
   if rest is None:break
   current=rest;start=nv
 if splits:bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-6)
 bad=[e for e in bm.edges if not e.is_manifold];print('CLEANUP',i,'zero_faces',len(deg),'edge_splits',splits,'invalid',len(bad),[(len(e.link_faces),[list(v.co)for v in e.verts])for e in bad][:10],flush=True)
 boundary=[e for e in bad if e.is_boundary]
 if boundary and not splits:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=[e for e in bm.edges if not e.is_manifold];volume=bm.calc_volume(signed=True);bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles();v=np.array([x.co[:]for x in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);t=v[f];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
np.savez_compressed(D/r['file'],v=v,f=f,mi=mi,uv=uv);qa=p['proof']['exact_union'];qa.update(cleanup_merge_distance_m=.00001,nonmanifold_edges=len(bad),zero_area_triangles=int((area<1e-12).sum()),signed_volume_m3=volume,triangles=len(f));r.update(triangles=len(f),volume_m3=volume);(D/'Prepared_House.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8');(D/'Exact_House_QA.json').write_text(json.dumps(qa,indent=2));print('CLEAN_HOUSE_FINAL',json.dumps(qa),flush=True)
