"""V16: interior soil grading and sealed wall/drain/scan junctions. LOCAL metres."""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np, mapbox_earcut, shapely, export_v5 as ex
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union,nearest_points
from shapely.geometry.polygon import orient
B=Path(r'E:/jz/JIA/Rebuild_V15');D=W/'v16';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
Q={'replace':[],'add':[],'remove':[]};QA={};native={}
def load(n):
 if n not in native:
  d=np.load(B/'02_Data'/ii[n]['file']);native[n]={k:d[k] for k in d.files}
 return native[n]
def polys(g):return [g] if g.geom_type=='Polygon' else [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon' and q.area>1e-10]
def tops(n):
 d=load(n);t=d['vertices'][d['faces']];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9
 return t[up]
def footprint(n):return unary_union([Polygon(q[:,:2]) for q in tops(n)]).buffer(0)
def put(n,g,m,new=False,**props):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM'}
 e.update(parts=[{'geometry':g,'material':m}],source='INSV 749/775/950/972 seconds and user wall/drain screenshot 110221; V15 fixed pavement elevations',**props)
 Q['add' if new else 'replace'].append(e);E[n]=e;return e
def refine(v,faces,maxlen=.8):
 v=[list(p) for p in v];faces=[list(map(int,f)) for f in faces]
 for step in range(12):
  mids={};nv=np.array(v)
  for f in faces:
   for a,b in zip(f,[f[1],f[2],f[0]]):
    k=tuple(sorted([a,b]))
    if k not in mids and np.linalg.norm(nv[a]-nv[b])>maxlen:mids[k]=len(v);v.append(((nv[a]+nv[b])/2).tolist())
  if not mids:return np.array(v),np.array(faces,np.int32)
  ff=[]
  for a,b,c in faces:
   ab=mids.get(tuple(sorted([a,b])));bc=mids.get(tuple(sorted([b,c])));ca=mids.get(tuple(sorted([c,a])));k=sum(q is not None for q in [ab,bc,ca])
   if k==0:ff.append([a,b,c])
   elif k==3:ff.extend([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])
   elif k==1:
    if ab is not None:ff.extend([[a,ab,c],[ab,b,c]])
    elif bc is not None:ff.extend([[b,bc,a],[bc,c,a]])
    else:ff.extend([[c,ca,b],[ca,a,b]])
   else:
    if ca is None:ff.extend([[a,ab,c],[ab,bc,c],[ab,b,bc]])
    elif ab is None:ff.extend([[b,bc,a],[bc,ca,a],[bc,c,ca]])
    else:ff.extend([[c,ca,b],[ca,ab,b],[ca,a,ab]])
  faces=ff
 raise ValueError('refine iterations exceeded')
def volume_from_domain(domain,height,bottom,maxlen=.8):
 allv=[];allf=[];topcnt=0
 for poly in polys(domain):
  p=orient(poly,1);rings=[list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in p.interiors];v=np.array([q for r in rings for q in r]);f=mapbox_earcut.triangulate_float64(v,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3)
  v,f=refine(v,f,maxlen);t=v[f];neg=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])<0;f[neg]=f[neg][:,::-1];N=len(v);vt=np.c_[v,[height(*q) for q in v]];vb=np.c_[v,np.full(N,bottom)];edges={}
  for tri in f:
   for a,b in zip(tri,np.roll(tri,-1)):
    k=tuple(sorted([int(a),int(b)]));edges.setdefault(k,[]).append((int(a),int(b)))
  ff=f.tolist()+(f[:,::-1]+N).tolist()
  for ed in edges.values():
   if len(ed)==1:
    a,b=ed[0];ff.extend([[b,a,a+N],[b,a+N,b+N]])
   else:assert len(ed)==2
  off=len(allv);allv.extend(vt.tolist()+vb.tolist());allf.extend((np.array(ff)+off).tolist());topcnt+=len(f)
 return {'type':'polyhedron','vertices':allv,'faces':allf},topcnt

