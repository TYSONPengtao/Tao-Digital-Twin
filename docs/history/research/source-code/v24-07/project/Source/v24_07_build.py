"""V24.07: user point 1 down to point 2, closed fitted kitchen joint, improved doors."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_07_common import *
from v24_03_junction_blender import _bounds,_tree,_mesh,_difference,_closed_stats
from v24_07_doors import improve_doors
import v24_06_roof as xr
for n in['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();base=snapshot(bpy);write('V24_07_Before_Snapshot.json',base)
roof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];before_bottom=min(_bounds(o)[0][2]for o in roof);target_bottom=3.10;dz=target_bottom-before_bottom
for o in roof:m=o.matrix_world.copy();m.translation.z+=dz;o.matrix_world=m
supports=['V24_05_Gate_Upper_Pier_Bearing_1','V24_05_Gate_Upper_Pier_Bearing_2','V24_05_Gate_Plain_Neck_Above_Carved_Lintel']
for n in supports:
 o=bpy.data.objects[n];inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if p.z>3.4:p.z=target_bottom+.017;v.co=inv@p
 o.data.update()
 # Regenerate only the plain extension UVs after the height change.
 uv=o.data.uv_layers.active
 for f in o.data.polygons:
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p.x if abs(f.normal.y)>.5 else p.y,p.z)
attachments=['GATE_V22_PALE_CEILING_DISK_Geometry','SITE_V15_INNER_GATE_HANGING_LANTERNS_Geometry','V20_INSPECTION_Gate_Soffit']
for n in attachments:o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation.z+=dz;o.matrix_world=m
bpy.context.view_layer.update();height={'previous_underside_z_m':before_bottom,'new_underside_z_m':min(_bounds(o)[0][2]for o in roof),'roof_translation_z_m':dz,'user_mark_1_hit':[8.54328346,-12.40808678,3.51274323],'user_mark_2_kitchen_coping_hit':[8.26568222,-11.91500092,3.07117224],'local_contact_clearance_m':target_bottom-3.07117224,'rule':'User point 1 down toward point 2; adjacent roof tucked at the closed side-eave joint, no global maximum-height offset'}
write('V24_07_Marked_Height.json',height);print('HEIGHT',height,flush=True)
# Derive the cutter from the actual continuous stepped eave enclosure plus
# its fine tile/finial geometry. Only intersecting kitchen parts are trimmed.
piers=bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry'];pb=_bounds(piers);xr.CY=sum(pb[i][1]for i in[0,1])/2;shift=target_bottom-2.538;V,F=xr.xieshan_clearance_mesh_data(padding=.008);V=[(x,y,z+shift)for x,y,z in V]
for ro in roof:
 off=len(V);V.extend(tuple(ro.matrix_world@v.co)for v in ro.data.vertices);F.extend([[off+i for i in p.vertices]for p in ro.data.polygons])
col=bpy.data.collections.new('V24_07_屋顶接缝处理');sc.collection.children.link(col);cut=_mesh(bpy,col,'V24_07_TEMP_Fitted_Eave_Envelope',V,F,bpy.data.materials['M_Roof'])
for o in bpy.context.selected_objects:o.select_set(False)
cut.select_set(True);bpy.context.view_layer.objects.active=cut;mod=cut.modifiers.new('Continuous_Fitted_Union','REMESH');mod.mode='VOXEL';mod.voxel_size=.012;mod.adaptivity=.10;bpy.ops.object.modifier_apply(modifier=mod.name);mod=cut.modifiers.new('Hidden_Contact_Clearance','DISPLACE');mod.strength=.018;mod.mid_level=0;bpy.ops.object.modifier_apply(modifier=mod.name);cut.select_set(False);bpy.context.view_layer.update();ct=_tree(cut);cb=_bounds(cut);contacts=[]
for o in list(bpy.data.objects):
 n=o.name
 if o.type!='MESH'or not(n.startswith(('SITE_KITCHEN_','SITE_V22_KITCHEN_','KITCHEN_V22_','V24_Kitchen_','V24_06_Kitchen_'))or n in['SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']):continue
 lo,hi=_bounds(o)
 if any(hi[i]<cb[0][i]or lo[i]>cb[1][i]for i in range(3))or not ct.overlap(_tree(o)):continue
 row=_difference(bpy,o,cut);contacts.append(row);print('FITTED CONTACT',row,flush=True)
me=cut.data;bpy.data.objects.remove(cut,do_unlink=True)
if not me.users:bpy.data.meshes.remove(me)
write('V24_07_Fitted_Kitchen_Joint.json',{'contact_clearance_m':.018,'cutter_voxel_m':.012,'changed_objects':[r['name']for r in contacts],'geometry':contacts,'method':'Closed kitchen ends conform to stepped gate soffit and real six-slope roof; no large rectangular notch'})
door=improve_doors(bpy);write('V24_07_Doors.json',door);print('DOOR REFINEMENT COMPLETE',flush=True)
after=snapshot(bpy);changed=[n for n,r in base['objects'].items()if n in after['objects']and r!=after['objects'][n]];added=sorted(set(after['objects'])-set(base['objects']));removed=sorted(set(base['objects'])-set(after['objects']));declared={o.name for o in roof}|set(supports+attachments+door['changed_objects']+[r['name']for r in contacts]);assert set(changed)<=declared,sorted(set(changed)-declared)
write('V24_07_Changes.json',{'changed_objects':changed,'added_objects':added,'removed_objects':removed,'declared_changes':sorted(declared),'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'roof_objects':[o.name for o in roof],'supports':supports,'attachments':attachments,'kitchen_contacts':[r['name']for r in contacts],'doors':door,'height':height})
guide=f'''V24.07：按用户“1到2”回落檐底，并细化内大门门扇。
屋檐由V24.06的3.500m整体回落{abs(dz):.3f}m至3.100m。用户2点所在厨房斜檐Z约3.071m；檐底贴近此线。相交厨房构件依门楼连续台阶包络闭合收口，保持原居中短檐、歇山结构和薄檐比例。
双门改为高上芯板、中芯板、窄菱饰格与下部踢板，真实凸起压线和斜面芯板；保留原曲柄长铜拉手、原铰轴和原内开动画，补三处铰链。门额与木门框细化。
上一版已完成的院墙中线、两树删除、过道同材质、树坑封平、厨房密排椽与托木垂瓜、后墙封闭继续保留。原15块实体浮雕与场地材质、26扇门动画保留。
默认40帧全开；1帧关闭，20帧半开。彩色预览和保存后校验位于Reports。
''';(O/'README_V24_07.txt').write_text(guide,encoding='utf-8-sig');txt=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');txt.clear();txt.write(guide)
for n,pos,tar,lens in [('V24_07_Gate_Whole',(6.6,-15.9,2.1),(6.6,-11.582,1.95),19),('V24_07_Gate_Junction',(10.8,-18.2,7.2),(6.9,-11.582,3.2),45),('V24_07_Door_Detail',(5.8,-14.8,1.25),(6.5,-11.58,1.0),42)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
sc.camera=bpy.data.objects['V24_07_Gate_Whole'];sc['Version']='V24_07_MARKED_EAVE_HEIGHT_AND_DOOR_DETAIL';sc.frame_set(40)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.overlay.show_overlays=False;a.spaces.active.shading.type='MATERIAL';a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_07_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'height':height,'kitchen_contacts':contacts,'doors':door});print('V24.07 SAVED',flush=True)
