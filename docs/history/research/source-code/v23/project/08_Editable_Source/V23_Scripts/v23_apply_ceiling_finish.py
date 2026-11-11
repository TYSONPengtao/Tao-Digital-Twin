"""Replace only the concealed ceiling disk in the already verified V23 file."""
from v23_common import *
import rhino3dm as rh,hashlib,shutil
O=Path('E:/jz/JIA/Rebuild_V23');P=O/'04_Rhino/Architecture_Complete_V23_ALIGNED_ENU.3dm'
F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'))
Q=json.loads((W/'v23/Mutation.json').read_text(encoding='utf8'));name='GATE_V22_PALE_CEILING_DISK'
e=next(e for e in Q['replace'] if e['name']==name)
assert len(e['parts'])==2 and e['centres_local_y_m']==[-12.,-11.12]
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
layers={l.Name:l.Index for l in F.Layers};mids={m.Name:i for i,m in enumerate(F.Materials)};created=AQ['created']
tree=ast.parse((W/'v23_assemble.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['sha','gh','uv_for','make','addmesh']],type_ignores=[]),'<native-mesh-writer>','exec'))
old=[ob for ob in F.Objects if ob.Attributes.Name.startswith(name+'__')];assert len(old)==1
oldids={str(ob.Attributes.Id) for ob in old};assert oldids.issubset({r['id'] for r in AQ['retained']})
for ob in old:
 AQ['deleted'].append({'id':str(ob.Attributes.Id),'name':ob.Attributes.Name});F.Objects.Delete(ob.Attributes.Id)
AQ['retained']=[r for r in AQ['retained'] if r['id'] not in oldids]
group=rh.Group();group.Name=name;gid=len(F.Groups);F.Groups.Add(group)
for j,p in enumerate(e['parts']):addmesh(name,e,make(p['geometry'],p['material'],name),p['material'],j,gid)
obs=[ob for ob in F.Objects if ob.Attributes.Name.startswith(name+'__')];vv=[];ff=[];uv=[];nn=[];mi=[];mats=[]
for ob in obs:
 mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
 if mat not in mats:mats.append(mat)
 off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
 for face in mm.Faces:ff.append((np.array(face[:3])+off).tolist());mi.append(mats.index(mat))
fn='Native_Readback/NATIVE_'+name+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));e['native_geometry_file']=fn
rows=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'))
rows=[r for r in rows if r['name']!=name]+[{'name':name,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(obs),'element':{k:v for k,v in e.items() if k not in ['parts','external_native_cache']}}]
SS=json.loads((O/'08_Editable_Source/Architecture_Scene_V23.json').read_text(encoding='utf8'));SS['elements']=[a for a in SS['elements'] if a['name']!=name]+[e];SS['v23_changes']=Q['change_notes'];sp=O/'08_Editable_Source/Architecture_Scene_V23.json';sp.write_text(json.dumps(SS,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V23_Editable_Scene_SHA256']=sha(sp)
assert F.Write(str(P),8)
for fn2 in ['Native_Readback_Index_V23.json','Modeled_Index_V23.json']:(O/'02_Data'/fn2).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
AQ.update(status='AWAITING_FRESH_READBACK',changed_nodes=sorted(set(AQ['changed_nodes'])|{name}),native_objects=len(F.Objects))
(O/'06_Report/V23_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(W/'v23/Mutation.json',O/'08_Editable_Source/Mutation_V23.json')
print('CEILING FINISH SAVED',len(F.Objects),len(rows),sha(P),flush=True)
