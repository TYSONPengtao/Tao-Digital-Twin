from v26_2_common import *
D=W/'v26_7_gate_audit';D.mkdir(exist_ok=True);FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};out=[]
for r in J.values():
 lo,hi=np.array(r['bounds'])
 if np.any(hi<[4.6,-12.6,-.9])or np.any(lo>[9.6,-9.6,3.2]):continue
 out.append(r);print(r['name'],np.round([lo,hi],4).tolist(),flush=True)
(D/'Native_Region_Index.json').write_text(json.dumps(out,indent=2),'utf8')
for n in ['SITE_V21_GATE_REFERENCE_LAYER_01_Geometry','V26_2_Continuous_Ground_And_Perimeter_Shell','V26_1_Courtyard_West_Wall_Single_Surface']:
 r=J[n];a=np.load(FD/r['file']);m=solid(a['v'],a['f']);print('PROFILES',n,flush=True)
 for x in [4.85,5.0,5.3,5.5,6.0,6.6,7.2,7.7,7.9,8.1,8.3,8.5]:
  for y in [-12.2,-12.,-11.9,-11.8,-11.7,-11.6,-11.4,-11.3,-11.2,-11.1,-10.9]:
   hits=m.ray_cast([x,y,.5],[x,y,-.9]);hits=[list(h.position)for h in hits if h.normal[2]>.8]
   if hits:print('UP',x,y,[round(v[2],5)for v in hits],flush=True)
