"""Traditional timber storage frame, open eave gallery and photo-proportioned stone guard."""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,LineString,box as sbox
B=Path(r'E:/jz/JIA/Rebuild_V17');D=W/'v17';S=json.loads((B/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
tree=ast.parse((W/'v14_building.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['part','beam','box']],type_ignores=[]),'<wood_helpers>','exec'))
rf=json.loads((W/'v14/Roof_Junction_QA.json').read_text(encoding='utf8'));cn=np.array(rf['inner_north_top_plane']);cs=np.array(rf['inner_south_top_plane'])
WOOD='M_V12_Kitchen_HONEY_WOOD';STONE='M_Stone';Q={'replace':[],'add':[],'part_edits':[]};QA={'source':'INSV 700, 705, 715, 725 seconds and user instruction','roof_planes_unchanged':rf,'gallery_width_m':1.30,'dimensions':'Photo fitted visible assembly; no independent site measurements'}
def ry(x):return float(-(cn[0]-cs[0])*x/(cn[1]-cs[1])-(cn[2]-cs[2])/(cn[1]-cs[1]))
def h(x,y):
 c=cs if y<ry(x) else cn;return float(c[0]*x+c[1]*y+c[2])
def put(n,parts,new=False,**meta):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}
 e.update(parts=parts,source=QA['source'],v17_storage_detail=True,dimension_status=QA['dimensions'],**meta);Q['add' if new else 'replace'].append(e);return e
def unite(parts,material):
 a=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in parts],mf.OpType.Add);assert not a.is_empty();return part(fromman(a),material)
def member(a,b,w,d,m=WOOD):return beam(a,b,w,d,m)
def column(x,y,z0,z1,r=.105):
 p=[[x+r*math.cos(t),y+r*math.sin(t),z0] for t in np.linspace(0,2*math.pi,20,endpoint=False)];return part({'type':'prism','profile':p,'vector':[0,0,z1-z0]},WOOD)

# Open the previously solid eave face. The other masonry faces and linked portals stay exact.
n='SITE_V14_INNER_STORAGE_MASONRY';e=copy.deepcopy(E[n]);old=e['parts'][2];e['parts']=[p for j,p in enumerate(e['parts']) if j!=2];e.update(v17_partwise=True,v17_repair='Solid eave-side masonry replaced by a timber entry front set back 1.30 m, leaving an open roof-covered gallery');Q['replace'].append(e);Q['part_edits'].append({'node':n,'native_name':n+'__3','part_index':2,'geometry':None,'material':old['material']})

# Main timber frames use stepped lifting beams and short posts below the existing fitted roof.
frames=[];supports=[];bases=[];records=[];xs=[13.74,15.90,18.50];ys=-15.92;yn=-10.13
for x in xs:
 ridge=ry(x);za=h(x,ys)-.22;zb=h(x,yn)-.22;tie=za-.16
 for y,z in [(ys,za),(yn,zb)]:
  supports.append(column(x,y,-.25,z+.075));bases.append(box(x-.18,y-.18,-.414,.36,.36,.17,STONE));records.append({'column':[x,y],'foot_z':-.25,'head_z':z+.075,'stone_base_top':-.244})
 frames.append(member([x,ys-.04,tie],[x,yn+.04,tie],.20,.24))
 # Lower and upper lifting beams bear on short posts seated on the previous beam.
 low_top=tie+.12;lifting_levels=[(ys-.04,yn+.04,low_top)]
 for dleft,dright in [(-2.55,1.50),(-1.05,.88)]:
  ya=ridge+dleft;yb=ridge+dright;zc=min(h(x,ya),h(x,yb))-.31
  frames.append(member([x,ya-.075,zc],[x,yb+.075,zc],.18,.20))
  for y in [ya,yb]:frames.append(member([x,y,low_top-.012],[x,y,zc+.012],.15,.15))
  low_top=zc+.10;lifting_levels.append((ya-.075,yb+.075,low_top))
 frames.append(member([x,ridge,low_top-.012],[x,ridge,h(x,ridge)-.19],.16,.16))
 # Every intermediate purlin bears on a short post seated on the highest beam below it.
 for dd in [-3.9,-2.5,-1.1,1.1,2.1]:
  yp=ridge+dd;zseat=max((z for a,b,z in lifting_levels if a-.10<=yp<=b+.10),default=tie+.12);zp=h(x,yp)-.205
  if zp>zseat+.01:frames.append(member([x,yp,zseat-.012],[x,yp,zp+.008],.12,.12))
 # Rear roof purlin has its own continuous bearing column, rather than a suspended spacer.
 for y,z in [(ys,za),(yn,zb)]:frames.append(box(x-.14,y-.16,z-.12,.28,.32,.18,WOOD))
for d in [-3.9,-2.5,-1.1,0,1.1,2.1]:
 a=[13.35,ry(13.35)+d,h(13.35,ry(13.35)+d)-.205];b=[18.9,ry(18.9)+d,h(18.9,ry(18.9)+d)-.205];frames.append(member(a,b,.16,.16))
for x in np.arange(13.4,18.97,.24):
 for y in [-16.4,-9.5]:frames.append(member([float(x),ry(x),h(x,ry(x))-.110],[float(x),y,h(x,y)-.110],.045,.06))
# Preserve the two fitted valley bearer members connecting to the original kitchen.
frames.extend(copy.deepcopy(E['SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME']['parts'][-2:]))
frontbeam=[]
frontbeam.append(member([13.48,ys,h(13.48,ys)-.22],[18.72,ys,h(18.72,ys)-.22],.18,.20))
for x in xs:
 for sign in [-1,1]:
  xx=x+sign*.42
  if 13.5<xx<18.7:frontbeam.append(member([x,ys,h(x,ys)-.67],[xx,ys,h(xx,ys)-.30],.075,.09))
frames.extend(frontbeam)
put('SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME',frames,classification='CHINESE_STEPPED_LIFTING_BEAMS_SHORT_POSTS_PURLINS_RAFTERS',v17_bearing='Six floor-supported timber columns and masonry gable supports; roof planes and valley unchanged',v17_frame_axes_x=xs)
put('SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES',supports+bases,True,classification='FLOOR_SUPPORTED_TIMBER_POSTS_ON_STONE_BASES',v17_columns=records)

# Gallery sits within the photographed roof silhouette, in front of a set-back timber enclosure.
put('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR',[box(13.35,-16.245,-.425,5.55,1.395,.031,STONE)],True,classification='OPEN_ROOF_COVERED_EAVE_GALLERY',v17_clear_depth_m=1.30,v17_entry_front_y=-14.85,v17_floor_level=-.394)
put('SITE_V17_STORAGE_VERANDA_EDGE_BASE',[box(13.35,-16.27,-4.45,5.55,.30,4.036,'M_Stone_Rubble')],True,classification='SUPPORTED_STONE_EDGE_UNDER_GALLERY_AND_GUARD')

# Timber front: paneled low sill, octagonal lattice windows and an open double leaf entry.
front=[];yf=-14.855;xl=13.63;xr=18.62;head=1.74;doora=15.60;doorb=16.65
for x in [xl,doora,doorb,xr]:front.append(box(x-.065,yf-.075,-.40,.13,.15,2.62,WOOD))
for z,ht in [(-.37,.08),(head,.12),(2.17,.11)]:
 if z<0:
  front.extend([box(xl,yf-.065,z,doora-xl,.13,ht,WOOD),box(doorb,yf-.065,z,xr-doorb,.13,ht,WOOD)])
 else:front.append(box(xl,yf-.07,z,xr-xl,.14,ht,WOOD))
for a,b in [(xl+.07,doora-.07),(doorb+.07,xr-.07)]:
 front.append(box(a,yf-.035,-.30,b-a,.07,.50,WOOD))
 # Vertical central subdivision gives the traditional two octagon window modules in each side bay.
 xm=(a+b)/2
 front.append(box(xm-.026,yf-.04,.20,.052,.08,1.49,WOOD))
 for aa,bb in [(a,xm-.025),(xm+.025,b)]:
  cx=(aa+bb)/2;cz=.94;rr=min((bb-aa)/2-.04,.36);q=[]
  for k in range(8):
   ang=math.pi/8+k*math.pi/4;q.append([cx+rr*math.cos(ang),yf,cz+rr*math.sin(ang)])
  for p0,p1 in zip(q,q[1:]+q[:1]):front.append(member(p0,p1,.032,.032))
  # Interlocking rectangular fretwork around the central octagon.
  for zz in [.28,.47,1.40,1.61]:front.append(box(aa,yf-.018,zz,bb-aa,.036,.026,WOOD))
  for xx in [aa+.08,bb-.08]:front.append(box(xx-.013,yf-.018,.20,.026,.036,1.49,WOOD))
  front.append(part({'type':'box','origin':[aa+.015,yf+.012,.23],'size':[bb-aa-.03,.010,1.42]},'M_Glass_Frosted'))
for a,b in zip([xl,doora,doorb],[doora,doorb,xr]):
 for xx in np.arange(a+.045,b-.02,.24):
  front.extend([box(float(xx),yf-.022,1.88,.026,.044,.30,WOOD),box(float(xx),yf-.022,1.98,min(.17,b-xx),.044,.026,WOOD)])
front.append(part({'type':'prism','profile':[[xl,yf-.035,2.25],[xr,yf-.035,2.25],[xr,yf-.035,h(xr,yf)-.095],[xl,yf-.035,h(xl,yf)-.095]],'vector':[0,.07,0]},WOOD))
# Leaves are shown open in the reference views. Their bottoms remain on the storage floor.
for hinge,side,angle in [(doora+.065,1,65),(doorb-.065,-1,-65)]:
 leaf=[box(0,-.035,-.392,(doorb-doora-.14)/2,.07,2.04,WOOD)]
 for z in [-.14,.64,1.48]:leaf.append(box(.052,-.043,z,(doorb-doora-.14)/2-.104,.086,.032,WOOD))
 a=math.radians(angle);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
 for p in leaf:
  v,fs,_,_=ex.solid_data(p['geometry']);v=np.array(v);v[:,0]*=side;v=v@R.T+np.array([hinge,yf,0]);g=oriented({'type':'polyhedron','vertices':v.tolist(),'faces':[list(f) for f in fs]});front.append(part(g,WOOD))
put('SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT',front,True,classification='TIMBER_PANEL_FRONT_WITH_OCTAGON_LATTICE_WINDOWS_AND_OPEN_DOUBLE_ENTRY',v17_setback_from_gallery_edge_m=1.345,v17_clear_entry_width_m=doorb-doora-.13)

# Hanging fretwork under the continuous eave beam, linked to its lower edge.
hang=[]
for aa,bb in zip(xs[:-1],xs[1:]):
 top=min(h(aa,ys),h(bb,ys))-.30;bot=top-.35
 hang.append(member([aa,ys,bot],[bb,ys,bot],.038,.038));hang.append(member([aa,ys,top],[bb,ys,top],.038,.038))
 for xx in np.arange(aa+.01,bb+.01,.30):
  xx=float(min(xx,bb));hang.append(member([xx,ys,bot],[xx,ys,top+.01],.032,.032))
  if xx+.18<bb:hang.append(member([xx,ys,bot+.13],[xx+.18,ys,bot+.13],.03,.03))
put('SITE_V17_STORAGE_VERANDA_EAVE_HANGING_LATTICE',hang,True,classification='WOOD_FRETWORK_HANGING_FROM_EAVE_BEAM')

# Stone rail: supported bases, framed relief panels, pierced hourglass balusters and square-capped posts.
def stone_guard(points):
 ps=[];postxy=[];bayrecords=[]
 for a,b in zip(points[:-1],points[1:]):
  a=np.array(a,float);b=np.array(b,float);d=b-a;L=np.linalg.norm(d);d/=L;nb=max(1,int(math.ceil(L/1.30)))
  for j in range(nb):
   p=a+d*(L*j/nb);q=a+d*(L*(j+1)/nb);postxy.extend([p,q]);ba=p+d*.06;bb=q-d*.06;mid=(ba+bb)/2
   ps.append(member([*ba,-.255],[*bb,-.255],.16,.13,STONE));ps.append(member([*ba,.50],[*bb,.50],.145,.10,STONE))
   # Solid relief panel has a visible inset frame; upper openings stay genuinely open.
   ps.append(member([*ba,.00],[*bb,.00],.075,.40,STONE))
   normal=np.array([-d[1],d[0]])
   for face in [-1,1]:
    oo=normal*face*.042
    for zz in [-.16,.16]:ps.append(member([*(ba+oo),zz],[*(bb+oo),zz],.025,.028,STONE))
    for tt in [.04,.96]:
     xy=ba+(bb-ba)*tt+oo;ps.append(member([*xy,-.16],[*xy,.16],.025,.027,STONE))
    # restrained shallow geometric relief avoids invented deep carved figures
    for s in [.3,.7]:
     xy=ba+(bb-ba)*s+oo;rr=.085
     pts=[[*(xy+d*rr),.00],[*xy,.105],[*(xy-d*rr),.00],[*xy,-.105]]
     for pp,qq in zip(pts,pts[1:]+pts[:1]):ps.append(member(pp,qq,.014,.014,STONE))
   for s in [.24,.5,.76]:
    xy=ba+(bb-ba)*s;perp=np.array([-d[1],d[0]])*.034
    profile=[[*(xy-d*.085-perp),.198],[*(xy+d*.085-perp),.198],[*(xy+d*.04-perp),.325],[*(xy+d*.085-perp),.452],[*(xy-d*.085-perp),.452],[*(xy-d*.04-perp),.325]]
    ps.append(part({'type':'prism','profile':profile,'vector':[*(perp*2),0]},STONE))
   bayrecords.append({'start':p.tolist(),'end':q.tolist(),'top_z':.55,'foot_z':-.40})
 unique={tuple(np.round(p,6)) for p in postxy}
 for x,y in unique:
  ps.extend([box(x-.11,y-.11,-.409,.22,.22,.14,STONE),box(x-.078,y-.078,-.285,.156,.156,.88,STONE),box(x-.092,y-.092,.57,.184,.184,.075,STONE)])
 return [unite(ps,STONE)],bayrecords
points=[[13.59,-16.10],[18.9,-16.2]];ps,br=stone_guard(points);put('SITE_V17_STORAGE_EAVE_GALLERY_STONE_GUARD',ps,True,classification='STONE_GUARD_WITH_RELIEF_PANELS_AND_PIERCED_BALUSTERS',v17_guard_line=points,v17_native_top=.645,v17_bays=br)
outer=[[18.9,-16.2],[20.2,-16.2],[21.30,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]];ps,br2=stone_guard(outer);put('SITE_V14_OUTER_STORAGE_STONE_BALUSTRADE',ps,classification='CONTINUOUS_STONE_GUARD_MATCHING_VERANDA_PROFILE',v17_guard_line=outer,v17_native_top=.645,v17_bays=br2)
QA['timber_columns']=records;QA['guard_bays']=br+br2;QA['replaced_eave_masonry_part']=2;QA['entry_clear_width_m']=doorb-doora-.13;QA['part_counts']={e['name']:len(e['parts']) for e in Q['replace']+Q['add']};QA['roof_and_portals_preserved']=True
(D/'Storage_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Storage_Geometry_QA.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8');print('V17 STORAGE READY',QA['part_counts'],flush=True)
