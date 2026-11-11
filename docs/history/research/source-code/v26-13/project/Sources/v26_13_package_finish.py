from pathlib import Path
import json,runpy
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_13')
p=O/'Reports/V26_13_Runtime_Viewport_QA.json';q=json.loads(p.read_text('utf8'))
for c in q['checks']:
 if c['check']=='Controller and displayed tour version use V26.13':c['check']='Embedded controller contains the V26.13 HUD label'
for c in q['captures']:
 if 'hud_version'in c:c['controller_hud_label']=c.pop('hud_version')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
p=W/'v26_13/Review/Viewport_01_Actual_Tour.json';q=json.loads(p.read_text('utf8'))
if 'hud_version'in q:q['controller_hud_label']=q.pop('hud_version')
p.write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
runpy.run_path(str(W/'v26_13_package.py'),run_name='__main__')
runpy.run_path(str(W/'v26_13_verify_package.py'),run_name='__main__')
