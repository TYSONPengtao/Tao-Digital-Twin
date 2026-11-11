import sys
from pathlib import Path
W=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
from v26_1_common import *
import v26_1_common as C
D=W/'v26_9_railing';C.D=D
def arr(n):return np.load(W/'v26_1'/C.I[n]['file'])
from v24_32_rail_profiles import lathe
from scipy.interpolate import PchipInterpolator
import math
WOOD='M_V24_31_Polished_Dark_Red_Stair_Wood';pieces=[];meta={'flights':[],'balusters':[],'posts':[],'wreaths':[],'guards':[],'grip_paths':[],'top_join_detail':[],'returns':[]}
def sweep(points,w=.082,h=.058):
 points=np.array(points);vv=[];ff=[];N=32
 for i,p in enumerate(points):
  T=points[min(i+1,len(points)-1)]-points[max(i-1,0)];T/=np.linalg.norm(T);u=np.cross(T,[0,0,1.]);u/=np.linalg.norm(u);v=np.cross(T,u)
  for k in range(N):
   a=math.tau*k/N;vv.append(p+u*w/2*math.cos(a)+v*h/2*math.sin(a))
 for j in range(len(points)-1):
  for k in range(N):
   a=j*N+k;b=j*N+(k+1)%N;c=b+N;d=a+N;ff.extend([[a,b,c],[a,c,d]])
 vv.extend([points[0],points[-1]]);aa=len(vv)-2;bb=aa+1
 for k in range(N):ff.extend([[aa,(k+1)%N,k],[bb,(len(points)-1)*N+k,(len(points)-1)*N+(k+1)%N]])
 return solid(vv,ff,'oval continuous wood grip')
def curved_prof(x,y,z,profile,N=32):
 p=np.array(profile);hp=np.unique(np.r_[p[:,0],np.linspace(p[0,0],p[-1,0],100)]);rad=PchipInterpolator(p[:,0],p[:,1])(hp);return lathe(x,y,z,list(zip(hp,rad)),N)
def shaped_block(x,y,z0,z1,width=.052,slope=(0.,0.),bevel=.0015):
 r=width/2;b=min(bevel,r/3);xy=np.array([[-r+b,-r],[r-b,-r],[r,-r+b],[r,r-b],[r-b,r],[-r+b,r],[-r,r-b],[-r,-r+b]])
 vv=np.vstack([np.c_[xy+[x,y],np.full(8,z0)],np.c_[xy+[x,y],z1+xy@np.array(slope)]])
 ff=[]
 for k in range(1,7):ff.extend([[0,k+1,k],[8,8+k,8+k+1]])
 for k in range(8):j=(k+1)%8;ff.extend([[k,j,j+8],[k,j+8,k+8]])
 return solid(vv,ff,'subtle chamfered wood square with fitted top')

def path_sample(path,coordinate,axis=0):
 q=np.asarray(path)
 for a,b in zip(q[:-1],q[1:]):
  den=b[axis]-a[axis]
  if abs(den)<1e-9:continue
  u=(coordinate-a[axis])/den
  if -.00001<=u<=1.00001:
   p=a+np.clip(u,0,1)*(b-a);T=b-a;return p,T/np.linalg.norm(T)
 i=np.argmin(abs(q[:,axis]-coordinate));T=q[min(i+1,len(q)-1)]-q[max(i-1,0)];return q[i],T/np.linalg.norm(T)

def rounded_sweep_cap(point,tangent,w=.082,h=.058):
 T=np.array(tangent);T/=np.linalg.norm(T);u=np.cross(T,[0,0,1.]);u/=np.linalg.norm(u);v=np.cross(T,u)
 return mf.Manifold.sphere(1.,32).transform(np.c_[T*w/2,u*w/2,v*h/2,point])

