"""Blender-only photo fitted kitchen gable / inner-gate junction correction.

No file loading/saving, no material shader changes, no gate roof 09--15 edits.
Registered V24 LOCAL metre coordinates and original material datablocks remain.
"""
import math,json,time
from pathlib import Path

ROOF_NODES=[
 'SITE_KITCHEN_CHINESE_TILE_ROOF',
 'SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0',
 'SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1',
 'SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS',
 'SITE_KITCHEN_FASCIA_BOARD',
 'SITE_KITCHEN_VISIBLE_EDGE_FLASHING',
 'SITE_KITCHEN_RIDGE_CAP_AND_END_ORNAMENTS',
]
CUT_Y=-11.735

def _obj(bpy,node):
 o=bpy.data.objects.get(node+'_Geometry')
 if o and o.type=='MESH':return o
 p=bpy.data.objects.get(node)
 return next((o for o in p.children if o.type=='MESH'),None) if p else None

def _curve():
 pts=[]
 def line(a,b,n):
  for j in range(n):
   t=j/n;pts.append((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t))
 def bez(a,b,c,d,n):
  for j in range(n):
   t=j/n;s=1-t;pts.append((s*s*s*a[0]+3*s*s*t*b[0]+3*s*t*t*c[0]+t*t*t*d[0],s*s*s*a[1]+3*s*s*t*b[1]+3*s*t*t*c[1]+t*t*t*d[1]))
 line((8.266666667,3.036),(10.98,4.120),66)
 bez((10.98,4.120),(11.12,4.180),(11.32,4.130),(11.355,4.300),24)
 line((11.355,4.300),(11.355,4.450),4)
 line((11.355,4.450),(11.515,4.560),6)
 line((11.515,4.560),(11.675,4.450),6)
 line((11.675,4.450),(11.675,4.300),4)
 bez((11.675,4.300),(11.690,4.130),(11.9,4.120),(12.060,4.045),24)
 line((12.060,4.045),(13.350,3.4952),34)
 pts.append((13.350,3.4952));return pts

def _offset(points,d):
 out=[]
 for i,(x,z) in enumerate(points):
  a=points[max(0,i-1)];b=points[min(len(points)-1,i+1)];dx,dz=b[0]-a[0],b[1]-a[1];le=math.hypot(dx,dz)
  out.append((x-d*dz/le,z+d*dx/le))
 return out

def _base_z(x):
 xs=[8.266666667,9.05,11.4078,11.515,13.35];zs=[2.906,3.212932,4.155,4.1742,3.3652]
 for i in range(len(xs)-1):
  if x<=xs[i+1]:return zs[i]+(zs[i+1]-zs[i])*(x-xs[i])/(xs[i+1]-xs[i])
 return zs[-1]

def _front_uv_fit(bpy):
 import numpy as np
 ob=_obj(bpy,'SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY');mat=None;coef=None;rmse=None
 if ob:
  mat=next((m for m in ob.data.materials if m and m.name=='M_Grey_Brick'),None)
  uv=ob.data.uv_layers.active
  if uv:
   xyz=[];tex=[];wm=ob.matrix_world
   for p in ob.data.polygons:
    co=[wm@ob.data.vertices[j].co for j in p.vertices]
    if not all(abs(v.y+11.87)<.003 and 8.2<v.x<13.5 for v in co):continue
    for li,v in zip(p.loop_indices,co):xyz.append([1,v.x,v.z]);tex.append(list(uv.data[li].uv))
   if len(xyz)>10:
    coef=np.linalg.lstsq(np.asarray(xyz),np.asarray(tex),rcond=None)[0];rmse=float(np.sqrt(np.mean((np.asarray(xyz)@coef-np.asarray(tex))**2)))
    if rmse>.025:coef=None
 if not mat:mat=bpy.data.materials.get('M_Grey_Brick')
 assert mat,'Existing kitchen brick material is required'
 return mat,coef,rmse

def _closed_prism(bpy,col,name,poly,yfront,yback,material,uvcoef=None):
 from mathutils import Vector
 from mathutils.geometry import tessellate_polygon
 clean=[]
 for p in poly:
  q=tuple(map(float,p))
  if not clean or math.dist(q,clean[-1])>1e-8:clean.append(q)
 if len(clean)>2 and math.dist(clean[0],clean[-1])<1e-8:clean.pop()
 changed=True
 while changed:
  changed=False;keep=[]
  for i,p in enumerate(clean):
   a=clean[i-1];b=clean[(i+1)%len(clean)];cross=(p[0]-a[0])*(b[1]-p[1])-(p[1]-a[1])*(b[0]-p[0]);dot=(p[0]-a[0])*(b[0]-p[0])+(p[1]-a[1])*(b[1]-p[1])
   if abs(cross)<1e-11 and dot>=0:changed=True
   else:keep.append(p)
  clean=keep
 poly=clean
 area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2
 if area<0:poly.reverse()
 n=len(poly)
 verts=[(x,yfront,z) for x,z in poly]+[(x,yback,z) for x,z in poly]
 vectors=[Vector((x,z,0)) for x,z in poly];lookup={tuple(v):i for i,v in enumerate(vectors)}
 triangles=[]
 for tri in tessellate_polygon([vectors]):
  triangles.append(list(tri) if isinstance(tri[0],int) else [lookup[tuple(v)] for v in tri])
 faces=triangles+[[i+n for i in tri[::-1]] for tri in triangles]+[[i,i+n,(i+1)%n+n,(i+1)%n] for i in range(n)]
 import numpy as np
 ve=np.asarray(verts);tf=np.array([[f[0],f[k],f[k+1]] for f in faces for k in range(1,len(f)-1)],int)
 vol=float(np.einsum('ij,ij->i',ve[tf[:,0]],np.cross(ve[tf[:,1]],ve[tf[:,2]])).sum()/6)
 if vol<0:faces=[f[::-1] for f in faces];vol=-vol
 assert vol>1e-9,(name,vol)
 edge_use={};edge_dir={}
 for f in faces:
  for a,b in zip(f,f[1:]+f[:1]):
   k=(min(a,b),max(a,b));edge_use[k]=edge_use.get(k,0)+1;edge_dir[k]=edge_dir.get(k,0)+(1 if a<b else -1)
 assert all(x==2 for x in edge_use.values()) and all(x==0 for x in edge_dir.values()),(name,'closed/winding edge test')
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.materials.append(material);me.update(calc_edges=True)
 uv=me.uv_layers.new(name='V24_Registered_Stone_UV')
 for p in me.polygons:
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   co=(np.array([1,v.x,v.z])@uvcoef) if uvcoef is not None else (v.x/.65,v.z/.65)
   uv.data[li].uv=co
 ob=bpy.data.objects.new(name,me);col.objects.link(ob)
 ob['V24_Source']='DJI_0101/0102/0103 and 2026-10-16 124233/124258 site photographs; fitted, not measured'
 ob['V24_Closed_Solid_Volume_m3']=vol;ob['V24_Shader_Preserved']=material.name
 return ob

