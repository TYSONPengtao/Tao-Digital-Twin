from pathlib import Path
import bpy,json,hashlib,collections,numpy as np
W=Path(__file__).parent;D=W/'v25';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rows=[];used=set();complex_names=[]
for o in sc.objects:
 if o.hide_render or o.type not in ['MESH','CURVE','FONT','SURFACE','META']:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=deps)
 if not me or not len(me.polygons):
  if me:ev.to_mesh_clear()
  continue
 me.calc_loop_triangles();mats=[m.name if m else None for m in me.materials];used.update(m for m in mats if m);row={'name':o.name,'type':o.type,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'materials':mats,'uv_layers':[u.name for u in me.uv_layers],'collections':[c.name for c in o.users_collection],'parent':o.parent.name if o.parent else None,'props':{k:str(o[k])[:600]for k in o.keys()if k!='_RNA_UI'},'modifiers':[(m.name,m.type,m.show_render,m.show_viewport)for m in o.modifiers],'smooth_faces':sum(p.use_smooth for p in me.polygons),'corner_normals':len(me.corner_normals)};rows.append(row);ev.to_mesh_clear()
for name in sorted(used):
 m=bpy.data.materials[name]
 if not m.use_nodes:continue
 bs=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'];base=bs[0].inputs['Base Color']if len(bs)==1 else None;direct=base is not None and(not base.is_linked or(len(base.links)==1 and base.links[0].from_node.type=='TEX_IMAGE'and(not base.links[0].from_node.inputs['Vector'].is_linked or base.links[0].from_node.inputs['Vector'].links[0].from_node.type=='UVMAP')))
 if not direct:complex_names.append(name)
out={'source':str(P),'source_sha256':hashlib.file_digest(P.open('rb'),'sha256').hexdigest(),'visible_objects':len(rows),'visible_triangles':sum(r['triangles']for r in rows),'material_count':len(used),'complex_materials':complex_names,'complex_objects':[r['name']for r in rows if any(m in complex_names for m in r['materials'])],'rows':rows};(D/'Blender_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('SOURCE_PROBE',{k:v for k,v in out.items()if k not in ['rows','complex_objects']},flush=True);print('COMPLEX_OBJECTS',len(out['complex_objects']),out['complex_objects'][:30],flush=True)
