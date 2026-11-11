"""V22 pavilion: photo-evidenced screens, entrance stiles and rainwater detailing.
Writes an isolated parts patch only. Dimensions are photograph fitted, not surveyed.
"""
import sys,json,copy,ast,hashlib,math,shutil
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
proof={}
B=Path('E:/jz/JIA/Rebuild_V21');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v14_building.py',['part','box','beam'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]}
QA={'status':'PENDING','source_native':'E:/jz/JIA/Rebuild_V21/04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm','dimension_status':'Photo-fit non-surveyed detail dimensions; preserve registered pavilion footprint and user-specified deck clearance','checks':[]}
def check(name,ok,**data):
 QA['checks'].append({'check':name,'pass':bool(ok),**data});assert ok,(name,data)
def cube(o,s):return manifold({'type':'box','origin':o,'size':s})
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def native(n):
 a=np.load(B/'02_Data'/I[n]['file']);v=a['vertices'];f=a['faces'];vv,iv=np.unique(np.round(v,9),axis=0,return_inverse=True)
 m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,(n,m.status());return m

def put(n,parts,**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}))
 for k in ['definition','origin','angle','angle_deg','external_mesh_file','native_geometry_file','external_native_cache','v20_native_cache_override','v21_native_cache_override']:e.pop(k,None)
 e.update(parts=parts,v22_pavilion=True,source='User comparison 2026-10-15 182329/182351 and original INSV 600/625 seconds',dimension_status=QA['dimension_status'],**meta)
 (Q['replace'] if n in E else Q['add']).append(e);return e

def ps(m,mat):return [part(fromman(m),mat)]
WOOD='M_V22_Pavilion_Aged_Warm_Posts';BAMBOO='M_V22_Pavilion_Weathered_Bamboo';PVC='M_V22_Pavilion_OffWhite_PVC';METAL='M_V22_Pavilion_Aged_Gutter';CORD='M_V22_Pavilion_Screen_Cord'
Q['materials'][WOOD]={'color':[110,66,34],'roughness':.83,'bump':str(B/'03_Textures/Modeled_PBR/Wood_Relief.png'),'bump_distance_m':.00055}
Q['materials'][BAMBOO]={'color':[105,91,68],'roughness':.96}
Q['materials'][PVC]={'color':[205,203,190],'roughness':.62}
Q['materials'][METAL]={'color':[115,113,103],'roughness':.65,'metallic':.55}
Q['materials'][CORD]={'color':[65,61,47],'roughness':.96}
# 1. Keep native registered structural positions; photo differentiates the warmer
# vertical posts from the dark sheltered horizontal frame. Positive post extension
# 2 mm meets ring beams without a floating seam; bottom remains in existing shoes.
n='SITE_GAZEBO_POSTS';parts=[]
for p in E[n]['parts']:
 v,f=ex.world_part(p,E[n]);v[v[:,2]>2.13,2]+=.002
 parts.append(part({'type':'polyhedron','vertices':v.tolist(),'faces':f},WOOD))
put(n,parts,v22_detail='Warm aged timber grain on four posts; 2 mm concealed head bearing into retained ring beams')
# 2. Real front opening has three slender full-height timber stiles at each end,
# with a broad central access. These are not a continuous balustrade across entry.
stiles=[];rodsets=[[-6.79,-6.59,-6.39],[-4.31,-4.11,-3.91]]
for ys in rodsets:
 for y in ys:stiles.append(cube([3.859,y-.014,-.35738],[.028,.028,2.4921]))
 a,b=(-6.95,-6.376) if min(ys)<-6 else (-4.324,-3.75)
 stiles.append(cube([3.847,a,-.35738],[.052,b-a,.048]))
