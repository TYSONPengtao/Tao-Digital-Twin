import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from PIL import Image,ImageDraw,ImageFont
D=W/'v8_terrain_clear';m=json.loads((D/'Merge_Manifest.json').read_text(encoding='utf-8'));q=json.loads((D/'Terrain_Clearance_Polygon.json').read_text(encoding='utf-8'));p=q['clearance'];bounds=q['bounds_local'];scale=36.;offset=np.array([80.-bounds[0]*scale,60.+bounds[3]*scale]);im=Image.new('RGB',(1050,1020),'white');dr=ImageDraw.Draw(im)
def xy(v):return np.column_stack([v[:,0]*scale,-v[:,1]*scale])+offset
colors=[(88,156,116),(198,171,116)]
for row,col in zip(m['new_patch_rows'],colors):
 d=np.load(D/'data'/row['file']);tt=d['vertices'][d['faces']];pp=xy(tt[:,:,:2].reshape(-1,2)).reshape(-1,3,2)
 for t in pp:dr.polygon([tuple(v) for v in t],fill=col)
parts=p if isinstance(p,list) else [p]
for part in parts:
 dr.line([tuple(v) for v in xy(np.array(part['outer']))],fill=(35,35,35),width=2)
for j,text in enumerate(['V8 WEST YARD - TERRAIN ONLY','Green: original measured ground + original UV','Tan: occluded ground interpolated from low earth samples','No source roof is pushed down to become ground','Editing scope 366.397 m2; calibration RMS 1.47 pixels']):dr.text((50,865+j*25),text,fill=(30,30,30))
im.save(D/'V8_West_Terrain_Ground_Classification.png')
