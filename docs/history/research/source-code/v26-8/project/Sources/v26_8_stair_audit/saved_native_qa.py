"""Independent V26.8 saved stairwell tests. Reads native readback; never mutates.

The original source is used only for tread X/Z datums, not wholesale source
volume preservation: that older criterion wrongly protects the 20 mm slit.
"""
from pathlib import Path
import sys,json,hashlib,time
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube

D=W/'v26_8/Final';PD=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_8')
P=O/'Blender/Architecture_Complete_V26_8.blend';R=O/'Reports';R.mkdir(parents=True,exist_ok=True)
HN='V26_3_House_Connected_Walls_And_Stairs';GRAY='M_V24_31_Stair_Gray_Marble'
TOL=.00025;checks=[]

def ck(name,yes,**details):
 checks.append({'check':name,'pass':bool(yes),**details})
 print('CHECK',name,bool(yes),''if yes else details,flush=True)

for required in [P,D/'Geometry_Index.json',PD/'Geometry_Index.json']:
 if not required.exists():raise FileNotFoundError('Wait for final native readback before running: '+str(required))
H=hashlib.sha256(P.read_bytes()).hexdigest()
J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
I={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
a=np.load(D/J[HN]['file']);V=a['v'];F=a['f'];MI=a['mi'];MATS=J[HN]['materials']
v,ix=np.unique(V,axis=0,return_inverse=True);f=ix[F];T=v[f]
rawnormal=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0]);area=np.linalg.norm(rawnormal,axis=1)/2
N=rawnormal/np.maximum(area[:,None]*2,1e-30)
edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
duplicates=len(f)-len(np.unique(np.sort(f,axis=1),axis=0))
mesh=mf.Mesh64(np.asarray(v,np.float64),np.asarray(f,np.uint64),face_id=np.arange(len(f),dtype=np.uint64))
house=mf.Manifold(mesh)
ck('Final cache postdates the saved native model', (D/'Geometry_Index.json').stat().st_mtime>=P.stat().st_mtime-.01,
   native_mtime=P.stat().st_mtime,index_mtime=(D/'Geometry_Index.json').stat().st_mtime)
ck('Saved house is one positive closed solid with no zero duplicate or nonmanifold triangle',
   house.status()==mf.Error.NoError and house.volume()>0 and len(house.decompose())==1 and
   bool((counts==2).all())and duplicates==0 and float(area.min())>1e-18,
   status=str(house.status()),components=len(house.decompose()),volume_m3=house.volume(),
   nonmanifold_edges=int((counts!=2).sum()),duplicate_faces=int(duplicates),minimum_triangle_area_m2=float(area.min()))

def rays(p,q):
 return [{'position':list(h.position),'normal':list(h.normal)}for h in house.ray_cast(p,q)]

def inside(p):
 p=np.asarray(p,float);hs=house.ray_cast(p-[40.,0,0],p+[40.,0,0]);return sum(h.position[0]<p[0]for h in hs)%2==1

def top_at(x,y,z):
 hs=rays([x,y,z+.035],[x,y,z-.065]);hs=[q for q in hs if q['normal'][2]>.99]
 return min(hs,key=lambda q:abs(q['position'][2]-z))if hs else None

def material_at(point,normal):
 point=np.asarray(point);normal=np.asarray(normal)
 possible=np.flatnonzero((T.min(1)<=point+2e-5).all(1)&(T.max(1)>=point-2e-5).all(1)&(N@normal>.99))
 found=[]
 for i in possible:
  u=T[i,1]-T[i,0];w=T[i,2]-T[i,0];q=point-T[i,0]
  aa=float(u@u);ab=float(u@w);bb=float(w@w);aq=float(u@q);bq=float(w@q);det=aa*bb-ab*ab
  if det<1e-24:continue
  s=(bb*aq-ab*bq)/det;t=(aa*bq-ab*aq)/det
  if s>=-1e-5 and t>=-1e-5 and s+t<=1.00001 and abs(float(N[i]@q))<2e-5:
   mat=MATS[int(MI[i])]
   if mat not in found:found.append(mat)
 return found

