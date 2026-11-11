"""Finish the compact sibling file when the earlier model is held open."""
import sys,json,hashlib,os,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path('E:/jz/JIA/Rebuild_V23');pending=O/'04_Rhino/Architecture_Complete_V23_COMPACT_PENDING.3dm';P=O/'04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm'
if pending.exists():os.replace(pending,P)
F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'));patch=json.loads((W/'v23_gate_roof_refit/Mutation.json').read_text(encoding='utf8'));names={e['name'] for e in patch['replace']}
def belongs(n):return any(n.startswith(a+'__') for a in names)
oldretained=[r for r in AQ['retained'] if belongs(r['name'])];AQ['deleted']+= [{'id':r['id'],'name':r['name']} for r in oldretained];AQ['retained']=[r for r in AQ['retained'] if not belongs(r['name'])]
AQ['superseded_during_v23']=[r for r in AQ.get('superseded_during_v23',[])]+[{'id':r['id'],'name':r['name']} for r in AQ['created'] if belongs(r['name'])]
AQ['created']=[r for r in AQ['created'] if not belongs(r['name'])]
groups={n:[] for n in names}
for ob in F.Objects:
 for n in names:
  if ob.Attributes.Name.startswith(n+'__'):groups[n].append(ob)
for n,obs in groups.items():
 for ob in obs:AQ['created'].append({'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'node':n,'geometry_hash':hashlib.sha256(json.dumps(ob.Geometry.Encode(),sort_keys=True).encode()).hexdigest(),'closed_expected':True})
rows=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'));rows=[r for r in rows if r['name'] not in names]
for n,obs in groups.items():
 fn='Native_Readback/NATIVE_'+n+'.npz';d=np.load(O/'02_Data'/fn);mats=list(dict.fromkeys(F.Materials[ob.Attributes.MaterialIndex].Name for ob in obs));meta=json.loads(obs[0].Attributes.GetUserString('Parameters'));meta['native_geometry_file']=fn
 rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(d['faces']),'native_objects':len(obs),'element':meta})
for fn in ['Native_Readback_Index_V23.json','Modeled_Index_V23.json']:(O/'02_Data'/fn).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
AQ.update(status='AWAITING_FRESH_READBACK',changed_nodes=sorted(set(AQ['changed_nodes'])|names),native_objects=len(F.Objects),final_model=str(P),earlier_locked_model_preserved=True)
(O/'06_Report/V23_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(W/'v23/Mutation.json',O/'08_Editable_Source/Mutation_V23.json')
print('COMPACT SIBLING FINALIZED',len(F.Objects),len(rows),hashlib.file_digest(P.open('rb'),'sha256').hexdigest(),flush=True)
