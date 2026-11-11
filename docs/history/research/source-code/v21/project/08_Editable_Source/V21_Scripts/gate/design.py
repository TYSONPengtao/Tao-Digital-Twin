"""V21: transfer the user-named Rhino gate, close source sheets and correct junction.

Reads original native objects without executing a reference file's instructions.
Produces a separate mutation; does not save over either source native model.
"""
import sys,json,copy,math,ast,hashlib
from pathlib import Path
from collections import Counter,defaultdict
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,export_v5 as ex
from shapely.geometry import MultiPoint,Polygon
O=Path(__file__).parent;B=Path('E:/jz/JIA/Rebuild_V20')
SRC=Path('E:/CODEXdata/before/内大门/内大门_实景复原_分层可编辑_Rhino8.3dm')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S
for fn,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v9_eave_layers/mutation.py',['shell'])]:
 tree=ast.parse((W/fn).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[]};records=[];layers=defaultdict(list);source=rh.File3dm.Read(str(SRC));assert source
# Body source +/-1428 mm -> same 3.40 m retained stone gate zone. Threshold
# top is the established approach datum -0.45 m. Decorative projections are
# deliberately retained beyond the principal flush stone face.
scale=np.array([3.4/2.856,.8,1.1])/1000
offset=np.array([6.6,-11.582,-.45-.187*1.1])
def pose(v):return np.asarray(v,dtype=float)*scale+offset
def poly(v,f):return {'type':'polyhedron','vertices':np.asarray(v,float).tolist(),'faces':[list(t) for t in f]}
def pp(g,m,**kw):return {'geometry':g,'material':m,**kw}
def bx(a,b):
 a=np.array(a,float);b=np.array(b,float)
 v=[[x,y,z] for z in [a[2],b[2]] for y in [a[1],b[1]] for x in [a[0],b[0]]]
 return oriented(poly(v,[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]]))
def thicken(v,f,delta):
 v=np.asarray(v,float);nv=len(v);ee={}
 for face in f:
  for a,b in zip(face,face[1:]+face[:1]):ee.setdefault(tuple(sorted([a,b])),[]).append((a,b))
 assert all(len(q)<=2 for q in ee.values())
 faces=[list(q) for q in f]+[[i+nv for i in q[::-1]] for q in f]
 for q in ee.values():
  if len(q)==1:
   a,b=q[0];faces.append([a,a+nv,b+nv,b])
 return oriented(poly(np.vstack([v,v+delta]),faces))
def put(name,parts,**meta):
 e=copy.deepcopy(E.get(name,{'name':name,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}))
 for k in ['definition','origin','angle','external_mesh_file','external_native_cache','v20_native_cache_override','native_geometry_file']:e.pop(k,None)
 e.update(parts=parts,source=str(SRC),dimension_status='User-named native gate proportions fitted to registered site, field dimensions unmeasured',v21_gate_reference=True,**meta)
 Q['replace' if name in E else 'add'].append(e);return e
for i,l in enumerate(source.Layers):
 if i>14:continue
 mat='M_V21_GATE_REF_'+str(i+1).zfill(2)
 col=list(l.Color)[:3]
 Q['materials'][mat]={'color':col,'roughness':.88 if i not in [5,6,7] else .58,'role':'Transferred material color from user-named reference layer '+l.Name}
