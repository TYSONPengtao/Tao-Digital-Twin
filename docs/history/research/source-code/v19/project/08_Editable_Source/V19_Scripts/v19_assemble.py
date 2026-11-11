"""Save the photo-fitted V19 perimeter as a separate native Rhino model."""
import sys,json,math,hashlib,shutil,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V18');O=Path(r'E:/jz/JIA/Rebuild_V19');D=W/'v19';BP=B/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm';P=O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(BP)=='ee452e5c6dbf3edb6d44d7a74f49c6d9d4a299d39303857f87fa5682ac3d2731','Baseline changed during V19 work'
for n in ['01_Source','02_Data/Native_Readback','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source/V19_Scripts']:(O/n).mkdir(parents=True,exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True);shutil.copytree(B/'07_Reference',O/'07_Reference',dirs_exist_ok=True)
for s in [r'D:/DJI/0002/DCIM/101MEDIA/DJI_0073.JPG',r'D:/Desktop/问题/屏幕截图 2026-10-12 110221.jpg',r'D:/Desktop/问题/屏幕截图 2026-10-12 125511.jpg',r'D:/Desktop/屏幕截图 2026-10-12 071212.jpg']:
 if Path(s).exists():shutil.copy2(s,O/'07_Reference'/Path(s).name)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));S=json.loads((B/'08_Editable_Source/Architecture_Scene_V18.json').read_text(encoding='utf8'));ex.SCENE=S;I=json.loads((B/'02_Data/Native_Readback_Index_V18.json').read_text(encoding='utf8'));F=rh.File3dm.Read(str(BP));C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
