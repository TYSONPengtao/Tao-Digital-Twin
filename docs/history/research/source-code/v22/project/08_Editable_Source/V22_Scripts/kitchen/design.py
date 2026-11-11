"""V22 photo comparison: kitchen eave column feet and supported projecting beams.
Only the two listed V21 column/base nodes are replaced. All new dimensions are
photo fitted to the retained registered shafts, floor and eave, not surveyed.
"""
import sys,json,copy,ast,math,shutil,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V21')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman']),('v14_building.py',['part','box','beam'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]}
R=D/'Reference';R.mkdir(exist_ok=True)
refs=list(Path('D:/Desktop/问题大全（每个细节）/厨房廊檐柱子').glob('*.jpg'))
refs.append(W/'v21_site/Reference/INSV_1036s_L1_Y+00_P-10.jpg')
for fp in refs:shutil.copy2(fp,R/fp.name)
QA={'status':'PENDING','evidence':[str(p) for p in refs],'dimension_status':'Visible profiles photo fitted; original bay centres, shaft diameters, floor and roof registration retained. Carving motif is a restrained contour approximation, not an exact measured reproduction.','checks':[]}
def check(label,ok,**data):
 QA['checks'].append(dict(check=label,pass_check=bool(ok),**data));assert ok,(label,data)
def cube(o,s):return manifold(dict(type='box',origin=o,size=s))
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def raw(n,material=None):
 a=np.load(B/'02_Data'/I[n]['file']);v=a['vertices'];f=a['faces']
 if material is not None:f=f[a['material_ids']==I[n]['materials'].index(material)]
 vv,inv=np.unique(np.round(v,9),axis=0,return_inverse=True)
 m=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,(n,m.status());return m
def put(n,ps,**meta):
 e=copy.deepcopy(E.get(n,dict(name=n,layer='60_SITE',family='SITE_MODEL',confidence='PHOTO_FIT')))
 for k in ['origin','angle_deg','angle','definition','v20_native_cache_override','v21_native_cache_override','external_native_cache','native_geometry_file']:e.pop(k,None)
 e.update(parts=ps,v22_kitchen=True,source='; '.join(str(p) for p in refs),dimension_status=QA['dimension_status'],**meta)
 Q['replace' if n in E else 'add'].append(e);return e
def ring(cx,cy,levels,N=64,angle=0):
 # Closed turned/faceted profile with shared vertices along each change in slope.
 vs=[]
 for z,r in levels:
  vs += [[cx+r*math.cos(angle+2*math.pi*j/N),cy+r*math.sin(angle+2*math.pi*j/N),z] for j in range(N)]
 fs=[list(range(N-1,-1,-1)),list(range((len(levels)-1)*N,len(levels)*N))]
 for k in range(len(levels)-1):
  for j in range(N):fs.append([k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j])
 return manifold(dict(type='polyhedron',vertices=vs,faces=fs))
def pad(cx,cy,z,w,h,c=.012):
 r=w/2;p=[[-r+c,-r],[r-c,-r],[r,-r+c],[r,r-c],[r-c,r],[-r+c,r],[-r,r-c],[-r,-r+c]]
 return manifold(dict(type='prism',profile=[[cx+x,cy+y,z] for x,y in p],vector=[0,0,h]))

centres=[(7.891,y) for y in [-11.24,-8.26,-5.94,-2.96]]
floor_top=-.4000244140625;stone_top=.040
Q['materials']['M_V22_Kitchen_Chiselled_Gray_Stone']={'color':[139,143,139],'roughness':.94}
# Real image shows a square foot, eight-sided slightly tapered stone drum and
# rolled circular bearing, rather than the current single cubic blocks.
stone=[];base_solids=[]
for k,(x,y) in enumerate(centres):
 foot=pad(x,y,floor_top,.365,.085)
 shoulder=ring(x,y,[(floor_top+.078,.179),(floor_top+.103,.174),(floor_top+.131,.157)],8,math.pi/8)
 drum=ring(x,y,[(floor_top+.123,.157),(floor_top+.361,.149)],8,math.pi/8)
 bearing=ring(x,y,[(floor_top+.350,.149),(floor_top+.368,.154),(floor_top+.382,.153),(floor_top+.394,.144),(stone_top,.137)],64)
 base=union([foot,shoulder,drum,bearing])
 # Small framed recesses on principal facets reproduce the visible panel depth
 # without inventing unresolvable floral or religious engraving.
 cuts=[]
 for ang in [0,math.pi/2,math.pi,3*math.pi/2]:
  r=.149*math.cos(math.pi/8);n=np.array([math.cos(ang),math.sin(ang)]);t=np.array([-n[1],n[0]])
  local=[[-.044,floor_top+.163],[.044,floor_top+.163],[.044,floor_top+.309],[.034,floor_top+.319],[-.034,floor_top+.319],[-.044,floor_top+.309]]
  profile=[[*(np.array([x,y])+n*(r-.003)+t*u),z] for u,z in local]
  cuts.append(manifold(dict(type='prism',profile=profile,vector=[*(n*.013),0])))
 base=base-union(cuts);base_solids.append(base);stone.append(part(fromman(base),'M_V22_Kitchen_Chiselled_Gray_Stone'))
 check(f'Base {k+1} one watertight solid',base.status()==mf.Error.NoError and len(base.decompose())==1 and base.volume()>0,volume_m3=base.volume(),bounds=list(base.bounding_box()))
 check(f'Base {k+1} keeps previous foot width',abs(base.bounding_box()[3]-base.bounding_box()[0]-.365)<1e-6)
put('SITE_KITCHEN_V12_GROUNDED_OUTER_COLUMN_STONE_BASES',stone,photo_visible_profile='Chamfered square pad, tapered octagonal drum, shallow framed panels, circular rolled top bearing',photo_fit_height_m=stone_top-floor_top)

