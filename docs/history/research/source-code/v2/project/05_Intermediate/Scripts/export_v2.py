import sys,os,json,math,collections,csv,ctypes as C
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
sys.path.insert(0,str(Path(__file__).parent/"geomlibs"))
import numpy as np,rhino3dm as rh
import v2_geometry
import skp_api as su
OUT=Path(r'E:\jz\JIA\Rebuild_V2');SCENE=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));MATS=SCENE['materials']
LAYERS=['00_REFERENCE','01_GRID','02_LEVEL','10_WALL_EXT','11_WALL_INT','20_COLUMN','21_BEAM','22_SLAB','30_DOOR','31_WINDOW','40_STAIR','41_RAILING','50_ROOF','51_CANOPY','60_SITE','70_EQUIPMENT','80_CONTEXT','90_UNCERTAIN','99_HELPER']
TAGS={'00_REFERENCE':'00_Reference','01_GRID':'01_Grid','02_LEVEL':'02_Level','10_WALL_EXT':'10_Walls','11_WALL_INT':'11_Walls_Interior','20_COLUMN':'20_Structure','21_BEAM':'21_Beams','22_SLAB':'22_Slabs','30_DOOR':'30_Doors','31_WINDOW':'31_Windows','40_STAIR':'40_Stairs','41_RAILING':'41_Railings','50_ROOF':'50_Roof','51_CANOPY':'51_Canopy','60_SITE':'60_Site','70_EQUIPMENT':'70_Equipment','80_CONTEXT':'80_Context','90_UNCERTAIN':'90_Uncertain','99_HELPER':'99_Helper'}
def triangulate(poly):
 p=np.array(poly,float);normal=np.cross(p[1]-p[0],p[2]-p[0]);drop=np.argmax(abs(normal));q=np.delete(p,drop,axis=1);area=sum(np.cross(q[(i+1)%len(q)]-q[i],q[(i+2)%len(q)]-q[(i+1)%len(q)]) for i in range(len(q)))
 signed=sum(q[i,0]*q[(i+1)%len(q),1]-q[(i+1)%len(q),0]*q[i,1] for i in range(len(q)));sgn=1 if signed>0 else -1
 ids=list(range(len(q)));tris=[];guard=0
 def inside(a,b,c,x):
  return all(sgn*np.cross(v-u,x-u)>=-1e-10 for u,v in [(a,b),(b,c),(c,a)])
 while len(ids)>3 and guard<len(q)**2:
  guard+=1;found=False
  for kk,j in enumerate(ids):
   i=ids[kk-1];k=ids[(kk+1)%len(ids)]
   if sgn*np.cross(q[j]-q[i],q[k]-q[j])<=1e-10:continue
   if any(inside(q[i],q[j],q[k],q[m]) for m in ids if m not in (i,j,k)):continue
   tris.append([i,j,k]);ids.pop(kk);found=True;break
  if not found:break
 if len(ids)==3:tris.append(ids)
 if len(tris)!=len(poly)-2:raise ValueError('Ear clipping failed '+str(poly))
 return tris
def solid_data(g):
 typ=g['type']
 if typ in v2_geometry.TYPES:return v2_geometry.data(g)
 if typ=='box':
  x,y,z=g['origin'];w,d,h=g['size'];p=np.array([[x,y,z],[x+w,y,z],[x+w,y+d,z],[x,y+d,z]]);vec=np.array([0,0,h])
 elif typ=='cylinder':
  x,y,z=g['origin'];r=g['radius'];p=np.array([[x+r*math.cos(a),y+r*math.sin(a),z] for a in np.linspace(0,2*math.pi,g['segments'],endpoint=False)]);vec=np.array([0,0,g['height']])
 elif typ=='prism':p=np.array(g['profile'],float);vec=np.array(g['vector'],float)
 elif typ=='mesh':return np.array(g['vertices'],float),g['faces'],None,None
 elif typ=='surface_polygon':
  p=np.array(g['points'],float);xy=np.column_stack([p[:,:2],np.zeros(len(p))]);return p,triangulate(xy),None,None
 else:return None,None,None,None
 # The Newell normal handles concave profiles and stairs.
 nn=np.sum(np.cross(p,np.roll(p,-1,axis=0)),axis=0)
 if np.dot(nn,vec)<0:p=p[::-1]
 N=len(p);v=np.vstack([p,p+vec]);f=[list(range(N-1,-1,-1)),list(range(N,2*N))]+[[i,(i+1)%N,(i+1)%N+N,i+N] for i in range(N)]
 return v,f,p,vec
