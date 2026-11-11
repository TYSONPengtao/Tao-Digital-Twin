import json,hashlib
from pathlib import Path
import v24_qa_blender as q
from v24_06_common import snapshot
O=Path('E:/jz/JIA/Rebuild_V24_07');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_07.blend'
B=Path('E:/jz/JIA/Rebuild_V24_06/Blender/Architecture_Complete_V24_06.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,data):
 R.mkdir(parents=True,exist_ok=True);(R/n).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
