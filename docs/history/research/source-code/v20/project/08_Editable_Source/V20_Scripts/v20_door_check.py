import sys,json,math,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V19');Q=json.loads((W/'v20/Mutation.json').read_text(encoding='utf8'));I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'))};E={e['name']:e for e in Q['replace']+Q['add']}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'<solid>','exec'))
cache={}
def node(n):
 if n in cache:return cache[n]
 if n in E and E[n]['parts']:a=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in E[n]['parts']],mf.OpType.Add)
 else:
  r=I[n];d=np.load(B/'02_Data'/r['file']);vv,inv=np.unique(np.round(d['vertices'],9),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv,inv[d['faces']].astype(np.uint64)))
 assert a.status()==mf.Error.NoError,(n,a.status());cache[n]=a;return a
DM=json.loads((W/'v20/Door_Manifest.json').read_text(encoding='utf8'));rs=[];oldreview=json.loads((W/'v20_house/Door_Review.json').read_text(encoding='utf8'))
for r in DM['doors']:
 n=r['name'];a=node(n);targets=[]
 if n.startswith('DOOR_') and not n.startswith(('DOOR_STORAGE','DOOR_COURTYARD')):
  ff=next((f for f in [1,2,3] if '_F'+str(f) in n),None)
  if ff:targets+=['PARTITIONS_JOINED_F'+str(ff)]
  frame=n.rsplit('__',1)[0]+'__FRAME'
  if frame in I:targets.append(frame)
  if 'FRONT_CENTER' in n:targets.append(n.split('__')[0]+'__FIXED')
 if n.startswith('DOOR_STORAGE'):targets+=['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES']
 if n.startswith('DOOR_COURTYARD'):targets+=[n.replace('__LEAF','__FRAME'),'SITE_KITCHEN_V12_RECESSED_DOOR_STONE_THRESHOLDS']
 if n.startswith('SITE_V20_INNER_GATE__LEAF'):targets+=['SITE_INNER_STONE_GATEHOUSE','SITE_KITCHEN_TIMBER_FRAME','SITE_KITCHEN_STONE_FLOOR']
 targets+= [c['collider'] for r0 in oldreview['doors'] if r0['name']==n for c in r0['collisions']];targets=list(dict.fromkeys(targets))
 checks=[]
 for t in targets:
  if t not in I and t not in E:continue
  inter=a^node(t);v=float(inter.volume());checks.append({'target':t,'intersection_m3':v})
  if v>1e-6:
   ar=np.array(inter.to_mesh64().vert_properties)[:,:3];print('CLASH',n,t,ar.min(0).tolist(),ar.max(0).tolist(),E[n]['pivot_world_m'],flush=True)
 rs.append({'door':n,'checks':checks})
bad=[(r['door'],c['target'],c['intersection_m3']) for r in rs for c in r['checks'] if c['intersection_m3']>1e-6 and 'FIXED_HINGE_HARDWARE' not in c['target']]
(W/'v20/Door_Clearance_Source_QA.json').write_text(json.dumps({'status':'PASS_SOURCE_DOOR_CLEARANCE' if not bad else 'NEEDS_CLEARANCE_FIX','doors':rs,'failures':bad},ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(bad),flush=True)
