from pathlib import Path
import json,shutil,hashlib
W=Path(__file__).parent;D=W/'v26_7';D.mkdir(exist_ok=True);rows=[];proof=[]
for folder,fn in [('v26_7_column_audit/final_candidate','Prepared_Geometry.json'),('v26_7_railing_audit','Prepared_Railing.json'),('v26_7_site_audit','Prepared_Site_Decoration.json'),('v26_7_gate_audit/Prepared','Prepared_Geometry.json')]:
 p=W/folder;data=json.loads((p/fn).read_text('utf8'))
 for r in data['objects']:
  assert r['name']not in [a['name']for a in rows];shutil.copy2(p/r['file'],D/r['file']);rows.append(r)
 proof.append({'prepared_source':str(p/fn),'source_sha256':hashlib.sha256((p/fn).read_bytes()).hexdigest(),'details':data.get('proof',{}),'finalize':data.get('finalize',{})})
(D/'Prepared_Geometry.json').write_text(json.dumps({'source':'E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend','source_sha256':'ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7','objects':rows,'archive':[],'proof':proof},ensure_ascii=False,indent=2),'utf8')
print('COLLECTED',len(rows),flush=True)
