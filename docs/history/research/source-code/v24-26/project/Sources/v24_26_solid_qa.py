from v24_26_common import *
R=Path('E:/jz/JIA/Rebuild_V24_26/Reports');idx=json.loads((D/'Saved_Geometry_Index.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];ms={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in idx['objects']:
 d=np.load(D/row['file']);v=d['v'];f=d['f'];m=solid(v,f,row['name']);ms[row['name']]=m;t=(v-v.mean(0))[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);err=abs(vol-row['volume_m3']);ck('Saved closed positive solid / '+row['name'],m.status()==mf.Error.NoError and vol>0 and err<max(3e-5,row['volume_m3']*3e-5),volume_m3=vol,volume_error_m3=err)
cut=cube([7.,-13.,2.],[15.5,-11.85,5.5])
for n in [r['name']for r in prep['proof']['kitchen_verge']['trimmed_objects']]:
 old=load(n);new=ms[n];wanted=old-cut;err=abs((wanted-new).volume())+abs((new-wanted).volume());ck('Only marked kitchen overhang trimmed / '+n,err<3e-5,symmetric_difference_m3=err)
cap=ms['SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING_Geometry']
# The unchanged inherited wall core has overlapping triangle seams. Contact is
# therefore checked against its actual triangles in Native_QA, without altering
# that core merely to import it into the Boolean library.
chain='SITE_COURTYARD_WEST_TILE_WALL';flower=ms[chain+'_V10_OPEN_FLOWER_BRICKS_Geometry'];ridge=ms[chain+'_V10_RIDGE_SEAT_AND_CAP_Geometry'];ck('Flower ridge seats on bedding',flower.min_gap(cap,.10)<.06);ck('Ridge cap supports and touches openwork',ridge.min_gap(flower,.02)<1e-5)
# Every changed coping body remains outside the protected carved pier.
gate=union([load(n)for n in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry']])
for n,m in ms.items():
 if n.startswith(chain):ck('No coping covers carved gate pier / '+n,abs((m^gate).volume())<1e-8)
fail=[c for c in checks if not c['pass']];(R/'V24_26_Solid_QA.json').write_text(json.dumps({'status':'PASS_SAVED_SOLIDS_AND_LOCAL_SCOPE'if not fail else'FAIL','model_sha256':idx['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V26_SOLID_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
