"""Read-only independent contact audit; records source/native evidence explicitly."""
from v23_common import *
import hashlib, time
import rhino3dm as rh

O=Path('E:/jz/JIA/Rebuild_V23'); NP=O/'04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm'
Q=json.loads((W/'v23/Mutation.json').read_text(encoding='utf8'))
N={e['name']:e for e in Q['replace']+Q['add']}
NI=O/'02_Data/Native_Readback_Index_V23.json'
native_index={r['name']:r for r in json.loads(NI.read_text(encoding='utf8'))} if NI.exists() else {}
checks=[];cache={};p_cache={};native_arrays={};native_part_proof={};solid_methods={};document_tolerance_m=None
if native_index and NP.exists():
 # Canonicalize actual individual saved Rhino objects.  Joining raw cache
 # shells into a single manifold before resolving overlaps can misinterpret
 # coincident internal partitions (notably the three jamb material parts).
 nf=rh.File3dm.Read(str(NP));co=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'))
 document_tolerance_m=float(nf.Settings.ModelAbsoluteTolerance)
 an=math.radians(co['rotation_deg']);rr=np.array([[math.cos(an),-math.sin(an),0],[math.sin(an),math.cos(an),0],[0,0,1]]);ori=np.array(co['origin'])
 for ob in nf.Objects:
  node=ob.Attributes.GetUserString('V23_Node')
  if node not in N:continue
  g=ob.Geometry;vv=(np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()])-ori)@rr;ff=[]
  for face in g.Faces:
   ff.append(list(face[:3]))
   if face[3]!=face[2]:ff.append([face[0],face[2],face[3]])
  native_arrays.setdefault(node,[]).append((int(ob.Attributes.Name.rsplit('__',1)[1]),ob.Attributes.Name,str(ob.Attributes.Id),nf.Materials[ob.Attributes.MaterialIndex].Name,vv,np.array(ff,np.uint64)))
 del nf

def sourceparts(n):
 e=N.get(n,E.get(n));out=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e);out.append(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':f}))
 return out

def pieces(n):
 if n not in p_cache:
  if n in native_arrays:
   ps=[];proof=[]
   for _,name,gid,mat,v,f in sorted(native_arrays[n],key=lambda r:r[0]):
    for dec in [10,9,8,7]:
     vv,iv=np.unique(np.round(v,dec),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)))
     if m.status()==mf.Error.NoError:break
    assert m.status()==mf.Error.NoError,(name,m.status());ps.append(m);proof.append({'object':name,'id':gid,'material':mat,'vertex_weld_decimals_m':dec,'volume_m3':m.volume()})
   p_cache[n]=ps;native_part_proof[n]=proof
  else:p_cache[n]=sourceparts(n)
 return p_cache[n]

def solid(n):
 if n in cache:return cache[n]
 method='merged_source' if n in N else 'V22_native_baseline'
 if n in native_arrays:
  m=uni(pieces(n));method='canonical_union_actual_individual_saved_V23_Rhino_objects'
 elif native_index and n in native_index:
  d=np.load(O/'02_Data'/native_index[n]['file']);v=d['vertices'];f=d['faces'];m=None
  for dec in [9,8,7,6]:
   vv,inv=np.unique(np.round(v,dec),axis=0,return_inverse=True)
   mm=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)))
   if mm.status()==mf.Error.NoError:m=mm;break
  if m is None:m=uni(pieces(n));method='merged_source_union_native_cache_compound'
  else:method='saved_V23_native_cache'
 else:m=uni(pieces(n)) if n in N else raw(n)
 assert m.status()==mf.Error.NoError,(n,m.status())
 cache[n]=m;solid_methods[n]=method;return m

def check(label,ok,**data):
 row={'check':label,'pass':bool(ok),**data};checks.append(row);print(json.dumps(row),flush=True)

def contact(label,a,b,overlap_required=False):
 ov=float((a^b).volume());gap=float(a.min_gap(b,.005))
 check(label,ov>1e-9 if overlap_required else gap<3e-6,overlap_m3=ov,gap_m=gap,overlap_required=overlap_required)

pier=solid('SITE_V21_GATE_REFERENCE_LAYER_02');header=solid('SITE_V21_GATE_REFERENCE_LAYER_05')
closure=solid('SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE')
kitchen=solid('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY')
soffit=solid('SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT');base=solid('SITE_V21_GATE_REFERENCE_LAYER_01')
contact('Faceted piers retain keyed kitchen closure connection',pier,closure,True)
contact('Closure retains original kitchen masonry connection',closure,kitchen,True)
contact('Closure retains gate closed soffit connection',closure,soffit,True)
contact('Closure retains kitchen roof connection',closure,solid('SITE_KITCHEN_CHINESE_TILE_ROOF'),True)
contact('Pier base support',pier,base)
contact('Carved header bears on faceted piers',header,pier)
contact('Pier capitals connect closed soffit',pier,soffit)

