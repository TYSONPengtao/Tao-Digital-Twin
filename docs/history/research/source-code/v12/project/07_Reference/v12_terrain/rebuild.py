# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,json,math,hashlib,collections
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,mapbox_earcut,rhino3dm as rh
from shapely.geometry import Polygon,box,mapping
from scipy.spatial import cKDTree
from scipy.ndimage import binary_closing,binary_fill_holes
O=Path(__file__).parent;V=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');O.joinpath('data').mkdir(exist_ok=True)
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
R=np.array(json.loads((V/'02_Data/Coordinate.json').read_text())['local_to_survey'])[:3,:3];origin=np.array([-3.45191261,-3.90043098,TAO_PRIVATE_SITE_002])
s=np.load(O/'Ground_Samples_Raw.npz')['samples'];raw=s[:,:3];kdt=cKDTree(raw[:,:2]);keep=[];envelope=[]
# Progressive lower-envelope test suppresses roofs, canopies and floating tree/scan islands.
# 35 percent grade allowance retains slopes; absolute terrain heights are not forced to one plane.
for j,q in enumerate(raw):
 ids=kdt.query_ball_point(q[:2],9.0);d=np.linalg.norm(raw[ids,:2]-q[:2],axis=1);lim=np.min(raw[ids,2]+.35*d+.35);envelope.append(lim);keep.append(q[2]<=lim+.4)
keep=np.array(keep);ground=raw[keep];tree=cKDTree(ground[:,:2]);
# Fine, low and locally screened west-earth samples inherited as height evidence only.
west=np.load(W/'v8_terrain_clear/data/V8_Measured_Ground_Support.npz')['points'];support=np.vstack([ground,west]);
# Use established -0.45 courtyard grade, matching entrance step foot and pavilion foundation.
# Boundary and terrain remain non-planar outside this paved court.
COURT=Polygon([[-.12,1.9],[14.08,1.9],[14.08,-3.30],[13.6,-14.5],[5.0,-14.5],[4.9,-11.7],[-.12,-11.7]])
BUILDING=box(-.12,-.02,13.12,11.20)
ga=np.array([-14.78814941727704,-8.672411229164949]);gb=np.array([-12.691036702414301,-12.516460251600984]);gd=gb-ga;gw=np.linalg.norm(gd);gd/=gw;gin=np.array([-gd[1],gd[0]])
RAMP=Polygon([ga-gin*2,gb-gin*2,gb,gb+gin*.90,ga+gin*.90,ga])
APRON=Polygon([ga-gd*.70-gin*3.2,gb+gd*.70-gin*3.2,gb+gd*.70+gin*1.6,ga-gd*.70+gin*1.6])
xs=np.arange(0,14.1,.8);ys=np.arange(-14.4,2.0,.8);cp=np.array([[x,y,-.45] for x in xs for y in ys if COURT.contains(shapely.Point(x,y))]);support=np.vstack([support,cp]);kd=cKDTree(support[:,:2])

def base_zfield(q):
 q=np.asarray(q);dist,idx=kd.query(q,k=10);w=1/np.maximum(dist,.12)**2;z=(w*support[idx,2]).sum(1)/w.sum(1)
 in_c=shapely.contains_xy(COURT.union(BUILDING).buffer(1e-6),q[:,0],q[:,1]);z[in_c]=-.45
 return z
ramproad=base_zfield(np.array([ga-gin*2,gb-gin*2]));rampinside=base_zfield(np.array([ga+gin*.90,gb+gin*.90]));rampgate=np.array([-.8217466039139902,-1.1182533960860097])-.035
def ramp_z(q):
 q=np.asarray(q);uv=np.c_[(q-ga)@gd,(q-ga)@gin];t=np.clip(uv[:,0]/gw,0,1);v=uv[:,1];zg=rampgate[0]*(1-t)+rampgate[1]*t;zr=ramproad[0]*(1-t)+ramproad[1]*t;zi=rampinside[0]*(1-t)+rampinside[1]*t
 return np.where(v<0,zg+(zr-zg)*np.clip(-v/2,0,1),zg+(zi-zg)*np.clip(v/.90,0,1))