de=next(e for e in Q['add'] if e['name']=='SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES');old_frames=sum(len(e['parts']) for e in S['elements'] if e['name'] in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_PLASTER_STEPPED_RELIEF','SITE_PERIMETER_JOINED_RETAINING_WALL_1_PLASTER_STEPPED_RELIEF']);de['v19_backing_piece_count']=len(de['parts'])-old_frames-2*len(de['v19_screen_frame_x_spans']);assert de['v19_backing_piece_count']>1
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def node_obs(n):return [ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
t=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented']],type_ignores=[]),'<helpers>','exec'))
changed={e['name'] for e in Q['replace']+Q['add']};removed=set(Q['remove']);delete_names=changed|removed;to_delete=[o for n in delete_names for o in node_obs(n)];delete_ids={str(o.Attributes.Id) for o in to_delete};stale={r['name'] for r in I if not node_obs(r['name'])};assert not stale,stale
retained=[{'id':str(o.Attributes.Id),'name':o.Attributes.Name,'geometry_hash':gh(o.Geometry)} for o in F.Objects if str(o.Attributes.Id) not in delete_ids];deleted=[{'id':str(o.Attributes.Id),'name':o.Attributes.Name} for o in to_delete];created=[]
print('V18 BASELINE HASHED',len(retained),'DELETING',len(to_delete),flush=True)
for m in F.Materials:
 for getter,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
  tx=getattr(m,getter)()
  if tx:
   pp=Path(tx.FileName.replace('Rebuild_V18','Rebuild_V19'));assert pp.exists(),pp;getattr(m,setter)(str(pp))
NM=json.loads((D/'Materials.json').read_text(encoding='utf8'));TD=O/'03_Textures/V19_Perimeter_AsBuilt'
for name,md in NM.items():
 m=rh.Material();m.Name=name;m.DiffuseColor=tuple(md['color'])+(255,);m.Transparency=md.get('transparency',0);m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=tuple(c/255 for c in md['color'])+(1,);m.PhysicallyBased.Roughness=md['roughness'];m.PhysicallyBased.Metallic=md.get('metallic',0)
 for key,setter in [('bitmap','SetBitmapTexture'),('bump','SetBumpTexture')]:
  p=TD/md[key] if key in md else O/'03_Textures'/md[key+'_relative'] if key+'_relative' in md else None
  if p:assert p.exists(),p;getattr(m,setter)(str(p))
 F.Materials.Add(m);S['materials'][name]={'color':md['color'],'roughness':md['roughness'],'source':'Real INSV 890-second reference and same perimeter walk; V19 surface record'}
FD=json.loads((D/'Facade_Segments.json').read_text(encoding='utf8'));routes={}
for kind in ['brick','stone']:
 for wall in sorted({r['node'] for r in FD[kind]}):
  rr=[];seen=set()
  for r in FD[kind]:
   if r['node']!=wall:continue
   aa,bb=np.array(r['a']),np.array(r['b']);L=np.linalg.norm(bb-aa)
   if L<.34:continue
   key=tuple(sorted((tuple(np.round(aa,8)),tuple(np.round(bb,8)))))
   if key in seen:continue
   seen.add(key);rr.append({**r,'a':aa,'b':bb})
  station=0.;prev=None
  for k,r in enumerate(rr):
   aa,bb=r['a'],r['b']
   if prev is not None:
    if np.linalg.norm(bb-prev)<np.linalg.norm(aa-prev):aa,bb=bb,aa
    station+=np.linalg.norm(aa-prev)
   elif len(rr)>1:
    nx=[rr[1]['a'],rr[1]['b']]
    if min(np.linalg.norm(aa-p) for p in nx)<min(np.linalg.norm(bb-p) for p in nx):aa,bb=bb,aa
   L=np.linalg.norm(bb-aa);r.update(a=aa,b=bb,u=(bb-aa)/L,L=L,station=station);station+=L;prev=bb
  routes[(kind,wall)]=rr
def uv_for(q,no,mat,node):
 axes=[j for j in range(3) if j!=int(np.argmax(abs(no)))];uv=q[:,axes].copy()
 if mat in ['M_V19_Perimeter_Brick','M_V19_Perimeter_Dark_Stone','M_V19_Perimeter_Rubble']:
  dim=NM[mat]['repeat_m'];uv/=np.array(dim);kind='brick' if mat.endswith('Brick') else 'stone';best=None;c=q.mean(0)
  for (kk,wall),rr in routes.items():
   if kk!=kind or (node.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_') and wall!=node):continue
   for r in rr:
    t=np.clip((c[:2]-r['a'])@r['u'],0,r['L']);dist=np.linalg.norm(c[:2]-r['a']-r['u']*t)
    if best is None or dist<best[0]:best=(dist,r)
  if best is not None and abs(no[2])<.5:
   r=best[1];uv[:,0]=((q[:,:2]-r['a'])@r['u']+r['station'])/dim[0]
   if abs(np.dot(no[:2],np.array(r['normal'])))<.65:
    tu=np.array([-no[1],no[0]]);tu/=np.linalg.norm(tu)
    if np.dot(tu,r['u'])<0:tu=-tu
    st=(c[:2]-r['a'])@r['u']+r['station'];uv[:,0]=((q[:,:2]-c[:2])@tu+st)/dim[0]
   if 'Dark_Stone' in mat:
    cp=np.array(r['top_plane']);uv[:,1]=(q[:,2]-np.c_[q[:,:2],np.ones(3)]@cp+.56)/dim[1]
   else:uv[:,1]=(q[:,2]+(4.45 if 'Rubble' in mat else 0))/dim[1]
 return uv
def make(g,mat,node):
 g=oriented(g);v=np.array(g['vertices']);ff=triangles(v,g['faces']);t=v[ff];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ll=np.linalg.norm(nn,axis=1);assert ll.min()>1e-12,(node,ll.min());nn/=ll[:,None];mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 for k,q in enumerate(t):
  uv=uv_for(q,nn[k],mat,node)
  for p,u in zip(q@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
  mm.Faces.AddFace(k*3,k*3+1,k*3+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid and mm.IsClosed,node
 return mm
for ob in to_delete:F.Objects.Delete(ob.Attributes.Id)
for e in Q['replace']+Q['add']:
 n=e['name'];gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for j,p in enumerate(e['parts']):
  mm=make(p['geometry'],p['material'],n);at=rh.ObjectAttributes();at.Name=f'{n}__{j+1}';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V19_Node',n);at.SetUserString('V19_Reference','INSV user anchor 890s; perimeter walk 870..972s; DJI_0073');at.SetUserString('Dimension_Status','PHOTO_FIT');ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True})
 print('CREATED V19',n,len(e['parts']),flush=True)
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
VIEWS=[('V19_Perimeter_Screenwall_Road',[7,-26,-.25],[7,-17,.65],80),('V19_Perimeter_Ordinary_South',[-7,-23,-.35],[-7,-15.7,.65],80),('V19_Perimeter_West_Road',[-32,-2,.0],[-24.5,-1,.8],82),('V19_Perimeter_Northwest_Corner',[-28,11,.8],[-23,6.5,1.0],75),('V19_Perimeter_Coping_Detail',[-10,-18.6,3.1],[-8.7,-16,2.6],72),('V19_Perimeter_Storage_Junction',[25,-22,2.0],[17.8,-14.9,.3],65)]
for name,pos,tar,fov in VIEWS:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));span=.1*math.tan(math.radians(fov/2));vp.SetFrustum(-span,span,-span*1100/1600,span*1100/1600,.1,5000);F.NamedViews.Add(vi)
S['version']='V19';S['v19_changes']=['INSV 890-second real perimeter finishes','Continuous rubble base, dark regular stone courses and gray brick','Narrow under-eave pale panels instead of blank white screen plate','Ordinary solid wall coping without unverified floral crown','Coping bedding contacts and orphan cut-tip cleanup'];sp=O/'08_Editable_Source/Architecture_Scene_V19.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2).replace('Rebuild_V18','Rebuild_V19'),encoding='utf8');F.Strings['V19_Editable_Scene_SHA256']=sha(sp);F.Strings['V19_Base_Model']='V18 preserved unchanged';F.Strings['V19_Status']='As-built photo-fitted perimeter; surface dimensions follow registered wall and video, without new field measurements';assert F.Write(str(P),8)
for name in ['Native_Readback_Index_V19.json','Modeled_Index_V19.json']:(O/'02_Data'/name).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported;md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':sup,'bump_distance_m':NM.get(m.Name,{}).get('bump_distance_m',.003)}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8');AQ={'status':'AWAITING_FRESH_READBACK','base_model':str(BP),'base_model_sha256':sha(BP),'retained':retained,'deleted':deleted,'created':created,'changed_nodes':sorted(changed),'removed_nodes':sorted(removed),'stale_base_cache_nodes_removed':sorted(stale),'native_objects':len(F.Objects),'nodes':len(rows),'cameras':VIEWS};(O/'06_Report/V19_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
for src,dest in [('Design_Control.json','06_Report/V19_Design_Control.json'),('Mutation.json','08_Editable_Source/Mutation_V19.json'),('Materials.json','08_Editable_Source/Perimeter_Materials_V19.json'),('Facade_Segments.json','02_Data/Perimeter_Facade_Segments_V19.json')]:shutil.copy2(D/src,O/dest)
(O/'08_Editable_Source/Mutation_V19.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
print('V19 NATIVE SAVED',len(F.Objects),len(rows),P.stat().st_size,flush=True)
