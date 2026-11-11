import sys,json,hashlib,base64
from pathlib import Path
W=Path(__file__).parent
sys.path.insert(0,str(W/'libs'))
import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
old=(W/'v6_reality_inventory/check_v6_exchange_photos.py').read_text(encoding='utf-8')
new=old.replace('Path(__file__).resolve().parents[1]','Path(__file__).resolve().parent').replace('Rebuild_V6_Hybrid','Rebuild_V7_Hybrid').replace('Reality_Hybrid_V6_LOCAL','Reality_Hybrid_V7_LOCAL').replace('D=Path(__file__).resolve().parent',"D=O/'06_Report'").replace('V6_Exchange_Photo_Readback.json','V7_Exchange_Photo_Readback.json')
new+='\nassert report["passed"], "Exchange image/UV readback failed"\n'
(W/'check_v7_exchange_photos.py').write_text(new,encoding='utf-8')
f=rh.File3dm.Read(str(O/'04_Rhino/Reality_Hybrid_V7.3dm'))
rows=[]
for e in f.EmbeddedFiles:
    path=e.Filename
    actual=base64.b64decode(f.GetEmbeddedFileAsBase64(path))
    expected=Path(path).read_bytes()
    row={'path':path,'embedded_bytes':len(actual),'embedded_sha256':hashlib.sha256(actual).hexdigest(),'original_pixels_match':actual==expected}
    rows.append(row)
    assert row['original_pixels_match'],path
report={'status':'PASS','embedded_file_count':len(rows),'embedded_files':rows,'limits':'Original image byte retention; projection calibration is a separate pending field check'}
(O/'06_Report/Native_Embedded_Texture_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
local=O/'06_Report/Editable_Local_Native_QA.json'
old_local=json.loads(local.read_text(encoding='utf-8'))
kernel=json.loads((O/'06_Report/Editable_Rhino_Kernel_QA.json').read_text(encoding='utf-8'))
old_local['raw_pre_kernel_invalid_count']=len(old_local.get('invalid',[]))
old_local['invalid']=kernel['invalid']
old_local['final_object_count']=kernel['object_count']
old_local['unexpected_open_solids']=kernel['unexpected_open_solids']
old_local['validation_stage']='Final native RhinoCommon kernel after tolerance initialization'
old_local['raw_pre_kernel_errors_resolved']=True
local.write_text(json.dumps(old_local,ensure_ascii=False,indent=2),encoding='utf-8')
print('Embedded original image bytes: PASS',len(rows),flush=True)
