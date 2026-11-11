import json,math
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';S=json.loads(p.read_text(encoding='utf-8'))
profile=[[6.5+.09*math.cos(a),-.82,8.4+.095*math.sin(a)] for a in [j*math.pi/16 for j in range(17)]]
e=dict(name='CANOPY_CENTER_RIDGE_CAP',layer='50_ROOF',family='ARCH_MODEL',parts=[dict(geometry=dict(type='prism',profile=profile,vector=[0,2.94,0]),material='M_Stone')],source='DJI 0002/DJI_0429.JPG; rounded ridge cap at canopy join',confidence='MEDIUM',status='PHOTO_SUPPORTED_RIDGE_CLOSURE; PROFILE_ESTIMATED')
S['elements'].append(e);S['v7_changes'].append(dict(id='V7_CANOPY_RIDGE_CLOSURE',elements=[e['name']],description='小坡屋顶中央加盖脊盖，遮蔽两坡接头及端部小空隙',evidence=['DJI 0002/DJI_0429.JPG'],metric_status='PHOTO_ESTIMATED_PROFILE'))
p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8');(O/'06_Report/Changes_V7.json').write_text(json.dumps(S['v7_changes'],ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/V7_Incremental_Nodes.json').write_text(json.dumps({'changed':[e['name']],'removed':[]},indent=2),encoding='utf-8')
c=json.loads((O/'02_Data/V7_Changed_Nodes.json').read_text());c['changed'].append(e['name']);(O/'02_Data/V7_Changed_Nodes.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
print('Centre ridge closure added',flush=True)
