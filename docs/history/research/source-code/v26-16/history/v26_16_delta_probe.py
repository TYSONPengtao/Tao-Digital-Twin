from v26_2_common import *
D=W/'v26_16';j=json.loads((D/'Prepared.json').read_text('utf8'));rows=json.loads((D/'Input/Source_Index.json').read_text('utf8'))['objects'];hn='V26_3_House_Connected_Walls_And_Stairs';r=next(r for r in rows if r['name']==hn);a=np.load(D/'Input'/r['file']);b=np.load(D/'Prepared'/(hn+'.npz'));old=solid(a['v'],a['f']);new=solid(b['v'],b['f']);scopes=[cube(*q['scope_bounds_m'])for q in j['proof']['nodes']+j['proof']['balcony_corner_ownership']];scopes.append(cube([9.0999,1.0999,10.219999],[13.0001,2.4001,10.4004]));mask=union(scopes)
for label,m in[('outside_add',(new-old)-mask),('outside_remove',(old-new)-mask)]:
 print(label,m.volume(),m.bounding_box(),len(m.decompose()))
 for part in m.decompose():
  if abs(part.volume())>1e-8:print(' PART',part.volume(),part.bounding_box())
