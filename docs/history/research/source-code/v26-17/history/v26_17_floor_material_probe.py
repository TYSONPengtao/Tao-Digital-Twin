from v26_2_common import *
D=W/'v26_17';j=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in j['objects']};prep=json.loads((D/'Prepared.json').read_text('utf8'));hn='V26_3_House_Connected_Walls_And_Stairs';src=np.load(D/'Input'/ix[hn]['file']);row=next(r for r in prep['objects']if r['name']==hn);dst=np.load(D/'Prepared'/row['file'])
points=[(9.41973,.95838),(9.55071,.93073),(9.72015,.95422),(8.97475,1.6436),(6.5,1.2),(10.5,3.5),(10.5,1.5),(9.2035,.96136)]
for label,a,mats in[('BEFORE',src,ix[hn]['materials']),('AFTER',dst,row['materials'])]:
 tr=a['v'][a['f']];n=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);ids=np.flatnonzero((n[:,2]>0)&(np.abs(tr[:,:,2]+.45).max(1)<2e-6));p=tr[ids,:,:2];u=p[:,1]-p[:,0];v=p[:,2]-p[:,0];det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
 for xy in points:
  d=np.asarray(xy)-p[:,0];s=(d[:,0]*v[:,1]-d[:,1]*v[:,0])/det;t=(u[:,0]*d[:,1]-u[:,1]*d[:,0])/det;hit=ids[(s>=-1e-6)&(t>=-1e-6)&(s+t<=1.000001)];print(label,xy,[(int(i),mats[a['mi'][i]])for i in hit])
