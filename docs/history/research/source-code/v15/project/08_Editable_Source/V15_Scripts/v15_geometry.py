import sys,json,copy,math,ast,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,LineString,Point,box as sb
from shapely.ops import unary_union
B=Path(r'E:/jz/JIA/Rebuild_V14');M=W/'v15';D=M/'data';D.mkdir(exist_ok=True);S=json.loads((B/'08_Editable_Source/Architecture_Scene_V14.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:copy.deepcopy(e) for e in S['elements']};I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'))};rep={};new={};rem=set();qa={}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
def p(g,m):return {'geometry':g,'material':m}
def bx(x,y,z,w,d,h,m='M_Wall_Interior'):return p({'type':'box','origin':[x,y,z],'size':[w,d,h]},m)
def put(n,ps,layer='60_SITE',**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':layer,'family':'SITE_MODEL','confidence':'MEDIUM'}));e['parts']=ps;e.update(meta);e['source']='INSV 160/235/265/674/700/725/749/775/950/972 seconds; user problem photos 2026-10-12';(rep if n in E else new)[n]=e;E[n]=e;return e
def polys(g):return [g] if g.geom_type=='Polygon' else [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon']
def beam(a,b,w,h,mat):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1]);v=np.array([1.,0,0]) if np.linalg.norm(v)<1e-8 else v/np.linalg.norm(v);n=np.cross(u,v);q=np.array([a-v*w/2-n*h/2,a+v*w/2-n*h/2,a+v*w/2+n*h/2,a-v*w/2+n*h/2]);return p({'type':'prism','profile':q.tolist(),'vector':(b-a).tolist()},mat)
# Cut the second-floor porch roof back to the exterior of the third-floor right bay.
# This is the roof fragment visible above the bedroom floor in the supplied screenshot.
bedpoly=Polygon([[9.10,2.10],[9.80,1.10],[12.30,1.10],[13.0,2.10],[13.0,10.0],[9.10,10.0]]).buffer(.055,join_style=2)
cut=manifold({'type':'prism_holes','outer':list(bedpoly.exterior.coords)[:-1],'holes':[],'z':7.25,'height':3.50});cutrows=[]
for n in ['CANOPY_CENTER_0','CANOPY_CENTER_1','CANOPY_CENTER_INDIVIDUAL_COVER_TILES','CANOPY_CENTER_RIDGE_CAP','CANOPY_FRONT_CLOSED_GABLE']:
 ps=[];count=0;removed=0
 for pp in E[n]['parts']:
  v,_=ex.world_part(pp,E[n]);poly=Polygon(v[:,:2]).convex_hull
  if not poly.intersects(bedpoly) or poly.intersection(bedpoly).area<1e-10:ps.append(pp);continue
  mm=manifold(pp['geometry']);rr=mm-cut
  if abs(mm.volume()-rr.volume())<1e-10:ps.append(pp);continue
  count+=1;removed+=mm.volume()-rr.volume()
  if not rr.is_empty():ps.append(p(fromman(rr),pp['material']))
 if count:put(n,ps,layer=E[n]['layer'],v15_fix='Right bay interior excluded from porch roof');cutrows.append({'node':n,'cut_parts':count,'removed_volume_m3':removed})
qa['bedroom_roof_cut']=cutrows;qa['bedroom_exclusion_xy']=list(bedpoly.exterior.coords)[:-1]
# Make hard wall faces flat, and give the actual outer wall grey brick with a separate white inside finish.
wallmask=[];inside=[];wc=[]
sitecenter=np.array([-3.5,-3.0])
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 e=E[n];ps=[];changed=0
 for pp in e['parts']:
  g=pp['geometry'];v,fs,_,_=ex.solid_data(g);wallmask.append(Polygon(v[:,:2]).convex_hull.buffer(.23,join_style=2));qq=copy.deepcopy(pp)
  if pp['material']=='M_Wall_Exterior':
   qq['material']='M_Grey_Brick';changed+=1;candidates=[]
   for f in fs:
    q=v[f];nn=np.cross(q[1]-q[0],q[2]-q[0]);nn/=np.linalg.norm(nn)+1e-30
    if abs(nn[2])<.35 and np.dot(nn[:2],sitecenter-q.mean(0)[:2])>0:
     area=np.linalg.norm(np.sum(np.cross(q,np.roll(q,-1,axis=0)),axis=0))/2;candidates.append((area,q,nn))
   if candidates:
    _,q,nn=max(candidates,key=lambda r:r[0]);inside.append(p({'type':'prism','profile':q.tolist(),'vector':(nn*.013).tolist()},'M_Wall_Exterior'))
  ps.append(qq)
 put(n,ps,v15_fix='Actual grey-brick exterior, existing stone base, separate inside plaster; flat surface normals applied in native writer');wc.append({'node':n,'upper_brick_parts':changed})