# Keep the existing approach road, ramp, tile court and tree opening exact.
earthnames=[n for n in E if n.startswith('SITE_V12_REBUILT_EARTH')]
oldsoil=unary_union([footprint(n) for n in earthnames]).buffer(0)
wall0=np.array(json.loads((D/'SITE_PERIMETER_JOINED_RETAINING_WALL_0_centerline.json').read_text(encoding='utf8')))
wall1=np.array(json.loads((D/'SITE_PERIMETER_JOINED_RETAINING_WALL_1_centerline.json').read_text(encoding='utf8')))
interior=Polygon(np.vstack([wall0[:,:2],wall1[:,:2]])).buffer(0).buffer(-.155,join_style=2)
store=Polygon([[13.3,-9.4],[18.9,-9.7],[20.95,-10.35],[21.45,-13],[21.3,-15.4],[20.2,-16.2],[18.9,-16.2],[13.3,-16.2]])
target=interior.union(store).buffer(0);toe_band=interior.difference(interior.buffer(-.6,join_style=2))
hardnames=[n for n in E if n.startswith(('SITE_V12_REBUILT_COURT','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','SITE_V12_OUTER_GATE_SCORED'))]
hard=[(footprint(n),tops(n)) for n in hardnames];hardunion=unary_union([g for g,t in hard]).buffer(0)
treehole=Point(-4,-13.5).buffer(.4,quad_segs=12)
domain=oldsoil.union(toe_band).intersection(target).difference(hardunion).difference(treehole).buffer(0).simplify(1e-7,preserve_topology=True)
boundary=hardunion.boundary
def surface_z(x,y,ts):
 q=ts[(ts[:,:,:2].min(1)<=[x+1e-7,y+1e-7]).all(1)&(ts[:,:,:2].max(1)>=[x-1e-7,y-1e-7]).all(1)]
 if not len(q):return None
 a=q[:,0,:2];u=q[:,1,:2]-a;v=q[:,2,:2]-a;w=np.array([x,y])-a;de=u[:,0]*v[:,1]-u[:,1]*v[:,0];aa=(w[:,0]*v[:,1]-w[:,1]*v[:,0])/de;bb=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/de;good=(aa>=-1e-5)&(bb>=-1e-5)&(aa+bb<=1+1e-5)
 return float(np.max(q[good,0,2]+aa[good]*(q[good,1,2]-q[good,0,2])+bb[good]*(q[good,2,2]-q[good,0,2]))) if good.any() else None
def height(x,y):
 base=-.48+.004*min(x,0);p=Point(x,y);dist=p.distance(boundary)
 if dist>=3.0:return base
 q=nearest_points(p,boundary)[1];zs=[]
 for poly,ts in hard:
  if poly.boundary.distance(q)<1e-5:
   z=surface_z(q.x,q.y,ts)
   if z is not None:zs.append(z)
 if not zs:return base
 s=min(1,dist/3);w=1-3*s*s+2*s*s*s
 return base*(1-w)+(max(zs)-.004)*w
