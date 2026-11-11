import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v3 as ex
from shapely.geometry import Polygon,box
E={e['name']:e for e in ex.SCENE['elements']}
def tris(e):
 t=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e)
  if v is None:continue
  for face in f:
   for j in range(1,len(face)-1):t.append(v[[face[0],face[j],face[j+1]]])
 return np.array(t)
def vertical(e,x,y):
 hits=[]
 for t in tris(e):
  a=t[0,:2];B=np.column_stack((t[1,:2]-a,t[2,:2]-a))
  if abs(np.linalg.det(B))<1e-10:continue
  q=np.linalg.solve(B,np.array([x,y])-a)
  if q.min()>=-1e-7 and q.sum()<=1+1e-7:hits.append(float(t[0,2]+q[0]*(t[1,2]-t[0,2])+q[1]*(t[2,2]-t[0,2])))
 return sorted(set(round(z,6) for z in hits))
def bb(e):
 v=np.vstack([ex.world_part(p,e)[0] for p in ex.expand_parts(e) if ex.world_part(p,e)[0] is not None]);return v.min(0),v.max(0)
R={'source':'E:/jz/JIA/Rebuild_V3/05_Intermediate/Architecture_Scene.json','units':'metres','method':'Analytic polygons for axis-aligned beam/wall volume; vertical face-triangle intersections for roof/top contact; source scene no mutations','wall_beam_overlaps':[],'roof_support_gaps':[],'roman_column_bearing':[],'ground_interface':[],'tile_wall_samples':[]}
# This is a physical-solid overlap, not contact faces, and geometry-derived not guessed.
for en,e in E.items():
 if not en.startswith(('FACADE_CONTINUOUS','PARTITIONS_JOINED')):continue
 for j,p in enumerate(e['parts']):
  g=p['geometry']
  if g['type']!='prism_holes':continue
  P=Polygon(g['outer'],g['holes']);za=g['z'];zb=za+g['height']
  for bn,b in E.items():
   if not bn.startswith('BEAM_'):continue
   for bpart in b['parts']:
    bg=bpart['geometry'];v,_=ex.world_part(bpart,b);lo=v.min(0);hi=v.max(0);h=min(zb,hi[2])-max(za,lo[2])
    if h<1e-7:continue
    A=P.intersection(box(*[lo[0],lo[1],hi[0],hi[1]])).area
    if A>1e-8:R['wall_beam_overlaps'].append({'wall':en,'wall_part_1based':j+1,'beam':bn,'overlap_area_m2':round(A,8),'overlap_height_m':round(h,8),'overlap_volume_m3':round(A*h,8)})
for k in [1,2,3]:
 pe=E[f'SITE_SHED_{k}_POSTS'];roof=E[f'SITE_SHED_{k}_ROOF']
 for j,p in enumerate(pe['parts']):
  v,_=ex.world_part(p,pe);lo=v.min(0);hi=v.max(0);x,y=(lo[:2]+hi[:2])/2;hits=vertical(roof,x,y)
  if hits:R['roof_support_gaps'].append({'lower_element':pe['name'],'part_1based':j+1,'roof':roof['name'],'xy':[round(float(x),5),round(float(y),5)],'support_top':float(hi[2]),'roof_bottom':hits[0],'gap_m':round(hits[0]-float(hi[2]),6)})
  for dx,dy in [(.2,0),(-.2,0),(0,.2),(0,-.2)]:
   hits=vertical(E['SITE_WEST_EARTH_COURTYARD'],x+dx,y+dy)
   if hits:R['ground_interface'].append({'element':pe['name'],'part_1based':j+1,'support_bottom':float(lo[2]),'soil_sample_xy':[round(float(x+dx),5),round(float(y+dy),5)],'soil_z':hits[0],'base_above_soil_m':round(float(lo[2])-hits[0],6)})
for lower,roof,points in [
 ('SITE_INNER_STONE_GATEHOUSE','SITE_INNER_GATEHOUSE_ROOF_CURVED_TILE_SHELL',[(5.1,-11.7),(6.6,-11.7),(8.1,-11.7)]),
 ('SITE_SOUTH_SCREENWALL_RAISED_BODY','SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL',[(3.45,-16.9),(6.6,-16.9),(10.6,-16.9)]),
 ('SITE_KITCHEN_GABLE_INFILL_-11.49','SITE_KITCHEN_CHINESE_TILE_ROOF',[(7.7,-11.4),(10.29,-11.4),(13.35,-11.4)]),
 ('SITE_KITCHEN_GABLE_INFILL_-2.71','SITE_KITCHEN_CHINESE_TILE_ROOF',[(7.7,-2.6),(10.29,-2.6),(13.35,-2.6)])]:
 for x,y in points:
  lo=vertical(E[lower],x,y);hi=vertical(E[roof],x,y)
  if lo and hi:R['roof_support_gaps'].append({'lower_element':lower,'roof':roof,'xy':[x,y],'support_top':lo[-1],'roof_bottom':hi[0],'gap_m':round(hi[0]-lo[-1],6)})
for z in [0,3.9]:
 arch=E[f'PORCH_ARCH_BEAM_Z{z}'];H=2.65 if z==0 else 2.9
 for x in [3.9,9.1]:
  pts=[]
  for dx in ([0,.05,.10,.15,.20] if x<6 else [-.20,-.15,-.10,-.05,0]):
   hit=vertical(arch,x+dx,0)
   if hit:pts.append({'dx':dx,'capital_top':z+H,'arch_bottom':hit[0],'vertical_gap_m':round(hit[0]-(z+H),6)})
  R['roman_column_bearing'].append({'column':f'ROMAN_COLUMN_X{x}_Z{z}','arch':arch['name'],'capital_flat_top_radius':.205,'samples':pts,'contact_area_claim':'At current spring point only a line at x=column centre touches flat capital. No finite horizontal bearing seat modelled.'})
for name in ['SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_WHITE_INSIDE','SITE_GATE_EAST_FLANK']:
 pts=[(0,-10),(0,-5),(0,.5)] if name=='SITE_COURTYARD_WEST_TILE_WALL' else [(8.4,-11.7),(10.7,-11.7),(13.2,-11.7)] if name=='SITE_GATE_EAST_FLANK' else [(.133,-10),(.133,-5),(.133,.5)]
 for x,y in pts:R['tile_wall_samples'].append({'element':name,'xy':[x,y],'vertical_extents':vertical(E[name],x,y)})
R['summary']={'wall_beam_overlap_records':len(R['wall_beam_overlaps']),'wall_beam_overlap_volume_m3':round(sum(i['overlap_volume_m3'] for i in R['wall_beam_overlaps']),6),'largest_roof_gap_m':max(i['gap_m'] for i in R['roof_support_gaps'])}
(W/'v4_audit_junction/Junction_Audit_V3.json').write_text(json.dumps(R,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in R.items() if k not in ['wall_beam_overlaps','ground_interface']},indent=2));print('Ground interface extremes',min(i['base_above_soil_m'] for i in R['ground_interface']),max(i['base_above_soil_m'] for i in R['ground_interface']))
