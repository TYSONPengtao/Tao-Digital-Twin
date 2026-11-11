"""Section previews only; native/mesh deliveries are not modified."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
O=Path(r'E:\jz\JIA\Rebuild_V5')
for floor,z in [(1,0),(2,3.9),(3,7.5)]:
 bpy.ops.wm.open_mainfile(filepath=str(O/'08_Export/Production_1QK_ARCH.blend'))
 sc=bpy.context.scene
 for ob in list(sc.objects):
  if ob.type!='MESH':continue
  if ob.hide_render:continue
  if ob.get('Layer') in ['60_SITE','80_CONTEXT','90_UNCERTAIN','50_ROOF','51_CANOPY','01_GRID','02_LEVEL','99_HELPER']:
   ob.hide_render=True;continue
  coords=[ob.matrix_world@v.co for v in ob.data.vertices];lo=min(p.z for p in coords);hi=max(p.z for p in coords)
  if hi<z-.17 or lo>z+2.3:ob.hide_render=True;continue
  ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data)
  for plane,above in [(z-.17,False),(z+2.3,True)]:
   localp=ob.matrix_world.inverted()@Vector((0,0,plane));normal=ob.matrix_world.to_3x3().transposed()@Vector((0,0,1))
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=localp,plane_no=normal,clear_outer=above,clear_inner=not above)
  bm.to_mesh(ob.data);bm.free();ob.data.update()
  if not len(ob.data.polygons):ob.hide_render=True
 cd=bpy.data.cameras.new('V5_Floor_Review');cam=bpy.data.objects.new('V5_Floor_Review',cd);sc.collection.objects.link(cam);cam.location=(18,-15,z+19);target=Vector((6.5,5.5,z+.8));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=20
 sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=20;sc.render.resolution_x=1400;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.filepath=str(O/'09_Report'/f'V5_F{floor}_Interior_Cutaway.png');bpy.ops.render.render(write_still=True)
print('Three independent floor cutaway previews rendered; delivery geometry unchanged')
