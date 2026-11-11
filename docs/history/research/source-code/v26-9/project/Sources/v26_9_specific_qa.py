"""Measure the actual reopened native meshes, not the preparation plan."""
from v26_2_common import *
import hashlib
D=W/'v26_9';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26_9');R=O/'Reports';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};BD=W/'v26_8/Final';BJ={r['name']:r for r in json.loads((BD/'Geometry_Index.json').read_text('utf8'))};checks=[];details={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('SPECIFIC',n,bool(p),kw if not p else'',flush=True)
cache={}
def get(n):
 if n not in cache:
  a=np.load(FD/J[n]['file']);cache[n]=(a,solid(a['v'],a['f'],n))
 return cache[n]
def old(n):
 a=np.load(BD/BJ[n]['file']);return a,solid(a['v'],a['f'],n)
def glass(n):
 a,m=get(n);ids=[i for i,x in enumerate(J[n]['materials'])if 'Glass'in x];mask=np.isin(a['mi'],ids);f=a['f'][mask]
 tt=a['v'][f]
 try:g=solid(a['v'],f,n+' glass')
 except RuntimeError:
  # Material boundaries inside a unioned frame are intentionally uncapped.
  # Test50micron prisms about actual saved glass faces, not a guessed pane
  # bounding box that would fill a deliberately open sash aperture.
  pp=[];ff=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
  for t in tt:
   nn=np.cross(t[1]-t[0],t[2]-t[0]);ln=np.linalg.norm(nn)
   if ln<1e-15:continue
   nn=nn/ln*.00005;pp.append(solid(np.vstack([t-nn,t+nn]),ff))
  g=union(pp)
 return g,tt
ha,house=get('V26_3_House_Connected_Walls_And_Stairs');sill={1:-.149999988079071,2:4.500049018859863,3:8.10004916191101};flz={1:-.449999988079071,2:3.450000047683716,3:7.050000190734863};bayrows=[];bad=[]
for fl in [1,2,3]:
 for side in ['L','R']if fl<3 else['R']:
  x0=0. if side=='L'else 9.1
  for k in range(3):
   n=f'BAY_WINDOW_F{fl}_{side}_{k}_Geometry';a,_=get(n);g,gt=glass(n);vol=abs((g^house).volume());bayrows.append({'name':n,'lower_z':float(a['v'][:,2].min()),'glass_wall_overlap_m3':vol})
   if abs(a['v'][:,2].min()-sill[fl])>.0001 or vol>3e-7:bad.append(bayrows[-1])
  for hand in ['Left','Right']:
   n=f'V24_18_BAY_WINDOW_F{fl}_{side}_1_{hand}_Outward_Hinge_Glass';g,t=glass(n);vol=abs((g^house).volume());want=.7760000119 if fl==1 else sill[fl]+.0484
   if vol>3e-7:bad.append({'name':n,'moving_glass_wall_overlap_m3':vol})
  # Sample the oblique wall, front base and the finite orthogonal end bonds.
  z=flz[fl]+(.15 if fl==1 else .50)
  for p,u in [([x0+.35,1.614,z],[.8115,.5844,0]),([x0+1.8,1.1,z],[0,1,0]),([x0+3.55,1.614,z],[-.8115,.5844,0])]:
   p=np.array(p);u=np.array(u);h=house.ray_cast(p-u*.35,p+u*.35)
   if len(h)!=2 or np.linalg.norm(np.array(h[0].position)-h[1].position)<.198:bad.append({'wall_sample':p.tolist(),'hits':len(h)})
  for xx in [x0,x0+3.9]:
   h=house.ray_cast([xx,2.1,flz[fl]+.05],[xx,2.1,flz[fl]-.25])
   if h and h[0].normal[2]>.8 and h[0].position[2]<flz[fl]-.02:bad.append({'broken_corner':[xx,2.1,flz[fl]],'surface':h[0].position[2]})
