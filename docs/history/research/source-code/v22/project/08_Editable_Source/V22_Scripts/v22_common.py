import sys,json,copy,ast,math
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,box as shbox
from shapely.ops import unary_union
B=Path('E:/jz/JIA/Rebuild_V21')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']}
I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'<helpers>','exec'))
proof={};D=W/'v22';D.mkdir(exist_ok=True)
tree=ast.parse((W/'v19_design.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='fromman'],type_ignores=[]),'<solid-cleanup>','exec'))
def fm(m):
 assert m.status()==mf.Error.NoError and m.volume()>1e-12,(m.status(),m.volume())
 return fromman(m)
def pp(m,mat):return {'geometry':fm(m) if isinstance(m,mf.Manifold) else m,'material':mat}
def cube(o,s):return manifold({'type':'box','origin':o,'size':s})
def uni(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def raw(n,mat=None):
 d=np.load(B/'02_Data'/I[n]['file']);v=d['vertices'];f=d['faces']
 if mat is not None:f=f[d['material_ids']==I[n]['materials'].index(mat)]
 for dec in [9,8,7,6]:
  vv,iv=np.unique(np.round(v,dec),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(vv,iv[f].astype(np.uint64)))
  if m.status()==mf.Error.NoError:return m
 # Authoritative caches sometimes contain overlapping individually valid native
 # parts; a Boolean union of their original parts has the same solid envelope.
 ms=[]
 for p in ex.expand_parts(E[n]):
  if mat and p['material']!=mat:continue
  vv,ff=ex.world_part(p,E[n]);ms.append(manifold({'type':'polyhedron','vertices':vv.tolist(),'faces':ff}))
 m=uni(ms);assert m.status()==mf.Error.NoError,(n,m.status());return m
def nativeparts(n):return [pp(raw(n,mat),mat) for mat in I[n]['materials']]
def cyl(x,y,z,r,h,n=32):return manifold({'type':'cylinder','origin':[x,y,z],'radius':r,'height':h,'segments':n})
def prismxz(poly,y,d):return manifold({'type':'prism','profile':[[x,y,z] for x,z in poly],'vector':[0,d,0]})
def stroke(points,r=.006,depth=.01):
 # Smooth, genuinely volumetric relief strokes in an XZ plane.
 ms=[]
 for (x,z),(u,w) in zip(points,points[1:]):
  dx,dz=u-x,w-z;le=math.hypot(dx,dz)
  if le<1e-8:continue
  a=np.array([-dz,dx])*r/le
  ms.append(prismxz([[x+a[0],z+a[1]],[u+a[0],w+a[1]],[u-a[0],w-a[1]],[x-a[0],z-a[1]]],0,depth))
 for x,z in points:
  q=[[x+r*math.cos(t),z+r*math.sin(t)] for t in np.linspace(0,2*math.pi,12,endpoint=False)]
  ms.append(prismxz(q,0,depth))
 return uni(ms)
def petal(cx,cz,length,width,angle,depth=.014):
 # Lenticular curved leaf with a shallow peaked ridge; pointed ends retained.
 ts=np.linspace(0,1,10);left=[];right=[];a=math.radians(angle);u=np.array([math.cos(a),math.sin(a)]);v=np.array([-u[1],u[0]])
 for t in ts:
  c=np.array([cx,cz])+u*(t-.5)*length;w=width*.5*math.sin(math.pi*t)**.72
  left.append((c+v*w).tolist());right.append((c-v*w).tolist())
 return prismxz(left+right[::-1][1:-1],0,depth)
def flower(cx,cz,r,depth=.014):
 ms=[]
 for a in np.arange(0,360,45):
  t=math.radians(a);ms.append(petal(cx+math.cos(t)*r*.45,cz+math.sin(t)*r*.45,r,.42*r,a,depth))
 ms.append(prismxz([[cx+r*.22*math.cos(t),cz+r*.22*math.sin(t)] for t in np.linspace(0,2*math.pi,20,endpoint=False)],0,depth+.004))
 return uni(ms)
def rectframe(x0,x1,z0,z1,y,th=.022,depth=.025):
 return cube([x0,y,z0],[x1-x0,depth,z1-z0])-cube([x0+th,y-.001,z0+th],[x1-x0-2*th,depth+.002,z1-z0-2*th])
def start():return {'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]}
def put(Q,n,parts,**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':'60_SITE','family':'DETAIL_MODEL','confidence':'PHOTO_FIT'}))
 for k in ['definition','origin','angle','angle_deg','external_mesh_file','native_geometry_file','external_native_cache','v20_native_cache_override','v21_native_cache_override']:e.pop(k,None)
 e.update(parts=parts,source='User latest ideal/current/site comparison folder, 2026-10-16',dimension_status='Photo and ideal-image fitting to registered V21 positions; hidden joints not surveyed',**meta)
 assert n not in {e['name'] for e in Q['replace']+Q['add']}
 Q['replace' if n in E else 'add'].append(e);return e
def save(Q,D,checks):
 D.mkdir(exist_ok=True)
 ps=[]
 for e in Q['replace']+Q['add']:
  for j,p in enumerate(e['parts']):
   try:m=manifold(p['geometry'])
   except Exception as err:raise RuntimeError((e['name'],j)) from err
   assert m.status()==mf.Error.NoError and m.volume()>1e-10,(e['name'],j,m.status(),m.volume())
   ps.append({'node':e['name'],'part':j,'closed_positive':True,'volume_m3':m.volume()})
 (D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
 (D/'Design_Control.json').write_text(json.dumps({'status':'PASS_SOURCE_DETAIL_QA','checks':checks,'parts':ps,'photo_fit_not_surveyed':True},ensure_ascii=False,indent=2),encoding='utf8')
 print('READY',D.name,len(Q['replace']),len(Q['add']),len(ps),flush=True)