put('SITE_V22_PAVILION_FRONT_SLENDER_STILES',ps(union(stiles),WOOD),classification='PHOTO_FRONT_END_STILES_WITH_CLEAR_CENTRAL_OPENING',clear_opening_y_m=[-6.376,-4.324],photo_fit_section_m=.028)
check('Front clear central entrance >= 2m',-4.324-(-6.376)>=2,clear_width_m=2.052)
# 3. Narrow bamboo reeds in three independent side screens. The house-side north
# screen reaches near the deck (shown clearly in original 600 s view); the southern
# screen is rolled high as in 625 s, and rear curtain retains partial opening.
reeds=[];strings=[];screen_specs=[{'side':'west','lo':-6.82,'hi':-3.88,'base':.545,'top':2.045}, {'side':'north','lo':.60,'hi':3.72,'base':-.28538,'top':2.045},{'side':'south','lo':.60,'hi':3.72,'base':1.676,'top':2.045}]
for spec in screen_specs:
 side=spec['side'];lo=spec['lo'];hi=spec['hi'];bot=spec['base'];top=spec['top'];ms=[]
 for z in np.arange(bot,top-.003,.008):
  h=min(.0068,top-z)
  if side=='west':ms.append(cube([.452,lo,float(z)],[.006,hi-lo,h]))
  else:ms.append(cube([lo,(-3.713 if side=='north' else -6.993),float(z)],[hi-lo,.006,h]))
 # 4 mm vertical woven tapes connect all the reeds; slight projection is visible.
 for t in np.linspace(lo+.15,hi-.15,7):
  if side=='west':ms.append(cube([.4515,float(t)-.002,bot],[.007,.004,top-bot+.002]))
  else:ms.append(cube([float(t)-.002,(-3.7135 if side=='north' else -6.9935),bot],[.004,.007,top-bot+.002]))
 # Woven interstices are a 1 mm closed fiber bed behind the raised reeds.
 # This represents the dense woven screen instead of deep transparent slots,
 # avoids distance moire, and keeps a shallow physical reed relief.
 if side=='west':ms.append(cube([.452,lo,bot],[.001,hi-lo,top-bot]))
 else:ms.append(cube([lo,(-3.713 if side=='north' else -6.993),bot],[hi-lo,.001,top-bot]))
 curtain=union(ms);reeds+=ps(curtain,BAMBOO)
 # Wooden head and bottom laths joined to screen edge, narrow hanging loops.
 if side=='west':
  reeds.append(box(.444,lo,top-.006,.022,hi-lo,.030,WOOD));reeds.append(box(.444,lo,bot-.009,.022,hi-lo,.022,WOOD))
  for t in [lo+.25,hi-.25]:strings.append(cube([.443,t-.002,top+.017],[.025,.004,.077]))
 else:
  y=-3.711 if side=='north' else -6.991
  reeds.append(box(lo,y-.012,top-.006,hi-lo,.024,.030,WOOD));reeds.append(box(lo,y-.012,bot-.009,hi-lo,.024,.022,WOOD))
  for t in [lo+.25,hi-.25]:strings.append(cube([t-.002,y-.012,top+.017],[.004,.024,.077]))
 check(side+' bamboo curtain connected',len(curtain.decompose())==1,volume_m3=curtain.volume(),reed_pitch_m=.008,nominal_open_gap_m=.0012)
put('SITE_GAZEBO_V11_BAMBOO_ROLLER_BLINDS',reeds,v22_detail='Fine 6.8 mm reeds on 8 mm pitch with 1 mm woven fiber bed; north curtain down to 7 cm above deck, south high rolled curtain, narrow wooden battens')
put('SITE_V22_PAVILION_BLIND_HANGERS',ps(union(strings),CORD),classification='SMALL_SCREEN_HANGING_LOOPS_TO_RING_BEAM')
# 4. Continuous thin-walled rainwater outlet visible beside southeast post.
# Wall solids are modeled around a real open bore; elbows are swept through the
# whole path and joined continuously, with two ordinary fixing straps.
def tube_path(points,outer,inner,sides=24):
 a=np.array(points,float);dirs=np.diff(a,axis=0);dirs/=np.linalg.norm(dirs,axis=1)[:,None];tans=np.vstack([dirs[0],dirs[:-1]+dirs[1:],dirs[-1]]);tans/=np.linalg.norm(tans,axis=1)[:,None]
 verts=[]
 for c,t in zip(a,tans):
  u=np.cross(t,[1.,0,0]);u/=np.linalg.norm(u);v=np.cross(t,u)
  for r in [outer,inner]:
   for ang in np.linspace(0,2*math.pi,sides,endpoint=False):verts.append((c+r*(u*math.cos(ang)+v*math.sin(ang))).tolist())
 faces=[];stride=sides*2
 for j in range(len(a)-1):
  for k in range(sides):
   l=(k+1)%sides;b=j*stride;e=(j+1)*stride
   faces.append([b+k,b+l,e+l,e+k]);faces.append([b+sides+l,b+sides+k,e+sides+k,e+sides+l])
 for j in [0,len(a)-1]:
  b=j*stride
  for k in range(sides):l=(k+1)%sides;faces.append([b+k,b+sides+k,b+sides+l,b+l] if j==0 else [b+l,b+sides+l,b+sides+k,b+k])
 return manifold(oriented({'type':'polyhedron','vertices':verts,'faces':faces}))