# Trim the shaft foot only; the original round shafts and all intricate capitals
# retain their actual V21 vertices. Remove old low dark collars concealed by the
# taller stone drums, and fit one narrow timber bearing collar per shaft.
n='SITE_KITCHEN_V12_BEFORE_WOOD_15';cut=cube([7,-12,-1],[3,10,1.037]);ps=[];new_wood=[]
for mat in I[n]['materials']:
 m=raw(n,mat)-cut
 if not m.is_empty():ps.append(part(fromman(m),mat));new_wood.append(m)
for k,(x,y) in enumerate(centres):
 collar=ring(x,y,[(.037,.126),(.050,.130),(.072,.127),(.077,.123)],64)
 ps.append(part(fromman(collar),'M_V12_Kitchen_WOOD_DARK'));new_wood.append(collar)
 check(f'Column {k+1} seated into circular bearing',(collar^base_solids[k]).volume()>1e-6,contact_volume_m3=(collar^base_solids[k]).volume())
wood=union(new_wood);old=raw(n)
above=cube([7,-12,.08],[3,10,4])
check('All original shaft and capital geometry above base retained',((old^above)-(wood^above)).volume()<1e-8,missing_m3=((old^above)-(wood^above)).volume())
put(n,ps,shaft_diameter_m=.246,base_adjustment='Shortened at bottom only to seat on documented tall octagonal stone bases; original capitals retained')

# Photo confirms projecting tie ends under the eave and short hanging ornaments
# at column axes. Existing V21 capital pieces run along Y and do not form this
# transverse connection. New cross ties end inside the existing facade head.
heads=[];head_solids=[]
for k,(x,y) in enumerate(centres):
 tie=cube([7.50,y-.082,2.365],[1.60,.164,.145])
 # Restrained concave/stepped carved silhouette at the projecting outer end.
 prof=[[7.50,2.365],[7.87,2.365],[7.87,2.290],[7.81,2.272],[7.76,2.231],[7.72,2.213],[7.66,2.220],[7.61,2.245],[7.55,2.249],[7.50,2.275]]
 under=manifold(dict(type='prism',profile=[[a,y-.067,z] for a,z in prof],vector=[0,.134,0]))
 hanging=ring(7.605,y,[(2.167,.028),(2.179,.043),(2.207,.056),(2.239,.058),(2.261,.048),(2.287,.045)],48)
 head=union([tie,under,hanging]);heads.append(part(fromman(head),'M_V12_Kitchen_HONEY_WOOD'));head_solids.append(head)
 check(f'Cross tie {k+1} and hanging end connected',len(head.decompose())==1 and head.volume()>0)
 contact=head^wood
 check(f'Cross tie {k+1} supported by retained column capital',contact.volume()>1e-5,contact_volume_m3=contact.volume())
put('SITE_V22_KITCHEN_TRANSVERSE_EAVE_TIES_AND_HANGING_ENDS',heads,classification='PHOTO_FITTED_PROJECTING_TIMBER_TIE_ENDS',construction_note='Solid timber projecting ends attached to existing capital and front head; approximate visible contours only, no unsupported invented mortise geometry')

changed=union(base_solids+[wood]+head_solids)
gallery_probe=cube([8.19,-11.0,floor_top+.005],[.72,7.8,2.2])
check('Retained inner gallery walking strip is clear',(changed^gallery_probe).volume()<1e-8,clear_width_m=.72)
door_rows=[r for r in I if r.startswith('DOOR_COURTYARD_KITCHEN') and r.endswith('__LEAF')]
for dn in door_rows:
 d=raw(dn);hit=d^changed
 check(dn+' default inward-open leaf clears new detail',hit.volume()<1e-8,overlap_m3=hit.volume())
QA['objects']=[]
for e in Q['replace']+Q['add']:
 for j,p in enumerate(e['parts']):
  m=manifold(p['geometry']);check(e['name']+f' part {j} valid closed positive',m.status()==mf.Error.NoError and m.volume()>1e-10,volume_m3=m.volume())
 QA['objects'].append({'name':e['name'],'parts':len(e['parts'])})
QA['preserved_nodes']=['SITE_KITCHEN_STONE_FLOOR','SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS','SITE_KITCHEN_V12_PHOTO_DOUBLE_OCTAGON_AND_EDGE_FRET_WINDOWS']
QA['source_cache_hashes']={n:hashlib.sha256((B/'02_Data'/I[n]['file']).read_bytes()).hexdigest() for n in QA['preserved_nodes']}
Q['cameras']=[['V22_Kitchen_Column_Comparison',[6.55,-11.55,1.22],[8.10,-5.8,1.12],75],['V22_Kitchen_Stone_Base_Detail',[7.05,-9.05,.26],[7.89,-8.26,-.13],61],['V22_Kitchen_Eave_Tie_Detail',[7.05,-9.6,1.72],[7.96,-8.26,2.38],60]]
Q['change_notes']=['按厨房廊檐柱子对比图，将四个方盒柱础改为低方座、八角收分鼓身、浅框面和圆形承接；保持原柱心、基脚范围和石板地面。','木柱仅从脚部裁短与石础密接，保留原有柱身和柱头；补齐实景可见的出挑穿头木和短垂饰，检查支承交接及通行净空。','雕刻轮廓和柱础高度按照片拟合，未作为实测尺寸；原厨房门扇向内开启。']
QA['status']='PASS_PHOTO_FITTED_KITCHEN_SOURCE_QA';QA['cameras']=Q['cameras'];QA['change_notes']=Q['change_notes']
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Design_Control.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8')
print('READY',len(Q['replace']),len(Q['add']),len(QA['checks']),flush=True)
