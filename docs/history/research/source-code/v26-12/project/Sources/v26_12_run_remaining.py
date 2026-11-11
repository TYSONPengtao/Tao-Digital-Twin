from pathlib import Path
import runpy,json,gc,sys
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_12')
for script,report in[
 ('v26_12_native_qa.py','V26_12_Native_QA.json'),
 ('v26_12_gate_clearance_qa.py','V26_12_Gate_Clearance_QA.json'),
 ('v26_12_physics_qa.py','V26_12_Interior_Physics_QA.json'),
 ('v26_12_build_fast.py',None),
 ('v26_12_verify_fast.py','V26_12_Fast_Display_QA.json'),
]:
 print('RUNNING',script,flush=True);runpy.run_path(str(W/script),run_name='__main__');gc.collect()
 if report:
  r=json.loads((O/'Reports'/report).read_text('utf8'));assert not r['failures']and all(q['pass']for q in r['checks']),(script,r['failures'])
sys.argv=['v26_12_render.py'];runpy.run_path(str(W/'v26_12_render.py'),run_name='__main__');gc.collect()
# The two immutable V26.11 comparison renders already exist at the same cameras.
print('ALL_REMAINING_DONE',flush=True)
