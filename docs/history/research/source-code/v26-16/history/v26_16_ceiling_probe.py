from v26_2_common import *
D=W/'v26_16';r=json.loads((D/'Prepared.json').read_text('utf8'))['objects'][0];a=np.load(D/'Prepared'/r['file']);v,f=a['v'],a['f'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(n,axis=1)/2;n/=np.maximum(ar[:,None]*2,1e-30);c=t.mean(1);s=solid(v,f);rows=[]
for x in[3.55,3.65,3.70,3.75,3.8,3.9]:
 for y in[2.25,2.3,2.35,2.4,2.45,2.5,2.6]:
  hits=s.ray_cast([x,y,2.9],[x,y,3.6]);rows.append({'xy':[x,y],'hits':[{'z':h.position[2],'n':list(h.normal)}for h in hits]})
print('RAYS',json.dumps(rows),flush=True)
ids=np.flatnonzero((c[:,0]>3.4)&(c[:,0]<4.3)&(c[:,1]>1.7)&(c[:,1]<2.9)&(c[:,2]>3.319)&(c[:,2]<3.321)&(n[:,2]<-.99));print('CEIL_MATERIALS',[(r['materials'][i],int(np.sum(a['mi'][ids]==i)),float(ar[ids][a['mi'][ids]==i].sum()))for i in np.unique(a['mi'][ids])],flush=True)
for i in ids:
 if r['materials'][a['mi'][i]]!='M_V26_3_Neutral_White_Interior_Ceiling'and ar[i]>.001:print('BAD_CEIL',r['materials'][a['mi'][i]],t[i].tolist(),flush=True)