def frontproj(m):
 q=m.to_mesh64();v=np.asarray(q.vert_properties)[:,:3];polys=[]
 for f in np.asarray(q.tri_verts):
  t=v[f]
  if np.max(abs(t[:,1]+11.87))>2e-6:continue
  p=Polygon(t[:,[0,2]])
  if p.area>1e-12:polys.append(p)
 return unary_union(polys)
fc=frontproj(closure);fk=frontproj(kitchen)
check('Kitchen front and closure remain coplanar and edge-connected',fc.area>.1 and fk.area>.1 and fc.distance(fk)<3e-6 and fc.intersection(fk).area<3e-6,plane_y_m=-11.87,closure_area_m2=fc.area,kitchen_area_m2=fk.area,edge_gap_m=fc.distance(fk),coplanar_overlap_area_m2=fc.intersection(fk).area)

if 'GATE_V23_LEFT_WALL_JAMB_CLOSURE' in N:
 jamb=solid('GATE_V23_LEFT_WALL_JAMB_CLOSURE')
 contact('Final left wall return keyed into retained wall',jamb,solid('SITE_COURTYARD_WEST_TILE_WALL'),True)
 contact('Final left wall return keyed into faceted pier',jamb,pier,True)
 for n in ['SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING','SITE_COURTYARD_WEST_TILE_WALL_V10_RIDGE_SEAT_AND_CAP','SITE_COURTYARD_WEST_TILE_WALL_V10_OPEN_FLOWER_BRICKS']:
  contact('Final left wall return closes coping end '+n,jamb,solid(n),True)
 ov=float((jamb^(solid('SITE_V21_GATE_REFERENCE_LAYER_03')+solid('SITE_V21_GATE_REFERENCE_LAYER_04'))).volume())
 check('Final jamb leaves exposed carving and frame lips clear',ov<1e-8,overlap_m3=ov)
 matrix=[]
 for j,jp in enumerate(pieces('GATE_V23_LEFT_WALL_JAMB_CLOSURE')):
  for n in ['SITE_V21_GATE_REFERENCE_LAYER_03','SITE_V21_GATE_REFERENCE_LAYER_04']:
   for k,p in enumerate(pieces(n)):
    overlap=jp^p;vol=float(overlap.volume())
    if abs(vol)>1e-11:matrix.append({'jamb_native_object':native_part_proof['GATE_V23_LEFT_WALL_JAMB_CLOSURE'][j],'ornament_native_object':native_part_proof[n][k],'overlap_m3':vol,'component_bounds':[{'volume_m3':x.volume(),'bbox_local_m':x.bounding_box()} for x in overlap.decompose() if abs(x.volume())>1e-11]})
 check('Individual actual native jamb/frame pairs have no material overlap above original threshold',all(abs(r['overlap_m3'])<1e-8 for r in matrix),nonzero_numerical_pairs=matrix,original_overlap_tolerance_m3=1e-8)
 check('Final jamb retains existing wall front plane',abs(jamb.bounding_box()[1]+11.825)<3e-6,front_y_m=jamb.bounding_box()[1])

for n in ['SITE_V21_GATE_REFERENCE_LAYER_03','SITE_V21_GATE_REFERENCE_LAYER_04']:
 mins=[];bad=[]
 support=pier+header+base+solid('SITE_V21_GATE_REFERENCE_LAYER_03')
 for i,p in enumerate(pieces(n)):
  # Remove this exact part from the support before checking frames/collars.
  ref=(pier+header+base) if n.endswith('_03') else support
  for j,c in enumerate(p.decompose()):
   if abs(c.volume())<1e-10:continue
   gap=float(c.min_gap(ref,.005));mins.append(gap)
   if gap>=3e-6:bad.append({'part':i,'component':j,'volume_m3':c.volume(),'gap_m':gap})
 check(n+' all positive ornament components rooted',not bad,components=len(mins),maximum_gap_m=max(mins,default=0),unrooted=bad)

# Check each changed roof ornament and short rafter against its solid carrier.
# Shallow decorative friezes can touch the cornice as well as the closed soffit.
roof=solid('SITE_V21_GATE_REFERENCE_LAYER_09');roof_support=roof+soffit
tile_parts=pieces('SITE_V21_GATE_REFERENCE_LAYER_10');tile_contacts=[];bad_tiles=[]
for i,p in enumerate(tile_parts):
 ov=float((p^roof).volume());tile_contacts.append(ov)
 if ov<=1e-10:bad_tiles.append({'part':i,'overlap_m3':ov,'gap_m':float(p.min_gap(roof,.005))})