def zfield(q):
 q=np.asarray(q);z=base_zfield(q);ins=shapely.contains_xy(APRON.buffer(1e-6),q[:,0],q[:,1]);pq=q[ins]
 if len(pq):
  uv=np.c_[(pq-ga)@gd,(pq-ga)@gin];cu=np.clip(uv[:,0],0,gw);cv=np.clip(uv[:,1],-2,.90);nearest=ga+cu[:,None]*gd+cv[:,None]*gin;rz=ramp_z(nearest)
  blend=np.maximum(np.abs(uv[:,0]-cu)/.70,np.where(uv[:,1]<-2,(-2-uv[:,1])/1.2,np.where(uv[:,1]>.9,(uv[:,1]-.9)/.7,0)));blend=np.clip(blend,0,1)
  z[ins]=rz*(1-blend)+z[ins]*blend
 return z
# Domain derives from original source ground sample plan, filled across the explicitly cut central site.
# Regularized outer line, no invented rectangular enclosing terrain.
cells=[box(x-.5,y-.5,x+.5,y+.5) for x,y,z,n in s];domain=shapely.union_all(cells).buffer(1.05).buffer(-1.05)
Hj=json.loads((V/'02_Data/Hole_Polygon.json').read_text());H=Polygon(Hj['local']['outer'],Hj['local']['holes']);domain=domain.union(H.buffer(.2)).buffer(0)
# Fill internal old scan cavities; external context surface reconstruction has no open projection holes.
ps=[domain] if domain.geom_type=='Polygon' else list(domain.geoms);domain=shapely.union_all([Polygon(p.exterior).simplify(.35,preserve_topology=True) for p in ps if p.area>10]).buffer(0)
# Read original road plan as outline reference only, rebuild grade/mesh independently.
S=json.loads((V/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
import export_v5 as ex;ex.SCENE=S
road=None
for e in S['elements']:
 if e['name']=='SITE_CURVED_PUBLIC_ROAD':
  v,f=ex.world_part(e['parts'][0],e);tr=[]
  for ff in f:
   if len(ff)==3:tr.append(v[ff,:2])
   elif len(ff)==4:tr.extend([v[np.array(ff)[[0,1,2]],:2],v[np.array(ff)[[0,2,3]],:2]])
  tr=np.array(tr);ar=abs(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]));road=shapely.union_all(shapely.polygons(tr[ar>1e-9])).buffer(0);break
road=road.union(APRON).intersection(domain).difference(COURT.buffer(.01)).difference(RAMP)
# Narrow sub-centimetre road-outline islands are plan triangulation artifacts,
# rebuilt as continuous concrete rather than orphaned soil triangles.
road=shapely.union_all([Polygon(pp.exterior,[rr for rr in pp.interiors if Polygon(rr).area>=.01]) for pp in ([road] if road.geom_type=='Polygon' else list(road.geoms))]);main=COURT.intersection(domain).difference(RAMP);earth=domain.difference(road.union(main).union(RAMP)).buffer(0)
# Canonical boundary stations are shared across every zone. GEOS/Earcut may otherwise
# drop collinear outline points on only one side, causing different Z interpolation.
boundary_nodes=[]
for boundary_geom in [road,main,earth,RAMP]:
 for pp in ([boundary_geom] if boundary_geom.geom_type=='Polygon' else list(boundary_geom.geoms)):
  boundary_nodes.extend(list(pp.exterior.coords)[:-1])
  for rr in pp.interiors:boundary_nodes.extend(list(rr.coords)[:-1])
