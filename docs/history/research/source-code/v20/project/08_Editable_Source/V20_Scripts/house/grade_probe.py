from pathlib import Path
exec((Path(__file__).parent/'inventory.py').read_text().split('rows=[]')[0])
for r in I:
 n=r['name']
 if n.startswith('SITE_V16') or n.startswith('SITE_V12_REBUILT_COURT') or n in ['SLAB_JOINED_F1']:
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];b=np.array([v.min(0),v.max(0)])
  if np.all(b[1]>[2,-4,-2]) and np.all(b[0]<[11,1.0,2]):
   t=v[d['faces']];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9
   print(n,np.round(b,4).tolist(),'TOPZ',np.round([t[up,:,2].min(),t[up,:,2].max()],4).tolist())
   print('METADATA',json.dumps(r['element'],ensure_ascii=False)[:1000])
   if n.startswith('SITE_V12_REBUILT_COURT'):print('UNIQUE_X',np.unique(np.round(v[:,0],5)).tolist(),'UNIQUE_Y',np.unique(np.round(v[:,1],5)).tolist())
