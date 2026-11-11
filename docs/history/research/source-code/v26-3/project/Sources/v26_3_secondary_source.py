from pathlib import Path
import bpy,numpy as np,json
W=Path(__file__).parent;D=W/'v26_3';P=Path('E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();rows=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','V24_21_Exterior_Continuous_White_Frieze','V24_21_Exterior_Long_Short_Stepped_Frames','V24_21_Exterior_Stepped_Cornices']:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn='ORIGINAL_LOCAL_'+str(len(rows))+'.npz';extra={}
 if n.startswith('SITE_PERIMETER'):extra['height_attribute']=np.array([d.value for d in me.attributes['V24_20_Height_Above_Finish_Division'].data])
 np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv,**extra);rows.append({'name':n,'file':fn,'materials':[m.name for m in me.materials],'triangles':len(f)})
(D/'Original_Secondary_Surfaces.json').write_text(json.dumps({'source':str(P),'objects':rows},ensure_ascii=False,indent=2),encoding='utf8');print('ORIGINAL_LOCAL_SURFACES',rows,flush=True)
