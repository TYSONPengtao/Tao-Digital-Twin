"""Photo-based visible kitchen rafters, bearing ties, curved brackets and pendants."""
import math,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
def build_timber(bpy):
 import bmesh
 from v24_03_junction_blender import _mesh,_tree
 col=bpy.data.collections.new('V24_06_厨房檐廊木构');bpy.context.scene.collection.children.link(col)
 honey=bpy.data.materials['M_V12_Kitchen_HONEY_WOOD'];dark=bpy.data.materials['M_V12_Kitchen_WOOD_DARK'];gold=bpy.data.materials['M_V12_Kitchen_GOLDEN_WOOD'];groups={};changed=[];added=[]
 def group(name,mat):
  g=[[],[],mat];groups[name]=g;return g
 def append(g,V,F):
  k=len(g[0]);g[0].extend(V);g[1].extend([[k+i for i in f]for f in F])
 def box(g,lo,hi):
  x,y,z=lo;X,Y,Z=hi;append(g,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
 def beam(g,a,b,w,d):
  a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,0,1)))
  if u.length<.01:u=t.cross(Vector((0,1,0)))
  u.normalize();v=t.cross(u).normalized();V=[]
  for p in [a,b]:
   for su,sv in [(-1,-1),(1,-1),(1,1),(-1,1)]:V.append(tuple(p+u*su*w/2+v*sv*d/2))
  append(g,V,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]])
 def tube(g,path,r,sides=10):
  V=[]
  for j,p in enumerate(path):
   p=Vector(p);t=Vector(path[min(j+1,len(path)-1)])-Vector(path[max(j-1,0)]);t.normalize();u=t.cross(Vector((0,0,1)))
   if u.length<.01:u=t.cross(Vector((0,1,0)))
   u.normalize();v=t.cross(u).normalized()
   for i in range(sides):V.append(tuple(p+r*(u*math.cos(i*math.tau/sides)+v*math.sin(i*math.tau/sides))))
  F=[list(range(sides-1,-1,-1)),list(range((len(path)-1)*sides,len(path)*sides))]
  for j in range(len(path)-1):
   for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;F.append([a,b,b+sides,a+sides])
  append(g,V,F)
 def prism_x(g,poly,x0,x1):
  n=len(poly);V=[(x,y,z)for x in [x0,x1]for y,z in poly];p=[Vector((y,z,0))for y,z in poly];idx={tuple(v):i for i,v in enumerate(p)};F=[]
  for tri in tessellate_polygon([p]):
   ii=list(tri)if isinstance(tri[0],int)else[idx[tuple(v)]for v in tri];F.extend([ii,[i+n for i in reversed(ii)]])
  F.extend([[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)]);append(g,V,F)
 def curve(a,b,c,steps=14):return[(a[0]*(1-t)**2+2*b[0]*(1-t)*t+c[0]*t*t,a[1]*(1-t)**2+2*b[1]*(1-t)*t+c[1]*t*t)for t in [i/steps for i in range(steps+1)]]
 roof=[_tree(bpy.data.objects[n])for n in ['SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry']]
 def underside(x,y):
  hits=[h[0].z for t in roof if(h:=t.ray_cast(Vector((x,y,1)),Vector((0,0,1)),5))[0]is not None]
  if not hits:raise RuntimeError(('No roof bearing above rafter',x,y))
  return min(hits)
 raf=group('SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry',dark)
 ys=[-11.13+i*8.10/39 for i in range(40)]
 for y in ys:
  xe=13.47
  for k in range(25):
   try:ze=underside(xe,y);break
   except RuntimeError:xe-=.02
  else:raise RuntimeError(('Cannot locate east rafter bearing',y))
  for x0,x1 in [(7.10,11.515),(11.515,xe)]:beam(raf,(x0,y,underside(x0,y)-.043),(x1,y,underside(x1,y)-.043),.047,.069)
 ties=group('SITE_V22_KITCHEN_TRANSVERSE_EAVE_TIES_AND_HANGING_ENDS_Geometry',honey);carve=group('KITCHEN_V22_CARVED_PROJECTING_TIE_ENDS_Geometry',gold);pend=group('V24_06_Kitchen_Fluted_Melon_Pendants',honey)
 for y in [-11.20,-7.10,-2.98]:
  box(ties,(7.49,y-.078,2.365),(9.16,y+.078,2.515));box(ties,(7.47,y-.092,2.385),(7.61,y+.092,2.505));box(pend,(7.52,y-.027,2.285),(7.58,y+.027,2.391))
  # Closed six-lobed melon, hand-sculptable dense geometry.
  sec,rings=32,18;V=[(7.55,y,2.143)]
  for j in range(1,rings):
   ph=math.pi*j/rings;z=2.237-.094*math.cos(ph)
   for k in range(sec):
    a=math.tau*k/sec;r=.071*math.sin(ph)*(1+.11*math.cos(6*a));V.append((7.55+r*math.cos(a),y+r*math.sin(a),z))
  V.append((7.55,y,2.331));F=[]
  for k in range(sec):F.append([0,1+(k+1)%sec,1+k]);F.append([len(V)-1,1+(rings-2)*sec+k,1+(rings-2)*sec+(k+1)%sec])
  for j in range(rings-2):
   for k in range(sec):a=1+j*sec+k;b=1+j*sec+(k+1)%sec;F.append([a,b,b+sec,a+sec])
  append(pend,V,F)
  # Actual low relief rosette on the projecting tie's end grain.
  for p in range(5):
   ang=math.tau*p/5;path=[]
   for k in range(25):
    t=math.tau*k/24;u=.025+.022*math.cos(t);v=.010*math.sin(t);path.append((7.466,y+math.cos(ang)*u-math.sin(ang)*v,2.448+math.sin(ang)*u+math.cos(ang)*v))
   tube(carve,path,.0033,8)
 # Curved bearing brackets replace the two plain diagonal sticks.
 heads=group('V24_06_Kitchen_Carved_Bracket_Heads',honey);relief=group('V24_06_Kitchen_Bracket_Scroll_Relief',gold)
 for k,s in enumerate([-1,1]):
  g=group('V24_03_Kitchen_Single_Column_Brace_'+str(k),honey)
  poly=[(0,2.075),(.065,2.075)]+curve((.065,2.075),(.11,2.33),(.47,2.345))[1:]+[(.51,2.405),(.49,2.435),(0,2.435)]
  prism_x(g,[(-7.10+s*u,z)for u,z in poly],7.825,7.957)
  for sign in [-1,1]:
   x=7.821 if sign<0 else 7.961;path=[]
   for j in range(55):
    t=j/54;theta=math.tau*1.45*t;r=.052*(1-t)+.006;path.append((x,-7.10+s*(.265+r*math.cos(theta)),2.322+r*.58*math.sin(theta)))
   tube(relief,path,.0035,8)
 # Photo DJI_0156/0157 shows small curved heads on attached facade posts.
 for y in [-11.12,-7.10,-3.08]:
  for s in [-1,1]:
   poly=[(0,2.730),(.05,2.730)]+curve((.05,2.730),(.085,2.95),(.28,2.965))[1:]+[(.32,3.015),(.29,3.045),(0,3.045)]
   prism_x(heads,[(y+s*u,z)for u,z in poly],8.970,9.098)
   path=[]
   for j in range(46):
    t=j/45;theta=math.tau*1.4*t;r=.04*(1-t)+.004;path.append((8.966,y+s*(.16+r*math.cos(theta)),2.944+r*.65*math.sin(theta)))
   tube(relief,path,.003,8)
 pins=group('V24_06_Kitchen_Exposed_Timber_Pegs',dark)
 for y,z in [(-7.10,2.385),(-11.12,2.998),(-7.10,2.998),(-3.08,2.998)]:tube(pins,[(7.81 if z<2.5 else 8.954,y,z),(7.97 if z<2.5 else 9.116,y,z)],.012,16)
 for n,(V,F,mat)in groups.items():
  temp=_mesh(bpy,col,n+'_TEMP',V,F,mat);me=temp.data
  uv=me.uv_layers.active
  for p in me.polygons:
   for li in p.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.y if abs(p.normal.x)>.5 else v.x,v.z)
  old=bpy.data.objects.get(n)
  if old:
   inv=old.matrix_world.inverted()
   for v in me.vertices:v.co=inv@v.co
   data=old.data;old.data=me;bpy.data.objects.remove(temp,do_unlink=True);ob=old;changed.append(n)
   if not data.users:bpy.data.meshes.remove(data)
  else:temp.name=n;ob=temp;added.append(n)
  ob['V24_06_Photo_References']='172938.jpg; DJI_0156.JPG; DJI_0157.JPG'
  if 'Scroll'in n or'Pendants'in n or'CARVED_PROJECTING'in n:
   for p in ob.data.polygons:p.use_smooth=True
  if n in ['V24_06_Kitchen_Carved_Bracket_Heads','V24_06_Kitchen_Fluted_Melon_Pendants']:
   for o in bpy.context.selected_objects:o.select_set(False)
   ob.select_set(True);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('V24_06_Editable_Wood_Sculpt','MULTIRES');bpy.ops.object.multires_subdivide(modifier=mod.name,mode='SIMPLE');mod.levels=1;mod.sculpt_levels=1;mod.render_levels=1;ob.select_set(False)
  if n=='SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry':
   mod=ob.modifiers.new('Subtle_Hand_Finished_Edges','BEVEL');mod.width=.002;mod.segments=2
  ob.data.update()
 return {'changed_objects':changed,'added_objects':added,'rafter_pairs':40,'closed_rafter_pieces':80,'rafter_width_depth_m':[.047,.069],'tie_bearing_stations_y_m':[-11.20,-7.10,-2.98],'melon_pendants':3,'curved_facade_brackets':6,'independent_veranda_columns':1,'existing_round_purlins_retained':6,'materials_modified':False,'reference_files':['172938.jpg','DJI_0156.JPG','DJI_0157.JPG']}
