"""Photo-based kitchen rear closure and a single independent veranda column."""
import math,json
from pathlib import Path
def apply_v24_03_kitchen_fix(bpy,report_dir):
 import bmesh
 from mathutils import Vector
 from mathutils.geometry import tessellate_polygon
 out=Path(report_dir);out.mkdir(parents=True,exist_ok=True);removed=[];added=[];changed=[]
 for n in ['SITE_KITCHEN_V12_BEFORE_WOOD_15_Geometry','SITE_KITCHEN_V12_GROUNDED_OUTER_COLUMN_STONE_BASES_Geometry']:
  ob=bpy.data.objects.get(n)
  if ob:removed.append(n);bpy.data.objects.remove(ob,do_unlink=True)
 col=bpy.data.collections.new('V24_03_厨房封墙与单柱檐廊');bpy.context.scene.collection.children.link(col)
 def mesh(name,V,F,mat):
  me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(V,[],F);me.materials.append(bpy.data.materials[mat]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True);assert all(e.is_manifold for e in bm.edges) and vol>0,(name,vol);bm.to_mesh(me);bm.free()
  uv=me.uv_layers.new(name='V24_03_Registered_Metric_UV')
  for p in me.polygons:
   for li in p.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((v.x if abs(p.normal.y)>.5 else v.y)/.65,v.z/.65)
  ob=bpy.data.objects.new(name,me);col.objects.link(ob);added.append(name);return ob
 def box(name,lo,hi,mat):
  x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
 def beam(name,a,b,r,mat,sides=24):
  a=Vector(a);b=Vector(b);d=(b-a).normalized();h=d.cross(Vector((0,0,1)))
  if h.length<.01:h=d.cross(Vector((0,1,0)))
  h.normalize();v=d.cross(h).normalized();V=[tuple(p+r*(h*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides)))for p in [a,b]for i in range(sides)];F=[list(range(sides-1,-1,-1)),list(range(sides,2*sides))]+[[i,(i+1)%sides,(i+1)%sides+sides,i+sides]for i in range(sides)];return mesh(name,V,F,mat)
 # Rear wall joins the existing masonry and closes the upper roof triangle.
 profile=[(7.70,-.414),(13.35,-.414),(13.35,3.367),(11.515,4.176),(9.05,3.215),(7.70,2.680)]
 V=[(x,y,z)for y in [-2.785,-2.595]for x,z in profile];n=len(profile);tri=tessellate_polygon([[Vector((x,z,0))for x,z in profile]]);idx={tuple(Vector((x,z,0))):i for i,(x,z)in enumerate(profile)};F=[]
 for t in tri:
  ii=list(t)if isinstance(t[0],int)else[idx[tuple(v)]for v in t];F.extend([ii,list(reversed([i+n for i in ii]))])
 F.extend([[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]);mesh('V24_03_Kitchen_Rear_Gable_Wall',V,F,'M_Grey_Brick')
 box('V24_03_Kitchen_Rear_Stone_Plinth',(7.69,-2.80,-.424),(13.36,-2.58,-.15),'M_Stone_Frame')
 # Exactly one freestanding veranda post, centred on the continuous lintel.
 x,y=7.891,-7.100;box('V24_03_Kitchen_Single_Column_Stone_Base',(x-.195,y-.195,-.405),(x+.195,y+.195,-.045),'M_V22_Kitchen_Chiselled_Gray_Stone')
 beam('V24_03_Kitchen_Single_Veranda_Column',(x,y,-.05),(x,y,2.445),.122,'M_V12_Kitchen_HONEY_WOOD',40)
 beam('V24_03_Kitchen_Single_Column_Foot_Ring',(x,y,-.052),(x,y,.018),.140,'M_V12_Kitchen_WOOD_DARK',40)
 box('V24_03_Kitchen_Single_Column_Abacus',(x-.155,y-.20,2.36),(x+.155,y+.20,2.445),'M_V12_Kitchen_HONEY_WOOD')
 for k,s in enumerate([-1,1]):beam('V24_03_Kitchen_Single_Column_Brace_'+str(k),(x,y+s*.05,2.08),(x,y+s*.48,2.40),.053,'M_V12_Kitchen_HONEY_WOOD',8)
 # Photo shows a corner rainwater pipe and a continuous wall-foot channel.
 beam('V24_03_Kitchen_Rear_Corner_Downpipe',(8.985,-2.825,-.305),(8.985,-2.825,3.10),.028,'M_PVC_Rainwater',20)
 beam('V24_03_Kitchen_Rear_Drain_Elbow',(8.985,-2.825,-.305),(8.985,-2.49,-.385),.028,'M_PVC_Rainwater',20)
 box('V24_03_Kitchen_Rear_Drain_Channel_Bed',(7.67,-2.56,-.46),(13.40,-2.36,-.435),'M_Stone')
 for k,y0 in enumerate([-2.57,-2.38]):box('V24_03_Kitchen_Rear_Drain_Channel_Edge_'+str(k),(7.67,y0,-.46),(13.40,y0+.025,-.385),'M_Stone_Frame')
 proof={'status':'PASS_KITCHEN_REAR_CLOSURE_AND_ONE_VERANDA_POST','removed_objects':removed,'changed_old_objects':changed,'added_objects':added,'new_objects':added,'freestanding_veranda_columns':1,'column_center_LOCAL_m':[x,y],'rear_wall_plane_y_m':[-2.785,-2.595],'rear_wall_upper_profile_xz':profile,'source':'User kitchen model screenshot 220256 and two supplied target/photo comparisons; existing registered footprint retained','corrections':['rear masonry and upper gable closed','four legacy freestanding post/base instances replaced by one centre post','post capital and diagonal braces support existing continuous lintel','rear rainwater downpipe and capped wall-foot drainage channel'],'material_shaders_modified':False}
 (out/'V24_03_Kitchen_Additional_Fixes.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');return proof
