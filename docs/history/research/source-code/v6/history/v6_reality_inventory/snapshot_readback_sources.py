import json,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');E=O/'05_Export';D=Path(__file__).resolve().parent
P=D/'V6_Exchange_Photo_Readback.json';R=json.loads(P.read_text(encoding='utf-8'))
def fh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
R['readback_file_snapshots']={ext:dict(path=str(E/f'Reality_Hybrid_V6_LOCAL.{ext}'),bytes=(E/f'Reality_Hybrid_V6_LOCAL.{ext}').stat().st_size,sha256=fh(E/f'Reality_Hybrid_V6_LOCAL.{ext}')) for ext in ['glb','fbx','obj','mtl']}
for kind,imageskey in [('glb','images'),('fbx','videos')]:
 for x in R[kind][imageskey]:
  x['expected_materials']=[v['material'] for v in R['expected_images'].values() if v['sha256']==x['sha256']];x.pop('expected_material',None)
P.write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8');print('captured exchange SHA256 snapshots',flush=True)
