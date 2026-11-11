"""Blender-only V24 stone bas-relief from a packed grayscale reference atlas.

Call apply_v24_relief(bpy, atlas_path, output_dir) after opening the V23 .blend.
Does not load/save a blend, change scene materials, render, or export geometry.
Atlas layout JSON is optional: Gate_Carving_HeightAtlas_Layout.json adjacent to
the PNG, with normalized bottom-left UV rectangles under ``cells``.  Keys are
bamboo, flowers, vine, header.  Default is four equal left-to-right cells.
"""
import json, math, hashlib, time
from pathlib import Path
import numpy as np

NODE04='SITE_V21_GATE_REFERENCE_LAYER_04'
NODE05='SITE_V21_GATE_REFERENCE_LAYER_05'
MAT='M_V21_GATE_REF_04'

def _atlas_layout(path):
 p=Path(path).with_name('Gate_Carving_HeightAtlas_Layout.json')
 if p.exists():
  d=json.loads(p.read_text(encoding='utf8'));cells=d.get('cells',d)
  return {k:list(map(float,cells[k].get('uv_rect',cells[k]) if isinstance(cells[k],dict) else cells[k])) for k in ['bamboo','flowers','vine','header']}
 return {k:[j/4,0,(j+1)/4,1] for j,k in enumerate(['bamboo','flowers','vine','header'])}

def _read_gray(bpy,path):
 im=bpy.data.images.load(str(path),check_existing=True)
 im.colorspace_settings.name='Non-Color';im.use_fake_user=True
 w,h=map(int,im.size);px=np.empty(w*h*4,np.float32);im.pixels.foreach_get(px)
 p=px.reshape(h,w,4);gray=p[...,:3].mean(axis=2)
 assert w>16 and h>16 and np.isfinite(gray).all(), 'Invalid grayscale atlas'
 if not im.packed_file:im.pack()
 return im,gray

def _sample(gray,rect,nx,nz):
 u0,v0,u1,v1=rect
 assert 0<=u0<u1<=1 and 0<=v0<v1<=1,rect
 h,w=gray.shape;uu=np.linspace(u0,u1,nx+1)*(w-1);vv=np.linspace(v0,v1,nz+1)*(h-1)
 xx,yy=np.meshgrid(uu,vv);x=np.floor(xx).astype(int);y=np.floor(yy).astype(int);fx=xx-x;fy=yy-y
 x1=np.minimum(x+1,w-1);y1=np.minimum(y+1,h-1)
 a=gray[y,x]*(1-fx)*(1-fy)+gray[y,x1]*fx*(1-fy)+gray[y1,x]*(1-fx)*fy+gray[y1,x1]*fx*fy
 lo,hi=np.quantile(a,[.08,.995]);assert hi-lo>.025, 'Atlas cell has insufficient relief contrast'
 a=np.clip((a-lo)/(hi-lo),0,1)
 # One separable binomial surface pass suppresses pixel ridges while retaining
 # the reference motif.  This is numerical smoothing, not a manual sculpt.
 p=np.pad(a,((1,1),(1,1)),mode='edge')
 a=(p[:-2,:-2]+2*p[:-2,1:-1]+p[:-2,2:]+2*p[1:-1,:-2]+4*p[1:-1,1:-1]+2*p[1:-1,2:]+p[2:,:-2]+2*p[2:,1:-1]+p[2:,2:])/16
 # Four grid intervals produce a clean, physically supported stone border.
 ez=np.minimum(np.arange(nz+1),np.arange(nz,-1,-1))/4
 ex=np.minimum(np.arange(nx+1),np.arange(nx,-1,-1))/4
 fade=np.minimum(1,ez[:,None])*np.minimum(1,ex[None,:])
 return np.power(a,1.08)*np.sin(np.minimum(1,fade)*math.pi/2)**2, {'cell_percentile_low':float(lo),'cell_percentile_high':float(hi)}

