from pathlib import Path
import bpy,sys,json,hashlib,struct,time,math,shutil,collections,numpy as np
from mathutils import Matrix
W=Path(__file__).parent;D=W/'v25';O=Path('E:/jz/JIA/Rebuild_V25');R=O/'Reports';T=O/'Textures';G=D/'Geometry';SOURCE=Path('E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend')
for p in [D,R,T,G,O/'Rhino',O/'Blender',O/'Roam',O/'Source_Metadata']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();start=time.perf_counter();probe=json.loads((D/'Blender_Probe.json').read_text());assert sha(SOURCE)==probe['source_sha256'];objects=[bpy.data.objects[r['name']]for r in probe['rows']];dep=bpy.context.evaluated_depsgraph_get();source_hash=sha(SOURCE)
# Keep the verified safe-tour implementation in the V25 companion before any
# temporary texture baking. This never changes the V24.37 source.
sc['Version']='V25_RHINO_EDITABLE_EXPORT_AND_SAFE_TOUR_COMPANION';sc['Rhino_Export_Description']='Visible evaluated geometry at frame 40; metres; original photo UV and editable material groups';comp=O/'Blender/Architecture_Complete_V25.blend'
if not comp.exists():bpy.ops.wm.save_as_mainfile(filepath=str(comp),compress=True)
for fn in ['start_roam.py','roam_controller.py','roam_physics.py','measure_tools.py']:shutil.copy2(SOURCE.parents[1]/'Roam'/fn,O/'Roam'/fn)
for fn in ['启动漫游.cmd','打开修正版模型.cmd']:(O/fn).write_text((SOURCE.parents[1]/fn).read_text('utf8').replace('V24_37','V25'),encoding='utf8')
textures={};image_cache={};materials={};exports=[];bakes=[];excluded=[];errors=[]
def extract(im):
 if im.name in image_cache:return image_cache[im.name]
 if im.packed_file:
  data=bytes(im.packed_file.data);h=hashlib.sha256(data).hexdigest();ext='.jpg'if data[:3]==b'\xff\xd8\xff'else'.png'if data[:8]==b'\x89PNG\r\n\x1a\n'else'.'+im.file_format.lower();path=T/('IMG_'+h[:24]+ext)
  if not path.exists():path.write_bytes(data)
  exact=True
 else:
  h=hashlib.sha256(im.name.encode()).hexdigest();path=T/('IMG_'+h[:24]+'.png');im.save(filepath=str(path));h=sha(path);exact=False
 key=sha(path);record={'file':str(path),'sha256':key,'source_image':im.name,'original_packed_bytes':exact,'size':list(im.size),'colorspace':im.colorspace_settings.name};textures[key]=record;image_cache[im.name]=record;return record
def inp(bs,n,default):
 return float(bs.inputs[n].default_value)if bs and n in bs.inputs and not bs.inputs[n].is_linked else default
def spec(m,key=None):
 key=key or m.name
 if key in materials:return materials[key]
 ns=m.node_tree.nodes if m.use_nodes else[];bs=next((n for n in ns if n.type=='BSDF_PRINCIPLED'),None);col=list(bs.inputs['Base Color'].default_value)if bs else list(m.diffuse_color)
 s={'key':key,'name':key,'source_material':m.name,'base_color_linear':col,'metallic':inp(bs,'Metallic',m.metallic),'roughness':inp(bs,'Roughness',m.roughness),'alpha':inp(bs,'Alpha',col[3]),'transmission':inp(bs,'Transmission Weight',0.),'ior':inp(bs,'IOR',1.5),'specular':inp(bs,'Specular IOR Level',.5),'base_texture':None,'bump_texture':None,'base_wrap':'REPEAT','uv_map':None,'method':'PBR constants'}
 if bs and bs.inputs['Base Color'].is_linked:
  node=bs.inputs['Base Color'].links[0].from_node
  if node.type=='TEX_IMAGE'and node.image:
   s['base_texture']=extract(node.image)['file'];s['base_color_linear']=[1.,1.,1.,1.];s['base_wrap']=node.extension;s['method']='Original packed image and UV'
   if node.inputs['Vector'].is_linked and node.inputs['Vector'].links[0].from_node.type=='UVMAP':s['uv_map']=node.inputs['Vector'].links[0].from_node.uv_map
 if bs and bs.inputs['Normal'].is_linked:
  bump=bs.inputs['Normal'].links[0].from_node
  if bump.type=='BUMP'and bump.inputs['Height'].is_linked:
   height=bump.inputs['Height'].links[0].from_node
   if height.type=='TEX_IMAGE'and height.image:s['bump_texture']=extract(height.image)['file'];s['bump_distance_m']=inp(bump,'Distance',.001);s['bump_strength']=inp(bump,'Strength',.18)
 materials[key]=s;return s
