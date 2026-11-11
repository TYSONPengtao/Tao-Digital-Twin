from pathlib import Path
import hashlib,json
O=Path(r'E:\jz\JIA\Rebuild_V4');P=Path(r'outputs\Production_1QK_Rebuild_V4');checks={}
for rel in ['06_Rhino/Production_1QK_Rebuild.3dm','07_SketchUp/Production_1QK_Rebuild.skp','05_Intermediate/Architecture_Scene.json']:
 checks[rel]=hashlib.sha256((O/rel).read_bytes()).digest()==hashlib.sha256((P/rel).read_bytes()).digest()
for rel in ['06_Rhino/Production_1QK_Rebuild.3dm','07_SketchUp/Production_1QK_Rebuild.skp']:
 a=Path(r'E:\jz\JIA\Rebuild_V3')/rel;b=Path(r'outputs\Production_1QK_Rebuild_V3')/rel
 checks['V3 preserved '+rel]=hashlib.sha256(a.read_bytes()).digest()==hashlib.sha256(b.read_bytes()).digest()
assert all(checks.values());print(json.dumps(checks))
