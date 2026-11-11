import bpy,sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_09/Blender/Architecture_Complete_V24_09.blend');bpy.context.scene.frame_set(1);bpy.context.view_layer.update();out=[]
for o in bpy.data.objects:
 if o.type=='MESH'and not o.hide_render:
  p=np.array([o.matrix_world@v.co for v in o.data.vertices]);ok=(p[:,0]>10.8)&(p[:,0]<13.8)&(p[:,1]>-17.5)&(p[:,1]<-14.0)&(p[:,2]>-.65)&(p[:,2]<3.2)
  if ok.any():out.append({'name':o.name,'vertices':int(ok.sum()),'local_bounds':[p[ok].min(0).tolist(),p[ok].max(0).tolist()]})
  if 'PERIMETER'in o.name:
   ok=(p[:,0]>10.85)&(p[:,0]<13.45)&(p[:,1]>-17.5)&(p[:,1]<-16.0)
   if ok.any():
    o.data.calc_loop_triangles();f=np.array([x.vertices for x in o.data.loop_triangles]);np.savez_compressed(W/'v24_10'/('WING_'+o.name+'.npz'),v=p,f=f)
(W/'v24_10/Entry_Node_Probe.json').write_text(json.dumps(out,indent=2),encoding='utf8');print('DONE_ENTRY_PROBE',len(out),flush=True)
