"""Remove submillimetre trim remnants and restore floor/ceiling provenance."""
from v26_2_common import *
import v26_2_common as C
from v26_8_native_cleanup import repair_native
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
D=W/'v26_11';D.mkdir(exist_ok=True);C.D=D;FD=W/'v26_10/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';r=J[HN];a=np.load(FD/r['file']);mats=r['materials'];flz=[-.44999998807907104,3.450000047683716,7.050000190734863];cz=[float(np.float32(z))for z in[3.32,6.92,10.220000267028809]];snaps=[]
old_t=a['v'][a['f']];old_n=np.cross(old_t[:,1]-old_t[:,0],old_t[:,2]-old_t[:,0]);old_n/=np.maximum(np.linalg.norm(old_n,axis=1)[:,None],1e-30);house=tracked(a['v'],a['f'],mats,a['mi'],a['uv'],HN);beam_repairs=[];slab_seals=[]
def extrude(p,z0,z1):
 rings=[]
 for q in (p.geoms if hasattr(p,'geoms')else[p]):
  if q.area<1e-12:continue
  q=orient(q,1);rings.append(np.array(q.exterior.coords)[:-1]);rings.extend(np.array(h.coords)[:-1]for h in q.interiors)
 return mf.CrossSection(rings,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
for z in flz:
 mask=(old_n[:,2]>.999)&(old_t[:,:,2].min(1)>z+.000001)&(old_t[:,:,2].max(1)<z+.00031)
 polys=[Polygon(q[:,:2])for q in old_t[mask]if Polygon(q[:,:2]).area>1e-12];domain=unary_union(polys)
 if not domain.is_empty:house-=finish(extrude(domain,z,z+.001),'M_Floor','Cut only exposed submillimetre floor-cap footprints down to their adjacent real floor plane')
 snaps.append({'plane':'floor','target_z_m':z,'cap_triangles':int(mask.sum()),'footprint_m2':domain.area,'maximum_old_offset_m':float((old_t[mask,:,2]-z).max(initial=0))})
for z in cz:
 mask=(old_n[:,2]<-.999)&(old_t[:,:,2].max(1)<z-.000001)&(old_t[:,:,2].min(1)>z-.00011)
 polys=[Polygon(q[:,:2])for q in old_t[mask]if Polygon(q[:,:2]).area>1e-12];domain=unary_union(polys)
 if not domain.is_empty:house-=finish(extrude(domain,z-.001,z),'M_V26_3_Neutral_White_Interior_Ceiling','Remove only microscopic down-facing ceiling cap footprints')
 snaps.append({'plane':'ceiling','target_z_m':z,'cap_triangles':int(mask.sum()),'footprint_m2':domain.area})
# At the old rear column intersections the slab stopped at its original
# column/finish outline. Trimming the visible column body exposed narrow
# slits down through the130mm slab. Seal the whole local bearing footprint,
# at the existing upper floor and lower ceiling planes, not with a skin.
for upper,lower in[(1,cz[0]),(2,cz[1])]:
 for x in[0.,2.2,3.9,9.1,10.8,13.]:
  lo=[max(.12,x-.31),6.99,lower];hi=[min(12.88,x+.31),7.61,flz[upper]];b=cube(lo,hi);bb=b.to_mesh64();bv=np.asarray(bb.vert_properties[:,:3]);bf=np.asarray(bb.tri_verts);bn=np.cross(bv[bf][:,1]-bv[bf][:,0],bv[bf][:,2]-bv[bf][:,0]);bmi=np.full(len(bf),mats.index('M_Wall_Interior'),int);bmi[bn[:,2]>0]=mats.index('M_Floor');bmi[bn[:,2]<0]=mats.index('M_V26_3_Neutral_White_Interior_Ceiling');house+=tracked(bv,bf,mats,bmi,uv_project(bv,bf),'Continuous slab bearing at old column-outline slit');slab_seals.append({'upper_floor':upper+1,'center_x':x,'bounds_m':[lo,hi]})
for fl,under in[(1,3.049999952316284),(2,6.649975776672363)]:
 for label,x0,x1,seat0,seat1 in [('left',2.28999,3.78001,2.11,4.02),('right',9.21999,10.71001,8.98,10.89)]:
  if fl==1 and label=='right':continue # The F1 right WC has a solid front wall and a perpendicular100mm divider, not an open passage.
  # Replace the interrupted aperture beam, preserving the seated wall
  # ends. A mid-height wall silhouette cannot represent its upper beam.
  region=cube([x0,7.03,under-.00001],[x1,7.57,cz[fl-1]]);house-=finish(region,'M_Wall_Interior','Remove notched beam fragments only above the original beam soffit')
  w0,w1=(7.2,7.4)if fl==1 and label=='right'else(7.18,7.42)
  b=cube([seat0,w0,under],[seat1,w1,cz[fl-1]+.0001]);ba=b.to_mesh64();bv=np.asarray(ba.vert_properties[:,:3]);bf=np.asarray(ba.tri_verts);bn=np.cross(bv[bf][:,1]-bv[bf][:,0],bv[bf][:,2]-bv[bf][:,0]);bmi=np.full(len(bf),mats.index('M_Wall_Interior'),int);bmi[bn[:,2]<-.0001]=mats.index('M_V26_3_Neutral_White_Interior_Ceiling');house+=tracked(bv,bf,mats,bmi,uv_project(bv,bf),'Continuous original beam over rear room passage')
  beam_repairs.append({'floor':fl,'side':label,'soffit_z_m':under,'new_beam_bounds_m':[[seat0,w0,under],[seat1,w1,cz[fl-1]+.0001]],'cause':'V26.10 wall-section cutter continued through the beam level and removed its end seats'})
# The user previously requested a flat third-floor ceiling. Clear the
# analogous right-hand opening fragment to that existing ceiling plane.
house-=finish(cube([9.21999,7.03,9.9499],[10.71001,7.57,cz[2]]),'M_V26_3_Neutral_White_Interior_Ceiling','F3 continuation of the user-requested flat ceiling over the room passage');beam_repairs.append({'floor':3,'side':'right','flat_ceiling_z_m':cz[2]})
temp,house=export('House_Cap_Stage',house,'Local cap footprints removed');aa=np.load(D/temp['file']);v,f,mi,uv=aa['v'],aa['f'],aa['mi'].copy(),aa['uv'].copy();mats=temp['materials'];t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-30);floor=[];ceiling=[];cleanup={'method':'Local solid subtraction at actual exposed cap footprints; no global vertex welding or floor elevation overlay'}
for z in flz:
 mask=(n[:,2]>.999)&(abs(t[:,:,2].mean(1)-np.float32(z))<.00001);white=np.array([('Wall'in mats[i]or'Ceiling'in mats[i])for i in mi]);bad=mask&white;source=(a['mi']==r['materials'].index('M_Floor'))&(old_n[:,2]>.999)&(abs(old_t[:,:,2].mean(1)-z)<.0004);needs_uv=bad|(mask&(mi==mats.index('M_Floor')))
 if needs_uv.any():
  _,newuv=remap({'v':a['v'],'f':a['f'][source],'mi':a['mi'][source],'uv':a['uv'][source]},v,f[needs_uv]);uv[needs_uv]=newuv;mi[bad]=mats.index('M_Floor')
 floor.append({'floor_z_m':z,'faces_reassigned':int(bad.sum()),'area_m2':float((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2)[bad].sum())})
