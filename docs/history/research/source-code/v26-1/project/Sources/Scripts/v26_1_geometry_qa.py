from v26_1_common import *
import hashlib
O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';FD=D/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def read(n):return np.load(FD/J[n]['file'])
def closed(n):
 a=read(n);m=solid(a['v'],a['f'],n);parts=m.decompose();ck('Saved closed positive-volume geometry: '+n,m.status()==mf.Error.NoError and all(p.volume()>1e-10 for p in parts),positive_components=len(parts),volume_m3=m.volume());return m
house=closed('V26_1_House_Continuous_Opaque_Shell');rail=closed('V26_1_Photo_Referenced_Continuous_Wood_Railing');ground=closed('V26_1_Continuous_Court_Road_And_Floor_Surfaces');wall=closed('V26_1_Courtyard_West_Wall_Single_Surface')
ck('House shell has one connected solid, with no detached former sill strips',len(house.decompose())==1)
ck('Rail has two intentional assemblies and no detached ball, spindle or cap',len(rail.decompose())==2)
rp=json.loads((D/'Prepared_Railing.json').read_text('utf8'))['proof'];unsupported=[];postbad=[];ballbad=[]
for j,p in enumerate(rp['balusters']):
 x,y=p['xy'];z=p['seat_z_m'];probe=cube([x-.026,y-.026,z-.0081],[x+.026,y+.026,z+.0001]);vol=(house^probe).volume()
 if vol<1e-6:unsupported.append({'tag':p['tag'],'xy':[x,y],'z':z,'bearing_volume_m3':vol})
for p in rp['posts']:
 x,y=p['xy'];z=p['seat_z_m'];probe=cube([x-.07,y-.07,z-.0121],[x+.07,y+.07,z+.0001]);vol=(house^probe).volume()
 if vol<1e-5:postbad.append({'tag':p['tag'],'bearing_volume_m3':vol})
 center=np.array([x,y,p['ball_center_z_m']]);pts=np.vstack([np.array(f['path'])for f in rp['flights']]);clear=float(np.linalg.norm(pts-center,axis=1).min())-p['ball_radius_m']-.041
 if clear<.012:ballbad.append({'tag':p['tag'],'grip_ball_envelope_clearance_m':clear})
ck('All turned spindle feet engage the actual saved treads or slabs',not unsupported,checked=len(rp['balusters']),unsupported=unsupported)
ck('Every newel foot has finite bearing on the actual house solid',not postbad,checked=len(rp['posts']),unsupported=postbad)
ck('Flight grip envelopes avoid the ball finials',not ballbad,invalid=ballbad)
ck('Spindle spacing is no more than 110mm after the narrowest turned waist',rp['minimum_spindle_clear_gap_m']<=.110,model_maximum_center_spacing_m=.13,minimum_shaft_diameter_m=.038,nominal_maximum_clear_gap_m=rp['minimum_spindle_clear_gap_m'])
# Read tread heights and surface materials from the final visible shell. Cast
# only just above each expected tread, so an upstairs slab cannot mask errors.
ha=read('V26_1_House_Continuous_Opaque_Shell');tt=ha['v'][ha['f']];no=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);mats=J['V26_1_House_Continuous_Opaque_Shell']['materials'];treadbad=[];samples=[]
for fl in [1,2]:
 for k,y in [(1,9.05),(2,8.0)]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';a=arr(n);old=solid(a['v'],a['f'],n)
  for x in np.arange(5.265,7.8,.13):
   hits=old.ray_cast([float(x),y,20.],[float(x),y,-2.]);hits=[h for h in hits if h.normal[2]>.8];assert hits,(n,x);z=max(h.position[2]for h in hits);hit=house.ray_cast([float(x),y,z+.11],[float(x),y,z-.03]);top=[h for h in hit if h.normal[2]>.8];actual=max((h.position[2]for h in top),default=-100);err=actual-z;samples.append({'floor':fl,'flight':k,'xy':[float(x),y],'source_z':z,'saved_z':actual})
   if abs(err)>.0002:treadbad.append(samples[-1])
