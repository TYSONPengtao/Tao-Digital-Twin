"""Replace only five front bay-to-bedroom jamb nodes with continuous fitted solids."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
from shapely.geometry import Polygon,LineString,box as box2
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
import hashlib
D=W/'v26_16';I=D/'Input';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P;J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};HN='V26_3_House_Connected_Walls_And_Stairs';r=ix[HN];a=np.load(I/r['file']);assert hashlib.sha256(Path(J['model']).read_bytes()).hexdigest()==J['sha256'];old=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);house=old
WHITE='M_Wall_Interior';CEIL='M_V26_3_Neutral_White_Interior_Ceiling';proof=[];scopes=[];ownership=[]
def box(lo,hi):return cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
def prism(poly,z0,z1):
 rings=[]
 for q in(poly.geoms if hasattr(poly,'geoms')else[poly]):
  if q.is_empty or q.area<1e-12:continue
  q=orient(q,1);rings.append(np.asarray(q.exterior.coords,np.float32).astype(float)[:-1]);rings.extend(np.asarray(h.coords,np.float32).astype(float)[:-1]for h in q.interiors)
 z0,z1=map(lambda z:float(np.float32(z)),[z0,z1]);return mf.CrossSection(rings,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
def white(m,name):return finish(m,WHITE,name)
for fl,floor,ceil,beam in[(1,-.44999998807907104,3.319999933242798,3.049999952316284),(2,3.450000047683716,6.920000076293945,6.649975776672363),(3,7.050000190734863,10.220000267028809,9.950024604797363)]:
 for side,cx,k in [('L',3.9,2),('R',9.1,0)]:
  if fl==3 and side=='L':continue
  wn=f'BAY_WINDOW_F{fl}_{side}_{k}_Geometry';wr=ix[wn];wa=np.load(I/wr['file']);uvector=np.asarray([(-1 if side=='L'else 1)*.5848568450639461,-.8111365302967483]);end=float((wa['v'][:,:2]@uvector).min());ys=[1.6,2.6];xp=[(end-uvector[1]*y)/uvector[0]for y in ys];far=cx+(1 if side=='L'else-1)*1.0;half=Polygon([[xp[0],ys[0]],[xp[1],ys[1]],[far,ys[1]],[far,ys[0]]]);bridge=box2(cx-.12 if side=='L'else cx-.20,1.95,cx+.20 if side=='L'else cx+.12,2.1904).intersection(half);rear=box2(cx-.12,2.19,cx+.12,2.4004);jamb=bridge.union(rear);plan=box2(cx-.35,1.78,cx+.35,2.4)
  lo=[cx-.35,1.78,floor];hi=[cx+.35,2.4,ceil];scope=box(lo,hi);scopes.append(scope);house-=white(scope,f'F{fl}{side} remove fragmented local bay/jamb/beam node only')
  node=white(prism(jamb.intersection(plan),floor-.0004,ceil+.0002),f'F{fl}{side} continuous narrow jamb and240mm bedroom wall bond')
  x0=0. if side=='L'else 9.1;centre=[(x0,2.1),(x0+.72,1.1),(x0+3.18,1.1),(x0+3.9,2.1)];strip=LineString(centre).buffer(.1,cap_style=2,join_style=2).intersection(plan)
  bottom=float(wa['v'][:,2].min());top=float(wa['v'][:,2].max());silltop=(-.151 if fl==1 else (4.500049018859863 if fl==2 else 8.100049161911011)-.001)
  node+=white(prism(strip,floor-.0004,silltop),f'F{fl}{side} continuous200mm under-window return, no square foot plug')
  # The bay lintel terminates above the retained frame. The ordinary beam
  # continues behind the jamb at its native250.6mm finished width/soffit.
  header=strip.union(box2(cx-.12 if side=='L'else cx-.2,1.95,cx+.2 if side=='L'else cx+.12,2.2253000736236572)).intersection(plan)
  node+=white(prism(header,top+.0004,ceil+.0002),f'F{fl}{side} complete window head above actual black frame')
  node+=white(box([cx-.1253,2.19,beam],[cx+.1253,2.4004,ceil+.0002]),f'F{fl}{side} straight existing longitudinal beam end')
  cross=box2(cx+.2,1.9746999740600586,cx+.3504,2.2253000736236572)if side=='L'else box2(cx-.3504,1.9746999740600586,cx-.2,2.2253000736236572)
  node+=white(prism(cross,beam,ceil+.0002),f'F{fl}{side} retained porch-side transverse beam soffit')
  # One full-height oriented frame seat removes every old white tab. Its
  # reveal is0.4mm; it does not change any black frame, glass or hinge mesh.
  glass_ids=[j for j,m in enumerate(wr['materials'])if'Glass'in m];gt=wa['v'][wa['f'][np.isin(wa['mi'],glass_ids)]];no=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);n=no[np.argmax(np.linalg.norm(no,axis=1)),:2];n/=np.linalg.norm(n);u=np.asarray([n[1],-n[0]]);pp=wa['v'][:,:2]@u;qq=wa['v'][:,:2]@n;seat=box([pp.min()-.0004,qq.min()-.0004,bottom-.0004],[pp.max()+.0004,qq.max()+.0004,top+.0004]).transform([[u[0],n[0],0,0],[u[1],n[1],0,0],[0,0,1,0]]);node-=white(seat,f'F{fl}{side} single clean frame-owned seat');house+=node^scope
  proof.append({'floor':fl,'side':side,'frame':wn,'jamb_plan':jamb.__geo_interface__,'scope_bounds_m':[lo,hi],'frame_bottom_z_m':bottom,'frame_top_z_m':top,'sill_top_z_m':silltop,'beam_soffit_z_m':beam,'ceiling_z_m':ceil,'ordinary_sill_wall_width_m':.20,'bedroom_wall_width_m':.24,'frame_seat_reveal_m':.0004,'frames_and_glass_unchanged':True})
# The right third-floor bay had no continuous closure at the bedroom's
# finished ceiling level. Roof-cut wall slivers above10.22m remained visible
# through that opening. Bond a flat soffit into the existing roof/header
# stock, entirely inside the bay wall centreline, rather than overlaying it.
bay_plan=Polygon([(9.1,2.1),(9.82,1.1),(12.28,1.1),(13.,2.1),(13.,2.4),(9.1,2.4)])
bay_scope=[[9.0999,1.0999,10.219999],[13.0001,2.4001,10.4004]]
bay_before=house
house+=finish(prism(bay_plan,10.220000267028809,10.4003),CEIL,'F3R continuous bay soffit bonded to the existing10.22m room ceiling')
scopes.append(box(*bay_scope))
bay_closure={'floor':3,'side':'R','scope_bounds_m':bay_scope,'plan':bay_plan.__geo_interface__,'finished_ceiling_z_m':10.220000267028809,'roof_stock_top_z_m':10.4003,'added_volume_m3':(house-bay_before).volume(),'cause':'Roof-cut wall slivers were exposed through an unclosed bay ceiling above the existing bedroom finished level.'}
# A separate rectangular balcony edge has an underside2mm below the room
# ceiling and was left exposed by the earlier jamb cuts. Transfer only its
# two inner corner nodes to the house, trim only actual room-air footprints
# to the existing ceiling, and remove those same nodes from the edge owner.
EN='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry';er=ix[EN];ea=np.load(I/er['file']);edge0=tracked(ea['v'],ea['f'],er['materials'],ea['mi'],ea['uv'],EN);edge=edge0
def sliced(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  p=np.asarray(p);sgn=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);(pos if sgn>0 else neg).append(Polygon(p))
 return unary_union(pos).difference(unary_union(neg))
for nd in [q for q in proof if q['floor']==1]:
 lo,hi=nd['scope_bounds_m'];cx=(lo[0]+hi[0])/2;roi=box([lo[0],lo[1],3.317],[hi[0],hi[1],3.53]);part=edge^roi;air=box2(lo[0]+.00001,lo[1]+.00001,hi[0]-.00001,hi[1]-.00001).difference(sliced(house,nd['ceiling_z_m']-.001));room=box2(lo[0]-.01,1.7,cx-.12,2.5)if nd['side']=='L'else box2(cx+.12,1.7,hi[0]+.01,2.5);air=air.intersection(room)
 cutter=finish(prism(air,3.317,nd['ceiling_z_m']),CEIL,'Trim only the balcony edge exposed below the true indoor ceiling');transferred=part-cutter;removed=(part^cutter).volume();house+=transferred;edge-=roi;scopes.append(roi);ownership.append({'floor':1,'side':nd['side'],'source':EN,'scope_bounds_m':[[lo[0],lo[1],3.317],[hi[0],hi[1],3.53]],'indoor_air_plan':air.__geo_interface__,'old_underside_z_m':3.318,'new_underside_z_m':nd['ceiling_z_m'],'exposed_intrusion_removed_m3':removed,'external_balcony_envelope_preserved':True})
row,house=export(HN,clean(house).simplify(.0000001),'Five continuous narrow front window jambs, complete head nodes and no frame-crossing sill/transom plugs');b=np.load(P/row['file']);v,f,mi,uv=b['v'],b['f'],b['mi'].copy(),b['uv'];tt=v[f];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);cc=tt.mean(1)
for q in proof:
 lo,hi=map(np.asarray,q['scope_bounds_m']);sel=np.all(cc>=lo-1e-6,1)&np.all(cc<=hi+1e-6,1)&(nn[:,2]<-1e-10)&(cc[:,2]>=q['beam_soffit_z_m']-1e-6);mi[sel]=row['materials'].index(CEIL)
v,f,mi,uv,cleanup=repair_indexed(v,f,mi,uv)
# Classify even the very small cleanup triangles by normalized direction.
tt=v[f];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);nn/=np.maximum(np.linalg.norm(nn,axis=1,keepdims=True),1e-30);cc=tt.mean(1)
for q in proof:
 lo,hi=map(np.asarray,q['scope_bounds_m']);head=np.all(cc>=lo-1e-6,1)&np.all(cc<=hi+1e-6,1)&(cc[:,2]>=q['beam_soffit_z_m']-1e-6);sel=head&(nn[:,2]<-.99);mi[sel]=row['materials'].index(CEIL)
 vertical=head&(abs(nn[:,2])<.01);mi[vertical]=row['materials'].index(WHITE);uv[vertical]=uv_project(v,f[vertical])
np.savez_compressed(P/row['file'],v=v,f=f,mi=mi,uv=uv);row.update(triangles=len(f),native_cleanup=cleanup);saved=solid(v,f);mask=union(scopes);outside_add=((saved-old)-mask).volume();outside_remove=((old-saved)-mask).volume();assert abs(outside_add)<5e-6 and abs(outside_remove)<5e-6,(outside_add,outside_remove);assert len(saved.decompose())==1
edge_row,edge=export(EN,edge,'Transfer only inner balcony corner nodes to the house owner and remove2mm visible intrusion below the indoor ceiling; external balcony silhouette retained');eb=np.load(P/edge_row['file']);ev,ef,emi,euv,ec=repair_indexed(eb['v'],eb['f'],eb['mi'],eb['uv']);np.savez_compressed(P/edge_row['file'],v=ev,f=ef,mi=emi,uv=euv);edge_row.update(triangles=len(ef),native_cleanup=ec)
out={'source':J['model'],'source_sha256':J['sha256'],'objects':[row,edge_row],'archive':[],'proof':{'cause':'Narrow jamb and frame-seat cuts ended at nearly the frame top, leaving fragmented original beam/column heads. Old under-window foot bonds and incomplete frame seats also produced white tabs at transoms and sill ends. A separate balcony edge underside also projected2mm below the indoor ceiling and exposed exterior-finish triangles. The third-floor right bay ceiling was not closed at the existing bedroom ceiling level, exposing roof-cut wall slivers.','method':'Replace only each bounded local joint by a continuous narrow jamb,200mm sill return, frame-fitted lintel and retained regular beam stubs; one0.4mm full-frame reveal owns the junction. Close the third-floor right bay soffit at the existing room finished level. Transfer the two inner balcony edge nodes to a single house owner and trim only the room-side intrusion. No overlay surfaces.','nodes':proof,'bay_ceiling_closure':bay_closure,'balcony_corner_ownership':ownership,'outside_added_m3':outside_add,'outside_removed_m3':outside_remove,'dimensions':'Registered native model and previously supplied real-photo proportions; not new field measurements','closed_house_components':len(saved.decompose()),'native_cleanup':cleanup}}
(D/'Prepared.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('PREPARED',len(proof),len(f),'outside',outside_add,outside_remove,flush=True)
