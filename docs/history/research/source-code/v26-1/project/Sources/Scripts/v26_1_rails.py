from v26_1_common import *
from v24_32_rail_profiles import lathe
from scipy.interpolate import PchipInterpolator
import math
WOOD='M_V24_31_Polished_Dark_Red_Stair_Wood';pieces=[];meta={'flights':[],'balusters':[],'posts':[],'wreaths':[],'guards':[]}
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
def post(x,y,z,collar,tag):
 h=collar-z;prof=[(.11,.068),(.14,.068),(.20,.049),(.27,.046),(.34,.061),(.39,.063),(.46,.047),(.67*h,.046),(.76*h,.058),(.81*h,.064),(.87*h,.051),(h-.065,.055),(h-.035,.082),(h+.035,.082),(h+.060,.038),(h+.102,.038)]
 # Keep profile heights ordered after fitting different floor/guard collars.
 prof=sorted({round(float(a),7):b for a,b in prof}.items());body=union([cube([x-.07,y-.07,z-.012],[x+.07,y+.07,z+.12]),curved_prof(x,y,z,prof,40),mf.Manifold.sphere(.066,40).translate([x,y,collar+.142])]);pieces.append(body);meta['posts'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'collar_z_m':collar,'ball_center_z_m':collar+.142,'ball_radius_m':.066,'base_m':.14,'volume_m3':body.volume()})
def spindle(x,y,z,top,tag):
 h=top-z;scale=h/.94;prof=[(.17,.024),(.195,.031),(.22,.032),(.245,.024),(.28,.022),(.34,.028),(.39,.030),(.44,.026),(.49,.019),(.57,.020),(.62,.028),(.65,.032),(.68,.032),(.71,.024),(.76,.023)];prof=[(a*scale,b)for a,b in prof];body=union([cube([x-.026,y-.026,z-.008],[x+.026,y+.026,z+.18*scale]),curved_prof(x,y,z,prof,24),cube([x-.026,y-.026,z+.75*scale],[x+.026,y+.026,top+.007])]);pieces.append(body);meta['balusters'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'top_z_m':top,'minimum_diameter_m':.038})
def hz(n,x,y):
 a=arr(n);t=a['v'][a['f']];A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];Q=np.array([x,y])-t[:,0,:2];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];u=np.divide(Q[:,0]*B[:,1]-Q[:,1]*B[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-12);w=np.divide(A[:,0]*Q[:,1]-A[:,1]*Q[:,0],det,out=np.zeros_like(det),where=abs(det)>1e-12);ok=(det>1e-10)&(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001);assert ok.any(),(n,x,y);return float((t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]))[ok].max())
