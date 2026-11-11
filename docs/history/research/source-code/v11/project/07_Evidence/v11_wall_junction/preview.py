import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex
O=Path(__file__).parent;M=json.loads((O/'Mutation.json').read_text(encoding='utf8'))
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf8'))
elements=M['replace']+M['add'];nodes=[]
for e in elements:
    by={}
    for p in e['parts']:
        vv,fs,_,_=ex.solid_data(p['geometry']);q=by.setdefault(p['material'],dict(name=e['name']+'__'+p['material'],vertices=[],faces=[],material=p['material']));off=len(q['vertices']);q['vertices']+=vv.tolist();q['faces'] += [[j+off for j in f] for f in fs]
    nodes+=list(by.values())
(O/'Preview_Mesh.json').write_text(json.dumps(dict(nodes=nodes,materials=S['materials']|M['materials']),separators=(',',':')),encoding='utf8')
print('previewmesh',len(nodes))
