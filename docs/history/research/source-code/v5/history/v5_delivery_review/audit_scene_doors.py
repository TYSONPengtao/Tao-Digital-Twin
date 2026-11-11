"""Read-only V5 leaf/frame pivot and swing clearance audit."""
import sys,json,math,copy
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W),str(W/'geomlibs'),str(W/'np1'),str(W/'libs')]
from shapely.geometry import box,Polygon,LineString
from shapely.affinity import rotate,translate
from scipy.integrate import quad
import v2_geometry
OUT=Path(r'E:\jz\JIA\Rebuild_V5')
S=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
E={e['name']:e for e in S['elements']}

def world_box(g,e,extra_rotation=0):
    x,y,z=g['origin'];w,d,h=g['size'];p=box(x,y,x+w,y+d)
    if extra_rotation:p=rotate(p,extra_rotation,origin=(0,0))
    p=rotate(p,math.degrees(e.get('angle',0)),origin=(0,0))
    origin=e.get('origin',[0,0,0])
    p=translate(p,origin[0],origin[1])
    return p,z+origin[2],z+origin[2]+h

def collision(frame,leaf,angle,axis_y_offset=0):
    leaf=copy.deepcopy(leaf)
    if axis_y_offset:
        a=leaf.get('angle',0)
        leaf['origin'][0]-=math.sin(a)*axis_y_offset
        leaf['origin'][1]+=math.cos(a)*axis_y_offset
    parts_f=[world_box(p['geometry'],frame) for p in S['definitions'][frame['definition']]['parts']]
    parts_l=[]
    for part in S['definitions'][leaf['definition']]['parts']:
        g=copy.deepcopy(part['geometry']);g['origin'][1]-=axis_y_offset
        parts_l.append(world_box(g,leaf,angle))
    return sum(p.intersection(q).area*max(0,min(b,d)-max(a,c))
               for p,a,b in parts_f for q,c,d in parts_l)

results=[]
obstacles=[]
for e in S['elements']:
    if e['layer'] not in ['11_WALL_INT','20_COLUMN','40_STAIR']:continue
    parts=S['definitions'][e['definition']]['parts'] if 'definition' in e else e['parts']
    for i,part in enumerate(parts):
        g=part['geometry'];typ=g['type']
        if typ=='box':
            p,a,b=world_box(g,e)
            obstacles.append({'name':e['name'],'part':i,'layer':e['layer'],'type':'VERTICAL','p':p,'a':a,'b':b})
        elif typ=='prism_holes':
            p=Polygon(g['outer'],g['holes']);p=rotate(p,math.degrees(e.get('angle',0)),origin=(0,0))
            t=e.get('origin',[0,0,0]);p=translate(p,t[0],t[1])
            obstacles.append({'name':e['name'],'part':i,'layer':e['layer'],'type':'VERTICAL','p':p,'a':g['z']+t[2],'b':g['z']+g['height']+t[2]})
        elif typ=='prism':
            # Current stairs are an XZ stepped profile, extruded along +Y.
            assert abs(g['vector'][0])+abs(g['vector'][2])<1e-8 and abs(e.get('angle',0))<1e-8
            profile=Polygon([(v[0],v[2]) for v in g['profile']]);x0,a,x1,b=profile.bounds
            y0=g['profile'][0][1];y1=y0+g['vector'][1]
            obstacles.append({'name':e['name'],'part':i,'layer':e['layer'],'type':'STAIR_XZ',
                              'p':box(x0,min(y0,y1),x1,max(y0,y1)),'a':a,'b':b,'profile':profile,'y':[min(y0,y1),max(y0,y1)]})
        elif typ=='lathe':
            verts,faces,*_=v2_geometry.data(g)
            t=e.get('origin',[0,0,0]);mins=verts.min(axis=0);maxs=verts.max(axis=0)
            obstacles.append({'name':e['name'],'part':i,'layer':e['layer'],'type':'LATHE_BBOX',
                'p':box(mins[0]+t[0],mins[1]+t[1],maxs[0]+t[0],maxs[1]+t[1]),'a':mins[2]+t[2],'b':maxs[2]+t[2]})
        else:raise ValueError('Unsupported obstacle '+typ)

