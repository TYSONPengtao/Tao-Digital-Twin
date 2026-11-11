exec(open(__file__.replace('analyse.py','plan.py'),encoding='utf8').read().split('fig,ax=')[0])
for n in idx:
 if any(t in n for t in ['REBUILT_COURT','Matching_Stone','WHITE_INSIDE','GRADED_INTERIOR']):print('GEO',n,idx[n]['materials'],idx[n]['vertices'],idx[n]['triangles'])
for r in json.loads((D/'Inventory.json').read_text('utf8')):
 if any(t in r['name']for t in ['SLAB_JOINED_F1','FACADE_CONTINUOUS_F1','BAY_WINDOW','GAZEBO_FLOOR','COURTYARD_WEST','Continuous_White_Courtyard']):print('BOUNDS',r['name'],r['bounds'])
segs=json.loads((W/'v16/Drain_Segments.json').read_text());east=[r for r in segs if r['ci']==0 and 44<=r['j']<=61];print('EAST',json.dumps(east))
n='SITE_V12_REBUILT_COURT_0_-20_0_Geometry';a=source(n);t=a['v'][a['f']];mi=a['mi'];print('COURT_MATERIALS',[(m,int((mi==i).sum()))for i,m in enumerate(idx[n]['materials'])]);print('COURT_TOP_Z',np.unique(np.round(t[(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-7)].reshape(-1,3)[:,2],4)).tolist())
