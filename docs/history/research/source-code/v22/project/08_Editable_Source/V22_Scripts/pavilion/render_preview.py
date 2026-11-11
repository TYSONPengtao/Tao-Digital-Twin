import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
D=Path(__file__).parent;B=Path('E:/jz/JIA/Rebuild_V21');Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(B/'05_Export/Actual_Rhino_V21_Readback_LOCAL.blend'))
sc=bpy.context.scene
for m,md in Q['materials'].items():
 mat=bpy.data.materials.new(m);mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=tuple((c/255)**2.2 for c in md['color'])+(1,);bs.inputs['Roughness'].default_value=md['roughness'];bs.inputs['Metallic'].default_value=md.get('metallic',0)
 if md.get('bitmap'):
  tx=mat.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(md['bitmap']);mat.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
for r in json.loads((D/'Preview_Meshes.json').read_text(encoding='utf8')):
 n=r['name'];old=bpy.data.objects.get(n+'_Geometry')
 if old:bpy.data.objects.remove(old,do_unlink=True)
 me=bpy.data.meshes.new(n+'_V22');me.from_pydata(r['vertices'],[],r['faces']);me.update();ob=bpy.data.objects.new(n+'_V22Preview',me);sc.collection.objects.link(ob)
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',r['material_ids']);uv=me.uv_layers.new(name='Planar_review')
 for po in me.polygons:
  axes=[i for i in range(3) if i!=int(np.argmax(np.abs(po.normal)))];scale=[.25,1]
  for i in po.loop_indices:
   co=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])
for n,p,t,fov in Q['cameras']:
 cd=bpy.data.cameras.new(n);cam=bpy.data.objects.new(n,cd);sc.collection.objects.link(cam);cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.frame_set(40)
for n,*_ in Q['cameras']:
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(D/(n+'.png'));bpy.ops.render.render(write_still=True)
(D/'Preview_Provenance.json').write_text(json.dumps({'note':'Source-patch preview over actual V21 native background. Final saved V22 readback render belongs to root integration.','views':Q['cameras']},indent=2),encoding='utf8')
print('V22 PAVILION PREVIEW DONE',flush=True)