def _panel_mesh_arrays(gray,rect,a,b,z0,z1,nx,nz,depth,front=-.001,back=.009):
 """Return closed geometry: dense raised front, boundary side skirt, planar back.

 a,b delimit the backing width in plan; positive normal points into the pier.
 The front and back planes match the V23 inserts, filling the existing recess.
 """
 a=np.array(a,float);b=np.array(b,float);t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]])
 heights,stats=_sample(gray,rect,nx,nz);width=float(np.linalg.norm(b-a))
 xx,zz=np.meshgrid(np.linspace(0,width,nx+1),np.linspace(z0,z1,nz+1))
 dd=front-depth*heights
 xy=a+xx[...,None]*t+dd[...,None]*n
 verts=np.c_[xy.reshape(-1,2),zz.ravel()].tolist()
 u0,v0,u1,v1=rect;uu,vv=np.meshgrid(np.linspace(u0,u1,nx+1),np.linspace(v0,v1,nz+1))
 uvs=np.c_[uu.ravel(),vv.ravel()].tolist();faces=[]
 for j in range(nz):
  row=j*(nx+1)
  for i in range(nx):
   p=row+i;faces.append([p,p+1,p+nx+2,p+nx+1])
 # Counterclockwise front perimeter, seen from outside (negative normal).
 boundary=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,nz+1)]+[nz*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(nz-1,0,-1)]
 backs=[]
 for p in boundary:
  q=np.array(verts[p]);q[:2]+=n*(back-dd.ravel()[p]);backs.append(len(verts));verts.append(q.tolist());uvs.append(uvs[p])
 for j,p in enumerate(boundary):
  k=(j+1)%len(boundary);faces.append([p,backs[j],backs[k],boundary[k]])
 # Avoid a thousand-edge centre fan: Catmull-Clark's extraordinary-vertex
 # limit calculation scales catastrophically with that valence.  A graded
 # back grid decimates from the dense top/bottom rim to three longitudinal
 # strips, keeping vertex valence bounded without doubling the front grid.
 boundary_back=dict(zip(boundary,backs));rows=[]
 max_rank=max(0,int(math.ceil(math.log2(max(1,nx/3)))))
 for j in range(nz+1):
  rank=min(j,nz-j,max_rank);count=max(3,int(math.ceil(nx/2**rank)))
  if j in [0,nz]:count=nx
  row=[]
  for i in range(count+1):
   if j in [0,nz]:idx=boundary_back[j*(nx+1)+i]
   elif i==0:idx=boundary_back[j*(nx+1)]
   elif i==count:idx=boundary_back[j*(nx+1)+nx]
   else:
    q=a+(b-a)*i/count+n*back;idx=len(verts);verts.append([q[0],q[1],z0+(z1-z0)*j/nz]);uvs.append([u0+(u1-u0)*i/count,v0+(v1-v0)*j/nz])
   row.append(idx)
  rows.append(row)
 for r,s in zip(rows,rows[1:]):
  nr,ns=len(r)-1,len(s)-1;i=j=0
  while i<nr or j<ns:
   u=(i+1)/nr if i<nr else float('inf');v=(j+1)/ns if j<ns else float('inf')
   if abs(u-v)<1e-10:faces.append([r[i],s[j],s[j+1],r[i+1]]);i+=1;j+=1
   elif u<v:faces.append([r[i],s[j],r[i+1]]);i+=1
   else:faces.append([r[i],s[j],s[j+1]]);j+=1
 # Check orientation by signed volume, then normalize to outward normals.
 ve=np.asarray(verts);tris=np.array([[f[0],f[k],f[k+1]] for f in faces for k in range(1,len(f)-1)],dtype=np.int32)
 vol=float(np.einsum('ij,ij->i',ve[tris[:,0]],np.cross(ve[tris[:,1]],ve[tris[:,2]])).sum()/6)
 if vol<0:faces=[f[::-1] for f in faces];vol=-vol
 assert vol>0 and np.isfinite(ve).all()
 # Exact edge incidence validates the closed backing and all side skirts.
 edges=np.array([[x,y] for f in faces for x,y in zip(f,f[1:]+f[:1])],dtype=np.int32);edges.sort(axis=1)
 unique_edges,incidence=np.unique(edges,axis=0,return_counts=True)
 assert np.all(incidence==2), 'Relief backing is not closed'
 valence=np.bincount(unique_edges.ravel(),minlength=len(verts))
 stats.update(base_vertices=len(verts),base_faces=len(faces),closed_edge_incidence=True,maximum_vertex_valence=int(valence.max()),positive_volume_m3=vol,minimum_height_m=float((depth*heights).min()),maximum_height_m=float((depth*heights).max()),nominal_height_m=depth)
 return verts,faces,uvs,stats

def _parent_collection(bpy,parent):
 return parent.users_collection[0] if parent.users_collection else bpy.context.scene.collection

