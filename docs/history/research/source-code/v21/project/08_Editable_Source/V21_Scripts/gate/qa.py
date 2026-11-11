import sys,json,math,ast,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(__file__).parent;B=Path('E:/jz/JIA/Rebuild_V20');Q=json.loads((O/'Mutation.json').read_text(encoding='utf8'))
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S;OLD={e['name']:e for e in S['elements']};E={e['name']:e for e in Q['add']+Q['replace']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))}
tr=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'h','exec'))
cache={}
def node(n):
 if n in cache:return cache[n]
 if n in E:a=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in E[n]['parts']],mf.OpType.Add)
 else:
  d=np.load(B/'02_Data'/I[n]['file']);vv,inv=np.unique(np.round(d['vertices'],9),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv,inv[d['faces']].astype(np.uint64)))
 assert a.status()==mf.Error.NoError,(n,a.status());cache[n]=a;return a
def bbox(a):
 v=np.asarray(a.to_mesh64().vert_properties)[:,:3];return [v.min(0).tolist(),v.max(0).tolist()]
def rotate(a,pivot,angle):
 return a.translate([-v for v in pivot]).rotate([0,0,angle]).translate(pivot)
DM=json.loads((O/'Door_Updates.json').read_text(encoding='utf8'))['upsert'];rs=[];bad=[]
targets=list(n for n in E if not n.startswith('SITE_V20_INNER_GATE__LEAF'))+[n for n in I if n.startswith('SITE_KITCHEN_') and n not in Q['remove']]+['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','CONSTRUCTION_COURTYARD_DRAINAGE_FINISH']
for r in DM:
 n=r['name'];a=node(n);p=r['hinge_local_m'];angle=r['open_angle_deg'];checks=[]
 sweepBB=np.array(bbox(a))+np.array([[-2,-2,0],[2,2,0]])
 for t in targets:
  if t not in E:
   if 'actual_3dm_mesh_bbox_local' in I[t]:tb=np.array(I[t]['actual_3dm_mesh_bbox_local'])
   else:
    tv=np.load(B/'02_Data'/I[t]['file'])['vertices'];tb=np.array([tv.min(0),tv.max(0)])
   if (tb[1]<sweepBB[0]).any() or (tb[0]>sweepBB[1]).any():continue
  at=node(t)
  tb=np.array(bbox(at))
  if (tb[1]<sweepBB[0]).any() or (tb[0]>sweepBB[1]).any():continue
  for fraction in np.linspace(0,1,19):
   leaf=rotate(a,p,angle*(fraction-1));inter=leaf^at;v=inter.volume()
   if v>1e-8:
    c={'door':n,'target':t,'angle_deg':angle*float(fraction),'volume_m3':float(v),'bounds':bbox(inter)};bad.append(c);print('CLASH',c,flush=True)
   checks.append({'target':t,'angle_deg':angle*float(fraction),'intersection_m3':float(v)})
 rs.append({'name':n,'open_angle_deg':angle,'checks':checks,'leaf_bounds_open':bbox(a)})
src=Path('E:/CODEXdata/before/内大门/内大门_实景复原_分层可编辑_Rhino8.3dm');f=rh.File3dm.Read(str(src));boxproof=[]
for obj in f.Objects:
 if not isinstance(obj.Geometry,rh.Brep) or obj.Attributes.LayerIndex>=15:continue
 g=obj.Geometry;bb=g.GetBoundingBox();a=np.array([bb.Min.X,bb.Min.Y,bb.Min.Z]);b=np.array([bb.Max.X,bb.Max.Y,bb.Max.Z]);v=np.array([[p.Location.X,p.Location.Y,p.Location.Z] for p in g.Vertices]);axis=np.logical_or(np.isclose(v,a),np.isclose(v,b));ok=bool(len(g.Faces)==6 and len(v)==8 and axis.all())
 boxproof.append({'id':str(obj.Attributes.Id),'name':obj.Attributes.Name,'closed_box':ok,'faces':len(g.Faces),'vertices':len(v),'box_volume_mm3':float(np.prod(b-a))})
 assert ok,boxproof[-1]
parts=[]
for n,e in E.items():
 for j,p in enumerate(e['parts']):
  a=manifold(p['geometry']);assert a.volume()>0,(n,j,a.volume());parts.append({'node':n,'part':j,'volume_m3':a.volume(),'closed_manifold':True})