def source_top(fl,k,x):
 row=I[f'STAIR_F{fl}_FLIGHT{k}_Geometry'];b=np.load(PD/row['file']);m=solid(b['v'],b['f'])
 y=9.05 if k==1 else 8.;hs=[q for q in m.ray_cast([x,y,10.],[x,y,-1.])if q.normal[2]>.99]
 return max(q.position[2]for q in hs)

levels=[-.44999998807907104,3.450024414,7.050000191]
mid=[1.4999511241912842,5.249951362609863]
steps=[]
for fl in[1,2]:
 for k in[1,2]:
  prior=levels[fl-1]if k==1 else mid[fl-1]
  for n in range(1,12):
   platform=n==11
   x=(5.07 if k==1 else 7.93)if platform else(7.8-(n-.5)*.26 if k==1 else 5.2+(n-.5)*.26)
   z=(mid[fl-1]if k==1 else levels[fl])if platform else source_top(fl,k,x)
   lo,hi=(8.60,9.68)if k==1 else(7.42,8.50)
   row={'floor':fl,'flight':k,'grade':n,'arrival_platform':platform,'x_m':x,'expected_z_m':float(z),
        'prior_z_m':float(prior),'riser_x_m':float(7.8-(n-1)*.26 if k==1 else 5.2+(n-1)*.26),
        'y_limits_m':[lo,hi],'mid_y_m':(lo+hi)/2}
   steps.append(row);prior=z

# Three independent transverse points ensure the former wall-edge loss
# cannot hide behind a correct centreline tread elevation.
tread_points=[];bad=[];material_bad=[];support=[]
for s in steps:
 lo,hi=s['y_limits_m'];ys=[lo+.015,s['mid_y_m'],hi-.015]
 for y in ys:
  q=top_at(s['x_m'],y,s['expected_z_m']);got=q['position'][2]if q else None
  mats=material_at(q['position'],[0,0,1])if q else[]
  allowed=[GRAY,'M_Floor']if s['arrival_platform']and s['flight']==2 else[GRAY]
  point={'floor':s['floor'],'flight':s['flight'],'grade':s['grade'],'x_m':s['x_m'],'y_m':y,
         'expected_z_m':s['expected_z_m'],'actual_z_m':got,'materials':mats}
  tread_points.append(point)
  if got is None or abs(got-s['expected_z_m'])>TOL:bad.append(point)
  if not mats or any(m not in allowed for m in mats):material_bad.append(point)
  # Eight centimetres of positive finite bearing at both inner and outer
  # edges; dimensional fit QA, not structural capacity certification.
  seat=[s['x_m'],y,s['expected_z_m']-.08]
  bearing=inside(seat);hh=rays([s['x_m'],y,s['expected_z_m']-.001],[s['x_m'],y,s['expected_z_m']-1.1])
  exits=[h for h in hh if h['normal'][2]<-.7]
  support.append({**point,'point_80mm_below_top_is_solid':bearing,'finite_bottom_within_1_1m':bool(exits),
                  'first_bottom_z_m':exits[0]['position'][2]if exits else None})
ck('All44 original X/Z stair grades match at inner middle and wall-side stations',not bad,
   grades=len(steps),stations=len(tread_points),tolerance_m=TOL,failures=bad)
ck('All40 tread tops and both half landings have one gray-marble surface owner',not material_bad,
   stations=len(tread_points),upper_storey_arrival_allows_original_floor_material=True,failures=material_bad)
support_bad=[q for q in support if not q['point_80mm_below_top_is_solid']or not q['finite_bottom_within_1_1m']]
ck('Each tread and landing has positive finite bearing across its full width',not support_bad,
   support_depth_test_m=.08,stations=len(support),failures=support_bad)

