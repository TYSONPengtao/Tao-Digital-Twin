from v24_23_common import *
R=Path('E:/jz/JIA/Rebuild_V24_23/Reports');idx=json.loads((D/'Saved_Geometry_Index.json').read_text());checks=[];ms={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in idx['objects']:
 d=np.load(D/row['file']);m=solid(d['v'],d['f'],row['name']);ms[row['name']]=m;err=abs(m.volume()-row['volume_m3']);ck('Saved closed solid / '+row['name'],m.status()==mf.Error.NoError and err<max(3e-5,row['volume_m3']*3e-5),bodies=len(m.decompose()),volume_error_m3=err)
wall=ms['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];gate=cube([7.73,-12.,-.6],[8.30,-11.2,3.12])
for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_22_South_Verge','V24_22_South_Verge_Bead','V24_Kitchen_Curved_Gable_Coping']:
 vol=(ms[n]^gate).volume();ck('Wall and verge do not cover gate pier / '+n,abs(vol)<1e-9,overlap_m3=vol)
post=ms['V24_23_Kitchen_North_End_Round_Post'];base=ms['V24_23_Kitchen_North_End_Stone_Base'];head=ms['V24_23_Kitchen_North_End_Abacus'];header=load('SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry')
ck('End column stands on its base',post.min_gap(base,.01)<.0001)
ck('End column supports the existing outer beam',post.min_gap(head,.01)<.0001 and head.min_gap(header,.01)<.0001)
ck('End column base stands on the veranda floor',base.min_gap(load('SITE_KITCHEN_STONE_FLOOR_Geometry'),.01)<.001)
fail=[c for c in checks if not c['pass']];(R/'V24_23_Solid_QA.json').write_text(json.dumps({'status':'PASS_SAVED_SOLIDS_AND_GATE_CLEARANCE'if not fail else'FAIL','model_sha256':idx['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V23_SOLID_QA',len(checks),'FAIL',len(fail))
