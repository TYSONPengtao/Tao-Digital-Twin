from pathlib import Path
import shutil
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_14');D=W/'v26_14_perf';D.mkdir(exist_ok=True)
shutil.copy2(O/'Roam/roam_controller_fast.py',D/'roam_controller_fast.py')
for tag in ['fast_display','build_fast','verify_fast','physics_qa']:
 s=(W/('v26_13_'+tag+'.py')).read_text('utf8').replace('V26_13','V26_14').replace('v26_13','v26_14').replace('V26.13','V26.14')
 (W/('v26_14_'+tag+'.py')).write_text(s,'utf8')
print('HELPERS_ADAPTED',flush=True)