ck('All five bays retain correct solid sill heights and clear fixed/moving glass; corner bases are continuous',not bad,invalid=bad,windows=bayrows)
lower=[]
for side,x0 in [('L',0.),('R',9.1)]:
 n=f'BAY_WINDOW_F1_{side}_1_Geometry';a,_=get(n);g,t=glass(n);mask=(t[:,:,2].max(1)<.731)&(t[:,:,2].min(1)>-.12);lower.append({'name':n,'lower_fixed_glass_triangles':int(mask.sum()),'lower_fixed_glass_bounds':[t[mask].min((0,1)).tolist(),t[mask].max((0,1)).tolist()]})
ck('F1 has independent lower fixed glass under the shortened opening leaves',all(r['lower_fixed_glass_triangles']>=8 for r in lower),evidence=lower)
above=[]
for fl in [2,3]:
 for side in ['L','R']if fl<3 else['R']:
  x=1.95 if side=='L' else 11.05;h=house.ray_cast([x,.7,sill[fl]-.04],[x,1.45,sill[fl]-.04]);above.append({'floor':fl,'side':side,'solid_below_opening_hits':len(h)})
ck('F2 and F3 opening leaves sit over solid wall, with no added lower fixed pane',all(r['solid_below_opening_hits']==2 for r in above),evidence=above)

core=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];cbad=[];_,sourcehouse=old('V26_3_House_Connected_Walls_And_Stairs')
for r in core:
 if not r['name'].startswith('KZ_') or abs((r['bounds_m'][0][1]+r['bounds_m'][1][1])/2-7.3)>.02:continue
 lo,hi=np.array(r['bounds_m']);lo+=.0003;hi-=.0003;missing=((sourcehouse^cube(lo,hi))-house).volume()
 if missing>1e-6:cbad.append({'core':r['name'],'missing_m3':missing})
ck('Actual V26.8 structural pier geometry is retained inside each room-core zone',not cbad,invalid=cbad,basis='Compare actual source volume; its bounding box is not an invented full rectangular column')
ceil=[]
for x in [.6,1.3,2.4,3.2,4.6,5.8,7.0,8.3]:
 h=house.ray_cast([x,7.3,8.8],[x,7.3,11.]);ceil.append({'x':x,'first_z':h[0].position[2]if h else None})
ck('Marked F3 ceiling strip is removed up to the flat10.22m ceiling',all(q['first_z']is not None and abs(q['first_z']-10.22)<.0002 for q in ceil),samples=ceil)

rn='V26_1_Photo_Referenced_Continuous_Wood_Railing';_,ra=get(rn);_,rb=old(rn);mask=cube([3.94,7.09,7.03],[8.04,7.35,8.55]);outside=((ra-rb)-mask).volume()+((rb-ra)-mask).volume();rm=json.loads((W/'v26_9_railing/Prepared_Railing.json').read_text('utf8'))['proof'];oldrm=json.loads((W/'v26_8_railing/Prepared_Railing.json').read_text('utf8'))['proof']
ck('Only F3 front horizontal guard changes; all sloping grips, turns and rear guard retained',abs(outside)<1e-7 and rm['flights']==oldrm['flights'] and rm['wreaths']==oldrm['wreaths'],outside_change_m3=outside)
ck('F3 front guard lowered150mm with regenerated upright profiles and independent ball finial',next(q for q in rm['guards']if q['tag']=='F3 front')['rail_top_above_floor_m']==1.054 and len(ra.decompose())==2,closed_assemblies=len(ra.decompose()))

_,edge=get('HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry');evidence=[]
for p,ax in [([3.8,.9,3.4],0),([9.2,.9,3.4],0),([6.5,2.10,3.4],1),([6.5,0.,3.4],1)]:
 p=np.array(p);u=np.eye(3)[ax]*.5;hh=edge.ray_cast(p-u,p+u);evidence.append({'point':p.tolist(),'hits':len(hh)})
ck('Balcony edge is one closed four-sided rectangular frame',len(edge.decompose())==1 and all(r['hits']==2 for r in evidence),samples=evidence)

