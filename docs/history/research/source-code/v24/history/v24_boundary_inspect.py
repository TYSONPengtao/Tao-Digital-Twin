import bpy,bmesh,json
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_03/Blender/Architecture_Complete_V24_03.blend')
for n in ['SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);rows=[]
 for e in bm.edges:
  if e.is_boundary:rows.append({'length':e.calc_length(),'points':[list(v.co)for v in e.verts],'adjacent_face_area':[f.calc_area()for f in e.link_faces]})
 print(n,json.dumps(rows),flush=True);bm.free()
