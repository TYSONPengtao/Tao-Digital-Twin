import sys,json,math,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex,numpy as np,rhino3dm as rh
P=Path(r'E:\jz\JIA\Rebuild_V12');O=W/'v13_structure';O.mkdir(exist_ok=True)
S=json.loads((P/'08_Editable_Source/Architecture_Scene_V12.json').read_text(encoding='utf8'));ex.SCENE=S
C=json.loads((P/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
scene={e['name']:e for e in S['elements']};f=rh.File3dm.Read(str(P/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm'))
print('loaded',len(f.Objects),flush=True);obs=collections.defaultdict(list)
for ob in f.Objects:
 if ob.Attributes.IsInstanceDefinitionObject:continue
 n=ob.Attributes.Name;base=n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
 obs[base].append(ob)
results=[]
for n,e in scene.items():
 vv=[]
 for part in ex.expand_parts(e):
  v,fs=ex.world_part(part,e)
  if v is not None:vv.append(v)
 if not vv:continue
 v=np.concatenate(vv);ve=v@R.T+origin;expected=np.array([ve.min(0),ve.max(0)]);b=[]
 for ob in obs[n]:
  if isinstance(ob.Geometry,rh.InstanceReference):continue
  bb=ob.Geometry.GetBoundingBox();b.extend([[bb.Min.X,bb.Min.Y,bb.Min.Z],[bb.Max.X,bb.Max.Y,bb.Max.Z]])
 if b:
  b=np.array(b);actual=np.array([b.min(0),b.max(0)]);err=float(np.max(abs(actual-expected)))
  results.append({'name':n,'parts_native':len(obs[n]),'parts_scene':len(ex.expand_parts(e)),'bbox_error_m':err,'expected_enu':expected.tolist(),'actual_enu':actual.tolist(),'scene_local':[v.min(0).tolist(),v.max(0).tolist()]})
results.sort(key=lambda r:-r['bbox_error_m']);(O/'Native_Scene_Parity_V12.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'objects_checked':sum(r['parts_native'] for r in results),'nodes':len(results),'mismatches_over_1mm':sum(r['bbox_error_m']>.001 for r in results),'worst':results[:24]},ensure_ascii=False,indent=2),flush=True)