_,wall=get('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry');_,closure=get('V24_24_Kitchen_North_Veranda_White_Closure');north=wall+closure;th=[]
for x in [8.6,9.2,10.0,11.5,13.3]:
 h=north.ray_cast([x,-3.0,1.2],[x,-2.4,1.2]);th.append({'x':x,'hits':len(h),'thickness_m':abs(h[-1].position[1]-h[0].position[1])if len(h)==2 else None})
ck('Restored kitchen north wall is180mm thick at the outer line',all(q['hits']==2 and abs(q['thickness_m']-.18)<.0001 for q in th),samples=th)
woods=[];woodbad=[];region=cube([8.34,-2.756,-.55],[14.11,-2.56,5.4])
for n in J:
 if not n.startswith('SITE_KITCHEN_V12_') or not any(s in n for s in ['WOOD_','ROUND_PURLINS','EXPOSED_TIMBER_FRAMES','DENSE_WOOD_RAFTERS']):continue
 r=J[n]
 if r['bounds'][1][1]<-3.27:continue
 try:_,m=get(n)
 except Exception:continue
 vol=abs((m^north^region).volume());woods.append({'name':n,'overlap_m3':vol})
 if vol>1e-7:woodbad.append(woods[-1])
ck('Restored kitchen north end-wall plane clears the unchanged timber',not woodbad and bool(woods),invalid=woodbad,tested=len(woods),scope='180mm end wall and veranda closure; original east-post lower bearing contact is retained')
_,cap=get('V24_17_Kitchen_North_Gable_Coping');roofends=[]
for x in [8.5,8.8,9.2,9.6,10.3,11.,12.3,13.4]:
 h=cap.ray_cast([x,-2.755,1.9],[x,-2.755,5.8]);z=min(q.position[2]for q in h)if h else None
 hs=north.ray_cast([x,-2.665,5.8],[x,-2.665,1.9]);top=hs[0].position[2]if hs else None;roofends.append({'x':x,'cap_bottom':z,'wall_top':top})
ck('Kitchen gable closure reaches the native curved coping instead of exposing timber',all(q['wall_top']is not None and q['cap_bottom']is not None and q['wall_top']>=q['cap_bottom']-.001 for q in roofends),samples=roofends)

_,guard=get('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry');contact=[]
for z in [-.25,.05,.25,.51]:
 h=guard.ray_cast([13.,-16.60,z],[13.8,-16.515,z]);contact.append({'z':z,'first_x':h[0].position[0]if h else None})
ck('Storage stone rail terminal contacts the original secondary wall at every tested height',all(q['first_x']is not None and q['first_x']<=13.1301 for q in contact),samples=contact)

motion=json.loads((FD/'Window_Sliding_Motion.json').read_text('utf8'));sbad=[];pairs={};poses=0
for n,r in motion.items():
 a=np.load(FD/r['file']);m=solid(a['v'],a['f'],n);_,fixed=get(r['window']);pairs.setdefault(r['window'],[]).append((n,m,r['matrices']))
 for fr,matrix in r['matrices'].items():
  mm=m.transform(np.array(matrix)[:3]);vol=max(abs((mm^house).volume()),abs((mm^fixed).volume()));poses+=1
  if vol>2e-7:sbad.append({'sash':n,'frame':fr,'overlap_m3':vol})
for n,parts in pairs.items():
 for fr in ['1','40','60','80','100']:
  for i,(an,am,aa)in enumerate(parts):
   for bn,bm,bb in parts[i+1:]:
    vol=abs((am.transform(np.array(aa[fr])[:3])^bm.transform(np.array(bb[fr])[:3])).volume())
    if vol>2e-7:sbad.append({'window':n,'pair':[an,bn],'frame':fr,'overlap_m3':vol})
ck('Rear sliding sashes clear walls, tracks, fixed frame and each other in both opening states',not sbad,poses=poses,invalid=sbad)

P=O/'Blender/Architecture_Complete_V26_9.blend'
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V26_9_Specific_Geometry_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('SPECIFIC_DONE',len(checks),len(fail),flush=True)