check('All individual saved segmented tiles contact actual compact carrier',not bad_tiles,count=len(tile_parts),minimum_overlap_m3=min(tile_contacts),unsupported=bad_tiles)
cap_parts=pieces('GATE_V22_EMBOSSED_TILE_END_CAPS');cap_contacts=[];bad_caps=[]
for i,p in enumerate(cap_parts):
 # Native order is lane/front/rear; the first 258 tiles are three barrel
 # segments for every front/rear lane, before the concave pan units.
 first=tile_parts[i*3];ov=float((p^first).volume());cap_contacts.append(ov)
 if ov<=1e-10:bad_caps.append({'part':i,'first_tile_part':i*3,'overlap_m3':ov,'gap_m':float(p.min_gap(first,.005))})
check('All individual saved flower caps contact their first compact barrel tile',not bad_caps,count=len(cap_parts),minimum_overlap_m3=min(cap_contacts),unsupported=bad_caps)
roof_bounds=roof.bounding_box();allroof=roof+solid('SITE_V21_GATE_REFERENCE_LAYER_14')
check('Compact eave remains above left concealed wall return',allroof.bounding_box()[5]<3.35 and solid('GATE_V23_LEFT_WALL_JAMB_CLOSURE').bounding_box()[5]<roof_bounds[2],compact_roof_ridge_max_z_m=allroof.bounding_box()[5],gate_carrier_min_z_m=roof_bounds[2],left_return_top_m=solid('GATE_V23_LEFT_WALL_JAMB_CLOSURE').bounding_box()[5])
# The gable closure bridges two covers: the compact gate's deep closed
# soffit on the left, and the retained kitchen roof beginning near x=8.9.
# Check each top section contacts its actual cover without protruding above
# the combined cover envelope. This also catches a gap at the roof handoff.
kroof=solid('SITE_KITCHEN_CHINESE_TILE_ROOF');combined_cover=kroof+roof+soffit;profile=[];profile_ok=True
ceramic_parts=[(n,i,p) for n in ['SITE_V21_GATE_REFERENCE_LAYER_10','GATE_V22_EMBOSSED_TILE_END_CAPS','SITE_V21_GATE_REFERENCE_LAYER_14'] for i,p in enumerate(pieces(n))]
for x in np.linspace(8.28,9.04,13):
 clip=cube([float(x)-.002,-11.868,2.0],[.004,.008,2.0]);wallsec=closure^clip;roofsec=combined_cover^clip
 ceramic_sections=[];ceramic_proof=[]
 for n,i,p in ceramic_parts:
  bb=p.bounding_box()
  if bb[0]>x+.002 or bb[3]<x-.002 or bb[1]>-11.860 or bb[4]<-11.868:continue
  sec=p^clip
  if sec.is_empty():continue
  ceramic_sections.append(sec);record=native_part_proof[n][i]
  ceramic_proof.append({'node':n,'part':i,'actual_native_object':record['object'],'native_id':record['id'],'material':record['material'],'section_bottom_z_m':sec.bounding_box()[2],'section_top_z_m':sec.bounding_box()[5]})
 if ceramic_sections:roofsec+=uni(ceramic_sections)
 if wallsec.is_empty() or roofsec.is_empty():
  profile_ok=False;profile.append({'x_m':float(x),'wall_present':not wallsec.is_empty(),'gate_or_kitchen_cover_present':not roofsec.is_empty()});continue
 wz=wallsec.bounding_box()[5];rz=roofsec.bounding_box()[2];rt=roofsec.bounding_box()[5];overlap=float((wallsec^roofsec).volume());profile_ok&=overlap>1e-10 and wz<=rt+(document_tolerance_m or 2e-6)
 profile.append({'x_m':float(x),'wall_top_z_m':wz,'gate_or_kitchen_cover_bottom_z_m':rz,'cover_top_z_m':rt,'wall_above_cover_top_m':max(0.,wz-rt),'positive_cover_contact_m3':overlap,'actual_ceramic_cover_sections':ceramic_proof})
