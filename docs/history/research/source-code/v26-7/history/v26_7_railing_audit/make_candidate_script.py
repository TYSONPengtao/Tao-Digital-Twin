from pathlib import Path
W=Path(__file__).resolve().parent.parent
src=(W/'v26_1_rails.py').read_text('utf8')
src=src.replace('from v26_1_common import *',"import sys\nfrom pathlib import Path\nW=Path(__file__).resolve().parent.parent\nsys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]\nfrom v26_1_common import *\nimport v26_1_common as C\nD=W/'v26_7_railing_audit';C.D=D\ndef arr(n):return np.load(W/'v26_1'/C.I[n]['file'])")
src=src.replace("'guards':[]}","'guards':[],'grip_paths':[],'top_join_detail':[],'returns':[]}")
# Subtle edge chamfers keep the existing turned-wood proportions.
needle='def post(x,y,z,collar,tag):'
helpers='''def shaped_block(x,y,z0,z1,width=.052,slope=(0.,0.),bevel=.0015):
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

'''
src=src.replace(needle,helpers+needle)
src=src.replace("cube([x-.07,y-.07,z-.012],[x+.07,y+.07,z+.12])","shaped_block(x,y,z-.012,z+.12,.14,bevel=.002)")
src=src.replace('def spindle(x,y,z,top,tag):','def spindle(x,y,z,top,tag,tangent=None):')
src=src.replace("body=union([cube([x-.026,y-.026,z-.008],[x+.026,y+.026,z+.18*scale]),curved_prof(x,y,z,prof,24),cube([x-.026,y-.026,z+.75*scale],[x+.026,y+.026,top+.007])]);pieces.append(body);meta['balusters'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'top_z_m':top,'minimum_diameter_m':.038})", "T=np.array([1.,0.,0.])if tangent is None else np.array(tangent);slope=T[2]*T[:2]/max(float(T[:2]@T[:2]),1e-12);body=union([shaped_block(x,y,z-.008,z+.18*scale),curved_prof(x,y,z,prof,24),shaped_block(x,y,z+.75*scale,top-.015,slope=slope)]);pieces.append(body);meta['balusters'].append({'tag':tag,'xy':[x,y],'seat_z_m':z,'top_z_m':top,'minimum_diameter_m':.038,'cap_plane_gradient':slope.tolist(),'cap_plane_below_grip_center_m':.015});meta['top_join_detail'].append({'tag':tag,'xy':[x,y],'head_joins_actual_sloped_grip':True,'subtle_vertical_edge_chamfer_m':.0015})")
needle="terminal=np.array([7.84,8.55,line(7.8)]);s0=np.array(p[-1]);p.extend([hermite(s0,terminal,np.array([.19,0,slope*.19]),np.array([.19,0,slope*.08]),u)for u in np.linspace(.05,1,20)])"
replacement="""terminal=np.array([7.84,8.55,line(7.8)])
  if fl==1 and k==1:
   # The actual lower newel has a curved external return beneath its ball.
   # Keep its inherited collar and ball heights; gently dip the outside of
   # the U to preserve the small open throat visible in the reference.
   p=[q for q in p if q[0]<7.44];startreturn=np.array([7.44,ya,line(7.44)]);p.append(startreturn);collar=float(terminal[2]);U=np.array([[7.84+.112*math.cos(a),8.55+.112*math.sin(a),collar-.060*math.cos(a)**2]for a in np.linspace(math.pi/2,-math.pi/2,81)])
   p.extend([hermite(startreturn,U[0],np.array([.40,0,slope*.40]),np.array([.40,0,0]),u)for u in np.linspace(.025,1,40)]);p.extend(U[1:]);meta['returns'].append({'tag':'F1 lower newel U return','center_xy_m':[7.84,8.55],'radius_m':.112,'collar_z_m':collar,'front_dip_m':.060,'evidence':['2026-10-23 015859','2026-10-23 015914'],'note':'Qualitative photo reconstruction; dimensions inherited or fitted, not surveyed'})
  else:
   s0=np.array(p[-1]);p.extend([hermite(s0,terminal,np.array([.19,0,slope*.19]),np.array([.19,0,slope*.08]),u)for u in np.linspace(.05,1,20)])"""
