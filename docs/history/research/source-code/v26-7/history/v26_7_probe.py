from v26_2_common import *
FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};D=W/'v26_7';D.mkdir(exist_ok=True)
hn='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[hn]['file']);m=solid(a['v'],a['f']);out=[]
for r in J.values():
 if any(k in r['name'].upper()for k in ['GATE','ENTRANCE','ENTRY']) or r['name'].startswith('V26_2_Continuous'):
  print(r['name'],np.round(r['bounds'],4).tolist(),flush=True)
for fl,floor in [(1,-.45),(2,3.45),(3,7.05)]:
 for z in [floor+.3,floor+1.0,floor+2.,floor+3.0,floor+3.3]:
  row={'floor':fl,'z':z,'walls':{}}
  for label,axis,center,along in [('west',0,3.9,[7.51,7.54,7.6,7.8,8.,8.5,9.,9.5,9.55,9.6,9.65]),('east',0,9.1,[7.51,7.54,7.6,7.8,8.,8.5,9.,9.5,9.55,9.6,9.65]),('rear',1,9.8,[3.95,4.02,4.1,4.2,4.3,4.5,5.,6.,7.,8.,8.8,8.95,9.05]),('front',1,7.3,[4.02,4.1,4.2,4.3,4.5,5.,6.,7.,7.7,8.95,9.05])]:
   arr=[]
   for u in along:
    p=[center,u,z]if axis==0 else[u,center,z];p=np.array(p,float);dv=np.eye(3)[axis]*.55;hs=m.ray_cast(p-dv,p+dv);arr.append([u,[round(float(h.position[axis]),5)for h in hs]])
   row['walls'][label]=arr
  out.append(row)
(D/'Stair_Wall_Plane_Probe.json').write_text(json.dumps(out,indent=2),'utf8')
print('WALLPLANE_JSON',str(D/'Stair_Wall_Plane_Probe.json'),flush=True)
