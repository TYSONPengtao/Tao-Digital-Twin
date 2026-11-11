import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,LineString,box
from shapely.geometry.polygon import orient
from v24_11_geometry import *
D=W/'v24_11';OUT={'replace':[],'add':[],'proof':{}};I={r['name']:r for r in json.loads((D/'Inventory.json').read_text(encoding='utf8'))}
def solid(v,f,name=''):
 for dec in [7,6,5]:
  vv,ii=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ii[f];ok=(ff[:,0]!=ff[:,1])&(ff[:,1]!=ff[:,2])&(ff[:,2]!=ff[:,0]);ff=ff[ok];ok=np.linalg.norm(np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]),axis=1)>1e-13;ff=ff[ok]
  m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(vv,dtype=np.float64),np.ascontiguousarray(ff,dtype=np.uint64)))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 raise RuntimeError((name,m.status(),m.volume()))
def native(n,warpfn=None):
 d=np.load(D/(n+'.npz'));v=d['v'];v=np.array([warpfn(p)for p in v])if warpfn else v;return solid(v,d['f'],n)
def cube(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
def data(m):
 assert m.status()==mf.Error.NoError and m.volume()>0,(m.status(),m.volume());d=m.to_mesh64();return {'v':np.asarray(d.vert_properties[:,:3]).tolist(),'f':np.asarray(d.tri_verts).tolist()}
def add(n,m,mat,new=False,**extra):
 OUT['add'if new else'replace'].append({'name':n,'parts':[{'material':mat,**data(m)}],**extra});print('PREPARED',n,m.volume(),len(m.decompose()),flush=True)
def variable_prism(poly,z0,zfn):
 poly=orient(poly,1);cs=mf.CrossSection([np.array(poly.exterior.coords)[:-1]]);d=cs.extrude(1).to_mesh64();v=np.asarray(d.vert_properties[:,:3]).copy();f=np.asarray(d.tri_verts).copy()
 for p in v:p[2]=z0+p[2]*(zfn(*p[:2])-z0)
 return solid(v,f,'variable prism')
def unions(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1.])
 if np.linalg.norm(v)<1e-8:v=np.array([1.,0,0])
 v/=np.linalg.norm(v);n=np.cross(u,v);T=np.c_[v,n,u,(a+b)/2];return mf.Manifold.cube([w,d,float(np.linalg.norm(b-a))],True).transform(T)
def post(x,y,z0,z1,r=.106):return mf.Manifold.cylinder(z1-z0,r,r,24).translate([x,y,z0])

# Delete the previous three forward gallery columns, their braces, and the
# gallery purlin that wrongly followed the railing. Rear room supports remain.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';m=native(n);cut=cube([13.24,-17.2,-.43],[18.54,-15.09,3.25]);m=m-cut
# Fit surviving roof-bearing timber; all lower window and door joinery is fixed.
dd=m.to_mesh64();vv=np.asarray(dd.vert_properties[:,:3]).copy();vv=np.array([structure_warp(p)for p in vv]);m=solid(vv,np.asarray(dd.tri_verts),n+' roof fit')
add(n,m,I[n]['materials'][0],transfer_original_materials_uv=True)
n='SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry';m=native(n)-cube([13.15,-17,-.5],[18.60,-15.15,0]);add(n,m,'M_Stone')
postproof=[];heads=[]
for i,(x,y)in enumerate(POSTS):
 head=roof_z(x,y)-.155;heads.append([x,y,head-.09]);col=post(x,y,-.237,head+.035);add(f'V24_11_Storage_Veranda_Column_{i+1}',col,'M_V18_Aged_Storage_Timber',True)
 base=cube([x-.175,y-.175,-.424],[x+.175,y+.175,-.249])+cube([x-.155,y-.155,-.249],[x+.155,y+.155,-.219]);add(f'V24_11_Storage_Veranda_Column_Base_{i+1}',base,'M_Stone',True)
 postproof.append({'center_xy':[x,y],'foot_z':-.237,'head_z':head+.035,'vertical':True,'entry_column_behind_wall':i==0})
members=[beam(heads[0],heads[1],.19,.23)]
u=np.array(POSTS[1])-POSTS[0];u/=np.linalg.norm(u)
for i,(x,y)in enumerate(POSTS):
 for sign in[-1,1]:
  p=np.array([x,y])+sign*.42*u
  if p[0]<13.20 or p[0]>18.57:continue
  z=roof_z(x,y)-.155;members.append(beam([x,y,z-.48],[*p,roof_z(*p)-.26],.075,.095))
 # Bearing block under the diagonal purlin.
 members.append(cube([x-.15,y-.16,heads[i][2]-.09],[x+.15,y+.16,heads[i][2]+.105]))
