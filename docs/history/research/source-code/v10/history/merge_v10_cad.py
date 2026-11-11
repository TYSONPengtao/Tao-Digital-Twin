import sys,json,math,hashlib,collections,gc
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');B=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa=read(O/'06_Report/Changed_CAD_Kernel_QA.json');assert qa['status']=='PASS';assert qa['sha256']==sha(O/'04_Rhino/V10_Changed_Wall_Solids_LOCAL.3dm')
baseline=B/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm';assert sha(baseline)==read(O/'06_Report/V10_Baseline_Hashes.json')['baseline_editable_sha256']
F=rh.File3dm.Read(str(baseline));G=rh.File3dm.Read(str(O/'04_Rhino/V10_Changed_Wall_Solids_LOCAL.3dm'))
change=read(O/'02_Data/V10_Changed_Nodes.json');changed=set(change['changed']);retire=changed|set(change['removed'])
removed=[]
for ob in list(F.Objects):
 if not ob.Attributes.IsInstanceDefinitionObject and any(ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__') for n in retire):removed.append(str(ob.Attributes.Id));F.Objects.Delete(ob.Attributes.Id)
mids={m.Name:i for i,m in enumerate(F.Materials)}
for m in G.Materials:
 if m.Name not in mids:mids[m.Name]=F.Materials.Add(m)
li=next(l.Index for l in F.Layers if l.Name=='60_SITE');C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);rot=rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0));T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rot)
groupids={}
for group in G.Groups:
 gr=rh.Group();gr.Name=group.Name;groupids[group.Index]=len(F.Groups);F.Groups.Add(gr)
for ob in G.Objects:
 at=ob.Attributes;gis=at.GetGroupList();at.RemoveFromAllGroups()
 for gi in gis:at.AddToGroup(groupids[gi])
 at.LayerIndex=li;at.MaterialIndex=mids[G.Materials[at.MaterialIndex].Name];at.SetUserString('CoordinateFrame','ENU; V10 detail parameters in LOCAL metres')
 assert ob.Geometry.Transform(T);F.Objects.Add(ob.Geometry,at)
F.Strings['Usage']='V10 incremental native editable architectural solids; V9 non-wall objects preserved. Same original ENU as hybrid. Individual courtyard tile, brick, molding and flower units editable.'
p=O/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm';assert F.Write(str(p),8)
del F,G;gc.collect()
G2=rh.File3dm.Read(str(p));bad=[ob.Attributes.Name for ob in G2.Objects if not ob.Geometry.IsValid];opens=[ob.Attributes.Name for ob in G2.Objects if ob.Attributes.GetUserString('V10_Element') and ((isinstance(ob.Geometry,(rh.Brep,rh.Extrusion)) and not ob.Geometry.IsSolid) or (isinstance(ob.Geometry,rh.Mesh) and not ob.Geometry.IsClosed))];assert not bad and not opens
total_edit_objects=len(G2.Objects)
S=read(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');wall_names=set(changed)|{'SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_WHITE_INSIDE','SITE_GATE_EAST_FLANK','SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1'}
H=G2;keep=[]
for ob in list(H.Objects):
 if ob.Attributes.IsInstanceDefinitionObject or not any(ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__') for n in wall_names):H.Objects.Delete(ob.Attributes.Id)
 else:keep.append(ob.Attributes.Name)
H.Strings['Usage']='V10 wall-only native solids in original ENU; reference construction dimensions not field certified. Existing gate openings retained. Use instead of duplicate wall surfaces in the whole architecture companion.'
hp=O/'04_Rhino/Courtyard_Walls_V10_ALIGNED_ENU.3dm';assert H.Write(str(hp),8)
save(O/'06_Report/Editable_Rhino_Alignment_QA.json',{'status':'PASS','path':str(p),'sha256':sha(p),'invalid':bad,'open_changed_solids':opens,'changed_native_solids':qa['parts'],'old_objects_removed':len(removed),'retained_old_object_ids':total_edit_objects-qa['parts'],'walls_only_path':str(hp),'walls_only_objects':len(keep),'units':'Metres, original ENU, Z up','incremental_from_exact_V9':True})
print('Merged CAD',total_edit_objects,'objects;',len(keep),'wall objects; all changed closed and valid',flush=True)
