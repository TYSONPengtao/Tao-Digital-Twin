"""Rebuild facade framing first, then fit the ten fixed bay returns in front of it."""
from v26_2_common import *
import v26_2_common as C
from v26_15_native_cleanup import repair_indexed
from shapely.geometry import Polygon,LineString,box as box2,mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
import shapely
import hashlib
D=W/'v26_17';I=D/'Input';P=D/'Prepared';P.mkdir(exist_ok=True);C.D=P
J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']}
assert hashlib.sha256(Path(J['model']).read_bytes()).hexdigest()==J['sha256']
HN='V26_3_House_Connected_Walls_And_Stairs';EN='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry'
r=ix[HN];a=np.load(I/r['file']);old=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN);house=old
er=ix[EN];ea=np.load(I/er['file']);edge0=tracked(ea['v'],ea['f'],er['materials'],ea['mi'],ea['uv'],EN)
WHITE='M_Wall_Interior';CEIL='M_V26_3_Neutral_White_Interior_Ceiling';FLOOR='M_Floor';EXT='M_V21_House_Exterior_Grey_White'
LEVELS=[(1,-.449999988079071,3.319999933242798,3.049999952316284,-.600024402141571,3.450000047683716),
        (2,3.450000047683716,6.920000076293945,6.649975776672363,3.319999933242798,7.050000190734863),
        (3,7.050000190734863,10.220000267028809,9.950024604797363,6.920000076293945,10.4003)]
