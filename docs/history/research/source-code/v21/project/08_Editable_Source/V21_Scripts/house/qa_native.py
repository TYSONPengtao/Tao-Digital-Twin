import sys,json,ast,copy,math
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V21');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
Q=json.loads((D/'Mutation.json').read_text());DU=json.loads((D/'Door_Updates.json').read_text());QE={e['name']:e for e in Q['replace']+Q['add']};REM=set(Q['remove']);AE={**E,**QE}
for fn,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold'])]:
 tree=ast.parse((W/fn).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),fn,'exec'))
report={'status':'PASS_HOUSE_FINAL_NATIVE_QA','closed_solids':[],'door_contacts':[],'critical':[],'opening_checks':[],'native_baseline':'V21 actual saved-native readback caches for changed and retained geometry'}
cache={};bounds={}
def union(e):
 ps=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e);ps.append(manifold({'type':'polyhedron','vertices':v.tolist(),'faces':f}))
 return mf.Manifold.batch_boolean(ps,mf.OpType.Add)
def get(n):
 if n not in cache:
  d=np.load(B/'02_Data'/ii[n]['file']);v=d['vertices'];f=d['faces'];uv,idx=np.unique(np.round(v,7),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(uv,idx[f].astype(np.uint64)))
  if m.status()!=mf.Error.NoError:
   e=E[n];start=0;parts=[]
   for p in ex.expand_parts(e):
    pv,pf=ex.world_part(p,e);ct=len(triangles(pv,pf));ff=f[start:start+ct];start+=ct
    valid=False
    for precision in [9,8,7,6]:
     used=np.unique(ff);vv=v[used];reidx=np.full(len(v),-1,np.int64);reidx[used]=np.arange(len(used));uv,idx=np.unique(np.round(vv,precision),axis=0,return_inverse=True);pm=mf.Manifold(mf.Mesh64(uv,idx[reidx[ff]].astype(np.uint64)))
     if pm.status()==mf.Error.NoError:valid=True;break
    assert valid,(n,start,'invalid native component');parts.append(pm)
   assert start==len(f),(n,start,len(f));m=mf.Manifold.batch_boolean(parts,mf.OpType.Add)
  assert m.status()==mf.Error.NoError,(n,m.status());cache[n]=m
 return cache[n]
def bb(n):
 if n not in bounds:
  v=np.load(B/'02_Data'/ii[n]['file'])['vertices'];bounds[n]=np.array([v.min(0),v.max(0)])
 return bounds[n]
def overlap(a,b):return (a[1]>b[0]+1e-7).all() and (b[1]>a[0]+1e-7).all()
for n,e in QE.items():
 for j,p in enumerate(e['parts']):
  m=manifold(p['geometry']);vol=m.volume();assert vol>1e-11,(n,j,vol);report['closed_solids'].append({'node':n,'part':j,'volume_m3':vol})
physical=[n for n in AE if n not in REM and not n.startswith(('SITE_V14_ORIGINAL','VIS_','REF_','GRID_')) and n in ii|QE and AE[n].get('family')!='VIS_MODEL']
for dr in DU['upsert']:
 n=dr['name'];m=get(n);vbox=bb(n);contacts=[]
 for cn in physical:
  if cn==n or not overlap(vbox,bb(cn)):continue
  try:vol=(m^get(cn)).volume()
  except Exception as e:report['critical'].append({'door':n,'collider':cn,'error':str(e)});continue
  if vol>1e-7:contacts.append({'collider':cn,'volume_m3':vol});report['critical'].append({'door':n,'collider':cn,'volume_m3':vol})
 report['door_contacts'].append({'door':n,'default_pose_collisions':contacts})
 if dr['operation']=='SLIDING':
  step=[]
  for t in [0,.25,.5,.75,1]:
   moved=m.translate((-np.array(dr['open_translation_m'])*(1-t)).tolist());bo=np.array(moved.bounding_box()).reshape(2,3)
   for cn in physical:
    if cn==n or cn.startswith('DOOR_FRONT_CENTER') or not overlap(bo,bb(cn)):continue
    vol=(moved^get(cn)).volume()
    if vol>1e-7:step.append({'sample':t,'collider':cn,'volume_m3':vol})
  report['door_contacts'][-1]['translation_sweep_collisions']=step;report['critical']+=step
# True blocked/clear volumes, using final partition and retained F1 infill.
def cube(origin,size):return manifold({'type':'box','origin':origin,'size':size})
for title,n,origin,size,mode in [
 ('F3 wrong north doorway now solid','PARTITIONS_JOINED_F3',[9.02,7.60,7.55],[.16,.8,2.0],'filled'),
 ('F3 right bedroom south doorway clear','PARTITIONS_JOINED_F3',[8.99,6.20,7.51],[.22,.8,2.04],'clear'),
 ('F3 terrace exit clear','PARTITIONS_JOINED_F3',[3.79,6.20,7.51],[.22,.8,2.04],'clear'),
 ('F1 red rear gap infill retained','HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS',[9.31,7.22,.02],[1.37,.16,3.30],'filled'),
 ('F1 red stair enclosure retained','HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS',[4.2,7.22,.02],[3.5,.16,3.30],'filled')]:
 c=cube(origin,size);over=(get(n)^c).volume();ratio=over/c.volume();ok=ratio>.999 if mode=='filled' else ratio<.0001
 report['opening_checks'].append({'test':title,'ratio':ratio,'passed':ok});assert ok,(title,ratio)
# Full-height infill reaches actual retained beams; test combined geometry, not
# just infill (which is intentionally trimmed to the concrete beam underside).
for title,x0,width,beam in [('F1 red rear partition full-height sealed',9.31,1.37,'BEAM_X_F1_7.3_9.1'),('F1 stair enclosure full-height sealed',4.2,3.5,'BEAM_X_F1_7.3_3.9')]:
 c=cube([x0,7.22,.02],[width,.16,3.65]);solid=get('HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS')+get(beam);ratio=(solid^c).volume()/c.volume();assert ratio>.99999,(title,ratio)
 report['opening_checks'].append({'test':title,'infill_and_beam_volume_ratio':ratio,'passed':True,'retained_beam':beam})
# Finish area and floor-surface support are independently bounded.
R=json.loads((D/'Design_Control.json').read_text());area={s:sum(q['source_projected_area_m2'] for q in R['checks']['exterior_finish'] if '_'+s.upper()+'_' in q['node']) for s in ['rear','west','east']};report['exterior_face_area_m2']=area;report['terrace_tile_m2']=R['checks']['terrace_tile_area_m2'];assert area['rear']>80 and area['east']>50 and report['terrace_tile_m2']>10
if report['critical']:report['status']='FAIL_HOUSE_FINAL_NATIVE_CONTACT_REVIEW'
(D/'House_Native_QA.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['closed_solids','door_contacts']},indent=2));print('QA',report['status'],len(report['closed_solids']))

