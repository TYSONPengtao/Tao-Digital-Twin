import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_33';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);dg=bpy.context.evaluated_depsgraph_get();out=[]
ix=json.loads((D/'Geometry_Index.json').read_text('utf8'));known={r['name'] for r in ix};inventory={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
targets=[n for n in inventory if any(t in n for t in ['CANOPY_CENTER','V24_10_Entry_Continuous_Threshold','V24_31_Continuous_Gray_Road','V24_22_Outer_Stepped','V24_22_Porch_Single','V24_23_Kitchen_North_End']) and inventory[n]['type']=='MESH']
for n in targets:
 if n in known:continue
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:] for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:] for i in t.loops]for t in me.loop_triangles]) if me.uv_layers.active else np.zeros((len(f),3,2));fn='SRC_'+str(len(ix))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);ix.append(dict(inventory[n],file=fn,vertices=len(v),triangles=len(f)))
(D/'Geometry_Index.json').write_text(json.dumps(ix,ensure_ascii=False),encoding='utf8')
def ray(tag,ori,di):
 h,p,n,fi,o,ma=sc.ray_cast(dg,Vector(ori),Vector(di),distance=30);r={'tag':tag,'point':list(p) if h else None,'normal':list(n) if h else None,'face':int(fi),'object':o.name if h else None,'material':o.data.materials[o.data.polygons[fi].material_index].name if h and fi>=0 and o.data.materials else None};out.append(r);print(r,flush=True)
tag,pos,aim,lens=json.loads((D/'Last_Diagnostic_Views.json').read_text('utf8'))[0];c=bpy.data.cameras.new(tag);ob=bpy.data.objects.new(tag,c);sc.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler();c.lens=lens;sc.render.resolution_x=960;sc.render.resolution_y=800;fr=c.view_frame(scene=sc);xl=min(v.x for v in fr);xh=max(v.x for v in fr);yl=min(v.y for v in fr);yh=max(v.y for v in fr);bpy.context.view_layer.update()
for px,py in [(338,150),(341,95),(340,63),(358,250)]:
 local=Vector((xl+(xh-xl)*px/960,yh-(yh-yl)*py/800,fr[0].z));ray('WOOD_'+str((px,py)),pos,(ob.matrix_world.to_3x3()@local).normalized())
for x,y in [(12.5,-15.),(12.8,-15.5),(13.1,-15.5),(13.2,-16.2),(13.5,-16.),(13.6,-15.0),(12.0,-15.0),(12.5,-14.8)]:
 row={'xy':[x,y],'surfaces':[]}
 for name in ['V24_10_Entry_Continuous_Threshold','V24_31_Continuous_Gray_Road_And_Storage_Approach','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V14_INNER_STORAGE_FLOOR_Geometry']:
  o=bpy.data.objects[name];iv=o.matrix_world.inverted();ori=iv@Vector((x,y,0.));di=(iv.to_3x3()@Vector((0,0,-1))).normalized();h,p,no,fi=o.ray_cast(ori,di,distance=10)
  if h:row['surfaces'].append({'object':name,'z':(o.matrix_world@p).z})
 out.append(row);print(row,flush=True)
(D/'Extra_Probes_Before.json').write_text(json.dumps(out,indent=2),encoding='utf8')
