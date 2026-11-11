from pathlib import Path
import json,shutil,hashlib
D=Path(__file__).resolve().parent;R=D/'References';O=D/'Representative_References';O.mkdir(exist_ok=True)
allrows=json.loads((R/'Frame_Provenance.json').read_text('utf8'));rows=[]
selected={
'Actual_t0115_L0_Pitch-40.jpg':'Tread edges meet wall continuously; opposite independent rail and well-side are visible.',
'Actual_t0135_L1_Pitch-40.jpg':'Half landing and turned post with the opposite flight visible.',
'Actual_t0150_L0_Pitch-40.jpg':'Upper flight and horizontal guard connection with open well-side.',
'Actual_t0270_L0_Pitch-40.jpg':'High downward view separates the two flights, half landing and turn-end posts.',
'Actual_t0275_L1_Pitch-40.jpg':'Storey arrival platform and separate post positions.'}
for row in allrows['rows']:
 if row['file']not in selected:continue
 src=R/row['file'];dst=O/src.name;shutil.copy2(src,dst);rows.append(dict(row,source_video=allrows['video'],observation=selected[src.name]))
src=Path('D:/Desktop/屏幕截图 2026-10-24 095619.jpg');dst=O/'User_Actual_2026-10-24_095619.jpg';shutil.copy2(src,dst)
rows.append({'file':dst.name,'source_file':str(src),'source_type':'User supplied actual site photo','observation':'User marked the continuous stair tread to tiled-wall junction; compare with model-side cavity.','metric_use':False,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(O/'Provenance.json').write_text(json.dumps({'purpose':'Six unedited representative actual references for stairwell reconstruction; not millimetre surveys.','rows':rows},ensure_ascii=False,indent=2),'utf8')
print('SELECTED',len(rows))
