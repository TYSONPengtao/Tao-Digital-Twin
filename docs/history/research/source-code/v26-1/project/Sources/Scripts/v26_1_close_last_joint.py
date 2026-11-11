from v26_1_common import *
# Close the small inherited notch under the old secondary frieze. The new
# brick segment already owns the wall above; extend only its first 400mm.
FD=D/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};n='V26_1_Secondary_Wall_Continuous_Upper_Brick';a=np.load(FD/J[n]['file']);m=tracked(a['v'],a['f'],J[n]['materials'],a['mi'],a['uv'],n)
U=np.array([1.,.098]);U/=np.linalg.norm(U);N=np.array([-U[1],U[0]]);A=np.array([10.80,-16.84174904]);bridge=section([[-.16,1.95],[.16,1.95],[.16,2.46],[-.16,2.46]],.445).transform(np.c_[np.r_[N,0.],[0,0,1.],np.r_[U,0.],np.r_[A-U*.035,0.]])
m+=finish(bridge,'M_V24_20_Shared_AsBuilt_Perimeter_Brick','closed inherited notch at branch joint');row,m=export(n,m,'Close the residual old secondary-wall notch below its retired frieze; keep the original registered wall axis')
a=np.load(D/row['file']);v=a['v'];f=a['f'];mi=a['mi'].copy();t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-25);mats=row['materials'];white='M_V24_11_Plain_White_Limewash';outer='M_V26_1_Reference_Wall_Rubble_Stone_Limewash_Brick'
for ma in [white,outer]:
 if ma not in mats:mats.append(ma)
mi[no[:,1]>.45]=mats.index(white);mi[no[:,1]<-.45]=mats.index(outer);np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=a['uv']);row['materials']=mats
(D/'Last_Joint.json').write_text(json.dumps({'object':row,'bridge_volume_m3':bridge.volume(),'reason':'A small dark notch exposed by removal of the erroneous old gable was closed with finite brick continuity; inward face remains white.'},ensure_ascii=False,indent=2),encoding='utf8');print('LAST_JOINT_PREPARED',len(f),flush=True)