def _new_panel(bpy,parent,name,gray,rect,a,b,z0,z1,nx,nz,depth,image,source_texture):
 from mathutils import Vector
 started=time.perf_counter();print('V24_PANEL_START',name,flush=True)
 v,f,uv,stats=_panel_mesh_arrays(gray,rect,a,b,z0,z1,nx,nz,depth)
 print('V24_PANEL_ARRAYS_READY',name,round(time.perf_counter()-started,3),'s',flush=True)
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(v,[],f);me.update(calc_edges=True)
 ob=bpy.data.objects.new(name,me);_parent_collection(bpy,parent).objects.link(ob)
 # Coordinates are registered world LOCAL metres.  Preserve this even if an
 # integration caller has transformed the existing gate parent.
 ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted()
 me.materials.append(bpy.data.materials[MAT])
 layer=me.uv_layers.new(name='V24_Height_Atlas_UV');uv=np.asarray(uv,np.float32)
 li=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',li);layer.data.foreach_set('uv',uv[li].ravel())
 for p in me.polygons:p.use_smooth=True
 ob['V24_Relief_Method']='Grayscale atlas sampled into actual dense closed mesh, binomial surface smoothing, editable Multires subdivision. No manual brush sculpt is claimed.'
 ob['V24_Height_Image']=image.name;ob['V24_Atlas_UV_Rect']=list(rect);ob['V24_Height_Depth_m']=depth
 ob['V24_Geometry_Status']='REAL_VERTEX_DISPLACEMENT_BAKED_IN_BASE_MESH';ob['V24_Stone_Material_Retained']=MAT
 ob['V24_Sculpt_Editable']=True;ob['V24_Recommended_Edit_Mode']='SCULPT with Multires level 1; use the front surface vertex group as a mask source'
 group=ob.vertex_groups.new(name='V24_Sculpt_Front_Surface');group.add(list(range((nx+1)*(nz+1))),1.0,'REPLACE')
 ob['V24_Base_Mesh_Stats']=json.dumps(stats)
 # The packed image is registered on a disabled source modifier.  Reapplying
 # it would double the relief already baked into base vertices, so it starts
 # disabled and is explicitly labelled as an editable source reference.
 src=ob.modifiers.new('Baked height source (disabled to avoid double relief)','DISPLACE');src.texture=source_texture;src.texture_coords='UV';src.uv_layer=layer.name;src.strength=0;src.mid_level=0;src.show_viewport=False;src.show_render=False
 # This base is already the detailed relief. One additional level is enough
 # for direct sculpt editing and caps the twelve panels below 1.9M vertices.
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 sub=ob.modifiers.new('V24 editable stone sculpt level','MULTIRES')
 bpy.ops.object.multires_subdivide(modifier=sub.name,mode='SIMPLE')
 sub.levels=1;sub.sculpt_levels=1;sub.render_levels=1
 stats['build_seconds']=round(time.perf_counter()-started,3)
 print('V24_PANEL_MULTIRES_READY',name,stats['build_seconds'],'s',flush=True)
 return ob,stats

def _filter_mesh_faces(bpy,ob,predicate):
 import bmesh
 new=ob.data.copy();new.name=ob.data.name+'_V24_Retained';bm=bmesh.new();bm.from_mesh(new)
 drop=[f for f in bm.faces if not predicate(f)]
 bmesh.ops.delete(bm,geom=drop,context='FACES');bm.to_mesh(new);bm.free();new.update()
 old=ob.data;ob.data=new
 if not old.users:bpy.data.meshes.remove(old)

