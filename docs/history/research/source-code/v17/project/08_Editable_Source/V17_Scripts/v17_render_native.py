import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V16');O=Path(r'E:/jz/JIA/Rebuild_V17');bpy.ops.wm.open_mainfile(filepath=str(B/'05_Export/Actual_Rhino_V16_Readback_LOCAL.blend'));sc=bpy.context.scene
I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));M=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));changed=set(AQ['changed_nodes']);col=bpy.data.collections['ACTUAL_RHINO_V16_READBACK'];col.name='ACTUAL_RHINO_V17_READBACK'
for n in AQ.get('removed_nodes',[]):
 par=bpy.data.objects.get(n)
 if par:
  for child in list(par.children):
   me=child.data if child.type=='MESH' else None;bpy.data.objects.remove(child,do_unlink=True)
   if me and not me.users:bpy.data.meshes.remove(me)
  bpy.data.objects.remove(par,do_unlink=True)
for im in bpy.data.images:
 if im.source=='FILE':
  path=im.filepath.replace('Rebuild_V16','Rebuild_V17')
  if Path(path).exists():im.filepath=path
m=bpy.data.materials.new('M_V17_Garden_Soil');m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.98;tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(M[m.name]['native_bitmap'],check_existing=True);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);bn=m.node_tree.nodes.new('ShaderNodeBump');bt=m.node_tree.nodes.new('ShaderNodeTexImage');bt.image=bpy.data.images.load(M[m.name]['native_bump'],check_existing=True);bt.image.colorspace_settings.name='Non-Color';bn.inputs['Strength'].default_value=.2;bn.inputs['Distance'].default_value=.004;m.node_tree.links.new(bt.outputs['Color'],bn.inputs['Height']);m.node_tree.links.new(bn.outputs['Normal'],bs.inputs['Normal']);m['Appearance_Source']='Actual native fine grain soil bitmap'
for r in I:
 n=r['name']
 if n not in changed:continue
 d=np.load(O/'02_Data'/r['file']);old=bpy.data.objects.get(n+'_Geometry')
 if old:
  oldme=old.data;par=old.parent;bpy.data.objects.remove(old,do_unlink=True)
  if not oldme.users:bpy.data.meshes.remove(oldme)
 else:par=bpy.data.objects.new(n,None);col.objects.link(par)
 me=bpy.data.meshes.new(n);v=d['vertices'];f=d['faces'];uv=d['uv'];me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(n+'_Geometry',me);col.objects.link(ob);ob.parent=par
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',d['material_ids']);u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',uv[f.ravel()].astype(np.float32).ravel())
 if n.startswith(('SITE_V14_ORIGINAL_EXTERIOR','SITE_V16_GRADED_INTERIOR_SOIL','SITE_V17_LOWER_EXTERIOR')):
  for p in me.polygons:p.use_smooth=p.normal.z>.35
  me.normals_split_custom_set(d['normals'][f.ravel()].tolist());me.update()
 par['Parameters']=json.dumps(r['element'],ensure_ascii=False);par['GeometrySource']='Actual V17 saved 3DM Mesh readback; concave facade, supported stone base and lower exterior grade';ob['Original_Rhino_Objects']=r['native_objects'];print('REFRESHED',n,len(f),flush=True)
for ob in bpy.data.objects:
 if ob.type=='CAMERA' and ob.name.startswith('V16_'):ob.name=ob.name.replace('V16_','V17_')
cameras=[('V17_Native_Concave_Corner',[24,-1.5,7],[15.2,-8.2,-.5],63,None),('V17_Native_Lower_Garden_Junction',[21,-7,-1],[14.8,-8.4,-1.6],75,None),('V17_Native_Storage_Return',[26,-14,5],[16,-9.8,-.3],61,None),('V17_Native_Junction_Plan',[16,-7,30],[16,-7,0],50,18),('V17_Native_Storage_Timber_Interior',[16.2,-14.30,.8],[16.1,-11.8,2.1],95,None),('V17_Native_Storage_Eave_Gallery',[14.5,-15.55,.75],[17.8,-15.5,1.0],89,None),('V17_Native_Storage_Stone_Guard_Exterior',[22,-22,2.0],[16.3,-15.75,.6],73,None)]
for name,pos,tar,fov,ortho in cameras:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)
 if ortho:cd.type='ORTHO';cd.ortho_scale=ortho
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.camera=bpy.data.objects[cameras[0][0]]
for j,p in enumerate([[14.8,-13.4,2.4],[17.5,-11.3,2.5],[16.2,-15.5,1.4]]):
 ld=bpy.data.lights.new('Storage_Review_Light_'+str(j),'POINT');ld.energy=85;ld.shadow_soft_size=.45;lo=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(lo);lo.location=p;lo['Role']='Inspection lighting only, not a modeled surveyed fixture'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V17_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V17_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
names=[r[0] for r in cameras]+['V17_Native_Whole_Site','V17_Native_Top','V17_Native_Screenwall_Inside','V17_Native_West_Wall_Drain','V17_Native_Outer_Storage_Base']
for name in names:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED V17 ACTUAL NATIVE',name,flush=True)
(O/'06_Report/Preview_View_States.json').write_text(json.dumps({'geometry':'V17 saved 3DM verified readback','view_names':names,'visibility':'All indexed native geometry visible; retained materials and review lighting from V16','source_coordinate_system':'LOCAL metres'},ensure_ascii=False,indent=2),encoding='utf8')
print('V17 NATIVE PREVIEW COMPLETE',flush=True)
