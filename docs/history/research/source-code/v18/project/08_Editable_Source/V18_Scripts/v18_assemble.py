"""Write a separate native V18 with selective photo-backed storage edits."""
import sys,json,math,hashlib,shutil,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V17');O=Path(r'E:/jz/JIA/Rebuild_V18');D=W/'v18';P=O/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm'
for n in ['01_Source','02_Data/Native_Readback','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source/V18_Scripts']:(O/n).mkdir(parents=True,exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True);shutil.copytree(B/'07_Reference',O/'07_Reference',dirs_exist_ok=True)
for s in [r'D:/Desktop/问题/屏幕截图 2026-10-12 180115.jpg',r'D:/Desktop/问题/屏幕截图 2026-10-12 180137.jpg']:shutil.copy2(s,O/'07_Reference'/Path(s).name)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));S=json.loads((B/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'))
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented']),('v17_assemble.py',['gh','node_obs'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
changed={e['name'] for e in Q['replace']+Q['add']};removed=set(Q['remove']);delete_names=changed|removed;to_delete=[o for n in delete_names for o in node_obs(n)];delete_ids={str(o.Attributes.Id) for o in to_delete}
stale_cache_names={r['name'] for r in I if not node_obs(r['name'])};removed|=stale_cache_names;delete_names|=stale_cache_names
retained=[{'id':str(o.Attributes.Id),'name':o.Attributes.Name,'geometry_hash':gh(o.Geometry)} for o in F.Objects if str(o.Attributes.Id) not in delete_ids];deleted=[{'id':str(o.Attributes.Id),'name':o.Attributes.Name} for o in to_delete];created=[]
print('LOADED V17; HASHED RETAINED',len(retained),'REMOVING',len(to_delete),flush=True)
for m in F.Materials:
 for getter,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
  tx=getattr(m,getter)()
  if tx:
   pp=Path(tx.FileName.replace('Rebuild_V17','Rebuild_V18'));assert pp.exists(),pp;getattr(m,setter)(str(pp))
NM=json.loads((D/'Materials.json').read_text(encoding='utf8'));TD=O/'03_Textures/V18_Storage_AsBuilt'
for name,md in NM.items():
 m=rh.Material();m.Name=name;m.DiffuseColor=tuple(md['color'])+(255,);m.Transparency=md.get('transparency',0);m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=tuple(c/255 for c in md['color'])+(1,);m.PhysicallyBased.Roughness=md['roughness'];m.PhysicallyBased.Metallic=md.get('metallic',0)
 if md.get('bitmap'):m.SetBitmapTexture(str(TD/md['bitmap']))
 if md.get('bump'):m.SetBumpTexture(str(TD/md['bump']))
 F.Materials.Add(m);S['materials'][name]={'color':md['color'],'roughness':md['roughness'],'source':'Photo 180115 storage finish; V18 material control record'}
bays=next(e for e in Q['replace'] if e['name']=='SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD')['v18_bays']
wallpoly=np.array(next(e for e in Q['add'] if e['name']=='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE')['v18_exterior_plan']);wallsegments=[];station=0
for p,r in zip(wallpoly,np.roll(wallpoly,-1,axis=0)):
 d=r-p;ll=np.linalg.norm(d);wallsegments.append((p,r,d/ll,ll,station));station+=ll
def uv_for(q,normal,mat):
 axes=[j for j in range(3) if j!=int(np.argmax(abs(normal)))];uv=q[:,axes].copy()
 if mat in ['M_V18_Storage_Rubble','M_V18_Storage_Dark_Courses']:
  dims=NM[mat]['repeat_m'];uv[:,0]/=dims[0];uv[:,1]/=dims[1]
  if abs(normal[2])<.4:
   center=q.mean(0);best=None
   for aa,bb,dd,L,st in wallsegments:
    tt=np.clip((center[:2]-aa)@dd,0,L);distance=np.linalg.norm(center[:2]-aa-dd*tt)
    if best is None or distance<best[0]:best=(distance,aa,dd,st)
   if best[0]<.18:uv[:,0]=((q[:,:2]-best[1])@best[2]+best[3])/dims[0]
   uv[:,1]=(q[:,2]+(4.45 if 'Rubble' in mat else 1.05))/dims[1]
  return uv
 if mat=='M_V18_Storage_Stone_Guard':
  uv=np.full((3,2),.94);center=q.mean(0)
  if -.249<center[2]<.190 and abs(normal[2])<.35:
   for bay in bays:
    aa,bb=np.array(bay['panel_start']),np.array(bay['panel_end']);d=np.array(bay['direction']);n=np.array(bay['normal']);L=np.linalg.norm(bb-aa);u=(q[:,:2]-aa)@d;delta=(center[:2]-aa)@n
    if .040<(center[:2]-aa)@d<L-.040 and abs(delta)<.061 and abs(np.dot(normal[:2],n))>.90:
     uv[:,0]=(32+768*np.clip(u/L,0,1))/1024;uv[:,1]=(32+384*np.clip((q[:,2]+.253)/.447,0,1))/512;break
  return uv
 return uv
def make(g,mat):
 g=oriented(g);v=np.array(g['vertices']);ff=triangles(v,g['faces']);t=v[ff];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.linalg.norm(no,axis=1)[:,None];mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 for k,q in enumerate(t):
  uv=uv_for(q,no[k],mat)
  for p,u in zip(q@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
  mm.Faces.AddFace(k*3,k*3+1,k*3+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid and mm.IsClosed
 return mm
for ob in to_delete:F.Objects.Delete(ob.Attributes.Id)
for e in Q['replace']+Q['add']:
 n=e['name'];gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for j,p in enumerate(e['parts']):
  mm=make(p['geometry'],p['material']);at=rh.ObjectAttributes();at.Name=f'{n}__{j+1}';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V18_Node',n);at.SetUserString('V18_Reference','180115 actual photo; INSV exterior 950/972');at.SetUserString('Dimension_Status','PHOTO_FIT');ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True})
 print('CREATED',n,len(e['parts']),flush=True)
S['elements']=[e for e in S['elements'] if e['name'] not in delete_names]+Q['replace']+Q['add'];rows=[]
for r in I:
 if r['name'] not in delete_names:shutil.copy2(B/'02_Data'/r['file'],O/'02_Data'/r['file']);rows.append(r)
for n in sorted(changed):
 e=next(e for e in S['elements'] if e['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node_obs(n)
 for ob in oo:
  mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(oo),'element':{k:v for k,v in e.items() if k!='parts'}})
paths=set()
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:paths.add(Path(tx.FileName))
embedded={ef.Filename for ef in F.EmbeddedFiles}
for pp in paths:
 assert pp.exists(),pp
 if str(pp) not in embedded:F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(pp)))
VIEWS=[('V18_Storage_Photo_Exterior',[17.5,-24.0,-3.10],[17.9,-15.8,-.35],72),('V18_Storage_Exterior_Oblique',[25,-22,2.0],[17.8,-14.9,.3],65),('V18_Storage_Base_Drain',[24,-17,-2.5],[20.7,-14,-2.2],66)]
for name,pos,tar,fov in VIEWS:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));span=.1*math.tan(math.radians(fov/2));vp.SetFrustum(-span,span,-span*1100/1600,span*1100/1600,.1,5000);F.NamedViews.Add(vi)
S['version']='V18';S['v18_changes']=['Continuous real stone plinth and road-level toe','Wider stone balustrade bays and horizontal pierced openings','Aged storage timber finish and thinner fitted metal canopy','Two photographed exterior white pipe/pole lines'];sp=O/'08_Editable_Source/Architecture_Scene_V18.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2).replace('Rebuild_V17','Rebuild_V18'),encoding='utf8');F.Strings['V18_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V18_Base_Model']='V17 preserved unchanged';F.Strings['V18_Status']='Photo-fitted storage exterior; hidden footing depth is display closure, not a structural design';assert F.Write(str(P),8)
for name in ['Native_Readback_Index_V18.json','Modeled_Index_V18.json']:(O/'02_Data'/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported;md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':sup,'bump_distance_m':NM.get(m.Name,{}).get('bump_distance_m',.003)}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8');AQ={'status':'AWAITING_FRESH_READBACK','base_model':str(B/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'),'base_model_sha256':hashlib.sha256((B/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm').read_bytes()).hexdigest(),'retained':retained,'deleted':deleted,'created':created,'changed_nodes':sorted(changed),'removed_nodes':sorted(removed),'stale_base_cache_nodes_removed':sorted(stale_cache_names),'native_objects':len(F.Objects),'nodes':len(rows),'cameras':VIEWS};(O/'06_Report/V18_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(D/'Design_Control.json',O/'06_Report/V18_Design_Control.json');shutil.copy2(D/'Baseline_Audit.json',O/'06_Report/V18_Baseline_Audit.json');shutil.copy2(D/'Mutation.json',O/'08_Editable_Source/Mutation_V18.json');shutil.copy2(D/'Materials.json',O/'08_Editable_Source/Storage_Materials_V18.json')
print('V18 NATIVE SAVED',len(F.Objects),len(rows),P.stat().st_size,flush=True)