for idx,obj in enumerate(source.Objects):
 k=obj.Attributes.LayerIndex;g=obj.Geometry;n=obj.Attributes.Name
 rec={'source_index':idx,'source_id':str(obj.Attributes.Id),'source_name':n,'source_layer_index':k,'source_layer_name':list(source.Layers)[k].Name,'source_geometry_type':type(g).__name__}
 if k>=15:
  rec['disposition']='Excluded illustrative side walls/side trim/hidden control curves; real site junction retained instead';records.append(rec);continue
 if isinstance(g,rh.Brep):
  bb=g.GetBoundingBox();lo=[bb.Min.X,bb.Min.Y,bb.Min.Z];hi=[bb.Max.X,bb.Max.Y,bb.Max.Z]
  corners=np.array([[p.Location.X,p.Location.Y,p.Location.Z] for p in g.Vertices]);assert len(g.Faces)==6 and len(corners)==8 and np.logical_or(np.isclose(corners,lo),np.isclose(corners,hi)).all(),('Non-box source Brep',idx,n)
  rec['source_box_verified']={'face_count':6,'vertex_count':8,'all_eight_bbox_corners':True,'source_box_volume_mm3':float(np.prod(np.array(hi)-lo))}
  if n=='立柱束腰与石刻基座':
   if hi[0]<0:hi[0]=-960
   else:lo[0]=960
   rec['correction']='Source belt protruded 12mm across source door jamb; inner edge trimmed to stone column face to permit full inward swing'
  if n=='门槛石':
   hi[2]+=.002/scale[2]
   rec['correction']='Stone threshold cap exposes 2mm above coincident retained entry pavement; bottom and plan unchanged, no duplicate visible horizontal faces'
  geom=bx(pose([lo])[0],pose([hi])[0]);rec['conversion']='Verified axis-aligned source closed box transferred; only identified belt jamb intrusion corrected'
 elif isinstance(g,rh.Mesh):
  v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices]);f=[]
  for face in g.Faces:
   a,b,c,d=face;f.append([a,b,c] if c==d else [a,b,c,d])
  try:geom=oriented(poly(pose(v),f));rec['conversion']='Original closed source mesh transferred exactly'
  except ValueError:
   delta=np.array([0,0,-.055]) if k==8 else np.array([0,.006 if k==3 else .009,0])
   geom=thicken(pose(v),f,delta);rec['conversion']='Original visible source sheet retained; closed backing thickness '+str(float(np.linalg.norm(delta)))+' m'
 else:raise TypeError((idx,type(g)))
 mat='M_V21_GATE_REF_'+str(k+1).zfill(2);part=pp(geom,mat,reference_object_id=str(obj.Attributes.Id),reference_object_name=n,reference_layer=list(source.Layers)[k].Name)
 rec['part_geometry_sha256']=hashlib.sha256(json.dumps(geom,sort_keys=True).encode()).hexdigest()
 rec['disposition']='Transferred';records.append(rec);layers[k].append(part)

# Independent native doors and associated decorations. Static upper transom
# remains separate; the specified model's own timber leaf proportions retained.
doorparts={'L':[],'R':[]};static=[]
for k in [5,6,7]:
 for p in layers.pop(k):
  v=np.array(p['geometry']['vertices']);a=v.min(0);b=v.max(0)
  if a[0]<6.6<b[0]:static.append(p)
  else:doorparts['L' if v[:,0].mean()<6.6 else 'R'].append(p)
if static:put('SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM',static,classification='REFERENCE_GATE_FIXED_TRANSOM')
doors=[]
for side,parts in doorparts.items():
 # Slight clearance over source stone threshold; keeps header and whole leaf
 # within the available original reference stone portal.
 for p in parts:
  for v in p['geometry']['vertices']:v[2]+=.012
 # Original source upper transom starts at 2490mm but leaf reaches2500mm.
 # Keep a real10mm header clearance rather than inheriting this intersection.
 allv=np.vstack([p['geometry']['vertices'] for p in parts]);bottom_z=float(allv[:,2].min());old_top=float(allv[:,2].max());new_top=2490*scale[2]+offset[2]-.010
 for p in parts:
  for v in p['geometry']['vertices']:v[2]=bottom_z+(v[2]-bottom_z)*(new_top-bottom_z)/(old_top-bottom_z)
 span=np.vstack([p['geometry']['vertices'] for p in parts if '双开木门' in p.get('reference_object_name','')]);lo=span.min(0);hi=span.max(0)
 pivot=[lo[0] if side=='L' else hi[0],float(hi[1]+.035),float(lo[2])]
 degree=90 if side=='L' else -90
 # The actual courtyard drainage finish has a shallow slope below the open
 # leaves. Find its maximum within a conservative closed-to-open sweep hull
 # and reprofile only the leaf bottom, holding the upper edge/pivot fixed.
 vv=np.vstack([p['geometry']['vertices'] for p in parts]);sweep=[]
 for theta in np.linspace(0,degree,37):
  aa=math.radians(theta);rr=np.array([[math.cos(aa),-math.sin(aa)],[math.sin(aa),math.cos(aa)]])
  sweep.extend((vv[:,:2]-pivot[:2])@rr.T+pivot[:2])
 hull=MultiPoint(sweep).convex_hull;fd=np.load(B/'02_Data/Native_Readback/NATIVE_CONSTRUCTION_COURTYARD_DRAINAGE_FINISH.npz');floor_max=-1e9
 for face in fd['faces']:
  tri=fd['vertices'][face];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0])
  if normal[2]<=1e-10:continue
  hit=Polygon(tri[:,:2]).intersection(hull)
  if hit.is_empty or hit.area<1e-10:continue
  xy=np.array(hit.exterior.coords);z=tri[0,2]-(normal[0]*(xy[:,0]-tri[0,0])+normal[1]*(xy[:,1]-tri[0,1]))/normal[2];floor_max=max(floor_max,float(z.max()))
 newbottom=max(float(vv[:,2].min()),floor_max+.010)
 oldbottom=float(vv[:,2].min());oldtop=float(vv[:,2].max())
 for p in parts:
  for v in p['geometry']['vertices']:v[2]=newbottom+(v[2]-oldbottom)*(oldtop-newbottom)/(oldtop-oldbottom)
 a=math.radians(degree);r=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 for p in parts:p['geometry']['vertices']=((np.array(p['geometry']['vertices'])-pivot)@r.T+pivot).tolist()
 name='SITE_V20_INNER_GATE__LEAF_'+side
 put(name,parts,role='LEAF',v20_door=True,interaction='HINGED_INWARD',pivot_world_m=pivot,pivot_local_m=[0,0,0],hinge_axis_local=[0,0,1],inward_normal_local_xy=[0,1],open_angle_degrees=degree,current_pose='OPEN_INWARD',closed_pose=False,parent_door_id=None,classification='SOURCE_REFERENCE_INDEPENDENT_TIMBER_GATE_LEAF',drainage_finish_max_in_sweep_m=floor_max,drainage_clearance_m=newbottom-floor_max,leaf_reprofiled_bottom_m=newbottom,header_clearance_m=.010)
 doors.append({'name':name,'hinge_local_m':pivot,'inward_normal_local_xy':[0,1],'closed_leaf_direction_xy':[1,0] if side=='L' else [-1,0],'open_angle_deg':degree,'parent_door_id':None,'interaction':'HINGED_INWARD','reference':str(SRC)})

