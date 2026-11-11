from v26_2_common import *
FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
for n in ['SITE_V21_GATE_REFERENCE_LAYER_01_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']:
 r=J[n];a=np.load(FD/r['file']);m=solid(a['v'],a['f']);print(n,len(m.decompose()),flush=True)
 if len(m.decompose())<30:
  for k,p in enumerate(m.decompose()):print('PART',k,round(p.volume(),6),np.round(p.bounding_box(),5).tolist(),flush=True)
 for z in [-.55,-.4,0.,1.,2.,2.9]:
  for x in [8.15,8.25,8.3,8.4,8.6,8.8,9.,9.2,9.4,9.5]:
   hs=m.ray_cast([x,-11.7,z],[x,-10.7,z]);print('SIDEWALL_Y',z,x,[round(float(h.position[1]),5)for h in hs],flush=True)
