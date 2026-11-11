from pathlib import Path
import json,runpy
W=Path(__file__).parent;p=Path('E:/jz/JIA/Rebuild_V26_14/Reports/V26_14_Runtime_Viewport_QA.json');q=json.loads(p.read_text('utf8'))
for c in q['checks']:
 if c['check']=='Delivered Fast file starts the person tour at the inspected F2 room':c['check']='Delivered Fast person tour runs at the inspected F2 room'
p.write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
metadata=W/'v26_14/Review/Viewport_02_WC_Flush_Return.json';record=json.loads(metadata.read_text('utf8'));record['mode']='Actual native material viewport close-up; person hidden only for unobstructed wall inspection';metadata.write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
q['captures'][1]['mode']=record['mode'];p.write_text(json.dumps(q,ensure_ascii=False,indent=2),'utf8')
runpy.run_path(str(W/'v26_14_package.py'),run_name='__main__')
runpy.run_path(str(W/'v26_14_verify_package.py'),run_name='__main__')
