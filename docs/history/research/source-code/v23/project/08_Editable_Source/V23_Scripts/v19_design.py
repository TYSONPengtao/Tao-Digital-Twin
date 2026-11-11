"""Perimeter masonry, eave bands and solid wall coping from the 14:50 walk."""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely import set_precision
from shapely.geometry import Polygon,LineString,Point,box as sb
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from PIL import Image,ImageFilter
B=Path(r'E:/jz/JIA/Rebuild_V18');O=Path(r'E:/jz/JIA/Rebuild_V19');D=W/'v19';D.mkdir(exist_ok=True);T=O/'03_Textures/V19_Perimeter_AsBuilt';T.mkdir(parents=True,exist_ok=True);REF=O/'07_Reference/INSV_Perimeter'
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V18.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V18.json').read_text(encoding='utf8'))}
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman']),('v14_building.py',['part','beam','box'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[]};proof={'reference':'Original INSV user reference 890 s; wall walk 870..972 s; DJI_0073 coping overview','dimension_status':'Photo fitted finishes on the retained registered wall route; no new field measurements','textures':[],'wall_solid_unions':[],'coping':[],'ornament_contacts':[]}
def fromman(a):
 # Remove zero-volume Boolean sheets and simplify below the 1 mm CAD tolerance.
 a=mf.Manifold.batch_boolean([p for p in a.decompose() if abs(p.volume())>1e-10],mf.OpType.Add)
 for tol in [1e-7,1e-6,1e-5]:
  b=a.set_tolerance(tol).simplify(tol);mm=b.to_mesh64();v=np.asarray(mm.vert_properties)[:,:3];f=np.asarray(mm.tri_verts);g={'type':'polyhedron','vertices':v.tolist(),'faces':f.tolist()}
  try:return oriented(g)
  except ValueError:continue
 for digits in [8,7,6]:
  vv,inv=np.unique(np.round(v,digits),axis=0,return_inverse=True);ff=inv[f];ff=ff[(ff[:,0]!=ff[:,1])&(ff[:,1]!=ff[:,2])&(ff[:,0]!=ff[:,2])];b=mf.Manifold(mf.Mesh64(vv,ff.astype(np.uint64)))
  if b.status()!=mf.Error.NoError:continue
  mm=b.simplify(1e-6).to_mesh64();vg=np.asarray(mm.vert_properties)[:,:3];fg=np.asarray(mm.tri_verts);gg={'type':'polyhedron','vertices':vg.tolist(),'faces':fg.tolist()}
  try:
   out=oriented(gg);proof.setdefault('boolean_cleanup',[]).append({'quantization_m':10**(-digits),'maximum_vertex_rounding_m':math.sqrt(3)*.5*10**(-digits),'triangles':len(fg)});return out
  except ValueError:continue
 (D/'Repair_Target.json').write_text(json.dumps(g),encoding='utf8')
 raise ValueError('Boolean output needs explicit local repair '+str((len(v),len(f))))
def tex(label,fp,quad,size):
 im=Image.open(fp).convert('RGB');q=tuple(v for p in [quad[0],quad[3],quad[2],quad[1]] for v in p);im=im.transform(size,Image.Transform.QUAD,q,Image.Resampling.BICUBIC);v=np.asarray(im,dtype=float);hh,ww=v.shape[:2];a=np.zeros_like(v);a[0]=v[-1]-v[0];a[-1]=v[0]-v[-1];a[:,0]+=v[:,-1]-v[:,0];a[:,-1]+=v[:,0]-v[:,-1];den=2*np.cos(2*np.pi*np.arange(hh)[:,None]/hh)+2*np.cos(2*np.pi*np.arange(ww)[None,:]/ww)-4;den[0,0]=1;sp=np.fft.fft2(a,axes=(0,1))/den[:,:,None];sp[0,0]=0;v=np.clip(v-np.fft.ifft2(sp,axes=(0,1)).real,0,255);out=Image.fromarray(v.astype(np.uint8));out.save(T/(label+'.png'));out.convert('L').save(T/(label+'_Height.png'));proof['textures'].append({'texture':label,'reference':str(fp),'quad_pixels_TL_TR_BR_BL':quad,'method':'Real frame planar patch extraction with periodic luminance correction','mean_boundary_rgb_difference_255':[float(abs(v[:,0]-v[:,-1]).mean()),float(abs(v[0]-v[-1]).mean())]})
