import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _bounds
P='E:/jz/JIA/Rebuild_V24_03/Blender/Architecture_Complete_V24_03.blend'
R=W/'v24_04_probe';R.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=P);sc=bpy.context.scene;sc.frame_set(40)
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 lo,hi=_bounds(o)
 if hi[0]<6.5 or lo[0]>14 or hi[1]<-3.5 or lo[1]>0:continue
 rows.append({'name':o.name,'bounds':[lo,hi],'materials':[m.name for m in o.data.materials if m]})
(R/'near_rear.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS_Geometry','SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry']:
 o=bpy.data.objects[n];p=[tuple(o.matrix_world@v.co) for v in o.data.vertices];p=[v for v in p if 6.5<v[0]<14 and -3.5<v[1]<0]
 (R/(n+'.json')).write_text(json.dumps({'materials':[m.name for m in o.data.materials if m],'points':p}),encoding='utf8')
sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
ds=sc.display.shading;ds.light='STUDIO';ds.studiolight_rotate_z=.4;ds.color_type='MATERIAL';ds.show_shadows=True;ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_object_outline=True;ds.background_type='WORLD';sc.world.color=(.15,.15,.15)
for name,pos,tar,lens in [('Rear_West',(4.2,-.6,2.1),(9.6,-2.8,1.5),28),('Rear_East',(15,-.9,3.4),(10.3,-2.8,1.8),24),('Rear_Close',(5.9,-1.55,1.3),(8.0,-2.7,1.3),30),('Gate_Rear',(4.6,-7.4,2.5),(6.6,-11.9,2.1),25)]:
 c=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;sc.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
print('PROBE COMPLETE',flush=True)