boundary_nodes=np.unique(np.round(boundary_nodes,7),axis=0);boundary_tree=cKDTree(boundary_nodes)
def nodal_ring(raw):
 raw=np.asarray(raw);out=[]
 for a,b in zip(raw,np.roll(raw,-1,axis=0)):
  dd=b-a;ll=np.dot(dd,dd);out.append(a)
  if ll<1e-18:continue
  ids=boundary_tree.query_ball_point((a+b)/2,math.sqrt(ll)/2+3e-7);candidate=boundary_nodes[ids];tt=(candidate-a)@dd/ll;cross=np.abs((candidate[:,0]-a[0])*dd[1]-(candidate[:,1]-a[1])*dd[0])/math.sqrt(ll);keep=(tt>1e-8)&(tt<1-1e-8)&(cross<2e-7)
  for q in candidate[keep][np.argsort(tt[keep])]:out.append(q)
 clean=[]
 for q in np.round(out,7):
  if not clean or np.linalg.norm(q-clean[-1])>1e-8:clean.append(q)
 if len(clean)>1 and np.linalg.norm(clean[0]-clean[-1])<1e-8:clean.pop()
 return np.array(clean)
# New regular 0.75m survey-derived terrain stations. Court 0.5m grid with geometric joint strips later.
# Each zone is split into 20m native mesh panels, not source photogrammetry triangles.
parts=[];rows=[];native=rh.File3dm();native.Settings.ModelUnitSystem=rh.UnitSystem.Meters
colors={'M_V12_Terrain_Earth':(113,105,78),'M_V12_Road_Concrete':(137,139,132),'M_V12_Court_Stone':(91,91,81)};midx={}
for n,c in colors.items():
 m=rh.Material();m.Name=n;m.DiffuseColor=__import__('System').Drawing.Color.FromArgb(*c) if False else (c[0],c[1],c[2],255);midx[n]=native.Materials.Add(m)
for n in ['60_SITE_REBUILT_TERRAIN','60_SITE_GATE_RAMP','60_SITE_ENTRY_STEPS']:
 l=rh.Layer();l.Name=n;native.Layers.Add(l)

def polys(p):
 if p.is_empty:return []
 if p.geom_type=='Polygon':return [p]
 return [g for g in p.geoms if g.geom_type=='Polygon'] if hasattr(p,'geoms') else []

def closed_piece(p,step):
 # Cell-clipped top triangles are welded with integer rounding then closed by a parallel bottom.
 vs=[];fs=[];lookup={}
 def idx(q):
  key=tuple(np.round(q,7));
  if key not in lookup:lookup[key]=len(vs);vs.append(list(key))
  return lookup[key]
 bounds=p.bounds
 for x in np.arange(math.floor(bounds[0]/step)*step,bounds[2]+1e-8,step):
  for y in np.arange(math.floor(bounds[1]/step)*step,bounds[3]+1e-8,step):
   for pp in polys(p.intersection(box(x,y,x+step,y+step))):
    if pp.area<1e-9:continue
    rings=[nodal_ring(pp.exterior.coords[:-1])]+[nodal_ring(r.coords[:-1]) for r in pp.interiors]
    noded=Polygon(rings[0],rings[1:])
    if not noded.is_valid:noded=noded.buffer(0)
    # GEOS constrained Delaunay retains each collinear boundary station as a
    # constrained edge; Earcut's dropped nodes previously created height seams.
    for poly in polys(noded):
     for tri in shapely.constrained_delaunay_triangles(poly).geoms:
      xy=np.array(tri.exterior.coords[:-1]);q=np.c_[xy,zfield(xy)]
      if np.cross(q[1,:2]-q[0,:2],q[2,:2]-q[0,:2])<0:q=q[::-1]
      ids=[idx(pt) for pt in q]
      if len(set(ids))==3:fs.append(ids)
 v=np.array(vs);N=len(v);bottom=v.copy();bottom[:,2]-=.20;faces=list(fs)+[[i+N for i in f[::-1]] for f in fs];edges=collections.Counter(tuple(sorted((a,b))) for f in fs for a,b in zip(f,f[1:]+f[:1]));oriented={tuple(sorted((a,b))):(a,b) for f in fs for a,b in zip(f,f[1:]+f[:1])};
 for ee,c in edges.items():
  if c==1:
   a,b=oriented[ee];faces.append([b,a,a+N,b+N])
 if any(c>2 for c in edges.values()):
  dump(O/'Debug_Nonmanifold.json',{'vertices':vs,'faces':fs,'bad_edges':[{ 'edge':list(e),'count':c,'faces':[ff for ff in fs if e[0] in ff and e[1] in ff]} for e,c in edges.items() if c>2]});raise ValueError('nonmanifold top')
 g={'type':'polyhedron','vertices':np.vstack([v,bottom]).tolist(),'faces':faces};m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for q in g['vertices']:m.Vertices.AddPoint3d(*q)
 for f in faces:m.Faces.AddFace(*f)
 m.Normals.ComputeNormals();m.Compact()
 return g,m

