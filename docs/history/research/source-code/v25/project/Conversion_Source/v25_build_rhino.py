# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from v25_rhino_common import *
import json,hashlib,time,math,uuid,gc
from System.Drawing import Color
T=time.monotonic();O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25'
def js(n):return json.loads((D/n).read_text('utf8'))
idx=js('Export_Index.json');mats={x['key']:x for x in js('Material_Index.json')};textures=js('Texture_Index.json');cameras=js('Camera_Index.json');hinges=js('Door_Hinges.json');exp=js('Export_Report.json')
used={x['material'] for x in idx};texture_paths=sorted({mats[k][s] for k in used for s in ['base_texture','bump_texture'] if mats[k].get(s)})
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def srgb(v):return 12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055
def color(vals):return Color.FromArgb(255,*[max(0,min(255,round(srgb(max(0,float(v)))*255))) for v in vals[:3]])
report={'source_sha256':exp['source_sha256'],'native_kernel':str(Rhino.RhinoApp.Version),'units':'metres','mesh_parts':len(idx),'source_objects':len({x['source_object'] for x in idx}),'triangles':sum(x['triangles'] for x in idx),'materials':len(used),'embedded_textures':len(texture_paths),'coordinate':'LOCAL metres, Z up','pose_frame':40,'geometry_hashes_before_write':0,'invalid_meshes':[],'files':[]}
core=start()
try:
 b=bridge();f=Rhino.FileIO.File3dm();f.Settings.ModelUnitSystem=Rhino.UnitSystem.Meters;f.Settings.ModelAbsoluteTolerance=.001;f.Settings.ModelAngleToleranceDegrees=1.;f.ApplicationDetails='Rebuild_V25; Rhino 8 native mesh conversion of verified V24.37, original photo bytes and UV retained.'
 mi={}
 for k in sorted(used):
  s=mats[k];m=Rhino.DocObjects.Material();m.Name=s['name'];m.ToPhysicallyBased();pb=m.PhysicallyBased
  rgb=[srgb(max(0,float(v))) for v in s['base_color_linear'][:3]]
  pb.BaseColor=Rhino.Display.Color4f(*rgb,1.);pb.Metallic=float(s['metallic']);pb.Roughness=float(s['roughness']);pb.Specular=float(s['specular']);pb.ReflectiveIOR=float(s['ior']);pb.OpacityIOR=float(s['ior']);pb.Alpha=float(s['alpha']);pb.Opacity=max(0.,1.-float(s['transmission']));pb.SynchronizeLegacyMaterial()
  for slot,tt in [('base_texture',Rhino.DocObjects.TextureType.Bitmap),('bump_texture',Rhino.DocObjects.TextureType.Bump)]:
   if s.get(slot):
    tx=Rhino.DocObjects.Texture();tx.FileName=s[slot];tx.Enabled=True
    tx.TextureType=tt
    if s.get('base_wrap')=='EXTEND':tx.WrapU=Rhino.DocObjects.TextureUvwWrapping.Clamp;tx.WrapV=Rhino.DocObjects.TextureUvwWrapping.Clamp
    assert m.SetTexture(tx,tt),('set texture failed',k,slot)
  m.SetUserString('V25_Source_Material',s.get('source_material',''));m.SetUserString('V25_Conversion',s['method'])
  f.Materials.Add(m);mi[k]=f.Materials.Count-1;m.Dispose()
 for p in texture_paths:f.EmbeddedFiles.Add(p)
 print('MATERIALS_TEXTURES_READY',len(mi),len(texture_paths),flush=True)
 layers={};groups={}
 def layer(path):
  key='::'.join(path)
  if key not in layers:
   parent=layer(path[:-1]) if len(path)>1 else None
   l=Rhino.DocObjects.Layer();l.Name=path[-1];l.Color=Color.FromArgb(135,151,155) if path[0].startswith('90') else Color.FromArgb(220,215,202)
   if parent is not None:l.ParentLayerId=f.Layers[parent].Id
   f.Layers.Add(l);layers[key]=f.Layers.Count-1;l.Dispose()
  return layers[key]
 def group(name):
  if name not in groups:
   gi=f.AllGroups.AddGroup();assert gi>=0;g=f.AllGroups.FindIndex(gi);g.Name=name;groups[name]=gi
  return groups[name]
 for i,x in enumerate(idx):
  mesh=call(b,'Read',x['file']);h=call(b,'Hash',mesh);assert h==x['sha256'],('geometry changed',i)
  report['geometry_hashes_before_write']+=1
  if not mesh.IsValid:report['invalid_meshes'].append({'index':i,'name':x['name'],'log':mesh.IsValidWithLog()})
  a=Rhino.DocObjects.ObjectAttributes();a.Name=x['name'];a.LayerIndex=layer(x['layer_path']);a.MaterialIndex=mi[x['material']];a.MaterialSource=Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject;a.ObjectId=System.Guid(str(uuid.uuid5(uuid.NAMESPACE_URL,'Rebuild_V25/'+str(i)+'/'+x['name'])))
  a.ObjectColor=color(mats[x['material']]['base_color_linear'])
  a.SetUserString('V25_PartIndex',str(i));a.SetUserString('V25_SourceObject',x['source_object']);a.SetUserString('V25_SourceParent',x['source_parent'] or '');a.SetUserString('V25_BinaryGeometrySHA256',h);a.SetUserString('V25_MaterialKey',x['material']);a.SetUserString('V25_GeometryMethod',x['geometry_method']);a.SetUserString('V25_SourceProperties',json.dumps(x['source_properties'],ensure_ascii=False));a.SetUserString('V25_Coordinates','LOCAL metres, Z up');a.SetUserString('V25_Groups',json.dumps(x['group_path'],ensure_ascii=False))
  for g in x['group_path']:a.AddToGroup(group(g))
  oid=f.Objects.AddMesh(mesh,a);assert oid!=System.Guid.Empty
  mesh.Dispose();a.Dispose()
  if i%200==0:print('MESH',i,len(idx),round(time.monotonic()-T,1),flush=True)
 assert not report['invalid_meshes'],report['invalid_meshes']
 aliases={'V24_37_02_House_And_PTJIA6':'01_建筑及外景','V24_37_01_Expanded_Context_Overview':'02_完整外景范围','V24_35_01_Kitchen_East':'03_院落附属建筑','V24_35_02_Kitchen_East_Close':'04_青砖墙细部','V24_37_04_PTJIA6_Road_Eye':'05_外景道路','V24_37_05_PTJIA6_Field_Context':'06_田地外景'}
 def view(c,transform_camera=None):
  v=Rhino.DocObjects.ViewportInfo();loc=Rhino.Geometry.Point3d(*c['location']);dire=Rhino.Geometry.Vector3d(*c['direction']);dire.Unitize();v.SetCameraLocation(loc);v.SetCameraDirection(dire);v.SetCameraUp(Rhino.Geometry.Vector3d(*c['up']));v.TargetPoint=loc+dire*30
  if c['orthographic']:
   half=c['ortho_scale']/2;v.IsParallelProjection=True;v.SetFrustum(-half*1.6,half*1.6,-half,half,.01,max(5000,c['clip_end']))
  else:
   near=.05;half=.018/c['lens_mm']*near*1000;v.IsPerspectiveProjection=True;v.SetFrustum(-half,half,-half/1.6,half/1.6,near,max(5000,c['clip_end']))
  v.SetScreenPort(0,1600,0,1000,0,1000)
  if transform_camera is not None:assert v.TransformCamera(transform_camera)
  assert v.IsValid,c['name'];rv=Rhino.Display.RhinoViewport();assert rv.SetViewProjection(v,True);vi=Rhino.DocObjects.ViewInfo(rv);vi.Name=aliases.get(c['name'],c['name']);assert vi.Viewport.CameraLocation.DistanceTo(v.CameraLocation)<1e-8;return vi
 for c in cameras:f.NamedViews.Add(view(c))
 maincam=next(c for c in cameras if c['name']=='V24_37_02_House_And_PTJIA6');f.Views.Add(view(maincam))
 f.Strings.SetString('Rebuild_V25','Source_SHA256',exp['source_sha256']);f.Strings.SetString('Rebuild_V25','Geometry','Independent editable meshes. No NURBS reconstruction or decimation.');f.Strings.SetString('Rebuild_V25','Pose','Static source animation frame 40. Blender companion retains interaction and safe roam.');f.Strings.SetString('Rebuild_V25','Door_Hinges_LOCAL',json.dumps(hinges,ensure_ascii=False));f.Strings.SetString('Rebuild_V25','Coordinates','LOCAL metres, Z up')
 p=O/'Rhino/Architecture_Complete_V25.3dm';print('WRITE_LOCAL',len(list(f.Objects)),flush=True);temp=p.with_name('_Building_LOCAL.3dm');assert f.Write(str(temp),8);temp.replace(p);report['files'].append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 print('LOCAL_SAVED',p.stat().st_size,flush=True)
 transform=Rhino.Geometry.Transform.Identity;ang=math.radians(19.65);transform.M00=math.cos(ang);transform.M01=-math.sin(ang);transform.M10=math.sin(ang);transform.M11=math.cos(ang);transform.M03=-3.45191261;transform.M13=-3.90043098;transform.M23=TAO_PRIVATE_SITE_002
 for ob in list(f.Objects):
  mesh=ob.Geometry.DuplicateMesh();a=ob.Attributes.Duplicate();oid=a.ObjectId;assert mesh.Transform(transform);a.SetUserString('V25_Coordinates','Original ENU project alignment, metres. Vertical offset +1303.75 m. Not independent survey control.');assert f.Objects.Delete(oid);assert f.Objects.AddMesh(mesh,a)==oid;mesh.Dispose();a.Dispose()
 f.NamedViews.Clear();f.Views.Clear()
 for c in cameras:f.NamedViews.Add(view(c,transform))
 f.Views.Add(view(maincam,transform))
 f.Strings.SetString('Rebuild_V25','Coordinates','ENU:TAO_PRIVATE_SITE_003,98.68275. Original project transform; not independently surveyed.');f.Strings.SetString('Rebuild_V25','LOCAL_to_ENU',json.dumps([[transform[i,j] for j in range(4)] for i in range(4)]));f.Strings.SetString('Rebuild_V25','Door_Hinges_Note','Door_Hinges_LOCAL remains original LOCAL; use LOCAL_to_ENU to transform pivots.')
 p=O/'Rhino/Architecture_Complete_V25_ALIGNED_ENU.3dm';print('WRITE_ENU',flush=True);temp=p.with_name('_Building_ENU.3dm');assert f.Write(str(temp),8);temp.replace(p);report['files'].append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 report['layers']=layers;report['groups']=len(groups);report['named_views']=len(cameras);report['seconds']=time.monotonic()-T;report['source_unchanged']=sha(exp['source'])==exp['source_sha256'];assert report['source_unchanged']
 (O/'Reports/V25_Rhino_Build_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');(D/'Rhino_Build_Report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('V25_NATIVE_RHINO_BUILD_OK',report['seconds'],flush=True)
 f.Dispose()
finally:core.Dispose()