tex('Perimeter_Actual_Gray_Brick',REF/'INSV_0890s_L0_Y-50_P+05.jpg',[[450,360],[1650,420],[1660,1100],[450,1200]],(1536,1024))
tex('Perimeter_Actual_Dark_Stone',REF/'INSV_0935s_L1_Y+45_P+15.jpg',[[850,1375],[1940,1430],[1940,1600],[850,1545]],(1536,256))
rng=np.random.default_rng(19890);no=rng.normal(0,1,(512,512));sm=np.asarray(Image.fromarray(np.uint8(np.clip(no*20+128,0,255))).filter(ImageFilter.GaussianBlur(16)),dtype=float)-128
for n,col in [('Weathered_Wall_Tile',[80,83,80]),('Pale_Limewash_Band',[205,205,194])]:
 v=np.clip(np.array(col)[None,None,:]+no[:,:,None]*2.3+sm[:,:,None]*1.4,0,255).astype(np.uint8);Image.fromarray(v).save(T/(n+'.png'));Image.fromarray(v.mean(2).astype(np.uint8)).save(T/(n+'_Height.png'))
NM={
 'M_V19_Perimeter_Brick':{'bitmap':'Perimeter_Actual_Gray_Brick.png','bump':'Perimeter_Actual_Gray_Brick_Height.png','color':[255,255,255],'roughness':.93,'repeat_m':[1.60,.90],'bump_distance_m':.0018},
 'M_V19_Perimeter_Dark_Stone':{'bitmap':'Perimeter_Actual_Dark_Stone.png','bump':'Perimeter_Actual_Dark_Stone_Height.png','color':[255,255,255],'roughness':.94,'repeat_m':[3.60,.56],'bump_distance_m':.002},
 'M_V19_Perimeter_Rubble':{'bitmap_relative':'V18_Storage_AsBuilt/Photo_Rubble_Stone.png','bump_relative':'V18_Storage_AsBuilt/Photo_Rubble_Microheight.png','color':[255,255,255],'roughness':.96,'repeat_m':[3.20,2.30],'bump_distance_m':.003},
 'M_V19_Limewash_Band':{'bitmap':'Pale_Limewash_Band.png','bump':'Pale_Limewash_Band_Height.png','color':[255,255,255],'roughness':.96,'bump_distance_m':.0005},
 'M_V19_Weathered_Wall_Tile':{'bitmap':'Weathered_Wall_Tile.png','bump':'Weathered_Wall_Tile_Height.png','color':[255,255,255],'roughness':.91,'bump_distance_m':.0008},
 'M_V19_Perimeter_Road_Shoulder':{'bitmap_relative':'V18_Storage_AsBuilt/Road_Shoulder_Microaggregate.png','bump_relative':'V18_Storage_AsBuilt/Road_Shoulder_Height.png','color':[255,255,255],'roughness':.98,'bump_distance_m':.001},
}
def put(n,ps,new=False,**meta):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'};e.update(parts=ps,v19_perimeter=True,source=proof['reference'],dimension_status=proof['dimension_status'],**meta);Q['add' if new else 'replace'].append(e);return e
def addall(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def front_faces(g):
 v,fs,_,_=ex.solid_data(g);rows=[]
 for f in fs:
  q=v[f];no=np.cross(q[1]-q[0],q[2]-q[0]);ll=np.linalg.norm(no)
  if ll<1e-12:continue
  no/=ll
  if abs(no[2])<.20 and np.dot(no[:2],np.array([-3.5,-3])-q.mean(0)[:2])<0:
   xy=np.unique(np.round(q[:,:2],9),axis=0)
   if len(xy)!=2:continue
   a,b=xy;ta=float(v[np.linalg.norm(v[:,:2]-a,axis=1)<1e-7,2].max());tb=float(v[np.linalg.norm(v[:,:2]-b,axis=1)<1e-7,2].max());rows.append({'a':a.tolist(),'b':b.tolist(),'za':ta,'zb':tb,'normal':no[:2].tolist()})
 return rows
bricksegments=[];stonesegments=[];cores={};bricks={};lowers={};darks={};bands=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 bs=[];ls=[];ds=[];original=[]
 for pp in E[n]['parts']:
  g=pp['geometry'];a=manifold(g);original.append(a);v=np.asarray(oriented(g)['vertices'])
  if pp['material']=='M_Grey_Brick':
   bs.append(a);rr=front_faces(g)
   for r in rr:r['node']=n
   bricksegments.extend(rr)
   for r in rr:
    if np.linalg.norm(np.array(r['b'])-np.array(r['a']))<.34:continue
    mid=(np.array(r['a'])+np.array(r['b']))/2
    if n.endswith('_0') and 3.25<mid[0]<10.8 and mid[1]<-16:continue
    pa,pb=np.array(r['a']),np.array(r['b']);no=np.array(r['normal']);z1,z2=r['za'],r['zb'];q=[[*(pa-no*.002),z1-.47],[*(pb-no*.002),z2-.47],[*(pb-no*.002),z2-.035],[*(pa-no*.002),z1-.035]];bands.append(manifold({'type':'prism','profile':q,'vector':[*(no*.010),0]}))
  elif pp['material']=='M_Stone_Rubble':
   tops=[];v0,fs,_,_=ex.solid_data(oriented(g));tt=v0[triangles(v0,fs)];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);tops=tt[nn[:,2]>.7*np.linalg.norm(nn,axis=1)].reshape(-1,3);co=np.linalg.lstsq(np.c_[tops[:,:2],np.ones(len(tops))],tops[:,2],rcond=None)[0];xmin,ymin=v[:,:2].min(0)-.1;xmax,ymax=v[:,:2].max(0)+.1;xy=np.array([[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]]);h=np.c_[xy,np.ones(4)]@co-.56;vv=np.vstack([np.c_[xy,np.full(4,-8.)],np.c_[xy,h]]);clip=manifold({'type':'polyhedron','vertices':vv.tolist(),'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]});lo=a^clip;da=a-lo
   if not lo.is_empty():ls.append(lo)
   if not da.is_empty():ds.append(da)
   rr=front_faces(g)
   for r in rr:r.update(node=n,top_plane=co.tolist())
   stonesegments.extend(rr)
  else:raise ValueError(pp['material'])
 cores[n]=addall(original);bricks[n]=addall(bs);lowers[n]=addall(ls);darks[n]=addall(ds);after=bricks[n]+lowers[n]+darks[n];sym=(cores[n]-after).volume()+(after-cores[n]).volume();assert sym<1e-6,sym;proof['wall_solid_unions'].append({'node':n,'original_parts':len(original),'original_connected_sections':len(cores[n].decompose()),'material_union_sections':len(after.decompose()),'before_after_symmetric_volume_m3':sym,'dark_course_band_depth_m':.56})
print('PERIMETER CORE PARTITIONS READY',flush=True)
south=[r for r in bricksegments if min(r['a'][1],r['b'][1])<-16 and abs(r['b'][0]-r['a'][0])>abs(r['b'][1]-r['a'][1])*2 and max(r['a'][0],r['b'][0])>=3.2 and min(r['a'][0],r['b'][0])<=10.85]
assert south
def segment_for(x):
 cand=[r for r in south if min(r['a'][0],r['b'][0])-1e-6<=x<=max(r['a'][0],r['b'][0])+1e-6]
 assert cand,('missing lower wall under screen',x)
 return min(cand,key=lambda r:(r['a'][1]+r['b'][1])/2)
def front_y(x):
 r=segment_for(x);a,b=np.array(r['a']),np.array(r['b']);return float(a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]))
