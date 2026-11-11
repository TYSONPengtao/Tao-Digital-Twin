from pathlib import Path
import shutil
W=Path(__file__).parent;D=W/'v26_15_perf';D.mkdir(exist_ok=True)
for name in ['build_fast','verify_fast','fast_display','physics_qa','door_clearance_qa','viewport_review']:
 source=W/('v26_14_'+name+'.py');(W/('v26_15_'+name+'.py')).write_text(source.read_text('utf8').replace('V26_14','V26_15').replace('v26_14','v26_15').replace('V26.14','V26.15'),'utf8')
(D/'roam_controller_fast.py').write_text(Path('E:/jz/JIA/Rebuild_V26_14/Roam/roam_controller_fast.py').read_text('utf8').replace('V26.14','V26.15').replace('Rebuild_V26_14','Rebuild_V26_15'),'utf8')