def post(x,y,z,collar,tag):
 h=collar-z;prof=[(.11,.068),(.14,.068),(.20,.049),(.27,.046),(.34,.061),(.39,.063),(.46,.047),(.67*h,.046),(.76*h,.058),(.81*h,.064),(.87*h,.051),(h-.065,.055),(h-.035,.082),(h+.035,.082),(h+.060,.038),(h+.102,.038)]
 # Keep profile heights ordered after fitting different floor/guard collars.
 prof=sorted({round(float(a),7):b for a,b in prof}.items());body=union([shaped_block(x,y,z-.012,z+.12,.14,bevel=.002),curved_prof(x,y,z,prof,40),mf.Manifold.sphere(.066,40).translate([x,y,collar+.142])]);pieces.append(body);meta['posts'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'collar_z_m':collar,'ball_center_z_m':collar+.142,'ball_radius_m':.066,'base_m':.14,'volume_m3':body.volume()})
def spindle_raw(x,y,z,top,tag,tangent=None):
 h=top-z;scale=h/.94;prof=[(.17,.024),(.195,.031),(.22,.032),(.245,.024),(.28,.022),(.34,.028),(.39,.030),(.44,.026),(.49,.019),(.57,.020),(.62,.028),(.65,.032),(.68,.032),(.71,.024),(.76,.023)];prof=[(a*scale,b)for a,b in prof];T=np.array([1.,0.,0.])if tangent is None else np.array(tangent);slope=T[2]*T[:2]/max(float(T[:2]@T[:2]),1e-12);body=union([shaped_block(x,y,z-.008,z+.18*scale),curved_prof(x,y,z,prof,24),shaped_block(x,y,z+.75*scale,top-.015,slope=slope)]);pieces.append(body);meta['balusters'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'top_z_m':top,'minimum_diameter_m':.038,'cap_plane_gradient':slope.tolist(),'cap_plane_below_grip_center_m':.015});meta['top_join_detail'].append({'tag':tag,'xy':[x,y],'head_joins_actual_sloped_grip':True,'subtle_vertical_edge_chamfer_m':.0015})
SOURCE_BALUSTERS=json.loads((W/'v26_1/Prepared_Railing.json').read_text('utf8'))['proof']['balusters']
def spindle(x,y,z,top,tag,tangent=None):
 T=np.array([1.,0.,0.])if tangent is None else np.array(tangent);slope=T[2]*T[:2]/max(float(T[:2]@T[:2]),1e-12)
 eligible=[b for b in SOURCE_BALUSTERS if b['tag']==tag]
 if not eligible:
  spindle_raw(x,y,z,top,tag,T);meta['balusters'][-1]['added_local_end_gap_infill']=True;return
 spindle_raw(float(x),float(y),float(z),float(top),tag,T)

def hz(n,x,y):
 a=arr(n);t=a['v'][a['f']];A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];Q=np.array([x,y])-t[:,0,:2];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];u=np.divide(Q[:,0]*B[:,1]-Q[:,1]*B[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-12);w=np.divide(A[:,0]*Q[:,1]-A[:,1]*Q[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-12);ok=(det>1e-10)&(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001);assert ok.any(),(n,x,y);return float((t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]))[ok].max())
