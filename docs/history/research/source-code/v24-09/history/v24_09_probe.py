import bpy,sys,json,bmesh
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds,_closed_stats
R=W/'v24_09_probe';R.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_08/Blender/Architecture_Complete_V24_08.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and('SCREEN'in o.name or o.name in['SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']):rows.append({'name':o.name,'bounds':_bounds(o),'materials':[m.name for m in o.data.materials],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'geometry':_closed_stats(o)})
(R/'Inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_shadows=True;ds.background_type='WORLD';sc.world.color=(.15,.15,.15)
for n,pos,tar,lens,ortho in [('Outside',(7,-29,3.8),(7,-16.9,2.3),38,10.5),('Inside',(7,-11,3.0),(7,-16.9,2.8),24,None),('Roof',(11,-21,7),(7,-16.9,4.0),48,None),('End',(13,-17,4.7),(10.6,-16.9,4.1),42,None)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 sc.camera=c;sc.render.filepath=str(R/(n+'.png'));bpy.ops.render.render(write_still=True);print('VIEW',n,flush=True)