def apply_v24_relief(bpy,atlas_path,output_dir):
 """Operate on the already-loaded V23 model. Return a geometry QA dictionary."""
 atlas_path=Path(atlas_path);output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
 assert atlas_path.exists(),atlas_path
 parent=bpy.data.objects.get(NODE04);assert parent is not None,'Load the V23 model before applying relief'
 assert bpy.data.materials.get(MAT),'Original gray stone material is required'
 assert not any(o.name.startswith('V24_Gate_Reference_Relief_') for o in bpy.data.objects),'V24 relief already applied; reload V23 before rebuilding'
 image,gray=_read_gray(bpy,atlas_path);layout=_atlas_layout(atlas_path)
 texture=bpy.data.textures.new('V24_Packed_Reference_HeightAtlas',type='IMAGE');texture.image=image;texture.extension='EXTEND'
 old_selected=list(bpy.context.selected_objects);old_active=bpy.context.view_layer.objects.active
 proof={'method':'Actual closed mesh displacement from packed grayscale reference; surface smoothing and editable Multires; no material override','atlas':str(atlas_path),'atlas_sha256':hashlib.sha256(atlas_path.read_bytes()).hexdigest(),'atlas_layout':layout,'panels':[],'preserved_nodes':['SITE_V21_GATE_REFERENCE_LAYER_02','SITE_V21_GATE_REFERENCE_LAYER_03'],'manual_brush_sculpt_claimed':False}
 # Preserve original waist carving, which is separate in Z from both panels.
 old04=[o for o in parent.children if o.type=='MESH']
 for ob in old04:
  wm=ob.matrix_world.copy()
  _filter_mesh_faces(bpy,ob,lambda f:all(.60<(wm@v.co).z<.75 for v in f.verts))
  ob.name='V24_Gate_Waist_Carving_Retained';ob['V24_Status']='Original V23 carved waist preserved; panel carving replaced'
 for pi,(x0,x1) in enumerate([(4.933333333333334,5.457142857142857),(7.742857142857142,8.266666666666666)]):
  y0=-11.87;c=.09
  plans=[([x0+c,y0],[x1-c,y0],'front'),([x0,y0+c],[x0+c,y0],'left_bevel'),([x1-c,y0],[x1,y0+c],'right_bevel')]
  for a,b,face in plans:
   aa=np.array(a);bb=np.array(b);ln=np.linalg.norm(bb-aa);t=(bb-aa)/ln;margin=.010 if face=='front' else .008
   # Exactly matches the V23 rectangular backing within its stepped frame.
   start=aa+t*(margin+.021);end=bb-t*(margin+.021)
   for band,(lo,hi) in enumerate([(-.305,.575),(.778,2.312)]):
    key='bamboo' if face=='front' and band==1 else 'flowers' if face=='front' else 'vine'
    nx,nz=(128,640 if band==1 else 400) if face=='front' else (48,320);depth=.020 if face=='front' else .012
    name=f'V24_Gate_Reference_Relief_P{pi+1}_{face}_{band+1}'
    ob,stats=_new_panel(bpy,parent,name,gray,layout[key],start,end,lo+.022,hi-.022,nx,nz,depth,image,texture)
    proof['panels'].append(dict(name=name,motif=key,stone_material=MAT,**stats))
 # The header structural body and mouldings retain their original geometry.
 # Only polygons using the old carved-field stone material are replaced.
 header=bpy.data.objects.get(NODE05)
 if header:
  for ob in [o for o in header.children if o.type=='MESH']:
   carved=[i for i,m in enumerate(ob.data.materials) if m and m.name==MAT]
   _filter_mesh_faces(bpy,ob,lambda f:f.material_index not in carved)
  for j,cx in enumerate([5.78,6.60,7.42]):
   # Header local baseline is y=-11.812, 58 mm behind the pier face.
   # _panel uses front=-.001 so shift normal base plane by +1 mm.
   name=f'V24_Gate_Reference_Relief_Header_{j+1}'
   ob,stats=_new_panel(bpy,header,name,gray,layout['header'],[cx-.340,-11.811],[cx+.340,-11.811],2.488,2.646,160,48,.015,image,texture)
   proof['panels'].append(dict(name=name,motif='header',stone_material=MAT,**stats))
 bpy.context.view_layer.update();proof['base_vertices_total']=sum(p['base_vertices'] for p in proof['panels']);proof['panel_count']=len(proof['panels'])
 proof['evaluated_vertices_total']=sum(len(bpy.data.objects[p['name']].evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices) for p in proof['panels'])
 assert proof['evaluated_vertices_total']<=1900000,proof['evaluated_vertices_total']
 proof['status']='PASS_BLENDER_CLOSED_MESH_RELIEF_QA';proof['materials_replaced']=False
 parent['V24_Relief_QA']=json.dumps(proof,ensure_ascii=False)
 parent['GeometrySource']='V24 Blender actual mesh displacement from packed grayscale reference atlas; V23 waist geometry retained'
 if header:header['GeometrySource']='V23 structural header and frames retained; V24 carved fields replaced by Blender height-relief geometry'
 bpy.ops.object.select_all(action='DESELECT')
 for ob in old_selected:
  if ob.name in bpy.data.objects:ob.select_set(True)
 if old_active and old_active.name in bpy.data.objects:bpy.context.view_layer.objects.active=old_active
 (output_dir/'V24_Gate_Relief_Geometry_QA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
 print('V24 REAL RELIEF READY',proof['panel_count'],proof['base_vertices_total'],proof['evaluated_vertices_total'],flush=True)
 return proof