def obstacle_collisions(leaf,angle):
    hits=[];candidate_count=0;integrated_stair_checks=0
    for part in S['definitions'][leaf['definition']]['parts']:
        p,a,b=world_box(part['geometry'],leaf,angle)
        for fixed in obstacles:
            lo,hi=max(a,fixed['a']),min(b,fixed['b'])
            if hi-lo<=1e-8:continue
            footprint=p.intersection(fixed['p'])
            if footprint.is_empty or footprint.area<=1e-10:continue
            candidate_count+=1
            if fixed['type']=='VERTICAL':volume=footprint.area*(hi-lo)
            elif fixed['type']=='LATHE_BBOX':
                raise ValueError('Lathe bbox overlaps leaf; needs exact lathe cross-section check '+fixed['name'])
            else:
                integrated_stair_checks+=1
                xlo,_,xhi,_=fixed['profile'].bounds
                def area_at(z):
                    sliced=fixed['profile'].intersection(LineString([(xlo-1,z),(xhi+1,z)]))
                    segments=list(sliced.geoms) if hasattr(sliced,'geoms') else [sliced]
                    total=0
                    for seg in segments:
                        if seg.is_empty or seg.geom_type not in ('LineString','LinearRing'):continue
                        xs=[q[0] for q in seg.coords]
                        if max(xs)-min(xs)>1e-10:
                            total+=p.intersection(box(min(xs),fixed['y'][0],max(xs),fixed['y'][1])).area
                    return total
                cuts=sorted({lo,hi}|{z for x,z in fixed['profile'].exterior.coords if lo<z<hi})
                volume=sum(quad(area_at,c,d,epsabs=1e-10,epsrel=1e-7,limit=80)[0] for c,d in zip(cuts[:-1],cuts[1:]))
            if volume>1e-8:hits.append({'obstacle':fixed['name'],'part':fixed['part'],'layer':fixed['layer'],'overlap_m3':volume})
    return {'angle_deg':angle,'bbox_candidates':candidate_count,'stair_section_integrals':integrated_stair_checks,'collisions':hits}
for reg in S['door_registry']:
    if not reg.get('leaf_element'):continue
    frame=E[reg['frame_element']];leaf=E[reg['leaf_element']]
    assert frame['door_id']==leaf['door_id']==reg['door_id']
    assert leaf['pivot_local_m']==[0,0,0]
    assert max(abs(x-y) for x,y in zip(leaf['origin'],reg['hinge_world_m']))<1e-8
    sign=1 if leaf.get('open_angle_degrees_provisional',90)>0 else -1
    samples=[{'angle_deg':sign*d,'frame_intersection_volume_m3':collision(frame,leaf,sign*d)}
             for d in range(0,91)]
    obstacle_samples=[obstacle_collisions(leaf,sign*d) for d in [0,30,60,90]]
    results.append({'door_id':reg['door_id'],'frame':frame['name'],'leaf':leaf['name'],
                    'pivot_world_m':leaf['origin'],'registered':True,
                    'closed_intersection_volume_m3':samples[0]['frame_intersection_volume_m3'],
                    'swing_samples':samples,'swing_collision':any(x['frame_intersection_volume_m3']>1e-8 for x in samples),
                    'obstacle_samples':obstacle_samples})
report={'scope':'V5 scene closed geometry and provisional interactive swing: frame every degree 0..90, interior walls/columns/stairs at 0/30/60/90. Vertical intersections exact, sloped stair XZ profiles by integrated horizontal cross-sections. Does not confirm real-world handedness or furniture clearances.',
        'registered_hinged_doors':len(results),'closed_collision_doors':sum(r['closed_intersection_volume_m3']>1e-8 for r in results),
        'swing_collision_doors':sum(r['swing_collision'] for r in results),
        'obstacle_collision_doors':sum(any(a['collisions'] for a in r['obstacle_samples']) for r in results),
        'results':results}
(OUT/'09_Report/Door_Pivot_Scene_Audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'registered_hinged_doors':len(results),'closed_collision_doors':report['closed_collision_doors'],
                  'swing_collision_doors':report['swing_collision_doors'],
                  'max_swing_overlap_m3':max(x['frame_intersection_volume_m3'] for r in results for x in r['swing_samples']),
                  'obstacle_collision_doors':report['obstacle_collision_doors'],
                  'obstacle_collisions':[{'door':r['door_id'],**a} for r in results for a in r['obstacle_samples'] if a['collisions']]},indent=2))