path=[[3.93,-7.112,2.289],[3.93,-7.112,2.195],[3.93,-7.10,2.14],[3.93,-7.10,-.298],[3.93,-7.145,-.362]]
pipe=tube_path(path,.025,.0215)
# Union gutters before cutting the actual outlet, preventing a closed cap.
gutter=union([manifold(p['geometry']) for p in E['SITE_GAZEBO_V11_METAL_GUTTERS']['parts']])
hole=manifold({'type':'cylinder','origin':[3.93,-7.112,2.270],'radius':.0215,'height':.035,'segments':24})
gutter=gutter-hole
put('SITE_GAZEBO_V11_METAL_GUTTERS',ps(gutter,METAL),v22_detail='Continuous gutter body, southeast open outlet to photo-observed PVC downpipe')
straps=[]
for z in [.02,1.50]:
 ring=tube_path([[3.93,-7.10,z],[3.93,-7.10,z+.013]],.029,.0253)
 straps+=[ring,cube([3.921,-7.091,z+.001],[.018,.04,.011])]
put('SITE_V22_PAVILION_RAINWATER_DOWNPIPE',ps(pipe,PVC)+ps(union(straps),METAL),classification='PHOTO_SOUTHEAST_WHITE_DOWNPIPE_OPEN_BORE_AND_FIXINGS',outer_diameter_m=.05,wall_thickness_m=.0035,reference='Original INSV 625 s and user 182351 real photograph')
check('Downpipe is one closed positive material shell',pipe.status()==mf.Error.NoError and len(pipe.decompose())==1 and pipe.volume()>0,volume_m3=pipe.volume(),bore_m=.043)
check('No pipe intrusion past registered roof/deck axis edge',pipe.bounding_box()[3]<=3.96,max_x_m=pipe.bounding_box()[3])
# Exact preserved authoritative references for layout checks: no regenerated deck.
deck=np.load(B/'02_Data'/I['SITE_V20_PAVILION_RAISED_WOOD_SLATS']['file'])['vertices']
check('Existing wood board underside remains 50 mm above ground',abs(deck[:,2].min()+.43038-.05)<1e-7,board_underside_m=float(deck[:,2].min()),ground_m=-.43038)
check('Principal axis retreat preserved at x=3.96',abs(deck[:,0].max()-3.96)<1e-6,max_x_m=float(deck[:,0].max()))
unchanged=[n for n in E if ('GAZEBO' in n or 'PAVILION' in n) and n not in [e['name'] for e in Q['replace']]]
QA['preserved_native_caches']={n:hashlib.sha256((B/'02_Data'/I[n]['file']).read_bytes()).hexdigest() for n in unchanged}
for e in Q['replace']+Q['add']:
 for j,p in enumerate(e['parts']):
  m=manifold(p['geometry']);check(e['name']+f' part {j+1} closed positive',m.status()==mf.Error.NoError and m.volume()>1e-10,status=str(m.status()),volume_m3=m.volume())
Q['cameras']=[['V22_Pavilion_Photo_Compare',[7.45,-10.2,1.37],[2.23,-5.10,1.15],68],['V22_Pavilion_Wood_Drain_Detail',[5.38,-8.48,.65],[3.88,-6.93,1.01],64]]
Q['change_notes']=['亭子保留收回主轴侧的位置和离地 5 cm 的薄木板平台，四柱调整为实景旧暖木色并补足柱头接触。','根据原片补出临主轴开敞面两端各三根细木竖杆，中央保留 2.05 m 入口；竹帘改细密竹片，靠楼房一侧降到近平台。','补齐白色落水管、连续弯头、开口管腔和固定箍，檐沟对应开出真实出水口；均未伸入中央通道。']
QA['status']='PASS_SOURCE_NATIVE_PAVILION_DETAIL_QA';QA['notes']=Q['change_notes'];QA['cameras']=Q['cameras'];QA['reference_evidence']=[{'source':'User 182351 and original625 s','observed':'White rain pipe at front left of photographed pavilion; thin full-height stiles at both front-opening ends; fine woven blinds; aged warm posts'}, {'source':'Original600 s','observed':'House-side/north bamboo curtain lowered close to deck'}, {'source':'User182329','observed':'Current model misses thin stiles and rain pipe; bamboo strips and hanging height simplified'}]
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8')
R=D/'Reference';R.mkdir(exist_ok=True)
for f in [Path('D:/Desktop/问题大全（每个细节）/亭子·/屏幕截图 2026-10-15 182329.jpg'),Path('D:/Desktop/问题大全（每个细节）/亭子·/屏幕截图 2026-10-15 182351.jpg'),W/'v20_gate_pavilion/Reference/INSV_0625s_L1_Y-30_P-20.jpg',W/'v20_gate_pavilion/Reference/INSV_0600s_L0_Y+00_P-20.jpg']:shutil.copy2(f,R/f.name)
print('READY',len(Q['replace']),'replace',len(Q['add']),'add',len(QA['checks']),'checks',flush=True)



