"""Finish the small ground append with separate paving/soil hybrid materials."""
import sys,json,hashlib,ast,gc,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');D=W/'v11_ground_gap'
tree=ast.parse((W/'append_v11_ground_repair.py').read_text(encoding='utf8'));fun=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['read','save','sha','material_table','attr']];exec(compile(ast.Module(fun,type_ignores=[]),'<append_helpers>','exec'))
S=read(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');ex.SCENE=S;new=read(D/'Mutation.json')['add'];M=read(O/'02_Data/Materials.json');I=read(O/'02_Data/Patch_Index.json');C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);co,si=math.cos(a),math.sin(a);R=np.array([[co,-si,0],[si,co,0],[0,0,1]]);origin=np.array(C['origin']);added_parts=sum(len(e['parts']) for e in new);pieces={e['name']:[(j,None,p['material']) for j,p in enumerate(e['parts'])] for e in new}
for filename in ['V11_Changed_Wall_Solids_LOCAL.3dm','Architecture_Edit_V11_ALIGNED_ENU.3dm','Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm']:
 F=rh.File3dm.Read(str(O/'04_Rhino'/filename));assert sum(ob.Attributes.GetUserString('V11_Element') in pieces for ob in F.Objects)==added_parts;del F;gc.collect()
path=O/'04_Rhino/Reality_Hybrid_V11.3dm';F=rh.File3dm.Read(str(path));assert not any(ob.Attributes.Name.startswith(tuple(pieces)) for ob in F.Objects);mids=material_table(F);li=next(l.Index for l in F.Layers if l.Name=='PATCH_60_SITE');hybridadded=0
for e in new:
 row=next(r for r in I if r['name']==e['name']);d=np.load(O/'02_Data'/row['file']);v=d['vertices']@R.T+origin;faces=d['faces'];uv=d['uv'];mid=d['material_ids'];gr=rh.Group();gr.Name=e['name'];gi=len(F.Groups);F.Groups.Add(gr)
 for mi,material in enumerate(row['materials']):
  ff=faces[mid==mi];ids=np.unique(ff);remap=np.full(len(v),-1,np.int32);remap[ids]=np.arange(len(ids));mesh=rh.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True
  for q in v[ids]:mesh.Vertices.AddPoint3d(*map(float,q))
  for f in remap[ff]:mesh.Faces.AddFace(*map(int,f))
  mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));mesh.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
  for j,q in enumerate(uv[ids]):mesh.TextureCoordinates[j]=rh.Point2f(*map(float,q))
  mesh.Normals.ComputeNormals();assert mesh.IsValid;at=attr(e,0,li,mids[material]);at.Name=e['name']+'__'+material;at.SetUserString('PatchRole',row['role']);at.AddToGroup(gi);F.Objects.AddMesh(mesh,at);hybridadded+=1
assert F.Write(str(path),8);print('Ground hybrid append',hybridadded,'material meshes',flush=True);del F;gc.collect()
q=read(O/'06_Report/Changed_CAD_Conversion_QA.json');assert 'closed_ground_repair_parts' not in q;q['parts']+=added_parts;q['types']['Mesh']+=added_parts;q['closed_ground_repair_parts']=added_parts;save(O/'06_Report/Changed_CAD_Conversion_QA.json',q)
q=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');q['changed_native_solids']+=added_parts;q['walls_only_objects']+=added_parts;q['sha256']=sha(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm');q['site_only_sha256']=sha(O/'04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm');save(O/'06_Report/Editable_Rhino_Alignment_QA.json',q)
q=read(O/'06_Report/Native_Hybrid_QA.json');q['total_objects']+=hybridadded;q['counts']['patch_meshes']+=hybridadded;q['ground_gap_repairs']=len(new);save(O/'06_Report/Native_Hybrid_QA.json',q)
guide=O/'使用说明.md';guide.write_text(guide.read_text(encoding='utf8')+'\n最终覆盖检查另补了亭旁及墙脚约2.38平方米局部露空地坪，沿用相邻保留地坪标高与坡面；未修改原实景网格或贴图。\n',encoding='utf8');print('Ground repair finished',len(new),'nodes',added_parts,'closed slabs',flush=True)