max_facet_projection=max(s.get('wall_above_cover_top_m',0.) for s in profile)
check('Closure top stays connected under actual gate-soffit or kitchen roof across compact junction',profile_ok,sections=profile,maximum_facet_projection_m=max_facet_projection,stored_document_absolute_tolerance_m=document_tolerance_m,verdict='PASS_WITHIN_DOCUMENT_TOLERANCE' if profile_ok else 'FAIL',mathematical_zero_projection_claimed=False)
for n in ['SITE_V21_GATE_REFERENCE_LAYER_11','SITE_V21_GATE_REFERENCE_LAYER_12','SITE_V21_GATE_REFERENCE_LAYER_13','SITE_V21_GATE_REFERENCE_LAYER_15']:
 ref=roof_support if not n.endswith('_13') else roof_support+solid('SITE_V21_GATE_REFERENCE_LAYER_11')+solid('SITE_V21_GATE_REFERENCE_LAYER_12')
 gaps=[];bad=[]
 for i,p in enumerate(pieces(n)):
  for j,c in enumerate(p.decompose()):
   if abs(c.volume())<1e-10:continue
   gap=float(c.min_gap(ref,.005));gaps.append(gap)
   if gap>=3e-6:bad.append({'part':i,'component':j,'gap_m':gap,'volume_m3':c.volume()})
 check(n+' all eave components supported',not bad,components=len(gaps),maximum_gap_m=max(gaps,default=0),unrooted=bad)

hp=pieces('SITE_V21_GATE_REFERENCE_LAYER_05')
for i,p in enumerate(hp[1:],1):contact('Header relief or frame '+str(i)+' rooted in structural field',p,hp[0])

if 'GATE_V22_PALE_CEILING_DISK' in native_index:
 disks=solid('GATE_V22_PALE_CEILING_DISK');overlap=float((disks^header).volume())
 check('Ceiling disks clear carved stone header',overlap<1e-8,overlap_m3=overlap)
 disk_parts=disks.decompose();check('Front and courtyard ceiling disks are separate assemblies',len(disk_parts)==2,assemblies=len(disk_parts))
 for i,d in enumerate(disk_parts):contact('Ceiling disk '+str(i)+' supported on closed soffit',d,soffit,True)

for n in ['SITE_V20_INNER_GATE__LEAF_L','SITE_V20_INNER_GATE__LEAF_R']:
 ps=pieces(n);body=ps[0];support=uni(ps[:17]);bad=[]
 for i in [1,3,5,14,15,16,17]:
  if i>=len(ps):continue
  contact(n+' supported moving part '+str(i),ps[i],ps[14] if i in [1,3,5] else body)
 check(n+' threshold clearance retained',abs(solid(n).bounding_box()[2]+.337)<3e-6,minimum_z_m=solid(n).bounding_box()[2],threshold_top_m=-.350)

lan=pieces('SITE_V15_INNER_GATE_HANGING_LANTERNS')
for k in [0,4]:
 body,fix,cord,tassel=lan[k:k+4]
 contact('Lantern '+str(k//4)+' cord meets soffit',cord,soffit,True)
 contact('Lantern '+str(k//4)+' cord meets upper cap',cord,fix,True)
 contact('Lantern '+str(k//4)+' body meets fixtures',body,fix,True)
 contact('Lantern '+str(k//4)+' tassels meet bottom cap',tassel,fix,True)

n='SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM';ps=pieces(n)
contact('Fixed wood scroll ornament backing meets timber',ps[-1],ps[0],True)

native_present=NP.exists();native_hash=None
if native_present and native_index:
 try:native_hash=hashlib.file_digest(NP.open('rb'),'sha256').hexdigest()
 except PermissionError:pass
out={'status':'PASS_INDEPENDENT_CONTACT_AUDIT' if all(r['pass'] for r in checks) else 'FAIL_INDEPENDENT_CONTACT_AUDIT','model':str(NP),'native_model_present':native_present,'native_cache_index_present':bool(native_index),'evidence':'Canonical Boolean unions of actual individual saved V23 Rhino objects for changed nodes; authoritative unchanged native caches for retained nodes' if native_index else 'Merged V23 source patch with authoritative retained V22 native baseline; V23 assembly not yet complete at start of this review','native_sha256':native_hash,'checks':checks,'failure_count':sum(not r['pass'] for r in checks),'solid_methods':solid_methods,'actual_native_part_proof':native_part_proof,'conditioning_diagnosis':'work/v23_native_overlap_diagnosis.json','limits':['No UE runtime test','No photographic accuracy metric; botanical carving composition is fitted','Contact tolerance 3 micrometres in local metre geometry']}
out['document_absolute_tolerance_m']=document_tolerance_m
if out['failure_count']==0 and max_facet_projection>0:
 out['status']='PASS_INDEPENDENT_CONTACT_AUDIT_WITHIN_DOCUMENT_TOLERANCE'
 out['limits'].append(f'Actual ceramic cover section has {max_facet_projection*1000:.6f} mm maximum measured facet projection, within saved Rhino {document_tolerance_m*1000:.6f} mm tolerance; not mathematically zero.')
(W/'v23_independent_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(out['status'],out['failure_count'],flush=True)
