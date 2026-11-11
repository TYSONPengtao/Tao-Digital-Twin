"""Verify the actual reopened intersections, level guard, piers and animated gate."""
from v26_2_common import *
from shapely.geometry import Polygon,box,shape,LineString
from shapely.ops import unary_union
import hashlib
D=W/'v26_10';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26_10');R=O/'Reports';BD=W/'v26_9/Final'
J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};BJ={r['name']:r for r in json.loads((BD/'Geometry_Index.json').read_text('utf8'))};checks=[];cache={};ch=json.loads((R/'V26_10_Changes.json').read_text('utf8'))
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('SPECIFIC',n,bool(p),kw if not p else'',flush=True)
def get(n,old=False):
 key=(n,old)
 if key not in cache:
  a=np.load((BD if old else FD)/(BJ if old else J)[n]['file']);cache[key]=(a,solid(a['v'],a['f'],n))
 return cache[key]
HN='V26_3_House_Connected_Walls_And_Stairs';ha,house=get(HN);_,oldhouse=get(HN,True);flz={1:-.44999998807907104,2:3.450024366378784,3:7.050000190734863};cz={1:3.32,2:6.92,3:10.220000267}
def polygon_section(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  a=np.asarray(p);signed=np.sum(a[:,0]*np.roll(a[:,1],-1)-np.roll(a[:,0],-1)*a[:,1]);(pos if signed>0 else neg).append(Polygon(a))
 return unary_union(pos).difference(unary_union(neg))
nodes=ch['proof']['walls']['corrections'];bad=[];sections=[];scopes=[]
for r in nodes:
 fl=r['floor'];cx=r['center_x'];roi=Polygon(r['roi_xy']);desired=shape(r['desired_outline'])
 if cx==13.:roi=roi.intersection(box(cx-.36,7.03,r['south_wall_x'][0],7.57))
 lo=[cx-.3601,7.0299,flz[fl]-.0001];hi=[cx+.3601,7.5701,cz[fl]+.0001];scopes.append(cube(lo,hi))
 for dz in [.35,1.25,2.5]:
  z=flz[fl]+dz;a=polygon_section(house,z);b=polygon_section(oldhouse,z);excess=a.intersection(roi).difference(desired.buffer(.000002)).area
  row={'floor':fl,'center_x':cx,'z_m':z,'remaining_excess_area_m2':excess,'before_outline':b.boundary.intersection(roi.buffer(.23)).__geo_interface__,'after_outline':a.boundary.intersection(roi.buffer(.23)).__geo_interface__}
  sections.append(row)
  if excess>2e-7:bad.append(row)
ck('Eleven actual wall intersections have no residual column-end ribs at three heights',not bad and len(sections)==33,samples=len(sections),invalid=bad)
scopes.append(cube([8.9798,7.3998,flz[1]-.0001],[9.0002,9.5601,cz[1]+.0001]));mask=union(scopes);out=max(0.,((house-oldhouse)-mask).volume())+max(0.,((oldhouse-house)-mask).volume())
ck('House geometry outside the eleven intersection repairs and20mm WC-face continuation is retained',out<2e-6,outside_change_m3=out)
# Trace the same real wall faces on both sides of every repaired junction.
plane_bad=[];plane_samples=[]
for r in nodes:
 fl=r['floor'];cx=r['center_x'];z=flz[fl]+1.25
 for y,plane in [(7.06,r['south_wall_x']),(7.52,r['north_wall_x'])]:
  if not plane:continue
  hs=house.ray_cast([cx-.34,y,z],[cx+.34,y,z]);xs=[q.position[0]for q in hs];row={'floor':fl,'center_x':cx,'y':y,'actual_x_m':xs,'target_x_m':plane};plane_samples.append(row)
  if len(xs)!=2 or max(abs(np.array(xs)-plane))>5e-5:plane_bad.append(row)
ck('Corrected returns follow the neighbouring finished wall planes',not plane_bad,samples=len(plane_samples),invalid=plane_bad)
rn='V26_1_Photo_Referenced_Continuous_Wood_Railing';_,ra=get(rn);_,rb=get(rn,True);rm=ch['railing_proof'];oldrm=json.loads((W/'v26_9_railing/Prepared_Railing.json').read_text('utf8'))['proof'];railmask=cube([7.76,8.59,7.03],[8.00,9.59,8.61]);outside=max(0.,((ra-rb)-railmask).volume())+max(0.,((rb-ra)-railmask).volume())
ck('All sloping flights, half turns and the previously lowered front guard retain their source geometry',outside<2e-7 and rm['flights']==oldrm['flights']and rm['wreaths']==oldrm['wreaths'],outside_change_m3=outside)
tops=[]
for y in np.linspace(8.68,9.36,18):
 hs=ra.ray_cast([7.88,y,8.30],[7.88,y,7.8]);tops.append(max((q.position[2]for q in hs if q.normal[2]>.4),default=-999))
posts=[q for q in rm['posts']if q['tag']in['Floor 3','F3 rear guard end']];target=posts[0]['collar_z_m']+.029
ck('Saved rear guard is horizontal between the two newel collars',len(posts)==2 and abs(posts[0]['collar_z_m']-posts[1]['collar_z_m'])<1e-9 and max(tops)-min(tops)<.00001 and max(abs(np.array(tops)-target))<.00001,samples=len(tops),top_range_m=[min(tops),max(tops)],collars_m=[q['collar_z_m']for q in posts])
fin=[]
for y in [8.55,9.49]:
 hs=ra.ray_cast([7.88,y,8.45],[7.88,y,8.06]);fin.append(max(q.position[2]for q in hs))
ck('Both actual newel ball tops are level; rail remains two closed assemblies',max(fin)-min(fin)<.00001 and len(ra.decompose())==2,newel_ball_top_z_m=fin,closed_assemblies=len(ra.decompose()),balusters=rm['baluster_count'])
pn='V26_10_Inner_Gate_Rectangular_Stone_Piers';_,piers=get(pn);_,platform=get('SITE_V21_GATE_REFERENCE_LAYER_01_Geometry');pb=[]
for x0,x1 in [(4.9333333969,5.4571428571),(7.7428571429,8.2666664124)]:
 # Sampling a plain strip avoids frame projection and the ornamental waist.
 hs=piers.ray_cast([x0-.1,-11.38,1.5],[x1+.1,-11.38,1.5]);dy=piers.ray_cast([(x0+x1)/2,-12.0,2.35],[(x0+x1)/2,-11.0,2.35]);pb.append({'width_m':hs[-1].position[0]-hs[0].position[0],'depth_m':dy[-1].position[1]-dy[0].position[1]})
ck('Both gate piers have complete rectangular cores with physical depth',len(piers.decompose())==2 and all(abs(p['width_m']-.52380946)<.0001 and abs(p['depth_m']-.576)<.0001 for p in pb),measurements=pb)
un=piers+platform;feet=[]
for x in [4.81,5.2,6.6,8.,8.39]:
 hs=un.ray_cast([x,-12.1,-.30],[x,-12.1,-.85]);feet.append({'x':x,'surface_z_m':max((q.position[2]for q in hs if q.normal[2]>.8),default=-999)})
ck('One continuous100mm front tread spans both flared pier bases without a platform gap',len(un.decompose())==1 and all(abs(q['surface_z_m']+.5)<.0001 for q in feet),front_tread_samples=feet,front_step_rise_m=.1,bonded_components=len(un.decompose()))
waists=[]
for x in [5.20,8.0]:
 h=piers.ray_cast([x,-12.0,.67],[x,-11.8,.67]);waists.append(h[0].position[1]if h else None)
ck('Horizontal waist courses wrap both rectangular piers',all(y is not None and y<-11.89 for y in waists),front_y_m=waists)
rbad=[]
for r in ch['proof']['gate']['upper_reliefs']:
 a,m=get(r['name']);edges=np.sort(np.vstack([a['f'][:,[0,1]],a['f'][:,[1,2]],a['f'][:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
 if len(m.decompose())!=1 or not np.all(counts==2)or m.volume()<1e-8:rbad.append(r['name'])
ck('All six added upper floral panels are closed positive native relief solids',not rbad,invalid=rbad)
# The inherited gate doors are CAD skins, not watertight solids. Their
# evaluated surface/solid clearance is measured in Gate_Clearance_QA.
invalid=[]
for n in ch['geometry_changed']:
 a,m=get(n)
 if m.volume()<=0 or not np.isfinite(a['v']).all()or not np.isfinite(a['uv']).all():invalid.append(n)
ck('All ten changed saved geometry objects remain finite positive closed solids',not invalid,objects=len(ch['geometry_changed']),invalid=invalid)
(D/'Wall_Sections_Before_After.json').write_text(json.dumps({'sections':sections,'wall_plane_samples':plane_samples},ensure_ascii=False,indent=2),'utf8')
P=O/'Blender/Architecture_Complete_V26_10.blend'
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(R/'V26_10_Specific_Geometry_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'basis':'Actual saved native meshes reopened; fitted geometry checks, not new site survey dimensions'},ensure_ascii=False,indent=2),'utf8');print('SPECIFIC_DONE',len(checks),len(fail),flush=True)
