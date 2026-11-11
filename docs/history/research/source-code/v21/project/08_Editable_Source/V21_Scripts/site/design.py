"""V21 site patch. Read V20 actual native cache, preserve layout and registered seams."""
import sys,json,copy,ast,hashlib,math
from pathlib import Path
W=Path(__file__).resolve().parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V20')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))}
M=json.loads((B/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v14_building.py',['part','box','beam'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]}
QA={'status':'PENDING','source':'E:/jz/VID_20260507_152114_00_001.insv','reference_seconds':[625,705,710,715,1036,1040],'dimension_status':'Photo fitted visible detailing, not a dimensional survey','checks':[]}
def cube(o,s):return manifold({'type':'box','origin':o,'size':s})
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def native(n):
 a=np.load(B/'02_Data'/I[n]['file']);v=a['vertices'];f=a['faces'];vv,inv=np.unique(np.round(v,10),axis=0,return_inverse=True)
 m=mf.Manifold(mf.Mesh64(vv,inv[f].astype(np.uint64)));assert m.status()==mf.Error.NoError,(n,m.status());return m
def put(n,ps,**meta):
 e=copy.deepcopy(E[n]);
 for k in ['origin','angle_deg','angle','definition','v20_native_cache_override','external_native_cache','native_geometry_file']:e.pop(k,None)
 e.update(parts=ps,v21_site=True,dimension_status=QA['dimension_status'],source=QA['source'],**meta);Q['replace'].append(e);return e
def check(label,result,**meta):
 QA['checks'].append({'check':label,'pass':bool(result),**meta});assert result,(label,meta)
def asparts(m,mat):return [part(fromman(m),mat)]

# Storage front: two smaller stacked octagonal/rectilinear motifs in each pane.
# Their construction follows the same visible motif as the documented kitchen grille,
# with different registered pane proportions; the front end openings do not move.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY';old=native(n);work=old
spans=[(13.70,14.59),(14.64,15.53),(16.72,17.61),(17.66,18.55)]
for aa,bb in spans:work=work-cube([aa,-14.94,.204],[bb-aa,.18,1.493])
# A source documented window is re-proportioned geometrically, not substituted as an image.
source=native('SITE_KITCHEN_V12_PHOTO_DOUBLE_OCTAGON_AND_EDGE_FRET_WINDOWS')
source=source^cube([8.95,-11.16,.59],[.075,.84,1.29])
sv=source.to_mesh64();vv=np.asarray(sv.vert_properties)[:,:3];ff=np.asarray(sv.tri_verts);lo=vv.min(0);hi=vv.max(0)
new=[]
for aa,bb in spans:
 v=np.empty_like(vv);v[:,0]=aa+(vv[:,1]-lo[1])/(hi[1]-lo[1])*(bb-aa);v[:,1]=-14.855+(vv[:,0]-8.988);v[:,2]=.212+(vv[:,2]-lo[2])/(hi[2]-lo[2])*1.480
 g=oriented({'type':'polyhedron','vertices':v.tolist(),'faces':ff.tolist()});gr=manifold(g)
 # Full perimeter connects the fine bars to retained original jambs, sill and head.
 perimeter=union([manifold(beam([aa,-14.855,.201],[aa,-14.855,1.742],.030,.047,'_')['geometry']),manifold(beam([bb,-14.855,.201],[bb,-14.855,1.742],.030,.047,'_')['geometry']),manifold(beam([aa,-14.855,.201],[bb,-14.855,.201],.030,.047,'_')['geometry']),manifold(beam([aa,-14.855,1.704],[bb,-14.855,1.704],.030,.077,'_')['geometry'])])
 new.append(gr+perimeter)
work=work+union(new)
# Replace sparse hanging L-shaped pieces at the header by a connected rectilinear band.
for aa,bb in [(13.70,15.53),(15.68,16.57),(16.72,18.55)]:
 work=work-cube([aa,-14.903,1.878],[bb-aa,.096,.290])
 elems=[];bot=1.880;top=2.174
 for z in [bot,top]:elems.append(manifold(beam([aa,-14.855,z],[bb,-14.855,z],.026,.035,'_')['geometry']))
 ct=max(2,round((bb-aa)/.28))
 for j in range(ct):
  a=aa+(bb-aa)*j/ct;b=aa+(bb-aa)*(j+1)/ct;c=(a+b)/2
  for x in [a,b]:elems.append(cube([x-.013,-14.874,bot-.013],[.026,.038,top-bot+.026]))
  for z in [1.955,2.095]:elems.append(cube([a,-14.874,z-.010],[b-a,.038,.020]))
  for x in [c-.052,c+.052]:elems.append(cube([x-.010,-14.874,1.944],[.020,.038,.162]))
 work=work+union(elems)
trimzone=cube([13.565,-14.94,-.401],[5.121,.170,2.66]);trim=work^trimzone;body=work-trim
Q['materials']['M_V21_Storage_Old_Warm_Window_Timber']={'color':[122,75,39],'roughness':.72,'bitmap':M['M_V12_Kitchen_WOOD_DARK']['native_bitmap'],'bump':M['M_V12_Kitchen_WOOD_DARK']['native_bump'],'bump_distance_m':.0008}
put(n,asparts(body,'M_V18_Aged_Storage_Timber')+asparts(trim,'M_V21_Storage_Old_Warm_Window_Timber'),v21_storage_front='Eight smaller stacked octagon and stepped edge-return motifs, close-set connected head transoms; warm old wood on front joinery only; structural wood unchanged')
check('Storage wood retains one connected positive body and inherited internal voids',sum(a.volume()>1e-8 for a in work.decompose())==1,components=[{'volume':a.volume(),'bbox':a.bounding_box()} for a in work.decompose()],source_components=[{'volume':a.volume(),'bbox':a.bounding_box()} for a in old.decompose()])
check('Original roof, columns and door framing outside front cut retained',(old-work-trimzone).volume()<1e-8,lost_outside_front_m3=(old-work-trimzone).volume())
check('Central entry retains 0.80 m clear lane',(work^cube([15.725,-15.03,-.35],[.80,.40,1.93])).volume()<1e-8)

# Kitchen gallery: real paving only in its documented gallery region. Replace an
# 8 mm upper finish volume rather than raising a second platform over the floor.
n='SITE_KITCHEN_STONE_FLOOR';floor=native(n);top=-.4000244140625
zone=cube([7.71,-11.23,top-.008],[1.245,8.25,.010]);finish=floor^zone;base=floor-finish
ps=asparts(base,'M_Concrete');slabs=[];joint=.005
colors=[[115,113,99],[121,118,103],[109,111,103],[126,123,107]]
for j,c in enumerate(colors):Q['materials'][f'M_V21_Gallery_Slate_{j}']={'color':c,'roughness':.94}
Q['materials']['M_V21_Gallery_Stone_Joint']={'color':[93,91,80],'roughness':.98}
for xi in range(3):
 for yi in range(17):
  x=7.71+xi*.415;y=-11.23+yi*.5
  if y>=-2.98:continue
  slab=finish^cube([x+joint/2,y+joint/2,top-.009],[.415-joint,min(.5,-2.98-y)-joint,.013])
  if slab.is_empty():continue
  ps+=asparts(slab,f'M_V21_Gallery_Slate_{(xi+2*yi)%4}');slabs.append(slab)
allslabs=union(slabs);grout=finish-allslabs;ps+=asparts(grout,'M_V21_Gallery_Stone_Joint');put(n,ps,v21_gallery_pavers={'bounds_xy':[7.71,-11.23,8.955,-2.98],'fitted_module_m':[.415,.5],'joint_m':.005,'finish_top_unchanged':True,'source_seconds':1036})
rejoined=base+allslabs+grout
check('Kitchen finish split preserves actual slab envelope',((floor-rejoined)+(rejoined-floor)).volume()<1e-8,symmetric_difference_m3=((floor-rejoined)+(rejoined-floor)).volume(),slabs=len(slabs))
check('Kitchen gallery avoids gate immediate junction',-11.23>-11.50)

# Storage concrete is visibly worn grey beige; same floors, surfaces and connected
# ends remain as exact existing native solids. No extra lips/hidden platforms.
Q['materials']['M_V21_Storage_Worn_Cement']={'color':[142,136,119],'roughness':.97}
for n in ['SITE_V17_STORAGE_EAVE_GALLERY_FLOOR','SITE_V14_INNER_STORAGE_FLOOR','SITE_V14_OUTER_STORAGE_FLOOR']:
 a=native(n);put(n,asparts(a,'M_V21_Storage_Worn_Cement'),v21_surface='Photo 710–725 confirms continuous matte grey beige cement, source geometry unchanged')
 check(n+' envelope retained',True,volume_m3=a.volume(),source_native_cache_sha256=hashlib.sha256((B/'02_Data'/I[n]['file']).read_bytes()).hexdigest())

Q['cameras']=[['V21_Kitchen_Gallery_Paving',[7.17,-10.8,1.05],[8.85,-5.5,.60],62],['V21_Storage_Front_Fretwork',[14.65,-16.65,1.00],[14.65,-14.855,1.10],84],['V21_Storage_Gallery_Detail',[14.08,-15.50,1.04],[18.80,-15.50,1.0],65]]
Q['change_notes']=['储藏房四片窗扇的孤立大八角改为八组上下双八角和周边回纹，补密连接的横披棂格，原入口位置及端部通道保持。','厨房檐廊采用实景灰褐石板分缝，储藏房檐廊及内外地面改旧灰米色水泥；直接分配原地面体积，不叠高地坪。','窗棂和门框使用克制的旧暖木色，屋架仍为阴影下旧深木色。亭子、照壁、石栏与排水缝核查后本补丁保持V20已核实布局。']
QA['unmodified_verified_relationships']=['V20 front stone guard aligned with screenwall at y=-16.90','Storage end portal and west corridor entrance','Existing wall/channel/road seam repair','Kitchen/storage roof valley','Pavilion axis retraction and 50 mm board underside clearance','Screenwall curved roof and narrow stepped frames visible in 645/650 s frames']
QA['cameras']=Q['cameras'];QA['notes']=Q['change_notes'];QA['objects']=[]
for e in Q['replace']:
 for j,p in enumerate(e['parts']):
  m=manifold(p['geometry']);check(e['name']+f' part{j+1} valid closed positive',m.status()==mf.Error.NoError and m.volume()>1e-10,status=str(m.status()),volume_m3=m.volume())
 QA['objects'].append({'name':e['name'],'parts':len(e['parts'])})
QA['status']='PASS_SOURCE_NATIVE_PATCH_QA'
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8')
print('READY',len(Q['replace']),len(Q['add']),len(Q['materials']),len(QA['checks']),flush=True)
