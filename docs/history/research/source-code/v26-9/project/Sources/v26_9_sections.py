from v26_2_common import *
from pathlib import Path
D=W/'v26_9';D.mkdir(exist_ok=True)
FD=W/'v26_8/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(FD/r['file']);m=solid(a['v'],a['f'])
rows=[]
for fl,base in [(1,-.45),(2,3.45),(3,7.05)]:
 for dz in[-.08,.04,.15,.26,.34,.94,1.1,1.21]:
  sec=m.slice(base+dz)^mf.CrossSection([[[9.,.9],[13.12,.9],[13.12,2.36],[9.,2.36]]])
  rows.append({'floor':fl,'z':base+dz,'loops':[np.array(p).round(6).tolist()for p in sec.to_polygons()]})
(D/'Existing_Bay_Sections.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
print('SECTIONS_DONE',len(rows))
