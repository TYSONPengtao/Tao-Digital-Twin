import bpy,json,numpy as np,sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_13';P=Path('E:/jz/JIA/Rebuild_V26_12/Blender/Architecture_Complete_V26_12.blend');bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
ch=json.loads(Path('E:/jz/JIA/Rebuild_V26_12/Reports/V26_12_Changes.json').read_text('utf8'));rows=[]
for r in ch['restored']:
 o=bpy.data.objects[r['name']];me=o.data;me.calc_loop_triangles();v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);fn='Input_'+o.name+'.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv,mi=mi);rows.append({**r,'file':fn,'materials':[m.name for m in me.materials],'mesh_hash':q._mesh_hash(me)})
(D/'Input_Reliefs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8');print('EXPORTED',len(rows),flush=True)
