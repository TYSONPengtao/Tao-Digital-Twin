from pathlib import Path
import sys,json,re
W=Path(__file__).parent;D=W/'v26';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,union
I={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};S={};checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
for n,r in I.items():
 if n.startswith(('KZ_','BEAM_','SLAB_JOINED','FACADE_CONTINUOUS','PARTITIONS_JOINED','STAIR_F','STAIR_LANDING','V26_Stair_','ROOF_MAIN')):
  a=np.load(FD/r['file'])
  try:S[n]=solid(a['v'],a['f'],n)
  except Exception as ex:ck('Closed solid '+n,False,error=str(ex))
ck('All 83 saved structural meshes are valid closed positive-volume solids',len(S)==sum(n.startswith(('KZ_','BEAM_','SLAB_JOINED','FACADE_CONTINUOUS','PARTITIONS_JOINED','STAIR_F','STAIR_LANDING','V26_Stair_','ROOF_MAIN'))for n in I),solids=len(S))
def volume(a,b):return max(0.,(a^b).volume())
def finite_contact(a,b):
 inter=volume(a,b)
 if inter>1e-7:return {'intersection_m3':inter,'contact_area_estimate_m2':None,'finite_connection':True}
 areas=[];eps=.0004
 for ax in range(3):
  for sign in [-1,1]:
   d=[0.,0.,0.];d[ax]=sign*eps;areas.append(volume(a.translate(d),b)/eps)
 return {'intersection_m3':inter,'contact_area_estimate_m2':max(areas),'finite_connection':max(areas)>1e-5}

for n,m in S.items():
 if not n.startswith('KZ_'):continue
 k=re.match(r'KZ_(\d)_(\d)_F(\d)_Geometry',n);i,j,fl=map(int,k.groups());lo,hi=np.array(I[n]['bounds']);ck('Column retains 400 x 400 section '+n,np.max(np.abs((hi-lo)[:2]-.4))<2e-6,section_m=(hi-lo).tolist()[:2])
 basecontact=finite_contact(m,S[f'SLAB_JOINED_F{fl}_Geometry']);ck('Column base has finite contact at its own floor '+n,basecontact['finite_connection'],**basecontact)
 if fl<3:
  nxt=f'KZ_{i}_{j}_F{fl+1}_Geometry'
  if nxt in S:
   c=finite_contact(m,S[nxt]);ck('Vertical column joint '+n,c['finite_connection']and c['contact_area_estimate_m2']>.159,**c)
for n,m in S.items():
 if n.startswith('BEAM_'):
  k=re.match(r'BEAM_([XY])_F(\d)_([^_]+)_([^_]+)_Geometry',n);axis,fl,fixed,start=k.groups();fl=int(fl);fixed=float(fixed);start=float(start);axisgrid=[0,3.9,9.1,13.]if axis=='X'else[2.1,7.3,9.8];end=axisgrid[axisgrid.index(start)+1]
  columns=[]
  for pos in [start,end]:
   x,y=(pos,fixed)if axis=='X'else(fixed,pos);i=[0,3.9,9.1,13.].index(x)+1;j=[2.1,7.3,9.8].index(y)+1;cn=f'KZ_{i}_{j}_F{fl}_Geometry';columns.append({'column':cn,'intersection_m3':volume(m,S[cn])})
  ck('Both beam ends have finite column engagement '+n,all(r['intersection_m3']>.003 for r in columns),ends=columns)
 if n.startswith('V26_Stair_Frame_'):
  fl=int(n[-1]);cols=[(nn,volume(m,ss))for nn,ss in S.items()if nn.startswith('KZ_')and f'_F{fl}_'in nn];hits=[(nn,v)for nn,v in cols if v>1e-5];ck('Restored stair frame beam engages two columns '+n,len(hits)>=2,contacts=hits)

for fl in [2,3]:
 supporting=union([m for n,m in S.items()if n.startswith('BEAM_')and f'_F{fl-1}_'in n or n.startswith('V26_Stair_Frame_')and n.endswith(f'F{fl-1}')]);c=finite_contact(S[f'SLAB_JOINED_F{fl}_Geometry'],supporting);ck('Floor slab underside bears on the connected beam frame F'+str(fl),c['finite_connection'],**c)