def native(g):
 if g['type'] in v2_geometry.TYPES:return v2_geometry.native(g)
 if g['type']=='nurbs_patch':
  surf=rh.NurbsSurface.Create(3,False,2,2,2,2)
  for ij,p in zip([(0,0),(1,0),(1,1),(0,1)],g['points']):surf.Points[ij]=rh.Point4d(*p,1)
  surf.KnotsU.CreateUniformKnots(1);surf.KnotsV.CreateUniformKnots(1);return surf
 typ=g['type'];v,f,p,vec=solid_data(g)
 if typ=='line':return rh.PolylineCurve([rh.Point3d(*x) for x in g['points']])
 if typ=='mesh':
  m=rh.Mesh()
  for pt in v:m.Vertices.Add(*pt)
  for face in f:m.Faces.AddFace(*face)
  m.Normals.ComputeNormals();m.Compact();return rh.Brep.CreateFromMesh(m,True)
 if typ=='surface_polygon':
  # Each scene polygon is split into planar triangles by callers.
  if len(v)!=3:raise ValueError('native site polygon must be triangulated')
  plane=rh.Plane(rh.Point3d(*v[0]),rh.Point3d(*v[1]),rh.Point3d(*v[2]));curve=rh.PolylineCurve([rh.Point3d(*a) for a in list(v)+[v[0]]]);return rh.Brep.CreateTrimmedPlane(plane,curve)
 if typ=='cylinder':
  return rh.Cylinder(rh.Circle(rh.Point3d(*g['origin']),g['radius']),g['height']).ToBrep(True,True)
 n=vec/np.linalg.norm(vec);u=p[1]-p[0];u/=np.linalg.norm(u);vv=np.cross(n,u)
 if max(abs((p-p[0])@n))<1e-7:
  coords=np.column_stack([(p-p[0])@u,(p-p[0])@vv,np.zeros(len(p))]);curve=rh.PolylineCurve([rh.Point3d(*a) for a in list(coords)+[coords[0]]]);ex=rh.Extrusion.Create(curve,float(np.linalg.norm(vec)),True)
  pl=rh.Plane(rh.Point3d(*p[0]),rh.Vector3d(*u),rh.Vector3d(*vv));ex.Transform(rh.Transform.PlaneToPlane(rh.Plane.WorldXY(),pl));return ex
 # Sheared clean analytic prism used only for approximate sloping courtyard wall.
 m=rh.Mesh()
 for a in v:m.Vertices.Add(*a)
 for face in f:
  for t in triangulate(v[face]):m.Faces.AddFace(*[face[i] for i in t])
 return rh.Brep.CreateFromMesh(m,True)
def world_part(part,e):
 v,f,p,vec=solid_data(part['geometry']);origin=e.get('origin',[0,0,0]);angle=e.get('angle',0);c=math.cos(angle);s=math.sin(angle);R=np.array([[c,-s,0],[s,c,0],[0,0,1]])
 if v is not None:v=v@R.T+np.array(origin)
 return v,f
def rh_transform(e):
 t=rh.Transform.Rotation(e.get('angle',0),rh.Vector3d(0,0,1),rh.Point3d(0,0,0));return rh.Transform.Multiply(rh.Transform.Translation(*e.get('origin',[0,0,0])),t)
def expand_parts(e):return SCENE['definitions'][e['definition']]['parts'] if 'definition' in e else e['parts']
def split_surface_parts(parts):
 result=[]
 for part in parts:
  g=part['geometry']
  if g['type']=='surface_polygon':
   p=np.array(g['points']);xy=np.column_stack([p[:,:2],np.zeros(len(p))]);
   for t in triangulate(xy):result.append({'geometry':{'type':'surface_polygon','points':p[t].tolist()},'material':part['material']})
  else:result.append(part)
 return result
def rhino_parts(parts):
 result=[]
 for part in split_surface_parts(parts):
  g=part['geometry']
  if g['type']=='mesh':
   for a,b in zip(g['faces'][::2],g['faces'][1::2]):
    result.append({'geometry':{'type':'nurbs_patch','points':[g['vertices'][i] for i in [a[0],a[1],a[2],b[2]]]},'material':part['material']})
  else:result.append(part)
 return result
