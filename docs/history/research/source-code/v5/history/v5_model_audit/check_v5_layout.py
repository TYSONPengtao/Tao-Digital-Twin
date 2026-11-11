"""Independent V5 door/layout QA. Reads V4/V5, writes audit reports only.
Run after V5 scene export; coordinate expectations are explicit in config.
"""
import sys,json,math,hashlib,collections
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['geomlibs','np1','libs']]
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
O=Path(__file__).parent
BASE=Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json')
TARGET=Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json')
CONFIG=O/'Expectations_V5.json'

def world(P,e):return translate(rotate(P,e.get('angle',0),origin=(0,0),use_radians=True),*e.get('origin',[0,0,0])[:2])
def volume_parts(e):
 out=[]
 for p in e.get('parts',[]):
  g=p['geometry'];typ=g['type'];dz=e.get('origin',[0,0,0])[2]
  if typ=='prism_holes':out.append((world(Polygon(g['outer'],g.get('holes',[])),e),g['z']+dz,g['z']+g['height']+dz))
  elif typ=='box':
   x,y,z=g['origin'];w,d,h=g['size'];out.append((world(box(x,y,x+w,y+d),e),z+dz,z+h+dz))
  else:raise ValueError(e['name']+' unsupported QA geometry '+typ)
 return out

def polys_at(parts,z):return unary_union([P for P,a,b in parts if a-1e-9<z<b+1e-9])
def integrate_in_region(parts,region,z0,z1):
 levels=sorted({z0,z1}|{v for _,a,b in parts for v in [a,b] if z0<v<z1});vol=0
 for a,b in zip(levels[:-1],levels[1:]):vol+=polys_at(parts,(a+b)/2).intersection(region).area*(b-a)
 return vol

def payload(e,S):
 keys=['parts','definition','origin','angle','layer','family']
 r={k:e[k] for k in keys if k in e}
 if 'definition' in e:r['definition_geometry']=S['definitions'][e['definition']]['parts']
 return r

