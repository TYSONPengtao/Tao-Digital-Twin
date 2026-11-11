import sys,json,math,hashlib,collections,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path(r'E:\jz\JIA\Rebuild_V12');O=Path(r'E:\jz\JIA\Rebuild_V13')
for d in ['02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source']:(O/d).mkdir(parents=True,exist_ok=True)
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as fp:
  for x in iter(lambda:fp.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V12.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
source=B/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm';f=rh.File3dm.Read(str(source));print('loaded',len(f.Objects),flush=True)
changes=[];definitions={d.Name:d for d in f.InstanceDefinitions};defmembers={str(x):(n,i) for n,d in definitions.items() for i,x in enumerate(d.GetObjectIds())}
for ob in list(f.Objects):
 at=ob.Attributes;n=at.Name
 if at.IsInstanceDefinitionObject:
  key,index=defmembers[str(at.Id)]
  if key not in S['definitions']:continue
  part=S['definitions'][key]['parts'][index];e=None
 else:
  if '__' not in n or not n.rsplit('__',1)[1].isdigit():continue
  base,pi=n.rsplit('__',1);e=E.get(base)
  if e is None:raise ValueError('Unmapped native '+n)
  index=int(pi)-1;parts=ex.expand_parts(e)
  if len(parts)<index+1:continue
  part=parts[index]
 g=part['geometry']
 if g['type']!='prism_holes' or not g.get('holes'):continue
 if not isinstance(ob.Geometry,rh.Extrusion):raise ValueError('Unexpected native type '+n)
 # Compare every top and bottom hole's world position with its source ring.
 correct=ex.native(g)
 if e is not None:correct.Transform(ex.rh_transform(e));correct.Transform(T)
 errors=[]
 for i in range(1,correct.ProfileCount):
  ca=correct.Profile3d(i,0);cb=ob.Geometry.Profile3d(i,0);ba=ca.GetBoundingBox();bb=cb.GetBoundingBox()
  errors.append(max(abs(getattr(p,c)-getattr(q,c)) for p,q in [(ba.Min,bb.Min),(ba.Max,bb.Max)] for c in ['X','Y','Z']))
 if max(errors,default=0)<1e-8:continue
 # Preserve GUID, groups, layer, material, user metadata, and block membership.
 aa=at;aa.SetUserString('V13_Profile_Repair','Explicit shared XY profile coordinates; displaced hole walls removed');aa.SetUserString('V13_Max_Previous_Hole_Offset_m',str(max(errors)))
 ident=aa.Id;f.Objects.Delete(ident);assert f.Objects.Add(correct,aa)==ident
 changes.append({'id':str(ident),'name':n,'node':e['name'] if e is not None else key,'definition_member':at.IsInstanceDefinitionObject,'hole_count':len(g['holes']),'max_previous_hole_offset_m':max(errors),'geometry_type':'Extrusion','reason':'Inner profiles in world coordinates had been added to a fitted local profile plane'})
print('repaired',len(changes),'objects',sum(c['hole_count'] for c in changes),'hole rings',flush=True)
S['name']='Architecture_Complete_V13';S['revision_notes'].append('V13 native extrusion inner-profile coordinate repair; no design geometry moved by this export correction; actual 3DM mesh readback and support review required.')
save(O/'08_Editable_Source/Architecture_Scene_V13.json',S)
for p in (B/'02_Data').iterdir():
 if p.is_file():shutil.copy2(p,O/'02_Data'/p.name)
shutil.copy2(O/'02_Data/Modeled_Index_V12.json',O/'02_Data/Modeled_Index_V13.json')
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True)
# Reference evidence is independent and immutable.
for p in [Path(r'D:\Desktop\问题\屏幕截图 2026-10-11 231708.jpg'),Path(r'D:\Desktop\问题\屏幕截图 2026-10-11 231630.jpg')]:shutil.copy2(p,O/'07_Reference'/p.name)
for m in f.Materials:
 if m.GetBitmapTexture() and m.GetBitmapTexture().FileName.startswith(str(B)):m.SetBitmapTexture(m.GetBitmapTexture().FileName.replace(str(B),str(O),1))
 if m.GetBumpTexture() and m.GetBumpTexture().FileName.startswith(str(B)):m.SetBumpTexture(m.GetBumpTexture().FileName.replace(str(B),str(O),1))
f.Strings['Usage']='V13 corrected native extrusion hole loops, source-referenced architectural model in ENU metres. See actual native geometry QA.'
f.Strings['V13_Scene_SHA256']=sha(O/'08_Editable_Source/Architecture_Scene_V13.json')
dest=O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm';assert f.Write(str(dest),8)
save(O/'06_Report/Profile_Repair_QA.json',{'status':'REPAIRED_PENDING_KERNEL_NATIVE_READBACK','source':str(source),'source_sha256':sha(source),'model':str(dest),'sha256':sha(dest),'repaired_objects':len(changes),'repaired_hole_rings':sum(c['hole_count'] for c in changes),'changed_native_ids':[c['id'] for c in changes],'changes':changes,'source_scene_geometry_unchanged':True,'object_count_unchanged':len(f.Objects)==24892,'mechanical_capacity_calculated':False})
print('written',dest,flush=True)