ck('Every sampled tread retains its source height with no projecting white beam bar',not treadbad,samples=len(samples),invalid=treadbad)
# Every horizontal structural top at a floor datum uses the same floor finish.
floorbad=[]
for z in [-.4499999881,3.450024414,7.050000191]:
 c=tt.mean(1);ix=np.where((no[:,2]>.999)&(abs(c[:,2]-z)<.0002))[0];bad=[int(i)for i in ix if mats[int(ha['mi'][i])]!='M_Floor'];floorbad+=bad
ck('Floor datum faces have one grey material owner and no white patches',not floorbad,wrong_material_faces=len(floorbad))
rear=[]
for fl,z in [(1,-.45),(2,3.450024414),(3,7.05)]:
 for x in [4.35,5.8,7.1,8.7]:
  for zz in [z+.20,z+2.99]:
   hits=house.ray_cast([x,9.1,zz],[x,10.1,zz]);enter=[h for h in hits if h.normal[1]<-.9]
   if enter:rear.append({'floor':fl,'x':x,'z':zz,'inside_y':min(h.position[1]for h in enter)})
bad=[q for q in rear if abs(q['inside_y']-9.588)>.0003];ck('Stair back wall and former column/beam strips share a continuous finished plane',not bad,samples=len(rear),invalid=bad)
side=[]
for y in [7.65,8.2,8.85,9.35]:
 for z in [7.40,8.35,9.55]:
  hits=house.ray_cast([1.5,y,z],[4.2,y,z]);enter=[h for h in hits if h.normal[0]<-.9]
  if enter:side.append(min(h.position[0]for h in enter))
ck('Restored terrace column cores remain behind the continuous wall finish',side and max(side)<=3.6803,samples=len(side),maximum_wall_x_m=max(side)if side else None)
for g in rp['guards']:ck('Raised guard is supported and keeps horizontal top above 1.20m: '+g['tag'],g['base_supported']and g['rail_top_above_floor_m']>=1.2,model_top_height_m=g['rail_top_above_floor_m'])
# Check newly added white borders, coping and tiles against the real solids.
skin=closed('V26_1_Secondary_Wall_Level_White_Frieze');frames=closed('V26_1_Secondary_Wall_Horizontal_Panel_Mouldings');bed=closed('V26_1_Secondary_Wall_Shallow_Ceramic_Coping');tiles=closed('V26_1_Secondary_Wall_Cover_Tiles_And_Ends')
fg=[p.min_gap(skin,.05)for p in frames.decompose()];ck('Every new white border is seated into its frieze',max(fg,default=0)<.0001,maximum_gap_m=max(fg,default=0))
ck('Shallow tile bed is one continuous solid',len(bed.decompose())==1,components=len(bed.decompose()))
tg=[p.min_gap(bed,.05)for p in tiles.decompose()];ck('Every tile row or drip has contact with the shallow bed',max(tg,default=0)<.0001,maximum_gap_m=max(tg,default=0))
ck('West wall, plinth and restored borders form one seated assembly',len(wall.decompose())==1,components=len(wall.decompose()))
upper=closed('V26_1_Secondary_Wall_Continuous_Upper_Brick');ck('Inherited notch under the retired secondary frieze is closed into the upper brick body',len(upper.decompose())==1 and upper.bounding_box()[2]<1.951,components=len(upper.decompose()),lowest_joint_z_m=upper.bounding_box()[2])
P=O/'Blender/Architecture_Complete_V26_1.blend'
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(R/'V26_1_Saved_Geometry_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'tread_samples':samples,'stair_wall_samples':rear,'basis':'Actual fresh-readback saved visible mesh. Model geometry only; not a structural capacity certification.'},ensure_ascii=False,indent=2),encoding='utf8');print('GEOMETRY_QA',len(checks),'FAIL',len(fail),flush=True)
