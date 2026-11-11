"""Apply the user's final compact-eave correction to saved V23 geometry."""
from v23_common import *
import rhino3dm as rh,hashlib,shutil
O=Path('E:/jz/JIA/Rebuild_V23');P=O/'04_Rhino/Architecture_Complete_V23_ALIGNED_ENU.3dm'
F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'))
Q=json.loads((W/'v23/Mutation.json').read_text(encoding='utf8'));patch=json.loads((W/'v23_gate_roof_refit/Mutation.json').read_text(encoding='utf8'));names={e['name'] for e in patch['replace']};assert len(names)==9 and not patch['add']
Q['replace']=[e for e in Q['replace'] if e['name'] not in names]+patch['replace'];Q['change_notes']+=patch['change_notes']
(W/'v23/Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
layers={l.Name:l.Index for l in F.Layers};mids={m.Name:i for i,m in enumerate(F.Materials)}
tree=ast.parse((W/'v23_assemble.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','gh','uv_for','make','addmesh']],type_ignores=[]),'<native-mesh-writer>','exec'))
old=[ob for ob in F.Objects if any(ob.Attributes.Name.startswith(n+'__') for n in names)];ids={str(ob.Attributes.Id) for ob in old};retainedids={r['id'] for r in AQ['retained']}
for ob in old:
 row={'id':str(ob.Attributes.Id),'name':ob.Attributes.Name}
 if row['id'] in retainedids:AQ['deleted'].append(row)
 else:AQ.setdefault('superseded_during_v23',[]).append(row)
 F.Objects.Delete(ob.Attributes.Id)
AQ['retained']=[r for r in AQ['retained'] if r['id'] not in ids];AQ['created']=[r for r in AQ['created'] if r['id'] not in ids];created=AQ['created']
rows=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'));rows=[r for r in rows if r['name'] not in names]
for e in patch['replace']:
 n=e['name'];group=rh.Group();group.Name=n;gid=len(F.Groups);F.Groups.Add(group)
 for j,p in enumerate(e['parts']):addmesh(n,e,make(p['geometry'],p['material'],n),p['material'],j,gid)
 obs=[ob for ob in F.Objects if ob.Attributes.Name.startswith(n+'__')];vv=[];ff=[];uv=[];nn=[];mi=[];mats=[]
 for ob in obs:
  mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for face in mm.Faces:ff.append((np.array(face[:3])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));e['native_geometry_file']=fn
 rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(obs),'element':{k:v for k,v in e.items() if k not in ['parts','external_native_cache']}})
 print('COMPACT ROOF',n,len(obs),flush=True)
SS=json.loads((O/'08_Editable_Source/Architecture_Scene_V23.json').read_text(encoding='utf8'));SS['elements']=[a for a in SS['elements'] if a['name'] not in names]+patch['replace'];SS['v23_changes']=Q['change_notes'];sp=O/'08_Editable_Source/Architecture_Scene_V23.json';sp.write_text(json.dumps(SS,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V23_Editable_Scene_SHA256']=sha(sp)
tmp=P.with_name('Architecture_Complete_V23_COMPACT_PENDING.3dm')
assert F.Write(str(tmp),8),'Cannot write new compact model to fresh sibling file'
import os
os.replace(tmp,P)
for fn2 in ['Native_Readback_Index_V23.json','Modeled_Index_V23.json']:(O/'02_Data'/fn2).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
AQ.update(status='AWAITING_FRESH_READBACK',changed_nodes=sorted(set(AQ['changed_nodes'])|names),native_objects=len(F.Objects))
(O/'06_Report/V23_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(W/'v23/Mutation.json',O/'08_Editable_Source/Mutation_V23.json')
print('COMPACT ROOF SAVED',len(F.Objects),len(rows),sha(P),flush=True)