def box(lo,hi):return cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
def prism(poly,z0,z1):
 rings=[]
 for p in(poly.geoms if hasattr(poly,'geoms')else[poly]):
  if p.is_empty or p.area<1e-12:continue
  p=orient(p,1);rings.append(np.asarray(p.exterior.coords,np.float32).astype(float)[:-1]);rings.extend(np.asarray(h.coords,np.float32).astype(float)[:-1]for h in p.interiors)
 if not rings:return mf.Manifold()
 z0,z1=map(lambda z:float(np.float32(z)),[z0,z1]);return mf.CrossSection(rings,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
def painted(m,mat,why):return finish(m,mat,why)
def white(m,why):return painted(m,WHITE,why)
def sliced(m,z):
 pos=[];neg=[]
 for ring in m.slice(z).to_polygons():
  ring=np.asarray(ring);area=np.sum(ring[:,0]*np.roll(ring[:,1],-1)-np.roll(ring[:,0],-1)*ring[:,1]);(pos if area>0 else neg).append(Polygon(ring))
 return unary_union(pos).difference(unary_union(neg))

bays=[];frames=[];rows=[];scopes=[];parts=[];plates={}
for fl,floor,ceil,beam,slab0,slabtop in LEVELS:
 for side,x0 in [('L',0.),('R',9.1)]:
  if fl==3 and side=='L':continue
  oldline=[(x0,2.1),(x0+.72,1.1),(x0+3.18,1.1),(x0+3.9,2.1)]
  line=[(x0-.10,1.89),oldline[1],oldline[2],(x0+4.,1.89)]
  room=Polygon(line+[(x0+4.,2.36),(x0-.1,2.36)])
  strip=LineString(line).buffer(.1,cap_style=2,join_style=2)
  lo=[x0-.35,.9,floor];hi=[x0+4.25,2.36,ceil];scope=box(lo,hi);scopes.append(scope)
  # Fixed returns are independent of the two central outward-opening leaves.
  transformed={}
  for k,corner,terminal,ncorner,nterminal in[(0,oldline[1],oldline[0],line[1],line[0]),(2,oldline[2],oldline[3],line[2],line[3])]:
   name=f'BAY_WINDOW_F{fl}_{side}_{k}_Geometry';wr=ix[name];wa=np.load(I/wr['file']);v=wa['v'].copy();oa,ob,na,nb=map(np.asarray,[corner,terminal,ncorner,nterminal]);ot=ob-oa;length=np.linalg.norm(ot);ot/=length;on=np.array([-ot[1],ot[0]]);nt=nb-na;new_length=np.linalg.norm(nt);nt/=new_length;nn=np.array([-nt[1],nt[0]])
   along=(v[:,:2]-oa)@ot;depth=(v[:,:2]-oa)@on;margin=.10
   newalong=np.where(along<margin,along,np.where(along>length-margin,new_length-(length-along),margin+(along-margin)*(new_length-2*margin)/(length-2*margin)))
   v[:,:2]=na+newalong[:,None]*nt+depth[:,None]*nn
   framed=tracked(v.astype(np.float32).astype(float),wa['f'],wr['materials'],wa['mi'],wa['uv'],name+' fitted fixed return')
   frame_row,framed=export(name,framed,'Remove inherited zero-area faces by native solid canonicalisation before fitting the fixed return')
   fa=np.load(P/frame_row['file']);local_mi=np.array([wr['materials'].index(frame_row['materials'][int(i)])for i in fa['mi']],np.int32)
   v,ff,fmi,fuv,frame_cleanup=repair_indexed(fa['v'],fa['f'],local_mi,fa['uv'])
   fbad=(~np.isfinite(fuv).all(axis=(1,2)))|(abs(fuv).max(axis=(1,2))>1e5);fuv[fbad]=uv_project(v,ff[fbad])
   file=name+'.npz';np.savez_compressed(P/file,v=v,f=ff,mi=fmi,uv=fuv);row={**wr,'file':file,'triangles':len(ff),'native_cleanup':frame_cleanup,'reason':'Fit the fixed return before the column, preserve glazing height and frame end profiles, and remove only collapsed indexed zero faces.'};rows.append(row);transformed[k]=(v,ff,nt,na)
   # Original400mm core and250mm beams are independent references, not cut by a window.
   cx=x0 if k==0 else x0+3.9;column=box([cx-.2,1.9,floor],[cx+.2,2.3,ceil]);cross=box([x0,1.975,beam],[x0+3.9,2.225,ceil]);long=box([cx-.125,2.1,beam],[cx+.125,2.36,ceil]);wm0=solid(wa['v'],wa['f']);wm1=solid(v,ff)
   core=column+cross+long
   frames.append({'name':name,'floor':fl,'side':side,'end':k,'original_segment_xy':[corner,terminal],'new_segment_xy':[ncorner,nterminal],'old_length_m':length,'new_length_m':new_length,'post_axis_x_m':cx,'post_front_y_m':1.9,'actual_new_frame_max_y_m':float(v[:,1].max()),'old_frame_core_overlap_m3':(wm0^core).volume(),'new_frame_core_overlap_m3':(wm1^core).volume(),'z_extent_retained':bool(np.allclose([v[:,2].min(),v[:,2].max()],[wa['v'][:,2].min(),wa['v'][:,2].max()],atol=2e-6,rtol=0)),'end_profile_zone_preserved_m':margin})
  zmin=min(float(transformed[k][0][:,2].min())for k in[0,2]);zmax=max(float(transformed[k][0][:,2].max())for k in[0,2]);sill=zmin-.001;header=zmax+.001
  house-=white(scope,f'F{fl}{side}: remove the old window-carved facade node, not slabs below its finished floor')
  rebuilt=mf.Manifold()
  for cx,k in[(x0,0),(x0+3.9,2)]:
   post=box([cx-.2,1.9,floor],[cx+.2,2.3,ceil]);rebuilt+=white(post,f'F{fl}{side} original400x400 axis column, complete shaft and head');parts.append({'type':'column','floor':fl,'side':side,'axis_x_m':cx,'bounds_m':[[cx-.2,1.9,floor],[cx+.2,2.3,ceil]],'reference':'Original saved KZ column definition, not a new field measurement'})
   # Thin nonstructural return fills only the frame-to-post mounting space.
   v,_,t,origin=transformed[k];end=float(((v[:,:2]-origin)@t).max())+.002
   anchor=origin+t*end;n=np.array([-t[1],t[0]]);hp=Polygon([anchor+n*2,anchor-n*2,anchor-n*2+t*2,anchor+n*2+t*2])
   jamb=box2(cx-.2,1.78,cx+.2,1.9001).intersection(hp)
   rebuilt+=white(prism(jamb,floor,ceil),f'F{fl}{side} continuous thin frame-end mounting return')
   # The rear wall stops before the existing bedroom door opening atY2.40.
   rebuilt+=white(box([cx-.12,2.3,floor],[cx+.12,2.3604,ceil]),f'F{fl}{side} preserved240mm ordinary wall after the column')
   long=box([cx-.1253,2.1,beam],[cx+.1253,2.3604,ceil]);rebuilt+=white(long,f'F{fl}{side} rectangular longitudinal beam into the full column');parts.append({'type':'beam_y','floor':fl,'side':side,'bounds_m':[[cx-.1253,2.1,beam],[cx+.1253,2.36,ceil]]})
  bx0=max(0.,lo[0])if fl<3 else x0;bx1=min(13.,hi[0])
  cross=box([bx0,1.9747,beam],[bx1,2.2253,ceil]);rebuilt+=white(cross,f'F{fl}{side} continuous unnotched transverse beam');parts.append({'type':'beam_x','floor':fl,'side':side,'bounds_m':[[x0,1.9747,beam],[x0+3.9,2.2253,ceil]],'soffit_z_m':beam})
  # Keep the previously accepted high entry head on F3, without recreating
  # the retired lower beam through the central passage.
  if fl==3:
   protect=box([lo[0],1.95,header],[x0-.2,2.36,ceil]);rebuilt+=old^protect
  rebuilt+=white(prism(strip,floor,sill),f'F{fl}{side} full opaque sill at the unchanged original height')
  rebuilt+=white(prism(strip,header,ceil),f'F{fl}{side} continuous bay head above the unchanged glazing height')
  house+=rebuilt^scope
  # The new return lies slightly in front of the previous one. Missing floor
  # and ceiling-edge stock is bonded to the existing slab, never overlaid.
  slabplan=room.buffer(.1,join_style=2)
  for tag,z0,z1 in [('floor',slab0,floor),('ceiling',ceil,slabtop)]:
   key=(side,round(z0,5),round(z1,5))
   if key in plates:continue
   plate=prism(slabplan,z0,z1);house+=painted(plate,FLOOR,f'F{fl}{side} bonded bay {tag} plate at existing level')
   bounds=[[*slabplan.bounds[:2],z0],[*slabplan.bounds[2:],z1]];scopes.append(box(*bounds));pr={'type':'slab','floor':fl,'side':side,'tag':tag,'z_m':[z0,z1],'plan':mapping(slabplan),'scope_bounds_m':bounds};plates[key]=pr;parts.append(pr)
  bays.append({'floor':fl,'side':side,'axis_span_m':[x0,x0+3.9],'scope_bounds_m':[lo,hi],'new_bay_plan':mapping(room),'sill_top_z_m':sill,'frame_bottom_z_m':zmin,'frame_top_z_m':zmax,'header_bottom_z_m':header,'ceiling_z_m':ceil,'floor_z_m':floor,'beam_soffit_z_m':beam,'source_axis_dimension_m':3.9})

mask=union(scopes)
# Transfer only affected balcony-edge stock into the house owner. Trim the
# two millimetre underside and five millimetre top cap only in actual room
# air, preserving the complete exterior balcony envelope.
edgepart=edge0^mask;edge=edge0-mask;edge_trim=[]
for b in[b for b in bays if b['floor']in[1,2]]:
 from shapely.geometry import shape
 room=shape(b['new_bay_plan']).buffer(-.1,join_style=2)
 if b['floor']==1:z0,z1,zsample=b['ceiling_z_m']-.01,b['ceiling_z_m'],b['ceiling_z_m']-.001
 else:z0,z1,zsample=b['floor_z_m'],b['floor_z_m']+.01,b['floor_z_m']+.002
 air=room.difference(sliced(house,zsample));cut=prism(air,z0,z1);removed=(edgepart^cut).volume();edgepart-=painted(cut,CEIL,'Balcony edge stops at the actual finished indoor slab boundary');edge_trim.append({'floor':b['floor'],'side':b['side'],'removed_m3':removed,'z_m':[z0,z1]})
house+=edgepart
# Repartition only the existing2mm floor finish stock by the source material
# regions. This keeps original paving/porch boundaries through Boolean cuts;
# assigning a whole new triangle by its centre would create triangular stains.
source_tr=a['v'][a['f']];source_no=np.cross(source_tr[:,1]-source_tr[:,0],source_tr[:,2]-source_tr[:,0]);floor_finish_regions=[]
for fl,floor,*_ in LEVELS:
 xyregions=[box2(*np.asarray(b['scope_bounds_m'])[:,:2].ravel())for b in bays if b['floor']==fl]
 xyregions += [shape(p['plan'])for p in plates.values()if abs(p['z_m'][1]-floor)<2e-6]
 if not xyregions:continue
 area=unary_union(xyregions);cap_scope=prism(area,floor-.002,floor);cap=house^cap_scope;house-=cap_scope;remaining=cap
 sid=np.flatnonzero((source_no[:,2]>0)&(abs(source_tr[:,:,2]-floor).max(1)<2e-6));groups={}
 for face in sid:
  polygon=Polygon(source_tr[face,:,:2]).intersection(area)
  if polygon.area>1e-12:groups.setdefault(int(a['mi'][face]),[]).append(polygon)
 for material,polygons in groups.items():
  region=unary_union(polygons);volume=prism(region,floor-.002,floor);piece=remaining^volume
  if piece.volume()>1e-12:
   house+=painted(piece,r['materials'][material],'Original coplanar floor finish boundary retained');remaining-=volume;floor_finish_regions.append({'floor':fl,'material':r['materials'][material],'area_m2':region.area})
 if remaining.volume()>1e-12:house+=painted(remaining,FLOOR,'New structural plate edge uses the adjoining original floor finish')
row,m=export(HN,house,'Restore complete original-axis columns, rectangular beams and continuous slab edges; fit fixed bay returns before the structural faces.')
aa=np.load(P/row['file']);v,f,mi,uv=aa['v'],aa['f'],aa['mi'].copy(),aa['uv'].copy();v,f,mi,uv,cleanup=repair_indexed(v,f,mi,uv)
tr=v[f];no=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1,keepdims=True),1e-30);c=tr.mean(1)
# New planar beam/slab soffits and vertical paints have consistent ownership
# and world mapping; preserve original face data outside the repair bounds.
for b in bays:
 lo,hi=map(np.asarray,b['scope_bounds_m']);inside=np.all(c>=lo-1e-6,1)&np.all(c<=hi+1e-6,1)
 down=inside&(no[:,2]<-.99)&(c[:,2]>=b['beam_soffit_z_m']-1e-6);mi[down]=row['materials'].index(CEIL)
 vertical=inside&(abs(no[:,2])<.01);mi[vertical]=row['materials'].index(WHITE);uv[vertical]=uv_project(v,f[vertical])
 from shapely.geometry import shape
 room=shape(b['new_bay_plan']).buffer(.001);to_room=shapely.contains_xy(room,c[:,0]+no[:,0]*.025,c[:,1]+no[:,1]*.025)
 exterior=vertical&(~to_room)&(c[:,1]<1.95);mi[exterior]=row['materials'].index(EXT)
