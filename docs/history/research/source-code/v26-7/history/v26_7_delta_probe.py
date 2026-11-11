from v26_2_common import *
F=W/'v26_7/Final';O=W/'v26_6/Final';J={r['name']:r for r in json.loads((F/'Geometry_Index.json').read_text('utf8'))};I={r['name']:r for r in json.loads((O/'Geometry_Index.json').read_text('utf8'))}
n='V26_3_House_Connected_Walls_And_Stairs';a=np.load(F/J[n]['file']);o=np.load(O/I[n]['file']);after=solid(a['v'],a['f']);before=solid(o['v'],o['f']);allowed=union([cube([.1999,9.6799,z0],[12.8001,9.9003,z1])for z0,z1 in[(-.4501,3.3201),(3.45,6.9201),(7.05,10.2201)]])
out=(after-before)-allowed;print('OUT_ADDED',out.volume(),'parts',len(out.decompose()),flush=True)
for p in sorted(out.decompose(),key=lambda p:p.volume(),reverse=True)[:8]:print(p.volume(),list(p.bounding_box()),flush=True)
for n in['SITE_V21_GATE_REFERENCE_LAYER_01_Geometry','SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry']:
 a=np.load(F/J[n]['file']);m=solid(a['v'],a['f'])
 for x in[8.1,8.2]:
  hs=m.ray_cast([x,-11.33,-1],[x,-11.33,4]);print('JAMB',n,x,[(h.position[2],h.normal[2])for h in hs],flush=True)
