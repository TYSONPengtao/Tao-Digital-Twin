from v26_2_common import *
D=W/'v26_9';FD=W/'v26_8/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
res={}
for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_11_Storage_Curved_Rear_Interior_White_Finish','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','V26_2_Continuous_Ground_And_Perimeter_Shell']:
 r=J[n];a=np.load(FD/r['file']);t=a['v'][a['f']];c=t.mean(1);no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-20)
 rows=[]
 for i,mat in enumerate(r['materials']):
  ids=(a['mi']==i)&(c[:,0]>12.7)&(c[:,0]<14.5)&(c[:,1]>-16.7)&(c[:,1]<-9.0)&(c[:,2]>.05)
  if not ids.any():continue
  rows.append({'material':mat,'triangles':int(ids.sum()),'bounds':[t[ids].min((0,1)).tolist(),t[ids].max((0,1)).tolist()], 'normal_means':no[ids].mean(0).tolist()})
 res[n]=rows
 if n=='V26_2_Continuous_Ground_And_Perimeter_Shell':
  m=solid(a['v'],a['f'],n);bay=json.loads((W/'v24_10/Prepared_Geometry.json').read_text())['guard_bays'][0];aa=np.array(bay['a']);bb=np.array(bay['b']);u=(bb-aa)/np.linalg.norm(bb-aa)
  hits=[]
  for z in [.0,.3,.51,.60]:
   p=[*(aa+.2*u),z];q=[*(aa-1.3*u),z];hh=m.ray_cast(p,q);hits.append({'z':z,'hits':[{'p':list(h.position),'n':list(h.normal)}for h in hh]})
  res['fence_wall_hits']=hits
core=json.loads((W/'v26_3/Prepared_House.json').read_text())['proof']['retained_core_components']
res['rear_room_cores']=[c for c in core if c['name'].startswith('KZ_') and abs((c['bounds_m'][0][1]+c['bounds_m'][1][1])/2-7.3)<.02]
(D/'Site_Probe.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),'utf8')
for k,v in res.items():print(k,json.dumps(v,ensure_ascii=False)[:6000])
