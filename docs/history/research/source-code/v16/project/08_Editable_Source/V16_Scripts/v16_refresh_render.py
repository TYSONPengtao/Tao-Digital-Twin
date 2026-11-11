import bpy,json,math
from pathlib import Path
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V16');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V16_Readback_LOCAL.blend'));sc=bpy.context.scene;I=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));col=bpy.data.collections['ACTUAL_RHINO_V16_READBACK']
for r in I:
 n=r['name']
 if not n.startswith(('SITE_V14_ORIGINAL_EXTERIOR','SITE_V16_SEALED_OUTER_WALL','SITE_V16_CONTINUOUS_WALL','SITE_V16_GRADED_INTERIOR_SOIL','SITE_V16_COURT_EDGE_INFILL_STEP')):continue
 d=np.load(O/'02_Data'/r['file']);old=bpy.data.objects.get(n+'_Geometry')
 if old:
  oldme=old.data;par=old.parent;bpy.data.objects.remove(old,do_unlink=True)
  if not oldme.users:bpy.data.meshes.remove(oldme)
 else:par=bpy.data.objects.new(n,None);col.objects.link(par)
 me=bpy.data.meshes.new(n);v=d['vertices'];f=d['faces'];uv=d['uv'];me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(n+'_Geometry',me);col.objects.link(ob);ob.parent=par
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',d['material_ids']);u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',uv[f.ravel()].astype(np.float32).ravel())
 if n.startswith(('SITE_V14_ORIGINAL_EXTERIOR','SITE_V16_GRADED_INTERIOR_SOIL')):
  for p in me.polygons:p.use_smooth=p.normal.z>.35
  me.normals_split_custom_set(d['normals'][f.ravel()].tolist());me.update()
 par['Parameters']=json.dumps(r['element'],ensure_ascii=False);par['GeometrySource']='Final V16 actual saved 3DM Mesh readback; limited miter, cleared interior scan scraps, stitched wall-side gutter edge';ob['Original_Rhino_Objects']=1;print('REFRESHED',n,len(f),flush=True)
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V16_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V16_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
names=['Whole_Site','Top','Graded_Courtyard','Screenwall_Inside','West_Wall_Drain','South_Wall_Drain','Outer_Storage_Base','Entry_Route']
for name in names:
 nn='V16_Native_'+name;sc.camera=bpy.data.objects[nn];sc.render.filepath=str(O/'06_Report'/f'{nn}.png');bpy.ops.render.render(write_still=True);print('RENDERED FINAL',nn,flush=True)
print('FINAL V16 NATIVE RENDERS COMPLETE',flush=True)