put('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH',inside)
qa['wall_finishes']=wc;qa['inside_finish_parts']=len(inside)
# A single continuous pavement connects the inner end of the existing gate ramp to the inner stone gate.
rd=np.load(B/'02_Data'/I['SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP']['file']);rv=rd['vertices'];rf=rd['faces'];rt=rv[rf];nr=np.cross(rt[:,1]-rt[:,0],rt[:,2]-rt[:,0]);ramp=unary_union([Polygon(t[:,:2]) for t in rt[nr[:,2]>1e-8]]).buffer(0)
centerline=LineString([[-12.8,-10.30],[-9.5,-11.35],[-3.0,-12.70],[3.0,-12.70],[6.60,-12.70],[6.60,-10.90]])
walk=centerline.buffer(1.30,cap_style=2,join_style=2).union(sb(-14.05,-12.48,-11.88,-8.22)).difference(ramp).buffer(0)
wallunion=unary_union(wallmask).buffer(0);walk=walk.difference(wallunion).buffer(0)
# Exclude gate pillars; their threshold remains a continuous floor across the clear doorway.
walk=walk.difference(sb(4.82,-12.00,5.30,-11.40)).difference(sb(7.90,-12.00,8.38,-11.40)).buffer(0)
route_anchors=np.array([[0,-.940],[3.46,-.730],[10.1,-.535],[16.1,-.470],[19.7,-.450],[21.5,-.450]])
def height(x,y):
 ss=centerline.project(Point(float(x),float(y)));z=float(np.interp(ss,route_anchors[:,0],route_anchors[:,1]))
 # Fit exact heights to the original ramp's inner boundary for the first transition.
 dist=ramp.boundary.distance(Point(float(x),float(y)))
 if dist<1.0:
  ids=np.argsort(np.linalg.norm(rv[:,:2]-[x,y],axis=1))[:12];pts=rv[ids];top=pts[pts[:,2]>pts[:,2].max()-.10]
  if len(top)>=3:
   aa=np.c_[top[:,:2],np.ones(len(top))];c=np.linalg.lstsq(aa,top[:,2],rcond=None)[0];zz=float(np.dot([x,y,1],c));w=max(0,1-dist);z=z*(1-w)+zz*w
 return z
vs=[];fs=[]
for poly in polys(walk):
 # Densify before triangulation so grade changes are represented, without a flat spanning plate.
 poly=shapely.segmentize(poly,.40)
 for tri in shapely.constrained_delaunay_triangles(poly).geoms:
  xy=np.array(tri.exterior.coords[:-1]);q=np.c_[xy,[height(x,y) for x,y in xy]]
  if np.cross(q[1]-q[0],q[2]-q[0])[2]<0:q=q[::-1]
  k=len(vs);vs.extend(q.tolist());fs.append([k,k+1,k+2])
vv=np.array(vs);ff=np.array(fs,np.int32);q,iv=np.unique(np.round(vv,7),axis=0,return_inverse=True);ff=iv[ff];N=len(q);bottom=q.copy();bottom[:,2]-=.22;allf=ff.tolist()+(ff[:,::-1]+N).tolist();edges=collections.Counter(tuple(sorted((int(a),int(b)))) for t in ff for a,b in zip(t,np.roll(t,-1)));orient={tuple(sorted((int(a),int(b)))):(int(a),int(b)) for t in ff for a,b in zip(t,np.roll(t,-1))}
for ed,c in edges.items():
 if c==1:
  a,b=orient[ed];allf.extend([[b,a,a+N],[b,a+N,b+N]])
