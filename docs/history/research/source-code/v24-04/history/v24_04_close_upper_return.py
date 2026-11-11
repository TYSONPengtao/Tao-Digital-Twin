"""Join the kitchen rear wall to the perimeter's upper wall, not its lower toe."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_04_common import *
from v24_03_junction_blender import _mesh,_tree,_closed_stats
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40)
contact=json.loads((R/'V24_04_Closure_and_Contact.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_04_Changes.json').read_text(encoding='utf8'));base=json.loads((R/'V24_04_Before_Snapshot.json').read_text(encoding='utf8'))
col=bpy.data.collections.get('V24_04_厨房端墙连续封闭')
a=Vector((14.02,-2.82));b=Vector((14.31,-2.04));d=(b-a).normalized();normal=Vector((-d.y,d.x));half=.15
roofh=min(contact['roof_top_fit'],key=lambda r:abs(r['x']-14.02))['wall_top_z']
brick=bpy.data.materials['M_Grey_Brick'];white=bpy.data.objects['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry'].data.materials[0];stone=bpy.data.materials['M_Stone_Frame'];roof=bpy.data.materials['M_Roof']
def strip(name,zlo0,zlo1,zhi0,zhi1,width,mat,finish=False):
 V=[]
 for top in [False,True]:
  for p,sign,z0,z1 in [(a,-1,zlo0,zhi0),(b,-1,zlo1,zhi1),(b,1,zlo1,zhi1),(a,1,zlo0,zhi0)]:
   p=p+normal*sign*width;V.append((p.x,p.y,z1 if top else z0))
 F=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 ob=_mesh(bpy,col,name,V,F,mat)
 if finish:ob.data.materials.append(white);ob.data.polygons[4].material_index=1
 uv=ob.data.uv_layers.active
 for f in ob.data.polygons:
  for li in f.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((Vector((v.x,v.y))-a).dot(d),v.z)
 return ob
returnwall=strip('V24_04_Kitchen_Perimeter_Upper_Return',-.434,-.434,roofh+.002,2.94,half,brick,True)
strip('V24_04_Kitchen_Perimeter_Upper_Return_Stone_Toe',-.444,-.444,-.15,-.15,half+.015,stone)
strip('V24_04_Kitchen_Perimeter_Return_Coping',roofh-.010,2.928,roofh+.025,2.965,half+.025,roof)
returnwall['Reference']='Closes full-height gap to existing upper perimeter endpoint at LOCAL 14.31,-2.04; lower retaining toe is not the wall endpoint'
# Avoid a coplanar overlay between the stone plinth and brick wall.
pl=bpy.data.objects['V24_03_Kitchen_Rear_Stone_Plinth']
for v in pl.data.vertices:
 x,y,z=v.co;t=max(0,(x-13.25)/.85);yc=-2.69-.13*t;v.co.y+=.016 if y>yc else -.016
pl.data.update()
repairs=[]
for n in ['SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']:
 ob=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 tiny=[f for f in bm.faces if f.calc_area()<1e-6 and any(e.is_boundary for e in f.edges)]
 if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
 boundary=list({v for e in bm.edges if e.is_boundary for v in e.verts})
 if boundary:bmesh.ops.remove_doubles(bm,verts=boundary,dist=.00010)
 wire=[e for e in bm.edges if not e.link_faces]
 if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
 isolated=[v for v in bm.verts if not v.link_edges]
 if isolated:bmesh.ops.delete(bm,geom=isolated,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update();s=_closed_stats(ob);repairs.append({'name':n,'local_boundary_weld_tolerance_m':.0001,**s});assert s['boundary_edges']==0,(n,s)
for ob in [o for o in bpy.data.objects if o.name.startswith('V24_04_Kitchen_Perimeter_')]:
 delta['added_objects'].append(ob.name);delta['expected_mesh_hashes'][ob.name]=q._mesh_hash(ob.data)
for n in ['V24_03_Kitchen_Rear_Stone_Plinth']+[r['name']for r in repairs]:delta['expected_mesh_hashes'][n]=q._mesh_hash(bpy.data.objects[n].data)
contact['upper_return']={'object':returnwall.name,'from_xy':list(a),'to_xy':list(b),'length_m':(b-a).length,'thickness_m':half*2,'top_from_z_m':roofh+.002,'top_to_z_m':2.94,'boundary_cut_repairs':repairs};write('V24_04_Closure_and_Contact.json',contact);write('V24_04_Changes.json',delta)
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);build=json.loads((R/'V24_04_Build.json').read_text(encoding='utf8'));build['sha256']=sha(P);build['upper_return']=contact['upper_return'];write('V24_04_Build.json',build);print('UPPER RETURN CLOSED',contact['upper_return'],flush=True)
