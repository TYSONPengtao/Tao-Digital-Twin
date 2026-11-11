import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_18/Blender/Architecture_Complete_V24_18.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100
c=bpy.data.objects['V24_18_Screen_Valley'];f=c.data.view_frame(scene=sc);x0=min(p.x for p in f);x1=max(p.x for p in f);y0=min(p.y for p in f);y1=max(p.y for p in f);z=f[0].z
for x,y in [(829,401),(829,390),(825,425)]:
 p=Vector((x0+(x+.5)/1200*(x1-x0),y0+(1-(y+.5)/900)*(y1-y0),z));d=(c.matrix_world.to_3x3()@p).normalized();hit,loc,no,idx,o,_=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d,distance=100);print('PIXEL_RAY',x,y,hit,o.name if o else None,list(loc),flush=True)
hits={}
for x in range(795,855,3):
 for y in range(405,505,3):
  p=Vector((x0+(x+.5)/1200*(x1-x0),y0+(1-(y+.5)/900)*(y1-y0),z));d=(c.matrix_world.to_3x3()@p).normalized();hit,loc,no,idx,o,_=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d,distance=100)
  if hit:
   key=o.name;hits.setdefault(key,[]).append([x,y,*loc])
for name,vals in hits.items():print('GRID_RAYS',name,len(vals),vals[:8],flush=True)
for name in ['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']:
 o=bpy.data.objects[name];v=np.array([o.matrix_world@p.co for p in o.data.vertices],dtype=np.float64);uv=o.data.uv_layers.active;bad=[]
 for face in o.data.polygons:
  t=v[list(face.vertices)];no=np.cross(t[1]-t[0],t[2]-t[0]);area=np.linalg.norm(no)/2;no/=max(np.linalg.norm(no),1e-15);u=np.array([uv.data[k].uv[:]for k in face.loop_indices]);err=np.abs(u[:,1]-t[:,2]).max()
  if abs(no[2])<.85 and err>.001:bad.append({'area':area,'n':list(no),'v':t.tolist(),'uv':u.tolist()})
 print('BAD_UV',name,len(bad),bad[:5],flush=True)
