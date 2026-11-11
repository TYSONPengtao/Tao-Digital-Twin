from v26_2_common import *
D=W/'v26_6/Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(D/r['file']);m=solid(a['v'],a['f']);print('NATIVE_V26_6_CURRENT')
for fl,off in [(1,0),(2,3.75)]:
 print('FLOOR',fl)
 for x in [5.19,5.2,5.21,5.25,5.299,5.301,5.31,5.35,5.4,5.45]:
  hits=m.ray_cast([x,9.05,1.7+off],[x,9.05,.95+off]);print('TOP',x,[(list(h.position),list(h.normal))for h in hits if h.normal[2]>.8])
 for z in [1.32,1.35,1.36,1.37,1.38,1.394,1.40,1.42,1.48]:
  hits=m.ray_cast([5.6,9.05,z+off],[4.7,9.05,z+off]);print('FRONT',z,[(list(h.position),list(h.normal))for h in hits])