def make_rhino(mode):
 model=rh.File3dm();model.Settings.ModelUnitSystem=rh.UnitSystem.Meters;model.Settings.ModelAbsoluteTolerance=.001;model.Settings.ModelAngleToleranceDegrees=.1
 model.ApplicationName='Source-grounded architectural reconstruction';model.ApplicationDetails='Native extrusions, capped Breps and repeated blocks. See Model_Report.md.'
 layerids={};matids={};definitions={};groups={};stats=collections.Counter()
 for name in LAYERS:
  ly=rh.Layer();ly.Name=name;ly.Color=(230,156,63,255) if name=='90_UNCERTAIN' else (160,170,175,255);ly.Visible=name not in ['00_REFERENCE','01_GRID','02_LEVEL','90_UNCERTAIN','99_HELPER'];layerids[name]=model.Layers.Add(ly)
 for name,spec in MATS.items():
  mat=rh.Material();mat.Name=name;mat.DiffuseColor=(*spec['color'],255);mat.Transparency=1-spec.get('alpha',1);mat.IndexOfRefraction=spec.get('ior',1.5);mat.ToPhysicallyBased();mat.PhysicallyBased.Roughness=spec['roughness'];mat.PhysicallyBased.Metallic=spec.get('metallic',0);mat.SetUserString('UV_Mapping','Planar/Box at 1.0m recommended; no bitmap baked');matids[name]=model.Materials.Add(mat)
 def attr(e,material=None,name=None):
  a=rh.ObjectAttributes();a.Name=name or e['name'];a.LayerIndex=layerids[e['layer']];a.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject
  if material:a.MaterialIndex=matids[material];a.ObjectColor=(*MATS[material]['color'],255);a.ColorSource=rh.ObjectColorSource.ColorFromObject
  for k in ['source','confidence','family','status','definition']:a.SetUserString(k,str(e.get(k,'')))
  a.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k not in ['parts']},ensure_ascii=False));return a
 for e in SCENE['elements']:
  if mode=='ARCH' and e['family']=='VIS_MODEL':continue
  if 'definition' in e:
   key=e['definition']
   if key not in definitions:
    geoms=[];attrs=[]
    for j,part in enumerate(SCENE['definitions'][key]['parts']):
     geoms.append(native(part['geometry']));attrs.append(attr(e,part['material'],key+f'_part{j}'))
    idx=model.InstanceDefinitions.Add(key,json.dumps(SCENE['definitions'][key]['parameters']), '', '',rh.Point3d(0,0,0),tuple(geoms),tuple(attrs));definitions[key]=model.InstanceDefinitions[idx].Id
   ir=rh.InstanceReference(definitions[key],rh_transform(e));model.Objects.AddInstanceObject(ir,attr(e));stats['instances']+=1
  else:
   g=rh.Group();g.Name=e['name'];gi=len(model.Groups);model.Groups.Add(g)
   for j,part in enumerate(rhino_parts(e['parts'])):
    ob=native(part['geometry']);ob.Transform(rh_transform(e));a=attr(e,part['material'],e['name']+f'__{j+1}');a.AddToGroup(gi);model.Objects.Add(ob,a);stats[type(ob).__name__]+=1
 for k,v in SCENE['coordinate'].items():model.Strings['Coordinate_'+k]=json.dumps(v)
 model.Strings['Project_Status']=SCENE['status'];model.Strings['ARCH_VIS_Mode']=mode;model.Strings['Source_Scene']='../05_Intermediate/Architecture_Scene.json';model.Strings['Reference_Model']='../04_ContextCapture/Production_1QK_Local_REFERENCE.3dm'
 for cam in SCENE['cameras']:
  vi=rh.ViewInfo();vi.Name=cam['name'];vp=vi.Viewport;pos=cam['position'];tar=cam['target'];vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[tar[k]-pos[k] for k in range(3)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.0625,.0625,.1,10000);vp.SetScreenPort((0,1600,1000,0,0,1));model.NamedViews.Add(vi)
 path=OUT/'06_Rhino'/f'Production_1QK_{mode}.3dm';assert model.Write(str(path),8)
 reread=rh.File3dm.Read(str(path));invalid=[];open_solids=[];objtypes=collections.Counter();visible=0;defobjects=0
 for o in reread.Objects:
  typ=type(o.Geometry).__name__;objtypes[typ]+=1
  if not o.Geometry.IsValid:invalid.append(o.Attributes.Name)
  if o.Attributes.IsInstanceDefinitionObject:defobjects+=1
  else:visible+=1
  if typ in ['Brep','Extrusion'] and not o.Geometry.IsSolid and reread.Layers[o.Attributes.LayerIndex].Name not in ['60_SITE','90_UNCERTAIN']:open_solids.append(o.Attributes.Name)
 result={'path':str(path),'all_objects_including_definitions':len(reread.Objects),'active_objects':visible,'definition_objects':defobjects,'blocks':len(reread.InstanceDefinitions),'types':dict(objtypes),'invalid':invalid,'unexpected_open_solids':open_solids,'units':'Meters','tolerance_m':.001};print('RHINO',json.dumps(result),flush=True);return result
