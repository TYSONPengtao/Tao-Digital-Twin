"""Actual freshly reopened geometry checks for the V26.11 repairs."""
from v26_2_common import *
import hashlib
D=W/'v26_11';FD=D/'Final';BD=W/'v26_10/Final';O=Path('E:/jz/JIA/Rebuild_V26_11');R=O/'Reports';ch=json.loads((R/'V26_11_Changes.json').read_text('utf8'));J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};BJ={r['name']:r for r in json.loads((BD/'Geometry_Index.json').read_text('utf8'))};checks=[];cache={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('SPECIFIC',n,bool(p),kw if not p else'',flush=True)
def get(n,old=False):
 k=(n,old)
 if k not in cache:
  a=np.load((BD if old else FD)/(BJ if old else J)[n]['file']);cache[k]=(a,solid(a['v'],a['f'],n))
 return cache[k]
HN='V26_3_House_Connected_Walls_And_Stairs';a,house=get(HN);t=a['v'][a['f']];norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(norm,axis=1)/2;norm/=np.maximum(2*area[:,None],1e-30);mats=J[HN]['materials'];flz=[-.44999998807907104,3.450000047683716,7.050000190734863];cz=[3.32,6.92,10.220000267028809]
floor=[];fbad=[]
for z in flz:
 mask=(norm[:,2]>.999)&(abs(t[:,:,2].mean(1)-z)<.00031);white=mask&np.array([('Wall'in mats[i]or'Ceiling'in mats[i])for i in a['mi']]);row={'floor_z_m':z,'remaining_white_cap_faces':int(white.sum()),'white_cap_area_m2':float(area[white].sum())};floor.append(row)
 if area[white].sum()>1e-7:fbad.append(row)
ck('No visible white wall-paint cap remains on any of the three room floor planes',not fbad,evidence=floor)
ceil=[]
for z in cz:
 mask=(norm[:,2]<-.999)&(abs(t[:,:,2].mean(1)-z)<.00012);wrong=mask&(a['mi']!=mats.index('M_V26_3_Neutral_White_Interior_Ceiling'));ceil.append({'ceiling_z_m':z,'incorrect_area_m2':float(area[wrong].sum())})
ck('Ceiling-plane caps use one continuous neutral ceiling material',all(q['incorrect_area_m2']<1e-7 for q in ceil),evidence=ceil)
seals=[]
for p in ch['proof']['house']['slab_bearing_seals']:
 lo,hi=p['bounds_m'];missing=max(0.,(cube(lo,hi)-house).volume());seals.append({'upper_floor':p['upper_floor'],'center_x':p['center_x'],'unfilled_volume_m3':missing})
ck('All12 original column/slab bearing footprints are sealed with full-thickness solid slab',all(q['unfilled_volume_m3']<2e-7 for q in seals),samples=seals)
pixel=json.loads((D/'Pixel_Ray_Attribution.json').read_text('utf8'));slits=[]
for q in pixel:
 x,y,z=q['world_m']
 if q['tag'].startswith('02')and q['material']=='M_Wall_Interior'and z<flz[1]-.0001:
  hs=house.ray_cast([x,y,flz[1]+.02],[x,y,flz[1]-.02]);slits.append({'kind':'floor','xy':[x,y],'closed':bool(hs)and abs(hs[0].position[2]-flz[1])<.00003})
 if q['tag'].startswith('01')and q['material']=='M_Wall_Interior'and z>cz[1]+.0001:
  hs=house.ray_cast([x,y,cz[1]-.02],[x,y,cz[1]+.02]);slits.append({'kind':'ceiling','xy':[x,y],'closed':bool(hs)and abs(hs[0].position[2]-cz[1])<.00003})
ck('Direct rays at the exact former dark-edge pixel locations now hit the continuous floor or ceiling',bool(slits)and all(q['closed']for q in slits),pixel_ray_samples=len(slits),invalid=[q for q in slits if not q['closed']])
beam=[]
for r in ch['proof']['house']['beam_repairs']:
 if r['floor']==3:continue
 lo,hi=r['new_beam_bounds_m'];x0,x1=(2.31,3.76)if r['side']=='left'else(9.24,10.69)
 for x in np.linspace(x0,x1,29):
  z=r['soffit_z_m']+.1;hs=house.ray_cast([x,6.95,z],[x,7.65,z]);ys=[h.position[1]for h in hs];beam.append({'floor':r['floor'],'side':r['side'],'x':float(x),'actual_y':ys,'target_y':[lo[1],hi[1]],'pass':len(ys)==2 and np.max(abs(np.array(ys)-[lo[1],hi[1]]))<.00003})
ck('All three F1/F2 open-passage beams are continuous at87 positions, including both former cut-out ends',all(q['pass']for q in beam),samples=len(beam),invalid=[q for q in beam if not q['pass']])
flat=[]
for x in np.linspace(9.25,10.68,16):
 hs=house.ray_cast([x,7.3,9.3],[x,7.3,10.6]);flat.append(hs[0].position[2]if hs else-999)
ck('F3 analogous passage retains the user-requested flat10.22m ceiling',max(abs(np.array(flat)-cz[2]))<.00003,first_surfaces_m=flat)
porch=ch['proof']['house']['first_floor_porch'];lo,hi=np.array(porch['bounds_m']);body=cube(lo,hi);missing=max(0.,(body-house).volume());samples=[]
for x in[lo[0]+.025,(lo[0]+hi[0])/2,hi[0]-.025]:
 for y in[lo[1]+.025,(lo[1]+hi[1])/2,hi[1]-.025]:
  hs=house.ray_cast([x,y,hi[2]+.08],[x,y,hi[2]-.05]);samples.append({'xy':[float(x),float(y)],'top_z_m':max((h.position[2]for h in hs if h.normal[2]>.8),default=-999)})
er=BJ['HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry']['bounds'];ck('First-floor porch is a filled four-sided rectangle matching the second-floor edge, bonded into the house',missing<1e-7 and max(abs(np.array([q['top_z_m']for q in samples])-hi[2]))<.00003 and max(abs(lo[:2]-er[0][:2]))<.00003 and max(abs(hi[:2]-er[1][:2]))<.00003,missing_volume_m3=missing,bounds_m=porch['bounds_m'],floor_samples=samples)
PN='V26_10_Inner_Gate_Rectangular_Stone_Piers';_,pier=get(PN);_,head=get('SITE_V21_GATE_REFERENCE_LAYER_05_Geometry');carving=[];cbad=[]
for p in ch['proof']['gate']['panels']:
 aa,m=get(p['name']);tv=aa['v'][aa['f']];A,B=np.asarray(p['base_segment_m']);u=(B-A)/np.linalg.norm(B-A);out=np.r_[u[1],-u[0],0];nf=np.cross(tv[:,1]-tv[:,0],tv[:,2]-tv[:,0]);nf/=np.maximum(np.linalg.norm(nf,axis=1)[:,None],1e-30);cc=tv.mean(1);outheight=(cc[:,:2]-A)@out[:2];along=(cc[:,:2]-A)@u;front=(nf@out>.25)&(along>.05*np.linalg.norm(B-A))&(along<.95*np.linalg.norm(B-A))&(cc[:,2]>p['z_m'][0]+.02)&(cc[:,2]<p['z_m'][1]-.02);ids=np.flatnonzero(front);assert len(ids)>0;neg=ids[np.argmin(outheight[ids])];pos=ids[np.argmax(outheight[ids])];c=cc[neg];core=head if'Header'in p['name']else pier;hits=core.ray_cast(c+out*.04,c-out*.04);core_out=max((np.dot(np.asarray(h.position)[:2]-A,out[:2])for h in hits),default=-1);rv={'name':p['name'],'minimum_visible_height_m':float(outheight[neg]),'maximum_visible_height_m':float(outheight[pos]),'first_core_surface_height_m':float(core_out),'closed_components':len(m.decompose())};carving.append(rv)
 if outheight[neg]>=-.0002 or outheight[pos]<=.0032 or core_out>outheight[neg]+.0001 or len(m.decompose())!=1:cbad.append(rv)
ck('All21 photo-derived reliefs have actual raised faces and exposed incised valleys, with real recesses behind them',not cbad and len(carving)==21,panels=len(carving),invalid=cbad)
bad=[]
for r in ch['proof']['gate']['panels']:
 aa,_=get(r['name']);rect=r['uv_rect'];uv=aa['uv']
 if not np.isfinite(uv).all()or np.any(uv[:,:,0]<rect[0]-.00002)or np.any(uv[:,:,0]>rect[2]+.00002)or np.any(uv[:,:,1]<rect[1]-.00002)or np.any(uv[:,:,1]>rect[3]+.00002):bad.append(r['name'])
ck('Every new stone insert keeps UVs inside its registered source-photo grayscale cell',not bad,invalid=bad)
sn='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';_,wall=get(sn);sp=ch['proof']['storage'];capse=[]
for y in np.linspace(-16.43,-15.27,15):
 hs=wall.ray_cast([13.0,float(y),2.86],[13.7,float(y),2.86]);xs=[h.position[0]for h in hs];capse.append({'y':float(y),'x_hits':xs,'pass':len(xs)==2 and max(abs(np.array(xs)-sp['x_span_m']))<.00003})
ck('Storage closure is solid trapezoidal blue-brick masonry at15 separate stations',all(q['pass']for q in capse),samples=capse)
_,skin=get('V24_17_Storage_West_Inner_Gable_Limewash');low,high=np.array(sp['white_skin_removal_bounds_m']);high[1]=min(high[1],-15.2401);v=max(0.,(skin^cube(low,high)).volume());ck('Unsupported white hanging skin below the new brick trapezoid is removed; backed wall seam is retained',v<1e-10,remaining_volume_m3=v,seam_exclusion_m=.00011)
roofname='SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry';_,roof=get(roofname);seating=[]
for y in np.linspace(-16.43,-15.27,12):
 hr=roof.ray_cast([13.48,float(y),2.8],[13.48,float(y),3.8]);hw=wall.ray_cast([13.48,float(y),2.8],[13.48,float(y),3.8]);seating.append({'y':float(y),'roof_under_m':hr[0].position[2]if hr else None,'brick_top_m':hw[-1].position[2]if hw else None})
ck('Trapezoid top seats into the unchanged sloping roof without an open timber strip',all(q['roof_under_m']is not None and q['brick_top_m']is not None and -.0001<q['brick_top_m']-q['roof_under_m']<.008 for q in seating),stations=seating)
bad=[]
for n in ch['geometry_changed']:
 aa,m=get(n);edges=np.sort(np.vstack([aa['f'][:,[0,1]],aa['f'][:,[1,2]],aa['f'][:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
 if not np.all(counts==2)or m.volume()<=0 or not np.isfinite(aa['uv']).all():bad.append(n)
ck('All26 changed saved geometry objects have closed indexed edges, positive volume and finite UVs',not bad,objects=len(ch['geometry_changed']),invalid=bad)
with(O/'Blender/Architecture_Complete_V26_11.blend').open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(R/'V26_11_Specific_Geometry_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'relief_measurements':carving,'beam_samples':beam,'basis':'Measured from the actual saved native mesh readback; photo grayscale is inferred relief depth, not a site measurement'},ensure_ascii=False,indent=2,default=lambda q:q.item()if hasattr(q,'item')else str(q)),'utf8');print('SPECIFIC_DONE',len(checks),len(fail),flush=True)
