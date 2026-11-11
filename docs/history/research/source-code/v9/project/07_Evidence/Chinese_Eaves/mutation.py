"""V8 Chinese eaves: isolated source-grounded scene mutation, never edits V7."""
import sys,json,math,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','libs','geomlibs']]+[str(W),str(W/'v4_audit_junction')]
import numpy as np
from collections import Counter
import export_v5 as ex
import apply_junction_v4 as J
OUT=Path(__file__).parent
SOURCE=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(SOURCE.read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
replace=[];add=[];remove=[];changes=[]
def part(g,m='M_Roof'):return dict(geometry=g,material=m)
def put(name,parts,classification='CHINESE_CURVED_TILE_ROOF',refs=None,**extra):
 e=copy.deepcopy(E[name]) if name in E else dict(name=name,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM')
 e.update(parts=parts,classification=classification,source='; '.join(refs or ['DJI_0046.JPG','DJI_0110.JPG','Registered original JIA OBJ roof samples']),status='V8_PHOTO_AND_REGISTERED_SCAN_CORRECTED; DETAILS_PROVISIONAL',**extra)
 (replace if name in E else add).append(e);return e
def shell(xs,ys,fn,thickness=.075):
 nx=len(xs);ny=len(ys);top=np.array([[x,y,fn(x,y)] for x in xs for y in ys]);v=np.vstack([top,top+[0,0,-thickness]]);N=len(top);f=[]
 for i in range(nx-1):
  for j in range(ny-1):
   a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;f += [[a,b,c],[a,c,d],[d+N,c+N,b+N],[d+N,b+N,a+N]]
 rim=list(range(ny))+[i*ny+ny-1 for i in range(1,nx)]+[(nx-1)*ny+j for j in range(ny-2,-1,-1)]+[i*ny for i in range(nx-2,0,-1)]
 for a,b in zip(rim,rim[1:]+rim[:1]):f.append([b,a,a+N,b+N])
 return dict(type='polyhedron',vertices=v.tolist(),faces=f)
def tube(points,r=.035,segments=10):
 p=np.array(points);closed=np.linalg.norm(p[0]-p[-1])<1e-8
 if closed:p=p[:-1]
 verts=[]
 for i,c in enumerate(p):
  t=p[(i+1)%len(p)]-p[(i-1)%len(p)] if closed else p[min(i+1,len(p)-1)]-p[max(i-1,0)];t/=np.linalg.norm(t);q=np.array([0,1,0.])
  if abs(q@t)>.9:q=np.array([1,0,0.])
  u=np.cross(t,q);u/=np.linalg.norm(u);v=np.cross(t,u)
  verts += [(c+r*(u*math.cos(a)+v*math.sin(a))).tolist() for a in np.linspace(0,2*math.pi,segments,endpoint=False)]
 f=[]
 for i in range(len(p) if closed else len(p)-1):
  k=(i+1)%len(p)
  for j in range(segments):f.append([i*segments+j,i*segments+(j+1)%segments,k*segments+(j+1)%segments,k*segments+j])
 if not closed:f.extend([list(range(segments-1,-1,-1)),list(range((len(p)-1)*segments,len(p)*segments))])
 return dict(type='polyhedron',vertices=verts,faces=f)
def zscreen(x,y):
 t=abs((x-7.025)/4.075);v=abs((y+16.9)/.74)
 return 3.88-.25*v**1.4+.65*t**4+.12*t**5*v**2
def zgate(x,y):
 t=abs((x-6.55)/2.55);v=abs((y+11.62)/1.40)
 return 4.35-.58*v**1.6+.30*t**6+.40*t**5*v**3
def zkitchen(x,y):
 # Robust independent fitted ordinary scan tile planes. Roof substrate is
 # 50mm below cover tile scan surface; ornamental high points are excluded.
 west=-.29889484+.39953197*x-.00177447*y
 east=9.41247826-.440834917*x+.00312578606*y
 return min(west,east)-.050+.080*max(0,(7.2-x)/.22)**2
def cover_tile(fn,x,y,axis,l,ro=.058,ri=.050):
 # Annular half-cylinder follows sampled ordinary roof pitch; true capped,
 # nonzero shell thickness, no tubes crossing adjoining roof surfaces.
 rings=[];a=np.linspace(0,math.pi,13);ends=[0,l/2,l]
 for k in ends:
  xx=x+k if axis==0 else x;yy=y+k if axis==1 else y
  z=fn(xx,yy)+.005;delta=.001
  grad=(fn(xx+delta,yy)-fn(xx-delta,yy))/(2*delta) if axis==0 else (fn(xx,yy+delta)-fn(xx,yy-delta))/(2*delta)
  tang=np.array([1,0,grad]) if axis==0 else np.array([0,1,grad]);tang/=np.linalg.norm(tang)
  lateral=np.array([0,1,0.]) if axis==0 else np.array([1,0,0.]);norm=np.cross(tang,lateral)
  if norm[2]<0:norm=-norm
  ring=[(np.array([xx,yy,z])+r*(math.cos(t)*lateral+math.sin(t)*norm)).tolist() for r in [ro,ri] for t in a];rings+=ring
 N=26;f=[]
 for j in range(2):
  for k in range(12):
   o=j*N+k;i=j*N+13+k;f.extend([[o,o+1,o+N+1,o+N],[i+N,i+N+1,i+1,i]])
  f += [[j*N,j*N+N,j*N+N+13,j*N+13],[j*N+12,j*N+25,j*N+N+25,j*N+N+12]]
 for off,reverse in [(0,True),(52,False)]:
  for k in range(12):
   face=[off+k,off+13+k,off+13+k+1,off+k+1];f.append(face[::-1] if reverse else face)
 return dict(type='polyhedron',vertices=rings,faces=f)
def tile_rows(name,fn,bounds,axis,pitch=.18,module=.28):
 x0,y0,x1,y1=bounds;cross=np.arange((y0 if axis==0 else x0)+.06,(y1 if axis==0 else x1)-.045,pitch);along0=x0 if axis==0 else y0;along1=x1 if axis==0 else y1;parts=[]
 for c in cross:
  for a in np.arange(along0+.008,along1-.008,module):
   ll=min(module-.006,along1-.008-a)
   if ll<.02:continue
   parts.append(part(cover_tile(fn,a,c,0,ll) if axis==0 else cover_tile(fn,c,a,1,ll)))
 return put(name,parts,visible_cover_tile_modules=len(parts),dimension_status='PHOTO_ESTIMATED_MODULES_NOT_FIELD_TILE_COUNT')
def curved_roof(name,fn,bounds,ridgey,xsegments):
 x0,y0,x1,y1=bounds;ys=np.unique(np.round(np.r_[np.linspace(y0,y1,17),ridgey],10));xs=np.linspace(x0,x1,xsegments)
 return put(name,[part(shell(xs,ys,fn))],roof_sampling_grid=[len(xs),len(ys)])
def ridge_and_eaves(prefix,fn,bounds,ridgey,flower=False):
 x0,y0,x1,y1=bounds;xs=np.linspace(x0+.03,x1-.03,81);ridge=[];border=[];lattice=[]
 for y in [y0+.012,y1-.012]:border.append(part(tube([[x,y,fn(x,y)-.015] for x in xs],.052,12)))
 lower,upper=(.045,.200) if 'SCREENWALL' in prefix else (.095,.290)
 for offset,r in [(lower,.026),(upper,.034)]:ridge.append(part(tube([[x,ridgey,fn(x,ridgey)+offset] for x in xs],r,12)))
 # X / flower pierced crown follows the real curved ridge, rather than a
 # horizontal strip with empty floating scan contours above it.
 for cx in np.arange(x0+.18,x1-.12,.23):
  if flower:
   zz=fn(cx,ridgey)+(lower+upper)/2
   # Four curved petals with actual negative openings; photograph motif is
   # floral rather than a plain repetitive crossed fence.
   for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
    pts=[]
    for a in np.linspace(0,2*math.pi,17):
     rr=.046;pts.append([cx+dx*.040+rr*math.cos(a),ridgey,zz+dz*.036+rr*.80*math.sin(a)])
    lattice.append(part(tube(pts,.009,8)))
  else:
   for slope in [-1,1]:
    pts=[[cx+s,ridgey,fn(cx+s,ridgey)+.19+s*slope*.75] for s in np.linspace(-.10,.10,7)];lattice.append(part(tube(pts,.012,8)))
 for x in [x0+.015,x1-.015]:
  # Upright outer ridge ends connect top and lower rails to the flown tiles.
  ridge.append(part(tube([[x,ridgey,fn(x,ridgey)+z] for z in [.025,lower,(lower+upper)/2,upper]],.030,12)))
 put(prefix+'_OPEN_RIDGE_LATTICE',ridge+lattice,classification='CHINESE_PIERCED_CURVED_RIDGE',real_negative_spaces=True)
 put(prefix+'_CURVED_EAVE_AND_RIDGE_BORDER',border,classification='CHINESE_CURVED_EAVE_MOULDING')
screen_bounds=[2.95,-17.64,11.10,-16.16]
gate_bounds=[4.05,-13.02,9.05,-10.22]
curved_roof('SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL',zscreen,screen_bounds,-16.9,65)
tile_rows('SITE_SOUTH_SCREENWALL_BARREL_TILE_ROWS',zscreen,screen_bounds,1,.18,.245)
ridge_and_eaves('SITE_SOUTH_SCREENWALL',zscreen,screen_bounds,-16.9,True)
curved_roof('SITE_INNER_GATEHOUSE_ROOF_CURVED_TILE_SHELL',zgate,gate_bounds,-11.62,65)
tile_rows('SITE_INNER_GATEHOUSE_ROOF_BARREL_TILE_ROWS',zgate,gate_bounds,1,.18,.265)
ridge_and_eaves('SITE_INNER_GATEHOUSE_ROOF',zgate,gate_bounds,-11.62,True)
# The gate upper masonry closure meets the ordinary roof underside. Retain
# lower door jambs/portal opening; no invented new doorway or timber class.
for name,fn,rectxy,base,m in [('SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE',zgate,[4.9,-11.95,8.3,-11.45],2.45,'M_Stone_Frame'),('SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE',zscreen,[3.25,-17.1,10.8,-16.72],2.6,'M_Wall_Exterior')]:
 x0,y0,x1,y1=rectxy;support=shell(np.linspace(x0,x1,33),np.linspace(y0,y1,7),lambda x,y:fn(x,y)-.075,.075)
 # A closed varying-height body extends to the existing upper wall plane.
 n=len(support['vertices'])//2
 for p in support['vertices'][n:]:p[2]=base
 put(name,[part(support,m)],classification='MASONRY_ROOF_BASE_CLOSURE')
# Kitchen keeps the masonry gables and Chinese timber front; ridge and
# pitch follow registered ordinary tile samples. West wood beam is unchanged.
kx=np.unique(np.r_[np.linspace(6.98,13.60,43),11.515]);ky=np.linspace(-12.05,-2.15,19)
put('SITE_KITCHEN_CHINESE_TILE_ROOF',[part(shell(kx,ky,zkitchen,.075))],classification='CHINESE_TIMBER_SUPPORTED_GABLE_TILE_ROOF',ridge_local_x=11.515)
tile_rows('SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0',zkitchen,[6.98,-12.05,11.515,-2.15],0,.24,.28)
tile_rows('SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1',zkitchen,[11.515,-12.05,13.60,-2.15],0,.24,.28)
frames=[]
for yy in np.arange(-11.1,-3.2,1.1):
 frames.append(part(J._box(7.7,yy-.05,zkitchen(7.7,yy)-.075-.16,5.45,.10,.16),'M_Timber_Honey'))
 for xa,xb in [(6.98,11.515),(11.515,13.6)]:
  pts=[[x,yy,zkitchen(x,yy)-.120] for x in np.linspace(xa,xb,19)];frames.append(part(tube(pts,.04,8),'M_Timber_Honey'))
put('SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING',frames,classification='CHINESE_TIMBER_PURLIN_AND_RAFTER',west_beam_roof_contact_gap_m=0)
timber=copy.deepcopy(E['SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS']['parts'])
for p in timber:
 g=p['geometry']
 if g['type']=='cylinder':g['height']=2.488-g['origin'][2]
 if g['type']=='box' and g['origin'][2]>2.5:
  x,y,_=g['origin'];w,d,_=g['size'];head=shell([x,x+w],[y,y+d],lambda xx,yy:zkitchen(xx,yy)-.075,.075)
  for vv in head['vertices'][len(head['vertices'])//2:]:vv[2]=2.488
  p['geometry']=head
put('SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS',timber,classification='EXPOSED_CHINESE_TIMBER_FRAME',roof_contact_corrected=True)
# Combined masonry end-wall/gable bodies have their top exactly at the
# curved roof underside. Retire separate overlapping old gable infills.
mas=[]
for x0,y0,x1,y1 in [(7.7,-11.6,13.35,-11.38),(7.7,-2.82,13.35,-2.6),(13.13,-11.38,13.35,-2.82)]:
 g=shell(np.unique(np.r_[np.linspace(x0,x1,25),11.515][(np.r_[np.linspace(x0,x1,25),11.515]>=x0)&(np.r_[np.linspace(x0,x1,25),11.515]<=x1)]),[y0,y1],lambda x,y:zkitchen(x,y)-.075,.075)
 for p in g['vertices'][len(g['vertices'])//2:]:p[2]=-.4
 mas.append(part(g,'M_Grey_Brick'))
put('SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES',mas,classification='MASONRY_BACK_AND_GABLE_WALLS')
remove += ['SITE_KITCHEN_GABLE_INFILL_-11.49','SITE_KITCHEN_GABLE_INFILL_-2.71']
# Historic model central roof ridge was absent; provide a continuous curved
# tile cap, three photographed upstanding terminal / central ridge ornaments.
rp=[]
for a in np.arange(-12.0,-2.2,.30):rp.append(part(tube([[11.515,y,zkitchen(11.515,y)+.115] for y in np.linspace(a,min(a+.295,-2.2),5)],.070,14)))
for yy in [-11.96,-7.15,-2.24]:
 zz=zkitchen(11.515,yy)+.115;prof=[[11.385,yy-.045,zz],[11.385,yy-.045,4.99],[11.515,yy-.045,5.15],[11.645,yy-.045,4.99],[11.645,yy-.045,zz]];rp.append(part(dict(type='prism',profile=prof,vector=[0,.09,0])))
put('SITE_KITCHEN_RIDGE_CAP_AND_END_ORNAMENTS',rp,classification='CHINESE_TILE_RIDGE_ORNAMENTS',ornamental_peak_separate_from_ordinary_roof=True)
# Courtyard wall stops at the solid southwest column (front planeY1.9),
# rather than floating in front of the bay glazing/terminating atY1.0.
for name in ['SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING']:
 e=copy.deepcopy(E[name]);changed=0
 for p in e['parts']:
  g=p['geometry']
  if g['type']=='polyhedron':
   for v in g['vertices']:
    if abs(v[1]-1)<1e-8:v[1]=1.9;changed+=1
 put(name,e['parts'],classification=E[name].get('classification','CHINESE_TILE_TOP_MASONRY_WALL'),termination_target='KZ_1_1_F1 front solid face Y1.9',extended_vertices=changed)
e=copy.deepcopy(E['SITE_COURTYARD_WEST_WHITE_INSIDE'])
for p in e['parts']:
 g=p['geometry']
 if g['type']=='prism_holes':
  for ring in [g['outer']]+g.get('holes',[]):
   for v in ring:
    if abs(v[1]-1)<1e-8:v[1]=1.9
 elif g['type']=='box':g['size'][1]+=.9
 elif g['type']=='polyhedron':
  for v in g['vertices']:
   if abs(v[1]-1)<1e-8:v[1]=1.9
put(e['name'],e['parts'],classification='PLASTER_INSIDE_MASONRY_WALL')
changes=[dict(id='V8_CHINESE_EAVE_CURVES',description='门楼、照壁曲面及瓦件按原OBJ普通屋面高度与照片飞翘修正，脊带及檐口随曲面；厨房脊东移避免门厨房瓦面互穿',evidence=['DJI_0046.JPG','DJI_0110.JPG','Registered original JIA OBJ sampled roof points'],metric_status='REGISTERED_SCAN_PROFILE_FIT; PHOTO_ESTIMATED_TILE_MODULES'),dict(id='V8_WALL_BUILDING_CLOSURE',description='西侧瓦顶院墙延至实体角柱Y1.9处收头，保持窗玻璃完整',evidence=['User screenshot001317','User screenshot001738'],metric_status='MODEL_SOLID_INTERFACE')]
def orient(g):
 if g['type']!='polyhedron':return
 fs=g['faces'];edges={}
 for i,f in enumerate(fs):
  for a,b in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((i,a,b))
 neighbors=[[] for f in fs]
 for rows in edges.values():
  if len(rows)!=2:raise ValueError('Unclosed builder geometry')
  (i,a,b),(j,c,d)=rows;same=(a==c and b==d);neighbors[i].append((j,same));neighbors[j].append((i,same))
 state={}
 for root in range(len(fs)):
  if root in state:continue
  state[root]=False;queue=[root]
  while queue:
   i=queue.pop()
   for j,same in neighbors[i]:
    want=state[i]^same
    if j in state:
     if state[j]!=want:raise ValueError('Nonorientable geometry')
    else:state[j]=want;queue.append(j)
 fs=[f[::-1] if state[i] else f for i,f in enumerate(fs)];v=np.array(g['vertices']);vol=0
 for f in fs:
  for j in range(1,len(f)-1):vol+=np.dot(v[f[0]],np.cross(v[f[j]],v[f[j+1]]))/6
 if vol<0:fs=[f[::-1] for f in fs]
 g['faces']=fs
for e in replace+add:
 for p in e['parts']:orient(p['geometry'])
mutation=dict(replace=replace,add=add,remove=remove,materials={},definitions={},changes=changes)
def apply(scene):
 scene['elements']=[e for e in scene['elements'] if e['name'] not in set(remove)|{e['name'] for e in replace}]+copy.deepcopy(replace)+copy.deepcopy(add)
 scene.setdefault('v8_changes',[]).extend(copy.deepcopy(changes));return scene
if __name__=='__main__':
 (OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf-8')
 qa=[]
 for e in replace+add:
  for i,p in enumerate(e['parts']):
   v,fs,_,_=ex.solid_data(p['geometry']);edges=Counter(tuple(sorted((a,b))) for f in fs for a,b in zip(f,f[1:]+f[:1]));bad=[edge for edge,n in edges.items() if n!=2]
   if bad:raise ValueError((e['name'],i,'nonmanifold',len(bad)))
   directed=Counter((a,b) for f in fs for a,b in zip(f,f[1:]+f[:1]));bad_directed=sum(n!=directed.get((b,a),0) for (a,b),n in directed.items())
   if bad_directed:raise ValueError((e['name'],i,'inconsistent_winding',bad_directed))
   if not np.isfinite(v).all():raise ValueError('Nonfinite')
  qa.append(dict(name=e['name'],parts=len(e['parts']),manifold_all=True,consistent_outward_winding=True))
 samples=np.load(OUT/'Donor_Roof_Samples.npz')['centroids'];fit=[]
 for name,fn,b,zlimits in [('kitchen',zkitchen,[7.0,-10,13.4,-3],[2.5,4.45]),('gate',zgate,[4.7,-12.95,8.5,-10.3],[3.55,4.55]),('screen',zscreen,[3.2,-17.6,10.9,-16.2],[3.55,4.45])]:
  x0,y0,x1,y1=b;q=samples[(samples[:,0]>=x0)&(samples[:,0]<=x1)&(samples[:,1]>=y0)&(samples[:,1]<=y1)&(samples[:,2]>=zlimits[0])&(samples[:,2]<=zlimits[1])]
  if name=='screen':q=q[abs(q[:,1]+16.9)>.18]
  r=np.array([p[2]-fn(*p[:2])-.050 for p in q]);fit.append(dict(region=name,sampling_xy=b,ordinary_roof_z_band=zlimits,samples=len(q),rmse_m=float(np.sqrt(np.mean(r*r))),median_signed_m=float(np.median(r)),absolute_p95_m=float(np.quantile(abs(r),.95)),note='NormalsZ>0.3 and ordinary roof bands; ornament/lattice excluded; ordinary cover surface=substrate+50mm; source model alignment remains provisional'))
 (OUT/'Geometry_QA.json').write_text(json.dumps(dict(status='PASS_CLOSED_MANIFOLD_GEOMETRY',elements=qa,scan_fit=fit,wall_terminal_y=1.9,gate_kitchen_separation_m_min=min(zgate(x,y)-.075-zkitchen(x,y)-.10 for x in np.linspace(6.98,9.05,50) for y in np.linspace(-12.05,-10.22,50))),indent=2),encoding='utf-8')
 print('Wrote',len(replace),'replace,',len(add),'added; tile modules',sum(e.get('visible_cover_tile_modules',0) for e in replace+add));print(json.dumps(fit,indent=2))
