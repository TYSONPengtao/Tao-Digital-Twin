"""Raise the slim gate roof 0.50 m, extend its bearing, and refit the kitchen."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_05_common import *
from v24_03_junction_blender import _bounds,_tree,_mesh,_difference,_closed_stats
import v24_04_roof as xr
for n in ['Blender','Reports','Source','Textures','References']:(O/n).mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(40);base=snapshot(bpy);write('V24_05_Before_Snapshot.json',base)
roof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')]
moved=[o.name for o in roof]+['GATE_V22_PALE_CEILING_DISK_Geometry','SITE_V15_INNER_GATE_HANGING_LANTERNS_Geometry','V20_INSPECTION_Gate_Soffit']
for n in moved:
 ob=bpy.data.objects[n];m=ob.matrix_world.copy();m.translation.z+=.50;ob.matrix_world=m;ob['V24_05_Raise_GLOBAL_Z_m']=.50
bpy.context.view_layer.update();print('ROOF AND ATTACHMENTS RAISED 0.50m',len(moved),flush=True)
col=bpy.data.collections.new('V24_05_门楼抬高承接');sc.collection.children.link(col)
def prism(name,poly,z0,z1,mat):
 n=len(poly);V=[(x,y,z)for z in [z0,z1]for x,y in poly];F=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]
 ob=_mesh(bpy,col,name,V,F,mat);uv=ob.data.uv_layers.active
 for p in ob.data.polygons:
  for li in p.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(v.x if abs(p.normal.y)>.5 else v.y,v.z)
 return ob
mat=bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry'].data.materials[0]
for k,(x0,x1)in enumerate([(4.9333333333,5.4571428571),(7.7428571429,8.2666666667)]):
 poly=[(x0,-11.78),(x0+.09,-11.87),(x1-.09,-11.87),(x1,-11.78),(x1,-11.294),(x0,-11.294)]
 prism('V24_05_Gate_Upper_Pier_Bearing_'+str(k+1),poly,2.622,3.055,mat)
prism('V24_05_Gate_Plain_Neck_Above_Carved_Lintel',[(5.338095,-11.799),(7.861905,-11.799),(7.861905,-11.382),(5.338095,-11.382)],2.630,3.055,bpy.data.materials['M_V21_GATE_REF_04'])

# Restore only the kitchen components formerly trimmed around the lower roof.
contact=json.loads(Path('E:/jz/JIA/Rebuild_V24_04/Reports/V24_04_Closure_and_Contact.json').read_text(encoding='utf8'));names=contact['restored_for_new_roof'];original={m.name:m for m in bpy.data.materials}
oldids={k:set(getattr(bpy.data,k))for k in ['objects','meshes','materials','images','collections']}
with bpy.data.libraries.load('E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend',link=False)as(a,b):b.objects=[n for n in names if n in a.objects]
for src,n in zip(b.objects,[n for n in names if n in a.objects]):
 dst=bpy.data.objects[n];me=src.data
 for i,m in enumerate(me.materials):
  if not m:continue
  key=m.name if m.name in original else m.name[:-4]if m.name[-4]=='.'and m.name[-3:].isdigit()else m.name
  assert key in original;me.materials[i]=original[key]
 old=dst.data;dst.data=me
 if not old.users:bpy.data.meshes.remove(old)
for o in list(bpy.data.objects):
 if o not in oldids['objects']:bpy.data.objects.remove(o,do_unlink=True)
for k in ['meshes','collections','materials','images']:
 for d in list(getattr(bpy.data,k)):
  if d not in oldids[k]and d.users==0:getattr(bpy.data,k).remove(d)
beam=bpy.data.objects['SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry'];inv=beam.matrix_world.inverted()
for v in beam.data.vertices:
 p=beam.matrix_world@v.co
 if p.y>-2.835:p.y=-2.770;v.co=inv@p
beam.data.update()
# An exact low-complexity closed envelope follows every roof step and slope.
# Corner finials are well above the kitchen and need no extra cutter geometry.
V,F=xr.xieshan_clearance_mesh_data(.035);V=[(x,y,z+.5)for x,y,z in V];cut=_mesh(bpy,col,'V24_05_TEMP_Raised_Roof_Bedding',V,F,bpy.data.materials['M_Roof']);assert _closed_stats(cut)['nonmanifold_edges']==0
cb=_bounds(cut);ct=_tree(cut);trims=[]
for n in names:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob)
 if any(hi[i]<cb[0][i]or lo[i]>cb[1][i]for i in range(3)):continue
 if ct.overlap(_tree(ob)):
  row=_difference(bpy,ob,cut);trims.append(row);print('RAISED CONTACT',n,row['boundary_edges'],flush=True)
bpy.data.objects.remove(cut,do_unlink=True)
for row in trims:
 ob=bpy.data.objects[row['name']];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 tiny=[f for f in bm.faces if f.calc_area()<1e-6 and any(e.is_boundary for e in f.edges)]
 if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
 bound=list({v for e in bm.edges if e.is_boundary for v in e.verts})
 if bound:bmesh.ops.remove_doubles(bm,verts=bound,dist=.00010)
 wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();row.update(_closed_stats(ob))
roofdata=[(o,_bounds(o),_tree(o))for o in roof];collisions=[]
for n in names:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob);tr=_tree(ob)
 for ro,bb,rt in roofdata:
  if any(hi[i]<bb[0][i]or lo[i]>bb[1][i]for i in range(3)):continue
  ov=tr.overlap(rt)
  if ov:collisions.append({'kitchen':n,'gate':ro.name,'triangles':len(ov)})
print('RAISED CONTACT COLLISIONS',collisions,flush=True)
# Compare the actual surfaces in the shared gate/kitchen footprint. This is
# the marked junction in the user's photograph, not the remote kitchen ridge.
gtr=[_tree(o)for o in roof if o.name.startswith(('V24_XIESHAN_01_','V24_XIESHAN_02_'))]
ktr=[_tree(bpy.data.objects[n])for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry']]
heights=[]
for x in [7.20,7.50,7.80,8.10,8.40,8.65,8.78]:
 for y in [-11.20,-10.85,-10.68]:
  origin=Vector((x,y,8));direc=Vector((0,0,-1));gh=[h[0].z for t in gtr if(h:=t.ray_cast(origin,direc,10))[0]is not None];kh=[h[0].z for t in ktr if(h:=t.ray_cast(origin,direc,10))[0]is not None]
  if gh and kh:heights.append({'x':x,'y':y,'gate_roof_z':max(gh),'kitchen_roof_z':max(kh),'gap_m':max(gh)-max(kh)})
assert heights,'No shared footprint samples'
after=snapshot(bpy);changed=[n for n,r in base['objects'].items()if n in after['objects']and r!=after['objects'][n]];added=sorted(set(after['objects'])-set(base['objects']));removed=sorted(set(base['objects'])-set(after['objects']))
write('V24_05_Changes.json',{'changed_objects':changed,'added_objects':added,'removed_objects':removed,'translated_050m_objects':moved,'restored_contacts':names,'expected_mesh_hashes':{n:after['objects'][n]['mesh_hash']for n in changed+added if after['objects'][n]['mesh_hash']},'trims':trims,'collisions':collisions,'junction_height_samples':heights,'minimum_roof_surface_height_gap_m':min(r['gap_m']for r in heights)})
guide='''V24.05：内大门轻薄歇山屋顶整体抬高0.50米。
V24.04屋顶的形状、厚度和宽深不变；屋面、檐下层次、灯笼和顶灯统一竖向平移0.50米。新增上部石柱承接和门楣上方素面墙颈，门扇、门洞及浮雕位置不变。
厨房交接按抬高后的屋顶重新收口；圈示共享区域的门楼屋面高于厨房坡面。厨房后端与外围墙的实体封闭、单根独立檐廊柱均保留。
保留全场地、实景材质与原26扇门动画，默认40帧。Reports记录精确位移、共享区域高差及保存后验证。
'''
(O/'README_V24_05.txt').write_text(guide,encoding='utf-8-sig');txt=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');txt.clear();txt.write(guide)
for n,pos,tar,lens in [('V24_05_Gate_Raised_Review',(4.6,-7.4,2.5),(6.6,-11.9,2.15),25),('V24_05_Gate_Kitchen_Junction',(4.2,-6.7,3.7),(7.8,-11.4,3.3),30)]:
 c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
sc.camera=bpy.data.objects['V24_05_Gate_Raised_Review'];sc['Version']='V24_05_GATE_ROOF_RAISED_050m';sc['Source_SHA256']=sha(B);sc.frame_set(40)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_05_Build.json',{'status':'SAVED','model':str(P),'sha256':sha(P),'source_sha256':sha(B),'raise_m':.5,'roof_geometry_unchanged':True,'minimum_junction_roof_height_gap_m':min(r['gap_m']for r in heights),'collisions':collisions});print('V24.05 SAVED',flush=True)
