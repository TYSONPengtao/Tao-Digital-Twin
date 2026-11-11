from pathlib import Path
import json
W=Path(__file__).parent;D=W/'v26_9_perf';D.mkdir(exist_ok=True)
code=(W/'v26_8_build_fast.py').read_text('utf8').replace('Rebuild_V26_8','Rebuild_V26_9').replace('Architecture_Complete_V26_8','Architecture_Complete_V26_9').replace("D=W/'v26_8_perf'","D=W/'v26_9_perf'")
code=code.replace("assert sha(SRC)=='e21a89f9b617a541790a383295266e852182c6b915559cddf93d070e7137da72'","assert sha(SRC)==json.loads((O/'Reports/V26_9_Build.json').read_text('utf8'))['sha256']")
(D/'roam_controller_fast.py').write_text((W/'v26_8_perf/roam_controller_fast.py').read_text('utf8').replace('Rebuild_V26_8','Rebuild_V26_9').replace('Architecture_Complete_V26_8','Architecture_Complete_V26_9'),'utf8')
(W/'v26_9_build_fast.py').write_text(code,'utf8')