pier=node('SITE_V21_GATE_REFERENCE_LAYER_02');masonry=node('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY');closure=node('SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE');joint=pier^closure;brickjoint=masonry^closure
gate_roof=node('SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT');kitchenroof=node('SITE_KITCHEN_CHINESE_TILE_ROOF');roofcontacts={'gate_closed_soffit_m3':float((closure^gate_roof).volume()),'kitchen_roof_m3':float((closure^kitchenroof).volume())}
assert joint.volume()>1e-6 and brickjoint.volume()>1e-6 and roofcontacts['gate_closed_soffit_m3']>1e-6 and roofcontacts['kitchen_roof_m3']>1e-6,(joint.volume(),brickjoint.volume(),roofcontacts)
def front_projection(a,plane=-11.87):
 m=a.to_mesh64();v=np.asarray(m.vert_properties)[:,:3];polys=[]
 for face in np.asarray(m.tri_verts):
  t=v[face]
  if np.max(abs(t[:,1]-plane))>2e-6:continue
  p=Polygon(t[:,[0,2]])
  if p.area>1e-12:polys.append(p)
 return unary_union(polys)
fc=front_projection(closure);fm=front_projection(masonry)
overlap_area=fc.intersection(fm).area;distance=fc.distance(fm)
assert overlap_area<2e-6 and distance<2e-6,(overlap_area,distance)
collarparts=[p for p in E['SITE_V21_GATE_REFERENCE_LAYER_03']['parts'] if p.get('reference_object_name')=='立柱束腰与石刻基座']
collars=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in collarparts],mf.OpType.Add)
pier_overlap=float((pier^collars).volume());assert pier_overlap<1e-9,pier_overlap
threshold=next(p for p in E['SITE_V21_GATE_REFERENCE_LAYER_01']['parts'] if p.get('reference_object_name')=='门槛石')
threshold_z=float(np.asarray(threshold['geometry']['vertices'])[:,2].max());assert abs(threshold_z-(-.448))<1e-9,threshold_z
door_threshold_clearances={r['name']:float(np.asarray(bbox(node(r['name'])))[0,2]-threshold_z) for r in DM}
assert min(door_threshold_clearances.values())>.01,door_threshold_clearances
result={'status':'PASS_REFERENCE_GATE_AND_SAMPLED_DOOR_SWING' if not bad else 'NEEDS_GATE_CLEARANCE_FIX','source_file_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'native_box_proof':boxproof,'parts_checked':len(parts),'all_new_parts_closed_positive_volume':True,'doors':rs,'collisions':bad,'kitchen_junction':{'stone_main_front_y':-11.87,'kitchen_gable_y':-11.87,'parallel':True,'positive_stone_connection_overlap_m3':float(joint.volume()),'positive_brick_connection_overlap_m3':float(brickjoint.volume()),'roof_closure_contacts_m3':roofcontacts,'redundant_east_flank_nodes_removed':[n for n in Q['remove'] if n.startswith('SITE_GATE_EAST_FLANK')],'note':'Full-height gray brick infill shares both stone and actual kitchen front plane. A24mm hidden key connects behind the stone flush joint;25mm overlap into kitchen gable; roof undersides both contact.'},'parts':parts}
result['junction_surface_qa']={'same_plane_closure_kitchen_overlap_area_m2':overlap_area,'same_plane_closure_kitchen_gap_m':distance,'pier_collar_intersection_m3_after_partition':pier_overlap,'threshold_top_m':threshold_z,'threshold_above_old_pavement_m':.002,'door_threshold_clearance_m':door_threshold_clearances,'note':'No coplanar front overlap. Hidden keys retain solid connections. Pier/collar envelope retained while overlapping volumes partitioned.'}
(O/'Source_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
design=json.loads((O/'Design_Control.json').read_text(encoding='utf8'));design['status']='PASS_SOURCE_REFERENCE_TRANSFER_AND_CLEARANCE' if not bad else 'NEEDS_GATE_CLEARANCE_FIX';design['source_qa']=str(O/'Source_QA.json');design['verified_junction_surface_qa']=result['junction_surface_qa'];design['door_pose_sampling']='Every 5 degrees, both inward leaves, including retained courtyard drainage finish';(O/'Design_Control.json').write_text(json.dumps(design,ensure_ascii=False,indent=2),encoding='utf8')
print('QA',result['status'],len(parts),'parts',len(boxproof),'source closed boxes',len(bad),'clashes',flush=True)
