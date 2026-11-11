import bpy,math,json
from mathutils import Vector
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V21/05_Export/Actual_Rhino_V21_Readback_LOCAL.blend')
sc=bpy.context.scene;c=sc.camera;c.location=[1.45,4.2,8.95];c.rotation_euler=(Vector([3.82,6.3,8.7])-c.location).to_track_quat('-Z','Y').to_euler();c.data.angle=math.radians(78);sc.render.resolution_x=1100;sc.render.resolution_y=760
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();vf=c.data.view_frame(scene=sc)
res=[]
for px,py in [(454,440),(485,199),(469,550),(494,448),(440,440),(420,440)]:
 x=(px/1100*2-1)*max(v.x for v in vf);y=(1-py/760*2)*max(v.y for v in vf);z=vf[0].z
 di=c.matrix_world.to_3x3()@Vector((x,y,z));di.normalize();hit,loc,no,i,ob,mat=sc.ray_cast(dep,c.location,di)
 r={'pixel':[px,py],'hit':hit,'object':ob.name if ob else None,'loc':list(loc),'normal':list(no)}
 if ob and ob.type=='MESH':
  r['material']=ob.data.materials[ob.data.polygons[i].material_index].name;r['poly_index']=i
 res.append(r)
Path('work/v21_house/Jamb_Raycast.json').write_text(json.dumps(res,indent=2));print(res)
