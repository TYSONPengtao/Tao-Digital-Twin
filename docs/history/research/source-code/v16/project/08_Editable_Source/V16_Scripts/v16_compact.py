import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V15')
rows=json.loads((W/'v16/Probe.json').read_text(encoding='utf8'))
for r in rows:
 if any(k in r['name'] for k in ['REBUILT_EARTH','REBUILT_COURT','REBUILT_ROAD','RETAINING_WALL_0','RETAINING_WALL_1','OUTER_GATE_SCORED','CONTINUOUS_PAVEMENT']):print(json.dumps({k:r[k] for k in ['name','bounds','top_z_quantiles','top_area']}))
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 e=E[n];pts=[]
 for p in e['parts']:
  g=p['geometry']
  if p['material']!='M_Stone_Rubble' or len(g.get('vertices',[]))!=8:continue
  v=np.array(g['vertices']);pts.append([*((v[0,:2]+v[3,:2])/2),v[[0,3],2].min()]);pts.append([*((v[1,:2]+v[2,:2])/2),v[[1,2],2].min()])
 unique=[]
 for q in pts:
  if not unique or np.linalg.norm(np.array(q[:2])-np.array(unique[-1][:2]))>.01:unique.append(q)
 (W/'v16'/f'{n}_centerline.json').write_text(json.dumps(unique,indent=2),encoding='utf8')
 print('WALL LINE',n,len(unique),'start',unique[:3],'end',unique[-3:],'metadata',{k:v for k,v in e.items() if k!='parts'})
for n in ['SITE_V12_REBUILT_EARTH_-20_-20_0','SITE_V12_REBUILT_EARTH_-20_0_0','SITE_V12_REBUILT_EARTH_0_-20_0','SITE_V12_REBUILT_EARTH_0_0_0']:
 g=E[n]['parts'][0]['geometry'];v=np.array(g['vertices']);print('EARTH SOLID',n,g['type'],len(v),len(g['faces']),v[:4].tolist())
print('MATERIAL',S['materials']['M_V12_Terrain_Earth'])
print('REFERENCES',[(p.name,p.stat().st_size) for p in (B/'07_Reference/INSV').glob('*') if p.suffix=='.json'])