for z in cz:
 mask=(n[:,2]<-.999)&(abs(t[:,:,2].mean(1)-np.float32(z))<.00012);bad=mask&(mi!=mats.index('M_V26_3_Neutral_White_Interior_Ceiling'));mi[bad]=mats.index('M_V26_3_Neutral_White_Interior_Ceiling');uv[bad]=uv_project(v,f[bad]);ceiling.append({'ceiling_z_m':z,'faces_reassigned':int(bad.sum())})
# Add the complete rectangular first-floor porch footprint, registered to
# the actual four-sided second-floor edge. Keep one150mm front step.
house=tracked(v,f,mats,mi,uv,HN);er=J['HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry'];ea=np.load(FD/er['file']);lo=ea['v'].min(0);hi=ea['v'].max(0);porch=cube([lo[0],lo[1],-.60],[hi[0],hi[1],flz[0]]);pa=porch.to_mesh64();pv=np.asarray(pa.vert_properties[:,:3]);pf=np.asarray(pa.tri_verts);pn=np.cross(pv[pf][:,1]-pv[pf][:,0],pv[pf][:,2]-pv[pf][:,0]);pmi=np.full(len(pf),mats.index('M_Wall_Exterior'),int);pmask=pn[:,2]>.00001;pmi[pmask]=mats.index('M_Floor');puv=uv_project(pv,pf);source=(a['mi']==r['materials'].index('M_Floor'))&(old_n[:,2]>.999)&(abs(old_t[:,:,2].mean(1)-flz[0])<.0004);_,puv[pmask]=remap({'v':a['v'],'f':a['f'][source],'mi':a['mi'][source],'uv':a['uv'][source]},pv,pf[pmask]);porch=tracked(pv,pf,mats,pmi,puv,'F1 complete rectangle matching the F2 balcony footprint');house+=porch
rr,house=export(HN,house,'Remove0.05–0.2mm trim leftovers at actual cap footprints; restore adjacent floor UV and neutral ceiling material; complete first-floor rectangular porch');aa=np.load(D/rr['file']);ff=aa['f'];tt=aa['v'][ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;ed=np.sort(np.vstack([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);_,ec=np.unique(ed,axis=0,return_counts=True);assert ar.min()>1e-18 and np.all(ec==2)and len(house.decompose())==1,(ar.min(),np.count_nonzero(ec!=2),len(house.decompose()));u=aa['uv'].copy();bad_uv=(~np.isfinite(u).all((1,2)))|(abs(u).max((1,2))>1000);u[bad_uv]=uv_project(aa['v'],ff[bad_uv]);np.savez_compressed(D/rr['file'],v=aa['v'],f=ff,mi=aa['mi'],uv=u);rr['native_cleanup']={'minimum_triangle_area_m2':float(ar.min()),'every_indexed_edge_has_two_faces':True,'distinct_manifold_contact_vertices_preserved':True,'unstable_legacy_UV_extrapolations_replaced':int(bad_uv.sum())}
proof={'cause':'Historical cuts left50–200micron wall-finish cap faces on room floors; Boolean cap material was wall paint. Original slab boundaries around old column finishes also left narrow open slits through the130mm storey slab. The beam-level wall cutter removed beam ends. No floor texture bitmap corruption is involved.','slab_bearing_seals':slab_seals,'beam_repairs':beam_repairs,'floor_caps':floor,'ceiling_caps':ceiling,'micro_plane_snaps':snaps,'cleanup':cleanup,'first_floor_porch':{'bounds_m':[[float(lo[0]),float(lo[1]),-.60],[float(hi[0]),float(hi[1]),flz[0]]],'matches_second_floor_edge_xy':True,'front_rise_m':.15}}
(D/'Prepared_House.json').write_text(json.dumps({'objects':[rr],'proof':proof},ensure_ascii=False,indent=2),'utf8');print('MATERIAL_REPAIR',floor,ceiling,len(house.decompose()),flush=True)