# Front rafter tails connect the retained roof to its new eave.
for x in np.arange(13.00,18.70,.24):
 xf=max(13.30,x);y0=-15.06;ye=south_edge(xf);a=[x,y0,roof_z(xf,y0)-.11];b=[x,ye,roof_z(xf,ye)-.11]
 members.append(beam(a,b,.045,.060))
members.append(beam([12.83,south_edge(13.3),south_eave_z(13.3)-.105],[18.73,south_edge(18.73),south_eave_z(18.73)-.105],.09,.13))
add('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails',unions(members),'M_V18_Aged_Storage_Timber',True)
OUT['proof']['veranda_columns']=postproof;OUT['proof']['removed_old_front_column_centers']=[[13.6444,-15.829],[15.7202,-15.807],[18.2594,-15.7803]]
OUT['proof']['column_axis_degrees']=math.degrees(math.atan2(POSTS[1][1]-POSTS[0][1],POSTS[1][0]-POSTS[0][0]));OUT['proof']['rail_axis_degrees']=math.degrees(math.atan(.10589))

# Continuous storage back wall follows the north foundation arc, with returns
# into both gables. The old straight back wall and its inner finish are removed.
xs=np.linspace(13.20,18.65,90);curve=np.array([[x,north_boundary(x)]for x in xs]);backpoly=Polygon(list(curve)+[[x,y-.285]for x,y in curve[::-1]])
cutpoly=Polygon([[13.245,-9.63],[18.72,-11.13],[18.72,-7.8],[13.245,-7.8]])
cutwall=variable_prism(cutpoly,-.60,lambda x,y:6.0)
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';m=native(n,masonry_warp);m=m-cutwall
parts=[variable_prism(backpoly,-.43,lambda x,y:float(np.dot([x,y,1],N))-.105)]
for x,y0 in[(13.40,-9.70),(18.52,-11.19)]:
 ye=north_boundary(x)-.14;pp=box(x-.135,y0,x+.135,ye+.07);parts.append(variable_prism(pp,-.43,lambda xx,yy:roof_z(xx,yy)-.105))
# Kitchen rear/outer cheek continues without a pavement-width notch or a
# detached lower return. Its outside trace follows the existing retaining base.
kpath=np.array([[13.13,-8.86],[13.53,-8.276],[14.244,-3.282],[14.26,-2.83]])
kpoly=LineString(kpath).buffer(.285,cap_style=2,join_style=1).intersection(Polygon([[12.90,-9.2],[13.13,-8.86],[13.53,-8.276],[14.244,-3.282],[14.26,-2.83],[13.7,-2.83],[13.0,-8.276],[12.90,-9.2]]))
def kh(x,y):
 oldx=13.583+(14.075-13.583)*(y+8.275)/4.979;return 3.298+(3.074-3.298)*(y+8.275)/4.979-.48*(x-oldx)
parts.append(variable_prism(kpoly,-.55,kh))
# Compact solid corner joins the foundation arc and the kitchen cheek.
cornerpoly=Polygon([[13.12,-9.68],[13.55,-9.68],[13.55,-8.44],[13.12,-8.69]])
parts.append(variable_prism(cornerpoly,-.55,lambda x,y:min(kh(x,y),roof_z(max(x,13.3),y)-.08)))
m=unions([m]+parts);add(n,m,'M_V24_08_AsBuilt_Kitchen_Exterior_Brick')
OUT['proof']['back_curve']=curve.tolist();OUT['proof']['kitchen_continuous_wall_trace']=kpath.tolist();OUT['proof']['masonry_connected_bodies']=len(m.decompose())
# Carry the solid cheek/miter down through the local footing, sealing the
# previous exposed paving notch at the kitchen/storage retaining-wall joint.
n='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry';base=native(n);base=unions([base,variable_prism(kpoly,-4.45,lambda x,y:-.38),variable_prism(cornerpoly,-4.45,lambda x,y:-.38)]).simplify(.00005);add(n,base,'M_V18_Storage_Rubble');OUT['proof']['continuous_footing_bodies']=len(base.decompose())
# Resolve the actual contact instead of leaving coincident exterior skins on
# the cheek: the wall starts on the fitted footing, without an overlapping
# 170 mm band that would self-shadow black in the corner.
wall=m-base;wall=wall.simplify(.00005)
wallrow=next(r for r in OUT['replace']if r['name']=='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry');wallrow['parts'][0].update(data(wall));OUT['proof']['masonry_connected_bodies']=len(wall.decompose());OUT['proof']['wall_footing_overlap_volume_m3']=float((wall^base).volume());assert len(wall.decompose())==1
# Split only the exterior triangles at the material datum in double precision.
# A shared edge/intersection cache keeps one closed surface; no paired caps or
# BMesh float bisect slivers are introduced at the old/new foundation miter.
row=OUT['replace'][-1];part=row['parts'][0];V=[list(p)for p in part['v']];tri=part['f'];edges={};FF=[];MM=[];cut=-1.05
for p in V:
 if abs(p[2]-cut)<.000002:p[2]=cut