for fl in [1,2]:
 land=f'STAIR_LANDING_F{fl}_Geometry';beam=f'V26_Stair_Landing_Bearing_Beam_F{fl}';m=S[land];ck('Landing bears on crossbeam F'+str(fl),volume(m,S[beam])>.003,intersection_m3=volume(m,S[beam]))
 for k in [1,2]:
  n=f'STAIR_F{fl}_FLIGHT{k}_Geometry';m=S[n];slab=f'SLAB_JOINED_F{fl if k==1 else fl+1}_Geometry';walls=union([S[f'PARTITIONS_JOINED_F{fl}_Geometry'],S[f'FACADE_CONTINUOUS_F{fl}_Geometry']]);contacts={'slab_m3':volume(m,S[slab]),'platform_beam_m3':volume(m,S[beam]),'side_wall_m3':volume(m,walls)};ck('Flight is one closed body with wall, platform beam and slab bearings '+n,len(m.decompose())==1 and all(v>1e-5 for v in contacts.values()),contacts=contacts)

wallparts=[]
for fl in [1,2,3]:
 frame=union([m for n,m in S.items()if n.startswith(('KZ_','BEAM_'))and f'_F{fl}_'in n or n.startswith('V26_Stair_Frame_')and n.endswith(f'F{fl}')]+[S[f'SLAB_JOINED_F{fl}_Geometry']]+([S[f'SLAB_JOINED_F{fl+1}_Geometry']]if fl<3 else[S['ROOF_MAIN_JOINED_Geometry']]))
 for kind in ['FACADE_CONTINUOUS','PARTITIONS_JOINED']:
  n=f'{kind}_F{fl}_Geometry'
  other=S[f'{"PARTITIONS_JOINED"if kind=="FACADE_CONTINUOUS"else"FACADE_CONTINUOUS"}_F{fl}_Geometry'];support=frame+other
  for j,m in enumerate(S[n].decompose()):
   c=finite_contact(m,support);row={'object':n,'component':j,'volume_m3':m.volume(),'bounds':list(m.bounding_box()),**c};wallparts.append(row)
   if not c['finite_connection']:print('UNSUPPORTED_WALL',row,flush=True)
ck('Every saved wall component has finite contact with floor, frame or connected crossing wall',all(r['finite_connection']for r in wallparts),components=len(wallparts),unsupported=[r for r in wallparts if not r['finite_connection']])
roof=S['ROOF_MAIN_JOINED_Geometry'];upper=union([m for n,m in S.items()if n.startswith(('KZ_','BEAM_','FACADE_CONTINUOUS','PARTITIONS_JOINED'))and ('_F3_'in n or '_F3_Geometry'in n) or n.startswith('V26_Stair_Frame_')and n.endswith('F3')]);roofcontact=finite_contact(roof,upper);ck('Roof has a finite connection to the top storey',roofcontact['finite_connection'],**roofcontact)
roofcols=[{'column':n,**finite_contact(roof,m)}for n,m in S.items()if n.startswith('KZ_')and'_F3_'in n]
fail=[r for r in checks if not r['pass']];h=json.loads((R/'V26_Build.json').read_text('utf8'))['sha256'];report={'status':'PASS_GEOMETRIC_CONNECTIONS'if not fail else'FAIL','model_sha256':h,'method':'Saved Blender mesh coordinates, exact manifold intersections and four-tenths-mm displacement contact-area estimate; no AABB-only pass','checks':checks,'wall_components':wallparts,'roof_column_contacts':roofcols,'failures':fail,'structural_capacity_verified':False,'reinforcement_verified':False,'codes_context':['GB 55008-2021','GB 55007-2021','GB 50010-2010 (2024 edition)'],'not_a_structural_safety_certificate':True};(R/'V26_Structural_Geometry_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('STRUCTURE_VERIFY_DONE',len(checks),'FAIL',len(fail),flush=True)
