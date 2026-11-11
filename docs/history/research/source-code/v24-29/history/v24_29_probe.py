import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
names={r['name']for r in json.loads(Path('E:/jz/JIA/Rebuild_V24_29/Reports/V24_29_Collision_Index.json').read_text())['objects']}
for x,y,z in [(6.5,-2.90,.12),(6.5,-3.0,.12),(8.27,-2.8,-.3),(8.04,-2.8,-.3),(10.,-2.8,-.3),(6.5,-3.35,.12)]:
 hits=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or o.name not in names:continue
  bb=[o.matrix_world@Vector(p)for p in o.bound_box]
  if not(min(p.x for p in bb)-.001<=x<=max(p.x for p in bb)+.001 and min(p.y for p in bb)-.001<=y<=max(p.y for p in bb)+.001):continue
  me=o.data;me.calc_loop_triangles();v=[o.matrix_world@p.co for p in me.vertices];f=[t.vertices[:]for t in me.loop_triangles];tree=BVHTree.FromPolygons(v,f,all_triangles=True)
  h=tree.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),10.)[0]
  if h:hits.append([round(h.z,6),o.name])
 print('HITS',x,y,z,sorted(hits,reverse=True),flush=True)
index=json.loads(Path('E:/jz/JIA/Rebuild_V24_29/Reports/V24_29_Collision_Index.json').read_text())['objects'];bounds=[];n=0
for row in index:n+=row['triangles'];bounds.append((n,row['name']))
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;me.calc_loop_triangles();tree=BVHTree.FromPolygons([cache.matrix_world@p.co for p in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True,epsilon=.00001)
for yy in [-3.119,-3.10,-2.95,-2.8,-2.0]:
 p=Vector((6.5,yy,-.45));bad=[]
 support=[]
 for dx,dy in [(0,0),(.227,0),(-.227,0),(0,.227),(0,-.227)]:
  hit,no,j,d=tree.ray_cast(Vector((p.x+dx,p.y+dy,p.z+.27)),Vector((0,0,-1)),.59)
  if hit:support.append((dx,dy,hit.z,next(name for end,name in bounds if j<end),list(no)))
 print('SUPPORT',yy,support,flush=True)
 if support:p.z=max(r[2]for r in support if r[4][2]>=.64)
 for i in range(7):
  centre=p+Vector((0,0,.215+(1.65-2*.215)*i/6))
  for loc,no,j,d in tree.find_nearest_range(centre,.212):
   if no.z>=.64 and loc.z<=p.z+.008:continue
   name=next(name for end,name in bounds if j<end);bad.append((name,[round(q,5)for q in loc],[round(q,5)for q in no],round(d,6)))
 print('CAPSULE',yy,bad[:15],flush=True)
