from v26_2_common import *
from shapely.geometry import shape,Polygon
from shapely.geometry.polygon import orient
import hashlib
D=W/'v26_19';prep=json.loads((D/'Prepared.json').read_text('utf8'));J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};prepared='--prepared'in sys.argv;FD=D/('Prepared'if prepared else'Final');rows=prep['objects']if prepared else json.loads((FD/'Geometry_Index.json').read_text('utf8'));ri={r['name']:r for r in rows};HN='V26_3_House_Connected_Walls_And_Stairs';r=ri[HN];a=np.load(FD/r['file']);b=np.load(D/'Input'/ix[HN]['file']);m=solid(a['v'],a['f']);old=solid(b['v'],b['f']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('GEOMETRY_QA',n,bool(yes),kw if not yes else'',flush=True)
def prism(p,z0,z1):
 rings=[]
 for q in([p]if p.geom_type=='Polygon'else[q for q in p.geoms if q.geom_type=='Polygon']):
  q=orient(q,1);rings.append(np.asarray(q.exterior.coords,np.float32).astype(float)[:-1]);rings.extend(np.asarray(k.coords,np.float32).astype(float)[:-1]for k in q.interiors)
 return mf.CrossSection(rings,mf.FillRule.NonZero).extrude(z1-z0).translate([0,0,z0])
scopes=[prism(shape(q['scope_plan']),*q['z_scope_m'])for q in prep['proof']['head_repairs']]+[cube(*[np.asarray(v,np.float32).astype(float)for v in q['bounds_m']])for q in prep['proof']['window_jamb_alignments']];scope=union(scopes);delta=[((m-old)-scope).volume(),((old-m)-scope).volume()];ck('House changes are confined to the annotated beam/head zones and continuous window piers',max(abs(x)for x in delta)<1e-5,outside_delta_m3=delta);ck('House stays one closed positive body',len(m.decompose())==1 and m.volume()>0)
OI={q['name']:q for q in json.loads((W/'v26/Geometry_Index.json').read_text('utf8'))};beams=[]
for q in prep['proof']['head_repairs']:
 for br in q['beam_cores']:
  core=cube(*[np.asarray(v,np.float32).astype(float)for v in OI[br['source']]['bounds']]);loss=((old^core)-m).volume();beams.append({'name':br['source'],'removed_core_m3':loss,'pass':abs(loss)<1e-6})
ck('Every existing nominal beam core is retained',all(q['pass']for q in beams),beams=beams)
casings=[]
for fl,z0,z1 in[(1,3.05,3.32),(2,6.649976,6.92),(3,9.950025,10.22)]:
 for lo,hi in[([4.026 if fl<3 else 4.021,2.4,z0+.002],[4.111,7.0,z1-.002]),([9.226 if fl<3 else 9.221,2.4,z0+.002],[9.311,7.0,z1-.002])]:
  c=cube(lo,hi);casings.append({'floor':fl,'bounds_m':[lo,hi],'before_m3':(old^c).volume(),'after_m3':(m^c).volume()})
ck('Oversized beam-side roof/finish encasements are absent outside the retained wall and beam faces',all(abs(q['after_m3'])<1e-8 for q in casings),samples=casings)
glazing=[];added=m-old
for wr in J['objects']:
 n=wr['name']
 if not n.endswith('_Geometry')or not n.startswith(('WINDOW_LEFT_','WINDOW_BACK_','BAY_WINDOW_')):continue
 lo,hi=np.asarray(wr['bounds']);aa=lo.copy();bb=hi.copy()
 if n.startswith('WINDOW_LEFT_'):aa[1]+=.06;bb[1]-=.06
 else:aa[0]+=.06;bb[0]-=.06
 aa[2]+=.06;bb[2]-=.06
 if np.all(bb>aa):v=(added^cube(aa,bb)).volume();glazing.append({'window':n,'new_intrusion_m3':v,'pass':abs(v)<1e-8})
ck('New opaque geometry does not intrude into any original glazing clear area',all(q['pass']for q in glazing),windows=glazing)
stairs=[]
for q in json.loads((W/'v26_18/Prepared.json').read_text('utf8'))['proof']['joins']:
 c=cube(*[np.asarray(v,np.float32).astype(float)for v in q['scope_m']]);d=abs(((old-m)^c).volume())+abs(((m-old)^c).volume());stairs.append({'floor':q['floor_to'],'envelope_delta_m3':d,'pass':d<2e-6})
ck('V26.18 repaired stair/slab underside joints remain intact',all(q['pass']for q in stairs),joints=stairs)
well=cube([5.2001,8.5001,-.4498],[7.6999,8.5999,7.0499]);ck('The central stairwell is still open',abs((m^well).volume())<1e-8)
top=[]
for z in[-.45,3.45,7.05]:
 for x,y in[(1.,3.),(2.7,5.),(4.5,5.),(8.5,5.),(10.,4.),(12.,5.),(4.5,8.)]:
  oa=old.ray_cast([x,y,z+.15],[x,y,z-.15]);na=m.ray_cast([x,y,z+.15],[x,y,z-.15]);ok=bool(oa and na and abs(oa[0].position[2]-na[0].position[2])<.000003)or not oa and not na;top.append(ok)
ck('Original room and hall floor levels stay unchanged',all(top))
for rr in rows:
 aa=np.load(FD/rr['file']);f=aa['f'];tt=aa['v'][f];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,ct=np.unique(edges,axis=0,return_counts=True);ck('Closed indexed edges, positive faces and finite UV: '+rr['name'],np.all(ct==2)and ar.min()>1e-18 and np.isfinite(aa['uv']).all())
if'SITE_PLANTER_1_Geometry'in ri:
 rr=ri['SITE_PLANTER_1_Geometry'];aa=np.load(FD/rr['file']);pot=solid(aa['v'],aa['f']);p=prep['proof']['fixtures']['planter_model'];cx,cy=p['centre_xy_m'];hs=pot.ray_cast([cx,cy,p['top_z_m']+.1],[cx,cy,p['base_z_m']-.1]);used={rr['materials'][i]for i in aa['mi']};ck('Planter has recessed soil and ceramic finish instead of solid wood',bool(hs)and abs(hs[0].position[2]-p['soil_z_m'])<.000002 and used==set(p['new_materials']),materials=sorted(used));ck('Planter centre, base and top keep the original placement',abs(aa['v'][:,2].min()-p['base_z_m'])<.000002 and abs(aa['v'][:,2].max()-p['top_z_m'])<.000002)
else:
 ck('User-requested planter removal is included and no replacement planter is prepared','SITE_PLANTER_1_Geometry'in prep['archive']and prep['proof']['fixtures'].get('planter_choice')=='remove')
ck('Source V26.18 remains byte-identical',hashlib.sha256(Path(J['model']).read_bytes()).hexdigest()==J['sha256']);fail=[q for q in checks if not q['pass']];out={'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail}
if prepared:p=D/'Prepared_Geometry_QA.json'
else:p=Path('E:/jz/JIA/Rebuild_V26_19/Reports/V26_19_Geometry_QA.json');out['model_sha256']=hashlib.sha256((p.parent.parent/'Blender/Architecture_Complete_V26_19.blend').read_bytes()).hexdigest()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError([q['check']for q in fail])
