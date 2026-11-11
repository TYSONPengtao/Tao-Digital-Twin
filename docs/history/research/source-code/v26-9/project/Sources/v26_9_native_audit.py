from pathlib import Path
import bpy,json,numpy as np
W=Path(__file__).parent;D=W/'v26_9';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
rows=[];cams={}
for o in bpy.data.objects:
 if o.type=='CAMERA' and any(k in o.name for k in ['Gate','Storage','Kitchen','Room','Interior','Landing','Stair']):
  cams[o.name]={'position':list(o.matrix_world.translation),'direction':list(o.matrix_world.to_quaternion()@__import__('mathutils').Vector((0,0,-1))),'lens':o.data.lens}
 if o.type!='MESH' or o.hide_render or not any(k in o.name for k in ['V24_Gate_Reference_Relief_Header','V24_Gate_Reference_Relief_P','V24_Gate_Waist']):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])
 fn='EXTRA_'+str(len(rows))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 rows.append({'name':o.name,'file':fn,'materials':[m.name for m in me.materials],'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
(D/'Extra_Source_Index.json').write_text(json.dumps(rows,indent=2),'utf8')
(D/'Existing_Cameras.json').write_text(json.dumps(cams,indent=2),'utf8')
print('NATIVE_EXTRA',len(rows),'CAMERAS',len(cams),flush=True)
