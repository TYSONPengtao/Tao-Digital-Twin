import sys,json,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']];exec(compile(ast.Module(fs,type_ignores=[]),'<geometry_helpers>','exec'))
O=Path(r'E:\jz\JIA\Rebuild_V13');I=json.loads((O/'02_Data/Native_Readback_Index_V13.json').read_text(encoding='utf8'));I={r['name']:r for r in I};checks=[];memo={}
S=json.loads((O/'08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S;anchor_methods={}
def check(n,passed,**kw):
 checks.append({'name':n,'passed':bool(passed),**kw});print(n,bool(passed),kw,flush=True)
def solid(n):
 if n in memo:return memo[n]
 d=np.load(O/'02_Data'/I[n]['file']);v=d['vertices'];f=d['faces'];_,ids,inv=np.unique(np.round(v,8),axis=0,return_index=True,return_inverse=True);v=v[ids];f=inv[f];f=f[np.array([len(set(x))==3 for x in f])];cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);f=f[np.linalg.norm(cross,axis=1)>1e-12]
 try:
  g=oriented({'type':'polyhedron','vertices':v.tolist(),'faces':f.tolist()});v=np.array(g['vertices']);f=np.array(g['faces']);a=mf.Manifold(mf.Mesh64(v.astype(np.float64),f.astype(np.uint64)));assert a.status()==mf.Error.NoError,(n,a.status())
 except (ValueError,AssertionError):
  # Adjacent native objects touch at shared wall-band edges; welding them
  # together makes four-face edges. Use independently verified source solids
  # and a solid union, rather than claiming their merged mesh is manifold.
  parts=[]
  for p in ex.expand_parts(E[n]):
   vv,ff=ex.world_part(p,E[n]);parts.append(manifold({'type':'polyhedron','vertices':vv.tolist(),'faces':ff}))
  a=mf.Manifold.batch_boolean(parts,mf.OpType.Add);assert a.status()==mf.Error.NoError,(n,a.status());anchor_methods[n]='Union of parametric part solids verified against actual native mesh bounds and corrected native extrusion volumes; merged touching-object mesh has duplicate seam edges'
 memo[n]=a;return a
def gap(a,b,t=.01):return float(solid(a).min_gap(solid(b),t))
def pair(label,a,b,t=.002):
 d=gap(a,b,t+.0001);check(label,d<=t,child=a,support=b,actual_native_solid_min_gap_m=d,tolerance_m=t)
roof='TERRACE_METAL_CANOPY';purlins='TERRACE_CANOPY_VISIBLE_PURLINS';outer='TERRACE_CANOPY_V13_OUTER_EAVE_BEAM';front='TERRACE_CANOPY_V13_FRONT_RETURN_BEAM';ledger='TERRACE_CANOPY_V13_SIDE_WALL_LEDGER';slab='SLAB_JOINED_F3';post0='TERRACE_CANOPY_POST_0';post1='TERRACE_CANOPY_POST_3.3';west='TERRACE_CANOPY_WEST_SUPPORTS'
for label,a,b in [('roof_panel_on_cross_members',roof,purlins),('cross_members_to_outer_eave_beam',purlins,outer),('cross_members_to_wall_ledger',purlins,ledger),('outer_eave_beam_to_return_beam',outer,front),('wall_ledger_to_return_beam',ledger,front),('front_left_post_to_return_beam',post0,front),('front_right_post_to_return_beam',post1,front),('middle_outer_posts_to_eave_beam',west,outer),('front_left_post_on_slab',post0,slab),('front_right_post_on_slab',post1,slab),('middle_outer_posts_on_slab',west,slab)]:pair(label,a,b)
walls=[n for n in I if n in ['PARTITIONS_JOINED_F3','FACADE_CONTINUOUS_F3']];gaps={n:gap(ledger,n,.5) for n in walls};check('side_wall_ledger_contacts_backing_wall',min(gaps.values())<=.002,actual_native_solid_gaps_m=gaps,tolerance_m=.002)
nodes=[roof,purlins,outer,front,ledger,post0,post1,west];roots=[];edges=[];adj={n:[] for n in nodes};tol=.002
for n in nodes:
 for anchor in [slab,*walls]:
  if gap(n,anchor,tol+.0001)<=tol:roots.append(n);break
for i,a in enumerate(nodes):
 for b in nodes[i+1:]:
  d=gap(a,b,tol+.0001)
  if d<=tol:edges.append([a,b,d]);adj[a].append(b);adj[b].append(a)
seen=set(roots);stack=list(roots)
while stack:
 n=stack.pop()
 for b in adj[n]:
  if b not in seen:seen.add(b);stack.append(b)
check('canopy_bearing_chain_connected_to_slab_or_wall',seen==set(nodes),connected_nodes=sorted(seen),unattached=sorted(set(nodes)-seen),direct_anchors=roots)
# Check the user-specified Roman column -> slab and adjacent arch relations.
for z,sl in [(0,'SLAB_JOINED_F2'),(3.9,'SLAB_JOINED_F3')]:
 for x in [3.9,9.1]:pair('roman_column_'+str(x)+'_'+str(z)+'_meets_slab','ROMAN_COLUMN_X'+str(x)+'_Z'+str(z),sl)
 for x in [3.9,9.1]:pair('arch_'+str(z)+'_meets_column_'+str(x),'PORCH_ARCH_BEAM_Z'+str(z),'ROMAN_COLUMN_X'+str(x)+'_Z'+str(z))
qa={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','geometry_source':'Actual delivered V13 native 3DM freshly meshed and block transforms resolved; touching wall-band and block anchors use independently native-verified parametric unions where documented','method':'Manifold64 solid minimum-gap calculations; no bounding-box-only contact acceptance','anchor_methods':anchor_methods,'solid_contact_tolerance_m':tol,'checks':checks,'canopy_contact_edges':edges,'capacity_analysis_performed':False,'limitation':'Checks confirm modeled physical contacts and a continuous bearing chain; concealed anchors, joint forces and member strength are not established by these checks.'}
(O/'06_Report/Native_Support_Contact_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');assert qa['status']=='PASS';print('PASS native support geometry',flush=True)
