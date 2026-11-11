import os,json,csv,collections,struct
from pathlib import Path
root=Path(r'D:\AJAVIS01\ContextCapture\CASES');out=Path(__file__).parent
summary=[];refs=[];files=[]
extensions={'.ccm','.3mx','.3mxb','.obj','.osgb','.ply','.las','.laz','.fbx','.glb','.xml','.kml','.tif','.3sm','.json'}
for case in sorted(x for x in root.iterdir() if x.is_dir()):
 counts=collections.Counter();sizes=collections.Counter();metas=[]
 for folder,dirs,names in os.walk(case):
  dirs[:]=[d for d in dirs if d not in ['Rebuild','Rebuild_V2','Rebuild_V3','node_modules']]
  for name in names:
   p=Path(folder)/name;ext=p.suffix.lower();size=p.stat().st_size;counts[ext]+=1;sizes[ext]+=size
   if ext in extensions:files.append({'case':case.name,'path':str(p),'ext':ext,'bytes':size})
   if ext=='.3mx':
    try:
     meta=json.loads(p.read_text(encoding='utf-8-sig'));refs.append({'case':case.name,'path':str(p),'metadata':meta});metas.append(str(p))
    except Exception as e:refs.append({'case':case.name,'path':str(p),'error':str(e)})
 summary.append({'case':case.name,'files':sum(counts.values()),'bytes':sum(sizes.values()),'extensions':dict(counts),'3mx':metas})
(out/'CASES_Inventory_V3.json').write_text(json.dumps({'summary':summary,'references':refs},ensure_ascii=False,indent=2),encoding='utf-8')
with (out/'CASES_Model_Files_V3.csv').open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=['case','path','ext','bytes']);writer.writeheader();writer.writerows(files)
for row in summary:print(row['case'],row['files'],round(row['bytes']/1e9,2),'GB',{k:v for k,v in row['extensions'].items() if k in extensions})
for row in refs:
 m=row.get('metadata',{});print('3MX',row['case'],Path(row['path']).name,'SRS',m.get('SRS',m.get('srs')),json.dumps(m.get('layers',[]),ensure_ascii=False)[:650])
