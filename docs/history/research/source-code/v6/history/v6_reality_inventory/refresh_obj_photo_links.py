"""Recheck only external photo links after root copies original JPEG files.

The geometry and embedded-image readback is reused only if exchange files
still match the snapshot SHA256. No source/export mesh file is rewritten.
"""
import json,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');E=O/'05_Export';D=Path(__file__).resolve().parent
P=D/'V6_Exchange_Photo_Readback.json';R=json.loads(P.read_text(encoding='utf-8'))
def fh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
for ext,row in R.get('readback_file_snapshots',{}).items():
 assert fh(Path(row['path']))==row['sha256'],f'{ext} changed since full readback; rerun full check'
byname={x['material']:x for x in R['expected_images'].values()}
for row in R['obj']['photo_material_links']:
 p=E/row['reference'];row['exists']=p.is_file();row['bytes']=p.stat().st_size if p.is_file() else None;row['linked_original_bytes']=p.is_file() and fh(p)==byname[row['material']]['sha256']
R['obj']['passed']=all(x['linked_original_bytes'] for x in R['obj']['photo_material_links']) and len(R['obj']['photo_material_links'])==9 and all(x['passed'] for x in R['obj']['base_mesh_uv']) and len(R['obj']['base_mesh_uv'])==5 and R['obj']['missing_face_uv']==0
R['passed']=all(R[k]['passed'] for k in ['glb','fbx','obj'])
P.write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'passed':R['passed'],'obj_passed':R['obj']['passed'],'photos_resolved':sum(x['linked_original_bytes'] for x in R['obj']['photo_material_links'])}),flush=True)