assert needle in src;src=src.replace(needle,replacement)
src=src.replace("q=np.array(p);y=float(np.interp(x,q[:,0],q[:,1]));top=float(np.interp(x,q[:,0],q[:,2]));z=hz", "q,T=path_sample(p,float(x));y=float(q[1]);top=float(q[2]);z=hz")
src=src.replace("spindle(float(x),y,z,top,f'F{fl} flight {k}')", "spindle(float(x),y,z,top,f'F{fl} flight {k}',T)")
src=src.replace("path=np.vstack([curves[fl,1][::-1],np.array(arc)[1:],curves[fl,2][1:]]);pieces.append(sweep(path))", "path=np.vstack([curves[fl,1][::-1],np.array(arc)[1:],curves[fl,2][1:]]);pieces.append(sweep(path));meta['grip_paths'].append({'tag':f'F{fl} continuous two flights and half turn','path':path.tolist(),'width_m':.082,'depth_m':.058});\n if fl==1:pieces.append(rounded_sweep_cap(path[0],path[1]-path[0]))")
src=src.replace("coll=max(float(curves[ff,k][-1,2])for ff,k in curves if (ff==fl and k==1)or(ff+1==fl and k==2));", "coll=max(float(curves[ff,k][-1,2])for ff,k in curves if (ff==fl and k==1)or(ff+1==fl and k==2));")
needle="p0=np.array(pts[0]);p1=np.array(pts[1]);pts0=[hermite(p0,p1,np.array([.08,.12,.10]),np.array([0,.15,0]),u)for u in np.linspace(0,1,33)];pts0 += [[7.88,y,h]for y in np.linspace(8.67,9.49,30)];pieces.append(sweep(pts0));post(7.88,9.49,z,h,'F3 rear guard end')\nfor y in np.arange(8.73,9.40,.13):spindle(7.88,float(y),z,h,'F3 rear guard')"
replacement="""p0=np.array(pts[0]);p1=np.array([7.88,8.76,p0[2]]);p2=np.array([7.88,9.03,h]);pts0=[hermite(p0,p1,np.array([.06,.21,0.]),np.array([0,.21,0.]),u)for u in np.linspace(0,1,41)];pts0.extend([hermite(p1,p2,np.array([0,.27,0.]),np.array([0,.27,0.]),u)for u in np.linspace(.025,1,40)]);pts0 += [[7.88,y,h]for y in np.linspace(9.05,9.49,30)];pieces.append(sweep(pts0));post(7.88,9.49,z,h,'F3 rear guard end');meta['grip_paths'].append({'tag':'F3 rear guard with rise beyond independent ball finial','path':np.array(pts0).tolist(),'width_m':.082,'depth_m':.058,'preserved_horizontal_guard_center_height_above_floor_m':1.175,'rise_begins_y_m':8.76})
for y in np.arange(8.73,9.40,.13):
 q,T=path_sample(pts0,float(y),1);spindle(float(q[0]),float(y),z,float(q[2]),'F3 rear guard',T)"""
assert needle in src;src=src.replace(needle,replacement)
src=src.replace("y=7.215;pts=[[4.035,y,h],[7.88,y,h]];pieces.append(sweep(np.array([pts[0],pts[1]])));post", "y=7.215;pts=[[4.035,y,h],[7.88,y,h]];pieces.append(sweep(np.array([pts[0],pts[1]])));meta['grip_paths'].append({'tag':'F3 front horizontal guard','path':pts,'width_m':.082,'depth_m':.058});post")
src=src.replace('m=union(pieces).simplify(.00025)', 'm=union(pieces).simplify(.00015)')
src=src.replace("'Turned wood profiles, oval continuous grips, 180 degree half-landing wreaths, supported guard posts, two balusters per tread'", "'Photo-referenced lower U return, independent ball finials, rear guard rise beyond ball, slope-fitted softly chamfered baluster caps; inherited treads, posts, wood material and guard ends retained'")
src=src.replace("meta['scope']='Visual reconstruction from user photos; no load or fixing design certification'", "meta['scope']='Qualitative refinement based on supplied real handrail photographs; preserves inherited step elevations, guard endpoints and wood material. Fitted return and join dimensions are model choices, not surveyed dimensions';meta['source_model']='E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend';meta['source_sha256']='ea7cd20cb3c30cf2b5984c1e262ca182fa3c168a8a16fd7201ef428267bf05b7';meta['photo_evidence']=['E:/jz/JIA/Rebuild_V26_6/References/楼梯实景/屏幕截图 2026-10-23 015859.jpg','E:/jz/JIA/Rebuild_V26_6/References/楼梯实景/屏幕截图 2026-10-23 015914.jpg']")
(W/'v26_7_railing_audit/build_candidate.py').write_text(src,'utf8')
print('CANDIDATE_SCRIPT_WRITTEN')