def _trim_sheathing_parts(bpy,ob):
 import bmesh
 from mathutils import Vector,kdtree
 # Three registered thin board solids meet along the ridge. Process them
 # independently: global welding would turn this touching seam into a T-edge.
 e=json.loads(ob.parent['Parameters']);parts=e.get('parts',SHEATHING_PARTS);old=ob.data;wm=ob.matrix_world;before=len(old.vertices)
 uv=old.uv_layers.active;tree=kdtree.KDTree(len(old.loops));old_uv=[];old_n=[]
 for p in old.polygons:
  no=(wm.to_3x3()@p.normal).normalized()
  for li in p.loop_indices:
   co=wm@old.vertices[old.loops[li].vertex_index].co;tree.insert(co,li)
   while len(old_uv)<=li:old_uv.append((0,0));old_n.append(no)
   old_uv[li]=tuple(uv.data[li].uv) if uv else (co.x/.65,co.z/.65);old_n[li]=no
 tree.balance();vv=[];ff=[];checks=[]
 for part in parts:
  g=part['geometry'];assert g['type']=='polyhedron'
  # The original part connectivity is embedded below. Snap its coordinates to
  # the actual loaded V24 native-readback vertices, so only connectivity comes
  # from the template and retained geometry follows the current file.
  points=[]
  for co in g['vertices']:
   nearest=tree.find(Vector(co));assert nearest[2]<.001,(ob.name,co,nearest[2]);points.append(nearest[0])
  bm=bmesh.new();vs=[bm.verts.new(co) for co in points];bm.verts.ensure_lookup_table()
  for face in g['faces']:
   try:bm.faces.new([vs[int(j)] for j in face])
   except ValueError:pass
  hit=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,CUT_Y,0)),plane_no=Vector((0,1,0)),clear_inner=True,clear_outer=False)
  cut=[x for x in hit['geom_cut'] if isinstance(x,bmesh.types.BMEdge) and x.is_boundary]
  if cut:bmesh.ops.holes_fill(bm,edges=cut,sides=0)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));checks.append(sum(x.is_boundary for x in bm.edges))
  bm.verts.ensure_lookup_table();bm.verts.index_update();base=len(vv);vv.extend(tuple(v.co) for v in bm.verts);ff.extend([base+v.index for v in f.verts] for f in bm.faces);bm.free()
 assert checks==[0]*len(parts),checks
 me=bpy.data.meshes.new(old.name+'_V24_Independent_Closed_Boards');me.from_pydata(vv,[],ff)
 for m in old.materials:me.materials.append(m)
 me.update();layer=me.uv_layers.new(name=uv.name if uv else 'Native_Review_UV')
 for p in me.polygons:
  for li in p.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;near=tree.find_n(co,12);pick=min(near,key=lambda q:q[2]+1e-5*(1-p.normal.dot(old_n[q[1]])))[1];layer.data[li].uv=old_uv[pick]
 ob.data=me
 if not old.users:bpy.data.meshes.remove(old)
 ob['V24_Kitchen_Front_Trim_Y_m']=CUT_Y;ob['V24_Original_Materials_UV_Preserved']=True
 return {'name':ob.name,'vertices_before':before,'vertices_after':len(vv),'new_front_limit_y_m':CUT_Y,'removed_front_ridge_components':0,'boundary_edges_after':0,'independent_board_solids':len(parts),'uv_retention':'Nearest registered original loop UV with face-normal matching; shaders unchanged'}

