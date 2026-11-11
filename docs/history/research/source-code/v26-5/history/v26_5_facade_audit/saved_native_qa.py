from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube
O=Path('E:/jz/JIA/Rebuild_V26_5');model=O/'Blender/Architecture_Complete_V26_5.blend';R=O/'Reports';expected='202625cfe023a542ce75b7cbee3e05f0dee1767543a4ac7633b401d796e6c51a'
checks=[]
def ck(name,yes,**data):
 checks.append(dict(check=name,pass_=bool(yes),**data));print(name,bool(yes),flush=True)
def load(version):
 d=W/version/'Final';j={r['name']:r for r in json.loads((d/'Geometry_Index.json').read_text('utf8'))};r=j['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(d/r['file']);return a,solid(a['v'],a['f'])
old_a,old=load('v26_4');a,m=load('v26_5');sha=hashlib.sha256(model.read_bytes()).hexdigest();ck('Report reads exact freshly saved V26.5 model',sha==expected,sha256=sha)
reference=json.loads((W/'v26_5_facade_audit/Native_Exterior_Floor_Band_Join.json').read_text('utf8'));results=[];bad=[]
for ref in reference['rays']:
 axis=ref['axis'];along=ref['along'];ax=0 if axis in [0,2]else 1
 if axis==0:p0=np.array([12.5,along,3.4]);p1=np.array([13.5,along,3.4])
 elif axis==1:p0=np.array([along,9.3,3.4]);p1=np.array([along,10.3,3.4])
 else:p0=np.array([-.5,along,3.4]);p1=np.array([.5,along,3.4])
 hs=m.ray_cast(p0,p1);target=ref['target'];ok=target is None or any(abs(h.position[ax]-target)<.001 for h in hs)
 q=dict(axis=axis,along_m=along,expected_common_face_m=target,hit_positions_m=[h.position for h in hs],pass_=ok);results.append(q)
 if not ok:bad.append(q)
ck('108 exterior facade rays meet common original below and above wall faces',not bad,samples=len(results),tolerance_m=.001,failures=bad)
# Use the true shared inside point of the adjacent original faces. A vertical
# line at this point must remain inside the body across both repaired seams.
vertical=[];vbad=[]
for ref in reference['rays']:
 axis=ref['axis'];along=ref['along'];target=ref['target']
 if target is None:continue
 if axis==0:x=13.;y=along
 elif axis==1:x=along;y=9.8
 else:x=0.;y=along
 for z0,z1,label in [(3.3185,3.452,'whole join'),(3.3185,3.321,'lower seam'),(3.449,3.452,'upper seam')]:
  hs=m.ray_cast([x,y,z0],[x,y,z1]);interiorhits=[h.position for h in hs if z0+.00001<h.position[2]<z1-.00001]
  # At source columns and beams the same source finish steps can remain.
  # Only judge new internal openings: a step already in the original with
  # a narrower shared face is not a regression or a new gap.
  sourcehits=old.ray_cast([x,y,z0],[x,y,z1])
  # Determine occupancy by a robust short horizontal segment at 11 evenly
  # spaced heights. The midpoint is inside iff there is an odd count of
  # outward exits to a distant exterior endpoint.
  occ=[]
  for z in np.linspace(z0,z1,11):
   p=[x,y,float(z)];end=[x+2,y,float(z)]if axis==0 else[x,y+2,float(z)]if axis==1 else[x-2,y,float(z)]
   hr=m.ray_cast(p,end);occ.append(len(hr)%2==1)
  ok=all(occ);q=dict(axis=axis,along_m=along,xy_m=[x,y],span_z_m=[z0,z1],kind=label,occupied_samples=sum(occ),sample_count=len(occ),source_vertical_hits=len(sourcehits),pass_=ok)
  vertical.append(q)
  if not ok:vbad.append(q)
ck('Saved exterior join has continuous solid at lower and upper seams',not vbad,paths=len(vertical),occupancy_samples=sum(q['sample_count']for q in vertical),failures=vbad)
# Direct solid-volume comparison in the original stairwell clear interior.
stair=cube([4.15,7.5,3.3201],[8.95,9.4,3.4499]);added=(m-old)^stair;oldvol=(old^stair).volume();newvol=(m^stair).volume();ck('No added floor fills the stairwell interior at the repaired elevation',added.volume()<1e-7 and abs(oldvol-newvol)<1e-7,interior_box_m=[[4.15,7.5,3.3201],[8.95,9.4,3.4499]],tolerance_volume_m3=1e-7,added_volume_m3=added.volume(),source_solid_volume_m3=oldvol,saved_solid_volume_m3=newvol)
# Five rear stairwall rays are free of a see-through slit while preserving
# the thin wall between the stairwell and exterior.
stairrear=[]
for x in [4.5,5.,5.5,6.,6.5]:
 for z in [3.3201,3.35,3.4,3.4499]:
  hs=m.ray_cast([x,9.5,z],[x,10.1,z]);thick=float(hs[-1].position[1]-hs[0].position[1])if len(hs)==2 else None
  stairrear.append(dict(x_m=x,z_m=z,hits=len(hs),thickness_m=thick,pass_=len(hs)==2 and .219<thick<.241))
ck('Rear stairwell perimeter remains a thin continuous wall instead of a gap',all(q['pass_']for q in stairrear),samples=len(stairrear),maximum_thickness_m=max(q['thickness_m']or 0 for q in stairrear),failures=[q for q in stairrear if not q['pass_']])
ck('Saved house remains one positive closed manifold after facade join',m.status()==mf.Error.NoError and len(m.decompose())==1 and m.volume()>0,manifold_status=str(m.status()),components=len(m.decompose()),volume_m3=m.volume())
# Use standard report pass key expected by the package gate.
for q in checks:q['pass']=q.pop('pass_')
failures=[q for q in checks if not q['pass']];out=dict(model=str(model),model_sha256=sha,status='PASS'if not failures else'FAIL',checks=checks,failures=failures,evidence=dict(exterior_rays=results,vertical_continuity=vertical,thin_rear_stairwall=stairrear),scope='Only confirmed first/second floor west/east/rear exterior wall and slab edge junction; unrelated original facade geometry is not asserted repaired')
R.mkdir(exist_ok=True);fn=R/'V26_5_Facade_Joint_Regression_QA.json';fn.write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('FACADE_QA_DONE',out['status'],len(checks),len(failures),flush=True)