for name in sorted({m.name for o in objects for m in o.data.materials if m}):spec(bpy.data.materials[name])
# Bake only base-colour expressions. Baking emission excludes all lighting and
# reproduces diffuse, noisy wood, stone and mixed masonry albedo faithfully.
bake_sc=bpy.data.scenes.new('V25_TEMP_ALBEDO_BAKE');bake_sc.render.engine='CYCLES';bake_sc.cycles.samples=1;bake_sc.cycles.use_denoising=False;bake_sc.render.bake.margin=8;bake_sc.view_settings.view_transform='Standard'
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 bake_sc.cycles.device='GPU'
except Exception:pass
def clone_for_bake(mat,original_uv,target):
 m=mat.copy();ns=m.node_tree.nodes;links=m.node_tree.links
 # Make source UV explicit before activating the new, non-overlapping atlas.
 if original_uv:
  uv=ns.new('ShaderNodeUVMap');uv.uv_map=original_uv
  for n in list(ns):
   if n.type=='TEX_IMAGE'and n!=uv and not n.inputs['Vector'].is_linked:links.new(uv.outputs['UV'],n.inputs['Vector'])
   if n.type=='TEX_COORD':
    for link in list(n.outputs['UV'].links):links.new(uv.outputs['UV'],link.to_socket)
 def colour(socket):
  node=socket.node
  if node.type=='BSDF_PRINCIPLED':
   s=node.inputs['Base Color']
   if s.is_linked:return s.links[0].from_socket
   rgb=ns.new('ShaderNodeRGB');rgb.outputs[0].default_value=s.default_value;return rgb.outputs[0]
  if node.type=='MIX_SHADER':
   mix=ns.new('ShaderNodeMixRGB');mix.blend_type='MIX';fac=node.inputs[0]
   if fac.is_linked:links.new(fac.links[0].from_socket,mix.inputs[0])
   else:mix.inputs[0].default_value=fac.default_value
   for i in [1,2]:links.new(colour(node.inputs[i].links[0].from_socket),mix.inputs[i])
   return mix.outputs[0]
  raise RuntimeError('Unsupported surface for albedo export: '+node.type)
 out=next(n for n in ns if n.type=='OUTPUT_MATERIAL'and n.is_active_output);c=colour(out.inputs['Surface'].links[0].from_socket);em=ns.new('ShaderNodeEmission');links.new(c,em.inputs['Color']);links.new(em.outputs[0],out.inputs['Surface']);tx=ns.new('ShaderNodeTexImage');tx.image=target;ns.active=tx;return m
