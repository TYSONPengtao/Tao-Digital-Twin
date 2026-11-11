import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_17';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_16/Blender/Architecture_Complete_V26_16.blend');sc=bpy.context.scene;sc.frame_set(40)
prep=json.loads((D/'Prepared.json').read_text('utf8'))
for row in prep['objects']:
 a=np.load(D/'Prepared'/row['file']);o=bpy.data.objects[row['name']];me=bpy.data.meshes.new('Probe_'+row['name']);inv=o.matrix_world.inverted();me.from_pydata([inv@Vector(v)for v in a['v']],[],a['f'].astype(np.int64).tolist())
 for name in row['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.uv_layers.new(name='ProbeUV').data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o.data=me
cam=bpy.data.objects.new('Probe',bpy.data.cameras.new('Probe'));sc.collection.objects.link(cam);cam.location=(6.2,-1.7,1.3);cam.rotation_euler=(Vector((9.05,1.96,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=31;sc.camera=cam;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();M=(cam.calc_matrix_camera(deps,x=1000,y=1100)@cam.matrix_world.inverted()).inverted();out=[]
for x,y in[(490,951),(500,940),(520,960),(550,960),(530,980),(715,1006),(740,1000),(760,988),(725,980),(680,1020),(800,1030)]:
 p=M@Vector((x/500-1,1-y/550,1,1));p=p.xyz/p.w;ray=(p-cam.location).normalized();yes,pos,no,index,ob,mat=sc.ray_cast(deps,cam.location,ray);poly=ob.data.polygons[index];out.append({'pixel':[x,y],'object':ob.name,'position':list(pos),'normal':list(no),'face':index,'material':ob.data.materials[poly.material_index].name,'world_vertices':[list(ob.matrix_world@ob.data.vertices[i].co)for i in poly.vertices],'uv':[list(ob.data.uv_layers.active.data[i].uv)for i in poly.loop_indices]})
(D/'Floor_Pixel_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('FLOOR_PROBE_SAVED',flush=True)
