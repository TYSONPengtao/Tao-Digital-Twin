from v26_2_common import *
D=W/'v26_5/Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};n='V26_3_House_Connected_Walls_And_Stairs';r=J[n];a=np.load(D/r['file']);m=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],n)
def stats(m,label):
 b=m.to_mesh64();v=np.array(b.vert_properties[:,:3]);f=np.array(b.tri_verts);tr=v[f];ar=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;keys={};dup=[]
 for i,t in enumerate(tr):
  k=tuple(sorted(map(tuple,np.round(t,7))))
  if k in keys:dup.append((i,keys[k]))
  keys[k]=i
 print(label,'TRIS',len(f),'DUP',len(dup),'MIN_AREA',ar.min(),'STATUS',m.status(),'VOLUME',m.volume(),flush=True)
 if label=='native':
  for i,j in dup[:8]:print('DUP_DETAIL',i,j,'areas',ar[i],ar[j],'coords',tr[[i,j]].tolist(),flush=True)
 return not dup and ar.min()>1e-18
stats(m,'native')
for tol in [1e-6,1e-5,2.5e-5,5e-5]:
 trial=m.set_tolerance(tol).simplify(tol);trial=clean(trial);stats(trial,str(tol));print('SYMMETRIC_DIFF',((trial-m)+(m-trial)).volume(),flush=True)
for decimals in [7,6,5]:
 v,rev=np.unique(np.round(a['v'],decimals),axis=0,return_inverse=True);f=rev[a['f']];tr=v[f];ok=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)>1e-18
 trial=mf.Manifold(mf.Mesh64(np.array(v,copy=True),np.array(f[ok],np.uint64,copy=True)));print('ROUND_RAW',decimals,'status',trial.status(),'dropped',int((~ok).sum()),flush=True)
 if trial.status()==mf.Error.NoError:
  trial=clean(trial);stats(trial,'round '+str(decimals));print('SYMMETRIC_DIFF',((trial-m)+(m-trial)).volume(),flush=True)
 else:
  ff=f[ok];keys,rev2,counts=np.unique(np.sort(ff,axis=1),axis=0,return_inverse=True,return_counts=True);keep=counts[rev2]==1;trial=mf.Manifold(mf.Mesh64(np.array(v,copy=True),np.array(ff[keep],np.uint64,copy=True)));print('ROUND_CANCEL',decimals,'status',trial.status(),'pairs',int((~keep).sum()),flush=True)
  if trial.status()==mf.Error.NoError:stats(clean(trial),'round_cancel '+str(decimals));print('SYMMETRIC_DIFF',((trial-m)+(m-trial)).volume(),flush=True)
