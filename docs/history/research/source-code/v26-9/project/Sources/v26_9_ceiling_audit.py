from v26_2_common import *
D=W/'v26_9'
FD=W/'v26_8/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(FD/r['file']);m=solid(a['v'],a['f']);rows=[]
for x in[2.,4.6,6.2,7.8,8.5,11.]:
 for y in[3.,6.,7.7,8.55,9.3]:
  h=m.ray_cast([x,y,8.8],[x,y,11.5]);rows.append({'xy':[x,y],'hits':[(q.position[2],q.normal[2])for q in h]})
(D/'Ceiling_Audit.json').write_text(json.dumps(rows,indent=2),'utf8')
print([(r['xy'],r['hits'][:3])for r in rows if r['xy'][0]in[6.2,8.5]])