def extra_su_bind():
 for n,args in {'SUCameraCreate':[su.PRef],'SUCameraSetOrientation':[su.Ref,C.POINTER(su.Point),C.POINTER(su.Point),C.POINTER(su.Point)],'SUCameraSetPerspectiveFrustumFOV':[su.Ref,C.c_double],'SUCameraSetAspectRatio':[su.Ref,C.c_double],'SUModelSetCamera':[su.Ref,su.PRef],'SUSceneCreate':[su.PRef],'SUSceneSetName':[su.Ref,C.c_char_p],'SUSceneSetCamera':[su.Ref,su.Ref],'SUModelAddScene':[su.Ref,C.c_int,su.Ref,C.POINTER(C.c_int)],'SUTypedValueCreate':[su.PRef],'SUTypedValueSetInt32':[su.Ref,C.c_int32],'SUTypedValueSetString':[su.Ref,C.c_char_p],'SUTypedValueRelease':[su.PRef],'SUModelGetOptionsManager':[su.Ref,su.PRef],'SUOptionsManagerGetOptionsProviderByName':[su.Ref,C.c_char_p,su.PRef],'SUOptionsProviderSetValue':[su.Ref,C.c_char_p,su.Ref],'SUEntityGetAttributeDictionary':[su.Ref,C.c_char_p,su.PRef],'SUAttributeDictionarySetValue':[su.Ref,C.c_char_p,su.Ref]}.items():su.bind(n,args)
 for n in ['SUComponentInstanceToEntity','SUGroupToEntity']:su.bind(n,[su.Ref],su.Ref)
def soft_edges(ents):
 for n,a in {'SUEntitiesGetEdges':[su.Ref,C.c_bool,su.SZ,su.PRef,C.POINTER(su.SZ)],'SUEdgeSetSoft':[su.Ref,C.c_bool],'SUEdgeSetSmooth':[su.Ref,C.c_bool]}.items():su.bind(n,a)
 n=su.count('SUEntitiesGetNumEdges',ents,True);arr=(su.Ref*n)();got=su.SZ();su.ck(su.SUEntitiesGetEdges(ents,True,n,arr,C.byref(got)))
 for edge in arr:su.ck(su.SUEdgeSetSoft(edge,True));su.ck(su.SUEdgeSetSmooth(edge,True))

