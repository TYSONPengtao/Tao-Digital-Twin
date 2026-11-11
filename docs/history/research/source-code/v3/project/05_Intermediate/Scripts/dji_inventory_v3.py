import sys,os,json,csv,collections,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageOps
root=Path(r'D:\DJI');out=W/'dji_v3';out.mkdir(exist_ok=True);rows=[];sets=collections.Counter()
def rational(value):
 try:return float(value)
 except:return 0.
def degree(v):return rational(v[0])+rational(v[1])/60+rational(v[2])/3600
for folder,dirs,names in os.walk(root):
 for name in names:
  p=Path(folder)/name;ext=p.suffix.lower()
  if ext not in ['.jpg','.jpeg','.dng','.png','.mp4','.mov']:continue
  rel=p.relative_to(root);group=rel.parent.as_posix();sets[group]+=1
  row={'path':str(p),'set':group,'name':name,'ext':ext,'bytes':p.stat().st_size,'datetime':'','lat':None,'lon':None,'alt':None,'near_site':False}
  if ext in ['.jpg','.jpeg']:
   try:
    im=Image.open(p);ex=im.getexif();row['width'],row['height']=im.size;row['datetime']=str(ex.get(306,''));gps=ex.get_ifd(34853)
    if 2 in gps and 4 in gps:
     row['lat']=degree(gps[2])*(-1 if gps.get(1)=='S' else 1);row['lon']=degree(gps[4])*(-1 if gps.get(3)=='W' else 1);row['alt']=rational(gps.get(6,0))
     row['distance_m']=math.hypot((row['lat']-24.92009)*111000,(row['lon']-98.68275)*100600);row['near_site']=row['distance_m']<250
   except Exception as e:row['error']=str(e)
  rows.append(row)
  if len(rows)%1000==0:print('indexed',len(rows),flush=True)
(out/'DJI_All_Collections.json').write_text(json.dumps({'sets':dict(sets),'files':rows},ensure_ascii=False,indent=2),encoding='utf-8')
fields=['path','set','name','ext','bytes','datetime','width','height','lat','lon','alt','distance_m','near_site','error']
with (out/'DJI_All_Collections.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
near=[r for r in rows if r['near_site']];print('TOTAL',len(rows),'SETS',dict(sets),'NEAR SITE JPG',len(near),flush=True)
for group in sorted(sets):
 imgs=[r for r in rows if r['set']==group and r['ext'] in ['.jpg','.jpeg']]
 if not imgs:continue
 sample=imgs[::max(1,len(imgs)//70)];tiles=[]
 for r in sample[:90]:
  try:
   im=Image.open(r['path']);im.thumbnail((256,180));tile=Image.new('RGB',(256,207),'white');tile.paste(im,((256-im.width)//2,0));ImageDraw.Draw(tile).text((4,182),r['name']+(' NEAR' if r['near_site'] else ''),fill='black');tiles.append(tile)
  except:pass
 if not tiles:continue
 sheet=Image.new('RGB',(256*6,207*math.ceil(len(tiles)/6)),(200,200,200))
 for i,tile in enumerate(tiles):sheet.paste(tile,((i%6)*256,(i//6)*207))
 sheet.save(out/('Collection_'+group.replace('/','_')+'.jpg'))
print('COLLECTION CONTACTS COMPLETE',flush=True)
