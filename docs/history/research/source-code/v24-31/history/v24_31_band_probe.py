import bpy,numpy as np
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_31/Blender/Architecture_Complete_V24_31.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1120;sc.render.resolution_y=800;c=bpy.data.objects['V24_31_Stair_Lower_Reference'];bpy.context.view_layer.update();fr=c.data.view_frame(scene=sc);xl=min(p.x for p in fr);xh=max(p.x for p in fr);yl=min(p.y for p in fr);yh=max(p.y for p in fr);zz=fr[0].z
for px,py in [(780,190),(840,190),(900,190),(960,190),(840,220),(900,220),(960,220),(1000,155),(850,150),(780,150)]:
 d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1120,yh-(yh-yl)*py/800,zz))).normalized();ok,loc,no,i,o,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d,distance=50);print('PIXEL',px,py,o.name if ok else None,list(loc),flush=True)
for n in ['FLOOR_FASCIA_CONTINUOUS_F2_Geometry','SLAB_JOINED_F2_Geometry','BEAM_X_F1_9.8_3.9_Geometry']:
 o=bpy.data.objects[n];v=np.array([o.matrix_world@p.co for p in o.data.vertices]);v=v[(v[:,0]>=4)&(v[:,0]<=9)&(v[:,1]>9.3)];print(n,'rear vertices',np.unique(np.round(v,5),axis=0).tolist(),flush=True)
