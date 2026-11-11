"""Resolve the superseded perimeter branch through the kitchen/storage concave corner.
All geometry is local metres. Reference images establish topology; grade is photo fitted.
"""
import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,manifold3d as mf,triangle,mapbox_earcut,export_v5 as ex
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union,nearest_points
from shapely.geometry.polygon import orient
B=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v17';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I=json.loads((B/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};native={}
Q={'part_edits':[],'replace':[],'add':[],'remove':[]};QA={'reference':['DJI_0525.JPG','DJI_0526.JPG','INSV 700/725/950/972 seconds','User screenshots 112805 and 125511']}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
def load(n):
 if n not in native:
  d=np.load(B/'02_Data'/ii[n]['file']);native[n]={k:d[k] for k in d.files}
 return native[n]
def polys(g):return [g] if g.geom_type=='Polygon' else [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon' and q.area>1e-7]
def prism(p,z,h):
 p=orient(p,1);return {'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in p.interiors],'z':z,'height':h}
def poly_man(p,z=-6,h=14):return mf.Manifold.batch_boolean([manifold(prism(q,z,h)) for q in polys(p)],mf.OpType.Add)
def put(n,parts,new=False,**props):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM'}
 e.update(parts=parts,v17_reference=QA['reference'],**props);Q['add' if new else 'replace'].append(e);return e

# The real exterior is the L formed by the registered kitchen facade and the north storage wall.
facade=np.array([[14.0723,-3.295618],[13.528737,-8.275],[13.35,-8.475],[13.35,-9.7],[18.9,-9.7]])
old_branch_box=box(12.95,-16.56,22.0,-3.32);branch_cutter=poly_man(old_branch_box)
changed_parts=[]
for n,e in E.items():
 if not (n.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_0') or n=='SITE_V15_PERIMETER_WHITE_INSIDE_FINISH'):continue
 kept=[];count=0
 for j,p in enumerate(e['parts']):
  g=p['geometry'];v,fs,_,_=ex.solid_data(g);xy=v[:,:2];lo=xy.min(0);hi=xy.max(0)
  if hi[0]<12.95 or lo[0]>22 or hi[1]<-16.56 or lo[1]>-3.32:kept.append(p);continue
  pp=Polygon(xy).convex_hull
  if not pp.intersects(old_branch_box):kept.append(p);continue
  if old_branch_box.covers(pp):gg=None
  else:
   a=manifold(g)-branch_cutter;gg=None if a.is_empty() or a.volume()<1e-10 else fromman(a)
  Q['part_edits'].append({'node':n,'part_index':j,'native_name':f'{n}__{j+1}','material':p['material'],'geometry':gg})
  count+=1
  if gg is not None:kept.append({**p,'geometry':gg,'v17_original_part_index':j})
 if count:
  Q['replace'].append({**e,'parts':kept,'v17_partwise':True,'v17_repair':'Removed obsolete perimeter branch beneath and across photo fitted storage block; registered kitchen/storage facades form the exterior boundary'})
  changed_parts.append({'node':n,'edited_or_removed_parts':count,'remaining_parts':len(kept)})
  print('PERIMETER CORRECTION',n,count,len(kept),flush=True)
QA['obsolete_perimeter_parts']=changed_parts

# Cut the raised soil back to the actual masonry face. Keep the courtyard grading unchanged.
outside=Polygon([[14.063,-3.24],[13.518,-8.275],[13.335,-8.475],[13.335,-9.715],[18.88,-9.715],[18.90,-9.7],[25,-9.7],[25,0],[14.43,0]])
n='SITE_V16_GRADED_INTERIOR_SOIL';g0=E[n]['parts'][0]['geometry'];soil=manifold(g0);sg=fromman(soil-poly_man(outside))
put(n,[{'geometry':sg,'material':'M_V12_Terrain_Earth'}],v17_repair='Raised interior soil stops inside the actual kitchen/storage L; concave exterior garden is lower photo fitted terrain')
v0=np.array(g0['vertices']);f0=triangles(v0,g0['faces']);t=v0[f0];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9
beforearea=unary_union([Polygon(ti[:,:2]) for ti in t[up]]).area
v=np.array(sg['vertices']);f=np.array(sg['faces']);t=v[f];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-9;afterarea=unary_union([Polygon(ti[:,:2]) for ti in t[up]]).area
QA['interior_soil']={'before_area_m2':beforearea,'after_area_m2':afterarea,'removed_exterior_raised_fill_m2':beforearea-afterarea,'unchanged_grade_outside_cut':True}
print('RAISED FILL CUT',beforearea-afterarea,flush=True)

# Preserve the correctly positioned outer-store gutter; remove only the obsolete branch.
segments=json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8'));lastci=max(r['ci'] for r in segments);store_segs=[r for r in segments if r['ci']==lastci];protected=[];edge_lines=[]
for r in store_segs:
 a=np.array(r['a']);b=np.array(r['b']);oa=(np.array(r['outer_a'])-a)/1.05;ob=(np.array(r['outer_b'])-b)/1.05
 protected.append(Polygon([a-oa*.30,b-ob*.30,np.array(r['outer_b']),np.array(r['outer_a'])]).buffer(0));edge_lines.append(LineString([r['outer_a'],r['outer_b']]))
protected=unary_union(protected).buffer(0);cut_branch=box(12.95,-9.59,19.30,-3.32).difference(protected)
for n in ['SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE','SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE']:
 a=manifold(E[n]['parts'][0]['geometry'])-poly_man(cut_branch);put(n,[{'geometry':fromman(a),'material':E[n]['parts'][0]['material']}],v17_repair='Obsolete kitchen concave-corner branch removed; all remaining perimeter and outer-store gutter/toe retained')

# Continuous stone support below the existing slabs, with a wall strip overlapping the facade bases.
store=Polygon([[13.35,-16.2],[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7],[13.35,-9.7]])
wall_strip=LineString(facade).buffer(-.32,single_sided=True,join_style=2).buffer(0)
# Tiny extension at the kitchen north joint overlaps the retained stone support.
wall_strip=wall_strip.union(LineString([facade[0],facade[0]+np.array([.003,.03])]).buffer(.17,cap_style=2)).buffer(0)
foundation=mf.Manifold.batch_boolean([poly_man(store,-4.45,3.94),poly_man(wall_strip,-4.45,4.07)],mf.OpType.Add)
put('SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE',[{'geometry':fromman(foundation),'material':'M_Stone_Rubble'}],True,classification='SUPPORTED_L_FACADE_AND_STORAGE_PLINTH',v17_floor_top=-.4,v17_wall_strip_top=-.38,v17_under_slab_top=-.51,v17_note='Support visualization only; hidden depth is not independently measured; existing slab surfaces and room portals unchanged',v17_facade_outer_line=facade.tolist())

# Lower garden patch, gently photo fitted. The original photogrammetry controls low ground levels.
ground=np.load(D/'Local_Original_Ground.npz')['triangles'];gc=ground.mean(1);controls=[]
for x in np.arange(13.6,20.1,.7):
 for y in np.arange(-9.3,-2.9,.7):
  di=np.linalg.norm(gc[:,:2]-[x,y],axis=1);z=gc[di<.50,2]
  if len(z)>4:controls.append([x,y,float(np.quantile(z,.25))])
controls=np.array(controls);coef=np.linalg.lstsq(np.c_[controls[:,:2],np.ones(len(controls))],controls[:,2],rcond=None)[0]
assert np.linalg.norm(coef[:2])<.15,coef
outerlines=unary_union(edge_lines)
def drain_z(q):
 p=np.array(q);best=None
 for r in store_segs:
  a=np.array(r['outer_a']);d=np.array(r['outer_b'])-a;s=np.clip((p-a)@d/(d@d),0,1);dist=np.linalg.norm(p-(a+s*d));z=r['za']+s*(r['zb']-r['za'])
  if best is None or dist<best[0]:best=(dist,z)
 return best
def garden_height(x,y):
 z=float(np.dot([x,y,1],coef));di,zz=drain_z([x,y])
 if di<2.0:
  s=di/2.0;w=1-3*s*s+2*s*s*s;z=z*(1-w)+zz*w
 return z
patch=Polygon([[14.04,-3.27],[13.50,-8.27],[13.31,-8.47],[13.31,-9.75],[18.88,-9.75],[20.30,-9.10],[20.40,-6.20],[19.50,-3.15],[17.60,-2.75],[14.20,-2.75]]).difference(protected).buffer(0)
def quality_volume(domain,h,bottom):
 vv=[];ff=[];gr=[]
 for poly in polys(domain):
  if poly.area<1e-7:continue
  p=orient(poly,1);rings=[list(p.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in p.interiors];v=[];se=[]
  for r in rings:
   off=len(v);v.extend(r);se.extend([[off+j,off+(j+1)%len(r)] for j in range(len(r))])
  inp={'vertices':np.array(v),'segments':np.array(se,np.int32)}
  if len(rings)>1:inp['holes']=np.array([[Polygon(r).representative_point().x,Polygon(r).representative_point().y] for r in rings[1:]])
  out=triangle.triangulate(inp,'pq25a0.09Q');v=out['vertices'];f=out['triangles'];tt=v[f];neg=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0])<0;f[neg]=f[neg][:,::-1];N=len(v);v3=np.c_[v,[h(*q) for q in v]];t=v3[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);gr.extend((np.linalg.norm(no[:,:2],axis=1)/no[:,2]).tolist());edges={}
  for tri in f:
   for a,b in zip(tri,np.roll(tri,-1)):edges.setdefault(tuple(sorted([int(a),int(b)])),[]).append((int(a),int(b)))
  fs=f.tolist()+(f[:,::-1]+N).tolist()
  for ed in edges.values():
   if len(ed)==1:
    a,b=ed[0];fs.extend([[b,a,a+N],[b,a+N,b+N]])
   else:assert len(ed)==2
  off=len(vv);vv.extend(v3.tolist()+np.c_[v,np.full(N,bottom)].tolist());ff.extend((np.array(fs)+off).tolist())
 return {'type':'polyhedron','vertices':vv,'faces':ff},np.array(gr)
garden,grades=quality_volume(patch,garden_height,-4.65);assert grades.max()<.7,grades.max()
put('SITE_V17_LOWER_EXTERIOR_GARDEN_TERRAIN',[{'geometry':garden,'material':'M_V17_Garden_Soil'}],True,classification='PHOTO_FITTED_LOW_GROUND_OUTSIDE_CONCAVE_FACADE',v17_plane_coefficients=coef.tolist(),v17_note='Low soil grade fitted to retained exterior mesh; source detail not independently surveyed',v17_continuity='2 m soft transition to retained outer storage drain')
QA['garden']={'area_m2':patch.area,'ground_control_count':len(controls),'fit_coefficients':coef.tolist(),'fit_residual_p90_m':float(np.quantile(abs(controls[:,2]-np.c_[controls[:,:2],np.ones(len(controls))]@coef),.9)),'top_height_minmax_m':[min(q[2] for q in garden['vertices'][:len(garden['vertices'])//2]),max(q[2] for q in garden['vertices'])],'grade_quantiles':np.quantile(grades,[.1,.5,.9,.99,1]).tolist()}

# Clear only the repaired pocket's scan scraps. At the boundary, blend original road/soil to the exact new patch grade.
maskbuff=patch.buffer(.36);clipchecks=[]
for n in E:
 if not n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 dat=load(n);v=dat['vertices'];f=dat['faces'];uv=dat['uv'];nv=[];nf=[];nu=[];removed=0;cut=0;blend=0
 def addtri(vs,us):
  global blend
  vs=np.array(vs);us=np.array(us);vs=vs.copy()
  for j,p0 in enumerate(vs):
   p=Point(p0[:2]);di=p.distance(patch)
   if di<.36 and maskbuff.covers(p) and p0[2]<-1.7:
    qq=nearest_points(p,patch)[1];z0=garden_height(qq.x,qq.y);s=di/.36;w=1-3*s*s+2*s*s*s
    # Vertical crop tips at the seam would otherwise reveal a scan tear.
    vs[j,2]=p0[2]*(1-w)+z0*w;blend+=1
  if np.linalg.norm(np.cross(vs[1]-vs[0],vs[2]-vs[0]))<1e-10:return
  off=len(nv);nv.extend(vs.tolist());nu.extend(us.tolist());nf.append([off,off+1,off+2])
 for fi,face in enumerate(f):
  t=v[face];u=uv[face];p=Polygon(t[:,:2]);lo=t[:,:2].min(0);hi=t[:,:2].max(0)
  if hi[0]<13.25 or lo[0]>20.8 or hi[1]<-10.1 or lo[1]>-2.4:
   addtri(t,u);continue
  if p.area<1e-12:
   if patch.covers(Point(t[:,:2].mean(0))):removed+=1;continue
   addtri(t,u);continue
  if not p.is_valid:p=p.buffer(0)
  if not p.intersects(patch):addtri(t,u);continue
  rem=p.difference(patch)
  if rem.is_empty:removed+=1;continue
  cut+=1
  a=t[0,:2];A=np.column_stack([t[1,:2]-a,t[2,:2]-a]);ai=np.linalg.inv(A)
  for po in polys(rem):
   po=orient(po,1);rings=[list(po.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in po.interiors];pv=np.array([q for ring in rings for q in ring]);ix=mapbox_earcut.triangulate_float64(pv,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3)
   ab=(pv-a)@ai.T;weights=np.c_[1-ab.sum(1),ab];vv=weights@t;uu=weights@u
   for tri in ix:
    q=vv[tri];oldno=np.cross(t[1]-t[0],t[2]-t[0]);newno=np.cross(q[1]-q[0],q[2]-q[0])
    if oldno@newno<0:tri=tri[::-1]
    addtri(vv[tri],uu[tri])
 fn='SOURCE_'+n+'.npz';np.savez_compressed(D/fn,vertices=np.array(nv),faces=np.array(nf,np.int32),uv=np.array(nu),material_ids=np.zeros(len(nf),np.int32))
 if removed or cut or blend:put(n,[],v17_native_source_file=fn,v17_repair='Concave corner scan scraps removed; lower soil boundary matched with 360 mm blend; original UV preserved elsewhere')
 clipchecks.append({'node':n,'old_triangles':len(f),'new_triangles':len(nf),'removed_triangles':removed,'cut_triangles':cut,'blended_vertex_occurrences':blend});print('SCAN CORRECTION',n,clipchecks[-1],flush=True)
QA['scan']=clipchecks;QA['protected_outer_store_drain_chain']=lastci
for name,g in [('obsolete_branch',old_branch_box),('raised_soil_cut',outside),('low_garden_patch',patch),('protected_store_drain',protected),('foundation_wall_strip',wall_strip)]:
 (D/(name+'.geojson')).write_text(json.dumps(shapely.geometry.mapping(g)),encoding='utf8')
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Geometry_QA.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8')
print('V17 GEOMETRY READY',len(Q['part_edits']),len(Q['replace']),len(Q['add']),flush=True)
