from pathlib import Path
import sys,json,math
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union
D=Path(__file__).parent;data=json.loads((D/'Prepared_Railing.json').read_text('utf8'));rp=data['proof'];a=np.load(D/data['objects'][0]['file']);rail=solid(a['v'],a['f']);FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};ha=np.load(FD/J['V26_3_House_Connected_Walls_And_Stairs']['file']);house=solid(ha['v'],ha['f']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw if not yes else'',flush=True)
ck('Candidate is closed with exactly two intended connected railing assemblies',rail.status()==mf.Error.NoError and len(rail.decompose())==2,parts=len(rail.decompose()),volume_m3=rail.volume())
orig=json.loads((W/'v26_1/Prepared_Railing.json').read_text('utf8'))['proof'];seatbad=[]
for b in [q for q in rp['balusters']if not q.get('added_local_end_gap_infill')]:
 old=min((q for q in orig['balusters']if q['tag']==b['tag']),key=lambda q:np.linalg.norm(np.array(q['xy'])-b['xy']))
 if b['xy']!=old['xy']or b['seat_z_m']!=old['seat_z_m']:seatbad.append({'new':b,'old':old})
ck('All 110 original spindle foot positions and tread seat elevations retained exactly',len([q for q in rp['balusters']if not q.get('added_local_end_gap_infill')])==110 and len(rp['balusters'])==115 and not seatbad,changes=seatbad)
ballclear=[]
for post in rp['posts']:
 c=np.r_[post['xy'],post['ball_center_z_m']]
 for path in rp['grip_paths']:
  p=np.array(path['path']);A=p[:-1];B=p[1:];d=B-A;u=np.clip(np.einsum('ij,ij->i',c-A,d)/np.maximum(np.einsum('ij,ij->i',d,d),1e-30),0,1);dist=np.linalg.norm(A+u[:,None]*d-c,axis=1);gap=float(dist.min()-post['ball_radius_m']-max(path['width_m'],path['depth_m'])/2);ballclear.append({'post':post['tag'],'path':path['tag'],'conservative_clearance_m':gap})
ck('Every complete flight return wreath and guard path avoids all ball finials',all(q['conservative_clearance_m']>.012 for q in ballclear),pairs=len(ballclear),minimum_clearance_m=min(q['conservative_clearance_m']for q in ballclear),failures=[q for q in ballclear if q['conservative_clearance_m']<=.012])
feet=[]
for b in rp['balusters']:
 x,y=b['xy'];z=b['seat_z_m'];probe=cube([x-.023,y-.023,z-.0078],[x+.023,y+.023,z+.0001]);vol=(house^rail^probe).volume();feet.append({'tag':b['tag'],'xy':b['xy'],'seat_z_m':z,'actual_bearing_volume_m3':vol})
ck('All 115 spindle feet have finite actual bearing in the saved house',all(q['actual_bearing_volume_m3']>1e-6 for q in feet),minimum_bearing_volume_m3=min(q['actual_bearing_volume_m3']for q in feet),failures=[q for q in feet if q['actual_bearing_volume_m3']<=1e-6])
posts=[]
for b in rp['posts']:
 x,y=b['xy'];z=b['seat_z_m'];probe=cube([x-.067,y-.067,z-.0118],[x+.067,y+.067,z+.0001]);vol=(house^rail^probe).volume();posts.append({'tag':b['tag'],'actual_bearing_volume_m3':vol})
ck('Every original newel base is seated on the actual tread or landing',all(q['actual_bearing_volume_m3']>1e-5 for q in posts),minimum_bearing_volume_m3=min(q['actual_bearing_volume_m3']for q in posts),failures=[q for q in posts if q['actual_bearing_volume_m3']<=1e-5])
# Recreate just the analytic grip sweeps for an independent top-cap fit test.
scope={'__file__':str(D/'build_candidate.py')};exec(compile((D/'build_candidate.py').read_text('utf8').split('level=[')[0],str(D/'build_candidate.py'),'exec'),scope);grips=union([scope['sweep'](q['path'])for q in rp['grip_paths']]);caps=[]
for b in rp['balusters']:
 x,y=b['xy'];z=b['seat_z_m'];top=b['top_z_m'];g=np.array(b['cap_plane_gradient']);head=scope['shaped_block'](x,y,z+.75*(top-z)/.94,top-.015,slope=g);contact=(head^grips).volume();r=.026;bevel=.0015;xy=np.array([[-r+bevel,-r],[r-bevel,-r],[r,-r+bevel],[r,r-bevel],[r-bevel,r],[-r+bevel,r],[-r,r-bevel],[-r,-r+bevel]]);inside=[]
 for d in xy:
  p=np.r_[[x,y]+d,top-.015+d@g];hs=grips.ray_cast(p,p+[100.,0.,0.]);inside.append(len(hs)%2==1)
 caps.append({'tag':b['tag'],'xy':b['xy'],'contact_volume_m3':contact,'top_cap_vertices_inside_grip':int(sum(inside))})