# Source collars penetrate the continuous stone piers. After trimming their
# jamb projection, their inner faces coincide with the pier side and render as
# black seams. Partition the solids at the real collars, keeping the visible
# envelope and every collar's reference layer/material intact.
collars=[p for p in layers[2] if p.get('reference_object_name')=='立柱束腰与石刻基座']
collar_union=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in collars],mf.OpType.Add)
for p in layers[1]:
 a=manifold(p['geometry']);cut=a-collar_union;mm=cut.to_mesh64()
 p['geometry']=oriented(poly(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts).tolist()))
 p['v21_junction_correction']='Reference collar volume partitioned from pier to remove coplanar inner faces; union envelope unchanged'
 for rec in records:
  if rec['source_id']==p.get('reference_object_id'):
   rec['junction_correction']=p['v21_junction_correction'];rec['final_part_geometry_sha256']=hashlib.sha256(json.dumps(p['geometry'],sort_keys=True).encode()).hexdigest()
for k,parts in layers.items():put('SITE_V21_GATE_REFERENCE_LAYER_'+str(k+1).zfill(2),parts,classification='USER_NATIVE_GATE_REFERENCE_'+str(k+1).zfill(2),reference_layer_name=list(source.Layers)[k].Name)

# The 657 s live view shows a continuous pale soffit. The source roof is
# a single sheet over partly visible braces, therefore fill its underside
# while retaining the reference exterior profiles and front ornament.
def source_eave(x):return 3150+70*(min(1,abs(x)/2230))**2+580*(min(1,abs(x)/2230))**7
def roof(x,y):
 hi=3540+350*(abs(x)/2230)**4
 if y<=120:t=(y+850)/970;return source_eave(x)*(1-t)+hi*t
 t=(y-120)/750;return hi*(1-t)+(source_eave(x)+45)*t
xs=pose(np.c_[np.linspace(-2210,2210,65),np.zeros(65),np.zeros(65)])[:,0]
ys=pose(np.c_[np.zeros(39),np.linspace(-835,855,39),np.zeros(39)])[:,1]
def top(x,y):
 xx=(x-offset[0])/scale[0];yy=(y-offset[1])/scale[1]
 return roof(xx,yy)*scale[2]+offset[2]-.004
def bottom(x,y):
 xx=(x-offset[0])/scale[0]
 return (source_eave(xx)-244)*scale[2]+offset[2]
Q['materials']['M_V21_GATE_CLOSED_PALE_SOFFIT']={'color':[187,182,172],'roughness':.91,'role':'Original INSV 657s continuous closed pale gate underside'}
put('SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT',[pp(oriented(shell(xs,ys,top,bottom=bottom)),'M_V21_GATE_CLOSED_PALE_SOFFIT')],classification='PHOTOGRAPHIC_CONTINUOUS_CLOSED_GATE_UNDERSIDE',reference_seconds=[650,657])

