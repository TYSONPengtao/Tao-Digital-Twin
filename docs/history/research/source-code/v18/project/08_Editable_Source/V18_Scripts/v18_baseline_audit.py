import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import rhino3dm as rh
B=Path(r'E:/jz/JIA/Rebuild_V17');F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'));I=json.loads((B/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));AQ=json.loads((B/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));obs={str(o.Attributes.Id):o for o in F.Objects};q={r['id']:r for r in AQ['retained']+AQ['created']};bad=[];missing=[]
for r in I:
 oo=[o for o in F.Objects if o.Attributes.Name==r['name'] or o.Attributes.Name.startswith(r['name']+'__')]
 if not oo:missing.append(r['name'])
for id,ob in obs.items():
 h=hashlib.sha256(json.dumps(ob.Geometry.Encode(),sort_keys=True).encode()).hexdigest()
 if id not in q or h!=q[id]['geometry_hash']:bad.append({'id':id,'name':ob.Attributes.Name,'geometry_type':type(ob.Geometry).__name__})
result={'baseline_native_objects':len(F.Objects),'last_delivered_objects':AQ['native_objects'],'cache_nodes_missing_from_current_native':missing,'changed_current_geometries_vs_last_delivery':bad,'missing_current_native_objects_vs_last_delivery':[r['name'] for id,r in q.items() if id not in obs]};print(json.dumps(result,ensure_ascii=False,indent=2),flush=True);(W/'v18/Baseline_Audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