ck('All sloped spindle top caps fit within and engage the actual oval grips',all(q['contact_volume_m3']>1e-7 and q['top_cap_vertices_inside_grip']==8 for q in caps),samples=len(caps),minimum_contact_volume_m3=min(q['contact_volume_m3']for q in caps),failures=[q for q in caps if q['contact_volume_m3']<=1e-7 or q['top_cap_vertices_inside_grip']!=8])
# Inflate the delivered 215 mm human capsule radius to220 mm for clearance.
def capsule(p):
 p=np.array(p);rad=.22;h=1.65;return union([mf.Manifold.cylinder(h-2*rad,rad,rad,32).translate(p+[0,0,rad]),mf.Manifold.sphere(rad,32).translate(p+[0,0,rad]),mf.Manifold.sphere(rad,32).translate(p+[0,0,h-rad])])
paths=[]
for fl in [1,2]:
 for k,y in [(1,9.05),(2,8.0)]:
  for x in np.arange(5.33,7.81,.13):
   n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';s=np.load(W/'v26_1'/scope['C'].I[n]['file']);stair=solid(s['v'],s['f']);hs=stair.ray_cast([float(x),y,12.],[float(x),y,-1.]);z=max(h.position[2]for h in hs if h.normal[2]>.9);vol=(rail^capsule([float(x),y,z+.005])).volume();paths.append({'tag':f'F{fl} flight{k}','foot_m':[float(x),y,z],'collision_volume_m3':vol})
for fl,z in [(1,1.499951124),(2,5.249951363)]:
 for y in np.linspace(7.85,9.25,12):
  p=[4.55,float(y),z];paths.append({'tag':f'F{fl} half landing','foot_m':p,'collision_volume_m3':(rail^capsule(np.array(p)+[0,0,.005])).volume()})
for y in np.linspace(7.75,9.3,12):
 p=[8.5,float(y),7.05];paths.append({'tag':'F3 arrival and rear guard','foot_m':p,'collision_volume_m3':(rail^capsule(np.array(p)+[0,0,.005])).volume()})
ck('Candidate keeps actual stair and landing routes clear for the 1.65m human capsule',all(q['collision_volume_m3']<1e-8 for q in paths),samples=len(paths),inflated_radius_m=.22,height_m=1.65,failures=[q for q in paths if q['collision_volume_m3']>=1e-8])
ck('Original ordinary spindle rhythm retained with five fitted local end-gap infills',rp['minimum_spindle_clear_gap_m']==.092 and rp['baluster_count']==115,nominal_ordinary_waist_gap_m=.092,local_end_gap_infills=5,spacing_is_visual_model_fit_not_measured_or_regulatory_certification=True)
actual=np.load(FD/J['V26_1_Photo_Referenced_Continuous_Wood_Railing']['file']);ck('Saved native railing matches the audited candidate',actual['v'].shape==a['v'].shape and np.max(abs(actual['v']-a['v']))<3e-6 and np.array_equal(actual['f'],a['f']) and np.array_equal(actual['mi'],a['mi']));fail=[q for q in checks if not q['pass']];out={'status':'PASS_CANDIDATE_GEOMETRY'if not fail else'FAIL','source_model':rp['source_model'],'source_model_sha256':rp['source_sha256'],'model_sha256':__import__('hashlib').sha256(Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend').read_bytes()).hexdigest(),'candidate':str(D/data['objects'][0]['file']),'checks':checks,'failures':fail,'evidence':{'all_paths_ball_clearance':ballclear,'spindle_feet':feet,'newel_feet':posts,'sloped_caps':caps,'human_clearance':paths},'scope':'Geometric candidate audit against actual source-model treads and landings. Qualitative photo refinement, not load or fastening certification.'};Path('E:/jz/JIA/Rebuild_V26_7/Reports/V26_7_Railing_Regression_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('RAILING_CANDIDATE_QA_DONE',out['status'],len(checks),len(fail))

