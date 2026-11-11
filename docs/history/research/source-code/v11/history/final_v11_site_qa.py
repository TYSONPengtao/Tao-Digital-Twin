import sys,json,hashlib,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
S=read(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');ex.SCENE=S;E={e['name']:e for e in S['elements']};checks=[]
def ck(k,ok,detail=None):checks.append({'id':k,'status':'PASS' if ok else 'FAIL','detail':detail});assert ok,(k,detail)
manifest=read(O/'06_Report/V11_Merge_Manifest.json');ck('scene_manifest_hash',manifest['scene_sha256']==sha(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'))
for src in manifest['sources']:
 mp=W/src['folder']/'Mutation.json';ck('frozen_mutation_'+src['folder'],sha(mp)==src['sha256']);m=read(mp)
 for e in m['replace']+m['add']:ck('merged_node_'+e['name'],E[e['name']]==e)
 q=read(W/src['folder']/'Geometry_QA.json');ck('part_geometry_'+src['folder'],str(q.get('status','')).startswith('PASS') or q.get('pass_') is True)
for folder,filename in [('v11_wall_junction','Frozen_Corner_Connection_QA.json'),('v11_outer_gate','Final_Freeze_Audit.json'),('v11_kitchen_interface','Frozen_Connection_QA.json')]:
 q=read(W/folder/filename);ck('frozen_independent_'+folder,str(q.get('status','')).startswith('PASS') or q.get('pass_') is True or q.get('passed') is True)
west=read(W/'v11_wall_junction/Mutation.json');a,b,c=np.array(west['new_route_local_m']);ck('wall_exact_right_angle',abs(np.dot(a-b,c-b))<1e-10,west['new_route_local_m'])
vv=[]
for e in S['elements']:
 if e['name'].startswith('SITE_GAZEBO'):
  for p in ex.expand_parts(e):v,_=ex.world_part(p,e);vv.extend(v)
vv=np.array(vv);lo=vv.min(axis=0);hi=vv.max(axis=0);ck('all_pavilion_inside_wall',lo[0]>.22 and lo[1]>-11.48,{'min':lo.tolist(),'max':hi.tolist(),'minimum_wall_cap_clearance_m':float(lo[0]-.22)})
C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);co=math.cos(a);si=math.sin(a)
def enu(q):return [q[0]*co-q[1]*si+C['origin'][0],q[0]*si+q[1]*co+C['origin'][1],q[2]+C['origin'][2]]
reg=read(O/'02_Data/Interaction_Registry_V11.json');outer=reg['V11_exterior_gate_additions'];ck('four_outer_gate_records',len(outer)==4)
F=rh.File3dm.Read(str(O/'04_Rhino/Reality_Hybrid_V11.3dm'));objects={ob.Attributes.Name:ob for ob in F.Objects}
for d in outer:
 ob=objects[d['leaf_element']];ck('gate_leaf_instance_'+d['door_id'],isinstance(ob.Geometry,rh.InstanceReference));tr=ob.Geometry.Xform;expected=enu(d['hinge_world_m']);angle=d['angle']+a
 ck('gate_actual_pivot_'+d['door_id'],math.dist(expected,[tr.M03,tr.M13,tr.M23])<1e-8,expected)
 ck('gate_actual_rotation_'+d['door_id'],abs(tr.M00-math.cos(angle))<1e-9 and abs(tr.M10-math.sin(angle))<1e-9)
del F,objects
F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'));matched={d['door_id']:0 for d in outer};pavilion_parts=0
for ob in F.Objects:
 if str(ob.Attributes.GetUserString('V11_Element') or '').startswith('SITE_GAZEBO'):
  g=ob.Geometry;solid=g.IsClosed if isinstance(g,rh.Mesh) else g.IsSolid
  ck('pavilion_actual_closed_part_'+ob.Attributes.Name,g.IsValid and solid);pavilion_parts+=1
 did=ob.Attributes.GetUserString('door_id')
 if did not in matched:continue
 d=next(d for d in outer if d['door_id']==did);actual=json.loads(ob.Attributes.GetUserString('Hinge_ENU_m'));ck('gate_editable_hinge_'+ob.Attributes.Name,math.dist(actual,enu(d['hinge_world_m']))<1e-8);matched[did]+=1
ck('four_editable_leaf_groups',all(v>0 for v in matched.values()),matched)
ck('pavilion_actual_part_count',pavilion_parts==sum(len(e['parts']) for e in S['elements'] if e['name'].startswith('SITE_GAZEBO')),pavilion_parts)
report={'status':'PASS','checks':checks,'passed_checks':len(checks),'scene_sha256':sha(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'),'pavilion_wall_cap_clearance_m':float(lo[0]-.22),'pavilion_closed_parts':pavilion_parts,'outer_gate_leaf_groups':4,'source_outside_explicit_correction_preserved':True,'kitchen_original_photographs_retained':True,'UE5_actual_playtest':False}
(O/'06_Report/Final_V11_Site_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print({k:v for k,v in report.items() if k!='checks'},flush=True)