def hash_data(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run():
 if not TARGET.exists():
  print(json.dumps({'status':'WAITING_FOR_V5_SCENE','target':str(TARGET)},ensure_ascii=False));return
 A=json.loads(BASE.read_text(encoding='utf-8'));B=json.loads(TARGET.read_text(encoding='utf-8'));cfg=json.loads(CONFIG.read_text(encoding='utf-8-sig')) if CONFIG.exists() else {}
 EA={e['name']:e for e in A['elements']};EB={e['name']:e for e in B['elements']};checks=[]
 def check(id,ok,detail,status=None):checks.append({'id':id,'status':status or ('PASS' if ok else 'FAIL'),'detail':detail})
 exempt=set(cfg.get('removed_elements',['WINDOW_STUDY_C3620_F3']))
 protected=[e for e in A['elements'] if e['layer'] not in ['11_WALL_INT','30_DOOR'] and e['name'] not in exempt]
 mismatches=[e['name'] for e in protected if e['name'] not in EB or hash_data(payload(e,A))!=hash_data(payload(EB[e['name']],B))]
 check('Preserve_site_exterior_structure',not mismatches,{'protected_count':len(protected),'changed_or_missing':mismatches})
 check('Coordinate_unchanged',A['coordinate']==B['coordinate'],{})
 check('Levels_grid_unchanged',all(A[k]==B[k] for k in ['levels','grid_x','grid_y']),{})
 walls=[]
 for e in B['elements']:
  if e['layer'] in ['10_WALL_EXT','11_WALL_INT']:
   try:walls.extend((e['name'],*p) for p in volume_parts(e))
   except ValueError as er:check('Wall_QA_unsupported_'+e['name'],False,str(er))
 beam_overlaps=[]
 for e in B['elements']:
  if not e['name'].startswith('BEAM_'):continue
  for P,a,b in volume_parts(e):
   for name,Q,c,d in walls:
    dh=max(0,min(b,d)-max(a,c));vol=P.intersection(Q).area*dh
    if vol>1e-8:beam_overlaps.append({'beam':e['name'],'wall':name,'overlap_m3':vol})
 check('Beam_core_excluded',not beam_overlaps,beam_overlaps)
 # Explicit empty/filled region checks. This is geometric QA, not surveyed accuracy.
 for r in cfg.get('regions',[]):
  e=EB.get(r['host']);parts=volume_parts(e) if e else []
  P=Polygon(r['polygon']) if 'polygon' in r else box(*r['rect']);z0,z1=r['z'];vol=integrate_in_region(parts,P,z0,z1);expected=P.area*(z1-z0)
  if r['expect']=='empty':
   expected=0.;ok=vol<r.get('tolerance_m3',1e-7)
  elif r['expect']=='filled':
   # Deduct real framework volume from expected wall fill.
   lev=sorted({z0,z1}|{v for q in B['elements'] if q['name'].startswith('BEAM_') for _,a,b in volume_parts(q) for v in [a,b] if z0<v<z1});expected=0
   for a,b in zip(lev[:-1],lev[1:]):
    mid=(a+b)/2;core=unary_union([Q for q in B['elements'] if q['name'].startswith('BEAM_') for Q,c,d in volume_parts(q) if c<mid<d]);expected+=P.difference(core).area*(b-a)
   ok=abs(expected-vol)<r.get('tolerance_m3',1e-7)
  else:ok=False
  check(r['id'],ok,{'host':r['host'],'expect':r['expect'],'wall_volume_m3':vol,'expected_volume_m3':expected,'scope':r.get('note','')})
 # Door assemblies, original IDs and registry evidence.
 registry=B.get('door_registry',B.get('doors',[]));registry=list(registry.values()) if isinstance(registry,dict) else registry
 if not registry:registry=[r for r in B.get('openings',[]) if r.get('type')=='door']
 check('Door_registry_exists',bool(registry),{'count':len(registry)})
 for r in cfg.get('doors',[]):
  frame=EB.get(r['frame_element']);leaf=[EB[n] for n in r.get('leaf_elements',[]) if n in EB];old=EA.get(r['original_id']);width=r['opening_width'];height=r['opening_height'];origin=r['origin'];angle=r.get('angle',0)
  check('Door_assembly_'+r['original_id'],frame is not None and len(leaf)==len(r.get('leaf_elements',[])),{'frame':r['frame_element'],'leaves':r.get('leaf_elements',[])})
  if frame:
   check('Door_frame_role_'+r['original_id'],frame.get('role')=='FRAME' if width<2 else True,{'role':frame.get('role')})
   check('Door_transform_'+r['original_id'],all(abs(a-b)<1e-8 for a,b in zip(frame.get('origin',[0,0,0]),origin)) and abs(frame.get('angle',0)-angle)<1e-8,{'frame_origin':frame.get('origin'),'target':origin})
  for L in leaf:
   d=B['definitions'][L['definition']];check('Leaf_pivot_'+L['name'],L.get('role')=='LEAF' and L.get('pivot_world_m')==L.get('origin') and L.get('pivot_local_m')==[0,0,0] and d.get('parameters',{}).get('Hinge_Local')==[0,0,0],{'origin':L.get('origin'),'pivot_local':L.get('pivot_local_m'),'hinge_handedness_status':L.get('swing_status')})
  margins=r.get('frame_clear_margin',[.045,.045,.045,0]);left,right,top,bottom=margins
  cavity=world(box(left+.001,-.25,width-right-.001,.25),{'origin':origin,'angle':angle});z0=origin[2]+bottom+.001;z1=origin[2]+height-top-.001
  occupied=0
  for name,P,a,b in walls:occupied+=P.intersection(cavity).area*max(0,min(b,z1)-max(a,z0))
  check('New_door_clear_opening_'+r['original_id'],occupied<1e-7,{'wall_overlap_m3':occupied})
  if old and r.get('check_old_fill'):
   oldwidth=A['definitions'][old['definition']]['parameters']['Width'];oldheight=A['definitions'][old['definition']]['parameters']['Height'];oldP=world(box(0,-.25,oldwidth,.25),old);host=EA[r['old_host']];oldenv=unary_union([P for P,_,_ in volume_parts(host)]);targetP=world(box(0,-.25,width,.25),{'origin':origin,'angle':angle});restore=oldP.intersection(oldenv).difference(targetP)
   parts=volume_parts(EB[r['old_host']]);a=old['origin'][2]+.001;b=old['origin'][2]+oldheight-.001;actual=integrate_in_region(parts,restore,a,b);expected=restore.area*(b-a)
   check('Old_door_closed_'+r['original_id'],abs(expected-actual)<1e-7,{'restored_m3':actual,'expected_m3':expected})
  ids=[q.get('door_id',q.get('id',q.get('name'))) for q in registry];check('Door_ID_preserved_'+r['original_id'],r['original_id'] in ids or r['original_id'] in [q.get('previous_id') for q in registry],{'registry_ids':ids})
 expected_ids=cfg.get('required_checks',[]);present={r['id'] for r in checks}
 for id in expected_ids:
  if id not in present:check(id,False,'No configured coordinate expectation; cannot verify',status='NEEDS_CONFIGURATION')
 if not cfg.get('doors'):check('Door_coordinate_expectations',False,'Doors not configured',status='NEEDS_CONFIGURATION')
 if not cfg.get('regions'):check('Layout_region_expectations',False,'Regions not configured',status='NEEDS_CONFIGURATION')
 counts=collections.Counter(c['status'] for c in checks);result={'baseline':str(BASE),'target':str(TARGET),'source_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'status_counts':dict(counts),'checks':checks,'meaning':'Geometric consistency QA only; PASS is not field measurement verification.'}
 (O/'V5_Independent_Layout_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');lines=['# V5 门洞与布局独立几何核查','',result['meaning'],'',f'检查结果：{dict(counts)}','']
 for r in checks:lines.append(f"- {r['status']} — {r['id']}: {json.dumps(r['detail'],ensure_ascii=False)}")
 (O/'V5_Independent_Layout_QA.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':run()

