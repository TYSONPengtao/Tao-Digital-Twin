import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v4_audit_junction')]
import apply_junction_v4 as J
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';S=json.loads(p.read_text(encoding='utf-8'));e=next(e for e in S['elements'] if e['name']=='CANOPY_FRONT_CLOSED_GABLE')
pitch=.9/3.525;offset=.1*math.sqrt(1+pitch*pitch);ridge=8.4-offset;edge=ridge-(6.5-3)*pitch
e['parts']=[J._part({'type':'prism','profile':[[3,-.218,7.37],[10,-.218,7.37],[10,-.218,edge],[6.5,-.218,ridge],[3,-.218,edge]],'vector':[0,.2,0]},'M_Wall_Exterior')]
e['status']='ONE_CAPPED_GABLE_SOLID; NO_INTERNAL_COINCIDENT_HALF_FACES'
p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/V7_Incremental_Nodes.json').write_text(json.dumps({'changed':[e['name']],'removed':[]},indent=2),encoding='utf-8')
print('Gable unified',ridge,edge,flush=True)
