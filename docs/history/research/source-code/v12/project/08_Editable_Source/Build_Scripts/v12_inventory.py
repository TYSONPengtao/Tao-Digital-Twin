import sys,json,hashlib,math
from pathlib import Path
W=Path(__file__).parent; sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
from PIL import Image,ImageOps,ImageDraw
import numpy as np,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V12'); D=W/'v12_reference_audit';D.mkdir(exist_ok=True)
for f in ['01_Source','02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source']: (O/f).mkdir(parents=True,exist_ok=True)
S=json.loads(Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf8'));ex.SCENE=S
out=[]
for e in S['elements']:
 if e['layer']!='60_SITE' and not any(k in e['name'] for k in ['ROOF_MAIN','CANOPY']):continue
 vv=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e)
  if v is not None:vv.append(v)
 if vv:
  v=np.vstack(vv);out.append({'name':e['name'],'family':e['family'],'layer':e['layer'],'parts':len(ex.expand_parts(e)),'min':v.min(0).tolist(),'max':v.max(0).tolist(),'source':e.get('source')})
(D/'Scene_Site_Inventory.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
rows=[];sheets=[]
for directory in sorted(Path(r'G:\处理').iterdir()):
 if not directory.is_dir() or not directory.name.isdigit():continue
 files=sorted(directory.rglob('*.JPG'))
 # Every JPG is inventoried; overview contact sheets show every twelfth frame.
 for p in files:
  with Image.open(p) as im:
   exif=im.getexif();rows.append({'path':str(p),'bytes':p.stat().st_size,'size':im.size,'date_time':exif.get(306),'orientation':exif.get(274,1)})
 sample=files[::max(1,len(files)//32)]
 if files[-1] not in sample:sample.append(files[-1])
 for batchid in range(0,len(sample),32):
  pp=sample[batchid:batchid+32];cols=4;tw,th=440,275;sheet=Image.new('RGB',(cols*tw,math.ceil(len(pp)/cols)*th),'#eeeeee');dr=ImageDraw.Draw(sheet)
  for i,p in enumerate(pp):
   with Image.open(p) as im:im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((tw-10,th-35));x=(i%cols)*tw;y=(i//cols)*th;sheet.paste(im,(x+(tw-im.width)//2,y+4));dr.text((x+8,y+th-26),directory.name+'/'+p.name,fill='black')
  dst=D/f'Aerial_{directory.name}_{batchid//32+1}.jpg';sheet.save(dst,quality=86);sheets.append(str(dst))
(D/'Aerial_Inventory.json').write_text(json.dumps({'JPG_count':len(rows),'files':rows,'overview_contact_sheets':sheets,'DNG_count':len(list(Path(r'G:\处理').rglob('*.DNG'))),'raw_photographs_unchanged':True},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'scene_site_nodes':len(out),'aerial_photos':len(rows),'contact_sheets':sheets},ensure_ascii=False),flush=True)
