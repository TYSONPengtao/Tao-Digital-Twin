import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
ex.OUT=O/'08_Editable_Source';ex.SCENE=json.loads((ex.OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.MATS=ex.SCENE['materials']
qa=ex.make_rhino('ARCH')
(O/'06_Report/Editable_Local_Native_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
assert not qa['unexpected_open_solids']
print('RhinoCommon tolerance initialization required for faceted Breps before final QA',flush=True)
