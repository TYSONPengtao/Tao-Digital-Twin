"""Read-only merged-scene navigation audit, independent of mutation assertions."""
import sys,json,math,hashlib,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from shapely import affinity
import export_v5 as ex
P=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(P.read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
R={r['room_id']:r for r in S['rooms']};checks=[];risks=[]
def add(id,ok,**data):checks.append(dict(id=id,status='PASS' if ok else 'FAIL',**data))
def wall_xy(f,z):
 return unary_union([Polygon(g['outer'],g['holes']) for p in E[f'PARTITIONS_JOINED_F{f}']['parts'] if (g:=p['geometry'])['z']<z<g['z']+g['height']])

# Confirm actual portals straddle their registered pair of room query zones.
# The normal samples avoid the empty 0.1m review buffer around physical walls.
for r in S['door_registry']:
 if r['floor'] not in [1,2] or not r.get('leaf_element'):continue
 a=r['angle'];w=r['nominal_opening_width_m'];c=np.array(r['origin'][:2])+w/2*np.array([math.cos(a),math.sin(a)])
 n=np.array([-math.sin(a),math.cos(a)]);sides=[c-.27*n,c+.27*n]
 found=[]
 for p in sides:
  found.append([rr['room_id'] for rr in S['rooms'] if rr['floor']==r['floor'] and Polygon(rr['review_polygon_xy_m']).buffer(1e-7).covers(Point(p))])
 expected=r['connected_rooms'];covered=set(sum(found,[]))
 add('Room_query_sides_'+r['door_id'],set(expected)<=covered and all(len(v)==1 for v in found),expected=expected,actual_sides=found,points_xy=[p.tolist() for p in sides])
 # Clear door portal independent of frame/leaf: walls may not occupy the
 # middle 0.58m of a nominal 0.8/0.9m door at any occupied-body height.
 bad=[]
 for dz in [.15,.75,1.45,1.95]:
  pp=wall_xy(r['floor'],r['origin'][2]+dz)
  for t in [.18,.35,.5,.65,.82]:
   for side in [-.085,0,.085]:
    p=np.array(r['origin'][:2])+w*t*np.array([math.cos(a),math.sin(a)])+side*n
    if pp.covers(Point(p)):bad.append([*p.tolist(),r['origin'][2]+dz])
 add('Actual_wall_portal_clear_'+r['door_id'],not bad,obstructed_samples=bad[:12])

# Extract the actual static solid triangles, including structural beams,
# floors and the other flight; test vertical walking headroom on centre line.
tri=[];tri_names=[]
for e in S['elements']:
 if e['name'].startswith('CONSTRUCTION_') or e['layer'] not in ['10_WALL_EXT','11_WALL_INT','20_COLUMN','21_BEAM','22_SLAB','40_STAIR']:continue
 for p in ex.expand_parts(e):
  vv,ff=ex.world_part(p,e)
  if vv is None:continue
  for face in ff:
   for ids in ex.triangulate(vv[face]) if len(face)>3 else [[0,1,2]]:
    t=vv[[face[i] for i in ids]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>1e-10:tri.append(t);tri_names.append(e['name'])
T=np.asarray(tri);names=np.asarray(tri_names);A=T[:,0,:2];B=T[:,1,:2];C=T[:,2,:2];u=B-A;v=C-A;det=u[:,0]*v[:,1]-u[:,1]*v[:,0]
def ceiling(x,y,z):
 rel=np.array([x,y])-A;den=det.copy();den[abs(den)<1e-12]=1
 ss=(rel[:,0]*v[:,1]-rel[:,1]*v[:,0])/den;tt=(u[:,0]*rel[:,1]-u[:,1]*rel[:,0])/den
 hit=(abs(det)>1e-10)&(ss>=-1e-8)&(tt>=-1e-8)&(ss+tt<=1+1e-8)
 zz=T[:,0,2]+ss*(T[:,1,2]-T[:,0,2])+tt*(T[:,2,2]-T[:,0,2]);ids=np.flatnonzero(hit&(zz>z+.05))
 if not len(ids):return None
 j=ids[np.argmin(zz[ids])];return dict(headroom_m=float(zz[j]-z),overhead=str(names[j]),overhead_z=float(zz[j]))
headroom=[]
for f,z,mid,top in [(1,0,1.95,3.9),(2,3.9,5.7,7.5)]:
 for flight,bz,yy in [(1,z,9.11),(2,mid,7.99)]:
  rise=(mid-z)/11 if flight==1 else (top-mid)/11
  for k in range(10):
   xx=7.8-(k+.5)*.26 if flight==1 else 5.2+(k+.5)*.26
   zz=bz+(k+1)*rise;q=ceiling(xx,yy,zz)
   if q:headroom.append(dict(floor=f,flight=flight,step=k+1,point=[xx,yy,zz],**q))
 for x,y,zz,label in [(8.4,9.11,z,'approach'),(4.7,9.11,mid,'mid_turn_rear'),(4.7,7.99,mid,'mid_turn_front'),(8.4,7.99,top,'arrival')]:
  q=ceiling(x,y,zz)
  if q:headroom.append(dict(floor=f,flight=label,point=[x,y,zz],**q))
mn=min(q['headroom_m'] for q in headroom)
add('Centreline_stair_headroom',mn>=2.0,minimum_m=mn,worst=sorted(headroom,key=lambda q:q['headroom_m'])[:5],method='Vertical intersections with actual static geometry at 40 tread centres plus 8 landing/approach centres; 2.0m geometric review threshold')

# Circle-clearance through the approach and arrival must have geometric gaps
# and not just clear centre points. Exclude handrails of own flight at mouth.
for f,z,top in [(1,0,3.9),(2,3.9,7.5)]:
 for dz in [.2,1.0,1.8]:
  add(f'Approach_body_clear_F{f}_{dz}',not wall_xy(f,z+dz).intersects(box(7.8,8.70,8.99,9.50)))
 for dz in [.2,1.0,1.8]:
  add(f'Arrival_body_clear_F{f+1}_{dz}',not wall_xy(f+1,top+dz).intersects(box(7.8,7.60,8.99,8.35)))

# Current default all room queries are rough review polygons and leave buffers
# at thresholds. Record this practical UE5 routing limitation candidly.
for f in [1,2]:
 rr=[r for r in S['rooms'] if r['floor']==f]
 for i,a in enumerate(rr):
  for b in rr[i+1:]:
   overlap=Polygon(a['review_polygon_xy_m']).intersection(Polygon(b['review_polygon_xy_m'])).area
   add('Room_polygon_overlap_'+a['room_id']+'_'+b['room_id'],overlap<1e-9,area_m2=overlap)

# Test the actual local leaf body at three intermediate swing states against
# walls, rather than assuming a mirrored angle always yields usable motion.
for r in S['door_registry']:
 if r['floor'] not in [1,2] or not r.get('leaf_element'):continue
 le=E[r['leaf_element']];zz=r['origin'][2]+1;polys=[]
 for p in S['definitions'][le['definition']]['parts']:
  g=p['geometry']
  if g['type']!='box':continue
  x,y,z=g['origin'];w,d,h=g['size']
  if z<1<h+z:polys.append(box(x,y,x+w,y+d))
 body=unary_union(polys);wall=wall_xy(r['floor'],zz)
 for fraction in [.25,.5,1]:
  ang=math.degrees(le['angle'])+le['open_angle_degrees_provisional']*fraction
  q=affinity.translate(affinity.rotate(body,ang,origin=(0,0)),le['origin'][0],le['origin'][1])
  ov=q.intersection(wall).area
  add(f'Leaf_swing_wall_clear_{r["door_id"]}_{fraction}',ov<1e-8,intersection_area_m2=ov,swing_fraction=fraction)

risks=[dict(severity='PROVISIONAL',scope='DOOR_KITCHEN_F1',issue='Panorama establishes a free stair mouth and more distant opposite frosted bathroom door; inherited-grid X9.1/Y8.6 door offset and compact room boundary are unmeasured candidates.',action='Collect door-to-corner offsets and washroom width/depth before claiming as-built metric accuracy.'),
       dict(severity='UE5_INTEGRATION',scope='Room query thresholds',issue='Rooms are review polygons with wall/threshold buffers, so a point exactly inside door opening may match no room.',action='Route queries through stable door/room IDs and portal transitions; do not require complete floor polygon coverage.'),
       dict(severity='UE5_INTEGRATION',scope='Collision and doors',issue='This audit checks geometric portals/headroom, not UE5 imported collision or animated door collision. Frosted leaves are closed solids until interaction animates them.',action='Use separated door leaf collision and static wall collision; run UE5 walk tests after import. Do not use a single convex hull for the stair/wall assembly.')]
report=dict(scene=str(P),scene_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL',checks=checks,headroom_samples=headroom,risks=risks,non_claims=['No UE5 collision test executed','No field-survey accuracy assertion','No approved construction or structural certification'])
(Path(__file__).parent/'Final_Merged_Interior_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(status=report['status'],checks=len(checks),failed=[c for c in checks if c['status']=='FAIL'],minimum_headroom_m=mn),ensure_ascii=False,indent=2))
