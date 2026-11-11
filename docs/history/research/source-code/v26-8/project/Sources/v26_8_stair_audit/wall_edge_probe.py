exec((__import__('pathlib').Path(__file__).parent/'diagnose.py').read_text('utf8').split('out=')[0])
T=aa['v'][aa['f']];N=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);A=np.linalg.norm(N,axis=1)/2;N=N/np.maximum(A[:,None]*2,1e-30); C=T.mean(1)
rows=[]
for side,y0,y1 in [('south',7.42,7.70),('north',9.40,9.681)]:
 sel=(T.max(1)[:,0]>=5.2)&(T.min(1)[:,0]<=7.8)&(T.max(1)[:,1]>=y0)&(T.min(1)[:,1]<=y1)&(T.max(1)[:,2]>=-.45)&(T.min(1)[:,2]<=7.05)
 sums={}
 for i in np.flatnonzero(sel):
  mat=J['V26_3_House_Connected_Walls_And_Stairs']['materials'][int(aa['mi'][i])];axis=np.argmax(abs(N[i]));plane=round(float(C[i,axis]),5)if abs(N[i,axis])>.9999 else None;k=(mat,int(axis),plane,round(float(N[i,axis]),4))
  if k not in sums:sums[k]={'area':0.,'lo':T[i].min(0),'hi':T[i].max(0),'triangles':[]}
  q=sums[k];q['area']+=A[i];q['lo']=np.minimum(q['lo'],T[i].min(0));q['hi']=np.maximum(q['hi'],T[i].max(0));q['triangles'].append(int(i))
 groups=[{'material':k[0],'axis':k[1],'plane':k[2],'normal':k[3],'area_m2':float(q['area']),'lo':q['lo'].tolist(),'hi':q['hi'].tolist(),'triangles':q['triangles']}for k,q in sums.items()]
 rows.append({'side':side,'groups':groups})
 print(side)
 for q in groups:
  if q['axis']==1:print(q)
out=[]
for x in [5.4,6.3,7.4]:
 for y in [7.42,7.44,7.48,7.50,7.52,7.54,7.58,7.6,7.65,9.55,9.56,9.57,9.58,9.6,9.65,9.67,9.68]:
  for z in[-.1,.5,1.0,1.4,1.7,2.3,2.8,3.44,3.6,4.2,4.9,5.4,5.8,6.4,6.9]:
   hs=house.ray_cast([x,y-.05,z],[x,y+.05,z]);out.append({'point':[x,y,z],'hits':[{'position':list(h.position),'normal':list(h.normal)}for h in hs]})
(D/'Wall_Edge_Material_Groups.json').write_text(json.dumps(rows,indent=2),'utf8');(D/'Wall_Edge_Horizontal_Rays.json').write_text(json.dumps(out,indent=2),'utf8')
