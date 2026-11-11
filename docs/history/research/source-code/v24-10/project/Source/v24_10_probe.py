import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds
O=W/'v24_10';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_09/Blender/Architecture_Complete_V24_09.blend')
sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and any(s in o.name.upper()for s in ['STORAGE','KITCHEN','SCREENWALL','PERIMETER','TERRAIN','DRAIN','ROAD','TOE','COURT']):
  rows.append({'name':o.name,'bounds':_bounds(o),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name if m else None for m in o.data.materials],'parent':o.parent.name if o.parent else None})
  if ('STORAGE'in o.name or o.name in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry'])and o.type=='MESH':
   v=np.array([o.matrix_world@p.co for p in o.data.vertices]);o.data.calc_loop_triangles();f=np.array([tuple(p.vertices)for p in o.data.loop_triangles]);np.savez_compressed(O/('BASE_'+o.name+'.npz'),v=v,f=f)
(O/'Baseline_Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
d=np.load(O/'AsBuilt_All_LOCAL.npz');me=bpy.data.meshes.new('REF_AsBuilt_Unmodified');me.from_pydata(d['v'].tolist(),[],d['f'].tolist());me.update();ref=bpy.data.objects.new('REF_AsBuilt_Unmodified',me);sc.collection.objects.link(ref)
uv=me.uv_layers.new(name='Original_3dm_UV');uvv=d['uv'];arr=np.array([uvv[l.vertex_index]for l in me.loops],dtype=np.float32);uv.data.foreach_set('uv',arr.ravel())
info=json.loads((O/'AsBuilt_Reference.json').read_text(encoding='utf8'));tex=Path(info['materials'][0]['file'])
if not tex.is_file():
 tex=Path('E:/jz/JIA/Productions/Production_OBJ/Data/Model/Model_0.jpg')
assert tex.is_file(),str(tex)
mat=bpy.data.materials.new('REF_AsBuilt_Original_Photo');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();tx=ns.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(tex));em=ns.new('ShaderNodeEmission');out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tx.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs[0]);me.materials.append(mat)
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=1500;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
base=[o for o in bpy.data.objects if o.type=='MESH'and o!=ref];hide={o.name:o.hide_render for o in base}
for name,pos,tar,ortho,lens in [('Top',(15,-12.5,26),(15,-12.5,0),17,40),('Entry',(11.8,-20.2,2.1),(14.4,-15.1,1.8),None,32),('Oblique',(24,-25,13),(15.5,-13.1,0),None,46)]:
 c=bpy.data.objects.new('Probe_'+name,bpy.data.cameras.new('Probe_'+name));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 sc.camera=c
 for mode in ['BASE','REF']:
  ref.hide_render=mode!='REF'
  for o in base:o.hide_render=True if mode=='REF'else hide[o.name]
  sc.render.filepath=str(O/(mode+'_'+name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER',mode,name,flush=True)
print('DONE_PROBE',len(rows),str(tex),flush=True)
