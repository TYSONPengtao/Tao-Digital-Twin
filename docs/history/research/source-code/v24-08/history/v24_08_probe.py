import bpy,json,sys,bmesh,math,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds
R=W/'v24_08_probe';R.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_07/Blender/Architecture_Complete_V24_07.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH':rows.append({'name':o.name,'bounds':_bounds(o),'materials':[m.name for m in o.data.materials],'vertices':len(o.data.vertices),'faces':len(o.data.polygons)})
(R/'Inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
out={}
names=['SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS_Geometry']
for n in names:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);left=set(bm.verts);comps=[]
 while left:
  v=left.pop();part={v};stack=[v]
  while stack:
   for e in stack.pop().link_edges:
    for q in e.verts:
     if q in left:left.remove(q);part.add(q);stack.append(q)
  pts=[o.matrix_world@v.co for v in part];comps.append({'bounds':[[min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)]],'vertices':len(part)})
 bm.free();out[n]=comps
(R/'Components.json').write_text(json.dumps(out,indent=2),encoding='utf8')
mats={}
for n in ['M_Grey_Brick','M_V19_Perimeter_Brick','M_V19_Perimeter_Rubble','M_V19_Perimeter_Dark_Stone','M_V19_Limewash_Band','M_V18_Metal_Weathered']:
 m=bpy.data.materials[n];mats[n]={'nodes':[{'name':x.name,'type':x.type,'inputs':{s.name:list(s.default_value)if hasattr(s.default_value,'__len__')and not isinstance(s.default_value,str)else str(s.default_value)for s in x.inputs if hasattr(s,'default_value')},'image':x.image.name if x.type=='TEX_IMAGE'and x.image else None}for x in m.node_tree.nodes]}
 for x in m.node_tree.nodes:
  if x.type=='TEX_IMAGE'and x.image and x.image.packed_file:
   im=x.image;(R/im.name).write_bytes(bytes(im.packed_file.data))
(R/'Materials.json').write_text(json.dumps(mats,indent=2),encoding='utf8')
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1440;sc.render.resolution_y=1080;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_shadows=True;ds.background_type='WORLD';sc.world.color=(.15,.15,.15)
for n,pos,tar,lens,ortho in [('Exterior',(29,12,12),(10,-4,.8),45,None),('Kitchen_North',(16,7,5),(10.5,-2.5,1.4),40,None),('Court',(6.5,-11,1.7),(6.5,0,1.6),24,None),('Plan',(7,-6,30),(7,-6,0),50,22)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 sc.camera=c;sc.render.filepath=str(R/(n+'.png'));bpy.ops.render.render(write_still=True)
print('PROBE COMPLETE',flush=True)
