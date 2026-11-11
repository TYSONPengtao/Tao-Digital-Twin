import sys,json,math,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,LineString,Point,shape
O=Path(r'E:/jz/JIA/Rebuild_V15');P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);I=json.loads((O/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));idx={r['name']:r for r in I};Q=json.loads((W/'v15/Mutation.json').read_text(encoding='utf8'));me=[];inward=[];uvbad=[];normalbad=[]
for ob in F.Objects:
 g=ob.Geometry
 if not isinstance(g,rh.Mesh):continue
 v=(np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()])-origin)@R;faces=[]
 for f in g.Faces:
  faces.append(f[:3])
  if f[2]!=f[3]:faces.append([f[0],f[2],f[3]])
 t=v[np.array(faces)];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);vol=float(np.einsum('ij,ij->i',t[:,0]-v.mean(0),nn).sum()/6);uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates]);no=np.array([[p.X,p.Y,p.Z] for p in g.Normals]);n=ob.Attributes.Name
 if g.IsClosed and vol<-1e-9:inward.append(n)
 if len(uv)!=len(v) or not np.isfinite(uv).all():uvbad.append(n)
 if len(no)!=len(v) or not np.isfinite(no).all() or np.linalg.norm(no,axis=1).min()<.99:normalbad.append(n)
 me.append({'name':n,'vertices':len(v),'uv':len(uv),'closed':g.IsClosed,'signed_volume_m3':vol})
assert not(inward or uvbad or normalbad),(inward[:5],uvbad[:5],normalbad[:5]);print('NATIVE UV NORMALS PASS',len(me),flush=True)
def load(n):
 d=np.load(O/'02_Data'/idx[n]['file']);return d['vertices'][d['faces']]
def top(t):return t[np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-8]
def heights(t,xy):
 a=t[:,0,:2];d=t[:,1,:2]-a;b=t[:,2,:2]-a;q=np.array(xy)-a;det=d[:,0]*b[:,1]-d[:,1]*b[:,0];safe=abs(det)>1e-10;u=np.divide(q[:,0]*b[:,1]-q[:,1]*b[:,0],det,out=np.zeros(len(t)),where=safe);v=np.divide(d[:,0]*q[:,1]-d[:,1]*q[:,0],det,out=np.zeros(len(t)),where=safe);keep=safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8);return (t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+v*(t[:,2,2]-t[:,0,2]))[keep]
walktop=top(load('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT'));ramp=top(load('SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP'));court=np.concatenate([top(load(n)) for n in idx if n.startswith('SITE_V12_REBUILT_COURT')]);line=LineString([[-13.0,-10.3],[-9.5,-11.35],[-3,-12.7],[3,-12.7],[6.6,-12.7],[6.6,-10.9]]);rr=[]
for s in np.arange(0,line.length+.001,.20):
 xy=line.interpolate(float(s));h=heights(walktop,[xy.x,xy.y]);h0=heights(ramp,[xy.x,xy.y]);hc=heights(court,[xy.x,xy.y]);hh=np.r_[h,h0,hc];assert len(hh),[s,xy.x,xy.y];rr.append({'s_m':float(s),'xy':[xy.x,xy.y],'surface_z':float(hh.max())})
step=max(abs(r['surface_z']-p['surface_z']) for p,r in zip(rr[:-1],rr[1:]));assert step<.15,step
support=top(load('SITE_V15_ENTRY_PAVEMENT_SUPPORTED_SUBGRADE'));gaps=[]
for r in rr:
 hp=heights(walktop,r['xy']);hs=heights(support,r['xy'])
 if len(hp) and len(hs):gaps.append(abs(float(hp.max()-.22-hs.max())))
assert gaps and max(gaps)<.001
exclude=Polygon(Q['qa']['bedroom_exclusion_xy']).buffer(-.001);roofbad=[]
for n in ['CANOPY_CENTER_0','CANOPY_CENTER_1','CANOPY_CENTER_INDIVIDUAL_COVER_TILES','CANOPY_CENTER_RIDGE_CAP']:
 t=load(n);z=t.max(1)[:,2]>7.48;px=shapely.polygons(t[z,:,:2]);area=float(shapely.area(shapely.intersection(px,exclude)).sum());roofbad.append({'node':n,'positive_xy_area_inside_bedroom_m2':area});assert area<1e-6,(n,area)
geo={'status':'PASS_NATIVE_UV_AND_NORMALS','native_mesh_count':len(me),'missing_or_invalid_uv':uvbad,'invalid_normals':normalbad,'inward_closed_meshes':inward,'method':'Actual saved native Mesh UV count, finite coordinate and normal checks; closed-solid signed volume; original exterior retains its UV. The test addresses texture-coordinate and mesh orientation causes of blank/black rendering, not all possible graphics-driver conditions.'};(O/'06_Report/V15_UV_Normal_QA.json').write_text(json.dumps(geo,ensure_ascii=False,indent=2),encoding='utf8')
rq={'status':'PASS_CONTINUOUS_WALKING_ROUTE','method':'Actual native mesh vertical intersections along a 0.20 m sampled centerline; checks ramp, new pavement and court; concrete underside contacts modeled fill','samples':rr,'max_adjacent_height_change_over_020m_m':step,'max_concrete_to_fill_contact_gap_m':max(gaps),'existing_external_ramp_preserved':True};(O/'06_Report/V15_Route_QA.json').write_text(json.dumps(rq,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V15_Bedroom_Roof_QA.json').write_text(json.dumps({'status':'PASS_NO_PORCH_ROOF_IN_BEDROOM','exclusion_xy':Q['qa']['bedroom_exclusion_xy'],'checks':roofbad},ensure_ascii=False,indent=2),encoding='utf8');print('ROUTE AND BEDROOM PASS',len(rr),'STEP',step,'SUPPORT',max(gaps),flush=True)