def crossing(a,b):
 if abs(V[a][2]-cut)<1e-10:return a
 if abs(V[b][2]-cut)<1e-10:return b
 key=tuple(sorted([a,b]))
 if key not in edges:
  A=np.array(V[a]);B=np.array(V[b]);p=A+(B-A)*(cut-A[2])/(B[2]-A[2]);p[2]=cut;edges[key]=len(V);V.append(p.tolist())
 return edges[key]
for ids in tri:
 zz=[V[i][2]for i in ids]
 if max(zz)<=cut+1e-10:FF.append(ids);MM.append(0);continue
 if min(zz)>=cut-1e-10:FF.append(ids);MM.append(1);continue
 for side in[0,1]:
  pp=[]
  for a,b in zip(ids,ids[1:]+ids[:1]):
   aa=V[a][2]<=cut if side==0 else V[a][2]>=cut;bb=V[b][2]<=cut if side==0 else V[b][2]>=cut
   if aa and bb:pp.append(b)
   elif aa and not bb:pp.append(crossing(a,b))
   elif not aa and bb:pp.extend([crossing(a,b),b])
  pp=[p for j,p in enumerate(pp)if p!=pp[j-1]]
  for j in range(1,len(pp)-1):
   face=[pp[0],pp[j],pp[j+1]]
   if len(set(face))==3:FF.append(face);MM.append(side)
# Quantized readback simulation catches precision-related seams before save.
test=solid(np.array(V,dtype=np.float32).astype(float),np.array(FF),'foundation material split readback');print('BASE_FLOAT32_SOLID',test.status(),test.volume(),flush=True)
part.update(v=V,f=FF,face_material=MM);row['materials']=['M_V18_Storage_Rubble','M_V18_Storage_Dark_Courses']
n='SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry';m=native(n,masonry_warp)-cutwall;add(n,m,'M_Wall_Interior')
plasterpoly=Polygon([[x,y-.281]for x,y in curve]+[[x,y-.295]for x,y in curve[::-1]])
add('V24_11_Storage_Curved_Rear_Interior_White_Finish',variable_prism(plasterpoly,-.395,lambda x,y:float(np.dot([x,y,1],N))-.125),'M_Wall_Interior',True)

# Crisp three-course stone foot, matching the inner-gate plinth vocabulary.
plinth=unions([cube([3.17,-17.21,-.70],[10.88,-16.36,-.55]),cube([3.23,-17.15,-.55],[10.82,-16.42,-.29]),cube([3.19,-17.19,-.29],[10.86,-16.38,-.23])]);add('V24_11_Screenwall_Continuous_Stepped_Stone_Plinth',plinth,'M_V24_11_Screenwall_Dressed_Stone',True)
OUT['proof']['screenwall_plinth']={'steps':3,'z_range':[-.70,-.23],'one_closed_body':len(plinth.decompose())==1}
# Uniform shared-edge subdivision lets the native closed shell follow the
# curved north boundary instead of retaining a straight coarse polygon edge.
n='SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry';d=np.load(D/(n+'.npz'));v,inv=np.unique(np.round(d['v'],7),axis=0,return_inverse=True);f=inv[d['f']]
for level in range(6):
 ed=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);ed=np.sort(ed,axis=1);ue,ix=np.unique(ed,axis=0,return_inverse=True);mi=ix+len(v);Nf=len(f);ab=mi[:Nf];bc=mi[Nf:2*Nf];ca=mi[2*Nf:];v=np.vstack([v,(v[ue[:,0]]+v[ue[:,1]])/2]);f=np.concatenate([np.c_[f[:,0],ab,ca],np.c_[ab,f[:,1],bc],np.c_[ca,bc,f[:,2]],np.c_[ab,bc,ca]])
v=np.array([warp(p)for p in v]);roof=solid(v,f,'subdivided roof');add(n,roof,I[n]['materials'][0]);OUT['proof']['storage_roof_subdivision_levels']=6
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,separators=(',',':')),encoding='utf8');print('PREPARATION DONE',flush=True)