put('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT',[p({'type':'mesh','vertices':np.vstack([q,bottom]).tolist(),'faces':allf},'M_V12_Road_Concrete')],classification='CONTINUOUS_PHOTO_REFERENCED_WALKING_ROUTE',grade_anchors=route_anchors.tolist())
# Fill and smooth the old depression beneath and immediately beside the new path.
groundrows=[]
for n in [n for n in E if n.startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD'))]:
 e=copy.deepcopy(E[n]);count=0
 for pp in e['parts']:
  g=pp['geometry'];v=np.array(g['vertices']);nv=len(v)//2;xy=v[:nv,:2];dist=shapely.distance(shapely.points(xy),walk);near=np.where(dist<1.7)[0]
  for i in near:
   zz=height(*xy[i])-.225;w=max(0,1-dist[i]/1.7);target=v[i,2]+max(0,zz-v[i,2])*w
   if target-v[i,2]>.001:
    delta=target-v[i,2];v[i,2]=target;v[i+nv,2]+=delta;count+=1
  g['vertices']=v.tolist()
 if count:put(n,e['parts'],v15_fix='Supported and blended road subgrade; no deep pit at entry route');groundrows.append({'node':n,'raised_vertices':count})
qa['walking_route']={'polygon':shapely.geometry.mapping(walk),'area_m2':walk.area,'anchors':route_anchors.tolist(),'ground_blending':groundrows,'existing_external_ramp_preserved':True,'inner_gate_target_level_local_m':-.45}
# Remove only overlapping original photographed vertical wall fragments in the modeled-wall band.
source_rows=[]
for n in [n for n in E if n.startswith('SITE_V14_ORIGINAL_EXTERIOR')]:
 rr=I[n];d=np.load(B/'02_Data'/rr['file']);v=d['vertices'];f=d['faces'];uv=d['uv'];t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);nl=np.linalg.norm(nn,axis=1);vertical=(abs(nn[:,2])/(nl+1e-30)<.65);cent=t.mean(1);candidate=vertical&shapely.contains_xy(wallunion,cent[:,0],cent[:,1]);candidate&=(cent[:,2]>-5)&(cent[:,2]<3.5)
 ids=f[~candidate].ravel();vc=v[ids];uc=uv[ids];fc=np.arange(len(ids),dtype=np.int32).reshape(-1,3);fn=n+'.npz';np.savez_compressed(D/fn,vertices=vc,faces=fc,uv=uc,material_ids=np.zeros(len(fc),np.int32));ee=copy.deepcopy(E[n]);ee['external_mesh_file']=fn;rep[n]=ee;source_rows.append({'node':n,'removed_overlapping_vertical_source_faces':int(candidate.sum()),'preserved_faces':len(fc),'materials':rr['materials']})
qa['source_wall_overlap_cleanup']=source_rows
# The real gate has a broad grey carved frame and a timber transom below the roof.
# Reduce the old oversized blank upper mass together with its attached roof detail.
gate_roof_names=[n for n in E if n.startswith('SITE_INNER_GATEHOUSE_ROOF_') or n.startswith(('SITE_GATEHOUSE_VISIBLE_','SITE_GATEHOUSE_FASCIA','SITE_GATEHOUSE_EAVE_FRIEZE','SITE_GATEHOUSE_HANGING_'))]
for n in gate_roof_names:
 ee=copy.deepcopy(E[n]);ee['origin']=list(ee.get('origin',[0,0,0]));ee['origin'][2]-=.55;rep[n]=ee;E[n]=ee
upper=copy.deepcopy(E['SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE']);ps=[]
for pp in upper['parts']:
 v,fs,_,_=ex.solid_data(pp['geometry']);v[:,2]=np.maximum(2.43,v[:,2]-.55);ps.append(p({'type':'polyhedron','vertices':v.tolist(),'faces':fs},'M_Stone_Frame'))
put('SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE',ps,v15_fix='Reduced blank upper wall to photographed eave/transom proportions')
# Chamfered front pillars, six framed relief panels and bamboo/leaf relief.
cores=[]
for x in [4.90,7.90]:
 ring=[[x+.055,-11.975],[x+.345,-11.975],[x+.40,-11.92],[x+.40,-11.45],[x,-11.45],[x,-11.92]];cores.append(p({'type':'prism_holes','outer':ring,'holes':[],'z':-.45,'height':2.50},'M_Stone_Frame'))
cores.append(bx(5.30,-11.95,2.05,2.60,.50,.40,'M_Stone_Frame'));put('SITE_INNER_STONE_GATEHOUSE',cores)
for n in ['SITE_GATEHOUSE_CARVED_PANEL_FRAME_4.95','SITE_GATEHOUSE_CARVED_PANEL_FRAME_7.95']:rem.add(n)
decor=[]
for x in [4.925,7.925]:
 for z,h in [(-.38,.64),(.34,.73),(1.15,.74)]:
  decor.extend([bx(x,-11.990,z,.035,.025,h,'M_Stone_Frame'),bx(x+.315,-11.990,z,.035,.025,h,'M_Stone_Frame'),bx(x,-11.990,z,.350,.025,.032,'M_Stone_Frame'),bx(x,-11.990,z+h-.032,.350,.025,.032,'M_Stone_Frame')]);cx=x+.177
  decor.append(beam([cx-.065,-11.984,z+.08],[cx+.07,-11.984,z+h-.10],.018,.013,'M_Stone_Frame'))
  for k in range(5):
   zz=z+.15+k*(h-.27)/4;xx=cx-.04+k*.025;sgn=(-1)**k;pts=[[xx,-11.999,zz],[xx+sgn*.113,-11.999,zz+.045],[xx+sgn*.065,-11.999,zz+.108]];decor.append(p({'type':'prism','profile':pts,'vector':[0,-.012,0]},'M_Stone_Frame'))