def bake_mesh(o,me,tag,res,keep_uv=False):
 original_uv=me.uv_layers.active.name if me.uv_layers.active else None;target=bpy.data.images.new('V25_BAKE_'+tag,width=res,height=res,alpha=False);target.colorspace_settings.name='sRGB';temp=bpy.data.objects.new('V25_TEMP_'+tag,me);bake_sc.collection.objects.link(temp);temp.matrix_world=o.matrix_world.copy();copies=[]
 originals=list(me.materials);face_materials=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('material_index',face_materials);me.materials.clear()
 for mat in originals:
  if mat is None:mat=bpy.data.materials.new('V25_Default_Gray');mat.use_nodes=True
  cp=clone_for_bake(mat,original_uv,target);copies.append(cp);me.materials.append(cp)
 # Blender clears polygon material indices when clearing material slots.
 # Restore them before baking so every source face uses its actual shader.
 me.polygons.foreach_set('material_index',face_materials);me.update()
 prior_scene=bpy.context.window.scene if bpy.context.window else None
 if bpy.context.window:bpy.context.window.scene=bake_sc
 with bpy.context.temp_override(scene=bake_sc,view_layer=bake_sc.view_layers[0],object=temp,active_object=temp,selected_objects=[temp],selected_editable_objects=[temp]):
  temp.select_set(True,view_layer=bake_sc.view_layers[0]);bake_sc.view_layers[0].objects.active=temp
  if not keep_uv:
   atlas=me.uv_layers.new(name='V25_Rhino_Baked_Atlas');me.uv_layers.active=atlas
   for u in me.uv_layers:u.active_render=(u==atlas)
   bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=2/res,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
  bake_sc.render.bake.use_clear=True;print('BAKE_CONTEXT',tag,bpy.ops.object.bake.poll(),bpy.context.scene.name,bpy.context.active_object.name,flush=True);bpy.ops.object.bake(type='EMIT')
 if bpy.context.window and prior_scene:bpy.context.window.scene=prior_scene
 path=T/('BAKED_'+tag+'.png');target.filepath_raw=str(path);target.file_format='PNG';target.save();record={'file':str(path),'sha256':sha(path),'source_image':None,'original_packed_bytes':False,'size':[res,res],'colorspace':'sRGB','method':'Source colour graph baked as unlit emission'};textures[record['sha256']]=record
 me.materials.clear()
 for mat in originals:me.materials.append(mat)
 me.polygons.foreach_set('material_index',face_materials);me.update()
 check_materials=np.empty(len(me.polygons),np.int32);me.polygons.foreach_get('material_index',check_materials);assert np.array_equal(face_materials,check_materials),'Material face partition changed in '+o.name
 for mat in copies:bpy.data.materials.remove(mat)
 bpy.data.objects.remove(temp,do_unlink=True);bpy.data.images.remove(target);return path