def hermite(p0,p1,d0,d1,t):
 return (2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*d0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*d1
level=[-.4499999881,3.450024414,7.050000191];lands=[1.499951124,5.249951363];curves={}
for fl,base,land,upper in [(1,level[0],lands[0],level[1]),(2,level[1],lands[1],level[2])]:
 rise=(land-base)/11;upperrise=(upper-land)/11
 # Both flights meet a shared semicircular wreath at the half landing.
 # Grips are oval; their roots intersect a real turned collar below the ball.
 r=.102;zarc=land+1.085;arc=[[5.13+r*math.cos(a),8.55+r*math.sin(a),zarc]for a in np.linspace(math.pi/2,3*math.pi/2,73)]
 post(5.13,8.55,land,zarc,f'F{fl} half landing');meta['wreaths'].append({'floor':fl,'radius_m':r,'arc_degrees':180,'center':[5.13,8.55,zarc],'continuous_to_both_flights':True})
 for k,ya in [(1,8.652),(2,8.448)]:
  rr=rise if k==1 else upperrise
  def line(x):return land+.965+((-1 if k==1 else 1)*(x-5.2)/.26+(0 if k==1 else 1))*rr
  xx=5.65;start=np.array([xx,ya,line(xx)]);end=np.array(arc[0 if k==1 else -1]);slope=(-rr/.26 if k==1 else rr/.26);p=[]
  # Form the curve from the landing outward, with zero twist at the wreath.
  for u in np.linspace(0,1,45):p.append(hermite(end,start,np.array([.52,0,0]),np.array([.52,0,slope*.52]),u))
  p.extend([[x,ya,line(x)]for x in np.linspace(xx+.025,7.71,81)])
  # The shared floor newel is on the slab, outside the open well.
  terminal=np.array([7.88,8.55,line(7.8)])
  if fl==1 and k==1:
   # The actual lower newel has a curved external return beneath its ball.
   # Keep its inherited collar and ball heights; gently dip the outside of
   # the U to preserve the small open throat visible in the reference.
   p=[q for q in p if q[0]<7.70];startreturn=np.array([7.70,ya,line(7.70)]);p.append(startreturn);collar=float(terminal[2]);U=np.array([[7.88+.112*math.cos(a),8.55+.112*math.sin(a),collar-.060*math.cos(a)**2]for a in np.linspace(math.pi/2,-math.pi/2,81)])
   p.extend([hermite(startreturn,U[0],np.array([.14,0,slope*.14]),np.array([.14,0,0]),u)for u in np.linspace(.025,1,40)]);p.extend(U[1:]);meta['returns'].append({'tag':'F1 lower newel U return','center_xy_m':[7.88,8.55],'radius_m':.112,'collar_z_m':collar,'front_dip_m':.060,'evidence':['2026-10-23 015859','2026-10-23 015914'],'note':'Qualitative photo reconstruction; dimensions inherited or fitted, not surveyed'})
  else:
   s0=np.array(p[-1]);p.extend([hermite(s0,terminal,np.array([.19,0,slope*.19]),np.array([.19,0,slope*.08]),u)for u in np.linspace(.05,1,20)])
  curves[fl,k]=np.array(p);meta['flights'].append({'floor':fl,'flight':k,'path':np.array(p).tolist(),'grip_width_m':.082,'grip_depth_m':.058,'nosing_clearance_center_m':.965,'ball_contact':False})
  for x in np.r_[5.245,np.arange(5.33,7.70,.13)]:
   q,T=path_sample(p,float(x));y=float(q[1]);top=float(q[2]);z=hz(f'STAIR_F{fl}_FLIGHT{k}_Geometry',float(x),9.05 if k==1 else 8.0);spindle(float(x),y,z,top,f'F{fl} flight {k}'+(' turn-end gap infill'if abs(x-5.245)<1e-6 else''),T)
 # One shared-ring sweep through both flights and the wreath eliminates the
 # artificial dark joint that separate capped sweeps left at the bend.
 path=np.vstack([curves[fl,1][::-1],np.array(arc)[1:],curves[fl,2][1:]]);pieces.append(sweep(path));meta['grip_paths'].append({'tag':f'F{fl} continuous two flights and half turn','path':path.tolist(),'width_m':.082,'depth_m':.058});
 if fl==1:pieces.append(rounded_sweep_cap(path[0],path[1]-path[0]))
# A single base at each floor receives the two grips on different collar
# faces; their ends are curved into the wood and never cut through the ball.
for fl,z in enumerate(level,1):
 coll=max(float(curves[ff,k][-1,2])for ff,k in curves if (ff==fl and k==1)or(ff+1==fl and k==2));post(7.88,8.55,z,coll,f'Floor {fl}')
# Final floor guard feet sit wholly inside the slab, not above the void.
z=level[2];h=z+1.175
pts=[[7.88,8.55,float(curves[2,2][-1,2])],[7.88,8.65,h],[7.88,9.49,h]]
# Smooth rising connection to the higher horizontal guard.
p0=np.array(pts[0]);p1=np.array([7.88,8.76,p0[2]]);p2=np.array([7.88,9.03,h]);pts0=[hermite(p0,p1,np.array([.06,.21,0.]),np.array([0,.21,0.]),u)for u in np.linspace(0,1,41)];pts0.extend([hermite(p1,p2,np.array([0,.27,0.]),np.array([0,.27,0.]),u)for u in np.linspace(.025,1,40)]);pts0 += [[7.88,y,h]for y in np.linspace(9.05,9.49,30)];pieces.append(sweep(pts0));post(7.88,9.49,z,h,'F3 rear guard end');meta['grip_paths'].append({'tag':'F3 rear guard with rise beyond independent ball finial','path':np.array(pts0).tolist(),'width_m':.082,'depth_m':.058,'preserved_horizontal_guard_center_height_above_floor_m':1.175,'rise_begins_y_m':8.76})
for y in np.r_[8.66,np.arange(8.73,9.40,.13)]:
 q,T=path_sample(pts0,float(y),1);spindle(float(q[0]),float(y),z,float(q[2]),'F3 rear guard'+(' end gap infill'if abs(y-8.66)<1e-6 else''),T)
meta['guards'].append({'tag':'F3 rear','axis_x_m':7.88,'slab_edge_x_m':7.8,'rail_top_above_floor_m':1.204,'base_supported':True})
y=7.215;front_h=h-.15;pts=[[4.035,y,front_h],[7.88,y,front_h]];pieces.append(sweep(np.array([pts[0],pts[1]])));meta['grip_paths'].append({'tag':'F3 front horizontal guard','path':pts,'width_m':.082,'depth_m':.058});post(7.88,y,z,front_h,'F3 front guard end')
for x in np.arange(4.23,7.78,.13):spindle(float(x),y,z,front_h,'F3 front guard')
meta['guards'].append({'tag':'F3 front','axis_y_m':y,'slab_edge_y_m':7.30,'rail_top_above_floor_m':1.054,'lowered_m':.15,'base_supported':True})
print('RAIL_UNION',len(pieces),flush=True);m=union(pieces).simplify(.00015);m=finish(m,WOOD,'photo referenced turned wood and continuous wreaths');row,m=export('V26_1_Photo_Referenced_Continuous_Wood_Railing',m,'Photo-referenced lower U return, independent ball finials, rear guard rise beyond ball, slope-fitted softly chamfered baluster caps; original XZ tread datums retained; inner rail axes and half-turn newel bases refitted around visible central well; wood material retained',smooth_wood=True)
assert len(m.decompose())==2,('Only the separate front guard and continuous flights/rear guard should remain',len(m.decompose()))
meta['V26_9_front_guard_only_lowered_m']=.15;meta['all_sloping_grip_paths_and_rear_guard_retained']=True;meta['closed_assemblies']=len(m.decompose());meta['baluster_count']=len(meta['balusters']);meta['minimum_spindle_clear_gap_m']=.13-.038;meta['scope']='Qualitative refinement based on supplied real handrail photographs; preserves original step elevations and wood material; half-turn radius and inner rail positions refitted around the visible central well. Fitted return and join dimensions are model choices, not surveyed dimensions';meta['original_spindle_X_and_Z_retained']=True;meta['inner_railing_Y_refitted_for_central_well']=True;meta['central_well_clear_width_m']=.10;meta['flight_inner_axes_y_m']=[8.448,8.652];meta['latest_reference']='D:/Desktop/屏幕截图 2026-10-24 130324.jpg';meta['enlarged_return_and_double_neck_ring_removed']=True;meta['local_end_gap_infill_count']=5;meta['spacing_basis']='Retain the original overall turned-baluster rhythm and locally fill the four visible turn-end gaps and one rear-guard end gap; nominal dimensions are visual/model choices, not site measurements or a regulatory compliance claim';meta['source_model']='E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend';meta['source_sha256']='ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e';meta['photo_evidence']=['E:/jz/JIA/Rebuild_V26_6/References/楼梯实景/屏幕截图 2026-10-23 015859.jpg','E:/jz/JIA/Rebuild_V26_6/References/楼梯实景/屏幕截图 2026-10-23 015914.jpg'];out={'objects':[row],'archive':[],'proof':meta};(D/'Prepared_Railing.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('RAIL_PREPARED',m.num_tri(),len(m.decompose()),len(meta['balusters']),flush=True)