decor.extend([bx(4.89,-11.985,.265,.42,.035,.055,'M_Stone_Frame'),bx(7.89,-11.985,.265,.42,.035,.055,'M_Stone_Frame'),bx(4.89,-11.985,1.06,.42,.035,.055,'M_Stone_Frame'),bx(7.89,-11.985,1.06,.42,.035,.055,'M_Stone_Frame')])
for x in np.arange(5.35,7.88,.23):decor.append(beam([float(x),-11.98,2.15],[float(x)+.14,-11.98,2.31],.02,.018,'M_Stone_Frame'))
put('SITE_V15_INNER_GATE_STONE_RELIEF',decor,classification='SIMPLIFIED_PHOTOGRAPHED_STONE_PANEL_AND_BAMBOO_RELIEF')
door_names=[n for n in E if 'INNER' in n and 'DOOR' in n and n not in gate_roof_names]
qa['prior_gate_door_nodes']=door_names
# Existing double door leaf height is kept; a dark timber header, handles and brass hardware add the photographed hierarchy.
wood=[bx(5.33,-11.962,1.70,2.54,.095,.35,'MAT_DOOR_FRAME_RED')]
wood.extend([bx(5.33,-12.003,1.735,2.54,.030,.035,'MAT_DOOR_FRAME_RED'),bx(5.33,-12.003,1.985,2.54,.030,.035,'MAT_DOOR_FRAME_RED')])
for x in [6.515,6.685]:wood.append(beam([x,-12.015,.50],[x,-12.015,.73],.022,.027,'M_Metal_Black'))
put('SITE_V15_INNER_GATE_TIMBER_TRANSOM_AND_HARDWARE',wood)
lantern=[]
for x in [5.02,8.17]:
 # Each lantern has an explicit hanging cord reaching its roof-side bracket.
 soff=np.load(B/'02_Data'/I['SITE_GATEHOUSE_VISIBLE_SOFFIT_BOARD']['file']);tv=soff['vertices'][soff['faces']];hs=[]
 for t in tv:
  aa=np.vstack([t[:,:2].T,np.ones(3)])
  if abs(np.linalg.det(aa))<1e-12:continue
  w=np.linalg.solve(aa,[x,-12.24,1])
  if np.min(w)>-1e-8:hs.append(float(w@t[:,2])-.55)
 cordtop=min(hs) if hs else 3.30
 lantern.append(beam([x,-12.24,cordtop+.012],[x,-12.24,2.455],.012,.012,'M_Metal_Black'));profile=[[.025,2.03],[.10,2.07],[.205,2.16],[.225,2.29],[.18,2.41],[.065,2.46]];lantern.append(p({'type':'lathe','profile':profile,'segments':40},'M_V12_Kitchen_PAPER_RED'))
 lantern[-1]['geometry']['vertices_origin']=[x,-12.24,0]
 # Convert lathe coordinates to a portable prism/polyhedron before applying the centre.
 vv,ff,_,_=ex.solid_data(lantern[-1]['geometry']);vv[:,:2]+=[x,-12.24];lantern[-1]['geometry']={'type':'polyhedron','vertices':vv.tolist(),'faces':ff}
 for dx in [-.06,-.02,.02,.06]:lantern.append(beam([x+dx,-12.24,2.06],[x+dx,-12.24,1.88],.009,.009,'M_V12_Kitchen_PAPER_RED'))
put('SITE_V15_INNER_GATE_HANGING_LANTERNS',lantern)
for n in ['SITE_INNER_STONE_GATEHOUSE','SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE','SITE_V15_INNER_GATE_STONE_RELIEF']:
 for pp in E[n]['parts']:
  if pp['material']=='M_Stone_Frame':pp['material']='M_V15_GATE_GREY_STONE'
qa['gate']={'roof_and_ornament_shift_z_m':-.55,'reference':'002727 real gate photo; INSV route context','stone_panel_geometry':'Simplified relief fitted to visible forms; not an exact stone-carving reproduction'}
out={'replace':list(rep.values()),'add':list(new.values()),'remove':sorted(rem),'qa':qa,'external_rows':source_rows};(M/'Mutation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(M/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print('GEOMETRY',len(rep),len(new),len(rem),flush=True)
