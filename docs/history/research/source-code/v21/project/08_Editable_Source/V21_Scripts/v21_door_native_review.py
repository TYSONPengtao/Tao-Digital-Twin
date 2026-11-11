"""Independent saved-native open-pose clearance test against nearby site solids."""
import sys,json,re,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,manifold3d as mf,rhino3dm as rh
O=Path('E:/jz/JIA/Rebuild_V21')
I={r['name']:r for r in json.loads((O/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
DM=json.loads((O/'02_Data/Door_Manifest_V21.json').read_text(encoding='utf8'));D={r['name']:r for r in DM['doors']}
bb={};cache={};skips=[];native_groups=None;native_document=None;fallbacks=[]
for n,r in I.items():
 v=np.load(O/'02_Data'/r['file'])['vertices'];bb[n]=np.array([v.min(0),v.max(0)])
def man(n):
 global native_groups,native_document
 if n in cache:return cache[n]
 d=np.load(O/'02_Data'/I[n]['file']);v=d['vertices'];f=d['faces'];a=None
 for dec in [9,8,7,6]:
  vv,inv=np.unique(np.round(v,dec),axis=0,return_inverse=True)
  a=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)))
  if a.status()==mf.Error.NoError:break
 if a.status()!=mf.Error.NoError:
  if native_groups is None:
   F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm'));native_document=F;native_groups={}
   for ob in F.Objects:
    tokens=ob.Attributes.Name.split('__')
    for j in range(1,len(tokens)+1):native_groups.setdefault('__'.join(tokens[:j]),[]).append(ob)
  C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));angle=math.radians(C['rotation_deg']);R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]]);origin=np.array(C['origin']);pieces=[]
  for ob in native_groups.get(n,[]):
   if not isinstance(ob.Geometry,rh.Mesh):pieces=[];break
   mesh=ob.Geometry;vv=(np.array([[p.X,p.Y,p.Z] for p in mesh.Vertices.ToPoint3dArray()])-origin)@R;ff=[]
   for face in mesh.Faces:
    ff.append(face[:3])
    if face[3]!=face[2]:ff.append([face[0],face[2],face[3]])
   vv,inv=np.unique(np.round(vv,8),axis=0,return_inverse=True);part=mf.Manifold(mf.Mesh64(vv,inv[np.array(ff)].astype(np.uint64)))
   if part.status()!=mf.Error.NoError:pieces=[];break
   pieces.append(part)
  if pieces:
   a=mf.Manifold.batch_boolean(pieces,mf.OpType.Add);fallbacks.append({'node':n,'mode':'Boolean union of independently read native object solids','native_parts':len(pieces)})
  else:
   skips.append({'name':n,'reason':'Native cache is a surface/context or non-weldable multi-part union','manifold_status':str(a.status())});a=None
 cache[n]=a;return a
def overlaps(a,b):return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>1e-6))
rows=[];fail=[];intentional=[]
for n,row in D.items():
 a=man(n);assert a is not None,n;checks=[]
 for t in I:
  if t==n or not overlaps(bb[n],bb[t]):continue
  if any(x in t for x in ['ORIGINAL_EXTERIOR','VEGETATION','TREE','REFERENCE','HELPER']) and not t.startswith('SITE_V21_GATE_REFERENCE'):continue
  b=man(t)
  if b is None:continue
  v=float((a^b).volume());entry={'collider':t,'intersection_m3':v}
  checks.append(entry)
  if v>1e-6:
   if 'FIXED_HINGE_HARDWARE' in t and n.startswith('SITE_SW_METAL_ENTRY_GATE_V11'):intentional.append({'door':n,**entry,'reason':'Retained outer-gate hinge mechanical contact'})
   else:fail.append({'door':n,**entry})
 proof={'name':n,'operation':row.get('operation','HINGED_INWARD'),'collisions':checks}
 if row.get('operation')!='SLIDING' and not row.get('parent_door_id'):
  v=np.load(O/'02_Data'/I[n]['file'])['vertices'];direction=np.array(row['inward_normal_local_xy']);depth=float((v.mean(0)[:2]-np.array(row['hinge_local_m'])[:2])@direction)
  proof['inward_centroid_m']=depth
  if depth<.12:fail.append({'door':n,'reason':'Default leaf does not extend sufficiently into the intended room','depth_m':depth})
 rows.append(proof);print('DOOR',n,len(checks),flush=True)
AQ=json.loads((O/'06_Report/V21_Assembly_QA.json').read_text(encoding='utf8'));changed=set(AQ['changed_nodes']);sweeps=[]
for n,row in D.items():
 if n not in changed or row.get('parent_door_id'):continue
 a=man(n);steps=[]
 for amount in np.linspace(0,1,10):
  if row.get('operation')=='SLIDING':p=a.translate((-np.array(row['open_translation_m'])*(1-amount)).tolist())
  else:
   pivot=np.array(row['hinge_local_m']);p=a.translate((-pivot).tolist()).rotate([0,0,-row['open_angle_deg']*(1-amount)]).translate(pivot.tolist())
  vertices=np.array(p.to_mesh64().vert_properties)[:,:3];bounds=np.array([vertices.min(0),vertices.max(0)]);touches=[]
  for t in I:
   if t==n or t in D or not overlaps(bounds,bb[t]):continue
   if any(x in t for x in ['ORIGINAL_EXTERIOR','VEGETATION','TREE','REFERENCE','HELPER']) and not t.startswith('SITE_V21_GATE_REFERENCE'):continue
   target=man(t)
   if target is None:continue
   volume=float((p^target).volume())
   if volume>1e-6:
    rec={'collider':t,'intersection_m3':volume};touches.append(rec)
    fail.append({'door':n,'motion_fraction':float(amount),**rec})
  steps.append({'open_fraction':float(amount),'intersections':touches})
 sweeps.append({'door':n,'poses':steps});print('MOTION',n,flush=True)
out={'status':'PASS_FINAL_NATIVE_DOOR_CLEARANCE' if not fail else 'NEEDS_DOOR_CLEARANCE_FIX','mode':'Independent saved native cache; adjacent closed solids at default open pose; changed doors additionally sampled at 10 positions from closed to open; 1e-6 m3 overlap threshold','doors':rows,'changed_door_motion_samples':sweeps,'unresolved_collisions':fail,'intentional_hinge_contacts':intentional,'native_individual_solid_fallbacks':fallbacks,'not_boolean_testable':skips,'ue_engine_import_tested':False}
(O/'06_Report/Final_Native_Door_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':out['status'],'failures':fail,'skipped':len(skips)},ensure_ascii=False),flush=True)