# Riser X coordinates are measured independently, so unchanged top heights
# cannot conceal a tread run shortened or shifted in plan.
riser_samples=[];riser_bad=[]
for s in steps:
 x=s['riser_x_m'];sign=-1 if s['flight']==1 else 1;z=(s['prior_z_m']+s['expected_z_m'])/2;y=s['mid_y_m']
 p=[x-sign*.025,y,z];q=[x+sign*.025,y,z];hs=rays(p,q)
 entering=[h for h in hs if h['normal'][0]*sign<-.99]
 hit=min(entering,key=lambda h:abs(h['position'][0]-x))if entering else None
 row={'floor':s['floor'],'flight':s['flight'],'grade':s['grade'],'expected_riser_x_m':x,
      'z_mid_rise_m':z,'actual_x_m':hit['position'][0]if hit else None}
 riser_samples.append(row)
 if not hit or abs(hit['position'][0]-x)>TOL:riser_bad.append(row)
ck('All44 original riser X stations and22 rises per storey are preserved',not riser_bad,
   risers=len(riser_samples),failures=riser_bad)

wall_rays=[];wall_bad=[];inner_rays=[];inner_bad=[]
for s in steps:
 k=s['flight'];sign=1 if k==1 else -1;wall=9.68 if k==1 else 7.42;edge=8.60 if k==1 else 8.50
 for depth in[.010,.040]:
  x=s['x_m'];y=s['mid_y_m'];z=s['expected_z_m']-depth
  p=np.array([x,y,z]);q=np.array([x,wall+sign*.012,z]);hs=rays(p.tolist(),q.tolist())
  maxlen=abs(q[1]-p[1]);premature=[h for h in hs if h['normal'][1]*sign>.9 and
               1e-5<(h['position'][1]-y)*sign<maxlen-1e-5]
  occupied=inside(p.tolist())and inside(q.tolist())
  row={'floor':s['floor'],'flight':k,'grade':s['grade'],'depth_below_tread_m':depth,
       'from':p.tolist(),'to':q.tolist(),'ray_hits':hs,'both_ends_solid':occupied,'premature_air_exit':premature}
  wall_rays.append(row)
  if not occupied or premature:wall_bad.append(row)
  # At actual treads the ray must leave at the inner edge, with no later
  # material within the well. Arrival platforms remain whole across it.
  q=np.array([x,8.55,z]);hs=rays(p.tolist(),q.tolist());signin=-sign
  exits=[h for h in hs if h['normal'][1]*signin>.9]
  if s['arrival_platform']:
   passed=inside(q.tolist())and not exits
  else:
   first=exits[0]if exits else None
   reentry=[h for h in hs if h['normal'][1]*signin<-.9 and
            (h['position'][1]-edge)*signin>.0003]
   passed=bool(first)and abs(first['position'][1]-edge)<=TOL and not reentry and not inside(q.tolist())
  row={'floor':s['floor'],'flight':k,'grade':s['grade'],'arrival_platform':s['arrival_platform'],
       'depth_below_tread_m':depth,'expected_inner_edge_y_m':None if s['arrival_platform']else edge,
       'from':p.tolist(),'to':q.tolist(),'ray_hits':hs,'pass':bool(passed)}
  inner_rays.append(row)
  if not passed:inner_bad.append(row)
ck('Every grade joins its actual wall-side body with no residual180mm or other air cavity',not wall_bad,
   grades=44,transverse_rays=len(wall_rays),depths_below_tread_m=[.010,.040],failures=wall_bad)
ck('Every tread terminates at the new inner well edge while all arrival platforms remain whole',not inner_bad,
   transverse_rays=len(inner_rays),failures=inner_bad)

well=[];well_bad=[]
for x in[5.40,6.30,7.50]:
 for y in[8.52,8.55,8.58]:
  hs=rays([x,y,7.15],[x,y,-.70]);up=[q for q in hs if q['normal'][2]>.9]
  top=up[0]['position'][2]if up else None;above=[q for q in hs if q['position'][2]>levels[0]+TOL]
  row={'x_m':x,'y_m':y,'ray_hits':hs,'first_upward_hit_z_m':top,'unexpected_hits_above_F1_floor':above}
  well.append(row)
  if top is None or abs(top-levels[0])>TOL or above:well_bad.append(row)
