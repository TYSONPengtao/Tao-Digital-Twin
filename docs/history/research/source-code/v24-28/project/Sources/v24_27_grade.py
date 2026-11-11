"""Local continuous grading, referenced to the retained F1 floor and riser."""
import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np
D=W/'v24_27';idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
OUT={'raw_objects':[],'objects':[],'remove':[],'proof':{}}

def refine(d):
 # Add only affine subdivisions in the local grading rectangles. This inserts
 # enough controls into the old coarse outer soil triangles to represent the
 # long plane; every child retains the original face and UV interpolation.
 V=d['v'].tolist();F=d['f'].tolist();MI=d['mi'].tolist();UV=d['uv'].tolist();P=list(range(len(F)))
 for step in range(16):
  vv=np.array(V);ff=np.array(F);tt=vv[ff];lo=tt[:,:,:2].min(1);hi=tt[:,:,:2].max(1)
  west=(hi[:,0]>-6.3)&(lo[:,0]<.15)&(hi[:,1]>-3.8)&(lo[:,1]<12.0)
  front=(hi[:,0]>-.20)&(lo[:,0]<14.2)&(hi[:,1]>-3.8)&(lo[:,1]<2.)
  take=(west|front)&(tt[:,:,2].max(1)>-1.1);mids={}
  for ids in ff[take]:
   for a,b in zip(ids,np.roll(ids,-1)):
    k=tuple(sorted((int(a),int(b))))
    if k not in mids and np.linalg.norm(vv[a,:2]-vv[b,:2])>.23:
     mids[k]=len(V);V.append(((vv[a]+vv[b])/2).tolist())
  if not mids:break
  nf=[];nm=[];nu=[];npf=[]
  for ids,mat,tuv,parent in zip(F,MI,UV,P):
   a,b,c=ids;ab=mids.get(tuple(sorted((a,b))));bc=mids.get(tuple(sorted((b,c))));ca=mids.get(tuple(sorted((c,a))));k=sum(q is not None for q in [ab,bc,ca])
   if k==0:parts=[ids]
   elif k==3:parts=[[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]]
   elif k==1:parts=[[a,ab,c],[ab,b,c]]if ab is not None else [[b,bc,a],[bc,c,a]]if bc is not None else [[c,ca,b],[ca,a,b]]
   elif ca is None:parts=[[a,ab,c],[ab,bc,c],[ab,b,bc]]
   elif ab is None:parts=[[b,bc,a],[bc,ca,a],[bc,c,ca]]
   else:parts=[[c,ca,b],[ca,ab,b],[ca,a,ab]]
   u={i:np.array(q)for i,q in zip(ids,tuv)}
   for mid,i,j in [(ab,a,b),(bc,b,c),(ca,c,a)]:
    if mid is not None:u[mid]=(u[i]+u[j])/2
   for ids2 in parts:nf.append(ids2);nm.append(mat);nu.append([u[i].tolist()for i in ids2]);npf.append(parent)
  F,MI,UV,P=nf,nm,nu,npf
 else:raise RuntimeError('Local grading subdivisions did not converge')
 return np.array(V),np.array(F),np.array(MI),np.array(UV),np.array(P)

def clamp(x):return min(1.,max(0.,x))
def front_level(y):return -.15 if y>=-.60 else -.45+.30*clamp((y+3.60)/3.0)
def west_contact(y):
 if y<=1.90:return front_level(y)
 if y<=9.85:return -.15
 return -.15-.33*clamp((y-9.85)/1.85)

