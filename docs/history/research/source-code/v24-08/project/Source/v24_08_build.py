"""Native Blender: controlled kitchen setback, actual exterior brick finish, exterior detail."""
import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_08_common import *
from v24_03_junction_blender import _bounds,_tree,_mesh,_box,_difference,_closed_stats
from v24_08_geometry import setback,exterior_bands,finishes,exhaust,east_eave_tiles
import v24_06_roof as xr
for n in['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;base=snapshot(bpy);write('V24_08_Before_Snapshot.json',base)
sc.frame_set(40);bpy.context.view_layer.update()
restore=['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry','V24_Kitchen_Curved_Gable_Coping','V24_Kitchen_Gable_Upper_Brick_Infill','V24_Kitchen_Thin_Dark_Coping_Edge']
# Restore the unlowered-gate kitchen end before deforming it, then recut against
# the fixed current gate. This avoids moving an old notch away from its joint.
ids={k:set(getattr(bpy.data,k))for k in['objects','meshes','materials','images','collections']}
src='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend'
with bpy.data.libraries.load(src,link=False)as(a,b):b.objects=list(restore)
for n,o in zip(restore,b.objects):
 target=bpy.data.objects[n];old=target.data;target.data=o.data
 for i,m in enumerate(target.data.materials):
  name=m.name
  if name[-4:-3]=='.'and name[-3:].isdigit():name=name[:-4]
  if name in bpy.data.materials:target.data.materials[i]=bpy.data.materials[name]
 if not old.users:bpy.data.meshes.remove(old)
for o in list(bpy.data.objects):
 if o not in ids['objects']:bpy.data.objects.remove(o,do_unlink=True)
for k in['meshes','collections','materials','images']:
 for d in list(getattr(bpy.data,k)):
  if d not in ids[k]and d.users==0:getattr(bpy.data,k).remove(d)
setback_report=setback();write('V24_08_Kitchen_Setback.json',setback_report);print('SETBACK COMPLETE',len(setback_report['changed_objects']),flush=True)
bands=exterior_bands(W);write('V24_08_Exterior_Bands.json',bands);finish=finishes();write('V24_08_Exterior_Finishes.json',finish);print('FINISH COMPLETE',bands,flush=True)
col=bpy.data.collections.new('V24_08_厨房退让及外墙实景细化');sc.collection.children.link(col)
# New exposed strip uses the same five original courtyard surface shaders.
floor_source=bpy.data.objects['CONSTRUCTION_COURTYARD_DRAINAGE_FINISH_Geometry'];fm=list(floor_source.data.materials);newfloor=[]
for j in range(13):
 y=-10.90+j*.6384;Y=min(-2.60,y+.6384);z0=-.421-.022*((y+10.90)/8.30);z1=-.421-.022*((Y+10.90)/8.30)
 for k in range(2):
  x=7.25+k*.45;X=x+.45;gap=.004;z=(z0+z1)/2
  o=_box(bpy,col,'V24_08_Exposed_Court_Slab_'+str(j)+'_'+str(k),(x+gap,y+gap,z-.032),(X-gap,Y-gap,z),fm[1+(j*3+k)%4]);newfloor.append(o)
  uv=o.data.uv_layers.active
  for l in o.data.loops:
   p=o.data.vertices[l.vertex_index].co;uv.data[l.index].uv=(p.x/1.2,p.y/1.2)
o=_box(bpy,col,'V24_08_Exposed_Court_Joint_Bed',(7.25,-10.9,-.48),(8.15,-2.6,-.452),fm[0]);newfloor.append(o)
# Complete the short strip beside the accepted inner-gate sill.
o=_box(bpy,col,'V24_08_Gate_Side_Exposed_Court_Strip',(7.7,-11.40,-.49),(8.15,-10.9,-.447),bpy.data.materials['M_V12_Court_Stone']);newfloor.append(o)
ex=exhaust(col);write('V24_08_Exhaust_Detail.json',ex)
tiles=east_eave_tiles(col);write('V24_08_East_Eave_Tiles.json',tiles)
# Fitted closed kitchen/gate joint. Gate itself stays at the accepted 3.10m.
roof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];pb=_bounds(bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry']);xr.CY=sum(pb[i][1]for i in[0,1])/2;V,F=xr.xieshan_clearance_mesh_data(padding=.008);V=[(x,y,z+.562)for x,y,z in V]
for ro in roof:
 off=len(V);V.extend(tuple(ro.matrix_world@v.co)for v in ro.data.vertices);F.extend([[off+i for i in p.vertices]for p in ro.data.polygons])
cut=_mesh(bpy,col,'V24_08_TEMP_Fitted_Eave_Envelope',V,F,bpy.data.materials['M_Roof'])
for o in bpy.context.selected_objects:o.select_set(False)
cut.select_set(True);bpy.context.view_layer.objects.active=cut;mod=cut.modifiers.new('Continuous_Fitted_Union','REMESH');mod.mode='VOXEL';mod.voxel_size=.012;mod.adaptivity=.10;bpy.ops.object.modifier_apply(modifier=mod.name);mod=cut.modifiers.new('Hidden_Clearance','DISPLACE');mod.strength=.018;mod.mid_level=0;bpy.ops.object.modifier_apply(modifier=mod.name);cut.select_set(False);bpy.context.view_layer.update();ct=_tree(cut);cb=_bounds(cut);contacts=[]
for o in list(bpy.data.objects):
 n=o.name
 if o.type!='MESH'or not(n.startswith(('SITE_KITCHEN_','SITE_V22_KITCHEN_','KITCHEN_V22_','V24_Kitchen_','V24_06_Kitchen_'))or n=='SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry'):continue
 lo,hi=_bounds(o)
 if any(hi[i]<cb[0][i]or lo[i]>cb[1][i]for i in range(3))or not ct.overlap(_tree(o)):continue
 contacts.append(_difference(bpy,o,cut));print('FITTED',n,flush=True)
me=cut.data;bpy.data.objects.remove(cut,do_unlink=True)
if not me.users:bpy.data.meshes.remove(me)
write('V24_08_Kitchen_Gate_Joint.json',{'fixed_gate_soffit_z_m':3.10,'clearance_m':.018,'contact_objects':contacts,'restored_before_fitting':restore})
# Read actual exposed ground levels for QA / visual review.
ground=[]
for n in['SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_KITCHEN_STONE_FLOOR_Geometry','CONSTRUCTION_COURTYARD_DRAINAGE_FINISH_Geometry']:
 o=bpy.data.objects[n];tr=_tree(o)
 for x in[7.4,7.8,8.1,8.3]:
  p,no,idx,dist=tr.ray_cast(Vector((x,-6,5)),Vector((0,0,-1)),10)
  ground.append({'name':n,'x':x,'z':p.z if p else None})
write('V24_08_Ground_Sections.json',ground)
for n,pos,tar,lens,ortho in [('V24_08_Court',(6.5,-11,1.72),(6.5,0,1.65),23,None),('V24_08_Exterior',(34,-24,16),(12,-6,.8),45,None),('V24_08_Exterior_Wall',(25,4,7),(14,2,.9),40,None),('V24_08_Kitchen_Exterior',(23,-9,7),(13.4,-6,1.4),34,None),('V24_08_Court_Plan',(8,-6,30),(8,-6,0),50,22),('V24_08_Gate_Junction',(10.8,-18.2,7.2),(7.5,-11.582,3.2),45,None)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
sc.camera=bpy.data.objects['V24_08_Court'];sc.frame_set(40);sc['Version']='V24_08_KITCHEN_SETBACK_AND_ASBUILT_EXTERIOR'
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.overlay.show_overlays=False;a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
guide='V24.08：厨房向外退让0.45m，内院侧基础X7.70→8.15，立面X9.05→9.50；外墙基线X14.10控制保持。檐廊、门窗、铰轴、柱梁、屋面及连接储物间同步过渡，释放区域补同款院内石材。外侧灰砖至瓦口，去除多余白带，保留内侧白墙及正门照壁装饰，厨房使用实景灰砖纹理和单块砖材质，补两种排烟管。门楼檐底仍为3.10m，双门细节和动画、院墙中线、南过道铺地及两树删除全部保留。厨房退让数值为依用户照片的小幅模型校正，不作为独立实测尺寸。默认40帧开门，1帧关闭，20帧半开。'
(O/'README_V24_08.txt').write_text(guide,encoding='utf-8-sig');t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide)
after=snapshot(bpy);changed=[n for n,r in base['objects'].items()if n in after['objects']and r!=after['objects'][n]];added=sorted(set(after['objects'])-set(base['objects']));removed=sorted(set(base['objects'])-set(after['objects']));write('V24_08_Changes.json',{'changed_objects':changed,'added_objects':added,'removed_objects':removed,'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'setback':setback_report,'finish':finish,'bands':bands,'exhaust':ex,'contacts':contacts})
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_08_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'changed_count':len(changed),'added_count':len(added)});print('V24.08 SAVED',len(changed),len(added),flush=True)