def normal(x):return np.array(segment_for(x)['normal'])
rd=np.load(B/'02_Data'/I['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL']['file']);rt=rd['vertices'][rd['faces']];rn=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);rt=rt[abs(rn[:,2])>1e-8]
def underroof(x,y):
 p=np.array([x,y]);ts=rt[(rt[:,:,:2].min(1)<=p+1e-7).all(1)&(rt[:,:,:2].max(1)>=p-1e-7).all(1)];zz=[]
 for t in ts:
  a=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]]);v=np.linalg.solve(a,p-t[0,:2])
  if (v>=-1e-6).all() and v.sum()<=1+1e-6:zz.append(float(t[0,2]+v@(t[1:,2]-t[0,2])))
 assert zz,(x,y);return min(zz)
def head(x):return underroof(x,front_y(x))
xs=sorted(set([round(float(x),10) for x in np.linspace(3.25,10.8,51)]+[float(p[0]) for r in south for p in [r['a'],r['b']] if 3.25<p[0]<10.8]));vv=[];ny=7
for bottom in [False,True]:
 for x in xs:
  fy=front_y(x);by=fy+.32/max(abs(normal(x)[1]),.85)
  for f in np.linspace(0,1,ny):
   y=fy+(by-fy)*f;vv.append([x,y,2.14 if bottom else underroof(x,y)+.004])
