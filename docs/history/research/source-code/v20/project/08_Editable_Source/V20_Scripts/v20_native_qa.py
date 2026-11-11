"""Fresh native V20 verification, including inward leaves and corrected circulation."""
from pathlib import Path
import ast
W=Path(__file__).parent
s=(W/'v19_readback_qa.py').read_text(encoding='utf8').split('BF=rh.File3dm.Read')[0].replace('V19','V20').replace('mm.IsValid and mm.IsClosed','mm.IsValid and (mm.IsClosed or not r.get("closed_expected",True))').replace('vol>1e-10,volume_m3=vol','vol>1e-10 or not r.get("closed_expected",True),volume_m3=vol')
exec(compile(s,'<fresh_native_v20>','exec'))
import export_v5 as ex
S=json.loads((O/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'<qa_helpers>','exec'))
Q=json.loads((W/'v20/Mutation.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};IDX={r['name']:r for r in I}
def cachedman(n):
 d=np.load(O/'02_Data'/IDX[n]['file']);v=d['vertices'];ff=d['faces'];vv,inv=np.unique(np.round(v,9),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv,inv[ff].astype(np.uint64)));check('Cached solid topology '+n,a.status()==mf.Error.NoError);return a
def cube(p,s):return mf.Manifold.cube(s).translate(p)
def alladd(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
newwalls=next(e['name'] for e in Q['add'] if 'MISSING' in e['name'] and 'WALL' in e['name']);wall=cachedman(newwalls)
for p,s in [([4.4,7.23,.2],[3.1,.1,2.5]),([9.4,7.23,.2],[1.1,.1,2.5])]:check('Red marked wall genuinely solid',(cube(p,s)-wall).volume()<1e-8)
check('Stair right-side entrance preserved',(cube([7.85,7.17,.05],[1.1,.28,2.2])^wall).volume()<1e-9)
storage=json.loads((W/'v20_storage/Design_Control.json').read_text(encoding='utf8'));masonry=cachedman('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY');allstorage=alladd([cachedman(n) for n in IDX if n.startswith('SITE_V20_STORAGE') and ('WALL' in n or 'WHITE' in n or 'LIMEWASH' in n)])+masonry
for p,s in [([13.36,-11.45,-.35],[.21,1.15,1.95]),([18.66,-13.40,-.35],[.21,1.20,1.95])]:check('Incorrect middle opening sealed',(cube(p,s)-allstorage).volume()<1e-7)
for r in storage['clearance_boxes']:
 if 'portal' in r['label'].lower() or 'entry' in r['label'].lower():check('Corrected storage passage '+r['label'],(cube(r['origin'],r['size'])^allstorage).volume()<1e-7)
doorproof=[];DM=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'))
walls={f:cachedman('PARTITIONS_JOINED_F'+str(f)) for f in [1,2,3]}
for r in DM['doors']:
 n=r['name'];d=np.load(O/'02_Data'/IDX[n]['file']);v=d['vertices'];pivot=np.array(r['hinge_local_m']);no=np.array(r['inward_normal_local_xy']);amount=(v.mean(0)[:2]-pivot[:2])@no;check('Actual leaf extends inward '+n,amount>.18,inward_centroid_distance_m=float(amount))
 a=cachedman(n);vol=0
 if n.startswith('DOOR_') and not n.startswith(('DOOR_STORAGE','DOOR_COURTYARD')):
  floor=next((f for f in [1,2,3] if '_F'+str(f) in n),None)
  if floor:vol=(a^walls[floor]).volume();check('Inward main-house leaf clears partition '+n,vol<.00002,intersection_m3=vol)
  if floor==1:check('New enclosure does not obstruct inward leaf '+n,(a^wall).volume()<1e-8)
 doorproof.append({'name':n,'inward_distance_m':float(amount),'partition_intersection_m3':vol,'hinge_local_m':r['hinge_local_m']})
gate=cachedman('SITE_GATEHOUSE_VISIBLE_SOFFIT_BOARD');check('Inner gate eave is a substantial closed body',gate.volume()>.15,volume_m3=gate.volume())
gp=json.loads((W/'v20_gate_pavilion/Audit.json').read_text(encoding='utf8'));deckname='SITE_V20_PAVILION_RAISED_WOOD_SLATS';dd=np.load(O/'02_Data'/IDX[deckname]['file']);check('Slatted deck bottom has user 5cm clearance',abs(float(dd['vertices'][:,2].min())-gp['pavilion']['reference_ground_m']-.05)<1e-7);check('Axis edge pavilion retraction',abs(max(np.load(O/'02_Data'/IDX[n]['file'])['vertices'][:,0].max() for n in IDX if n.startswith('SITE_GAZEBO_') and 'ROOF' in n)-gp['pavilion']['new_axis_edge_x_m'])<.05)
check('V19 original file unchanged',sha(Path(AQ['base_model']))==AQ['base_model_sha256']);report={'status':'PASS_FRESH_NATIVE_V20_QA','model':str(P),'sha256':sha(P),'native_objects':len(F.Objects),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_objects':len(AQ['retained']),'changed_objects':len(AQ['created']),'doors':doorproof,'checks':checks,'index_parity':indexproof,'ue5_import_tested':False};(O/'06_Report/V20_Native_Readback_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('V20 FRESH NATIVE PASS',len(I),len(doorproof),flush=True)
