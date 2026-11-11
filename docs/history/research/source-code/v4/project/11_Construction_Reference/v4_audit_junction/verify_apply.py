import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v3 as ex
src=(W/'v4_audit_junction/audit.py').read_text(encoding='utf-8-sig')
start=src.index('def tris(');stop=src.index("R={'source'")
ex.SCENE=json.loads((W/'v4_audit_junction/Scene_Repair_Test.json').read_text(encoding='utf-8'));E={e['name']:e for e in ex.SCENE['elements']}
exec(src[start:stop])
report={'roof_support_chain':[],'arch_end_bearing':[],'bathroom_openings':[],'wall_beam_overlap_volume':0}
for i in [1,2,3]:
 post=E[f'SITE_SHED_{i}_POSTS'];beam=E[f'SITE_SHED_{i}_CONTINUOUS_SUPPORT_BEAMS'];roof=E[f'SITE_SHED_{i}_ROOF']
 for j,p in enumerate(post['parts']):
  v,f=ex.world_part(p,post);xy=np.mean(v[:4,:2],axis=0);pv=vertical(post,*xy);bv=vertical(beam,*xy);rv=vertical(roof,*xy)
  report['roof_support_chain'].append({'group':post['name'],'column_1based':j+1,'xy':xy.tolist(),'post_to_beam_gap':round(bv[0]-pv[-1],8),'beam_to_roof_gap':round(rv[0]-bv[-1],8)})
for a,b,c in [('SITE_INNER_STONE_GATEHOUSE','SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE','SITE_INNER_GATEHOUSE_ROOF_CURVED_TILE_SHELL'),('SITE_SOUTH_SCREENWALL_RAISED_BODY','SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE','SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL')]:
 for xy in [(6.6,-11.7)] if 'GATEHOUSE' in a else [(6.6,-16.9)]:
  av=vertical(E[a],*xy);bv=vertical(E[b],*xy);cv=vertical(E[c],*xy)
  report['roof_support_chain'].append({'group':a,'xy':xy,'lower_to_base_gap':round(bv[0]-av[-1],8),'base_to_roof_gap':round(cv[0]-bv[-1],8)})
for z in [0,3.9]:
 for x in [3.9,9.1]:
  report['arch_end_bearing'].append({'arch':f'PORCH_ARCH_BEAM_Z{z}','column':f'ROMAN_COLUMN_X{x}_Z{z}','sample_xy':[x,.18],'capital_top':z+(2.65 if z==0 else 2.90),'enlarged_seat_bottom':vertical(E[f'PORCH_ARCH_BEAM_Z{z}'],x,.18)[0]})
for floor,z in [(2,3.9),(3,7.5)]:
 e=E[f'PARTITIONS_JOINED_F{floor}'];report['bathroom_openings'].append({'floor':floor,'closed_old_y_wall':vertical(e,12.3,7.3),'new_x_wall_opening':vertical(e,10.8,8.05),'door_origin':E[f'DOOR_BATH_F{floor}_R']['origin']})
# Exact axis-aligned wall/beam volume.
from shapely.geometry import Polygon,box
for e in ex.SCENE['elements']:
 if not e['name'].startswith(('FACADE_CONTINUOUS','PARTITIONS_JOINED')):continue
 for p in e['parts']:
  g=p['geometry'];P=Polygon(g['outer'],g['holes']);za=g['z'];zb=za+g['height']
  for b in ex.SCENE['elements']:
   if not b['name'].startswith('BEAM_'):continue
   for bp in b['parts']:
    v,f=ex.world_part(bp,b);lo=v.min(0);hi=v.max(0);h=min(zb,hi[2])-max(za,lo[2])
    if h>1e-7:report['wall_beam_overlap_volume']+=P.intersection(box(lo[0],lo[1],hi[0],hi[1])).area*h
report['wall_beam_overlap_volume']=round(report['wall_beam_overlap_volume'],12)
(W/'v4_audit_junction/Interface_Repair_Check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
assert report['wall_beam_overlap_volume']<1e-8
assert all(abs(v)<1e-7 for row in report['roof_support_chain'] for k,v in row.items() if k.endswith('_gap'))
assert all(abs(row['capital_top']-row['enlarged_seat_bottom'])<1e-7 for row in report['arch_end_bearing'])
