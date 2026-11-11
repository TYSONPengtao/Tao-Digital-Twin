from v26_2_common import *
a=np.load(W/'v26_7_column_audit/final_candidate/V26_3_House_Connected_Walls_And_Stairs.npz');t=a['v'][a['f']];ar=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;ix=np.flatnonzero(ar<=1e-18)
print('ZERO',len(ix),flush=True)
for i in ix[:30]:print(i,t[i].tolist(),np.linalg.norm(t[i]-np.roll(t[i],1,axis=0),axis=1).tolist(),flush=True)
