import bpy,bmesh,json,math,hashlib,numpy as np
from mathutils import Vector
from pathlib import Path
from v24_09_roof import Batch,h,old_h
from v24_03_junction_blender import _closed_stats,_box

def weather(name,lo,hi,rough=.94,scale=(15,15,15),distance=.0008,streaks=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=tuple((a+b)/2 for a,b in zip(lo,hi))+(1,);nt=m.node_tree;ns=nt.nodes;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.25
 co=ns.new('ShaderNodeNewGeometry');mul=ns.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scale;nt.links.new(co.outputs['Position'],mul.inputs[0]);tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1;tex.inputs['Detail'].default_value=3.2;nt.links.new(mul.outputs['Vector'],tex.inputs['Vector']);r=ns.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.23;r.color_ramp.elements[1].position=.76;r.color_ramp.elements[0].color=tuple(lo)+(1,);r.color_ramp.elements[1].color=tuple(hi)+(1,);nt.links.new(tex.outputs['Fac'],r.inputs['Fac']);nt.links.new(r.outputs['Color'],bs.inputs['Base Color'])
 micro=ns.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=95;micro.inputs['Detail'].default_value=2;nt.links.new(co.outputs['Position'],micro.inputs['Vector']);b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=distance;b.inputs['Strength'].default_value=.35;nt.links.new(micro.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
 m['V24_09_Source']='Native surface variation fitted to supplied screen-wall photographs; original photo textures untouched'
 return m
def materials():
 palette=[]
 for i,f in enumerate([.80,.93,1.0,1.10,1.20]):palette.append(weather('M_V24_09_Screenwall_Ceramic_'+str(i),(.050*f,.057*f,.054*f),(.112*f,.120*f,.110*f),.93,(5,5,8),.0007))
 trim=weather('M_V24_09_Screenwall_Gray_Moulding',(.16,.153,.137),(.28,.269,.239),.97,(7,7,4),.0008)
 lime=weather('M_V24_09_Screenwall_Aged_Lime',(.18,.185,.17),(.63,.625,.59),.98,(5,3,.50),.0011,True)
 field=weather('M_V24_09_Screenwall_Pale_Panel',(.44,.43,.40),(.66,.65,.61),.97,(7,7,7),.0007)
 return palette,trim,lime,field

def wall_route(work):
 fd=json.loads((Path(work)/'v19/Facade_Segments.json').read_text());ss=[]
 for r in fd['brick']:
  a,b=r['a'],r['b']
  if min(a[1],b[1])<-16 and abs(b[0]-a[0])>2*abs(b[1]-a[1])and max(a[0],b[0])>=3.2 and min(a[0],b[0])<=10.85:ss.append(r)
 def fy(x):
  cand=[r for r in ss if min(r['a'][0],r['b'][0])-1e-5<=x<=max(r['a'][0],r['b'][0])+1e-5]
  if not cand:cand=ss
  r=min(cand,key=lambda r:abs((r['a'][0]+r['b'][0])/2-x));a,b=r['a'],r['b'];return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
 return fy
def deform_crown():
 result=[]
 for name in['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
  o=bpy.data.objects[name];old=o.data;o.data=old.copy();wm=o.matrix_world;inv=wm.inverted();changes={}
  for v in o.data.vertices:
   p=wm@v.co
   if not(3.2499<=p.x<=10.8001 and -17.56<=p.y<=-16.25 and p.z>2.65):continue
   dh=h(p.x,p.y)-old_h(p.x,p.y)
   if abs(dh)<1e-8:continue
   w=max(0,min(1,(p.z-2.65)/(old_h(p.x,p.y)-.075-2.65)));d=dh*w;p.z+=d;v.co=inv@p;changes[v.index]=d
  # Preserve metre-scaled brick courses while the local end crown is fitted.
  if name.startswith('SITE_PERIMETER_')and o.data.uv_layers:
   uv=o.data.uv_layers.active
   for p in o.data.polygons:
    if o.data.materials[p.material_index].name!='M_V19_Perimeter_Brick':continue
    for li in p.loop_indices:
     i=o.data.loops[li].vertex_index
     if i in changes:uv.data[li].uv.y+=changes[i]/.9
  if changes:
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  o.data.update()
  if not old.users:bpy.data.meshes.remove(old)
  result.append({'name':name,'changed_vertex_count':len(changes),'maximum_crown_change_m':max(abs(x)for x in changes.values())if changes else 0,'affected_region_m':[3.25,10.8,-17.56,-16.25,2.65],'lower_foundation_and_xy_untouched':True})
 return result
def clear_screen_frames():
 n='SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry';o=bpy.data.objects[n];old=o.data;o.data=old.copy();bm=bmesh.new();bm.from_mesh(o.data);left=set(bm.verts);parts=[];delete=[]
 while left:
  v=left.pop();part={v};stack=[v]
  while stack:
   for e in stack.pop().link_edges:
    for q in e.verts:
     if q in left:left.remove(q);part.add(q);stack.append(q)
  pts=[o.matrix_world@v.co for v in part];a=[min(p[i]for p in pts)for i in range(3)];b=[max(p[i]for p in pts)for i in range(3)];cx=(a[0]+b[0])/2
  if 3.20<cx<10.85 and b[1]<-16.65 and a[2]>2.75:delete.extend(part);parts.append({'bounds':[a,b],'vertices':len(part)})
 bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update()
 if not old.users:bpy.data.meshes.remove(old)
 return {'name':n,'removed_complete_screen_components':parts,'other_inside_wall_frames_retained':True}

def panels(col,trim,field,work):
 fy=wall_route(work);band=Batch();frames=Batch();zig=Batch();spans=[];x=3.39
 for width in[1.45,.34,1.45,.34,1.45,.34,1.45]:spans.append((x,x+width));x+=width+.075
 def pos(x,dz,side,d):
  y=fy(x)+(.32 if side>0 else 0);return(x,y+side*d,h(x,y)-.075+dz)
 # Thin closed continuous backing, subdivided along the actual curved wall.
 for side in[-1,1]:
  xs=[3.25+(10.8-3.25)*i/120 for i in range(121)];V=[];F=[]
  for d,z in[(-.002,-.49),(.010,-.49),(.010,-.132),(-.002,-.132)]:V.extend(pos(xx,z,side,d)for xx in xs)
  N=len(xs)
  for j in range(4):
   J=(j+1)%4
   for i in range(N-1):F.append((j*N+i,j*N+i+1,J*N+i+1,J*N+i))
  F.extend([(3*N,2*N,N,0),(N-1,2*N-1,3*N-1,4*N-1)]);band.add(V,F)
  # Chamfered long/short panels with an outer stone border and a fine inner line.
  for s0,s1 in spans:
   for inset,w,d in[(0,.018,.022),(.031,.008,.018)]:
    a,b=s0+inset,s1-inset;z0,z1=-.445+inset,-.185-inset;c=.024
    outer=[(a+c,z0),(b-c,z0),(b,z0+c),(b,z1-c),(b-c,z1),(a+c,z1),(a,z1-c),(a,z0+c)]
    inner=[(a+c+w,z0+w),(b-c-w,z0+w),(b-w,z0+c+w),(b-w,z1-c-w),(b-c-w,z1-w),(a+c+w,z1-w),(a+w,z1-c-w),(a+w,z0+c+w)]
    # Corresponding edge subdivisions preserve curved head heights and closed rings.
    oo=[];ii=[]
    for k in range(8):
     A,B=outer[k],outer[(k+1)%8];C,D=inner[k],inner[(k+1)%8];n=max(1,math.ceil(abs(B[0]-A[0])/.06))
     for j in range(n):t=j/n;oo.append((A[0]*(1-t)+B[0]*t,A[1]*(1-t)+B[1]*t));ii.append((C[0]*(1-t)+D[0]*t,C[1]*(1-t)+D[1]*t))
    N=len(oo);V=[];F=[]
    for rr,dd in[(oo,.008),(ii,.008),(oo,d),(ii,d)]:V.extend(pos(xx,z,side,dd)for xx,z in rr)
    for j in range(N):
     J=(j+1)%N;F.extend([(j,J,N+J,N+j),(2*N+j,3*N+j,3*N+J,2*N+J),(j,2*N+j,2*N+J,J),(N+j,N+J,3*N+J,3*N+j)])
    frames.add(V,F)
  # Restrained saw-tooth plaster line above the panel row, as in the close-up.
  for i in range(83):
   a=3.28+i*.09;b=a+.086;c=(a+b)/2
   if b>10.77:continue
   vv=[pos(a,-.176,side,.008),pos(c,-.141,side,.008),pos(b,-.176,side,.008),pos(a,-.176,side,.025),pos(c,-.141,side,.025),pos(b,-.176,side,.025)];zig.add(vv,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
 added=[]
 for n,b,mat in[('V24_09_Screenwall_Curved_Panel_Backings',band,field),('V24_09_Screenwall_Long_Short_Moulded_Frames',frames,trim),('V24_09_Screenwall_Triangular_Frieze',zig,trim)]:added.append(b.object(col,n,[mat],False))
 # White framed inset end faces below the branched hip soffit.
 endbatch=Batch();endwhite=Batch()
 for x,sign in[(3.25,-1),(10.80,1)]:
  y=fy(x)+.16;z=h(x,y)-.075-.18;Y0=y-.127;Y1=y+.127;Z0=z-.29;Z1=z
  V=[(x+sign*d,yy,zz)for d in[-.002,.013]for yy,zz in[(Y0,Z0),(Y1,Z0),(Y1,Z1),(Y0,Z1)]];endwhite.add(V,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
  outer=[(Y0-.020,Z0-.020),(Y1+.020,Z0-.020),(Y1+.020,Z1+.020),(Y0-.020,Z1+.020)];inner=[(Y0,Z0),(Y1,Z0),(Y1,Z1),(Y0,Z1)];V=[];F=[]
  for rr,d in[(outer,.005),(inner,.005),(outer,.024),(inner,.024)]:V.extend((x+sign*d,yy,zz)for yy,zz in rr)
  for j in range(4):J=(j+1)%4;F.extend([(j,J,4+J,4+j),(8+j,12+j,12+J,8+J),(j,8+j,8+J,J),(4+j,4+J,12+J,12+j)])
  endbatch.add(V,F)
 added.append(endbatch.object(col,'V24_09_Screenwall_End_Panel_Stone_Frames',[trim],False));added.append(endwhite.object(col,'V24_09_Screenwall_White_End_Inset_Panels',[field],False))
 return {'added_objects':[o.name for o in added],'panel_spans_x_m':spans,'panels_per_face':7,'sides':2,'end_inset_panels':2,'geometry':{o.name:_closed_stats(o)for o in added}}

def inner_plaster(lime):
 o=bpy.data.objects['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry'];idx=len(o.data.materials);o.data.materials.append(lime);cnt=0
 photo=Path('D:/Desktop/问题/屏幕截图 2026-10-11 101327.jpg');im=bpy.data.images.load(str(photo),check_existing=False);im.name='V24_09_Actual_Inner_Screenwall_Plaster_Photo';im.pack();nt=lime.node_tree;ns=nt.nodes;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');uvn=ns.new('ShaderNodeUVMap');uvn.uv_map='V24_09_Actual_Plaster_Projective';tex=ns.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';nt.links.new(uvn.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bw=ns.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],bw.inputs['Color']);b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=.0010;b.inputs['Strength'].default_value=.22;nt.links.new(bw.outputs['Val'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],bs.inputs['Normal'])
 # Project the unchanged supplied photograph onto the body below the frieze.
 # This is native mesh UV work: no bitmap crop, retouch or image synthesis.
 src=[(0,0),(1,0),(1,1),(0,1)];dst=[(105/1645,1-852/961),(1416/1645,1-928/961),(1345/1645,1-361/961),(218/1645,1-350/961)];A=[];B=[]
 for (x,y),(u,v)in zip(src,dst):A.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]);B.extend([u,v])
 H=np.r_[np.linalg.solve(np.array(A),np.array(B)),1.].reshape(3,3);old_active=o.data.uv_layers.active_index;uv=o.data.uv_layers.new(name=uvn.uv_map);o.data.uv_layers.active_index=old_active
 for f in o.data.polygons:
  pts=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];c=sum(pts,Vector())/len(pts)
  if 2.80<c.x<11.25 and -17.16<c.y<-16.50:
   f.material_index=idx;cnt+=1
   for li,p in zip(f.loop_indices,pts):
    x=max(0,min(1,(10.80-p.x)/7.55));top=h(p.x,p.y)-.075-.49;y=max(0,min(1,(p.z+.45)/(top+.45)));q=H@np.array([x,y,1]);uv.data[li].uv=(q[0]/q[2],q[1]/q[2])
 lime['V24_09_Source']='Unmodified user photograph 101327; projective UV on screen-wall plaster only'
 return {'name':o.name,'screen_faces_assigned':cnt,'material':lime.name,'all_other_perimeter_plaster_slots_unchanged':True,'photo_path':str(photo),'packed_image':im.name,'photo_size_px':list(im.size),'source_unmodified_sha256':hashlib.sha256(photo.read_bytes()).hexdigest(),'packed_sha256':hashlib.sha256(bytes(im.packed_file.data)).hexdigest(),'method':'Native projective UV mapping onto the curved screen-wall face; original JPEG bytes packed unchanged'}
