"""Native framed/raised timber leaves, fitted mouldings and animated bronze hardware."""
import math
from mathutils import Vector

def improve_doors(bpy):
 import bmesh
 from v24_03_junction_blender import _mesh,_bounds
 sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();col=bpy.data.collections.get('V24_07_门扇与木门框')
 if col is None:col=bpy.data.collections.new('V24_07_门扇与木门框');sc.collection.children.link(col)
 mats=[bpy.data.materials[n]for n in ['M_V21_GATE_REF_06','M_V21_GATE_REF_07','M_V21_GATE_REF_08','M_V23_GATE_CAST_BRONZE']];changed=[];added=[];rows=[]
 def data():return[[],[],[]]
 def put(g,V,F,mat):
  off=len(g[0]);g[0].extend(V);g[1].extend([[off+i for i in f]for f in F]);g[2].extend([mat]*len(F))
 def box(g,lo,hi,mat=0):
  x,y,z=lo;X,Y,Z=hi;put(g,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],mat)
 def continuous_frame(g,x0,x1,z0,z1,yf,yb,stile):
  # A single closed extrusion with three apertures. Shared front/back
  # grid vertices eliminate coplanar rail/stile overlays at the joinery.
  xs=[x0,x0+stile,x1-stile,x1];zs=[z0,-.190,.150,.245,.830,.940,1.955,z1];V=[];F=[];ids={}
  def vid(i,k,back):
   key=(i,k,back)
   if key not in ids:ids[key]=len(V);V.append((xs[i],yb if back else yf,zs[k]))
   return ids[key]
  occupied={(i,k)for i in range(3)for k in range(7)if i!=1 or k%2==0}
  for i,k in occupied:
   F.extend([[vid(i,k,0),vid(i+1,k,0),vid(i+1,k+1,0),vid(i,k+1,0)],[vid(i,k,1),vid(i,k+1,1),vid(i+1,k+1,1),vid(i+1,k,1)]])
   for nb,a,b in[((i,k-1),(i,k),(i+1,k)),((i+1,k),(i+1,k),(i+1,k+1)),((i,k+1),(i+1,k+1),(i,k+1)),((i-1,k),(i,k+1),(i,k))]:
    if nb not in occupied:F.append([vid(*a,0),vid(*b,0),vid(*b,1),vid(*a,1)])
  put(g,V,F,0)
 def frame(g,x0,x1,z0,z1,y,profile,mat=1):
  V=[]
  for d,dy in profile:V.extend([(x0+d,y+dy,z0+d),(x1-d,y+dy,z0+d),(x1-d,y+dy,z1-d),(x0+d,y+dy,z1-d)])
  F=[];n=len(profile)
  for k in range(n):
   for j in range(4):F.append([4*k+j,4*k+(j+1)%4,4*((k+1)%n)+(j+1)%4,4*((k+1)%n)+j])
  put(g,V,F,mat)
 def panel(g,x0,x1,z0,z1,yfront,yback,inset=.026,proud=.009):
  # Edge tongue keys into the rails; the central field rises through a bevel.
  rings=[(0,yback),(0,yfront+.004),(inset,yfront-proud)];V=[]
  for d,y in rings:V.extend([(x0+d,y,z0+d),(x1-d,y,z0+d),(x1-d,y,z1-d),(x0+d,y,z1-d)])
  F=[[0,3,2,1],[8,9,10,11]]
  for k in range(2):
   for j in range(4):F.append([4*k+j,4*k+(j+1)%4,4*(k+1)+(j+1)%4,4*(k+1)+j])
  put(g,V,F,0)
 def boss(g,x,y,z,w=.049,h=.044):
  V=[(x-w,y,z),(x,y,z+h),(x+w,y,z),(x,y,z-h),(x-w,y+.018,z),(x,y+.018,z+h),(x+w,y+.018,z),(x,y+.018,z-h),(x,y-.013,z)]
  put(g,V,[[0,1,8],[1,2,8],[2,3,8],[3,0,8],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],1)
 def cylinder(g,x,y,z0,z1,r,mat=3,sec=24):
  V=[(x+r*math.cos(a),y+r*math.sin(a),z)for z in[z0,z1]for a in[math.tau*k/sec for k in range(sec)]];F=[list(range(sec-1,-1,-1)),list(range(sec,sec*2))]+[[k,(k+1)%sec,(k+1)%sec+sec,k+sec]for k in range(sec)];put(g,V,F,mat)
 def finish(name,g,old=None):
  ob=_mesh(bpy,col,name+'_TEMP',g[0],g[1],mats[0]);me=ob.data
  for m in mats[1:]:me.materials.append(m)
  for p,mi in zip(me.polygons,g[2]):p.material_index=mi
  uv=me.uv_layers.active
  for f in me.polygons:
   for li in f.loop_indices:
    p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.x*.72,p.z*.72)
  if old:
   inv=old.matrix_world.inverted()
   for v in me.vertices:v.co=inv@v.co
   prev=old.data;old.data=me;bpy.data.objects.remove(ob,do_unlink=True);ob=old;changed.append(name)
   if not prev.users:bpy.data.meshes.remove(prev)
  else:ob.name=name;added.append(name)
  ob['V24_07_References']='实景照片.jpg; 理想模型.png';me.update();return ob
 prof=[(0,.004),(.003,-.002),(.010,-.015),(.016,-.023),(.025,-.023),(.034,-.012),(.040,-.003),(.041,.012),(0,.012)]
 jambs=data();leafnames=['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']
 for n in leafnames:
  old=bpy.data.objects[n];hinge=old.matrix_world.translation.copy();bodyids={i for f in old.data.polygons if f.material_index==0 for i in f.vertices};bodypts=[old.matrix_world@old.data.vertices[i].co for i in bodyids];lo=[min(v[i]for v in bodypts)for i in range(3)];hi=[max(v[i]for v in bodypts)for i in range(3)];x0,x1=lo[0],hi[0];z0,z1=lo[2],hi[2];g=data()
  # Retain the sculpted bronze pull and shaped escutcheon already fitted to
  # this animated leaf. Replace the former three equal panel sheets.
  hfaces=[f for f in old.data.polygons if f.material_index==3 and all(math.hypot((p:=old.matrix_world@old.data.vertices[i].co).x-hinge.x,p.y-hinge.y)>.20 for i in f.vertices)];used={i for f in hfaces for i in f.vertices};ids={i:j for j,i in enumerate(sorted(used))};V=[tuple(old.matrix_world@old.data.vertices[i].co)for i in sorted(used)];F=[[ids[i]for i in f.vertices]for f in hfaces];put(g,V,F,3)
  yf=-11.574;yb=-11.494;stile=.090
  continuous_frame(g,x0,x1,z0,z1,yf,yb,stile)
  fields=[(-.190,.150),(.245,.830),(.940,1.955)];rails=[(z0,-.190),(.150,.245),(.830,.940),(1.955,z1)]
  for k,(a,b)in enumerate(fields):
   panel(g,x0+stile-.008,x1-stile+.008,a-.008,b+.008,yf,-11.500,.029,.010)
   frame(g,x0+stile+.004,x1-stile-.004,a+.004,b-.004,yf,prof)
   # Rear face carries a restrained moulding that stays inside the old back envelope.
   frame(g,x0+stile+.006,x1-stile-.006,a+.006,b-.006,yb,[(0,-.007),(.006,.002),(.017,.006),(.027,.002),(.033,-.007)])
  for k in[-1,0,1]:boss(g,(x0+x1)/2+k*.205,-11.596,-.020)
  # Fine applied arris along the long stiles, inset from the leaf perimeter.
  for x in[x0+.025,x1-.025]:box(g,(x-.004,-11.582,z0+.035),(x+.004,-11.570,z1-.035),1)
  for z in[.080,.805,1.675]:
   cylinder(g,hinge.x,hinge.y,z-.043,z+.043,.0115,3)
   cylinder(g,hinge.x,hinge.y,z-.048,z-.038,.014,3);cylinder(g,hinge.x,hinge.y,z+.038,z+.048,.014,3)
   # A keyed leaf wing meets the barrel and embeds in the original leaf body.
   sign=1 if n==leafnames[0]else-1;xa,xb=sorted([hinge.x,hinge.x+sign*.061]);box(g,(xa,-11.563,z-.026),(xb,-11.450,z+.026),3)
  finish(n,g,old)
  rows.append({'name':n,'leaf_bounds_closed_before':[lo,hi],'tall_upper_panel_z_m':[.940,1.955],'middle_panel_z_m':[.245,.830],'diamond_panel_z_m':[-.190,.150],'diamond_bosses':3,'hinge_axis_world':tuple(hinge),'retained_cast_handle_vertices':len(used),'panel_tongue_into_frame_m':.008,'original_action_and_pivot_preserved':True})
 # Thin fixed jambs remain outside the original inward sweep aperture.
 for x0,x1 in[(5.410,5.463),(7.737,7.790)]:
  box(jambs,(x0,-11.741,-.349),(x1,-11.464,2.435),0)
  box(jambs,(x0+.004,-11.758,-.325),(x1-.004,-11.735,2.414),1)
 jn='V24_07_Gate_Moulded_Timber_Jambs';finish(jn,jambs,bpy.data.objects.get(jn))
 # Keep the fixed wooden transom at its original aperture and deepen its
 # mitered outline. Preserve the existing cast scroll crest on its face.
 n='SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM_Geometry';old=bpy.data.objects[n];g=data();box(g,(5.45714,-11.751,2.0833),(7.74286,-11.426,2.438),0)
 frame(g,5.478,7.722,2.103,2.417,-11.751,[(d*.55,y*.68)for d,y in prof],1)
 frame(g,5.478,7.722,2.103,2.417,-11.426,[(0,-.006),(.006,.007),(.018,.012),(.026,-.006)],1)
 # The original non-lettered scroll has vertices in the central 0.94m field.
 fs=[f for f in old.data.polygons if all(6.129< (old.matrix_world@old.data.vertices[i].co).x <7.071 for i in f.vertices)and f.material_index==1]
 used={i for f in fs for i in f.vertices};ids={i:j for j,i in enumerate(sorted(used))};put(g,[tuple(old.matrix_world@old.data.vertices[i].co)for i in sorted(used)],[[ids[i]for i in f.vertices]for f in fs],1)
 for x in[5.80,7.40]:boss(g,x,-11.759,2.275,.026,.023)
 finish(n,g,old);sc.frame_set(40);bpy.context.view_layer.update()
 return{'changed_objects':changed,'added_objects':added,'leaves':rows,'panel_layout':'tall upper raised panel, medium lower panel, narrow diamond field, solid kick rail','continuous_joinery_frame':True,'original_26_door_animation_actions_preserved':True,'original_moving_leaf_names_and_parents_preserved':True,'new_surface_materials':False}
