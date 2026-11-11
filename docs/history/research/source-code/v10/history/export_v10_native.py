# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,math,collections,hashlib,struct,os
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');F=rh.File3dm.Read(str(O/'01_Source/V9_Current_Before_V10.3dm'));base_count=5;I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));coord=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(coord['rotation_deg']);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(coord['origin']);layerids={ly.Name[6:]:ly.Index for ly in F.Layers if ly.Name.startswith('PATCH_')};matids={m.Name:i for i,m in enumerate(F.Materials)}
change=json.loads((O/'02_Data/V10_Changed_Nodes.json').read_text(encoding='utf-8'));changed=set(change['changed']);retire=changed|set(change['removed'])
for ob in list(F.Objects):
 if not ob.Attributes.IsInstanceDefinitionObject and any(ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__') for n in retire):F.Objects.Delete(ob.Attributes.Id)
I=[r for r in I if r['name'] in changed]
# Original base materials and their embedded image references remain intact.
for name,spec in M.items():
 if 'base_material_index' in spec:
  matids[name]=spec['base_material_index'];continue
 if name in matids:continue
 mat=rh.Material();mat.Name=name;mat.DiffuseColor=(*spec['color'],255);mat.Transparency=1-spec.get('alpha',1);mat.IndexOfRefraction=spec.get('ior',1.52);mat.ToPhysicallyBased();mat.PhysicallyBased.Roughness=spec['roughness'];mat.PhysicallyBased.Metallic=spec.get('metallic',0)
 if spec.get('texture'):
  mat.SetBitmapTexture(spec['texture']);F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(spec['texture']))
 matids[name]=F.Materials.Add(mat)
for row in I:
 layer=row['element'].get('layer','60_SITE')
 if layer not in layerids:
  ly=rh.Layer();ly.Name='PATCH_'+layer;ly.Color=(210,170,90,255);layerids[layer]=F.Layers.Add(ly)
definitions={};invalid=[];count=collections.Counter()
def make_mesh(v,f,uv):
 mesh=rh.Mesh()
 mesh.Vertices.UseDoublePrecisionVertices=True
 for p in v:mesh.Vertices.AddPoint3d(*map(float,p))
 for face in f:mesh.Faces.AddFace(*map(int,face))
 mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));mesh.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
 for j,q in enumerate(uv):mesh.TextureCoordinates[j]=rh.Point2f(*map(float,q))
 before=len(mesh.Faces);mesh.Faces.CullDegenerateFaces();count['tiny_patch_faces_removed']+=before-len(mesh.Faces)
 mesh.Normals.ComputeNormals()
 return mesh
def attrs(row,m,name):
 e=row['element'];at=rh.ObjectAttributes();at.Name=name;at.LayerIndex=layerids[e.get('layer','60_SITE')];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=matids[m]
 for k in ['door_id','role','source','confidence','status','family','interaction']:at.SetUserString(k,str(e.get(k,'')))
 at.SetUserString('PatchRole',row['role']);at.SetUserString('Parameters',json.dumps(e,ensure_ascii=False));return at
for row in I:
 e=row['element'];d=np.load(O/'02_Data'/row['file']);v=d['vertices'];faces=d['faces'];uv=d['uv'];mid=d['material_ids'];geoms=[];ats=[]
 isblock=bool(e.get('definition'))
 if isblock:
  aa=e.get('angle',0);cc=math.cos(aa);ss=math.sin(aa);inv=np.array([[cc,ss,0],[-ss,cc,0],[0,0,1]]);v=(v-np.array(e.get('origin',[0,0,0])))@inv.T
 else:v=v@R.T+origin
 for mi,m in enumerate(row['materials']):
  ff=faces[mid==mi]
  if not len(ff):continue
  ids=np.unique(ff);remap=np.full(len(v),-1,np.int32);remap[ids]=np.arange(len(ids));mesh=make_mesh(v[ids],remap[ff],uv[ids]);geoms.append(mesh);ats.append(attrs(row,m,row['name']+'__'+m));count['patch_meshes']+=1
 if isblock:
  key='PATCH_'+row['name']+'_'+e['definition']
  if key not in definitions:
   idx=F.InstanceDefinitions.Add(key,'V10 corrected patch definition with true hinge origin','','',rh.Point3d(0,0,0),tuple(geoms),tuple(ats));definitions[key]=F.InstanceDefinitions[idx].Id
  eo=np.array(e['origin'])@R.T+origin;rot=rh.Transform.Rotation(e.get('angle',0)+a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0));tr=rh.Transform.Multiply(rh.Transform.Translation(*eo),rot);ir=rh.InstanceReference(definitions[key],tr);at=attrs(row,row['materials'][0],row['name']);F.Objects.AddInstanceObject(ir,at);count['patch_blocks']+=1
 else:
  g=rh.Group();g.Name=row['name'];gi=len(F.Groups);F.Groups.Add(g)
  for mesh,at in zip(geoms,ats):at.AddToGroup(gi);F.Objects.AddMesh(mesh,at)
campos=np.array([41,-52,47])@R.T+origin;target=np.array([0,-1,3])@R.T+origin
vi=rh.ViewInfo();vi.Name='V10_Whole_Site';vp=vi.Viewport;vp.SetCameraLocation(rh.Point3d(*campos));vp.SetCameraDirection(rh.Vector3d(*(target-campos)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.07,.07,.1,10000);vp.SetScreenPort((0,1600,1120,0,0,1));F.NamedViews.Add(vi);F.Views.Add(vi)
F.Strings['SourceBase']='../01_Source/Pure_Site_WORKING_V8.3dm';F.Strings['V10Baseline']='../01_Source/V9_Current_Before_V10.3dm';F.Strings['OriginalSource']='../01_Source/Pure_Site_UNMODIFIED.3dm';F.Strings['SourceBaseRole']='Original source file retained; working derivative locally clipped only in user-authorized terrain/roof/contact repair regions';F.Strings['PatchCoordinate']=json.dumps(coord);F.Strings['PatchScope']='V10 Chinese courtyard wall detail clipped to inherited void/contact scope; unchanged current V9 geometry and source photographs outside changed wall nodes preserved; full editable wall solids in aligned companion';F.Strings['SRS']='ENU:TAO_PRIVATE_SITE_003,TAO_PRIVATE_SITE_024; metres, Z up'
path=O/'04_Rhino/Reality_Hybrid_V10.3dm';assert F.Write(str(path),8);check=rh.File3dm.Read(str(path))
for ob in check.Objects:
 if not ob.Geometry.IsValid:invalid.append(ob.Attributes.Name)
report={'path':str(path),'base_objects':base_count,'total_objects':len(check.Objects),'blocks':len(check.InstanceDefinitions),'counts':dict(count),'invalid':invalid,'embedded_images':len(check.EmbeddedFiles),'units':'Metres, original ENU Z-up','base_materials_unmodified':True,'original_source_file_unmodified':True,'working_geometry_has_authorized_local_edits':True,'texture_resolution':'Original five embedded photos, four original donor photos and a directly referenced DJI gable image; companion external copies included'}
(O/'06_Report/Native_Hybrid_QA.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report,flush=True)
assert not invalid
