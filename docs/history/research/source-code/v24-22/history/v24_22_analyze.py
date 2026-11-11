from v24_22_common import *
names=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_03_Kitchen_Rear_Gable_Wall','V24_Kitchen_Gable_Upper_Brick_Infill','V24_17_Kitchen_North_Inner_Gable_Limewash','V24_17_Kitchen_South_Inner_Gable_Limewash','SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry']
ms={n:load(n)for n in names}
contours={'sections':{},'plans':{}}
for y in [-11.645,-11.630,-2.945,-2.930,-11.24,-2.96]:
 contours['sections'][y]={n:[pp.tolist() for pp in m.rotate([-90,0,0]).slice(-y).to_polygons()] for n,m in ms.items()}
for z in [1.,2.35,3.0]:
 contours['plans'][z]={n:[pp.tolist() for pp in m.slice(z).to_polygons()] for n,m in ms.items()}
(D/'Wall_Contours_Before.json').write_text(json.dumps(contours))
for n in ['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_16_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_18_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_29_Geometry','SITE_KITCHEN_V12_BEFORE_WOOD_35_Geometry']:
 m=load(n);cs=[]
 for c in m.decompose():
  v=c.to_mesh64().vert_properties[:,:3];lo=v.min(0);hi=v.max(0);cs.append({'lo':lo.tolist(),'hi':hi.tolist(),'volume':c.volume()})
 (D/(n+'_Components.json')).write_text(json.dumps(cs,indent=2))
 print('COMPONENTS',n,len(cs),flush=True)
 for c in cs:
  if 'FRAMES'in n and c['hi'][0]>12.7:print('EAST_FRAME',np.round(c['lo'],3),np.round(c['hi'],3),flush=True)
for n,m in ms.items():
 d=source(n);t=d['v'][d['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(no,axis=1);no/=np.maximum(a[:,None],1e-30);cc=t.mean(1)
 print('WALL',n,'vol',m.volume(),'bodies',len(m.decompose()),flush=True)
 for label,sel in [('NORTH_INNER',(no[:,1]<-.5)&(cc[:,1]>-3.1)),('SOUTH_INNER',(no[:,1]>.5)&(cc[:,1]<-11.4)),('EAST_INNER',(no[:,0]<-.5)&(cc[:,0]>12.7)&(cc[:,1]>-11.95)&(cc[:,1]<-2.6))]:
  print(' INNER',label,[(INDEX[n]['materials'][i],float(a[sel&(d['mi']==i)].sum()/2))for i in np.unique(d['mi'][sel])],flush=True)
print('ANALYSIS_DONE',flush=True)
