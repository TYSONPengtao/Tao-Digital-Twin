from pathlib import Path
W=Path(__file__).parent
text=(W/'v24_34_interior_physics_qa.py').read_text('utf8').replace('Rebuild_V24_34','Rebuild_V26').replace('Architecture_Complete_V24_34','Architecture_Complete_V26').replace('V24_34_Interior_Physics_QA','V26_Interior_Physics_QA')
anchor="with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()"
extra='''
# Cross the recovered photographed ramp at four separate positions, in both
# directions, using the same capsule and gravity as the delivered runtime.
import math
P0=Vector((-14.8813,-8.4793,0));P1=Vector((-12.5895,-12.7096,0));u=(P1-P0).normalized();inward=Vector((-u.y,u.x,0))
for s in [0.9,1.9,2.9,3.9]:
 a=P0+u*s-inward*1.6;b=P0+u*s+inward*1.8
 w=Walker(world,(a.x,a.y,-.8));recoveries=w.recoveries;ok,tr=go(w,(b.x,b.y),limit=8.);traces['source_ramp_in_'+str(s)]=tr
 ck('Original photographed ramp enters continuously at station '+str(s),ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
 ok,tr=go(w,(a.x,a.y),limit=8.);traces['source_ramp_out_'+str(s)]=tr
 ck('Original photographed ramp exits continuously at station '+str(s),ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
a=P0+u*2.5-inward*.6;w=Walker(world,(a.x,a.y,-1.));z0=w.p.z;peak=z0
for i in range(150):w.update((0,0),1/60,jump=i==0);peak=max(peak,w.p.z)
ck('Jump lands on the recovered photographic ramp',w.grounded and w.recoveries==0 and abs(w.p.z-z0)<.01 and peak-z0>.5,position=list(w.p),jump_height_m=peak-z0)
headroom=[]
for key,trace in traces.items():
 if not key.startswith(('ascend_floor_','descend_floor_')):continue
 for p in trace:
  hit,no,index,dist=world.bvh.ray_cast(Vector((p[0],p[1],p[2]+.025)),Vector((0,0,1)),10.)
  if hit is not None:headroom.append(float(hit.z-p[2]))
ck('Actual stair route overhead clearance is at least 2.20m',headroom and min(headroom)>=2.20,minimum_vertical_clearance_m=min(headroom) if headroom else None,sampled_positions=len(headroom))
'''
assert anchor in text;text=text.replace(anchor,extra+'\n'+anchor);(W/'v26_physics_qa.py').write_text(text,encoding='utf8')
print('PHYSICS_QA_PREPARED')
