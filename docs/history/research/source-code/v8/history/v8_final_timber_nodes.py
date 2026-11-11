import json,shutil
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
p=O/'02_Data/V8_Changed_Nodes.json'
shutil.copy2(p,O/'02_Data/V8_All_Changed_Nodes.json')
p.write_text(json.dumps({'changed':['SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS'],'removed':[]}),encoding='utf-8')
print('Regenerating final angled timber head beam and column contacts')