# The original kitchen has its front gable at y=-11.87 only beyond x9.05.
# The retired short white wing covered the intervening0.78m. Fill this in
# the same full-height gray brick gable plane, with a hidden keyed overlap
# behind the flush stone joint and a25mm connection into the actual gable.
gx=6.6+1400*scale[0];gy=-11.87;exx=9.05;back=-11.65
def kitchen_under(x,y):return min(-.29889484+.39953197*x-.00177447*y,9.41247826-.440834917*x+.00312578606*y)-.05-.075
vv=[[x,y,z] for z in [-.60,0.] for y in [gy,back] for x in [gx,exx]]
for i in range(4,8):vv[i][2]=kitchen_under(vv[i][0],vv[i][1])+.006
f=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]]
main=manifold(oriented(poly(vv,f)));key=manifold(bx([gx-.024,gy+.025,-.395],[gx+.006,back+.008,2.40]));brickkey=manifold(bx([exx-.024,gy+.025,-.395],[exx+.025,back+.008,2.40]));whole=main+key+brickkey;mm=whole.to_mesh64();vg=np.asarray(mm.vert_properties)[:,:3];fg=np.asarray(mm.tri_verts);join=oriented(poly(vg,fg.tolist()))
put('SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE',[pp(join,'M_Grey_Brick')],classification='SAME_PLANE_FULL_HEIGHT_GABLE_COMPLETION_WITH_HIDDEN_STONE_JOINT',front_y_m=gy,stone_butt_x_m=gx,existing_kitchen_start_x_m=9.05,kitchen_overlap_m=.025,roof_underlap_m=.006,hidden_stone_key_m=.024,reference='User screenshot2026-10-13 151254 and verified native kitchen gable endpoints')

# Remove every obsolete gate roof/body/decoration ancestor and redundant east
# flank. The real kitchen full-height masonry already occupies this junction.
for n in E:
 if (n.startswith('SITE_INNER_GATEHOUSE_') or n.startswith('SITE_GATEHOUSE_') or n.startswith('SITE_GATE_EAST_FLANK') or n in ['SITE_INNER_STONE_GATEHOUSE','SITE_V15_INNER_GATE_STONE_RELIEF','SITE_V15_INNER_GATE_TIMBER_TRANSOM_AND_HARDWARE']):Q['remove'].append(n)
# Old custom underlap depended on the superseded gate roof height, so retire
# it and use the true retained kitchen roof entering the new sealed body.
Q['remove'].append('SITE_KITCHEN_GATE_UNDERLAP_TILE_EDGE_CLOSURE')

# Lanterns are real video-observed loose fittings absent from the primary
# gate reference. Preserve their distinct material while fitting new columns.
n='SITE_V15_INNER_GATE_HANGING_LANTERNS';parts=[]
for p in E[n]['parts']:
 v,f=ex.world_part(p,E[n]);v=np.array(v);left=v[:,0].mean()<6.6
 v[:,0]+=(6.6+(-1 if left else 1)*1.18*scale[0]*1000)-(5.025 if left else 8.165)
 v[:,1]+=.01;v[:,2]-=.13
 parts.append(pp(oriented(poly(v,f)),p['material']))
put(n,parts,classification='RETAINED_PHOTO_LANTERNS_ALIGNED_TO_REFERENCE_GATE')
Q['cameras']=[['V21_Inner_Gate_Reference_Front',[6.6,-16.5,1.7],[6.6,-11.65,1.7],70],['V21_Inner_Gate_Kitchen_Flush_Junction',[9.8,-14.8,1.1],[8.35,-11.8,1.25],60],['V21_Inner_Gate_Reference_Underside',[6.6,-13.1,1.3],[6.6,-11.7,2.85],90]]
proof={'status':'DESIGN_WRITTEN_QA_PENDING','reference_file':str(SRC),'reference_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_unit':'Millimeters','source_object_count':len(records),'source_layers':len(list(source.Layers)),'transfer_scale_m_per_mm':scale.tolist(),'offset_local_m':offset.tolist(),'fixed_stone_front_and_kitchen_gable_y_m':-11.87,'door_clear_opening_nominal_m':1.888*scale[0]*1000,'photo_evidence':['Original INSV 650s lens0 yaw40 pitch20','Original INSV 657s lens0/lens1 pitch25','User screenshot2026-10-13 151254 red circle'],'removed_obsolete_nodes':Q['remove'],'source_object_transfer':records,'dimension_status':'Photo-fit affine placement; no surveyed new dimensions','kitchen_junction_completion':'Source kitchen gable starts x9.05; visible face ends exactly there with no coplanar strip, full roof height, 24mm hidden stone key and 25mm hidden gable key'}
(O/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Door_Updates.json').write_text(json.dumps({'remove':[],'upsert':doors},ensure_ascii=False,indent=2),encoding='utf8')
(O/'Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print('PATCH',len(Q['replace']),len(Q['add']),len(Q['remove']),'SOURCE OBJECTS',len(records),flush=True)
