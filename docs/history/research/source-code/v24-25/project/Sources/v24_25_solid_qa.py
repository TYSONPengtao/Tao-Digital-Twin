from v24_25_common import *
R=Path('E:/jz/JIA/Rebuild_V24_25/Reports');idx=json.loads((D/'Saved_Geometry_Index.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];ms={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in idx['objects']:
 d=np.load(D/row['file']);v=d['v'];f=d['f'];m=solid(v,f,row['name']);ms[row['name']]=m
 # Measure the saved triangles directly. Re-importing a near-coplanar inherited
 # facade into Manifold can simplify small seams, changing its calculated volume.
 t=(v-v.mean(0))[f];saved_volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);err=abs(saved_volume-row['volume_m3']);ck('Saved closed positive solid / '+row['name'],m.status()==mf.Error.NoError and saved_volume>0 and err<max(3e-5,row['volume_m3']*3e-5),bodies=len(m.decompose()),saved_triangle_volume_error_m3=err,manifold_reimport_volume_m3=m.volume())
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';wall=ms[n];old=load(n);local=cube([8.2499,-11.7301,-.551],[9.541,-11.6199,3.6]);err=abs(((old-wall)-local).volume())+abs(((wall-old)-local).volume());ck('Gate wall changes remain local to the marked joint',err<3e-5,outside_joint_difference_m3=err)
protected=cube([8.190,-11.855,-.284],[8.251,-11.793,2.291]);ck('New masonry does not cover the carved bevel',abs(((wall-old)^protected).volume())<1e-8)
pier=load('SITE_V21_GATE_REFERENCE_LAYER_02_Geometry');ck('Masonry physically meets the gate pier',wall.min_gap(pier,.02)<1e-5)
eave=ms['V24_25_Gate_Pier_Continuous_Eave_Return'];ceiling=load('V24_XIESHAN_07_Closed_Pale_Ceiling');ck('Top return reaches gate soffit',eave.min_gap(ceiling,.02)<1e-4)
zone=cube([10.8999,-16.4201,-2],[13.6201,-11.5999,1]);floor=ms['V24_25_Storage_Entrance_Continuous_Light_Gray_Finish'];ck('Entrance finish stays within marked approach',abs((floor-zone).volume())<1e-8)
for n in prep['proof']['storage_entrance']['recolored_existing_floors']:
 a=load(n);b=ms[n];err=abs((a-b).volume())+abs((b-a).volume());ck('Storage original slab envelope retained / '+n,err<3e-5,symmetric_difference_m3=err)
for r in prep['proof']['bathroom_windows']['windows']:
 a=ms[r['name']];ck('Window frame and two independent frosted panes / '+r['name'],len(a.decompose())==3)
fail=[c for c in checks if not c['pass']];(R/'V24_25_Solid_QA.json').write_text(json.dumps({'status':'PASS_SAVED_SOLIDS_AND_LOCAL_SCOPE'if not fail else'FAIL','model_sha256':idx['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V25_SOLID_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
