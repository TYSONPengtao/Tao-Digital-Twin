from v26_2_common import *
PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
for n,r in PI.items():
 if n.startswith(('STAIR_','V24_31_F','V26_Stair_')):
  print(n,np.round(np.array(r['bounds']),6).tolist() if 'bounds'in r else 'no bounds')
  if n.startswith(('STAIR_F','STAIR_LANDING')):
   a=np.load(PD/r['file']);print('GEOM',a['v'].min(0).tolist(),a['v'].max(0).tolist(),'mats',r['materials'])