nt=len(xs)*ny;ff=[]
for i in range(len(xs)-1):
 for j in range(ny-1):
  k=i*ny+j;ff.extend([[k,k+ny,k+ny+1],[k,k+ny+1,k+1],[k+nt,k+ny+1+nt,k+ny+nt],[k+nt,k+1+nt,k+ny+1+nt]])
boundary=list(range(ny))+[i*ny+ny-1 for i in range(1,len(xs))]+list(range((len(xs)-1)*ny+ny-2,(len(xs)-1)*ny-1,-1))+[i*ny for i in range(len(xs)-2,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):ff.append([a,b,b+nt,a+nt])
sg=oriented({'type':'polyhedron','vertices':vv,'faces':ff});screen=manifold(sg);contact=(screen^bricks['SITE_PERIMETER_JOINED_RETAINING_WALL_0']).volume();assert contact>1e-3,contact;bricks['SITE_PERIMETER_JOINED_RETAINING_WALL_0']+=screen
Q['remove']+=['SITE_SOUTH_SCREENWALL_RAISED_BODY','SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE','SITE_SCREENWALL_HORIZONTAL_MOULDINGS']+[n for n in E if n.startswith('SITE_SCREENWALL_STEPPED_PANEL_')]
proof['screenwall']={'front_follows_registered_lower_wall':True,'core_width_normal_m':.32,'lower_joint_overlap_m3':contact,'roof_bearing_overlap_m3':(screen^manifold(E['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL']['parts'][0]['geometry'])).volume(),'previous_large_white_blank_plate_removed':True,'outer_front_xy':[[x,front_y(x)] for x in xs]}
print('SCREEN CORE ALIGNED',proof['screenwall']['lower_joint_overlap_m3'],flush=True)
# Thin surface bands and mouldings follow the actual lower wall curve and roof underside.
def dense(poly):
 rings=[]
 for ring in [poly.exterior]+list(poly.interiors):
  pts=list(ring.coords)[:-1];out=[]
  for a,b in zip(pts,pts[1:]+pts[:1]):
   out.append(a)
   if abs(a[0]-b[0])>1e-8:
    xx=sorted(set([float(x) for x in xs if min(a[0],b[0])+1e-7<x<max(a[0],b[0])-1e-7]+list(np.arange(min(a[0],b[0])+.12,max(a[0],b[0]),.12))),reverse=a[0]>b[0])
    for x in xx:out.append((x,a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])))
  rings.append(out)
 return Polygon(rings[0],rings[1:])
