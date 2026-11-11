from pathlib import Path
import json,shutil,hashlib
W=Path(__file__).parent;D=W/'v26_19';O=Path('E:/jz/JIA/Rebuild_V26_19');n='SITE_PLANTER_1_Geometry'
# Preserve the previous delivered geometry fingerprints for the bounded edit check.
p=D/'Before_Planter_Removal_Index.json'
if not p.exists():shutil.copy2(D/'Final/Geometry_Index.json',p)
(D/'Fixture_Choice.json').write_text(json.dumps({'choice':'remove','source':'Direct user reply: 直接移除'},ensure_ascii=False,indent=2),'utf8')
prep=json.loads((D/'Prepared.json').read_text('utf8'));prep['objects']=[r for r in prep['objects']if r['name']!=n];prep['archive']=list(dict.fromkeys(prep['archive']+[n]));prep['new_materials']=[];prep['proof']['fixtures'].pop('planter_model',None);prep['proof']['fixtures']['planter_choice']='remove';prep['proof']['fixtures']['user_confirmation']='直接移除';(D/'Prepared.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8')
for fname in['build','make_helpers']:
 p=W/('v26_19_'+fname+'.py');s=p.read_text('utf8').replace('木材圆柱占位花盆按实景补成陶盆','按用户确认移除院内红圈占位花盆');p.write_text(s,'utf8')
print('USER_REMOVE_CHOICE_APPLIED')