g,nt=volume_from_domain(domain,height,-4.80,.70)
Q['remove'].extend(earthnames)
put('SITE_V16_GRADED_INTERIOR_SOIL',g,'M_V12_Terrain_Earth',True,classification='CONTINUOUS_GRADED_SOIL_TO_INSIDE_WALL_FACE',v16_note='Smooth interior grade; 3 m soft transition to unchanged ramp and path; base -4.80 is hidden visualization closure, not surveyed footing; no exterior scan flattening')
QA['soil']={'removed_old_patches':earthnames,'old_footprint_area_m2':oldsoil.area,'new_footprint_area_m2':domain.area,'top_triangles':nt,'base_height_m':-.48,'main_plane_grade':.004,'hard_overlap_m2':domain.intersection(hardunion).area,'tree_pit_overlap_m2':domain.intersection(treehole).area,'height_minmax_m':[min(q[2] for q in g['vertices'][:len(g['vertices'])//2]),max(q[2] for q in g['vertices'])]}
(D/'Soil_Domain.json').write_text(json.dumps(shapely.geometry.mapping(domain)),encoding='utf8')
print('SOIL BUILT',len(g['vertices']),len(g['faces']),domain.area,flush=True)

# Wall-to-road transition: narrow open gutter, road shoulder and overlapping buried toe.
profiles=json.loads((D/'Drain_Profiles.json').read_text(encoding='utf8'));chains=[]
c0=profiles[0]['profile'][0];c1=profiles[1]['profile'][-1];n0=np.array(c0['offset']);n1=np.array(c1['offset']);corner=(n0+n1)/2;corner/=np.dot(corner,n0);c0['offset']=c1['offset']=corner.tolist();c0['base']=c1['base']=max(c0['base'],c1['base'])
for chain in profiles:
 for r in chain['profile']:
  no=np.array(r['offset']);length=np.linalg.norm(no)
  if length>2:r['offset']=(no*2/length).tolist()
for chain in profiles:
 pp=chain['profile'];xy=np.array([r['xy'] for r in pp]);z=np.array([r['road_z'] if r['road_z'] is not None else np.nan for r in pp]);st=np.r_[0,np.cumsum(np.linalg.norm(np.diff(xy,axis=0),axis=1))];z=np.interp(st,st[np.isfinite(z)],z[np.isfinite(z)])
 z[1:-1]=(z[:-2]+2*z[1:-1]+z[2:])/4
 # Two wall chains share the north-west corner. Use the same road level there.
 if chain['chain']==0:z[0]=-.70
 else:z[-1]=-.70
 group=[]
 for j in range(len(pp)-1):
  # Original retaining route is buried within the outer store here; its exterior is the photo-fitted polygonal plinth.
  mid=(xy[j]+xy[j+1])/2
  if chain['chain']==0 and mid[0]>13.0 and mid[1]<-9.25:
   if group:chains.append(group);group=[]
   continue
  if not group:group.append({'xy':xy[j].tolist(),'base':pp[j]['base'],'z':float(z[j]),'offset':pp[j]['offset']})
  group.append({'xy':xy[j+1].tolist(),'base':pp[j+1]['base'],'z':float(z[j+1]),'offset':pp[j+1]['offset']})
 if group:chains.append(group)
# Outer store's outermost five stone wall faces, reversed for the same outward-left convention.
storeline=np.array([[18.9,-9.7],[20.95,-10.35],[21.45,-13],[21.3,-15.4],[20.2,-16.2],[18.9,-16.2]])
# Query the retained exterior triangles for road-level control along this plinth.
extt=[]
for n in E:
 if n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):
  d=load(n);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);extt.extend(t[abs(no[:,2])>.7*np.linalg.norm(no,axis=1)])
extt=np.array(extt);u=np.diff(storeline,axis=0);u/=np.linalg.norm(u,axis=1)[:,None];nn=np.c_[-u[:,1],u[:,0]];sp=[]
for j,p in enumerate(storeline):
 n=nn[0] if j==0 else nn[-1] if j==len(storeline)-1 else (nn[j-1]+nn[j])/2
 if 0<j<len(storeline)-1:n/=np.dot(n,nn[j])
 q=p+n*1.05;zz=surface_z(*q,extt);zz=-4.0 if zz is None or zz>-.9 else zz
 sp.append({'xy':p.tolist(),'base':-1.9,'z':zz,'offset':n.tolist()})
chains.append(sp)
# Each segment uses a planar outer edge. Cut scan vertices use this exact same plane.
segments=[];drainparts=[];toeparts=[];masks=[];station_records=[]
for ci,chain in enumerate(chains):
 for j in range(len(chain)-1):
  a,b=chain[j],chain[j+1];pa=np.array(a['xy']);pb=np.array(b['xy']);oa=np.array(a['offset']);ob=np.array(b['offset']);L=float(np.linalg.norm(pb-pa));N=max(1,int(math.ceil(L/.45)))
  roadzone=bool(ci==len(chains)-1 or ((pa+pb)/2)[1]>5 or ((pa+pb)/2)[1]<-12 or ((pa+pb)/2)[0]<-14)
  outer_a=pa+oa*1.05;outer_b=pb+ob*1.05
  seg={'a':pa.tolist(),'b':pb.tolist(),'outer_a':outer_a.tolist(),'outer_b':outer_b.tolist(),'za':a['z'],'zb':b['z'],'ci':ci,'j':j,'roadzone':roadzone};segments.append(seg)
  masks.append(Polygon([pa+oa*.11,pb+ob*.11,outer_b,outer_a]).buffer(0))
  for k in range(N):
   s0=k/N;s1=(k+1)/N;ends=[]
   for t0 in [s0,s1]:ends.append((pa+(pb-pa)*t0,oa+(ob-oa)*t0,a['z']+(b['z']-a['z'])*t0,a['base']+(b['base']-a['base'])*t0))
   if roadzone:cross=[(.15,-.02),(.18,-.02),(.18,-.18),(.43,-.18),(.43,-.02),(.54,-.02),(1.05,0),(1.05,-.50),(.15,-.50)]
   else:cross=[(.15,-.015),(1.05,0),(1.05,-.5),(.15,-.5)]
   verts=[]
   for pp,off,zz,base in ends:verts.extend([[*(pp+off*d),zz+dz] for d,dz in cross])
   cnt=len(cross);faces=[list(range(cnt-1,-1,-1)),list(range(cnt,2*cnt))]+[[i,(i+1)%cnt,(i+1)%cnt+cnt,i+cnt] for i in range(cnt)]
   drainparts.append({'type':'polyhedron','vertices':verts,'faces':faces})
   tv=[]
   for pp,off,zz,base in ends:tv.extend([[*(pp+off*d),z] for d,z in [(-.14,base+.06),(.175,base+.06),(.175,min(base,zz)-.53),(-.14,min(base,zz)-.53)]])
   toeparts.append({'type':'polyhedron','vertices':tv,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]})
   station_records.append({'chain':ci,'segment':j,'wall_base':ends[0][3],'road_z':ends[0][2],'gutter_bottom':ends[0][2]-.18 if roadzone else None,'toe_lower':min(ends[0][3],ends[0][2])-.53})
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
def combine(parts):
 vv=[];ff=[]
 for g in parts:
  g=oriented(g);off=len(vv);vv.extend(g['vertices']);ff.extend((np.array(triangles(np.array(g['vertices']),g['faces']))+off).tolist())
 return {'type':'polyhedron','vertices':vv,'faces':ff}
# Boolean union removes touching station caps, giving real shared gutter and toe solids.
import manifold3d as mf
dg=fromman(mf.Manifold.batch_boolean([manifold(g) for g in drainparts],mf.OpType.Add));tg=fromman(mf.Manifold.batch_boolean([manifold(g) for g in toeparts],mf.OpType.Add))
put('SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE',dg,'M_V16_Drain_Concrete',True,classification='CONTINUOUS_OPEN_GUTTER_WITH_ROAD_TIE',v16_note='0.25 m modeled clear trough, 0.16 m relative drop; photo fitted, not a hydraulic sizing calculation')
put('SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE',tg,'M_Stone_Rubble',True,classification='STONE_TOE_SEALS_WALL_TO_GUTTER',v16_note='Toe overlaps existing wall bottom by 60 mm and extends below the channel; no through gap')
mask=unary_union(masks).buffer(0);(D/'Drain_Mask.json').write_text(json.dumps(shapely.geometry.mapping(mask)),encoding='utf8');(D/'Drain_Segments.json').write_text(json.dumps(segments,indent=2),encoding='utf8')
print('DRAIN BUILT',len(segments),len(dg['faces']),len(tg['faces']),mask.area,flush=True)

# Trim only the local wall/drain band of the retained photo mesh. Match all cut road vertices to the modeled edge.
outer=np.array([[r['outer_a'],r['outer_b']] for r in segments]);oa=outer[:,0];od=outer[:,1]-oa;oll=(od*od).sum(1);zab=np.array([[r['za'],r['zb']] for r in segments])
def edge_contact(p,z):
 q=np.array(p);s=np.clip(((q-oa)*od).sum(1)/oll,0,1);near=oa+od*s[:,None];dist=np.linalg.norm(near-q,axis=1);i=int(np.argmin(dist));road=zab[i,0]+s[i]*(zab[i,1]-zab[i,0]);dd=dist[i]
 if dd<.35 and abs(z-road)<.7:
  h=min(1,dd/.35);blend=1-3*h*h+2*h*h*h;return float(z*(1-blend)+road*blend)
 return float(z)
source_checks=[]
maskbuff=mask.buffer(.001)
scan_cut=mask.union(interior).buffer(0)
scan_cutbuff=scan_cut.buffer(.001)
for n in list(E):
 if not n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 d=load(n);v=d['vertices'];f=d['faces'];uv=d['uv'];nv=[];nuv=[];nf=[];cutcnt=0;dropped=0;changed=0;dedup={}
 def append_tri(q,quv):
  nonlocal_dummy=None;ids=[]
  for p,pu in zip(q,quv):
   key=tuple(np.round(np.r_[p,pu],9))
   if key not in dedup:dedup[key]=len(nv);nv.append(p.tolist());nuv.append(pu.tolist())
   ids.append(dedup[key])
  if len(set(ids))==3 and np.linalg.norm(np.cross(np.array(nv[ids[1]])-nv[ids[0]],np.array(nv[ids[2]])-nv[ids[0]]))>1e-12:nf.append(ids)
 for inds in f:
  q=v[inds];quv=uv[inds];poly=Polygon(q[:,:2]);normal=np.cross(q[1]-q[0],q[2]-q[0])
  if poly.area<1e-11:
   if scan_cutbuff.intersects(LineString(q[:,:2])):dropped+=1;continue
   append_tri(q,quv);continue
  if not scan_cut.intersects(poly):
   qq=q.copy()
   if abs(normal[2])>.6*np.linalg.norm(normal):
    for p in qq:p[2]=edge_contact(p[:2],p[2])
   changed+=int(abs(qq[:,2]-q[:,2]).max()>1e-7);append_tri(qq,quv);continue
  rem=poly.difference(scan_cut);cutcnt+=1
  if rem.is_empty:dropped+=1;continue
  A=q[0,:2];du=q[1,:2]-A;dv=q[2,:2]-A;de=du[0]*dv[1]-du[1]*dv[0]
  for pp in polys(rem):
   rings=[list(pp.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in pp.interiors];p2=np.array([p for r in rings for p in r]);ts=mapbox_earcut.triangulate_float64(p2,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3);w=p2-A;aa=(w[:,0]*dv[1]-w[:,1]*dv[0])/de;bb=(du[0]*w[:,1]-du[1]*w[:,0])/de;weights=np.c_[1-aa-bb,aa,bb];q3=weights@q;u3=weights@quv
   if abs(normal[2])>.6*np.linalg.norm(normal):
    for p in q3:p[2]=edge_contact(p[:2],p[2])
   for inds2 in ts:
    qs=q3[inds2];us=u3[inds2]
    if np.dot(np.cross(qs[1]-qs[0],qs[2]-qs[0]),normal)<0:qs=qs[::-1];us=us[::-1]
    append_tri(qs,us)
 vv=np.array(nv);ff=np.array(nf,np.int32);uu=np.array(nuv);fn='SOURCE_'+n+'.npz';np.savez_compressed(D/fn,vertices=vv,faces=ff,uv=uu,material_ids=np.zeros(len(ff),np.int32));Q['replace'].append({**{k:v for k,v in E[n].items() if k!='parts'},'v16_scan_trim':'Local drain band trimmed; road boundary snapped to matching modeled edge with 350 mm shoulder blend; remainder uses original UV','native_source_file':fn,'parts':[]});source_checks.append({'name':n,'original_triangles':len(f),'new_triangles':len(ff),'cut_faces':cutcnt,'removed_faces':dropped,'shoulder_adjusted_faces':changed,'vertices':len(vv)});print('SOURCE TRIM',n,source_checks[-1],flush=True)
QA['drain']={'station_count':len(station_records),'segment_count':len(segments),'mask_area_m2':mask.area,'trough_width_m':.25,'trough_drop_m':.16,'edge_match_rule':'Source cut road z equals exact same outer segment affine plane; 350 mm transition to unchanged original scan','source_changes':source_checks,'stations':station_records}
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Geometry_QA.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8');print('V16 GEOMETRY READY',len(Q['replace']),len(Q['add']),len(Q['remove']),flush=True)