ck('The100mm well is open at3 longitudinal by3 transverse stations down to F1 floor',not well_bad,
   claimed_size_is_model_fit_not_survey=True,well_plan_m=[[5.2,8.50],[7.8,8.60]],flight_width_m=1.08,
   nominal_inner_rail_axes_y_m=[8.448,8.652],rays=len(well),failures=well_bad)
wellbox=cube([5.2005,8.5005,levels[0]+.02],[7.7995,8.5995,7.15]);residual=house^wellbox
ck('No landing-bearing beam old slab or stair body remains inside the well',residual.volume()<1e-7,
   inspected_inset_m=.0005,well_volume_above_F1_floor_m3=residual.volume(),allowed_volume_m3=1e-7)

landings=[];land_bad=[]
for fl,z in enumerate(mid,1):
 for x in[4.15,4.60,5.10,5.185]:
  for y in[7.46,7.80,8.55,9.20,9.64]:
   hit=top_at(x,y,z);got=hit['position'][2]if hit else None
   supported=inside([x,y,z-.08]);row={'floor':fl,'x_m':x,'y_m':y,'expected_z_m':z,'actual_z_m':got,'supported_80mm_below':supported};landings.append(row)
   if got is None or abs(got-z)>TOL or not supported:land_bad.append(row)
ck('Both half landings remain full width and supported beyond both flight connections',not land_bad,
   half_landing_plan_m=[[4.02,7.42],[5.2,9.68]],stations=len(landings),failures=land_bad)

# Check interior points just outside each well edge: a real stair slab rather
# than a paper cap must support the baluster line after its XY relocation.
edge_support=[];edge_bad=[]
for s in steps:
 if s['arrival_platform']:continue
 edge=8.60 if s['flight']==1 else 8.50;sign=1 if s['flight']==1 else -1
 for offset in[.012,.052]:
  y=edge+sign*offset;x=s['x_m'];z=s['expected_z_m'];top=top_at(x,y,z)
  solid60=inside([x,y,z-.06]);wellair=not inside([x,edge-sign*.012,z-.01])
  row={'floor':s['floor'],'flight':s['flight'],'grade':s['grade'],'y_m':y,'edge_y_m':edge,'inset_m':offset,
       'top_found':bool(top),'solid_60mm_below':solid60,'adjacent_well_is_air':wellair};edge_support.append(row)
  if not top or abs(top['position'][2]-z)>TOL or not solid60 or not wellair:edge_bad.append(row)
ck('New well-side slab edges and nominal rail-foot axes have positive thickness beside actual open air',not edge_bad,
   stations=len(edge_support),offsets_from_well_edge_m=[.012,.052],solid_depth_test_m=.06,failures=edge_bad)

failures=[q for q in checks if not q['pass']]
out={'model':str(P),'model_sha256':H,'status':'PASS'if not failures else'FAIL','checks':checks,'failures':failures,
     'source_index':str(PD/'Geometry_Index.json'),'native_cache_index_sha256':hashlib.sha256((D/'Geometry_Index.json').read_bytes()).hexdigest(),
     'basis':'Independent saved-visible-mesh geometry QA. Tread X/Z are inherited source dimensions. The100mm well and1.08m flights are a revised photo/model fit following the user reference130324, not field measurements or structural certification. Nominal inner rail axes are Y8.448/8.652. Whole old stair volume is deliberately not a protected criterion.',
     'scope_limit':'This static QA does not certify that viewport flicker has disappeared. Final oblique dynamic or video inspection plus near-coplanar auditing is still required.',
     'tread_samples':tread_points,'riser_samples':riser_samples,'positive_support_samples':support,
     'wall_side_rays':wall_rays,'inner_edge_rays':inner_rays,'well_vertical_rays':well,
     'half_landings':landings,'well_edge_support':edge_support}
fn=R/'V26_8_Stair_Well_QA.json';fn.write_text(json.dumps(out,ensure_ascii=False,indent=2,default=lambda x:x.item()if isinstance(x,np.generic)else str(x)),'utf8')
print('STAIR_WELL_QA',len(checks),'FAIL',len(failures),H,flush=True)
sys.exit(0 if not failures else 2)
