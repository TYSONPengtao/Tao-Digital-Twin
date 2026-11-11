import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
D=Path(__file__).parent
Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V21/05_Export/Actual_Rhino_V21_Readback_LOCAL.blend')
sc=bpy.context.scene
for e in Q['replace']:
 n=e['name'];par=bpy.data.objects.get(n)
 if par:
  for ob in list(par.children):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.objects.remove(par,do_unlink=True)
for n,md in Q['materials'].items():
 m=bpy.data.materials.new(n);m.use_nodes=True;bs=next(a for a in m.node_tree.nodes if a.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=tuple((c/255)**2.2 for c in md['color'])+(1,);bs.inputs['Roughness'].default_value=md['roughness']
for e in Q['replace']+Q['add']:
 for j,p in enumerate(e['parts']):
  g=p['geometry'];v=np.array(g['vertices']);f=np.array(g['faces'])
  me=bpy.data.meshes.new(e['name']+str(j));me.from_pydata(v.tolist(),[],f.tolist());me.update()
  ob=bpy.data.objects.new(e['name']+str(j),me);sc.collection.objects.link(ob);me.materials.append(bpy.data.materials[p['material']])
  uv=me.uv_layers.new(name='Native_Projection')
  for pol in me.polygons:
   axes=[k for k in range(3) if k!=int(np.argmax(np.abs(pol.normal)))]
   for li in pol.loop_indices:uv.data[li].uv=v[me.loops[li].vertex_index,axes]
sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True
sc.render.resolution_x=1400;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
for n,pos,tar,fov in Q['cameras']:
 cd=bpy.data.cameras.new(n);cam=bpy.data.objects.new(n,cd);sc.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov);sc.camera=cam
 sc.render.filepath=str(D/(n+'.png'));bpy.ops.render.render(write_still=True);print('DONE',n,flush=True)
