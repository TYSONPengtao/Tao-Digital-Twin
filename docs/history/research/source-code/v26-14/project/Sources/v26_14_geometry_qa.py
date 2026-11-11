from v26_2_common import *
import hashlib
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
D=W/'v26_14';O=Path('E:/jz/JIA/Rebuild_V26_14');P=O/'Blender/Architecture_Complete_V26_14.blend';ch=json.loads((O/'Reports/V26_14_Changes.json').read_text('utf8'));prep=ch['proof'];src=json.loads((D/'Source_Index.json').read_text('utf8'));r=next(r for r in src['objects']if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(D/r['file']);b=np.load(D/'Saved_House.npz');old=solid(a['v'],a['f']);new=solid(b['v'],b['f']);scopes=[cube(p['bounds_m'][0],p['bounds_m'][1])for p in prep['patches']+prep['head_seats']];mask=union(scopes);checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('GEOMETRY_QA',n,bool(p),kw if not p else'',flush=True)
added=new-old;removed=old-new;outside=max(0.,(added-mask).volume())+max(0.,removed.volume())
ck('Actual saved geometry differs only within four wall returns and four partition-head seats',outside<2e-7,outside_change_m3=outside,added_m3=added.volume(),removed_m3=removed.volume())
ck('Saved house remains one positive connected shell',len(new.decompose())==1 and new.volume()>0,components=len(new.decompose()),volume_m3=new.volume())
ck('Saved added volume equals the prepared local repair',abs(added.volume()-sum(p['added_m3']for p in prep['patches']+prep['head_seats']))<2e-6)
def section(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  p=np.asarray(p);sgn=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);(pos if sgn>0 else neg).append(Polygon(p))
 return unary_union(pos).difference(unary_union(neg))
sections=[]
for p in prep['patches']:
 cx=p['adjacent_finished_x_m'];roi=box(cx-.40,6.95,cx+.40,7.82);z=p['bounds_m'][0][2]+1.25
 sections.append({'floor':p['floor'],'side':p['side'],'z_m':z,'target_x':cx,'before':section(old,z).intersection(roi).__geo_interface__,'after':section(new,z).intersection(roi).__geo_interface__})
(D/'Sections_Before_After.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),'utf8')
fail=[q for q in checks if not q['pass']];(O/'Reports/V26_14_Geometry_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
