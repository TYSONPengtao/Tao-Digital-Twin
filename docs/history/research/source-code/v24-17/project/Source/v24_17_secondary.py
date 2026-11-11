from v24_17_common import *
U=np.array([1.,.098]);U/=np.linalg.norm(U);N=np.array([-U[1],U[0]]);A=np.array([10.80,-16.84174904]);L=(13.10-A[0])/U[0]
def xy(s,t):return A+U*s+N*t
def p(s,t,z):return np.r_[xy(s,t),z]
def prism(profile,s0,s1):
 m=section(profile,s1-s0);return m.transform(np.c_[np.r_[N,0.],[0.,0.,1.],np.r_[U,0.],np.r_[xy(s0,0),0.]])
def zroof(t):return 2.82-.50*abs(t)
def prepare_secondary():
 mats='M_V19_Weathered_Wall_Tile';WHITE='M_V24_11_Plain_White_Limewash'
 # A closed two-slope cap and connected masonry carrier, on the level wall.
 shell=prism([(-.315,2.62),(.315,2.62),(.315,zroof(.315)),(0,2.82),(-.315,zroof(-.315))],.008,L-.04)
 put('V24_17_Secondary_Screenwall_Continuous_Tile_Bed',shell,mats,True)
 carrier=union([prism([(-w,z0),(w,z0),(w,z1),(-w,z1)],0,L-.02)for w,z0,z1 in [(.18,2.48,2.55),(.21,2.55,2.595),(.24,2.595,2.635)]])
 put('V24_17_Secondary_Screenwall_Continuous_Masonry_Carrier',carrier,'M_V24_11_Screenwall_Crisp_Soffit_Stone',True)
 tiles=[];drips=[];rows=np.arange(.065,L-.04,.135)
 for s in rows:
  for sg in [-1,1]:
   # Half round barrel section extruded down the transverse roof slope.
   t0,t1=sorted([sg*.018,sg*.322]);a=p(s,t0,zroof(t0)-.003);b=p(s,t1,zroof(t1)-.003);axis=b-a;length=float(np.linalg.norm(axis));axis/=length;normal=np.array([*N*(.5*sg),1.]);normal/=np.linalg.norm(normal);lat=np.r_[U,0.];ang=np.linspace(0,math.pi,11);prof=[(.043*math.cos(t),.043*math.sin(t))for t in ang]+[(.034*math.cos(t),.034*math.sin(t))for t in ang[::-1]];tile=section(prof,length).transform(np.c_[lat,normal,axis,a]);tiles.append(tile)
   # Solid plate between neighbouring cover rows, above the closed bed.
   aa=s+.047;bb=min(s+.088,L-.035)
   if bb>aa:tiles.append(prism([(t0,zroof(t0)-.002),(t1,zroof(t1)-.002),(t1,zroof(t1)+.012),(t0,zroof(t0)+.012)],aa,bb))
   center=p(s,sg*.312,zroof(sg*.322)+.014);drips.append(rod(center,center+np.r_[N*sg*.028,0.],.039,20))
 put('V24_17_Secondary_Screenwall_Barrel_and_Pan_Tiles',compose(tiles),mats,True)
 put('V24_17_Secondary_Screenwall_Eave_Disks',compose(drips),mats,True)
 put('V24_17_Secondary_Screenwall_Level_Ridge',rod(p(.008,0,2.838),p(L-.04,0,2.838),.035,20),mats,True)
 # Exterior and interior panels are closed solids, offset from the original
 # wall face. Framing is seated into each backing, with no coincident skin.
 panels=[];frames=[]
 for sg in [-1,1]:
  panels.append(prism([(sg*.158,2.18),(sg*.177,2.18),(sg*.177,2.50),(sg*.158,2.50)],.012,L-.03))
  for j in [0,1]:
   s0=.10+j*(L-.20)/2;s1=.10+(j+1)*(L-.20)/2-.035
   for z in [2.225,2.455]:frames.append(beam(p(s0,sg*.184,z),p(s1,sg*.184,z),.020,.022))
   for s in [s0,s1]:frames.append(beam(p(s,sg*.184,2.225),p(s,sg*.184,2.455),.020,.022))
 put('V24_10_Secondary_Screenwall_Closed_Panel_Band',compose(panels),WHITE)
 put('V24_10_Secondary_Screenwall_Panel_Mouldings',union(frames),'M_Stone_Frame')
 ts=np.linspace(-.32,.32,121)
 def head(t):
  d=abs(t);z=2.665+.23*(1-d/.32)
  if d<.095:z=max(z,2.895+math.sqrt(max(0,.095**2-d*d)))
  return z
 outer=[(-.32,2.605),(.32,2.605)]+[(float(t),head(t))for t in ts[::-1]]
 put('V24_14_Secondary_Screenwall_Volute_End',prism(outer,L-.17,L+.13),WHITE)
 rim=[(float(t),head(t)+.035)for t in ts]+[(float(t),head(t)-.024)for t in ts[::-1]]
 put('V24_14_Secondary_Screenwall_Volute_Rim',prism(rim,L-.195,L+.15),mats)
 steps=[]
 for w,z0,z1,s0,s1 in [(.35,2.55,2.61,L-.21,L+.165),(.30,2.495,2.55,L-.17,L+.125),(.25,2.44,2.495,L-.12,L+.075)]:steps.append(prism([(-w,z0),(w,z0),(w,z1),(-w,z1)],s0,s1))
 put('V24_14_Secondary_Screenwall_Stepped_End_Soffit',union(steps),'M_V24_11_Screenwall_Crisp_Soffit_Stone')
 frames=[]
 for sg in [-1,1]:frames.append(beam(p(L+.134,sg*.27,2.66),p(L+.134,sg*.09,2.835),.018,.018))
 circle=[p(L+.134,.065*math.cos(t),2.895+.065*math.sin(t))for t in np.linspace(0,math.tau,49)]
 for a,b in zip(circle,circle[1:]):frames.append(rod(a,b,.010,10))
 put('V24_14_Secondary_Screenwall_White_Inset_Frame',union(frames),mats)
 OUT['proof']['secondary']={'original_flat_wall_plan_and_crown_retained':True,'roof_ridge_z':2.838,'two_slope_bed':True,'barrel_rows':len(rows),'eave_disks':len(drips),'panel_faces':2,'scroll_end_centerline_xy':xy(L,0).tolist(),'scroll_end_top_z':max(head(float(t))for t in ts)+.035,'retire_old_native_coping_region':[10.79,13.18,-17.20,-16.18,2.47,2.85],'white_inner_finish_preserved':True}
