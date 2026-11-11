from v26_2_common import *
D=W/'v26_3'/'Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(D/r['file']);m=solid(a['v'],a['f'],'actual current house')
for x in [12.7,12.7875,12.9]:
 for y in [7.3,7.49,7.51,7.6,8.55,9.49,9.51,9.59]:
  hs=m.ray_cast([x,y,2.4],[x,y,3.8]);print('CEILING_XY',x,y,[(list(np.round(h.position,5)),list(np.round(h.normal,4)))for h in hs])
print('DOOR_FLOOR')
for fl in [1,2,3]:
 floor=[-.45,3.45,7.05][fl-1]
 for x in [3.7,3.9,4.1,8.9,9.1,9.3]:
  for y in [2.5,2.7,3.1]:
   hs=m.ray_cast([x,y,floor+.15],[x,y,floor-.1]);tops=[h for h in hs if h.normal[2]>.9];print(fl,x,y,[(np.round(h.position[2],6))for h in tops])