def top_sampler(d):
 t=d['v'][d['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);keep=n[:,2]>1e-11;t=t[keep];A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];de=A[:,0]*B[:,1]-A[:,1]*B[:,0];xyz=d['v'][d['v'][:,2]>-1.2]
 def sample(x,y):
  q=np.array([x,y])-t[:,0,:2];a=(q[:,0]*B[:,1]-q[:,1]*B[:,0])/de;b=(A[:,0]*q[:,1]-A[:,1]*q[:,0])/de;good=(a>=-2e-5)&(b>=-2e-5)&(a+b<=1+2e-5)
  if good.any():return float((t[:,0,2]+a*(t[:,1,2]-t[:,0,2])+b*(t[:,2,2]-t[:,0,2]))[good].max())
  ds=((xyz[:,:2]-[x,y])**2).sum(1);ids=np.argsort(ds)[:6];return float(xyz[ids,2].max())
 return sample

def target(x,y,oldtop,soil=False,finish=False):
 # The six-metre outer run replaces the old 1.65m smooth hump with a long
 # planar fall. Only the west side visible in the marked screenshot is reset.
 if x<.25 and -3.6<y<11.9:
  dist=max(0.,-x-.125);span=5.875
  if dist>=span:return oldtop
  base=-.48+.004*x;near=west_contact(y);far=-.504
  wanted=near+(far-near)*(dist/span)
  wy=clamp((y+3.6)/.60)*clamp((11.9-y)/.20)
  return oldtop+(wanted-oldtop)*wy
 if -.125-1e-6<=x<14.08 and -3.6<y<=1.90002:
  wanted=front_level(y)+( .002 if finish else 0.)
  w=clamp((y+3.6)/.60)*clamp((14.08-x)/.98)
  # Keep the already fitted gutter/porch edge at its accepted lower level;
  # introduce a shallow lateral fall to that edge rather than burying it.
  near_kitchen=clamp((x-6.55)/.70)*(1-clamp((y+2.60)/.75))
  w*=1-near_kitchen
  return oldtop+(wanted-oldtop)*w
 return oldtop

names=['SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_V12_REBUILT_COURT_-20_-20_0_Geometry','SITE_V12_REBUILT_COURT_-20_0_0_Geometry','SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_V12_REBUILT_COURT_0_0_0_Geometry','V24_24_House_Front_Matching_Stone_Paving']
records=[]
for n in names:
 d=np.load(D/idx[n]['file']);sv,f,mi,uv,parent=refine(d);v=sv.copy();sample=top_sampler(d);cache={};soil='SOIL'in n;finish=n.startswith('V24_24_');lower=float(v[:,2].min());moved=0
 tri=sv[f];up=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])[:,2]>1e-11;topids=np.unique(f[up]);upper={}
 for i in topids:
  x,y,z=sv[i];key=(round(float(x),8),round(float(y),8));upper[key]=max(upper.get(key,-1e10),float(z))
 for i,(x,y,z)in enumerate(sv):
  if not(-6.0001<x<14.0801 and -3.6001<y<11.9001):continue
  key=(round(float(x),8),round(float(y),8))
  if key not in cache:
   top=upper[key]if key in upper else sample(float(x),float(y));new=target(float(x),float(y),top,soil,finish);cache[key]=(top,new-top)
  top,dz=cache[key]
  if abs(dz)<1e-10:continue
  if finish:factor=1.
  else:factor=clamp((float(z)-lower)/max(1e-6,top-lower))
  v[i,2]+=dz*factor;moved+=1
 # Recess only the supporting court substrate inside the existing finish
 # footprint. The 12mm stone skin still overlaps it, while the old substrate
 # cannot poke through the 2mm surface offset along a changing crossfall.
 if not soil and not finish:
  for i in topids:
   x,y,z=sv[i]
   if .125<x<13.10 and -3.6<y<1.9:
    w=clamp((x-.125)/.03)*clamp((13.10-x)/.03)*clamp((y+3.6)/.03)*clamp((1.9-y)/.03)
    v[i,2]-=.008*w
 if moved:
  fn='GRADE_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv,source_v=sv,parent=parent)
  OUT['raw_objects'].append({'name':n,'file':fn,'materials':idx[n]['materials'],'smooth_top':soil})
  records.append({'object':n,'changed_vertices':moved,'max_raise_m':float((v-sv)[:,2].max()),'max_lower_m':float((sv-v)[:,2].max()),'xy_footprint_unchanged':bool(np.array_equal(v[:,:2],sv[:,:2])),'source_vertices_retained':len(d['v']),'affine_subdivision_vertices_added':len(v)-len(d['v']),'uv_interpolation_and_material_slots_retained':True,'buried_base_unchanged':True})
  print('GRADE',records[-1],flush=True)
OUT['proof']={'references':['123610','123632'],'source':'Native F1 floor0.00m and existing single 150mm riser; photo-supported hierarchy, no new field survey','cause':'Prior local contact grade -0.06m and 1.65m smooth blend concealed the F1 slab edge and formed a raised mound beside the house. Independent entry raise and later paving followed the same distorted substrate.','floor_z_m':0.,'near_house_court_and_wall_contact_z_m':-.15,'existing_kitchen_floor_z_m':-.4,'courtyard_outer_datum_z_m':-.45,'front_court_profile_yz':[[-3.6,-.45],[-.6,-.15],[1.9,-.15]],'west_outer_run_xz':[[-.125,-.15],[-6.,-.504]],'west_outer_run_width_m':5.875,'existing_single_entry_riser_retained_m':.15,'kitchen_gutter_edge_retained':True,'west_scope_xy':[-6.,-3.6,.25,11.9],'front_scope_xy':[-.125,-3.6,14.08,1.9],'court_substrate_recess_below_visible_finish_m':.008,'wall_contact_continued_beneath_slab_edge':True,'raw_changes':records,'protected':['All building slabs and columns','Existing house entry riser and porch solid','Kitchen and storage gallery levels','Door/window actions and high bathroom windows','Kitchen roof and courtyard tile coping','Exterior surveyed scan and road/drain outside the local grade scope','L/P measurement runtime']}
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2),encoding='utf8');print('V27_GRADE_READY',len(records),flush=True)
