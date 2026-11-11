import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
D=Path(__file__).parent/'v24_31';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_31/Blender/Architecture_Complete_V24_31.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1600;sc.render.resolution_y=1100;dg=bpy.context.evaluated_depsgraph_get();out={}
for tag in ['Stair_Lower_Reference','Stair_Smooth_White_Wall']:
 c=bpy.data.objects['V24_31_'+tag];fr=c.data.view_frame(scene=sc);xl=min(p.x for p in fr);xh=max(p.x for p in fr);yl=min(p.y for p in fr);yh=max(p.y for p in fr);zz=fr[0].z;rows=[];names=[]
 for py in range(10,1100,20):
  row=[]
  for px in range(10,1600,20):
   d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1600,yh-(yh-yl)*py/1100,zz))).normalized();ok,loc,no,i,o,mat=sc.ray_cast(dg,c.location,d,distance=30)
   n=o.name if ok else 'BACKGROUND'
   if n not in names:names.append(n)
   row.append([names.index(n),list(loc)if ok else None])
  rows.append(row)
 out[tag]={'names':names,'grid':rows}
 print(tag,'names',names,flush=True)
 if tag=='Stair_Lower_Reference':
  for px,py in [(1240,350),(1280,350),(1260,380),(1280,400),(1250,450),(1300,480),(1300,500)]:
   d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1600,yh-(yh-yl)*py/1100,zz))).normalized();ok,loc,no,i,o,mat=sc.ray_cast(dg,c.location,d,distance=30);print('EXACT',px,py,o.name if ok else None,list(loc),list(world_to_camera_view(sc,c,loc))if ok else None,flush=True)
 if tag=='Stair_Smooth_White_Wall':
  for px,py in [(555,760),(570,650),(540,850),(550,940),(590,810),(570,830),(545,960),(600,680)]:
   d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1600,yh-(yh-yl)*py/1100,zz))).normalized();ok,loc,no,i,o,mat=sc.ray_cast(dg,c.location,d,distance=30);print('STRIPE',px,py,o.name if ok else None,list(loc),flush=True)
(D/'Object_ID_Grid.json').write_text(json.dumps(out),encoding='utf8')
for o in bpy.data.objects:
 if o.type=='MESH'and 'DOOR_'in o.name and '__FRAME' in o.name:
  vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(p[i]for p in vs)for i in range(3)];hi=[max(p[i]for p in vs)for i in range(3)]
  if lo[0]<4.15 and hi[0]>3.7 and lo[1]>7.:print('LEFT_STAIR_DOOR',o.name,lo,hi,flush=True)