for zone,poly,mat,step in [('COURT',main,'M_V12_Court_Stone',.5),('ROAD',road,'M_V12_Road_Concrete',1.0),('EARTH',earth,'M_V12_Terrain_Earth',1.0)]:
 b=poly.bounds
 for x in np.arange(math.floor(b[0]/20)*20,b[2],20):
  for y in np.arange(math.floor(b[1]/20)*20,b[3],20):
   pp=poly.intersection(box(x,y,x+20,y+20)).buffer(0)
   for j,p in enumerate(polys(pp)):
    if p.area<1e-9:continue
    g,m=closed_piece(p,step);name=f'SITE_V12_REBUILT_{zone}_{int(x)}_{int(y)}_{j}'
    if not m.IsClosed:print('OPEN',name,flush=True)
    at=rh.ObjectAttributes();at.Name=name;at.LayerIndex=0;at.MaterialIndex=midx[mat];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.SetUserString('source','Regular resampled lower terrain height envelope; no original photo triangles');native.Objects.AddMesh(m,at)
    e={'name':name,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','source':'E:/jz/纯场地版本.3dm lower-envelope ground heights; V8 screened west ground support; V11 inherited courtyard grade','classification':'MANUALLY_RECONSTRUCTED_TERRAIN; NEW_REGULAR_GRID; NOT_SOURCE_PHOTOGRAMMETRY','parts':[{'geometry':g,'material':mat}],'terrain_zone':zone,'projection_area_m2':p.area,'metric_status':'REFERENCE_HEIGHTS; NOT_FIELD_CONTROLLED'};parts.append(e);rows.append({'name':name,'valid':m.IsValid,'closed':m.IsClosed,'vertices':len(m.Vertices),'faces':len(m.Faces),'area_m2':p.area,'top_z_min':min(q[2] for q in g['vertices'][:len(g['vertices'])//2]),'top_z_max':max(q[2] for q in g['vertices'][:len(g['vertices'])//2]),'grid_m':step})
    print(name,len(m.Faces),m.IsValid,m.IsClosed,flush=True)
# The outer gate's independently modeled, scored concrete transition ramp.
# Corners inherit source ground; the gate line is 35mm below the four closed leaf bottom pivots.
us=np.linspace(0,gw,16);grooves=np.arange(-1.85,.85,.3);vv=sorted(set([-2.0,0.0,.9]+[round(float(t),7) for c in grooves for t in [c-.008,c,c+.008] if -2<t<.9]));v=[];f=[]
for u in us:
 for t in vv:
  xy=ga+gd*u+gin*t;zz=float(ramp_z([xy])[0]);zz-=.004*min(1,u/.2,(gw-u)/.2) if min(abs(t-grooves))<1e-6 else 0;v.append([*xy,zz])
nu=len(us);nv=len(vv)
for i in range(nu-1):
 for j in range(nv-1):
  a=i*nv+j;b=(i+1)*nv+j;f.extend([[a,b,b+1],[a,b+1,a+1]])
v=np.array(v);N=len(v);bot=v.copy();bot[:,2]-=.20;faces=list(f)+[[a+N for a in ff[::-1]] for ff in f];ec=collections.Counter(tuple(sorted((a,b))) for ff in f for a,b in zip(ff,ff[1:]+ff[:1]));oe={tuple(sorted((a,b))):(a,b) for ff in f for a,b in zip(ff,ff[1:]+ff[:1])}
for edge,n in ec.items():
 if n==1:
  a,b=oe[edge];faces.append([b,a,a+N,b+N])
g={'type':'polyhedron','vertices':np.vstack([v,bot]).tolist(),'faces':faces};mesh=rh.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True
for q in g['vertices']:mesh.Vertices.AddPoint3d(*q)
for ff in faces:mesh.Faces.AddFace(*ff)
mesh.Normals.ComputeNormals();mesh.Compact();name='SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP';at=rh.ObjectAttributes();at.Name=name;at.LayerIndex=1;at.MaterialIndex=midx['M_V12_Road_Concrete'];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;native.Objects.AddMesh(mesh,at)
e={'name':name,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','source':'INSV Ground_L0_0775s_Y+00_P-35.jpg / Ground_L0_0897s_Y+00_P-35.jpg; original source road heights; V11 external gate pivots','classification':'MANUALLY_MODELED_GATE_RAMP_WITH_4MM_PRESSURE_GROOVES','parts':[{'geometry':g,'material':'M_V12_Road_Concrete'}],'metric_status':'REFERENCE_METRIC_VALUES; NOT_FIELD_MEASURED'};parts.append(e);rows.append({'name':name,'valid':mesh.IsValid,'closed':mesh.IsClosed,'vertices':len(mesh.Vertices),'faces':len(mesh.Faces),'area_m2':RAMP.area,'top_z_min':float(v[:,2].min()),'top_z_max':float(v[:,2].max()),'grid_m':.3,'gate_ground_Z_line_m':rampgate.tolist(),'road_edge_Z_corners_m':ramproad.tolist(),'yard_edge_Z_corners_m':rampinside.tolist(),'closed_leaf_clearance_m':.035,'groove_depth_m':.004})
assert native.Write(str(O/'Rebuilt_Terrain_LOCAL.3dm'),8)
# Clean reference-only original ground pieces keep exact coordinates and UV; all high scan skin discarded.
F=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');reference=rh.File3dm();reference.Settings.ModelUnitSystem=rh.UnitSystem.Meters
for mat in F.Materials:reference.Materials.Add(mat)
l=rh.Layer();l.Name='00_REFERENCE_CLEANED_GROUND_ONLY';reference.Layers.Add(l);refcounts=[]
for i,obj in enumerate(F.Objects):
 d=np.load(O/f'source_{i}.npz');v=d['local'];f=d['faces'];t=v[f[:,:3]];c=t.mean(1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nz=abs(n[:,2])/(np.linalg.norm(n,axis=1)+1e-30);z=zfield(c[:,:2]);sel=(nz>.35)&(np.ptp(t[:,:,2],axis=1)<.85)&(c[:,2]<=z+.28)&(c[:,2]>=z-.45)
 used=np.unique(f[sel]);remap=np.full(len(v),-1,np.int32);remap[used]=np.arange(len(used));m=rh.Mesh()
 for q in d['vertices'][used]:m.Vertices.AddPoint3d(*q)
 for q in f[sel]:
  qq=remap[q];m.Faces.AddFace(*qq[:3] if qq[2]==qq[3] else qq)
 for q in d['uv'][used]:m.TextureCoordinates.__add__(*q)
 m.Normals.ComputeNormals();m.Compact();at=rh.ObjectAttributes();at.Name=f'REFERENCE_ONLY_VALID_GROUND_{i}';at.LayerIndex=0;at.MaterialIndex=obj.Attributes.MaterialIndex;at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;reference.Objects.AddMesh(m,at);refcounts.append({'source_mesh':i,'input_faces':len(f),'retained_ground_faces':int(sel.sum()),'removed_high_vertical_or_disconnected_skin_faces':int((~sel).sum()),'source_xyz_uv_exact':True});print('reference',i,int(sel.sum()),flush=True)
assert reference.Write(str(O/'Pure_Site_Cleaned_Ground_Reference_ENU.3dm'),8)
np.savez_compressed(O/'Terrain_Support.npz',points=support,raw_samples=raw,accepted_ground_mask=keep,lower_envelope=np.array(envelope))
dump(O/'Terrain_Domain.json',{'domain':mapping(domain),'courtyard':mapping(main),'road':mapping(road),'earth':mapping(earth),'coordinate':'LOCAL; ENU transform same V11'})
remove=[e['name'] for e in S['elements'] if e['name'] in ['SITE_MAIN_COURTYARD_PAVING','SITE_WEST_EARTH_COURTYARD','SITE_CURVED_PUBLIC_ROAD','SITE_CONTEXT_TERRAIN','SITE_EAST_GARDEN','SITE_V11_LOCAL_EXPOSED_PAVILION_GROUND_GAPS']]
mutation={'replace':[],'add':parts,'remove':remove,'definitions':{},'materials':{n:{'color':list(c),'roughness':.93,'source':'Reference natural soil / worn concrete / courtyard stone; reconstructed without baked photogrammetry floating texture'} for n,c in colors.items()},'changes':['Rebuild source extent terrain as closed regular-grid panels, remove all source scan floaters from primary architecture version; valid scan ground isolated in reference-only companion.','Preserve non-planar terrain profile and courtyard datum; video confirms main steps, kitchen raised threshold and exterior textured ramp.']}
mutation['construction_control']=[{'names':[p['name'] for p in parts],'description':'全场分区人工地形及带压槽入口坡坪。入口准确 XYZ 驱动道路过渡，共享约束边界节点保留；主楼/厨房/亭子标高及三级台阶保持，门扇几何不变。纯场地原摄影地面仅在独立参考文件。','evidence':['E:/jz/纯场地版本.3dm']+['E:/jz/JIA/Rebuild_V12/07_Reference/Panorama/'+n for n in ['Ground_L0_0600s_Y+00_P-35.jpg','Ground_L0_0650s_Y+00_P-35.jpg','Ground_L0_0775s_Y+00_P-35.jpg','Ground_L0_0897s_Y+00_P-35.jpg']],'metric_status':'REFERENCE_HEIGHTS_AND_FORM; NOT_NEW_SURVEY_OR_APPROVED_CONSTRUCTION_DESIGN'}];mutation['changes'].extend(['Road apron shares exact ramp perimeter height, continuous front and both sides; native constrained triangulation preserves every shared zone boundary station.','Sub-centimetre plan islands within road outline rebuilt as continuous concrete; all native terrain companion meshes use double-precision vertices.']);dump(O/'Mutation.json',mutation);qa={'status':'PASS' if all(r['valid'] and r['closed'] for r in rows) else 'FAIL','source_sha256':sha(Path(r'E:\jz\纯场地版本.3dm')),'source_objects':5,'source_unit':'m','source_frame':'ENU','reconstructed_grid_parts':len(parts),'source_photogrammetry_triangles_in_main':0,'retained_original_geometry_in_main':False,'original_source_modified':False,'terrain_domain_m2':domain.area,'domain_covers_original_main_void_m2_residual':H.difference(domain).area,'domain_height_m_range':[min(r['top_z_min'] for r in rows),max(r['top_z_max'] for r in rows)],'lower_terrain_support_points':len(ground),'raw_cell_points':len(raw),'suppressed_upper_roof_tree_cells':int((~keep).sum()),'main_courtyard_grade_m':-.45,'paved_court_area_m2':main.area,'road_area_m2':road.area,'terrain_parts':rows,'clean_reference_source_face_selection':refcounts,'limits':'Terrain boundary and gridded interpolation follow lower geometry envelope; elevations are inherited reference values, not independently controlled survey. Roof and tree skin removed from this ground-only reference, not from preserved original files.'};dump(O/'Geometry_QA.json',qa);print('DONE',qa['status'],len(parts),domain.area,flush=True)


