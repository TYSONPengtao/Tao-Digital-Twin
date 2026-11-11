import numpy as np,manifold3d as mf,math
from v24_16_common import solid,cube,union
def lathe(x,y,z,profile,sides=24):
 vv=[]
 for h,r in profile:
  for k in range(sides):
   t=2*math.pi*k/sides;vv.append([x+r*math.cos(t),y+r*math.sin(t),z+h])
 ff=[]
 for j in range(len(profile)-1):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides;c=(j+1)*sides+(k+1)%sides;d=(j+1)*sides+k;ff.extend([[a,b,c],[a,c,d]])
 vv.extend([[x,y,z+profile[0][0]],[x,y,z+profile[-1][0]]]);bot=len(vv)-2;top=bot+1
 for k in range(sides):ff.append([bot,(k+1)%sides,k]);ff.append([top,(len(profile)-1)*sides+k,(len(profile)-1)*sides+(k+1)%sides])
 return solid(vv,ff,'lathe')
def baluster(x,y,z,top):
 h=top-z;assert h>.5
 prof=[(.17,.024),(.195,.033),(.22,.034),(.245,.024),(.28,.022),(.34,.029),(.39,.031),(.44,.026),(.49,.019),(.57,.020),(.62,.028),(.65,.034),(.68,.034),(.71,.024),(.76,.023)]
 pp=[(q*h/.94,r) for q,r in prof];baseh=.18*h/.94;toph=.75*h/.94
 return union([cube([x-.0275,y-.0275,z],[x+.0275,y+.0275,z+baseh]),lathe(x,y,z,pp,20),cube([x-.0275,y-.0275,z+toph],[x+.0275,y+.0275,top-.008])])
def newel(x,y,z):
 prof=[(.105,.075),(.145,.075),(.18,.058),(.24,.048),(.30,.057),(.34,.068),(.38,.066),(.425,.052),(.68,.050),(.72,.065),(.75,.071),(.79,.059),(.86,.052),(.93,.052),(.96,.075),(1.01,.075),(1.035,.040)]
 return union([cube([x-.075,y-.075,z-.008],[x+.075,y+.075,z+.12]),lathe(x,y,z,prof),mf.Manifold.sphere(.074,24).translate([x,y,z+1.10])])
def handpath(points):
 # One swept tube with shared rings, avoiding lumpy cylinder/ball unions.
 points=np.asarray(points,float);vv=[];ff=[];sides=32
 for i,p in enumerate(points):
  tangent=points[min(i+1,len(points)-1)]-points[max(i-1,0)];tangent/=np.linalg.norm(tangent);ex=np.cross(tangent,[0.,0.,1.]);ex/=np.linalg.norm(ex);ey=np.cross(tangent,ex)
  for k in range(sides):
   t=2*math.pi*k/sides;vv.append(p+.039*(ex*math.cos(t)+ey*math.sin(t)))
 for j in range(len(points)-1):
  for k in range(sides):
   a=j*sides+k;b=j*sides+(k+1)%sides;c=(j+1)*sides+(k+1)%sides;d=(j+1)*sides+k;ff.extend([[a,b,c],[a,c,d]])
 vv.extend([points[0],points[-1]]);a=len(vv)-2;b=a+1
 for k in range(sides):ff.append([a,(k+1)%sides,k]);ff.append([b,(len(points)-1)*sides+k,(len(points)-1)*sides+(k+1)%sides])
 return solid(vv,ff,'swept handrail')