# The roof colour expression is a purely UV-based grayscale adjustment. One
# periodic tile reproduces it for all roofs without repacking their original UV.
roof='M_V24_20_Unified_Weathered_Gray_Clay';roofmat=bpy.data.materials.get(roof)
if roofmat:
 plane=bpy.data.meshes.new('V25_Roof_Material_Plane');plane.from_pydata([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[],[(0,1,2,3)]);plane.materials.append(roofmat);uv=plane.uv_layers.new(name='Source_UV');uv.data.foreach_set('uv',np.array([[0,0],[1,0],[1,1],[0,1]],np.float32).ravel());holder=bpy.data.objects.new('V25_ROOF_BAKE_HOLDER',plane);path=bake_mesh(holder,plane,'ROOF_UV_GRAY_CLAY',2048,True);materials[roof].update(base_texture=str(path),base_color_linear=[1.,1.,1.,1.],base_wrap='REPEAT',method='Unlit baked original roof colour expression; original UV retained');bpy.data.objects.remove(holder);bpy.data.meshes.remove(plane)
complex_names=set(probe['complex_materials'])-{roof};source_summary=[];skipped_zero=0;photo_faces=0
def lineage(o):
 arr=[];p=o
 while p:arr.append(p.name);p=p.parent
 return arr
def classify(o):
 name=o.name.upper()
 if 'ORIGINAL_EXTERIOR_'in name:return ['90_实景外景','01_原有实景']
 if o.name.startswith('V24_34_MB7_'):return ['90_实景外景','02_MB7外景']
 if o.name.startswith('V24_36_PTJIA6_'):return ['90_实景外景','03_PTJIA6外景']
 if any('ROAM_PERSON'in n.upper()for n in lineage(o)):return ['80_人物参考','165cm人物']
 if any(x in name for x in ['STAIR','RAILING','HANDRAIL']):return ['30_楼梯扶手']
 if any(x in name for x in ['DOOR','WINDOW','GLAZ','GLASS','TRANSOM']):return ['20_门窗构件']
 if any(x in name for x in ['ROOF','TILE','EAVE','RIDGE','SOFFIT','CANOPY']):return ['10_屋面瓦顶']
 if any(x in name for x in ['SITE_','COURT','KITCHEN','STORAGE','PAVILION','SCREENWALL','PERIMETER','GATE','PIPE','FLUE','EXHAUST']):return ['40_院落附属建筑']
 return ['01_主体建筑']
for j,o in enumerate(objects):
 ev=o.evaluated_get(dep);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dep);me.calc_loop_triangles();mats=list(me.materials);baked=any(m and m.name in complex_names for m in mats);keybase=hashlib.sha256(o.name.encode()).hexdigest()[:16];oldv=np.empty(len(me.vertices)*3,np.float64);me.vertices.foreach_get('co',oldv);oldv=oldv.reshape(-1,3);M=np.array(o.matrix_world);v=oldv@M[:3,:3].T+M[:3,3];tri=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',tri);tri=tri.reshape(-1,3);t=v[tri];area=float(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).sum()/2);baked_path=None
 if baked:
  res=4096 if area>300 else 2048 if area>50 else 1024 if area>8 else 512;baked_path=bake_mesh(o,me,keybase,res);bakes.append({'source_object':o.name,'area_m2':area,'resolution':res,'file':str(baked_path)});print('BAKE_DONE',j,o.name,res,'seconds',time.perf_counter()-start,flush=True)
 me.calc_loop_triangles();f=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3);loops=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('loops',loops);loops=loops.reshape(-1,3);mi=np.array([t.material_index for t in me.loop_triangles],np.int32);no=np.empty(len(me.corner_normals)*3,np.float32);me.corner_normals.foreach_get('vector',no);no=no.reshape(-1,3);N=np.linalg.inv(M[:3,:3]).T;no=no@N.T;no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-20);changed_v=np.empty(len(me.vertices)*3,np.float64);me.vertices.foreach_get('co',changed_v);assert np.array_equal(changed_v,oldv.ravel()),o.name+' geometry changed during UV export'
 source_summary.append({'name':o.name,'vertices':len(v),'triangles':len(f),'area_m2':area,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'source_matrix':M.tolist(),'source_parent':o.parent.name if o.parent else None,'lineage':lineage(o),'source_materials':[m.name if m else None for m in mats],'baked_base_colour':baked})
 for mid in np.unique(mi):
  mat=mats[int(mid)]if mid<len(mats)and mats[int(mid)]else None
  if mat is None:mat=bpy.data.materials.get('V25_Default_Gray')or bpy.data.materials.new('V25_Default_Gray');mat.use_nodes=True
  s=spec(mat);key=s['key']
  if baked_path:
   key=o.name+'::'+mat.name;sp={**s,'key':key,'name':key,'base_texture':str(baked_path),'bump_texture':None,'base_color_linear':[1.,1.,1.,1.],'base_wrap':'EXTEND','uv_map':me.uv_layers.active.name,'method':'Unlit baked source colour; new non-overlapping UV atlas'};materials[key]=sp;s=sp
  uv=me.uv_layers.get(s['uv_map'])if s['uv_map']else me.uv_layers.active;uu=np.zeros((len(me.loops),2),np.float32)
  if uv:uv.data.foreach_get('uv',uu.ravel())
  sel=mi==mid;ff=f[sel];ll=loops[sel];tt=v[ff];valid=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)>1e-11;skipped_zero+=int((~valid).sum());ff=ff[valid];ll=ll[valid]
  if not len(ff):continue
  dtype=np.dtype([('vi','<i4'),('uv','<f4',(2,)),('normal','<f4',(3,))]);corners=np.empty(ff.size,dtype=dtype);corners['vi']=ff.ravel();corners['uv']=uu[ll.ravel()];corners['normal']=no[ll.ravel()].astype(np.float32);unique,idx,inv=np.unique(corners,return_index=True,return_inverse=True);vv=v[unique['vi']];uvs=unique['uv'];normals=unique['normal'];faces=inv.reshape(-1,3).astype('<i4')
  if np.linalg.det(M[:3,:3])<0:faces=faces[:,::-1].copy()
  fn=G/(str(len(exports)).zfill(5)+'.r25mesh')
  with fn.open('wb')as out:
   out.write(b'R25M');out.write(struct.pack('<III',1,len(vv),len(faces)));vv.astype('<f8').tofile(out);normals.astype('<f4').tofile(out);uvs.astype('<f4').tofile(out);faces.tofile(out)
  exports.append({'source_object':o.name,'name':o.name if len(np.unique(mi))==1 else o.name+'__MAT_'+str(mid),'file':str(fn),'sha256':sha(fn),'material':key,'vertices':len(vv),'triangles':len(faces),'area_m2':float(np.linalg.norm(np.cross(tt[valid,1]-tt[valid,0],tt[valid,2]-tt[valid,0]),axis=1).sum()/2),'bounds':[vv.min(0).tolist(),vv.max(0).tolist()],'layer_path':classify(o),'group_path':lineage(o),'source_parent':o.parent.name if o.parent else None,'source_properties':{k:str(o[k])for k in o.keys()if k!='_RNA_UI'},'geometry_method':'Evaluated source triangles; only UV/normal seam vertex duplication; no decimation'})
  if o.name.startswith(('V24_34_MB7_','V24_36_PTJIA6_'))or'ORIGINAL_EXTERIOR_'in o.name:photo_faces+=len(faces)
 bpy.data.meshes.remove(me)
 if j%100==0:print('EXPORTED_VISIBLE',j,len(objects),'parts',len(exports),'seconds',time.perf_counter()-start,flush=True)
