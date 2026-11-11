import json,math
from pathlib import Path
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
E={e['name']:e for e in S['elements']}
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_COURTYARD_WEST_TILE_WALL','SITE_GATE_EAST_FLANK']:
 e=E[n];pts=[];zs=[]
 for p in e['parts'][::2]:
  v=p['geometry']['vertices'];a=[(v[0][i]+v[3][i])/2 for i in range(2)];b=[(v[1][i]+v[2][i])/2 for i in range(2)]
  if not pts:pts.append(a)
  pts.append(b)
  zs.extend([p2['geometry']['vertices'][j][2] for p2 in e['parts'][1::2] for j in range(4,8)])
 print(n,'nseg',len(pts)-1,'ends',pts[0],pts[-1],'length',sum(math.dist(a,b) for a,b in zip(pts,pts[1:])),'crownrange',min(zs),max(zs))
 Path('work/v10_wall_audit/'+n+'_Centreline.json').write_text(json.dumps(pts,indent=2),encoding='utf-8')
for n in ['SITE_SW_METAL_ENTRY_GATE','SITE_INNER_DARK_TIMBER_DOORS','SITE_INNER_STONE_GATEHOUSE','SITE_COURTYARD_WEST_WHITE_INSIDE']:
 print(n,json.dumps({k:v for k,v in E[n].items() if k!='parts'},ensure_ascii=False))
print('otherwallnames',[(e['name'],e.get('classification')) for e in S['elements'] if 'WALL' in e['name'] and e['layer']=='60_SITE'])
