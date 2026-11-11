import sys,json,math,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v4_audit_junction')]
import numpy as np
from shapely.geometry import Polygon,box as rect
from shapely.ops import unary_union
import apply_junction_v4 as J
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';S=json.loads(p.read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']};delta=[];removed=[]
for e in list(S['elements']):
 if e['name'].startswith('BALCONY_STONE_PANEL_MOULDING_'):
  S['elements'].remove(e);removed.append(e['name']);S['v7_retired_elements'].append(e)
def add(name,layer,parts,refs,**kw):
 e=dict(name=name,layer=layer,family='ARCH_MODEL',parts=parts,confidence='MEDIUM',source='; '.join(refs),status='PHOTO_VISIBLE_DETAIL; DIMENSION_PROFILES_PROVISIONAL',**kw);S['elements'].append(e);delta.append(name);return e
def bp(x,y,z,w,d,h,m):return J._part(J._box(x,y,z,w,d,h),m)
# Pierced lozenge railing crown in the terrace photographs, retain only the
# lower solid wall. Each small opening is real geometry, not an alpha map.
e=E['TERRACE_STONE_PARAPET'];g=copy.deepcopy(e['parts'][0]['geometry']);g['height']=.94;e['parts']=[J._part(g,'M_Wall_Exterior')];e['source']='DJI 0002 0623 and panorama 200s: lower ceramic-faced solid wall, pierced upper crown';delta.append(e['name'])
bars=[];joints=[];paths=[([.1,1.1],[3.7,1.1]),([0,1.2],[0,7.25])]
for aa,bb in paths:
 aa=np.array(aa);bb=np.array(bb);L=np.linalg.norm(bb-aa);u=(bb-aa)/L;n=np.array([-u[1],u[0]])
 def extr(s0,s1,z,h,d):
  q=[[*aa+u*s0-n*d/2,z],[*aa+u*s1-n*d/2,z],[*aa+u*s1+n*d/2,z],[*aa+u*s0+n*d/2,z]]
  return J._part({'type':'prism','profile':q,'vector':[0,0,h]},'M_Stone')
 bars += [extr(0,L,8.44,.028,.10),extr(0,L,8.635,.05,.14)]
 for st in np.arange(.105,L-.09,.21):
  corners=[(st-.092,8.55),(st,8.468),(st+.092,8.55),(st,8.632)]
  for (s0,z0),(s1,z1) in zip(corners,corners[1:]+corners[:1]):
   v=np.array([s1-s0,z1-z0]);perp=np.array([-v[1],v[0]]);perp=perp/np.linalg.norm(perp)*.011
   prof=[]
   for sx,zz in [(s0+perp[0],z0+perp[1]),(s1+perp[0],z1+perp[1]),(s1-perp[0],z1-perp[1]),(s0-perp[0],z0-perp[1])]:prof.append([*aa+u*sx-n*.04,zz])
   bars.append(J._part({'type':'prism','profile':prof,'vector':[*n*.08,0]},'M_Stone'))
 # Thin grout runs on the solid ceramic face, observed horizontal courses.
 for z in [7.90,8.30]:joints.append(extr(0,L,z,.002,.205))
