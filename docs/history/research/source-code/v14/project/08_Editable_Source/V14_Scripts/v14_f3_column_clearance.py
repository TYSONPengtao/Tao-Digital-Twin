import sys,json,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
from shapely.geometry import Polygon,box
Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));E={e['name']:e for e in Q['replace']+Q['add']}
e=E['PARTITIONS_JOINED_F3'];ps=[]
for p in e['parts']:
 g=p['geometry'];p=copy.deepcopy(p);g=p['geometry']
 if g['type']=='box' and abs(g['origin'][1]-6.10)<1e-6:g['origin'][1]-=.15
 if g['type']=='prism_holes' and g['z']<9.6:
  poly=Polygon(g['outer'],g['holes']).difference(box(3.79,6.15,4.01,7.05));qq=[poly] if poly.geom_type=='Polygon' else [q for q in poly.geoms if q.geom_type=='Polygon']
  for q in qq:
   if q.area>1e-10:
    gg=copy.deepcopy(g);gg['outer']=list(q.exterior.coords)[:-1];gg['holes']=[list(r.coords)[:-1] for r in q.interiors];ps.append({'geometry':gg,'material':p['material']})
 else:ps.append(p)
ps.append({'geometry':{'type':'box','origin':[3.8,7.05,7.5],'size':[.20,.15,2.1]},'material':e['parts'][0]['material']});e['parts']=ps;e['v14_circulation']='Floor-supported hall y6.15..7.30; terrace opening y6.15..7.05 clear of retained column y7.10..7.50'
for n,dy in [('DOOR_LAUNDRY_F3__FRAME',-.15),('DOOR_LAUNDRY_F3__LEAF',-.15),('DOOR_STUDY_F3__FRAME',-.05),('DOOR_STUDY_F3__LEAF',-.05)]:
 e=E[n];e['origin'][1]+=dy
 for k in ['pivot_world_m','hinge_origin_local_m']:
  if k in e:e[k][1]+=dy
e=E['TERRACE_SIDE_CERAMIC_PANEL_GRID'];ps=[]
for p in e['parts']:
 g=p['geometry']
 # Panels are small boxes. The lower opening edge crosses just one tile column.
 if g['type']=='box':
  x,y,z=g['origin'];w,d,h=g['size']
  if x<4.05 and x+w>3.6 and y<7.05 and y+d>6.15 and z<9.61 and z+h>7.48:
   # Only remove rectangular pieces within the opening; preserve trimmed ends.
   for yy,dd in [(y,max(0,6.15-y)),(max(y,7.05),max(0,y+d-max(y,7.05)))]:
    if dd>1e-8:
     gg=copy.deepcopy(g);gg['origin'][1]=yy;gg['size'][1]=dd;ps.append({'geometry':gg,'material':p['material']})
   continue
 ps.append(p)
ps.append({'geometry':{'type':'box','origin':[3.792,7.05,7.50],'size':[.008,.148,2.10]},'material':e['parts'][0]['material']});e['parts']=ps
Q['circulation']['route_local_xy']=[[8.45,6.60],[7.8,6.60],[5.2,6.60],[3.9,6.60],[3.3,6.60]];Q['circulation']['clear_width_m']=1.15;Q['circulation']['exit_revised_y']=6.15;Q['circulation']['column_clearance_y_m']=.05;Q['circulation']['stair_geometry_unchanged']=True
(W/'v14/Building_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('CLEAR EXIT: 6.15..7.05; original column starts 7.10; hall 1.15m',flush=True)
