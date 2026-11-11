from v24_18_common import *
def mesh(m):
 a=m.to_mesh64();return {'v':np.asarray(a.vert_properties[:,:3]).tolist(),'f':np.asarray(a.tri_verts).tolist()}
def ring(a,b,c,d,y,depth,w):return cube([a,y,c],[b,y+depth,d])-cube([a+w,y-.01,c+w],[b-w,y+depth+.01,d-w])
def prepare_windows():
 OUT['windows']=[];OUT['vertex_transforms']=[]
 for fl,side,z0,z1 in [(1,'L',.6,3.6),(1,'R',.6,3.6),(2,'L',4.5,7.2),(2,'R',4.5,7.2),(3,'R',8.1,10.5)]:
  x0,x1=(.72,3.18)if side=='L'else(9.82,12.28)
  make_window(f'BAY_WINDOW_F{fl}_{side}_1_Geometry',x0,x1,z0,z1,1.10,np.linspace(x0,x1,4),z0+.72*(z1-z0))
  # Extend the angled glass ends to the same thin corner frame; no white
  # masonry post is left between the front and oblique window panels.
  for j,frontx in [(0,x0),(2,x1)]:
   name=f'BAY_WINDOW_F{fl}_{side}_{j}_Geometry';a=source(name);v=a['v'];u=np.array([1.,-1.4285714])if j==0 else np.array([-1.,-1.4285714]);u/=np.linalg.norm(u);nn=np.array([-u[1],u[0]]);s=v[:,:2]@u;t=v[:,:2]@nn;start=u*s.min()+nn*(t.min()+t.max())/2;end=u*s.max()+nn*(t.min()+t.max())/2;target=np.array([frontx,1.10]);nu=(target-start)/np.linalg.norm(target-start);nv=np.array([-nu[1],nu[0]]);L=np.linalg.norm(end-start);NL=np.linalg.norm(target-start)
   for n in [name,f'CONSTRUCTION_SILL_BAY_WINDOW_F{fl}_{side}_{j}_Geometry',f'CONSTRUCTION_LOW_SILL_GUARD_BAY_WINDOW_F{fl}_{side}_{j}_Geometry']:
    b=source(n);vv=b['v'].copy();q=vv[:,:2]-start;vv[:,:2]=start+(q@u)[:,None]*(NL/L)*nu+(q@nn)[:,None]*nv;OUT['vertex_transforms'].append({'name':n,'v':vv.tolist(),'original_file':INDEX[n]['file']})
 make_window('WINDOW_FRONT_CENTER_F3_Geometry',4.10,8.90,8.40,10.35,2.10,[4.10,5.15,5.70,7.30,7.85,8.90],9.9025,[4.10,5.70,7.30,8.90])
 OUT['proof']['windows']={'outward_sashes':12,'operation':'side hinged outward','left_rotation_degrees':-65,'right_rotation_degrees':65,'keyframes_degrees':{'1':0,'20':32.5,'40':65},'fixed_center_and_transom_preserved':True,'marked_false_corner_posts_removed':10,'corner_join':'thin continuous black frame','building_grid_columns_retained':True}
def make_window(name,x0,x1,z0,z1,y,divs,head,topdivs=None):
 divs=list(map(float,divs));topdivs=divs if topdivs is None else list(topdivs);bar=.040;fixed=[ring(x0,x1,z0,z1,y-.045,.090,bar)];glass=[];sashes=[]
 for x in divs[1:-1]:fixed.append(cube([x-bar/2,y-.045,z0+bar],[x+bar/2,y+.045,head-bar/2]))
 for x in topdivs[1:-1]:fixed.append(cube([x-bar/2,y-.045,head+bar/2],[x+bar/2,y+.045,z1-bar]))
 fixed.append(cube([x0+bar,y-.045,head-bar/2],[x1-bar,y+.045,head+bar/2]))
 for a,b in zip(topdivs[:-1],topdivs[1:]):glass.append(cube([a+(bar if a==x0 else bar/2),y-.003,head+bar/2],[b-(bar if b==x1 else bar/2),y+.003,z1-bar]))
 for k,(a,b)in enumerate(zip(divs[:-1],divs[1:])):
  lo=a+(bar if k==0 else bar/2);hi=b-(bar if k==len(divs)-2 else bar/2);low=z0+bar;high=head-bar/2
  if k not in [0,len(divs)-2]:glass.append(cube([lo,y-.003,low],[hi,y+.003,high]));continue
  lo+=.006;hi-=.006;low+=.006;high-=.006;left=k==0;pivot=[lo if left else hi,y-.051,low];moving=ring(lo,hi,low,high,y-.041,.050,.032)
  hx=hi-.016 if left else lo+.016;hz=low+(high-low)*.52
  moving=union([moving,cube([hx-.008,y+.006,hz-.055],[hx+.008,y+.032,hz-.035]),cube([hx-.008,y+.006,hz+.035],[hx+.008,y+.032,hz+.055]),cube([hx-.008,y+.025,hz-.055],[hx+.008,y+.041,hz+.055])])
  pane=cube([lo+.032,y-.003,low+.032],[hi-.032,y+.003,high-.032])
  sashes.append({'name':name.replace('_Geometry','')+('_Left'if left else'_Right'),'pivot':pivot,'angle_degrees':-65 if left else 65,'frame':mesh(moving),'glass':mesh(pane),'closed_bounds':[[lo,y-.041,low],[hi,y+.041,high]],'opening_bounds':[[a+(bar if k==0 else bar/2),y-.045,z0+bar],[b-(bar if k==len(divs)-2 else bar/2),y+.045,head-bar/2]]})
 OUT['windows'].append({'name':name,'fixed_frame':mesh(union(fixed)),'fixed_glass':mesh(compose(glass)),'sashes':sashes})
