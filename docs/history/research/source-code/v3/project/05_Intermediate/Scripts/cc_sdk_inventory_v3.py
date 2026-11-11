import sys,json,csv
from pathlib import Path
import ccmasterkernel as cc
W=Path(__file__).parent;root=Path(r'D:\AJAVIS01\ContextCapture\CASES')
items=list(csv.DictReader((W/'CASES_Model_Files_V3.csv').open(encoding='utf-8-sig')));result=[]
print('SDK',cc.version(),flush=True)
for item in items:
 if item['ext']!='.ccm':continue
 p=cc.Project();err=p.readFromFile(item['path']);row={'case':item['case'],'path':item['path'],'error':None if err.isNone() else err.message,'blocks':[]}
 if err.isNone():
  row['name']=p.getName()
  for i in range(p.getNumBlocks()):
   b=p.getBlock(i);pgs=b.getPhotogroups();br={'name':b.getName(),'photos':pgs.getNumPhotos(),'reconstructions':[],'photo_examples':[]}
   for j in range(pgs.getNumPhotogroups()):
    pg=pgs.getPhotogroup(j)
    for photo in pg.getPhotoArray()[:2]:
     br['photo_examples'].append({'image':photo.imageFilePath,'gps':[photo.exifData.GPSLatitude,photo.exifData.GPSLongitude,photo.exifData.GPSAltitude]})
   for j in range(b.getNumReconstructions()):
    rec=b.getReconstruction(j);bbox=rec.getROI().getBoundingBox();rr={'name':rec.getName(),'SRS':rec.getSRS(),'bbox':[bbox.xMin,bbox.yMin,bbox.xMax,bbox.yMax],'productions':[]}
    for k in range(rec.getNumProductions()):prod=rec.getProduction(k);rr['productions'].append({'name':prod.getName()})
    br['reconstructions'].append(rr)
   row['blocks'].append(br)
 result.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 (W/'CC_SDK_Projects_V3.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('No source writes or reconstruction jobs submitted',flush=True)
