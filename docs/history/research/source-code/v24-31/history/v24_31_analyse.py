import json
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_31';rows=json.loads((D/'Inventory.json').read_text('utf8'));mats=json.loads((D/'Materials.json').read_text('utf8'))
for r in rows:
 if r['type']!='MESH':continue
 n=r['name']
 if any(t in n.upper()for t in ['BAY_BASE','BAY_PLINTH','WINDOW_REVEAL','REVEAL','SILL_WINDOW','BEAM','BRACE','FLOOR','CEILING','SOFFIT','WC_','BATH','STAIR_V4','ROOM_ZONE']):print('PART',n,r['bounds'],r['materials'])
red=[m for m,a in mats.items()if a['base']and a['base'][0]>a['base'][1]*1.45 and a['base'][0]>.08]
print('RED_MATS',red)
for r in rows:
 if r['bounds']and any(m in red for m in r['materials'])and r['bounds'][0][2]>6.9 and r['bounds'][0][2]<7.4:print('F3_RED',r['name'],r['bounds'],r['materials'])
for r in rows:
 if r['bounds']and r['type']=='MESH'and r['bounds'][0][0]<-.2 and r['bounds'][1][0]>.2 and r['bounds'][0][1]>7 and r['bounds'][1][1]<10. and r['bounds'][1][2]<4:print('WEST_WC',r['name'],r['bounds'],r['materials'])
