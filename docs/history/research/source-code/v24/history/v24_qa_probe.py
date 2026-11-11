import bpy,json,sys
from pathlib import Path
W=Path(r'C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work');sys.path.insert(0,str(W));from v24_qa_blender import baseline_snapshot
b=baseline_snapshot(bpy);out=W/'v24_qa_probe';out.mkdir(exist_ok=True);(out/'Baseline_Snapshot.json').write_text(json.dumps(b),encoding='utf8');print('V24QA BASELINE SNAPSHOT READY',len(b['objects']),len(b['materials']),len(b['images']),len(b['doors']),len(b['wings']['components']),len(b['wings']['anchor_points']),flush=True)