for p in plates.values():
 lo,hi=map(np.asarray,p['scope_bounds_m']);inside=np.all(c>=lo-1e-6,1)&np.all(c<=hi+1e-6,1)
 bottom=inside&(no[:,2]<-.99)&(abs(c[:,2]-p['z_m'][0])<2e-6);mi[bottom]=row['materials'].index(CEIL)
# Recover the original coplanar floor finish by exact2D containment. A large
# floor triangle must not be recoloured from its centroid bounding box alone.
source_tr=a['v'][a['f']];source_no=np.cross(source_tr[:,1]-source_tr[:,0],source_tr[:,2]-source_tr[:,0])
from shapely.strtree import STRtree
from shapely.geometry import Point
for fl,floor,*_ in LEVELS:
 sid=np.flatnonzero((source_no[:,2]>1e-9)&(abs(source_tr[:,:,2]-floor).max(1)<2e-6));polys=[Polygon(t[:,:2])for t in source_tr[sid]];tree=STRtree(polys)
 for face in np.flatnonzero((no[:,2]>.99)&(abs(c[:,2]-floor)<2e-6)):
  point=Point(c[face,:2]);hits=tree.query(point,predicate='intersects')
  if len(hits):
   orig=int(sid[max(hits,key=lambda i:polys[int(i)].area)]);mi[face]=row['materials'].index(r['materials'][int(a['mi'][orig])]);uv[face]=bary_uv(tr[face:face+1],source_tr[orig:orig+1],a['uv'][orig:orig+1])[0]
  elif any(shape(p['plan']).covers(point)and abs(p['z_m'][1]-floor)<2e-6 for p in plates.values()):mi[face]=row['materials'].index(FLOOR);uv[face]=uv_project(v,f[face:face+1])[0]
