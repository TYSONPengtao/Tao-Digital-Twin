from v26_2_common import *
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};a=np.load(FD/J['V26_3_House_Connected_Walls_And_Stairs']['file']);m=solid(a['v'],a['f']);t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30)
q=np.array([4.4,7.55,10.220049858093262]);ids=np.flatnonzero(abs(np.einsum('ij,ij->i',n,q-t[:,0]))<3e-6)
for i in ids:
 u,v=t[i,1]-t[i,0],t[i,2]-t[i,0];p=q-t[i,0];det=(u@u)*(v@v)-(u@v)**2
 if det<1e-20:continue
 s=((v@v)*(u@p)-(u@v)*(v@p))/det;r=((u@u)*(v@p)-(u@v)*(u@p))/det
 if min(s,r)>-1e-5 and s+r<1.00001:print('AT',i,n[i],J['V26_3_House_Connected_Walls_And_Stairs']['materials'][int(a['mi'][i])],t[i].tolist())
oldD=W/'v26_6/Final';K={r['name']:r for r in json.loads((oldD/'Geometry_Index.json').read_text('utf8'))};a0=np.load(oldD/K['V26_3_House_Connected_Walls_And_Stairs']['file']);before=solid(a0['v'],a0['f']);prep=json.loads((W/'v26_7_column_audit/final_candidate/Prepared_Geometry.json').read_text('utf8'));side=union([cube(r['bounds_m'][0],r['bounds_m'][1])for r in prep['finalize']['stair_frame_wall_side_normalization']]);cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];r=next(q for q in cp if q['name']=='V26_Stair_Frame_North_Beam_F3');loss=((before^cube(*r['bounds_m']))-m)-side
print('LOSS',loss.volume(),r['bounds_m'])
for c in loss.decompose():
 v=np.array(c.to_mesh64().vert_properties[:,:3]);print('LOSS_PART',c.volume(),v.min(0).tolist(),v.max(0).tolist())
