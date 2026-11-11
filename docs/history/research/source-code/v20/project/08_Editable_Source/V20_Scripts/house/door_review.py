"""Independent read-only 90-degree inward-pose collision review of V20."""
import json,sys,ast,math,time
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
O=Path('E:/jz/JIA/Rebuild_V20');B=Path('E:/jz/JIA/Rebuild_V19')
Q=json.loads((W/'v20/Mutation.json').read_text(encoding='utf8'));QE={e['name']:e for e in Q['replace']+Q['add']}
M=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'helpers','exec'))
cache={};mesh_cache={};fallback=[];S=None
def native(n):
 if n not in mesh_cache:
  d=np.load(O/'02_Data'/ii[n]['file']);v=d['vertices'];f=d['faces'];mesh_cache[n]=(v,f,np.array([v.min(0),v.max(0)]))
 return mesh_cache[n]
def ms(v,f):
 vv,idx=np.unique(np.round(v,9),axis=0,return_inverse=True);return mf.Manifold(mf.Mesh(vert_properties=vv.astype(np.float32),tri_verts=idx[f].astype(np.uint32)))
def get(n):
 global S
 if n in cache:return cache[n]
 v,f,b=native(n);r=ms(v,f)
 if r.status()!=mf.Error.NoError:
  # Changed nodes' actual native cache is per-part in write order. Split it
  # by the author's triangle-count boundaries, then union those actual meshes.
  ee=QE.get(n)
  if ee and not ee.get('external_native_cache') and not ee.get('v20_native_cache_override'):
   parts=[];start=0
   for p in ee['parts']:
    g=oriented(p['geometry']);pv=np.array(g['vertices']);count=len(triangles(pv,g['faces']));ff=f[start:start+count];start+=count;rr=ms(v,ff);assert rr.status()==mf.Error.NoError,(n,'part',rr.status());parts.append(rr)
   assert start==len(f),(n,start,len(f));r=mf.Manifold.batch_boolean(parts,mf.OpType.Add)
  else:
   if S is None:
    S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
   ee=next(e for e in S['elements'] if e['name']==n);parts=[]
   for p in ex.expand_parts(ee):
    pv,pf=ex.world_part(p,ee);g={'type':'polyhedron','vertices':pv.tolist(),'faces':pf};parts.append(manifold(g))
   r=mf.Manifold.batch_boolean(parts,mf.OpType.Add);fallback.append({'name':n,'native_cache_status':str(ms(v,f).status()),'fallback':'Original unchanged source parts; actual cache volume verification remains root native QA responsibility'})
 assert r.status()==mf.Error.NoError,(n,r.status())
 cache[n]=r;return r
def bbox_overlap(a,b):return np.all(a[1]>b[0]+1e-6) and np.all(b[1]>a[0]+1e-6)
report={'status':'PASS_FINAL_NATIVE_INWARD_POSE_COLLISION_REVIEW','pose':'actual saved inward-open native cache; right inner gate 50 degrees, other leaves as recorded in saved Door Manifest','native_file':str(O/'04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm'),'native_index_modified_unix':(O/'02_Data/Native_Readback_Index_V20.json').stat().st_mtime,'assembly_report_modified_unix':(O/'06_Report/V20_Assembly_QA.json').stat().st_mtime,'door_count':len(M['doors']),'doors':[],'critical_collisions':[],'intentional_mechanical_contacts':[],'minor_hinge_or_frame_contacts':[],'unresolved':[],'fallbacks':fallback}
leaf_names={r['name'] for r in M['doors']};assert len(leaf_names)==27
skip_prefixes=('SITE_V14_ORIGINAL_EXTERIOR','CONTEXT','VIS_','REF_','GRID_')
physical=[]
for r in I:
 n=r['name']
 if n in leaf_names or n.startswith(skip_prefixes) or r['element'].get('family')=='VIS_MODEL' or not r['triangles']:continue
 # Bounding boxes can come from metadata, otherwise load on demand.
 b=r.get('actual_3dm_mesh_bbox_local')
 if b is None:b=native(n)[2]
 physical.append((n,np.asarray(b)))
for mr in M['doors']:
 n=mr['name'];v,f,b=native(n);dm=get(n);pivot=np.array(mr['hinge_local_m']);normal=np.r_[mr['inward_normal_local_xy'],0.];center=(b[0]+b[1])/2
 row={'name':n,'bounds_local_m':b.tolist(),'hinge_local_m':pivot.tolist(),'inward_normal_local':normal.tolist(),'open_angle_deg':mr['open_angle_deg'],'parent_door_id':mr.get('parent_door_id'),'leaf_center_distance_into_room_m':float(np.dot(center-pivot,normal)),'leaf_volume_m3':dm.volume(),'collisions':[]}
 assert row['leaf_center_distance_into_room_m']>.05,(n,row)
 for cn,cb in physical:
  if not bbox_overlap(b,cb):continue
  try:
   cm=get(cn);inter=dm^cm;vol=inter.volume()
   if vol<=1e-7:continue
   rr={'collider':cn,'intersection_volume_m3':vol,'door_volume_fraction':vol/dm.volume(),'intersection_bounds':list(inter.bounding_box())}
   row['collisions'].append(rr)
   # Minute hinge/frame overlap can be visually benign. Any large wall/column
   # overlap, or a significant glazing overlap, is a modeling problem.
   intentional=(n.startswith('SITE_SW_METAL_ENTRY_GATE_V11__LEAF_') and cn=='SITE_SW_GATE_FIXED_HINGE_HARDWARE')
   minor=(('__FRAME' in cn or '__FIXED' in cn) and vol<.0003 and vol/dm.volume()<.03)
   target='intentional_mechanical_contacts' if intentional else 'minor_hinge_or_frame_contacts' if minor else 'critical_collisions'
   report[target].append({'door':n,**rr,**({'reason':'Fixed hinge pins and moving hinge sleeves intentionally meet; root confirmed mechanical assembly contact'} if intentional else {})})
  except Exception as err:
   report['unresolved'].append({'door':n,'collider':cn,'error':str(err)})
 report['doors'].append(row);print('DOOR',n,'checks',sum(bbox_overlap(b,cb) for cn,cb in physical),'hits',len(row['collisions']),flush=True)
 # Leaf-vs-leaf checks only once, distinct from the wall review.
for a in M['doors']:
 for b in M['doors']:
  if a['name']>=b['name']:continue
  if not bbox_overlap(native(a['name'])[2],native(b['name'])[2]):continue
  m=get(a['name'])^get(b['name']);vol=m.volume()
  if vol>1e-7:report['critical_collisions'].append({'door':a['name'],'collider':b['name'],'intersection_volume_m3':vol,'intersection_bounds':list(m.bounding_box()),'kind':'door-to-door'})
if report['critical_collisions']:report['status']='FAIL_COLLISIONS_REQUIRING_GEOMETRY_FIX'
elif report['unresolved']:report['status']='INCOMPLETE_COLLISION_REVIEW'
(D/'Door_Review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL',report['status'],'critical',len(report['critical_collisions']),'unresolved',len(report['unresolved']),'minor',len(report['minor_hinge_or_frame_contacts']),'intentional_mechanical',len(report['intentional_mechanical_contacts']),flush=True)
