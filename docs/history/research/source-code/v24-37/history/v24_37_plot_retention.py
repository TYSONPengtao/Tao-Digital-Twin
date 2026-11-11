from pathlib import Path
import json,sys
W=Path(__file__).parent
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import shape
D=W/'v24_37';meta=json.loads((W/'v24_36/Top_Projection.json').read_text())
im=Image.open('E:/jz/JIA/Rebuild_V24_36/Reports/V24_36_Context_Top.png').convert('RGB')
draw=ImageDraw.Draw(im);c=meta['center'];sx=im.width/meta['width_m']
def pixel(x,y):return (round((x-c[0])*sx+im.width/2),round((c[1]-y)*sx+im.height/2))
g=shape(json.loads((D/'Complete_Scan_Retention.geojson').read_text()))
for p in ([g]if g.geom_type=='Polygon'else g.geoms):
 draw.line([pixel(x,y)for x,y in p.exterior.coords],fill=(255,50,180),width=3)
for x,y,s in [(-80,100,'ROAD'),(-390,5,'FIELD'),(-615,-150,'WEST'),(6.5,-4.8,'HOUSE')]:
 px,py=pixel(x,y);draw.ellipse((px-5,py-5,px+5,py+5),fill=(255,255,0));draw.text((px+6,py),s,fill='yellow')
im.save(D/'Retention_Overlay.png')
print('SAVED',D/'Retention_Overlay.png')