def curved_plate(poly,d0,d1,inside=False):
 # Subdivide the caps as well as their boundary. A single global diagonal
 # across the curved head would lift the narrow frames off the backing.
 xmin,zmin,xmax,zmax=poly.bounds;cuts=sorted(set([xmin,xmax]+[x for x in xs if xmin+1e-6<x<xmax-1e-6]+list(np.arange(xmin+.10,xmax,.10))));pieces=[]
 for aa,bb in zip(cuts[:-1],cuts[1:]):
  if bb-aa<1e-6:continue
  q=set_precision(poly.intersection(sb(aa,zmin-1,bb,zmax+1)),1e-7,mode='valid_output')
  for p in ([q] if q.geom_type=='Polygon' else [p for p in q.geoms if p.geom_type=='Polygon']):
   if p.area<1e-10:continue
   p=orient(p.simplify(1e-7,preserve_topology=True),1);g={'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in p.interiors],'z':d0,'height':d1-d0};v,fs,_,_=ex.solid_data(g);vs=[]
   for x,z,d in v:
    no=normal(x);fy=front_y(x)
    if inside:fy+=.32/max(abs(no[1]),.85);no=-no
    vs.append([x+no[0]*d,fy+no[1]*d,head(x)+z])
   mg={'type':'polyhedron','vertices':vs,'faces':[list(f) for f in fs]}
   try:pieces.append(manifold(oriented(mg)))
   except ValueError:
    (D/'Plate_Local_Repair.json').write_text(json.dumps({'source':g,'mapped':mg,'strip':[aa,bb]},indent=2),encoding='utf8');raise
 return addall(pieces)
screenband=curved_plate(Polygon([[3.25,-.52],[10.8,-.52],[10.8,-.055],[3.25,-.055]]),-.002,.008);screen_frames=[]
spans=[];x=3.39
for width in [1.45,.34,1.45,.34,1.45,.34,1.45]:
 s0,s1=x,x+width;z0,z1=-.447,-.112;st=.024;poly=Polygon([[s0,z0+st],[s0+st,z0+st],[s0+st,z0],[s1-st,z0],[s1-st,z0+st],[s1,z0+st],[s1,z1-st],[s1-st,z1-st],[s1-st,z1],[s0+st,z1],[s0+st,z1-st],[s0,z1-st]])
 for off,w,d in [(0,.019,.021),(.030,.010,.016)]:
  p=poly.buffer(-off,join_style=2);ring=p.difference(p.buffer(-w,join_style=2));screen_frames.append(curved_plate(ring,-.003,d))
 spans.append([s0,s1]);x=s1+.075
ordinary=addall(bands);frames=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_PLASTER_STEPPED_RELIEF','SITE_PERIMETER_JOINED_RETAINING_WALL_1_PLASTER_STEPPED_RELIEF']:
 frames.extend(manifold(p['geometry']) for p in E[n]['parts']);Q['remove'].append(n)
dp=[]
for j,a in enumerate(bands+[screenband]+screen_frames+frames):
 dp.append(part(fromman(a),'M_V19_Limewash_Band'))
put('SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES',dp,True,classification='PALE_UNDEREAVE_STRIP_WITH_RETAINED_STEPPED_MOULDINGS_AND_REPOSITIONED_SCREEN_PANELS',v19_screen_frame_x_spans=spans,v19_surface_offsets_m=[-.003,.008,.021],v19_note='Old screen frames moved from mid-wall to the photographed eave band; four long panels alternate with three short panels; ordinary panels retained on their fitted wall route')
# Extend the inside plaster to the corrected screen head, and remove duplicate thin-layer station caps.
inside=addall([manifold(p['geometry']) for p in E['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH']['parts']]);insideplates=[]
for a,b in zip(xs[:-1],xs[1:]):
 va=[]
 for x in [a,b]:
  no=-normal(x);fy=front_y(x)+.32/max(abs(normal(x)[1]),.85);bot=2.15;top=underroof(x,fy)-.004;va.extend([[x+no[0]*dd,fy+no[1]*dd,z] for dd,z in [(-.002,bot),(.011,bot),(.011,top),(-.002,top)]])
 insideplates.append(manifold({'type':'polyhedron','vertices':va,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}))
inside+=addall(insideplates);put('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH',copy.deepcopy(E['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH']['parts'])+[part(fromman(p),'M_Wall_Exterior') for p in insideplates],v19_note='Existing inside plaster retained with fitted upper screen return; each station is a closed thin solid backed by the masonry')
combined_core=addall(list(bricks.values())+list(lowers.values())+list(darks.values()))
for j,f in enumerate(frames):
 vol=(f^(combined_core+inside+ordinary)).volume();assert vol>1e-10,(j,vol);proof['ornament_contacts'].append({'frame_index':j,'backing_overlap_m3':vol})
proof['screenwall']['frame_count']=len(spans);proof['screenwall']['lime_band_backing_overlap_m3']=(screenband^screen).volume();proof['screenwall']['frame_to_band_contacts_m3']=[(f^screenband).volume() for f in screen_frames];assert min(proof['screenwall']['frame_to_band_contacts_m3'])>1e-8,proof['screenwall']['frame_to_band_contacts_m3']
for n in bricks:put(n,[part(fromman(lowers[n]),'M_V19_Perimeter_Rubble'),part(fromman(darks[n]),'M_V19_Perimeter_Dark_Stone'),part(fromman(bricks[n]),'M_V19_Perimeter_Brick')],v19_dark_stone_band_height_m=.56,v19_note='Original outer wall route and lower retaining elevations retained; material blocks unioned to eliminate duplicated station faces')
# Remove the stylistic all-around pierced crown: the ordinary walls have solid low tile ridges.
# Seat the individual covers/pans and ridge bed positively on their retained substrate.
def crest_values(v,wall):
 rr=[r for r in bricksegments if r['node']==wall];aa=np.array([r['a'] for r in rr]);bb=np.array([r['b'] for r in rr]);dd=bb-aa;za=np.array([r['za'] for r in rr]);zb=np.array([r['zb'] for r in rr]);delta=v[:,:2,None].transpose(0,2,1)-aa[None,:,:];tt=np.clip(np.sum(delta*dd[None,:,:],axis=2)/np.sum(dd*dd,axis=1)[None,:],0,1);ds=np.sum((delta-tt[:,:,None]*dd[None,:,:])**2,axis=2);jj=ds.argmin(1);ss=tt[np.arange(len(v)),jj];return za[jj]*(1-ss)+zb[jj]*ss
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 body=[];counts={'bedding':0,'ridge_seat':0,'tiles':0};shifts=[]
 for p in E[n+'_TILE_COPING']['parts']:
  v,fs,_,_=ex.solid_data(p['geometry']);v=np.array(v);dz=v[:,2]-crest_values(v,n);g=copy.deepcopy(p['geometry'])
  # Six-vertex triangular backing shells plus clipped versions retain their old silhouette.
  bed=len(v)==6 or (dz.min()<.001 and abs(dz.max()-.115)<.003 and len(v)<24)
  ridge=not bed and dz.max()>.145 and dz.min()>.105
  if bed:v[:,2]-=.002;counts['bedding']+=1
  elif ridge:
   low=dz<.140;v[low,2]-=.030;v[:,2]-=.002;counts['ridge_seat']+=1
  else:v[:,2]-=.007;counts['tiles']+=1
  aa=manifold(oriented({'type':'polyhedron','vertices':v.tolist(),'faces':[list(f) for f in fs]}));body.append(aa)
 a=addall(body);cs=a.decompose();kept=[];orphans=[];contacts=[];support=bricks[n]+lowers[n]+darks[n]+inside
 for p in cs:
  vol=p.volume();contact=(p^support).volume()
  if vol<=1e-10 or (vol<1e-5 and contact<1e-10):orphans.append({'volume_m3':vol,'reason':'Zero-volume Boolean sheet or isolated cropped tile tip'});continue
  assert contact>1e-10,('Unsupported coping section',n,vol,contact)
  kept.append(p);contacts.append({'volume_m3':vol,'wall_bearing_overlap_m3':contact})
 a=addall(kept);put(n+'_TILE_COPING',[part(fromman(a),'M_V19_Weathered_Wall_Tile')],v19_finish='Weathered gray wall tile; no invented all-around floral crown',v19_ridge='Retained solid low ridge and circular tile ends',v19_tile_seating_shift_m=-.007,v19_bedding_seating_shift_m=-.002,v19_ridge_bearing_lowered_m=.030)
 Q['remove'].append(n+'_PROVISIONAL_FLOWER_CROWN');proof['coping'].append({'node':n+'_TILE_COPING','part_classes':counts,'supported_sections':contacts,'removed_numerical_sheets_or_orphan_tips':orphans,'connected_sections_after_union':len(a.decompose()),'tiles_lowered_m':.007,'bedding_lowered_m':.002,'ridge_bottom_lowered_m':.030,'source_top_route_preserved_except_tile_seating':True});print('COPING UNION',n,counts,len(a.decompose()),flush=True)
# Tone the actual road-transition strip while keeping every drain/scan boundary coordinate.
segs=json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8'));masks=[]
for s in segs:
 if not s['roadzone']:continue
 a,b=np.array(s['a']),np.array(s['b']);oa=(np.array(s['outer_a'])-a)/1.05;ob=(np.array(s['outer_b'])-b)/1.05;masks.append(Polygon([a+oa*.431,b+ob*.431,b+ob*1.052,a+oa*1.052]))
mask=unary_union(masks).buffer(0);clip=[]
for p in ([mask] if mask.geom_type=='Polygon' else mask.geoms):
 clip.append(manifold({'type':'prism_holes','outer':list(orient(p,1).exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in orient(p,1).interiors],'z':-8,'height':12}))
drain=addall([manifold(p['geometry']) for p in E['SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE']['parts']]);road=drain^addall(clip);gutter=drain-road;put('SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE',[part(fromman(gutter),'M_V16_Drain_Concrete'),part(fromman(road),'M_V19_Perimeter_Road_Shoulder')],v19_note='Road-side shoulder appearance blended in the retained exact geometry; gutter width, longitudinal grade, and survey-mesh boundary unchanged');proof['drain_geometry_unchanged_m3']=(drain-(gutter+road)).volume()+((gutter+road)-drain).volume()
e=E['SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE'];put(e['name'],[part(p['geometry'],'M_V19_Perimeter_Rubble') for p in e['parts']],v19_note='Same closed wall-toe geometry; matching photo rubble finish')
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8');(D/'Materials.json').write_text(json.dumps(NM,ensure_ascii=False,indent=2),encoding='utf8');(D/'Facade_Segments.json').write_text(json.dumps({'brick':bricksegments,'stone':stonesegments,'screen_front':[[x,front_y(x),head(x)] for x in xs]},ensure_ascii=False,indent=2),encoding='utf8');print('V19 DESIGN READY',len(Q['replace']),len(Q['add']),len(Q['remove']),flush=True)
