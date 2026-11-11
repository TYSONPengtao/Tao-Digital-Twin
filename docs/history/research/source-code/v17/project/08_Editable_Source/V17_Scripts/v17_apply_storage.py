import sys,json,math,hashlib,ast,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:/jz/JIA/Rebuild_V17');D=W/'v17';P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'
S=json.loads((O/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;Q=json.loads((D/'Storage_Mutation.json').read_text(encoding='utf8'));F=rh.File3dm.Read(str(P));I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'))
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
tree=ast.parse((W/'v17_assemble.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['make_mesh','gh','node_obs']],type_ignores=[]),'<native_helpers>','exec'))
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented']],type_ignores=[]),'<geometry_helpers>','exec'))
removedids=set();new_records=[];deleted=[];checks=[];changednames=set()
def delete(ob,node):
 ident=str(ob.Attributes.Id);removedids.add(ident);F.Objects.Delete(ob.Attributes.Id);deleted.append({'id':ident,'name':ob.Attributes.Name,'node':node})
def add(node,p,at,name):
 p['geometry']=oriented(p['geometry']);mm,_,_,_=make_mesh(p['geometry']);at.Name=name;at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V17_Node',node);at.SetUserString('V17_Repair','Chinese timber storage and open eave gallery; stone guard');ident=F.Objects.Add(mm,at);new_records.append({'id':str(ident),'name':name,'node':node,'geometry_hash':gh(mm),'closed_expected':True});checks.append({'name':name,'is_valid':mm.IsValid,'is_closed':mm.IsClosed,'vertices':len(mm.Vertices),'faces':len(mm.Faces),'full_uv':len(mm.TextureCoordinates)==len(mm.Vertices)})
for pe in Q['part_edits']:
 oo=next(ob for ob in F.Objects if ob.Attributes.Name==pe['native_name']);delete(oo,pe['node']);changednames.add(pe['node'])
for e in Q['replace']:
 n=e['name'];changednames.add(n)
 if e.get('v17_partwise'):continue
 oo=node_obs(n);ats=[o.Attributes for o in oo];assert oo,n;groupids=ats[0].GetGroupList();layer=ats[0].LayerIndex
 for ob in oo:delete(ob,n)
 for j,p in enumerate(e['parts']):
  if j<len(ats):at=ats[j]
  else:
   at=rh.ObjectAttributes();at.LayerIndex=layer
   for gid in groupids:at.AddToGroup(gid)
  add(n,p,at,f'{n}__{j+1}')
 print('UPDATED STORAGE NODE',n,len(e['parts']),flush=True)
for e in Q['add']:
 n=e['name'];assert not node_obs(n),n;changednames.add(n);gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for j,p in enumerate(e['parts']):
  at=rh.ObjectAttributes();at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);add(n,p,at,f'{n}__{j+1}')
 print('ADDED STORAGE NODE',n,len(e['parts']),flush=True)
newids={r['id'] for r in new_records};deleted=[r for r in deleted if r['id'] not in newids];AQ['retained']=[r for r in AQ['retained'] if r['id'] not in removedids];AQ['created']=[r for r in AQ['created'] if r['id'] not in removedids]+new_records;AQ['deleted']+=[r for r in deleted if r['id'] not in {q['id'] for q in AQ['deleted']}];AQ['mesh_checks']+=checks;AQ['changed_nodes']=sorted(set(AQ['changed_nodes'])|changednames)
S['elements']=[e for e in S['elements'] if e['name'] not in changednames]+Q['replace']+Q['add'];rows=[r for r in I if r['name'] not in changednames]
for n in sorted(changednames):
 eo=next(e for e in S['elements'] if e['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node_obs(n)
 for ob in oo:
  mm=ob.Geometry;assert isinstance(mm,rh.Mesh);mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:
   ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
   if f[3]!=f[2]:ff.append((np.array([f[0],f[2],f[3]])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(oo),'element':{k:v for k,v in eo.items() if k!='parts'}})
for name,pos,tar in [('V17_Storage_Timber_Interior',[16.2,-14.30,.8],[16.1,-11.8,2.1]),('V17_Storage_Eave_Gallery',[14.5,-15.55,.75],[17.8,-15.5,1.0]),('V17_Storage_Stone_Guard_Exterior',[22,-22,2.0],[16.3,-15.75,.6])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
S['v17_changes']+=['Chinese timber storage frame with floor-supported columns, stepped lifting beams, purlins and rafters','Roof-covered open gallery with set-back timber entry front and continuous stone guard'];sp=O/'08_Editable_Source/Architecture_Scene_V17.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V17_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V17_Storage_Reference']='INSV 700/705/715/725 s; Chinese timber frame and eave gallery, photo-fitted; existing roof valley kept';assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V17.json','Modeled_Index_V17.json']:(O/'02_Data'/nm).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
AQ['native_objects']=len(F.Objects);AQ['nodes']=len(rows);AQ['storage_detail_added']=True;(O/'06_Report/V17_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(D/'Storage_Geometry_QA.json',O/'06_Report/V17_Storage_Design_Control.json');shutil.copy2(D/'Storage_Mutation.json',O/'08_Editable_Source/Storage_Mutation_V17.json')
for pp in W.glob('v17_*.py'):shutil.copy2(pp,O/'08_Editable_Source/V17_Scripts'/pp.name)
print('V17 STORAGE SAVED',len(F.Objects),len(rows),len(AQ['retained']),len(AQ['created']),len(AQ['deleted']),flush=True)