def make_skp(mode):
 su.SUInitialize();extra_su_bind();model=su.new('SUModelCreate');root=su.new('SUModelGetEntities',model);su.ck(su.SUModelSetName(model,f'Production_1QK_{mode}'.encode()));su.ck(su.SUModelSetDescription(model,SCENE['status'].encode()));layers={};mats={};defs={};stats=collections.Counter()
 su.bind('SUModelGetAttributeDictionary',[su.Ref,C.c_char_p,su.PRef]);ad=su.new('SUModelGetAttributeDictionary',model,b'Reconstruction');tv=su.new('SUTypedValueCreate');su.ck(su.SUTypedValueSetString(tv,json.dumps(SCENE['coordinate']).encode()));su.ck(su.SUAttributeDictionarySetValue(ad,b'LocalToSurvey',tv));su.SUTypedValueRelease(C.byref(tv))
 for name in LAYERS:
  ly=su.new('SULayerCreate');su.ck(su.SUModelAddLayers(model,1,C.byref(ly)));su.ck(su.SULayerSetName(ly,TAGS[name].encode()));su.ck(su.SULayerSetVisibility(ly,name not in ['00_REFERENCE','01_GRID','02_LEVEL','90_UNCERTAIN','99_HELPER']));layers[name]=ly
 for name,spec in MATS.items():
  mat=su.new('SUMaterialCreate');su.ck(su.SUModelAddMaterials(model,1,C.byref(mat)));su.ck(su.SUMaterialSetName(mat,name.encode()));color=su.Color(*spec['color'],255);su.ck(su.SUMaterialSetColor(mat,C.byref(color)))
  if spec.get('alpha',1)<1:su.ck(su.SUMaterialSetOpacity(mat,spec['alpha']));su.ck(su.SUMaterialSetUseOpacity(mat,True))
  mats[name]=mat
 mgr=su.new('SUModelGetOptionsManager',model);provider=su.new('SUOptionsManagerGetOptionsProviderByName',mgr,b'UnitsOptions')
 for k,val in [('LengthUnit',4),('LengthPrecision',3),('LengthFormat',0)]:
  tv=su.new('SUTypedValueCreate');su.ck(su.SUTypedValueSetInt32(tv,val));su.ck(su.SUOptionsProviderSetValue(provider,k.encode(),tv));su.SUTypedValueRelease(C.byref(tv))
 ag,arch=su.group(root,'ARCH_MODEL');vg,vis=su.group(root,'VIS_MODEL');sg,site=su.group(root,'SITE_MODEL',layers['60_SITE']);ug,unc=su.group(root,'UNCERTAIN_REVIEW',layers['90_UNCERTAIN'])
 def metadata(entity,e):
  tv=su.new('SUTypedValueCreate');su.ck(su.SUTypedValueSetString(tv,json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False).encode()));ad=su.new('SUEntityGetAttributeDictionary',entity,b'Reconstruction');su.ck(su.SUAttributeDictionarySetValue(ad,b'Parameters',tv));su.SUTypedValueRelease(C.byref(tv))
 def fillpart(parent,part,name):
  g,ents=su.group(parent,name);v,f,p,vec=solid_data(part['geometry'])
  if v is None:
   if part['geometry']['type']=='line':su.fill_edges(ents,part['geometry']['points'])
   return g
  if part['geometry']['type']=='prism_holes':
   from su_hole_fill import fill_holes
   fill_holes(ents,part['geometry'],mats[part['material']])
  else:su.fill(ents,v,f,mats[part['material']])
  if part['geometry']['type'] in ['lathe','terrain']:soft_edges(ents)
  return g
 solid_failures=[];volumes=[];index=[]
 for e in SCENE['elements']:
  if mode=='ARCH' and e['family']=='VIS_MODEL':continue
  parent=unc if e['confidence']=='LOW' else site if e['layer']=='60_SITE' else vis if e['family']=='VIS_MODEL' else arch
  if 'definition' in e:
   key=e['definition']
   if key not in defs:
    de=su.new('SUComponentDefinitionCreate');su.ck(su.SUModelAddComponentDefinitions(model,1,C.byref(de)));su.ck(su.SUComponentDefinitionSetName(de,key.encode()));su.ck(su.SUComponentDefinitionSetDescription(de,json.dumps(SCENE['definitions'][key]['parameters']).encode()));ents=su.new('SUComponentDefinitionGetEntities',de)
    for j,part in enumerate(SCENE['definitions'][key]['parts']):fillpart(ents,part,key+f'_part{j+1}')
    defs[key]=de
   ins=su.new('SUComponentDefinitionCreateInstance',defs[key]);su.ck(su.SUEntitiesAddInstance(parent,ins,None));su.ck(su.SUComponentInstanceSetName(ins,e['name'].encode()));su.ck(su.SUComponentInstanceSetTransform(ins,C.byref(su.transform(e.get('origin',[0,0,0]),e.get('angle',0)))));su.ck(su.SUDrawingElementSetLayer(su.SUComponentInstanceToDrawingElement(ins),layers[e['layer']]));metadata(su.SUComponentInstanceToEntity(ins),e);stats['instances']+=1;index.append((e,ins))
  else:
   g,ents=su.group(parent,e['name'],layers[e['layer']]);su.ck(su.SUGroupSetTransform(g,C.byref(su.transform(e.get('origin',[0,0,0]),e.get('angle',0)))));metadata(su.SUGroupToEntity(g),e);stats['groups']+=1
   for j,part in enumerate(split_surface_parts(e['parts'])):
    gg=fillpart(ents,part,e['name']+f'__{j+1}');typ=part['geometry']['type']
    if typ not in ['surface_polygon','mesh','line','terrain']:
     volume=C.c_double();result=su.SUComponentInstanceComputeVolume(su.SUGroupToComponentInstance(gg),None,C.byref(volume))
     if result!=0 or volume.value<=0:solid_failures.append(e['name']+f'__{j+1}:code={result},volume={volume.value}')
     else:volumes.append(volume.value*.0254**3)
 for cam in SCENE['cameras']:
  cr=su.new('SUCameraCreate');pp=su.Point(*[v/.0254 for v in cam['position']]);tt=su.Point(*[v/.0254 for v in cam['target']]);up=su.Point(0,0,1);su.ck(su.SUCameraSetOrientation(cr,C.byref(pp),C.byref(tt),C.byref(up)));su.ck(su.SUCameraSetPerspectiveFrustumFOV(cr,cam['fov']));su.ck(su.SUCameraSetAspectRatio(cr,1.6));sr=su.new('SUSceneCreate');su.ck(su.SUSceneSetName(sr,cam['name'].encode()));idx=C.c_int();su.ck(su.SUModelAddScene(model,-1,sr,C.byref(idx)));su.ck(su.SUSceneSetCamera(sr,cr))
  if cam['name']=='CAM_02_Front':su.ck(su.SUModelSetCamera(model,C.byref(cr)))
 path=OUT/'07_SketchUp'/f'Production_1QK_{mode}.skp';su.ck(su.SUModelSaveToFile(model,str(path).encode()));su.ck(su.SUModelRelease(C.byref(model)))
 reread=su.new('SUModelCreateFromFile',str(path).encode());rroot=su.new('SUModelGetEntities',reread);result={'path':str(path),'semantic_counts':dict(stats),'component_definitions':su.count('SUModelGetNumComponentDefinitions',reread),'tags':su.count('SUModelGetNumLayers',reread),'root_groups':su.count('SUEntitiesGetNumGroups',rroot),'root_loose_faces':su.count('SUEntitiesGetNumFaces',rroot),'root_loose_edges':su.count('SUEntitiesGetNumEdges',rroot,True),'solid_part_count':len(volumes),'solid_failures':solid_failures,'units_display':'metres','internal_units':'inches; conversion 1m=39.37007874015748in','known_width_roundtrip_m':su.readback_door_width(reread)};su.SUModelRelease(C.byref(reread));su.SUTerminate();print('SKP',json.dumps(result),flush=True);return result