bad_uv=(~np.isfinite(uv).all(axis=(1,2)))|(abs(uv).max(axis=(1,2))>1e5);uv[bad_uv]=uv_project(v,f[bad_uv])
np.savez_compressed(P/row['file'],v=v,f=f,mi=mi,uv=uv);row.update(triangles=len(f),native_cleanup=cleanup,invalid_uv_faces_reprojected=int(bad_uv.sum()));saved=solid(v,f);assert len(saved.decompose())==1
outside=[((saved-old)-mask).volume(),((old-saved)-mask).volume()];assert max(map(abs,outside))<1e-5,outside
edge_row,em=export(EN,edge,'Affect only the facade-frame joint ownership; keep the original exterior balcony outline.')
ee=np.load(P/edge_row['file']);ev,ef,emi,euv,ec=repair_indexed(ee['v'],ee['f'],ee['mi'],ee['uv']);np.savez_compressed(P/edge_row['file'],v=ev,f=ef,mi=emi,uv=euv);edge_row.update(triangles=len(ef),native_cleanup=ec)
proof={'axes_x_m':[0.,3.9,9.1,13.],'bays_m':[3.9,5.2,3.9],'axis_source':'User supplied 150122 plan crop','section_source':'Original saved KZ400mm columns and250x270mm beam definitions; not new surveyed sections','cause':'The fixed oblique return crossed the original column/beam footprint. Prior edits carved the structural joint around the window and retained chopped beam fragments.','method':'Preserve full primary framing, move only the fixed oblique return endpoints in front of the column, and bond floor/ceiling edges at their existing levels. The five central frames and all outward-opening leaves stay unchanged.','bays':bays,'fixed_return_frames':frames,'parts':parts,'ownership_scopes_m':[b['scope_bounds_m']for b in bays]+[p['scope_bounds_m']for p in plates.values()],'balcony_edge_trim':edge_trim,'outside_added_removed_m3':outside,'native_float32_volume_tolerance_m3':1e-5,'closed_house_components':len(saved.decompose()),'native_cleanup':cleanup}
out={'source':J['model'],'source_sha256':J['sha256'],'objects':[row,edge_row]+rows,'archive':[],'proof':proof}
(D/'Prepared.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
print('PREPARED',len(bays),'bays',len(frames),'fixed returns','outside',outside,flush=True)
for q in frames:print('FRAME_CORE',q['name'],q['old_frame_core_overlap_m3'],q['new_frame_core_overlap_m3'],q['actual_new_frame_max_y_m'],flush=True)
