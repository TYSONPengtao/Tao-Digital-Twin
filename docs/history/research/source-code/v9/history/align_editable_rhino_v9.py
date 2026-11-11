"""Align editable V5 Rhino Breps/blocks to the original ENU site.
This is an editing companion, not a second replacement of the intact source.
"""
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');V5=O/'08_Editable_Source'
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));S=json.loads((V5/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
F=rh.File3dm.Read(str(V5/'06_Rhino/Production_1QK_ARCH.3dm'));a=math.radians(C['rotation_deg']);origin=C['origin']
rot=rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0));T=rh.Transform.Multiply(rh.Transform.Translation(*origin),rot)
transformed=0
for ob in F.Objects:
 if ob.Attributes.IsInstanceDefinitionObject:continue
 assert ob.Geometry.Transform(T),ob.Attributes.Name
 ob.Attributes.SetUserString('CoordinateFrame','ENU; editable source parameter values remain V9 LOCAL')
 transformed+=1
proposal=rh.Layer();proposal.Name='CONSTRUCTION_PROPOSALS_HIDDEN';proposal.Color=(220,145,65,255);proposal.Visible=False;pi=F.Layers.Add(proposal)
for ob in F.Objects:
 if not ob.Attributes.IsInstanceDefinitionObject and ob.Attributes.Name.startswith('CONSTRUCTION_'):ob.Attributes.LayerIndex=pi
for ly in F.Layers:
 if ly.Name in ['99_HELPER','90_UNCERTAIN','01_GRID','02_LEVEL']:
  ly.Visible=False
for vi in list(F.Views)+list(F.NamedViews):
 vp=vi.Viewport;p=vp.CameraLocation;q=rh.Point3d(p.X,p.Y,p.Z);q.Transform(T);vp.SetCameraLocation(q)
 d=vp.CameraDirection;v=rh.Vector3d(d.X,d.Y,d.Z);v.Transform(rot);vp.SetCameraDirection(v)
 up=vp.CameraUp;u=rh.Vector3d(up.X,up.Y,up.Z);u.Transform(rot);vp.SetCameraUp(u)
F.Strings['AlignmentToHybrid']=json.dumps(C,ensure_ascii=False);F.Strings['Usage']='Editing companion in same ENU as Reality_Hybrid_V9.3dm; toggle instead of overlaying duplicate visible architectural surfaces. Site components visible for editing the V9 eave joint; hybrid file governs final source preservation and patch scope.'
p=O/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm';assert F.Write(str(p),8)
G=rh.File3dm.Read(str(p));invalid=[o.Attributes.Name for o in G.Objects if not o.Geometry.IsValid]
reg={r['leaf_element']:r for r in S['door_registry'] if r.get('leaf_element')};doors=[]
for ob in G.Objects:
 if ob.Attributes.IsInstanceDefinitionObject or ob.Attributes.Name not in reg:continue
 h=reg[ob.Attributes.Name]['hinge_world_m'];q=rh.Point3d(*h);q.Transform(T);t=ob.Geometry.Xform;err=math.dist([q.X,q.Y,q.Z],[t.M03,t.M13,t.M23]);assert err<1e-8
 doors.append({'leaf':ob.Attributes.Name,'door_id':reg[ob.Attributes.Name]['door_id'],'hinge_ENU_m':[t.M03,t.M13,t.M23],'alignment_error_m':err})
assert len(doors)==13;assert not invalid
report={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'root_objects_transformed':transformed,'invalid':invalid,'independent_hinged_door_leaves':len(doors),'doors':doors,'coordinate':'Original ENU, metres, Z up','editing_companion_only':True,'source_V5_untouched':True}
(O/'06_Report/Editable_Rhino_Alignment_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