def hermite(p0,p1,d0,d1,t):
 return (2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*d0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*d1
level=[-.4499999881,3.450024414,7.050000191];lands=[1.499951124,5.249951363];curves={}
for fl,base,land,upper in [(1,level[0],lands[0],level[1]),(2,level[1],lands[1],level[2])]:
 rise=(land-base)/11;upperrise=(upper-land)/11
 # Both flights meet a shared semicircular wreath at the half landing.
 # Grips are oval; their roots intersect a real turned collar below the ball.
 r=.112;zarc=land+1.085;arc=[[5.13+r*math.cos(a),8.55+r*math.sin(a),zarc]for a in np.linspace(math.pi/2,3*math.pi/2,73)]
 post(5.13,8.55,land,zarc,f'F{fl} half landing');meta['wreaths'].append({'floor':fl,'radius_m':r,'arc_degrees':180,'center':[5.13,8.55,zarc],'continuous_to_both_flights':True})
 for k,ya in [(1,8.602),(2,8.498)]:
  rr=rise if k==1 else upperrise
  def line(x):return land+.965+((-1 if k==1 else 1)*(x-5.2)/.26+(0 if k==1 else 1))*rr
  xx=5.65;start=np.array([xx,ya,line(xx)]);end=np.array(arc[0 if k==1 else -1]);slope=(-rr/.26 if k==1 else rr/.26);p=[]
  # Form the curve from the landing outward, with zero twist at the wreath.
  for u in np.linspace(0,1,45):p.append(hermite(end,start,np.array([.52,0,0]),np.array([.52,0,slope*.52]),u))
  p.extend([[x,ya,line(x)]for x in np.linspace(xx+.025,7.65,81)])
  # The shared floor newel is on the slab, outside the open well.
  terminal=np.array([7.84,8.55,line(7.8)]);s0=np.array(p[-1]);p.extend([hermite(s0,terminal,np.array([.19,0,slope*.19]),np.array([.19,0,slope*.08]),u)for u in np.linspace(.05,1,20)])
  curves[fl,k]=np.array(p);meta['flights'].append({'floor':fl,'flight':k,'path':np.array(p).tolist(),'grip_width_m':.082,'grip_depth_m':.058,'nosing_clearance_center_m':.965,'ball_contact':False})
  for x in np.arange(5.33,7.70,.13):
   q=np.array(p);y=float(np.interp(x,q[:,0],q[:,1]));top=float(np.interp(x,q[:,0],q[:,2]));z=hz(f'STAIR_F{fl}_FLIGHT{k}_Geometry',float(x),9.05 if k==1 else 8.0);spindle(float(x),y,z,top,f'F{fl} flight {k}')
 # One shared-ring sweep through both flights and the wreath eliminates the
 # artificial dark joint that separate capped sweeps left at the bend.
 path=np.vstack([curves[fl,1][::-1],np.array(arc)[1:],curves[fl,2][1:]]);pieces.append(sweep(path))
# A single base at each floor receives the two grips on different collar
# faces; their ends are curved into the wood and never cut through the ball.
for fl,z in enumerate(level,1):
 coll=max(float(curves[ff,k][-1,2])for ff,k in curves if (ff==fl and k==1)or(ff+1==fl and k==2));post(7.84,8.55,z,coll,f'Floor {fl}')
 if fl==2:
  # Short upper neck molding seals the lower rail socket without a loose cap.
  lo=float(curves[1,2][-1,2]);pieces.append(curved_prof(7.84,8.55,lo,[(-.035,.064),(-.022,.073),(.022,.073),(.035,.060)],40))
# Final floor guard feet sit wholly inside the slab, not above the void.
z=level[2];h=z+1.175
pts=[[7.84,8.55,float(curves[2,2][-1,2])],[7.88,8.65,h],[7.88,9.49,h]]
# Smooth rising connection to the higher horizontal guard.
p0=np.array(pts[0]);p1=np.array(pts[1]);pts0=[hermite(p0,p1,np.array([.08,.12,.10]),np.array([0,.15,0]),u)for u in np.linspace(0,1,33)];pts0 += [[7.88,y,h]for y in np.linspace(8.67,9.49,30)];pieces.append(sweep(pts0));post(7.88,9.49,z,h,'F3 rear guard end')
for y in np.arange(8.73,9.40,.13):spindle(7.88,float(y),z,h,'F3 rear guard')
meta['guards'].append({'tag':'F3 rear','axis_x_m':7.88,'slab_edge_x_m':7.8,'rail_top_above_floor_m':1.204,'base_supported':True})
y=7.215;pts=[[4.035,y,h],[7.88,y,h]];pieces.append(sweep(np.array([pts[0],pts[1]])));post(7.88,y,z,h,'F3 front guard end')
for x in np.arange(4.23,7.78,.13):spindle(float(x),y,z,h,'F3 front guard')
meta['guards'].append({'tag':'F3 front','axis_y_m':y,'slab_edge_y_m':7.30,'rail_top_above_floor_m':1.204,'base_supported':True})
print('RAIL_UNION',len(pieces),flush=True);m=union(pieces).simplify(.00025);m=finish(m,WOOD,'photo referenced turned wood and continuous wreaths');row,m=export('V26_1_Photo_Referenced_Continuous_Wood_Railing',m,'Turned wood profiles, oval continuous grips, 180 degree half-landing wreaths, supported guard posts, two balusters per tread',smooth_wood=True)
assert len(m.decompose())==2,('Only the separate front guard and continuous flights/rear guard should remain',len(m.decompose()))
meta['closed_assemblies']=len(m.decompose());meta['baluster_count']=len(meta['balusters']);meta['minimum_spindle_clear_gap_m']=.13-.038;meta['scope']='Visual reconstruction from user photos; no load or fixing design certification';out={'objects':[row],'archive':['V24_32_Continuous_Stair_Wood_Railing'],'proof':meta};(D/'Prepared_Railing.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('RAIL_PREPARED',m.num_tri(),len(m.decompose()),len(meta['balusters']),flush=True)
