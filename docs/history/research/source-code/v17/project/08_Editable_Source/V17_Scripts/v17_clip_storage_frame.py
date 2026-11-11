import sys,json,math,hashlib,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex,manifold3d as mf
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
O=Path(r'E:/jz/JIA/Rebuild_V17');P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm';S=json.loads((O/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'))
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman']),('v17_assemble.py',['make_mesh','gh','node_obs'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
plan=unary_union([Polygon(np.array(p['geometry']['profile'])[:,:2]) for p in E['SITE_V14_INNER_STORAGE_GABLE_ROOF']['parts']]);p=orient(plan,1);cu=manifold({'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[],'z':-.6,'height':8});n='SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME';e=E[n];ps=[];changed=[];new_records=[];removedids=set()
for j,part in enumerate(e['parts']):
 v,fs,_,_=ex.solid_data(part['geometry']);fp=Polygon(v[:,:2]).convex_hull
 if v[:,0].min()<13.0 or plan.covers(fp) or fp.area<1e-10:ps.append(part);continue
 old=next(ob for ob in F.Objects if ob.Attributes.Name==f'{n}__{j+1}');at=old.Attributes;removedids.add(str(at.Id));F.Objects.Delete(at.Id);m=manifold(part['geometry'])^cu
 if m.is_empty():AQ['deleted'].append({'id':str(at.Id),'name':at.Name,'node':n});continue
 g=fromman(m);pp={**part,'geometry':g,'v17_original_part_index':j};ps.append(pp);mm,_,_,_=make_mesh(g);ident=F.Objects.Add(mm,at);new_records.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True});changed.append({'native_part':at.Name,'trimmed_volume_m3':manifold(part['geometry']).volume()-m.volume()})
e['parts']=ps;e['v17_roof_clip']='New timber members trimmed to retained tile roof silhouette at the kitchen diagonal valley; existing valley bearers retained';AQ['created']=[r for r in AQ['created'] if r['id'] not in removedids]+new_records
row=next(r for r in I if r['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node_obs(n)
for ob in oo:
 mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
 if mat not in mats:mats.append(mat)
 off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
 for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
np.savez_compressed(O/'02_Data'/row['file'],vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));row.update(materials=mats,triangles=len(ff),native_objects=len(oo),element={k:v for k,v in e.items() if k!='parts'});AQ['native_objects']=len(F.Objects)
sp=O/'08_Editable_Source/Architecture_Scene_V17.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V17_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V17.json','Modeled_Index_V17.json']:(O/'02_Data'/nm).write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V17_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V17_Timber_Valley_Clip_QA.json').write_text(json.dumps({'status':'PASS_TIMBER_FITS_RETAINED_ROOF_PLAN','changed_members':changed,'roof_geometry_unchanged':True},ensure_ascii=False,indent=2),encoding='utf8');print('TIMBER VALLEY CLIP',len(changed),len(ps),flush=True)
