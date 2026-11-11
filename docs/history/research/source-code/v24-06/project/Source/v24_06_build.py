"""V24.06: balanced raised eaves, aligned courtyard wall, clear paved passage, timber detail."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
from v24_06_paving import apply_paving
from v24_06_timber import build_timber
import v24_06_roof as xr
for n in ['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();base=snapshot(bpy);write('V24_06_Before_Snapshot.json',base)
oldroof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];before_roof_bounds=[[min(_bounds(o)[0][i]for o in oldroof)for i in range(3)],[max(_bounds(o)[1][i]for o in oldroof)for i in range(3)]]
piers=bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry'];pb=_bounds(piers);pier_y=(pb[0][1]+pb[1][1])/2
# Recover the small, closed, photo-fitted kitchen parts before any old roof cuts.
prior=json.loads(Path('E:/jz/JIA/Rebuild_V24_05/Reports/V24_05_Changes.json').read_text(encoding='utf8'));restore=prior['restored_contacts'];mats={m.name:m for m in bpy.data.materials};ids={k:set(getattr(bpy.data,k))for k in ['objects','meshes','materials','images','collections']}
with bpy.data.libraries.load('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend',link=False)as(a,b):b.objects=[n for n in restore if n in a.objects]
for src,n in zip(b.objects,[n for n in restore if n in a.objects]):
 dst=bpy.data.objects[n];me=src.data
 for i,m in enumerate(me.materials):
  if not m:continue
  key=m.name if m.name in mats else m.name[:-4]if m.name[-4]=='.'and m.name[-3:].isdigit()else m.name
  assert key in mats;me.materials[i]=mats[key]
 old=dst.data;dst.data=me
 if not old.users:bpy.data.meshes.remove(old)
for o in list(bpy.data.objects):
 if o not in ids['objects']:bpy.data.objects.remove(o,do_unlink=True)
for k in ['meshes','collections','materials','images']:
 for d in list(getattr(bpy.data,k)):
  if d not in ids[k]and d.users==0:getattr(bpy.data,k).remove(d)
beam=bpy.data.objects['SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry'];inv=beam.matrix_world.inverted()
for v in beam.data.vertices:
 p=beam.matrix_world@v.co
 if p.y>-2.835:p.y=-2.770;v.co=inv@p
beam.data.update()
for o in oldroof:bpy.data.objects.remove(o,do_unlink=True)
xr.CY=pier_y;roof_report=xr.apply_v24_xieshan_roof(bpy,R);roof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];rb=[[min(_bounds(o)[0][i]for o in roof)for i in range(3)],[max(_bounds(o)[1][i]for o in roof)for i in range(3)]]
def clip(poly,axis,bound,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=bound if greater else a[axis]<=bound;ib=b[axis]>=bound if greater else b[axis]<=bound
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*((bound-a[axis])/(b[axis]-a[axis])))
 return out
contact_names=[];kheight=[]
for o in bpy.data.objects:
 n=o.name
 if o.type!='MESH'or not(n.startswith('SITE_KITCHEN_')and any(k in n for k in ['ROOF','FASCIA','FLASHING','SHEATHING'])or n in ['V24_Kitchen_Curved_Gable_Coping','V24_Kitchen_Thin_Dark_Coping_Edge']):continue
 o.data.calc_loop_triangles();pts=[]
 for tri in o.data.loop_triangles:
  p=[o.matrix_world@o.data.vertices[i].co for i in tri.vertices]
  for ax,b,g in [(0,rb[0][0],True),(0,rb[1][0],False),(1,rb[0][1],True),(1,rb[1][1],False)]:
   if p:p=clip(p,ax,b,g)
  if p:pts.extend(p)
 if pts:kheight.append({'name':n,'max_z_in_gate_plan':max(p.z for p in pts)});contact_names.append(n)
highest=max(r['max_z_in_gate_plan']for r in kheight);target_bottom=math.ceil((highest+.10)*20)/20;shift=target_bottom-rb[0][2];extra=target_bottom-before_roof_bounds[0][2]
for o in roof:
 m=o.matrix_world.copy();m.translation.z+=shift;o.matrix_world=m;o['V24_06_Centered_Depth_m']=2.0
# Extend the existing plain neck and upper pier bearings to the raised soffit.
supports=['V24_05_Gate_Upper_Pier_Bearing_1','V24_05_Gate_Upper_Pier_Bearing_2','V24_05_Gate_Plain_Neck_Above_Carved_Lintel']
for n in supports:
 o=bpy.data.objects[n];inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  if p.z>3.0:p.z=target_bottom+.017;v.co=inv@p
 o.data.update();uv=o.data.uv_layers.active
 for f in o.data.polygons:
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p.x if abs(f.normal.y)>.5 else p.y,p.z)
attachments=['GATE_V22_PALE_CEILING_DISK_Geometry','SITE_V15_INNER_GATE_HANGING_LANTERNS_Geometry','V20_INSPECTION_Gate_Soffit']
for n in attachments:
 o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation.z+=extra
 if n=='GATE_V22_PALE_CEILING_DISK_Geometry':bb=_bounds(o);m.translation.y+=pier_y-(bb[0][1]+bb[1][1])/2
 if n=='V20_INSPECTION_Gate_Soffit':m.translation.y=pier_y-.66
 o.matrix_world=m
bpy.context.view_layer.update();newrb=[[min(_bounds(o)[0][i]for o in roof)for i in range(3)],[max(_bounds(o)[1][i]for o in roof)for i in range(3)]]
balance={'old_bounds':before_roof_bounds,'new_bounds':newrb,'pier_center_y':pier_y,'old_roof_center_y':sum(before_roof_bounds[i][1]for i in [0,1])/2,'new_roof_center_y':sum(newrb[i][1]for i in [0,1])/2,'front_projection_from_pier_m':pb[0][1]-newrb[0][1],'back_projection_from_pier_m':newrb[1][1]-pb[1][1],'additional_roof_raise_m':extra,'minimum_eave_bottom_z':newrb[0][2],'highest_kitchen_roof_under_gate_plan_z':highest,'minimum_eave_bottom_clearance_m':newrb[0][2]-highest,'kitchen_clipped_height_proof':kheight,'roof_local_raise_m':shift}
write('V24_06_Roof_Balance_and_Clearance.json',balance);print('BALANCED ROOF',balance,flush=True)
# Align the front leg of the L-shaped courtyard wall while preserving its
# fixed northern endpoint. This is a 0.87% length correction along the return.
ridge=bpy.data.objects['SITE_COURTYARD_WEST_TILE_WALL_V10_OPEN_FLOWER_BRICKS_Geometry'];p=[ridge.matrix_world@v.co for v in ridge.data.vertices];p=[v for v in p if .5<v.x<4.5 and v.y<-11];oldwall=(min(v.y for v in p)+max(v.y for v in p))/2;anchor=1.9;scale=(anchor-pier_y)/(anchor-oldwall);wallnames=[];walltopology={}
for o in bpy.data.objects:
 n=o.name
 if o.type!='MESH'or not(n.startswith('SITE_COURTYARD_WEST_')or n.startswith('SITE_WEST_TILE_WALL_PANEL_')or n=='V24_03_Wall_Flower_Ridge_Terminal_Bearing'):continue
 walltopology[n]=_closed_stats(o);inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=o.matrix_world@v.co;p.y=anchor+(p.y-anchor)*scale;v.co=inv@p
 o.data.update();wallnames.append(n)
wall={'changed_objects':wallnames,'old_front_center_y':oldwall,'new_front_center_y':pier_y,'inward_shift_m':pier_y-oldwall,'return_length_factor':scale,'fixed_north_endpoint_y':anchor,'source_topology':walltopology}
write('V24_06_Wall_Centerline.json',wall)
pave=apply_paving(bpy);write('V24_06_Passage_Paving.json',pave);print('PASSAGE PAVED',pave['paved_surface_area_m2'],pave['south_edge_xy'],flush=True)
timber=build_timber(bpy);write('V24_06_Kitchen_Timber.json',timber);print('PHOTO TIMBER COMPLETE',flush=True)
after=snapshot(bpy);changed=[n for n,r in base['objects'].items()if n in after['objects']and r!=after['objects'][n]];added=sorted(set(after['objects'])-set(base['objects']));removed=sorted(set(base['objects'])-set(after['objects']))
declared=set([o.name for o in roof]+supports+attachments+restore+wallnames+pave['changed_objects']+timber['changed_objects'])
assert set(changed)<=declared,sorted(set(changed)-declared)
write('V24_06_Changes.json',{'changed_objects':changed,'added_objects':added,'removed_objects':removed,'declared_changes':sorted(declared),'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'roof_objects':[o.name for o in roof],'supports':supports,'attachments':attachments,'restored_kitchen':restore,'roof_balance':balance,'wall':wall,'timber':timber})
guide=f'''V24.06：屋顶居中短檐、檐下净高、墙线与檐廊木构。
门楼屋顶中心与门柱中心Y={pier_y:.3f}m一致，前后出挑各约{balance['front_projection_from_pier_m']:.3f}m；前檐向内收回约{newrb[0][1]-before_roof_bounds[0][1]:.3f}m。
檐下最低面抬至{target_bottom:.3f}m，比屋顶投影内厨房斜檐最高线{highest:.3f}m高{target_bottom-highest:.3f}m。新增素面承接段相接，门扇与15块浮雕不动。
内院围墙中线向内调整{pier_y-oldwall:.3f}m，与门柱中线对齐，北端连接点保持原位。
删除圈内Tree 5、Tree 6及残余树根土环；土黄色条带沿用旁边过道的{pave['material']}，按原UV尺度铺设并延续原坡度；原过道网格内的圆形树坑已封平。
厨房木构：40对密排椽、3处穿梁与垂瓜、曲线托木和实体卷草浮雕、木销；保留6根圆檩及1根独立檐廊柱。参考172938、DJI_0156、DJI_0157。
全场地Blender文件，实景材质与原26扇门动画保留。默认40帧，保存后报告及彩色预览位于Reports。
'''
(O/'README_V24_06.txt').write_text(guide,encoding='utf-8-sig');txt=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');txt.clear();txt.write(guide)
for n,pos,tar,lens in [('V24_06_Gate_Courtyard',(4.6,-7.4,2.8),(6.6,pier_y,2.65),21),('V24_06_Balanced_Side',(1.0,pier_y,3.5),(6.6,pier_y,2.8),38),('V24_06_Kitchen_Timber',(6.85,-9.6,1.45),(8.5,-6.0,2.58),25)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
sc.camera=bpy.data.objects['V24_06_Gate_Courtyard'];sc['Version']='V24_06_BALANCED_EAVE_WALL_PATH_TIMBER';sc['Source_SHA256']=sha(B);sc.frame_set(40)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False;area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_06_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'roof_balance':balance,'wall':wall,'timber':timber,'paving_area_m2':pave['paved_surface_area_m2']});print('V24.06 SAVED',flush=True)