add('TERRACE_PHOTO_PIERCED_CROWN','41_RAILING',bars,['DJI 0002/DJI_0623.JPG','Panorama 200s'],pierced=True,profile_dimension_status='PHOTO_ESTIMATED')
supports=[]
for yy in [3.45,5.75]:supports.append(bp(-.025,yy-.025,7.5,.05,.05,10.17+(yy-1)*.18/5.65-7.5,'M_Metal_Black'))
for yy in [1.1,3.45]:supports.append(bp(-.025,yy,8.98,.05,2.3,.035,'M_Metal_Black'))
add('TERRACE_CANOPY_WEST_SUPPORTS','51_CANOPY',supports,['DJI 0002/DJI_0623.JPG','Panorama 200s'])
# Individually editable exposed grey-brick faces on the southeast annex only.
# Plastered walls/Chinese timber/screenwall panels are not assigned masonry.
bricks=[];count=0;wall=E['SITE_SOUTH_EAST_ANNEX_WALLS'];ranges=sorted({z for p0 in wall['parts'] for z in [p0['geometry']['z'],p0['geometry']['z']+p0['geometry']['height']]})
outer=[([13.8,-16.2],[13.8,-9.7],[-1,0]),([13.8,-9.7],[18.9,-9.7],[0,1]),([18.9,-9.7],[18.9,-16.2],[1,0]),([18.9,-16.2],[13.8,-16.2],[0,-1])]
course=.073;length=.265
for row,z in enumerate(np.arange(min(ranges),max(ranges)-.001,course)):
 h=min(.065,max(ranges)-z-.004)
 if h<=.001:continue
 mid=z+h/2;mask=unary_union([Polygon(g['outer'],g['holes']) for pp in wall['parts'] if (g:=pp['geometry'])['z']-1e-8<mid<g['z']+g['height']+1e-8])
 for aa,bb,nn in outer:
  aa=np.array(aa,float);bb=np.array(bb,float);n=np.array(nn,float);u=(bb-aa)/np.linalg.norm(bb-aa);L=np.linalg.norm(bb-aa)
  for st in np.arange(-length/2 if row%2 else 0,L,length):
   lo=max(.004,st+.004);hi=min(L-.004,st+length-.004)
   if hi<=lo:continue
   q=[aa+u*lo-n*.008,aa+u*hi-n*.008,aa+u*hi+n*.003,aa+u*lo+n*.003];foot=Polygon(q).intersection(mask.buffer(.003,join_style=2))
   pieces=J._prisms(foot,z+.004,h,'M_Grey_Brick');bricks+=pieces;count+=len(pieces)
add('ANNEX_EXPOSED_GREY_BRICK_UNITS','60_SITE',bricks,['DJI 0002/DJI_0508.JPG','DJI 0002/DJI_0509.JPG'],brick_units=count,unit_dimensions_provisional_m=[.257,.065],joint_spacing_provisional_m=[.008,.008],scope='Only visible grey masonry of annex; donor hole clipping governs final hybrid')
S['v7_changes'] += [dict(id='V7_TERRACE_RAIL_DETAIL',elements=['TERRACE_STONE_PARAPET','TERRACE_PHOTO_PIERCED_CROWN','TERRACE_CANOPY_WEST_SUPPORTS'],description='按照片补充阳台下部实墙、上部透空菱形栏带及雨棚西侧支承',evidence=['DJI 0002/DJI_0623.JPG','Panorama 200s'],metric_status='PHOTO_ESTIMATED'),dict(id='V7_EXPOSED_BRICK_DETAIL',elements=['ANNEX_EXPOSED_GREY_BRICK_UNITS'],description='东南附房裸露灰砖面细化为独立砖件，灰缝与错缝独立可见；白灰墙、木构和照壁不改成砖墙',evidence=['DJI 0002/DJI_0508.JPG'],metric_status='PHOTO_ESTIMATED; NOT_SURVEYED_BRICK_COUNT',brick_units=count)]
S['v7_detail_counts']['exposed_grey_brick_face_units']=count
p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8');(O/'06_Report/Changes_V7.json').write_text(json.dumps(S['v7_changes'],ensure_ascii=False,indent=2),encoding='utf-8')
c=json.loads((O/'02_Data/V7_Changed_Nodes.json').read_text());c['changed']=list(dict.fromkeys(c['changed']+delta));c['removed']=list(dict.fromkeys(c['removed']+removed));(O/'02_Data/V7_Changed_Nodes.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
(O/'02_Data/V7_Incremental_Nodes.json').write_text(json.dumps(dict(changed=delta,removed=removed),indent=2),encoding='utf-8')
print('Detail added',count,'individual grey bricks;',len(bars),'pierced crown members',flush=True)
