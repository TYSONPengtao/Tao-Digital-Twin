import json,sys
from pathlib import Path
import ccmasterkernel as cc
W=Path(__file__).parent;rows=json.loads((W/'CC_SDK_Projects_V3.json').read_text(encoding='utf-8'));out=W/'cc_blocks_v3';out.mkdir(exist_ok=True)
for row in rows:
 if row['case'] not in ['JIA','PTHOUSE','PT666PT666','MB501','MB7','ui','DDD','ZZCLDQ','新建工程']:continue
 p=cc.Project();err=p.readFromFile(row['path'])
 if not err.isNone():continue
 for i in range(p.getNumBlocks()):
  b=p.getBlock(i)
  if b.getPhotogroups().getNumPhotos()==0:continue
  target=out/(row['case']+'_'+Path(row['path']).stem+'_B'+str(i)+'.xml');err=b.exportToBlocksExchangeXML(str(target),cc.BlockExportOptions());print(target.name,'OK' if err.isNone() else err.message,flush=True)
