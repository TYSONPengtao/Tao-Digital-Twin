"""Independent check of saved V21 actual Rhino gallery meshes and preserved site interfaces."""
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf
A=Path('E:/jz/JIA/Rebuild_V20');B=Path('E:/jz/JIA/Rebuild_V21')
F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm'));assert F
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));t=math.radians(C['rotation_deg']);R=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]]);offset=np.array(C['origin'])
Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
oldI={a['name']:a for a in json.loads((A/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))}
newI={a['name']:a for a in json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
out={'status':'PENDING','native_model':str(B/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm'),'checks':[],'limitations':['Unreal Engine import/collision runtime not tested here','Photo-fitting dimensions are not a site dimensional survey']}
def check(n,ok,**meta):
 out['checks'].append({'check':n,'pass':bool(ok),**meta});assert ok,(n,meta)
def manifold(v,f):
 vv,inv=np.unique(np.round(v,9),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,m.status();return m
def real_node(n):
 ps=[]
 for ob in F.Objects:
  if not (ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')):continue
  g=ob.Geometry;assert isinstance(g,rh.Mesh)
  v=(np.array([[q.X,q.Y,q.Z] for q in g.Vertices])-offset)@R
  f=[]
  for q in g.Faces:
   a,b,c,d=q;f.append([a,b,c]);
   if c!=d:f.append([a,c,d])
  m=manifold(v,np.array(f));ps.append(m)
  check(ob.Attributes.Name+' closed positive actual mesh',g.IsValid and g.IsClosed and m.volume()>1e-10,volume_m3=m.volume())
 return mf.Manifold.batch_boolean(ps,mf.OpType.Add)
def cached(root,idx,n):
 a=np.load(root/'02_Data'/idx[n]['file']);return a,manifold(a['vertices'],a['faces'])
actual={}
for e in Q['replace']:
 n=e['name'];actual[n]=real_node(n)
 if 'FLOOR' in n:
  da,old=cached(A,oldI,n);new=actual[n];diff=(old-new).volume()+(new-old).volume()
  print('FLOOR',n,'DIFF',diff,'OLD',old.bounding_box(),'NEW',new.bounding_box(),flush=True)
  bb0=np.array(old.bounding_box());bb1=np.array(new.bounding_box());mx=float(np.max(abs(bb0-bb1)))
  check(n+' native floor envelope unchanged within ENU mesh serialization tolerance',mx<.00010 and abs(diff)<.005,symmetric_difference_m3=diff,max_bound_delta_m=mx,serialization_tolerance_m=.0001)
wood=actual['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY']
check('Saved storage joinery remains one connected positive body',sum(a.volume()>1e-8 for a in wood.decompose())==1,components=[a.volume() for a in wood.decompose()])
lane=mf.Manifold.cube([.8,.40,1.93]).translate([15.725,-15.03,-.35]);check('Saved storage central door lane unobstructed',(wood^lane).volume()<1e-8)
names=[n for n in oldI if n.startswith('SITE_SOUTH_SCREENWALL') or n.startswith('SITE_GAZEBO_') or n in ['SITE_V20_PAVILION_RAISED_WOOD_SLATS','SITE_V20_PAVILION_DECK_JOISTS_AND_FEET','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE','SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION','SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER','SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY']]
for n in names:
 check(n+' remains present',n in newI)
 aa=np.load(A/'02_Data'/oldI[n]['file']);bb=np.load(B/'02_Data'/newI[n]['file'])
 same=aa['vertices'].shape==bb['vertices'].shape and np.array_equal(aa['faces'],bb['faces']) and np.max(np.abs(aa['vertices']-bb['vertices']))<1e-8
 check(n+' verified geometry retained',same,vertices=len(aa['vertices']))
slat=np.load(B/'02_Data'/newI['SITE_V20_PAVILION_RAISED_WOOD_SLATS']['file'])['vertices']
clearance=float(slat[:,2].min()-(-.43038));check('Pavilion board underside still 50 mm above graded ground',abs(clearance-.05)<1e-5,clearance_m=clearance)
check('Pavilion principal-axis edge remains retracted',abs(float(slat[:,0].max())-3.96)<.015,max_x_m=float(slat[:,0].max()))
out['status']='PASS_ACTUAL_NATIVE_SITE_REVIEW'
(D/'Final_Native_Review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(out['status'],len(out['checks']),flush=True)
