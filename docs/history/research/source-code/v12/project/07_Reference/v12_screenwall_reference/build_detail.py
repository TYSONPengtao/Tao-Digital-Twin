import sys,json,math,hashlib,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,trimesh
O=Path(__file__).parent
SRC=Path(r'E:\CODEXdata\before\照壁\照壁_三版融合_统一模型_v4.3dm')
SP=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(SP.read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
f=rh.File3dm.Read(str(SRC))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
refs=[str(SRC),r'G:\处理\0005\DJI_0086.JPG',r'G:\处理\0005\DJI_0095.JPG',r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama\Ground_L0_0749s_Y+00_P+00.jpg']
def zscreen(x,y):
 t=abs((x-7.025)/4.075);v=abs((y+16.9)/.74)
 return 3.88-.25*v**1.4+.65*t**4+.12*t**5*v**2
def rawmesh(m):
 v=np.array([[p.X,p.Y,p.Z] for p in m.Vertices])/1000
 faces=[]
 for face in m.Faces:faces.append(list(face[:4]) if len(set(face))==4 else list(face[:3]))
 return v,faces
def part(v,faces,mat='M_Roof',**meta):return dict(geometry=dict(type='polyhedron',vertices=np.asarray(v).tolist(),faces=faces),material=mat,**meta)
def element(name,parts,classification):return dict(name=name,parts=parts,layer='60_SITE',family='SITE_MODEL',classification=classification,confidence='MEDIUM',status='V12_PHOTO_RELATION_CONFIRMED_DETAIL_SIZE_PROVISIONAL',source='; '.join(refs),source_before=str(SRC),source_before_sha256=sha(SRC),source_video_sha256='3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f',dimension_status='Inherited registered V11 footprint and ridge centre; ornament sizes are before reference assumptions, pending survey')

# Explicitly retire only the two old short ridge end posts; the long rails and
# 140 original flower / rail parts remain geometrically unchanged.
old=copy.deepcopy(E['SITE_SOUTH_SCREENWALL_OPEN_RIDGE_LATTICE']);assert len(old['parts'])==144
retired=[];retained=[]
for i,p in enumerate(old['parts']):
 v=np.array(p['geometry']['vertices']);cx=v[:,0].mean()
 if (abs(cx-2.965)<1e-7 or abs(cx-11.085)<1e-7) and v[:,0].ptp()<.061 and v[:,1].ptp()<.061:
  retired.append(i+1)
 else:retained.append(p)
assert retired==[3,4]
old['parts']=retained;old.update(status='V12_TWO_SHORT_END_POSTS_REPLACED_BY_HIGH_RIDGE_FINIALS',source='; '.join(refs),source_before=str(SRC))
add=[]
finials=[]
for ob in f.Objects:
 if ob.Attributes.LayerIndex!=17:continue
 assert isinstance(ob.Geometry,rh.Mesh) and ob.Geometry.IsClosed
 v,faces=rawmesh(ob.Geometry);sign=-1 if v[:,0].mean()<0 else 1
 # Keep each source ornament's dimensions; place it at the already registered
# roof end. This copies no before wall body and never stretches the 5.052m model.
 v[:,0]+=5.42 if sign<0 else 8.63
 v[:,1]-=16.9
 v[:,2]+=zscreen(2.95,-16.9)-.075-3.3568310546875
 finials.append(part(v,faces,reference_object=ob.Attributes.Name,reference_object_id=str(ob.Attributes.Id)))
assert len(finials)==16
add.append(element('SITE_SOUTH_SCREENWALL_V12_HIGH_RIDGE_FINIALS',finials,'CHINESE_HIGH_UPRIGHT_RIDGE_TERMINALS'))

# Repeat the source lotus disk + eight petal reliefs at the actual 45 existing
# V11 cover-tile row centres, on both eaves. Do not scale the full reference.
template=[];start=False
for ob in f.Objects:
 if ob.Attributes.LayerIndex!=12:continue
 if not start:
  if ob.Attributes.Name=='花瓣筒瓦当':start=True
  else:continue
 template.append(ob)
 if len(template)==9:break
assert len(template)==9
tileE=E['SITE_SOUTH_SCREENWALL_BARREL_TILE_ROWS'];xs=sorted(set(round(np.array(p['geometry']['vertices'])[:,0].mean(),8) for p in tileE['parts']))
assert len(xs)==45
source_center=np.array([-2.040,-.524,2.942322265625]);lotus=[];drip_placement=[]
for x in xs:
 for side in [-1,1]:
  # Measure the original eave row's actual end ring. A vertical drip disk must
  # sit in front of the closed fascia while its back embeds into the tube rim.
  row=[p for p in tileE['parts'] if abs(np.array(p['geometry']['vertices'])[:,0].mean()-x)<1e-6]
  tile=row[0 if side<0 else -1];tv=np.array(tile['geometry']['vertices']);end=tv[:26] if side<0 else tv[52:78]
  base=(end[0]+end[12])/2;z=float(base[2]);y=-16.9+side*.767
  drip_placement.append(dict(x=x,eave_side=side,original_tube_axis=base.tolist(),disk_axis=[x,y,z],axis_push_m=abs(y-base[1]),front_relief_y=y+side*.0208))
  for template_index,ob in enumerate(template):
   assert ob.Geometry.IsClosed
   v,faces=rawmesh(ob.Geometry);v=(v-source_center)*1.3
   # The preserved round eave border projects 40mm beyond the main roof shell.
   # Keep the visible disk in front of that border; extend only its hidden rear
   # insertion by 19mm, creating a positive solid join to the measured tube rim.
   if template_index==0:v[v[:,1]>0,1]+=.019
   if side>0:v[:,1]*=-1;faces=[face[::-1] for face in faces]
   v+=np.array([x,y,z])
   lotus.append(part(v,faces,reference_object=ob.Attributes.Name,tile_row_x=x,eave_side=side,original_tube_end_axis=base.tolist(),drip_disk_axis=[x,y,z],original_eave_border_outer_y=-16.9+side*.780,front_eave_border_clearance_m=.0052,hidden_rear_insertion_extension_m=.019 if template_index==0 else 0))
assert len(lotus)==810
add.append(element('SITE_SOUTH_SCREENWALL_V12_LOTUS_DRIP_ENDS',lotus,'LOTUS_COVER_TILE_END_DISC_AND_RELIEF'))

def shell(rect,thickness):
 x0,y0,x1,y1=rect;xs=np.linspace(x0,x1,max(3,math.ceil((x1-x0)/.08)+1));ys=np.linspace(y0,y1,max(3,math.ceil((y1-y0)/.08)+1));nx=len(xs);ny=len(ys)
 top=np.array([[x,y,zscreen(x,y)-.075] for x in xs for y in ys]);N=len(top);v=np.vstack([top,top+[0,0,-thickness]]);faces=[]
 for i in range(nx-1):
  for j in range(ny-1):
   a=i*ny+j;b=(i+1)*ny+j;c=b+1;d=a+1;faces.extend([[a,b,c],[a,c,d],[d+N,c+N,b+N],[d+N,b+N,a+N]])
 rim=list(range(ny))+[i*ny+ny-1 for i in range(1,nx)]+[(nx-1)*ny+j for j in range(ny-2,-1,-1)]+[i*ny for i in range(nx-2,0,-1)]
 for a,b in zip(rim,rim[1:]+rim[:1]):faces.append([b,a,a+N,b+N])
 return part(v,faces,'M_Stone_Frame')
def ring(inside,outside,thickness):
 a,b,c,d=inside;x,y,z,w=outside
 # Disjoint four-sided rectangular frame, with only common edges at corners.
 return [shell(r,thickness) for r in [(x,y,z,b),(x,d,z,w),(x,b,a,d),(c,b,z,d)]]
inner=[3.25,-17.1,10.8,-16.72];tiers=[]
for outer,h in [([3.17,-17.25,10.88,-16.57],.27),([3.09,-17.4,10.96,-16.42],.18),([3.01,-17.54,11.04,-16.26],.09)]:
 tiers+=ring(inner,outer,h);inner=outer
add.append(element('SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE',tiers,'THREE_STEPPED_CLOSED_MASONRY_EAVE_SUPPORT_FRAMES'))
fascia=ring(inner,[2.95,-17.64,11.1,-16.16],.060)
add.append(element('SITE_SOUTH_SCREENWALL_V12_CLOSED_EAVE_FASCIA',fascia,'CLOSED_END_AND_EAVE_FASCIA_BELOW_CURVED_TILE_SHELL'))

mutation=dict(replace=[old],add=add,remove=[],definitions={},materials={},source_scene=str(SP),source_scene_sha256=sha(SP),reference_sources=refs,source_before_sha256=sha(SRC),retired_parts=['SITE_SOUTH_SCREENWALL_OPEN_RIDGE_LATTICE parts 3,4 (old short end posts only)'],preserved_nodes=[e['name'] for e in S['elements'] if 'SOUTH_SCREENWALL' in e['name'] and e['name']!=old['name']])
(O/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf-8')
scene=copy.deepcopy(S);lookup={old['name']:old};scene['elements']=[lookup.get(e['name'],e) for e in S['elements'] if 'SOUTH_SCREENWALL' in e['name']]+add
(O/'Preview_Scene.json').write_text(json.dumps(scene,ensure_ascii=False),encoding='utf-8')
qa=[];model=rh.File3dm();model.Settings.ModelUnitSystem=rh.UnitSystem.Meters;ly=rh.Layer();ly.Name='V12_Screenwall_Detail';model.Layers.Add(ly)
for e in [old]+add:
 for j,p in enumerate(e['parts']):
  g=p['geometry'];v=np.array(g['vertices']);faces=g['faces'];tri=[]
  for face in faces:
   if len(face)==3:tri.append(face)
   else:tri.extend([[face[0],face[k],face[k+1]] for k in range(1,len(face)-1)])
  tm=trimesh.Trimesh(v,np.array(tri),process=True);m=rh.Mesh()
  for pt in v:m.Vertices.Add(*pt)
  for face in tri:m.Faces.AddFace(*face)
  m.Normals.ComputeNormals();m.Compact();a=rh.ObjectAttributes();a.Name=e['name']+f'__{j+1}';a.LayerIndex=0;a.SetUserString('source_before',str(SRC));a.SetUserString('source',e['source']);a.SetUserString('node_name',e['name']);a.SetUserString('material',p['material']);model.Objects.AddMesh(m,a)
  qa.append(dict(node=e['name'],part=j+1,valid=m.IsValid,closed=m.IsClosed,watertight=bool(tm.is_watertight),volume_m3=abs(float(tm.volume)),min=v.min(0).tolist(),max=v.max(0).tolist()))
assert all(q['valid'] and q['closed'] and q['watertight'] and q['volume_m3']>1e-12 for q in qa)
bad_bounds=[q for q in qa if not (q['min'][0]>=2.95-1e-6 and q['max'][0]<=11.1+1e-6 and q['min'][1]>=(-17.688 if q['node'].endswith('LOTUS_DRIP_ENDS') else -17.64)-1e-6 and q['max'][1]<=(-16.112 if q['node'].endswith('LOTUS_DRIP_ENDS') else -16.16)+1e-6)]
if bad_bounds:print('BAD_BOUNDS',json.dumps(bad_bounds[:4]),flush=True)
assert not bad_bounds
assert model.Write(str(O/'Screenwall_V12_Detail_LOCAL.3dm'),8)
report=dict(status='PASS',parts=len(qa),added_parts=sum(len(e['parts']) for e in add),replaced_old_ridge_parts=len(old['parts']),retired_short_posts=2,high_finials=16,existing_cover_tile_rows=len(xs),lotus_relief_parts=810,all_closed=True,footprint_preserved=[2.95,-17.64,11.10,-16.16],max_new_ornament_z_m=max(q['max'][2] for q in qa),existing_base_and_roof_unchanged=True,lotus_relief_projecting_beyond_original_eave_border_m=.0078,drip_placement=drip_placement,reference_dimensions_surveyed=False,mutation_sha256=sha(O/'Mutation.json'),details=qa)
(O/'Geometry_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False),flush=True)
