from pathlib import Path
import json,hashlib,shutil
W=Path(__file__).parent;D=W/'v25';O=Path('E:/jz/JIA/Rebuild_V25');textures=json.loads((D/'Texture_Index.json').read_text('utf8'));mats=json.loads((D/'Material_Index.json').read_text('utf8'));report=json.loads((D/'Export_Report.json').read_text('utf8'));mapping={}
for t in textures:
 p=Path(t['file'])
 if p.name.startswith('BAKED_'):
  h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==t['sha256'];q=p.with_name(p.stem+'_'+h[:12]+p.suffix)
  if p!=q:shutil.copy2(p,q)
  mapping[str(p)]=str(q);t['file']=str(q)
for m in mats:
 for s in ['base_texture','bump_texture']:
  if m.get(s) in mapping:m[s]=mapping[m[s]]
for row in report['baked_objects']:row['file']=mapping.get(row['file'],row['file'])
for name,data in [('Texture_Index.json',textures),('Material_Index.json',mats),('Export_Report.json',report)]:
 (D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Reports/V25_Blender_Export_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('CONTENT_ADDRESSED_BAKED_TEXTURES',len(mapping),flush=True)
