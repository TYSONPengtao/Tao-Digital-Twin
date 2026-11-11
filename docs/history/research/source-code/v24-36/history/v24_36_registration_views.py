import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_36';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_35/Blender/Architecture_Complete_V24_35.blend');sc=bpy.context.scene;sc.frame_set(40);T=np.array(json.loads((D/'Coordinate_Seed.json').read_text('utf8'))['seed_source_to_local']);rows=json.loads((D/'Registration_Source_Index.json').read_text('utf8'));old=[o for o in bpy.data.objects if o.type=='MESH' and 'SITE_V14_ORIGINAL_EXTERIOR_' in o.name];new=[];col=bpy.data.collections.new('MB7_Geographic_Probe');sc.collection.children.link(col)
def emission(name,image):
 m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();out=ns.new('ShaderNodeOutputMaterial');tex=ns.new('ShaderNodeTexImage');tex.image=image;em=ns.new('ShaderNodeEmission');m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
for o in old:
 ims=[next(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image) for m in o.data.materials];o.data=o.data.copy();o.data.materials.clear()
 for i,im in enumerate(ims):o.data.materials.append(emission('OLD_Baked_'+o.name+str(i),im))
for r in rows:
 a=np.load(D/r['file']);v=a['v']@T[:3,:3].T+T[:3,3];me=bpy.data.meshes.new('Probe_'+r['node']);me.from_pydata(v,[],a['f']);me.polygons.foreach_set('material_index',a['mi']);me.update();uv=me.uv_layers.new(name='Source_UV')
 for p,t in zip(me.polygons,a['uv']):
  for k,q in zip(p.loop_indices,t):uv.data[k].uv=q
 for texture in r['textures']:me.materials.append(emission('MB7_Baked_'+Path(texture['file']).stem,bpy.data.images.load(str(D/texture['file']))))
 o=bpy.data.objects.new('Probe_'+r['node'],me);col.objects.link(o);new.append(o)
for o in bpy.data.objects:o.hide_render=o not in old
sc.render.engine='CYCLES';sc.cycles.samples=1;sc.cycles.use_denoising=False
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for x in p.devices:x.use=x.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
sc.world=bpy.data.worlds.new('RegistrationVoid');sc.world.color=(0.,0.,0.);sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.view_settings.exposure=0;sc.render.resolution_x=2560;sc.render.resolution_y=2560;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';cam=bpy.data.objects.new('RegistrationCamera',bpy.data.cameras.new('RegistrationCamera'));sc.collection.objects.link(cam);cam.location=(7.,0.,200.);cam.rotation_euler=(0,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=156.;cam.data.clip_start=.1;cam.data.clip_end=400.;sc.camera=cam
for tag,objects in [('Existing_Context_Top',old),('PTJIA6_Geographic_Seed_Top',new)]:
 for o in old+new:o.hide_render=o not in objects
 sc.render.filepath=str(D/(tag+'.png'));bpy.ops.render.render(write_still=True);print('REG_VIEW',tag,flush=True)
(D/'Registration_Projection.json').write_text(json.dumps({'center_xy_m':[7.,0.],'width_m':156.,'resolution':[2560,2560],'source_matrix':T.tolist()}),encoding='utf8')
