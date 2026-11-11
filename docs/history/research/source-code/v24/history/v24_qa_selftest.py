import bpy,json,sys
from pathlib import Path
W=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work');sys.path.insert(0,str(W));from v24_qa_blender import validate_v24
out=W/'v24_qa_probe';baseline=json.loads((out/'Baseline_Snapshot.json').read_text(encoding='utf8'))
try:validate_v24(bpy,baseline,out)
except AssertionError:pass
r=json.loads((out/'V24_Fresh_Blend_QA.json').read_text(encoding='utf8'));fail=[c['check']for c in r['failures']];assert set(fail)=={'Fifteen independent carved fields','Independent editable wing sculpture exists'},fail;print('QA JSON ROUNDTRIP / ALL ORIGINAL PRESERVATION CHECKS PASS; ONLY TWO EXPECTED V24-ABSENT FAILURES',flush=True)