def export_obj(mode):
 path=OUT/'08_Export'/f'Production_1QK_{mode}.obj';mtl=path.with_suffix('.mtl');offset=1;triangles=0
 with mtl.open('w') as f:
  for name,spec in MATS.items():f.write(f'newmtl {name}\nKd '+ ' '.join(str(c/255) for c in spec['color'])+f'\nd {spec.get("alpha",1)}\nPr {spec["roughness"]}\nPm {spec.get("metallic",0)}\n\n')
 with path.open('w') as f:
  f.write('# Units metres; Z up; Project local coordinates. See Coordinate_System_Report.md\nmtllib '+mtl.name+'\n')
  for e in SCENE['elements']:
   if mode=='ARCH' and e['family']=='VIS_MODEL':continue
   if e['layer'] in ['01_GRID','02_LEVEL','99_HELPER']:continue
   for j,part in enumerate(split_surface_parts(expand_parts(e))):
    v,faces=world_part(part,e)
    if v is None:continue
    f.write(f'o {e["family"]}__{e["name"]}__{j+1}\ng {e["layer"]}\nusemtl {part["material"]}\n')
    for pt in v:f.write('v '+' '.join(f'{x:.9f}' for x in pt)+'\n')
    for face in faces:
     ts=[list(range(len(face)))] if len(face)==3 else triangulate(v[face])
     for t in ts:f.write('f '+' '.join(str(face[i]+offset) for i in t)+'\n');triangles+=1
    offset+=len(v)
 print('OBJ',mode,'verts',offset-1,'triangles',triangles,flush=True);return {'path':str(path),'vertices':offset-1,'triangles':triangles,'units':'metres'}
if __name__=='__main__':
 qa={}
 for mode in ['ARCH','VIS']:
  qa[mode]={'rhino':make_rhino(mode),'sketchup':make_skp(mode),'obj':export_obj(mode)}
 import shutil
 for ext,d in [('3dm','06_Rhino'),('skp','07_SketchUp'),('obj','08_Export'),('mtl','08_Export')]:shutil.copy2(OUT/d/f'Production_1QK_ARCH.{ext}',OUT/d/f'Production_1QK_Rebuild.{ext}')
 (OUT/'09_Report/Native_Model_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