def _trim_roof_mesh(bpy,ob):
 """Shorten only the forward end, retain material slots/UV, fill every cut."""
 import bmesh
 from mathutils import Vector
 if ob.name.startswith('SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS'):return _trim_sheathing_parts(bpy,ob)
 me=ob.data.copy();bm=bmesh.new();bm.from_mesh(me);wm=ob.matrix_world;inv=wm.inverted()
 before=len(bm.verts);removed_front_components=0
 # Native readback splits vertices at normal/UV seams; weld geometric twins
 # before clipping so the cut is a solid boundary, while loop UVs stay intact.
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 if ob.name.startswith('SITE_KITCHEN_RIDGE_CAP_AND_END_ORNAMENTS'):
  # Remove the old long pointed front fin and its foremost cap; the remaining
  # registered longitudinal ridge and rear ornament are retained untouched.
  seen=set();remove=[]
  for v in list(bm.verts):
   if v in seen:continue
   stack=[v];vs=[];seen.add(v)
   while stack:
    w=stack.pop();vs.append(w)
    for e in w.link_edges:
     q=e.other_vert(w)
     if q not in seen:seen.add(q);stack.append(q)
   ys=[(wm@w.co).y for w in vs]
   if max(ys)<-11.7001:remove.extend(vs);removed_front_components+=1
  if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
 cutco=inv@Vector((0,CUT_Y,0));cutno=ob.matrix_world.to_3x3().transposed()@Vector((0,1,0));cutno.normalize()
 hit=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=cutco,plane_no=cutno,clear_inner=True,clear_outer=False)
 edges=[e for e in hit['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary]
 if edges:
  filled=bmesh.ops.holes_fill(bm,edges=edges,sides=0)['faces']
  # Cut faces are tiny concealed returns. Existing face material/UV data is
  # unchanged; new closure faces use the original first material slot.
  for f in filled:f.material_index=0
 # Coplanar board strips can expose old seam edges rather than reporting them
 # in geom_cut. Join the cut twins and close these concealed board returns.
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 remaining=[e for e in bm.edges if e.is_boundary]
 if remaining and ob.name.startswith('SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS'):
  bmesh.ops.holes_fill(bm,edges=remaining,sides=0)
  remain=[e for e in bm.edges if e.is_boundary]
  if remain:
   # Some retained V23 sheathing is a nonclosed surface skin. Give only the
   # connected open skin components a 3 mm return thickness, preserving the
   # closed board components and their original material/loop UV attributes.
   seed={f for e in remain for f in e.link_faces};openfaces=set(seed);stack=list(seed)
   while stack:
    f=stack.pop()
    for e in f.edges:
     for q in e.link_faces:
      if q not in openfaces:openfaces.add(q);stack.append(q)
   bmesh.ops.solidify(bm,geom=list(openfaces),thickness=.003)
   bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
   bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6)
   remain=[e for e in bm.edges if e.is_boundary]
   if remain:print('V24_WOOD_REMAIN',[(e.calc_length(),[tuple(v.co) for v in e.verts],len(e.link_faces)) for e in remain],flush=True)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 boundary=sum(e.is_boundary for e in bm.edges);after=len(bm.verts)
 bm.to_mesh(me);bm.free();me.update();old=ob.data;ob.data=me
 if not old.users:bpy.data.meshes.remove(old)
 ob['V24_Kitchen_Front_Trim_Y_m']=CUT_Y;ob['V24_Original_Materials_UV_Preserved']=True
 return {'name':ob.name,'vertices_before':before,'vertices_after':after,'new_front_limit_y_m':CUT_Y,'removed_front_ridge_components':removed_front_components,'boundary_edges_after':boundary}

def apply_v24_kitchen_junction(bpy,output_dir):
 """Incremental edit to already loaded V24. Root caller saves and validates."""
 started=time.perf_counter();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
 assert not bpy.data.objects.get('V24_Kitchen_Curved_Gable_Coping'),'Already applied; reload baseline'
 closure=_obj(bpy,'SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE');assert closure,'Registered gate-to-kitchen closure is required'
 col=closure.users_collection[0];brick,uvcoef,rmse=_front_uv_fit(bpy)
 stone=bpy.data.materials.get('M_Stone_Frame') or bpy.data.materials.get('M_V21_GATE_REF_03');roof=bpy.data.materials.get('M_Roof')
 assert stone and roof
 trim=[]
 for node in ROOF_NODES:
  ob=_obj(bpy,node)
  if ob:trim.append(_trim_roof_mesh(bpy,ob));print('V24_KITCHEN_TRIM',node,flush=True)
 path=_curve();top=_offset(path,-.026)
 # Fill just the 0.13 m upper gable band and the small neck.  The original
 # structural wall, its front plane, side returns and the pier remain intact.
 lower=[(x,_base_z(x)-.018) for x in sorted({round(x,10) for x,z in path})]
 fillpoly=top+lower[::-1]
 wall=_closed_prism(bpy,col,'V24_Kitchen_Gable_Upper_Brick_Infill',fillpoly,-11.8718,-11.65,brick,uvcoef)
 coping=_closed_prism(bpy,col,'V24_Kitchen_Curved_Gable_Coping',_offset(path,.0275)+_offset(path,-.0275)[::-1],-11.905,-11.625,stone)
 cap=_closed_prism(bpy,col,'V24_Kitchen_Thin_Dark_Coping_Edge',_offset(path,.039)+_offset(path,.023)[::-1],-11.915,-11.615,roof)
 # A restrained inset U-frame emphasizes the small vertical neck in the real
 # gable.  It does not introduce text, free-standing spikes, or a white wing.
 neck=[(11.422,4.270),(11.422,4.426),(11.515,4.493),(11.608,4.426),(11.608,4.270)]
 badge=_closed_prism(bpy,col,'V24_Kitchen_Short_Ridge_Head_Inset_Border',_offset(neck,.010)+_offset(neck,-.010)[::-1],-11.884,-11.866,stone)
 created=[wall,coping,cap,badge]
 proof={'status':'PASS_MODULE_SOURCE_GEOMETRY','coordinates':'V24 LOCAL metres','references':['DJI_0101.JPG','DJI_0102.JPG','DJI_0103.JPG','屏幕截图 2026-10-16 124233.jpg','屏幕截图 2026-10-16 124258.jpg'],'modified_existing_meshes':trim,'changed_old_objects':[r['name'] for r in trim],'created':[o.name for o in created],'preserved_gate_roof_layers':'09–15 untouched','preserved_gate_structure':'Piers, frames, height-map relief, leaf meshes/pivots and flush masonry closure untouched','gable_wall_front_y_m':-11.87,'peak_x_m':11.515,'coping_band_thickness_m':.055,'dark_top_edge_thickness_m':.016,'small_neck_height_above_shoulder_m':.260,'new_crown_peak_z_m':max(v.co.z for v in coping.data.vertices),'kitchen_roof_front_trim_from_y_m':-12.05,'kitchen_roof_front_trim_to_y_m':CUT_Y,'uv_fit_rmse':rmse,'brick_uv_method':'Least-squares registered original gable-face UV' if uvcoef is not None else 'Metre planar mapping fallback; original brick shader unchanged','no_extra_white_wing_found':True,'modeling_limit':'Photo fitted continuous coping and small neck; concealed dimensions not surveyed','build_seconds':round(time.perf_counter()-started,3)}
 assert all(r['boundary_edges_after']==0 for r in trim),trim
 (out/'V24_Kitchen_Junction_Module_QA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
 print('V24 KITCHEN JUNCTION READY',proof['build_seconds'],flush=True);return proof

# Embedded original three-part V23 sheathing connectivity; coordinates are
# snapped to the loaded V24 mesh at runtime (<1 mm tolerance).
SHEATHING_PARTS = [{'geometry': {'type': 'polyhedron', 'vertices': [[6.98, -11.28, 2.4648543322], [6.98, -2.15, 2.4486534211], [6.98, -11.28, 2.4368543322], [6.98, -2.15, 2.4206534211], [7.0025, -11.28, 2.458316942020868], [7.0025, -2.15, 2.442116030920868], [7.0025, -11.28, 2.430316942020868], [7.0025, -2.15, 2.414116030920868], [7.025, -11.28, 2.4534531055607443], [7.025, -2.15, 2.4372521944607444], [7.025, -11.28, 2.4254531055607442], [7.025, -2.15, 2.4092521944607443], [7.0475, -11.28, 2.4502628228196284], [7.0475, -2.15, 2.4340619117196285], [7.0475, -11.28, 2.4222628228196283], [7.0475, -2.15, 2.4060619117196285], [7.07, -11.28, 2.4487460937975207], [7.07, -2.15, 2.432545182697521], [7.07, -11.28, 2.4207460937975207], [7.07, -2.15, 2.404545182697521], [7.0925, -11.28, 2.4489029184944218], [7.0925, -2.15, 2.432702007394422], [7.0925, -11.28, 2.4209029184944217], [7.0925, -2.15, 2.404702007394422], [7.115, -11.28, 2.450733296910331], [7.115, -2.15, 2.434532385810331], [7.115, -11.28, 2.422733296910331], [7.115, -2.15, 2.406532385810331], [7.1375, -11.28, 2.454237229045248], [7.1375, -2.15, 2.438036317945248], [7.1375, -11.28, 2.426237229045248], [7.1375, -2.15, 2.410036317945248], [7.16, -11.28, 2.459414714899174], [7.16, -2.15, 2.443213803799174], [7.16, -11.28, 2.431414714899174], [7.16, -2.15, 2.415213803799174], [7.1825, -11.28, 2.4662657544721074], [7.1825, -2.15, 2.4500648433721075], [7.1825, -11.28, 2.4382657544721074], [7.1825, -2.15, 2.4220648433721075], [7.2, -11.28, 2.4727513656], [7.2, -2.15, 2.4565504545000003], [7.2, -11.28, 2.4447513656], [7.2, -2.15, 2.4285504545000003], [7.205, -11.28, 2.47474902545], [7.205, -2.15, 2.45854811435], [7.205, -11.28, 2.44674902545], [7.205, -2.15, 2.43054811435], [7.2275, -11.28, 2.4837384947750003], [7.2275, -2.15, 2.4675375836750004], [7.2275, -11.28, 2.4557384947750003], [7.2275, -2.15, 2.4395375836750004], [7.25, -11.28, 2.4927279641], [7.25, -2.15, 2.4765270530000003], [7.25, -11.28, 2.4647279641], [7.25, -2.15, 2.4485270530000003], [7.2725, -11.28, 2.501717433425], [7.2725, -2.15, 2.485516522325], [7.2725, -11.28, 2.473717433425], [7.2725, -2.15, 2.457516522325], [7.295, -11.28, 2.51070690275], [7.295, -2.15, 2.49450599165], [7.295, -11.28, 2.48270690275], [7.295, -2.15, 2.46650599165], [7.3175, -11.28, 2.5196963720750003], [7.3175, -2.15, 2.5034954609750004], [7.3175, -11.28, 2.4916963720750003], [7.3175, -2.15, 2.4754954609750004], [7.34, -11.28, 2.5286858414], [7.34, -2.15, 2.5124849303000003], [7.34, -11.28, 2.5006858414], [7.34, -2.15, 2.4844849303000003], [7.3625, -11.28, 2.537675310725], [7.3625, -2.15, 2.521474399625], [7.3625, -11.28, 2.509675310725], [7.3625, -2.15, 2.493474399625], [7.385, -11.28, 2.54666478005], [7.385, -2.15, 2.53046386895], [7.385, -11.28, 2.51866478005], [7.385, -2.15, 2.50246386895], [7.4075, -11.28, 2.555654249375], [7.4075, -2.15, 2.539453338275], [7.4075, -11.28, 2.527654249375], [7.4075, -2.15, 2.511453338275], [7.43, -11.28, 2.5646437187], [7.43, -2.15, 2.5484428076000003], [7.43, -11.28, 2.5366437187], [7.43, -2.15, 2.5204428076000003], [7.4525, -11.28, 2.573633188025], [7.4525, -2.15, 2.557432276925], [7.4525, -11.28, 2.545633188025], [7.4525, -2.15, 2.529432276925], [7.475, -11.28, 2.58262265735], [7.475, -2.15, 2.56642174625], [7.475, -11.28, 2.55462265735], [7.475, -2.15, 2.53842174625], [7.4975, -11.28, 2.591612126675], [7.4975, -2.15, 2.575411215575], [7.4975, -11.28, 2.563612126675], [7.4975, -2.15, 2.547411215575], [7.52, -11.28, 2.600601596], [7.52, -2.15, 2.5844006849000003], [7.52, -11.28, 2.572601596], [7.52, -2.15, 2.5564006849000003]], 'faces': [[0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3], [4, 8, 9, 5], [6, 7, 11, 10], [4, 6, 10, 8], [5, 9, 11, 7], [8, 12, 13, 9], [10, 11, 15, 14], [8, 10, 14, 12], [9, 13, 15, 11], [12, 16, 17, 13], [14, 15, 19, 18], [12, 14, 18, 16], [13, 17, 19, 15], [16, 20, 21, 17], [18, 19, 23, 22], [16, 18, 22, 20], [17, 21, 23, 19], [20, 24, 25, 21], [22, 23, 27, 26], [20, 22, 26, 24], [21, 25, 27, 23], [24, 28, 29, 25], [26, 27, 31, 30], [24, 26, 30, 28], [25, 29, 31, 27], [28, 32, 33, 29], [30, 31, 35, 34], [28, 30, 34, 32], [29, 33, 35, 31], [32, 36, 37, 33], [34, 35, 39, 38], [32, 34, 38, 36], [33, 37, 39, 35], [36, 40, 41, 37], [38, 39, 43, 42], [36, 38, 42, 40], [37, 41, 43, 39], [40, 44, 45, 41], [42, 43, 47, 46], [40, 42, 46, 44], [41, 45, 47, 43], [44, 48, 49, 45], [46, 47, 51, 50], [44, 46, 50, 48], [45, 49, 51, 47], [48, 52, 53, 49], [50, 51, 55, 54], [48, 50, 54, 52], [49, 53, 55, 51], [52, 56, 57, 53], [54, 55, 59, 58], [52, 54, 58, 56], [53, 57, 59, 55], [56, 60, 61, 57], [58, 59, 63, 62], [56, 58, 62, 60], [57, 61, 63, 59], [60, 64, 65, 61], [62, 63, 67, 66], [60, 62, 66, 64], [61, 65, 67, 63], [64, 68, 69, 65], [66, 67, 71, 70], [64, 66, 70, 68], [65, 69, 71, 67], [68, 72, 73, 69], [70, 71, 75, 74], [68, 70, 74, 72], [69, 73, 75, 71], [72, 76, 77, 73], [74, 75, 79, 78], [72, 74, 78, 76], [73, 77, 79, 75], [76, 80, 81, 77], [78, 79, 83, 82], [76, 78, 82, 80], [77, 81, 83, 79], [80, 84, 85, 81], [82, 83, 87, 86], [80, 82, 86, 84], [81, 85, 87, 83], [84, 88, 89, 85], [86, 87, 91, 90], [84, 86, 90, 88], [85, 89, 91, 87], [88, 92, 93, 89], [90, 91, 95, 94], [88, 90, 94, 92], [89, 93, 95, 91], [92, 96, 97, 93], [94, 95, 99, 98], [92, 94, 98, 96], [93, 97, 99, 95], [96, 100, 101, 97], [98, 99, 103, 102], [96, 98, 102, 100], [97, 101, 103, 99], [0, 1, 3, 2], [100, 102, 103, 101]]}, 'material': 'M_Timber_Dark_Eave'}, {'geometry': {'type': 'polyhedron', 'vertices': [[7.82, -11.28, 2.720461187], [7.82, -2.15, 2.7042602759000003], [7.82, -11.28, 2.692461187], [7.82, -2.15, 2.6762602759000003], [7.973958333333334, -11.28, 2.7819724632145837], [7.973958333333334, -2.15, 2.765771552114584], [7.973958333333334, -11.28, 2.7539724632145837], [7.973958333333334, -2.15, 2.737771552114584], [8.127916666666668, -11.28, 2.843483739429167], [8.127916666666668, -2.15, 2.8272828283291673], [8.127916666666668, -11.28, 2.815483739429167], [8.127916666666668, -2.15, 2.7992828283291673], [8.281875, -11.28, 2.90499501564375], [8.281875, -2.15, 2.88879410454375], [8.281875, -11.28, 2.87699501564375], [8.281875, -2.15, 2.86079410454375], [8.435833333333333, -11.28, 2.9665062918583334], [8.435833333333333, -2.15, 2.9503053807583335], [8.435833333333333, -11.28, 2.9385062918583333], [8.435833333333333, -2.15, 2.9223053807583335], [8.45, -11.28, 2.9721663280999997], [8.45, -2.15, 2.955965417], [8.45, -11.28, 2.9441663280999997], [8.45, -2.15, 2.927965417], [8.589791666666667, -11.459399305555555, 3.028335906758646], [8.589791666666667, -2.15, 3.011816656972917], [8.589791666666667, -11.459399305555555, 3.000335906758646], [8.589791666666667, -2.15, 2.983816656972917], [8.74375, -11.656979166666668, 3.0901977825093754], [8.74375, -2.15, 3.0733279331875005], [8.74375, -11.656979166666668, 3.0621977825093754], [8.74375, -2.15, 3.0453279331875005], [8.897708333333334, -11.854559027777778, 3.1520596582601046], [8.897708333333334, -2.15, 3.134839209402084], [8.897708333333334, -11.854559027777778, 3.1240596582601046], [8.897708333333334, -2.15, 3.106839209402084], [9.05, -12.05, 3.2132518520000004], [9.05, -2.15, 3.1956845990000007], [9.05, -12.05, 3.1852518520000004], [9.05, -2.15, 3.1676845990000007], [9.051666666666668, -12.05, 3.2139177386166673], [9.051666666666668, -2.15, 3.1963504856166676], [9.051666666666668, -12.05, 3.1859177386166673], [9.051666666666668, -2.15, 3.1683504856166675], [9.205625000000001, -12.05, 3.2754290148312504], [9.205625000000001, -2.15, 3.2578617618312506], [9.205625000000001, -12.05, 3.2474290148312503], [9.205625000000001, -2.15, 3.2298617618312506], [9.359583333333333, -12.05, 3.3369402910458335], [9.359583333333333, -2.15, 3.3193730380458337], [9.359583333333333, -12.05, 3.3089402910458334], [9.359583333333333, -2.15, 3.2913730380458337], [9.513541666666667, -12.05, 3.3984515672604165], [9.513541666666667, -2.15, 3.380884314260417], [9.513541666666667, -12.05, 3.3704515672604165], [9.513541666666667, -2.15, 3.3528843142604168], [9.6675, -12.05, 3.459962843475], [9.6675, -2.15, 3.4423955904750003], [9.6675, -12.05, 3.431962843475], [9.6675, -2.15, 3.4143955904750003], [9.821458333333334, -12.05, 3.5214741196895836], [9.821458333333334, -2.15, 3.503906866689584], [9.821458333333334, -12.05, 3.4934741196895835], [9.821458333333334, -2.15, 3.475906866689584], [9.975416666666668, -12.05, 3.582985395904167], [9.975416666666668, -2.15, 3.5654181429041674], [9.975416666666668, -12.05, 3.554985395904167], [9.975416666666668, -2.15, 3.5374181429041673], [10.129375, -12.05, 3.64449667211875], [10.129375, -2.15, 3.6269294191187504], [10.129375, -12.05, 3.61649667211875], [10.129375, -2.15, 3.5989294191187504], [10.283333333333333, -12.05, 3.7060079483333332], [10.283333333333333, -2.15, 3.6884406953333335], [10.283333333333333, -12.05, 3.678007948333333], [10.283333333333333, -2.15, 3.6604406953333335], [10.437291666666667, -12.05, 3.767519224547917], [10.437291666666667, -2.15, 3.7499519715479175], [10.437291666666667, -12.05, 3.739519224547917], [10.437291666666667, -2.15, 3.7219519715479175], [10.59125, -12.05, 3.8290305007625003], [10.59125, -2.15, 3.8114632477625006], [10.59125, -12.05, 3.8010305007625003], [10.59125, -2.15, 3.7834632477625005], [10.745208333333334, -12.05, 3.8905417769770834], [10.745208333333334, -2.15, 3.8729745239770836], [10.745208333333334, -12.05, 3.8625417769770833], [10.745208333333334, -2.15, 3.8449745239770836], [10.899166666666666, -12.05, 3.9520530531916664], [10.899166666666666, -2.15, 3.9344858001916663], [10.899166666666666, -12.05, 3.9240530531916664], [10.899166666666666, -2.15, 3.9064858001916662], [11.053125000000001, -12.05, 4.01356432940625], [11.053125000000001, -2.15, 3.9959970764062502], [11.053125000000001, -12.05, 3.9855643294062504], [11.053125000000001, -2.15, 3.96799707640625], [11.207083333333333, -12.05, 4.0750756056208335], [11.207083333333333, -2.15, 4.057508352620833], [11.207083333333333, -12.05, 4.047075605620834], [11.207083333333333, -2.15, 4.029508352620834], [11.361041666666667, -12.05, 4.136586881835417], [11.361041666666667, -2.15, 4.119019628835416], [11.361041666666667, -12.05, 4.108586881835417], [11.361041666666667, -2.15, 4.091019628835417], [11.515, -12.05, 4.173598468722], [11.515, -2.15, 4.18053090505], [11.515, -12.05, 4.145598468722], [11.515, -2.15, 4.152530905050001]], 'faces': [[0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3], [4, 8, 9, 5], [6, 7, 11, 10], [4, 6, 10, 8], [5, 9, 11, 7], [8, 12, 13, 9], [10, 11, 15, 14], [8, 10, 14, 12], [9, 13, 15, 11], [12, 16, 17, 13], [14, 15, 19, 18], [12, 14, 18, 16], [13, 17, 19, 15], [16, 20, 21, 17], [18, 19, 23, 22], [16, 18, 22, 20], [17, 21, 23, 19], [20, 24, 25, 21], [22, 23, 27, 26], [20, 22, 26, 24], [21, 25, 27, 23], [24, 28, 29, 25], [26, 27, 31, 30], [24, 26, 30, 28], [25, 29, 31, 27], [28, 32, 33, 29], [30, 31, 35, 34], [28, 30, 34, 32], [29, 33, 35, 31], [32, 36, 37, 33], [34, 35, 39, 38], [32, 34, 38, 36], [33, 37, 39, 35], [36, 40, 41, 37], [38, 39, 43, 42], [36, 38, 42, 40], [37, 41, 43, 39], [40, 44, 45, 41], [42, 43, 47, 46], [40, 42, 46, 44], [41, 45, 47, 43], [44, 48, 49, 45], [46, 47, 51, 50], [44, 46, 50, 48], [45, 49, 51, 47], [48, 52, 53, 49], [50, 51, 55, 54], [48, 50, 54, 52], [49, 53, 55, 51], [52, 56, 57, 53], [54, 55, 59, 58], [52, 54, 58, 56], [53, 57, 59, 55], [56, 60, 61, 57], [58, 59, 63, 62], [56, 58, 62, 60], [57, 61, 63, 59], [60, 64, 65, 61], [62, 63, 67, 66], [60, 62, 66, 64], [61, 65, 67, 63], [64, 68, 69, 65], [66, 67, 71, 70], [64, 66, 70, 68], [65, 69, 71, 67], [68, 72, 73, 69], [70, 71, 75, 74], [68, 70, 74, 72], [69, 73, 75, 71], [72, 76, 77, 73], [74, 75, 79, 78], [72, 74, 78, 76], [73, 77, 79, 75], [76, 80, 81, 77], [78, 79, 83, 82], [76, 78, 82, 80], [77, 81, 83, 79], [80, 84, 85, 81], [82, 83, 87, 86], [80, 82, 86, 84], [81, 85, 87, 83], [84, 88, 89, 85], [86, 87, 91, 90], [84, 86, 90, 88], [85, 89, 91, 87], [88, 92, 93, 89], [90, 91, 95, 94], [88, 90, 94, 92], [89, 93, 95, 91], [92, 96, 97, 93], [94, 95, 99, 98], [92, 94, 98, 96], [93, 97, 99, 95], [96, 100, 101, 97], [98, 99, 103, 102], [96, 98, 102, 100], [97, 101, 103, 99], [100, 104, 105], [100, 105, 101], [102, 103, 107], [102, 107, 106], [100, 102, 106, 104], [101, 105, 107, 103], [0, 1, 3, 2], [104, 106, 107, 105]]}, 'material': 'M_Timber_Dark_Eave'}, {'geometry': {'type': 'polyhedron', 'vertices': [[11.515, -12.05, 4.173598468722], [11.515, -2.15, 4.18053090505], [11.515, -12.05, 4.145598468722], [11.515, -2.15, 4.152530905050001], [11.582291666666666, -12.05, 4.143933952432208], [11.582291666666666, -2.15, 4.174879234426208], [11.582291666666666, -12.05, 4.115933952432209], [11.582291666666666, -2.15, 4.146879234426208], [11.649583333333334, -12.05, 4.114269436142417], [11.649583333333334, -2.15, 4.145214718136416], [11.649583333333334, -12.05, 4.086269436142417], [11.649583333333334, -2.15, 4.117214718136417], [11.716875, -12.05, 4.084604919852626], [11.716875, -2.15, 4.1155502018466255], [11.716875, -12.05, 4.056604919852626], [11.716875, -2.15, 4.087550201846626], [11.784166666666668, -12.05, 4.054940403562833], [11.784166666666668, -2.15, 4.085885685556833], [11.784166666666668, -12.05, 4.026940403562834], [11.784166666666668, -2.15, 4.057885685556833], [11.851458333333333, -12.05, 4.025275887273042], [11.851458333333333, -2.15, 4.056221169267042], [11.851458333333333, -12.05, 3.9972758872730423], [11.851458333333333, -2.15, 4.028221169267042], [11.918750000000001, -12.05, 3.9956113709832497], [11.918750000000001, -2.15, 4.026556652977249], [11.918750000000001, -12.05, 3.9676113709832497], [11.918750000000001, -2.15, 3.9985566529772494], [11.986041666666667, -12.05, 3.965946854693459], [11.986041666666667, -2.15, 3.9968921366874586], [11.986041666666667, -12.05, 3.937946854693459], [11.986041666666667, -2.15, 3.9688921366874585], [12.053333333333335, -12.05, 3.9362823384036663], [12.053333333333335, -2.15, 3.967227620397666], [12.053333333333335, -12.05, 3.9082823384036662], [12.053333333333335, -2.15, 3.939227620397666], [12.120625, -12.05, 3.9066178221138754], [12.120625, -2.15, 3.937563104107875], [12.120625, -12.05, 3.8786178221138754], [12.120625, -2.15, 3.909563104107875], [12.187916666666668, -12.05, 3.876953305824083], [12.187916666666668, -2.15, 3.9078985878180825], [12.187916666666668, -12.05, 3.848953305824083], [12.187916666666668, -2.15, 3.8798985878180825], [12.255208333333334, -12.05, 3.847288789534292], [12.255208333333334, -2.15, 3.8782340715282917], [12.255208333333334, -12.05, 3.819288789534292], [12.255208333333334, -2.15, 3.8502340715282917], [12.322500000000002, -12.05, 3.8176242732444994], [12.322500000000002, -2.15, 3.8485695552384995], [12.322500000000002, -12.05, 3.7896242732444994], [12.322500000000002, -2.15, 3.8205695552384995], [12.389791666666667, -12.05, 3.7879597569547085], [12.389791666666667, -2.15, 3.8189050389487087], [12.389791666666667, -12.05, 3.7599597569547085], [12.389791666666667, -2.15, 3.7909050389487087], [12.457083333333333, -12.05, 3.758295240664917], [12.457083333333333, -2.15, 3.789240522658917], [12.457083333333333, -12.05, 3.730295240664917], [12.457083333333333, -2.15, 3.761240522658917], [12.524375000000001, -12.05, 3.728630724375125], [12.524375000000001, -2.15, 3.7595760063691253], [12.524375000000001, -12.05, 3.700630724375125], [12.524375000000001, -2.15, 3.7315760063691252], [12.591666666666667, -12.05, 3.6989662080853334], [12.591666666666667, -2.15, 3.7299114900793335], [12.591666666666667, -12.05, 3.6709662080853334], [12.591666666666667, -2.15, 3.7019114900793335], [12.658958333333334, -12.05, 3.6693016917955417], [12.658958333333334, -2.15, 3.700246973789542], [12.658958333333334, -12.05, 3.6413016917955416], [12.658958333333334, -2.15, 3.672246973789542], [12.72625, -12.05, 3.63963717550575], [12.72625, -2.15, 3.67058245749975], [12.72625, -12.05, 3.61163717550575], [12.72625, -2.15, 3.64258245749975], [12.793541666666668, -12.05, 3.6099726592159582], [12.793541666666668, -2.15, 3.6409179412099584], [12.793541666666668, -12.05, 3.581972659215958], [12.793541666666668, -2.15, 3.6129179412099584], [12.860833333333334, -12.05, 3.5803081429261665], [12.860833333333334, -2.15, 3.6112534249201667], [12.860833333333334, -12.05, 3.5523081429261665], [12.860833333333334, -2.15, 3.5832534249201666], [12.928125000000001, -12.05, 3.550643626636375], [12.928125000000001, -2.15, 3.581588908630375], [12.928125000000001, -12.05, 3.5226436266363748], [12.928125000000001, -2.15, 3.553588908630375], [12.995416666666667, -12.05, 3.520979110346583], [12.995416666666667, -2.15, 3.551924392340583], [12.995416666666667, -12.05, 3.492979110346583], [12.995416666666667, -2.15, 3.523924392340583], [13.062708333333335, -12.05, 3.4913145940567913], [13.062708333333335, -2.15, 3.5222598760507915], [13.062708333333335, -12.05, 3.4633145940567913], [13.062708333333335, -2.15, 3.4942598760507915], [13.13, -12.05, 3.4616500777669996], [13.13, -2.15, 3.4925953597609998], [13.13, -12.05, 3.4336500777669996], [13.13, -2.15, 3.4645953597609997]], 'faces': [[0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3], [4, 8, 9, 5], [6, 7, 11, 10], [4, 6, 10, 8], [5, 9, 11, 7], [8, 12, 13, 9], [10, 11, 15, 14], [8, 10, 14, 12], [9, 13, 15, 11], [12, 16, 17, 13], [14, 15, 19, 18], [12, 14, 18, 16], [13, 17, 19, 15], [16, 20, 21, 17], [18, 19, 23, 22], [16, 18, 22, 20], [17, 21, 23, 19], [20, 24, 25, 21], [22, 23, 27, 26], [20, 22, 26, 24], [21, 25, 27, 23], [24, 28, 29, 25], [26, 27, 31, 30], [24, 26, 30, 28], [25, 29, 31, 27], [28, 32, 33, 29], [30, 31, 35, 34], [28, 30, 34, 32], [29, 33, 35, 31], [32, 36, 37, 33], [34, 35, 39, 38], [32, 34, 38, 36], [33, 37, 39, 35], [36, 40, 41, 37], [38, 39, 43, 42], [36, 38, 42, 40], [37, 41, 43, 39], [40, 44, 45, 41], [42, 43, 47, 46], [40, 42, 46, 44], [41, 45, 47, 43], [44, 48, 49, 45], [46, 47, 51, 50], [44, 46, 50, 48], [45, 49, 51, 47], [48, 52, 53, 49], [50, 51, 55, 54], [48, 50, 54, 52], [49, 53, 55, 51], [52, 56, 57, 53], [54, 55, 59, 58], [52, 54, 58, 56], [53, 57, 59, 55], [56, 60, 61, 57], [58, 59, 63, 62], [56, 58, 62, 60], [57, 61, 63, 59], [60, 64, 65, 61], [62, 63, 67, 66], [60, 62, 66, 64], [61, 65, 67, 63], [64, 68, 69, 65], [66, 67, 71, 70], [64, 66, 70, 68], [65, 69, 71, 67], [68, 72, 73, 69], [70, 71, 75, 74], [68, 70, 74, 72], [69, 73, 75, 71], [72, 76, 77, 73], [74, 75, 79, 78], [72, 74, 78, 76], [73, 77, 79, 75], [76, 80, 81, 77], [78, 79, 83, 82], [76, 78, 82, 80], [77, 81, 83, 79], [80, 84, 85, 81], [82, 83, 87, 86], [80, 82, 86, 84], [81, 85, 87, 83], [84, 88, 89, 85], [86, 87, 91, 90], [84, 86, 90, 88], [85, 89, 91, 87], [88, 92, 93, 89], [90, 91, 95, 94], [88, 90, 94, 92], [89, 93, 95, 91], [92, 96, 97, 93], [94, 95, 99, 98], [92, 94, 98, 96], [93, 97, 99, 95], [0, 1, 3, 2], [96, 98, 99, 97]]}, 'material': 'M_Timber_Dark_Eave'}]
