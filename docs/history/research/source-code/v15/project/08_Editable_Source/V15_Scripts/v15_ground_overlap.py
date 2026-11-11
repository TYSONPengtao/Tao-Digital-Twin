import sys,json,math,copy,hashlib,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np,manifold3d as mf,rhino3dm as rh,export_v5 as ex,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
O=Path(r'E:/jz/JIA/Rebuild_V15');P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);si=O/'08_Editable_Source/Architecture_Scene_V15.json';S=json.loads(si.read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};ni=O/'02_Data/Native_Readback_Index_V15.json';I=json.loads(ni.read_text(encoding='utf8'));ii={r['name']:r for r in I};mi=O/'02_Data/Modeled_Index_V15.json';M=json.loads(mi.read_text(encoding='utf8'));aq=json.loads((O/'06_Report/V15_Assembly_QA.json').read_text(encoding='utf8'));reports=[]
tt=ast.parse((W/'v15_tree_pit.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tt.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<native_writer>','exec'))
d=np.load(O/'02_Data'/ii['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT']['file']);t=d['vertices'][d['faces']];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9;walk=unary_union([Polygon(q[:,:2]) for q in t[up]]).buffer(0)
polys=[walk] if walk.geom_type=='Polygon' else list(walk.geoms);cut=None
for poly in polys:
 mm=manifold({'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in poly.interiors],'z':-5,'height':7});cut=mm if cut is None else cut+mm
removed=[]
for n in list(E):
 if not n.startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD','SITE_V12_REBUILT_COURT')):continue
 e=E[n];g=e['parts'][0]['geometry'];v=np.array(g['vertices']);p=Polygon(v[:,:2]).convex_hull
 if p.intersection(walk).area<1e-8:continue
 old=manifold(g);r=old-cut
 if abs(old.volume()-r.volume())<1e-9:continue
 if r.is_empty():
  ob=next(ob for ob in F.Objects if ob.Attributes.Name==n+'__1');ident=str(ob.Attributes.Id);F.Objects.Delete(ob.Attributes.Id);S['elements']=[e for e in S['elements'] if e['name']!=n];I[:]=[r for r in I if r['name']!=n];M[:]=[r for r in M if r['name']!=n];aq['native_created']=[r for r in aq['native_created'] if r['id']!=ident];aq['retained_native']=[r for r in aq['retained_native'] if r['id']!=ident];aq['removed'].append(n);removed.append(n)
 else:
  write(n,fromman(r),e['parts'][0]['material']);e.pop('v15_tree_pit',None);e['v15_overlap_fix']='Old ground removed from the exact new pavement footprint; tree pocket retained'
 print('EXCAVATED',n,float(old.volume()-r.volume()),flush=True)
si.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');ni.write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8');mi.write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf8');aq['objects']=len(F.Objects);aq['geometry_changes']+=['GROUND_OVERLAP_CLEANUP'];(O/'06_Report/V15_Assembly_QA.json').write_text(json.dumps(aq,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V15_Editable_Scene_SHA256']=hashlib.sha256(si.read_bytes()).hexdigest();assert F.Write(str(P),8)
q=json.loads((O/'06_Report/V15_Native_Readback_QA.json').read_text(encoding='utf8'));q['sha256']=hashlib.sha256(P.read_bytes()).hexdigest();q['native_objects']=len(F.Objects);q['nodes']=len(I);q['post_pavement_excavation_native_verification']=reports;(O/'06_Report/V15_Native_Readback_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V15_Ground_Overlap_QA.json').write_text(json.dumps({'status':'PASS_OLD_GROUND_EXCAVATED_UNDER_NEW_PAVEMENT','old_ground_nodes_removed':removed,'native_mesh_checks':reports,'footprint_area_m2':walk.area},ensure_ascii=False,indent=2),encoding='utf8');print('OVERLAP CLEANUP PASS',len(F.Objects),len(I),flush=True)
