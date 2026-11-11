import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V20');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'));sc=bpy.context.scene
rows=[('F1_Hall',[6.5,4.8,2.9],650,.8),('F1_Rear',[10.3,5.4,2.9],350,.7),('F3_Bedroom',[11.2,5.1,10.1],450,.8),('Storage_Interior',[16.2,-12.3,2.15],250,.7),('Storage_Gallery',[16.1,-15.75,2.0],130,.6),('Gate_Soffit',[6.6,-12.25,2.95],90,.5)]
for name,pos,watts,radius in rows:
 key='V20_INSPECTION_'+name;old=bpy.data.objects.get(key)
 if old:bpy.data.objects.remove(old,do_unlink=True)
 ld=bpy.data.lights.new(key,'POINT');ld.energy=watts;ld.shadow_soft_size=radius;ob=bpy.data.objects.new(key,ld);sc.collection.objects.link(ob);ob.location=pos;ob['Purpose']='Inspection lighting for actual native model; not a surveyed fixture'
cam=bpy.data.objects['V20_House_Entry_One_Solid_Step'];cam.location=[8.5,-2.2,1.1];cam.rotation_euler=(Vector([6.5,.25,-.05])-cam.location).to_track_quat('-Z','Y').to_euler()
sc.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'))
names=['V20_House_Stair_Enclosure','V20_House_Rear_Partition','V20_House_Entry_One_Solid_Step','V20_Inner_Gate_Closed_Soffit','V20_Storage_Aligned_Gallery','V20_Storage_Interior','V20_F3_Bedroom_Inward_Door']
for n in names:
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(O/'06_Report'/f'{n}.png');bpy.ops.render.render(write_still=True);print('INSPECTED',n,flush=True)
# The changed camera and all default-open pivot geometry are exported again. Lights stay in the local review file only.
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V20_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)
(O/'06_Report/Interior_Inspection_Lighting.json').write_text(json.dumps({'view_names':names,'point_lights':rows,'geometry_visibility':'All original native indexed geometry retained and visible','purpose':'Local preview illumination, not as-built fixtures','changed_entry_camera':[8.5,-2.2,1.1]},indent=2),encoding='utf8')
print('INSPECTION LIGHTING COMPLETE')
