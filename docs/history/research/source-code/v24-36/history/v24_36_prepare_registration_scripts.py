# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from pathlib import Path
import json,shutil,numpy as np
W=Path(__file__).parent;D=W/'v24_36';T=np.array(json.loads((D/'Coordinate_Seed.json').read_text())['seed_source_to_local']);rows=json.loads((D/'Decoded_L99_Index.json').read_text());chosen=[]
for r in rows:
 lo,hi=np.array(r['bounds']);corners=np.array([[x,y,z]for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]]);p=corners@T[:3,:3].T+T[:3,3]
 if p[:,0].max()>=-80 and p[:,0].min()<=85 and p[:,1].max()>=-78 and p[:,1].min()<=78:chosen.append(r)
(D/'Registration_Source_Index.json').write_text(json.dumps(chosen,indent=2));old=json.loads((W/'v24_34/Geometry_Index.json').read_text());old=[{**r,'file':str((W/'v24_34'/r['file']).resolve())}for r in old if'ORIGINAL_EXTERIOR_'in r['name']];(D/'Geometry_Index.json').write_text(json.dumps(old,indent=2))
s=(W/'v24_34_registration_views.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_36'").replace('Rebuild_V24_33','Rebuild_V24_35').replace('Architecture_Complete_V24_33','Architecture_Complete_V24_35').replace('Decoded_L21_Index.json','Registration_Source_Index.json').replace('MB7_Geographic_Seed_Top','PTJIA6_Geographic_Seed_Top');(W/'v24_36_registration_views.py').write_text(s,encoding='utf8')
s=(W/'v24_34_match.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_36'").replace('MB7_Geographic_Seed_Top','PTJIA6_Geographic_Seed_Top');(W/'v24_36_match.py').write_text(s,encoding='utf8')
s=(W/'v24_34_landmarks.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_36'").replace('Decoded_L21_Index.json','Registration_Source_Index.json');(W/'v24_36_landmarks.py').write_text(s,encoding='utf8')
s=(W/'v24_34_register.py').read_text('utf8').replace("D=W/'v24_34'","D=W/'v24_36'").replace('MB7_Registration.json','PTJIA6_Registration.json').replace("'source':'D:/AJAVIS01/ContextCapture/CASES/MB501/Productions/MB7/Data/Model'","'source':'D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model'").replace("'source_srs':'EPSG:32647'","'source_srs':'ENU:TAO_PRIVATE_SITE_004,TAO_PRIVATE_SITE_023'").replace("'source_origin':[TAO_PRIVATE_SITE_020,TAO_PRIVATE_SITE_005,0]","'source_origin':[0,0,0]");(W/'v24_36_register.py').write_text(s,encoding='utf8')
for n in ['registration_views','match','landmarks','register']:compile((W/('v24_36_'+n+'.py')).read_text('utf8'),n,'exec')
print('REGISTRATION_NEAR_SITE',len(chosen),'triangles',sum(r['triangles']for r in chosen),flush=True)