cams=[]
for o in sc.objects:
 if o.type!='CAMERA':continue
 mm=np.array(o.matrix_world);cams.append({'name':o.name,'location':mm[:3,3].tolist(),'direction':(-mm[:3,2]).tolist(),'up':mm[:3,1].tolist(),'lens_mm':o.data.lens,'orthographic':o.data.type=='ORTHO','ortho_scale':o.data.ortho_scale,'clip_end':o.data.clip_end})
hinges=[]
for o in sc.objects:
 if o.get('UE_Interaction')in ['HINGED_INWARD','SLIDING']:hinges.append({'name':o.name,'operation':o['UE_Interaction'],'location':list(o.matrix_world.translation),'properties':{k:str(o[k])for k in o.keys()if k!='_RNA_UI'}})
write=lambda n,x:(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');write('Export_Index.json',exports);write('Material_Index.json',list(materials.values()));write('Texture_Index.json',list(textures.values()));write('Camera_Index.json',cams);write('Door_Hinges.json',hinges);write('Source_Visible_Geometry.json',source_summary);report={'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':sha(SOURCE)==source_hash,'companion':str(comp),'companion_sha256':sha(comp),'source_visible_objects':len(objects),'exported_material_parts':len(exports),'source_triangles':sum(r['triangles']for r in source_summary),'export_triangles':sum(r['triangles']for r in exports),'photo_triangles':photo_faces,'degenerate_zero_area_faces_omitted':skipped_zero,'materials':len(materials),'textures':len(textures),'baked_objects':bakes,'coordinate':'Current model LOCAL, metres, Z up; exact ENU transform supplied separately','frame':40,'seconds':time.perf_counter()-start};write('Export_Report.json',report);(R/'V25_Blender_Export_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('EXPORT_V25_DONE',{k:v for k,v in report.items()if k!='baked_objects'},flush=True)
