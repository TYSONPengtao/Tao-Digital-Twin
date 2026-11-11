exec(open('work/v18_probe.py',encoding='utf8').read().split('for r in I:')[0])
ii={r['name']:r for r in I}
def hits(n,p):
 d=np.load(B/'02_Data'/ii[n]['file']);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[abs(no[:,2])>1e-9];p=np.array(p);t=t[(t[:,:,:2].min(1)<=p+1e-6).all(1)&(t[:,:,:2].max(1)>=p-1e-6).all(1)];zs=[]
 for q in t:
  a=np.column_stack([q[1,:2]-q[0,:2],q[2,:2]-q[0,:2]]);uv=np.linalg.solve(a,p-q[0,:2])
  if (uv>=-1e-6).all() and uv.sum()<=1+1e-6:zs.append(float(q[0,2]+uv@(q[1:,2]-q[0,2])))
 return sorted(set(round(z,5) for z in zs))
for p in [[21.45,-13],[21.55,-13],[21.64,-13],[21.8,-13],[22,-13],[22.506,-13],[20,-16.2],[20,-16.33],[20,-16.4],[20,-16.6],[20,-17.25],[16,-16.20],[16,-16.33],[16,-16.5]]:
 print('XY',p)
 for n in ['SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE','SITE_V17_OUTER_STORAGE_PLINTH_CAP_RETURN','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE','SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE','SITE_V16_GRADED_INTERIOR_SOIL','SITE_V14_ORIGINAL_EXTERIOR_3']:
  z=hits(n,p)
  if z:print(n,z)
